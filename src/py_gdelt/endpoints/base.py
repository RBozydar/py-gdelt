"""Base class for all GDELT REST API endpoints.

This module provides the BaseEndpoint abstract base class that handles shared
functionality for all GDELT API endpoints:
- HTTP client lifecycle management (owned or shared)
- Retry logic with exponential backoff
- Error handling and classification
- Async context manager support

All endpoint implementations should inherit from BaseEndpoint and implement
the _build_url() method for their specific URL construction logic.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from math import ceil
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from py_gdelt.config import GDELTSettings
from py_gdelt.exceptions import (
    APIError,
    APIUnavailableError,
    InvalidQueryError,
    RateLimitError,
    _enhance_query_error,
    _is_query_error,
)


__all__ = ["BaseEndpoint"]

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(UTC)


def _as_utc(value: datetime) -> datetime:
    """Return a datetime normalized to UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _parse_retry_after(value: str | None, now: datetime | None = None) -> int | None:
    """Parse a Retry-After header into non-negative seconds.

    Args:
        value: Retry-After header value.
        now: Reference time for HTTP-date values.

    Returns:
        Seconds until retry, or None when the header is absent or invalid.
    """
    if value is None:
        return None

    normalized_value = value.strip()
    if not normalized_value:
        return None

    if normalized_value.isdecimal():
        return int(normalized_value)

    reference_time = _utc_now() if now is None else _as_utc(now)
    try:
        retry_at = parsedate_to_datetime(normalized_value)
    except (TypeError, ValueError):
        return None

    remaining_seconds = (_as_utc(retry_at) - reference_time).total_seconds()
    return max(0, ceil(remaining_seconds))


class BaseEndpoint(ABC):
    """Base class for all GDELT REST API endpoints.

    Provides shared HTTP client, retry logic, and error handling.
    All endpoints should inherit from this class.

    Subclasses must:
    - Define BASE_URL class attribute
    - Implement _build_url() method

    Args:
        settings: Configuration settings. If None, uses defaults.
        client: Optional shared HTTP client. If None, creates owned client.
               When provided, the client lifecycle is managed externally.

    Attributes:
        BASE_URL: Base URL for the API endpoint (must be defined by subclasses)

    Raises:
        NotImplementedError: If subclass does not define BASE_URL class attribute.
    """

    # Subclasses must define their base URL
    BASE_URL: str

    def __init__(
        self,
        settings: GDELTSettings | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        # Validate that subclass defines BASE_URL
        if not hasattr(self.__class__, "BASE_URL") or not self.__class__.BASE_URL:
            msg = f"{self.__class__.__name__} must define a non-empty BASE_URL class attribute"
            raise NotImplementedError(msg)

        self.settings = settings or GDELTSettings()
        self._rate_limit_until: datetime | None = None
        self._transient_error_until: datetime | None = None
        self._consecutive_transient_errors = 0

        if client is not None:
            self._client = client
            self._owns_client = False
        else:
            self._client = self._create_client()
            self._owns_client = True

    def _create_client(self) -> httpx.AsyncClient:
        """Create a new HTTP client with proper configuration.

        Returns:
            Configured httpx.AsyncClient with timeouts and redirect following.
        """
        return httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,
                read=float(self.settings.timeout),
                write=10.0,
                pool=5.0,
            ),
            follow_redirects=True,
        )

    def _record_rate_limit(self, retry_after: int | None, now: datetime) -> None:
        """Record the endpoint-local rate-limit circuit when configured."""
        if not self.settings.rate_limit_fail_fast:
            return

        circuit_seconds = (
            retry_after if retry_after is not None else self.settings.rate_limit_circuit_seconds
        )
        if circuit_seconds is None or circuit_seconds <= 0:
            self._rate_limit_until = None
            return

        self._rate_limit_until = now + timedelta(seconds=circuit_seconds)

    def _cap_retry_after(self, retry_after: int | None) -> int | None:
        """Cap Retry-After seconds according to settings."""
        if retry_after is None:
            return None

        max_seconds = self.settings.rate_limit_retry_after_max_seconds
        if max_seconds <= 0:
            return retry_after
        return min(retry_after, max_seconds)

    def _rate_limit_remaining_seconds(self, now: datetime | None = None) -> int | None:
        """Return remaining endpoint-local circuit seconds if the circuit is open."""
        if not self.settings.rate_limit_fail_fast or self._rate_limit_until is None:
            return None

        reference_time = _utc_now() if now is None else _as_utc(now)
        remaining_seconds = (self._rate_limit_until - reference_time).total_seconds()
        if remaining_seconds <= 0:
            self._rate_limit_until = None
            return None

        return ceil(remaining_seconds)

    def _raise_for_open_rate_limit(self, url: str) -> None:
        """Raise RateLimitError without I/O when this endpoint is locally limited."""
        retry_after = self._rate_limit_remaining_seconds()
        if retry_after is None:
            return

        msg = f"Rate limit circuit open for {url}"
        raise RateLimitError(msg, retry_after=retry_after)

    def _record_transient_error(self, now: datetime) -> None:
        """Record a transient API failure and open the local circuit if needed."""
        threshold = self.settings.transient_error_circuit_threshold
        if threshold <= 0:
            return

        self._consecutive_transient_errors += 1
        if self._consecutive_transient_errors < threshold:
            return

        circuit_seconds = self.settings.transient_error_circuit_seconds
        if circuit_seconds <= 0:
            self._transient_error_until = None
            return

        self._transient_error_until = now + timedelta(seconds=circuit_seconds)

    def _reset_transient_errors(self) -> None:
        """Reset transient error tracking after a successful response."""
        self._consecutive_transient_errors = 0
        self._transient_error_until = None

    def _transient_error_remaining_seconds(self, now: datetime | None = None) -> int | None:
        """Return remaining endpoint-local transient circuit seconds if open."""
        if self._transient_error_until is None:
            return None

        reference_time = _utc_now() if now is None else _as_utc(now)
        remaining_seconds = (self._transient_error_until - reference_time).total_seconds()
        if remaining_seconds <= 0:
            self._transient_error_until = None
            self._consecutive_transient_errors = 0
            return None

        return ceil(remaining_seconds)

    def _raise_for_open_transient_error(self, url: str) -> None:
        """Raise APIUnavailableError without I/O when transient circuit is open."""
        retry_after = self._transient_error_remaining_seconds()
        if retry_after is None:
            return

        msg = f"Transient error circuit open for {url}; retry after {retry_after} seconds"
        raise APIUnavailableError(msg)

    def _should_retry_exception(self, exception: BaseException) -> bool:
        """Return whether tenacity should retry the exception."""
        if isinstance(exception, APIUnavailableError):
            return self._transient_error_remaining_seconds() is None
        if isinstance(exception, RateLimitError):
            return self._rate_limit_remaining_seconds() is None
        return False

    async def close(self) -> None:
        """Close the HTTP client if we own it.

        Only closes the client if it was created by this instance.
        Shared clients are not closed to allow reuse.
        """
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    async def __aenter__(self) -> BaseEndpoint:
        """Async context manager entry.

        Returns:
            Self for use in async with statement.
        """
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit - close client.

        Args:
            *args: Exception info (unused, but required by protocol).
        """
        await self.close()

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Make an HTTP request with retry logic.

        Implements retry logic for transient errors (rate limits, server errors).
        Classifies errors into specific exception types.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to request
            params: Query parameters
            headers: Additional headers

        Returns:
            httpx.Response object

        Raises:
            RateLimitError: On 429 response (retryable)
            APIUnavailableError: On 5xx response or connection error (retryable)
            APIError: On other HTTP errors (not retryable)
        """
        self._raise_for_open_rate_limit(url)
        self._raise_for_open_transient_error(url)

        async for attempt in AsyncRetrying(
            retry=retry_if_exception(self._should_retry_exception),
            wait=wait_exponential(multiplier=1, min=2, max=60),
            stop=stop_after_attempt(self.settings.max_retries),
            reraise=True,
        ):
            with attempt:
                try:
                    response = await self._client.request(
                        method=method,
                        url=url,
                        params=params,
                        headers=headers,
                    )

                    # Handle rate limiting
                    if response.status_code == 429:
                        retry_after_header = response.headers.get("Retry-After")
                        now = _utc_now()
                        retry_after = self._cap_retry_after(
                            _parse_retry_after(retry_after_header, now=now),
                        )
                        self._record_rate_limit(retry_after, now=now)
                        msg = f"Rate limited by {url}"
                        raise RateLimitError(
                            msg,
                            retry_after=retry_after,
                        )

                    # Handle server errors
                    if 500 <= response.status_code < 600:
                        self._record_transient_error(_utc_now())
                        msg = f"Server error {response.status_code} from {url}"
                        raise APIUnavailableError(msg)

                    # Handle client errors
                    if 400 <= response.status_code < 500:
                        msg = f"HTTP {response.status_code} from {url}: {response.text[:200]}"
                        raise APIError(msg)

                except httpx.ConnectError as e:
                    self._record_transient_error(_utc_now())
                    msg = f"Connection failed to {url}: {e}"
                    raise APIUnavailableError(msg) from e
                except httpx.TimeoutException as e:
                    self._record_transient_error(_utc_now())
                    msg = f"Request timed out to {url}: {e}"
                    raise APIUnavailableError(msg) from e
                except httpx.HTTPStatusError as e:
                    msg = f"HTTP error from {url}: {e}"
                    raise APIError(msg) from e
                else:
                    self._reset_transient_errors()
                    return response

        # This should never be reached due to reraise=True, but mypy needs it
        msg = f"Request failed after retries: {url}"
        raise APIError(msg)

    async def _get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Convenience method for GET requests.

        Args:
            url: Full URL to request
            params: Query parameters
            headers: Additional headers

        Returns:
            httpx.Response object

        Raises:
            RateLimitError: On 429 response
            APIUnavailableError: On 5xx response or connection error
            APIError: On other HTTP errors
        """
        return await self._request("GET", url, params=params, headers=headers)

    async def _get_json(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """GET request that returns JSON data.

        Args:
            url: Full URL to request
            params: Query parameters

        Returns:
            Parsed JSON data (dict, list, or primitive types)

        Raises:
            RateLimitError: On 429 response
            APIUnavailableError: On 5xx response or connection error
            APIError: On other HTTP errors or invalid JSON
        """
        response = await self._get(url, params=params)
        if not response.content:
            return {}  # Empty response = no results
        try:
            return response.json()
        except json.JSONDecodeError:
            # GDELT returns plain text error messages with HTTP 200
            raw_message = response.text.strip() or "Invalid JSON response"
            if _is_query_error(raw_message):
                message, hint = _enhance_query_error(raw_message)
                raise InvalidQueryError(message, hint=hint) from None
            raise APIError(raw_message) from None

    @abstractmethod
    async def _build_url(self, **kwargs: Any) -> str:
        """Build the request URL for this endpoint.

        Subclasses must implement this to construct their specific URLs
        based on the endpoint's parameters and BASE_URL.

        Args:
            **kwargs: Endpoint-specific parameters for URL construction.

        Returns:
            Complete URL string ready for request.

        Raises:
            NotImplementedError: Always (must be implemented by subclass).
        """
        ...
