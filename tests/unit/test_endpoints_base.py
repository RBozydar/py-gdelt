"""Tests for BaseEndpoint class.

Tests cover:
- Client lifecycle (owned vs shared clients)
- Async context manager behavior
- HTTP request/response handling
- Error classification and retry logic
- JSON helper methods
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from py_gdelt.config import GDELTSettings
from py_gdelt.endpoints.base import BaseEndpoint
from py_gdelt.exceptions import APIError, APIUnavailableError, RateLimitError


class TestEndpoint(BaseEndpoint):
    """Concrete test implementation of BaseEndpoint."""

    BASE_URL = "https://api.gdeltproject.org"

    async def _build_url(self, **kwargs: Any) -> str:
        """Simple URL builder for testing."""
        return self.BASE_URL


class TestClientLifecycle:
    """Test HTTP client creation and lifecycle management."""

    async def test_creates_owned_client_when_none_provided(self) -> None:
        """Test endpoint creates its own client when none provided."""
        endpoint = TestEndpoint()
        assert endpoint._owns_client is True
        assert endpoint._client is not None
        assert isinstance(endpoint._client, httpx.AsyncClient)
        await endpoint.close()

    async def test_uses_shared_client_when_provided(self) -> None:
        """Test endpoint uses provided client and doesn't close it."""
        async with httpx.AsyncClient() as shared_client:
            endpoint = TestEndpoint(client=shared_client)
            assert endpoint._owns_client is False
            assert endpoint._client is shared_client

            # close() should not close shared client
            await endpoint.close()

            # shared_client should still be open
            assert not shared_client.is_closed

    async def test_context_manager_creates_and_closes_client(self) -> None:
        """Test async context manager creates and closes owned client."""
        endpoint_ref = None
        async with TestEndpoint() as endpoint:
            endpoint_ref = endpoint
            assert endpoint._client is not None
            assert not endpoint._client.is_closed

        # Client should be closed after context exit
        assert endpoint_ref is not None
        assert endpoint_ref._client.is_closed

    async def test_context_manager_with_shared_client(self) -> None:
        """Test context manager doesn't close shared client."""
        async with httpx.AsyncClient() as shared_client:
            async with TestEndpoint(client=shared_client) as endpoint:
                assert endpoint._client is shared_client

            # Shared client should still be open
            assert not shared_client.is_closed

    async def test_custom_settings_passed_to_endpoint(self) -> None:
        """Test custom settings are stored on endpoint."""
        settings = GDELTSettings(max_retries=5, timeout=60)
        endpoint = TestEndpoint(settings=settings)
        assert endpoint.settings.max_retries == 5
        assert endpoint.settings.timeout == 60
        await endpoint.close()

    async def test_uses_default_settings_when_none_provided(self) -> None:
        """Test endpoint uses default settings when none provided."""
        endpoint = TestEndpoint()
        assert endpoint.settings is not None
        assert isinstance(endpoint.settings, GDELTSettings)
        await endpoint.close()


class TestRequestHandling:
    """Test HTTP request handling and error classification."""

    @respx.mock
    async def test_successful_request(self) -> None:
        """Test successful GET request returns response."""
        respx.get("https://api.gdeltproject.org/test").mock(
            return_value=httpx.Response(200, json={"data": "test"}),
        )

        async with TestEndpoint() as endpoint:
            response = await endpoint._get("https://api.gdeltproject.org/test")
            assert response.status_code == 200
            assert response.json() == {"data": "test"}

    @respx.mock
    async def test_successful_request_with_params(self) -> None:
        """Test GET request with query parameters."""
        respx.get("https://api.gdeltproject.org/test").mock(
            return_value=httpx.Response(200, json={"key": "value"}),
        )

        async with TestEndpoint() as endpoint:
            response = await endpoint._get(
                "https://api.gdeltproject.org/test",
                params={"query": "test", "mode": "json"},
            )
            assert response.status_code == 200

    @respx.mock
    async def test_successful_request_with_headers(self) -> None:
        """Test GET request with custom headers."""
        respx.get("https://api.gdeltproject.org/test").mock(
            return_value=httpx.Response(200, text="OK"),
        )

        async with TestEndpoint() as endpoint:
            response = await endpoint._get(
                "https://api.gdeltproject.org/test",
                headers={"X-Custom-Header": "value"},
            )
            assert response.status_code == 200


class TestErrorHandling:
    """Test error classification and exception raising."""

    @respx.mock
    async def test_rate_limit_raises_error_with_retry_after(self) -> None:
        """Test 429 response raises RateLimitError with retry_after."""
        respx.get("https://api.gdeltproject.org/test").mock(
            return_value=httpx.Response(429, headers={"Retry-After": "30"}),
        )

        async with TestEndpoint(settings=GDELTSettings(max_retries=1)) as endpoint:
            with pytest.raises(RateLimitError) as exc_info:
                await endpoint._get("https://api.gdeltproject.org/test")

            assert exc_info.value.retry_after == 30
            assert "Rate limited" in str(exc_info.value)

    @respx.mock
    async def test_rate_limit_without_retry_after(self) -> None:
        """Test 429 response without Retry-After header."""
        respx.get("https://api.gdeltproject.org/test").mock(return_value=httpx.Response(429))

        async with TestEndpoint(settings=GDELTSettings(max_retries=1)) as endpoint:
            with pytest.raises(RateLimitError) as exc_info:
                await endpoint._get("https://api.gdeltproject.org/test")

            assert exc_info.value.retry_after is None

    @respx.mock
    async def test_server_error_503_raises_unavailable(self) -> None:
        """Test 503 response raises APIUnavailableError."""
        respx.get("https://api.gdeltproject.org/test").mock(return_value=httpx.Response(503))

        async with TestEndpoint(settings=GDELTSettings(max_retries=1)) as endpoint:
            with pytest.raises(APIUnavailableError) as exc_info:
                await endpoint._get("https://api.gdeltproject.org/test")

            assert "Server error 503" in str(exc_info.value)

    @respx.mock
    async def test_server_error_500_raises_unavailable(self) -> None:
        """Test 500 response raises APIUnavailableError."""
        respx.get("https://api.gdeltproject.org/test").mock(return_value=httpx.Response(500))

        async with TestEndpoint(settings=GDELTSettings(max_retries=1)) as endpoint:
            with pytest.raises(APIUnavailableError):
                await endpoint._get("https://api.gdeltproject.org/test")

    @respx.mock
    async def test_client_error_400_raises_api_error(self) -> None:
        """Test 400 response raises APIError."""
        respx.get("https://api.gdeltproject.org/test").mock(
            return_value=httpx.Response(400, text="Bad request"),
        )

        async with TestEndpoint(settings=GDELTSettings(max_retries=1)) as endpoint:
            with pytest.raises(APIError) as exc_info:
                await endpoint._get("https://api.gdeltproject.org/test")

            assert "HTTP 400" in str(exc_info.value)
            assert "Bad request" in str(exc_info.value)

    @respx.mock
    async def test_client_error_404_raises_api_error(self) -> None:
        """Test 404 response raises APIError."""
        respx.get("https://api.gdeltproject.org/test").mock(
            return_value=httpx.Response(404, text="Not found"),
        )

        async with TestEndpoint(settings=GDELTSettings(max_retries=1)) as endpoint:
            with pytest.raises(APIError) as exc_info:
                await endpoint._get("https://api.gdeltproject.org/test")

            assert "HTTP 404" in str(exc_info.value)

    @respx.mock
    async def test_connection_error_raises_unavailable(self) -> None:
        """Test connection failure raises APIUnavailableError."""
        respx.get("https://api.gdeltproject.org/test").mock(
            side_effect=httpx.ConnectError("Connection refused"),
        )

        async with TestEndpoint(settings=GDELTSettings(max_retries=1)) as endpoint:
            with pytest.raises(APIUnavailableError) as exc_info:
                await endpoint._get("https://api.gdeltproject.org/test")

            assert "Connection failed" in str(exc_info.value)

    @respx.mock
    async def test_timeout_error_raises_unavailable(self) -> None:
        """Test timeout raises APIUnavailableError."""
        respx.get("https://api.gdeltproject.org/test").mock(
            side_effect=httpx.TimeoutException("Request timed out"),
        )

        async with TestEndpoint(settings=GDELTSettings(max_retries=1)) as endpoint:
            with pytest.raises(APIUnavailableError) as exc_info:
                await endpoint._get("https://api.gdeltproject.org/test")

            assert "Request timed out" in str(exc_info.value)

    @respx.mock
    async def test_http_status_error_raises_api_error(self) -> None:
        """Test httpx.HTTPStatusError is wrapped in APIError."""
        respx.get("https://api.gdeltproject.org/test").mock(
            side_effect=httpx.HTTPStatusError(
                "Bad request",
                request=httpx.Request("GET", "https://api.gdeltproject.org/test"),
                response=httpx.Response(400),
            ),
        )

        async with TestEndpoint(settings=GDELTSettings(max_retries=1)) as endpoint:
            with pytest.raises(APIError) as exc_info:
                await endpoint._get("https://api.gdeltproject.org/test")

            assert "HTTP error" in str(exc_info.value)


class TestJSONHelper:
    """Test JSON helper methods."""

    @respx.mock
    async def test_get_json_returns_parsed_data(self) -> None:
        """Test _get_json returns parsed JSON."""
        respx.get("https://api.gdeltproject.org/test").mock(
            return_value=httpx.Response(200, json={"key": "value", "count": 42}),
        )

        async with TestEndpoint() as endpoint:
            data = await endpoint._get_json("https://api.gdeltproject.org/test")
            assert data == {"key": "value", "count": 42}
            assert isinstance(data, dict)

    @respx.mock
    async def test_get_json_with_params(self) -> None:
        """Test _get_json with query parameters."""
        respx.get("https://api.gdeltproject.org/test").mock(
            return_value=httpx.Response(200, json=[1, 2, 3]),
        )

        async with TestEndpoint() as endpoint:
            data = await endpoint._get_json(
                "https://api.gdeltproject.org/test",
                params={"format": "json"},
            )
            assert data == [1, 2, 3]
            assert isinstance(data, list)

    @respx.mock
    async def test_get_json_raises_api_error_on_invalid_json(self) -> None:
        """Test _get_json raises APIError with message on invalid JSON response."""
        respx.get("https://api.gdeltproject.org/test").mock(
            return_value=httpx.Response(200, text="not json"),
        )

        async with TestEndpoint() as endpoint:
            with pytest.raises(APIError) as exc_info:
                await endpoint._get_json("https://api.gdeltproject.org/test")
            assert str(exc_info.value) == "not json"

    @respx.mock
    async def test_get_json_raises_api_error_on_gdelt_text_error(self) -> None:
        """Test _get_json raises APIError for GDELT plain text error messages."""
        error_msg = "One or more of your keywords were too short, too long or too common"
        respx.get("https://api.gdeltproject.org/test").mock(
            return_value=httpx.Response(200, text=error_msg),
        )

        async with TestEndpoint() as endpoint:
            with pytest.raises(APIError) as exc_info:
                await endpoint._get_json("https://api.gdeltproject.org/test")
            assert error_msg in str(exc_info.value)

    @respx.mock
    async def test_get_json_returns_empty_dict_on_empty_response(self) -> None:
        """Test _get_json returns empty dict for empty response body."""
        respx.get("https://api.gdeltproject.org/test").mock(
            return_value=httpx.Response(200, content=b""),
        )

        async with TestEndpoint() as endpoint:
            data = await endpoint._get_json("https://api.gdeltproject.org/test")
            assert data == {}
            assert isinstance(data, dict)


class TestRetryBehavior:
    """Test retry logic for transient errors."""

    @respx.mock
    async def test_retries_on_rate_limit(self) -> None:
        """Test request retries on 429 response."""
        # First call returns 429, second succeeds
        route = respx.get("https://api.gdeltproject.org/test").mock(
            side_effect=[
                httpx.Response(429, headers={"Retry-After": "1"}),
                httpx.Response(200, json={"success": True}),
            ],
        )

        async with TestEndpoint(settings=GDELTSettings(max_retries=3)) as endpoint:
            response = await endpoint._get("https://api.gdeltproject.org/test")
            assert response.status_code == 200
            assert response.json() == {"success": True}
            assert route.call_count == 2

    @respx.mock
    async def test_retries_on_server_error(self) -> None:
        """Test request retries on 503 response."""
        route = respx.get("https://api.gdeltproject.org/test").mock(
            side_effect=[
                httpx.Response(503),
                httpx.Response(200, json={"data": "ok"}),
            ],
        )

        async with TestEndpoint(settings=GDELTSettings(max_retries=3)) as endpoint:
            response = await endpoint._get("https://api.gdeltproject.org/test")
            assert response.status_code == 200
            assert route.call_count == 2

    @respx.mock
    async def test_does_not_retry_client_errors(self) -> None:
        """Test request does NOT retry on 4xx errors (except 429)."""
        route = respx.get("https://api.gdeltproject.org/test").mock(
            return_value=httpx.Response(400, text="Bad request"),
        )

        async with TestEndpoint(settings=GDELTSettings(max_retries=3)) as endpoint:
            with pytest.raises(APIError):
                await endpoint._get("https://api.gdeltproject.org/test")

            # Should only be called once (no retries)
            assert route.call_count == 1

    @respx.mock
    async def test_gives_up_after_max_retries(self) -> None:
        """Test request gives up after max_retries attempts."""
        route = respx.get("https://api.gdeltproject.org/test").mock(
            return_value=httpx.Response(503),
        )

        async with TestEndpoint(settings=GDELTSettings(max_retries=2)) as endpoint:
            with pytest.raises(APIUnavailableError):
                await endpoint._get("https://api.gdeltproject.org/test")

            # Should be called max_retries times
            assert route.call_count == 2


class TestAbstractMethod:
    """Test abstract method enforcement."""

    async def test_build_url_is_abstract(self) -> None:
        """Test _build_url must be implemented by subclasses."""

        class IncompleteEndpoint(BaseEndpoint):
            BASE_URL = "https://api.gdeltproject.org"
            # Missing _build_url implementation

        # Should not be able to instantiate without implementing abstract method
        with pytest.raises(TypeError):
            IncompleteEndpoint()  # type: ignore[abstract]
