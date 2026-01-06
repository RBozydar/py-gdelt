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

import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from py_gdelt.config import GDELTSettings
from py_gdelt.exceptions import APIError, APIUnavailableError, RateLimitError


__all__ = ["BaseEndpoint"]

logger = logging.getLogger(__name__)


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
                read=30.0,
                write=10.0,
                pool=5.0,
            ),
            follow_redirects=True,
        )

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

    async def __aexit__(self, *args: Any) -> None:
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
        async for attempt in AsyncRetrying(
            retry=retry_if_exception_type((RateLimitError, APIUnavailableError)),
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
                        retry_after = response.headers.get("Retry-After")
                        msg = f"Rate limited by {url}"
                        raise RateLimitError(
                            msg,
                            retry_after=int(retry_after) if retry_after else None,
                        )

                    # Handle server errors
                    if 500 <= response.status_code < 600:
                        msg = f"Server error {response.status_code} from {url}"
                        raise APIUnavailableError(msg)

                    # Handle client errors
                    if 400 <= response.status_code < 500:
                        msg = f"HTTP {response.status_code} from {url}: {response.text[:200]}"
                        raise APIError(msg)

                except httpx.ConnectError as e:
                    msg = f"Connection failed to {url}: {e}"
                    raise APIUnavailableError(msg) from e
                except httpx.TimeoutException as e:
                    msg = f"Request timed out to {url}: {e}"
                    raise APIUnavailableError(msg) from e
                except httpx.HTTPStatusError as e:
                    msg = f"HTTP error from {url}: {e}"
                    raise APIError(msg) from e
                else:
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
        return response.json()

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
