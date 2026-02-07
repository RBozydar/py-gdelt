"""Tests for the main GDELTClient class.

This module tests:
- Client initialization with various configuration options
- Context manager lifecycle (async and sync)
- Endpoint namespace access
- Lookup table access
- Dependency injection for testing
- Resource cleanup and error handling
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from py_gdelt import GDELTClient, GDELTSettings
from py_gdelt.endpoints import (
    ContextEndpoint,
    DocEndpoint,
    EventsEndpoint,
    GeoEndpoint,
    GKGEndpoint,
    MentionsEndpoint,
    NGramsEndpoint,
    TVAIEndpoint,
    TVEndpoint,
)
from py_gdelt.lookups import Lookups


if TYPE_CHECKING:
    from pathlib import Path


class TestGDELTClientInit:
    """Test client initialization with various configurations."""

    def test_init_default(self) -> None:
        """Test initialization with default settings."""
        client = GDELTClient()
        assert client.settings is not None
        assert isinstance(client.settings, GDELTSettings)
        assert client._owns_http_client is True
        assert client._http_client is None  # Not created until context manager entry
        assert client._initialized is False

    def test_init_with_settings(self) -> None:
        """Test initialization with custom settings."""
        settings = GDELTSettings(timeout=60, max_retries=5)
        client = GDELTClient(settings=settings)
        assert client.settings is settings
        assert client.settings.timeout == 60
        assert client.settings.max_retries == 5

    def test_init_with_config_path(self, tmp_path: Path) -> None:
        """Test initialization with TOML config file."""
        config_file = tmp_path / "test_gdelt.toml"
        config_file.write_text("""
[gdelt]
timeout = 45
max_retries = 4
""")
        client = GDELTClient(config_path=config_file)
        assert client.settings.timeout == 45
        assert client.settings.max_retries == 4

    def test_init_settings_overrides_config_path(self, tmp_path: Path) -> None:
        """Test that settings parameter takes precedence over config_path."""
        config_file = tmp_path / "test_gdelt.toml"
        config_file.write_text("""
[gdelt]
timeout = 45
""")
        settings = GDELTSettings(timeout=60)
        client = GDELTClient(settings=settings, config_path=config_file)
        # settings should take precedence
        assert client.settings.timeout == 60

    @pytest.mark.asyncio
    async def test_init_with_injected_http_client(self) -> None:
        """Test initialization with injected HTTP client."""
        async with httpx.AsyncClient() as http_client:
            client = GDELTClient(http_client=http_client)
            assert client._http_client is http_client
            assert client._owns_http_client is False


class TestGDELTClientAsyncContextManager:
    """Test async context manager lifecycle."""

    @pytest.mark.asyncio
    async def test_context_manager_initializes_resources(self) -> None:
        """Test that entering context manager initializes resources."""
        client = GDELTClient()
        assert client._initialized is False

        async with client:
            assert client._initialized is True
            assert client._http_client is not None
            assert client._file_source is not None

    @pytest.mark.asyncio
    async def test_context_manager_cleans_up_resources(self) -> None:
        """Test that exiting context manager cleans up resources."""
        client = GDELTClient()

        async with client:
            assert client._initialized is True
            http_client = client._http_client
            file_source = client._file_source

        # After exit, resources should be cleaned up
        assert client._initialized is False
        assert client._http_client is None
        assert client._file_source is None

    @pytest.mark.asyncio
    async def test_context_manager_does_not_close_injected_client(self) -> None:
        """Test that injected HTTP client is not closed on exit."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        client = GDELTClient(http_client=mock_client)

        async with client:
            pass

        # Injected client should NOT be closed
        mock_client.aclose.assert_not_called()

    @pytest.mark.asyncio
    async def test_context_manager_closes_owned_client(self) -> None:
        """Test that owned HTTP client is closed on exit."""
        client = GDELTClient()

        async with client:
            http_client = client._http_client
            assert http_client is not None

        # Owned client should be closed (can't easily test without mocking)
        assert client._http_client is None

    @pytest.mark.asyncio
    async def test_bigquery_source_initialized_when_configured(self) -> None:
        """Test that BigQuery source is created when credentials are configured."""
        settings = GDELTSettings(
            bigquery_project="test-project",
            bigquery_credentials="/path/to/creds.json",
        )
        client = GDELTClient(settings=settings)

        with patch("py_gdelt.client.BigQuerySource") as mock_bq:
            mock_bq.return_value = MagicMock()
            async with client:
                # BigQuerySource should be initialized
                mock_bq.assert_called_once_with(settings=settings)

    @pytest.mark.asyncio
    async def test_bigquery_source_not_initialized_without_credentials(self) -> None:
        """Test that BigQuery source is not created without credentials."""
        client = GDELTClient()  # No BQ credentials

        async with client:
            assert client._bigquery_source is None

    @pytest.mark.asyncio
    async def test_bigquery_initialization_failure_logged(self) -> None:
        """Test that BigQuery initialization failures are logged but don't crash."""
        settings = GDELTSettings(
            bigquery_project="test-project",
            bigquery_credentials="/path/to/creds.json",
        )
        client = GDELTClient(settings=settings)

        with patch(
            "py_gdelt.client.BigQuerySource",
            side_effect=Exception("BQ init failed"),
        ):
            # Should not raise, just log warning
            async with client:
                assert client._bigquery_source is None


class TestGDELTClientSyncContextManager:
    """Test synchronous context manager lifecycle."""

    def test_sync_context_manager_works(self) -> None:
        """Test that sync context manager initializes and cleans up."""
        client = GDELTClient()

        with client:
            assert client._initialized is True

        assert client._initialized is False


class TestGDELTClientEndpointAccess:
    """Test endpoint namespace access."""

    @pytest.mark.asyncio
    async def test_events_endpoint_access(self) -> None:
        """Test accessing events endpoint."""
        async with GDELTClient() as client:
            endpoint = client.events
            assert isinstance(endpoint, EventsEndpoint)
            # Cached property should return same instance
            assert client.events is endpoint

    @pytest.mark.asyncio
    async def test_mentions_endpoint_access(self) -> None:
        """Test accessing mentions endpoint."""
        async with GDELTClient() as client:
            endpoint = client.mentions
            assert isinstance(endpoint, MentionsEndpoint)
            assert client.mentions is endpoint

    @pytest.mark.asyncio
    async def test_gkg_endpoint_access(self) -> None:
        """Test accessing GKG endpoint."""
        async with GDELTClient() as client:
            endpoint = client.gkg
            assert isinstance(endpoint, GKGEndpoint)
            assert client.gkg is endpoint

    @pytest.mark.asyncio
    async def test_ngrams_endpoint_access(self) -> None:
        """Test accessing NGrams endpoint."""
        async with GDELTClient() as client:
            endpoint = client.ngrams
            assert isinstance(endpoint, NGramsEndpoint)
            assert client.ngrams is endpoint

    @pytest.mark.asyncio
    async def test_doc_endpoint_access(self) -> None:
        """Test accessing DOC endpoint."""
        async with GDELTClient() as client:
            endpoint = client.doc
            assert isinstance(endpoint, DocEndpoint)
            assert client.doc is endpoint

    @pytest.mark.asyncio
    async def test_geo_endpoint_access(self) -> None:
        """Test accessing GEO endpoint."""
        async with GDELTClient() as client:
            endpoint = client.geo
            assert isinstance(endpoint, GeoEndpoint)
            assert client.geo is endpoint

    @pytest.mark.asyncio
    async def test_context_endpoint_access(self) -> None:
        """Test accessing Context endpoint."""
        async with GDELTClient() as client:
            endpoint = client.context
            assert isinstance(endpoint, ContextEndpoint)
            assert client.context is endpoint

    @pytest.mark.asyncio
    async def test_tv_endpoint_access(self) -> None:
        """Test accessing TV endpoint."""
        async with GDELTClient() as client:
            endpoint = client.tv
            assert isinstance(endpoint, TVEndpoint)
            assert client.tv is endpoint

    @pytest.mark.asyncio
    async def test_tv_ai_endpoint_access(self) -> None:
        """Test accessing TVAI endpoint."""
        async with GDELTClient() as client:
            endpoint = client.tv_ai
            assert isinstance(endpoint, TVAIEndpoint)
            assert client.tv_ai is endpoint

    def test_endpoint_access_before_initialization_raises(self) -> None:
        """Test that accessing endpoints before initialization raises error."""
        client = GDELTClient()
        with pytest.raises(RuntimeError, match="not initialized"):
            _ = client.events

    def test_rest_endpoint_access_before_initialization_raises(self) -> None:
        """Test that REST endpoints also raise before initialization."""
        client = GDELTClient()
        with pytest.raises(RuntimeError, match="not initialized"):
            _ = client.doc


class TestGDELTClientLookups:
    """Test lookup table access."""

    @pytest.mark.asyncio
    async def test_lookups_access(self) -> None:
        """Test accessing lookup tables."""
        async with GDELTClient() as client:
            lookups = client.lookups
            assert isinstance(lookups, Lookups)
            # Should be cached
            assert client.lookups is lookups

    def test_lookups_access_before_initialization(self) -> None:
        """Test that lookups can be accessed before initialization.

        Lookups don't require HTTP client or sources, so they should work
        even before the client is initialized.
        """
        client = GDELTClient()
        lookups = client.lookups
        assert isinstance(lookups, Lookups)

    @pytest.mark.asyncio
    async def test_lookups_cameo_codes(self) -> None:
        """Test CAMEO code lookup integration."""
        async with GDELTClient() as client:
            # Basic lookup should work
            cameo = client.lookups.cameo
            assert cameo is not None
            # Actual lookup verification (assumes CAMEOCodes is implemented)
            # assert "01" in cameo

    @pytest.mark.asyncio
    async def test_lookups_themes(self) -> None:
        """Test GKG themes lookup integration."""
        async with GDELTClient() as client:
            themes = client.lookups.themes
            assert themes is not None

    @pytest.mark.asyncio
    async def test_lookups_countries(self) -> None:
        """Test country codes lookup integration."""
        async with GDELTClient() as client:
            countries = client.lookups.countries
            assert countries is not None


class TestGDELTClientIntegration:
    """Integration tests for the full client workflow."""

    @pytest.mark.asyncio
    async def test_multiple_endpoint_access_in_one_session(self) -> None:
        """Test accessing multiple endpoints in a single session."""
        async with GDELTClient() as client:
            # All endpoints should be accessible
            events = client.events
            mentions = client.mentions
            gkg = client.gkg
            doc = client.doc
            lookups = client.lookups

            assert isinstance(events, EventsEndpoint)
            assert isinstance(mentions, MentionsEndpoint)
            assert isinstance(gkg, GKGEndpoint)
            assert isinstance(doc, DocEndpoint)
            assert isinstance(lookups, Lookups)

    @pytest.mark.asyncio
    async def test_endpoint_shares_http_client(self) -> None:
        """Test that REST endpoints share the same HTTP client."""
        async with GDELTClient() as client:
            doc = client.doc
            geo = client.geo
            context = client.context

            # All should use the same HTTP client instance
            assert doc._client is geo._client
            assert geo._client is context._client
            assert doc._client is client._http_client

    @pytest.mark.asyncio
    async def test_file_based_endpoints_share_file_source(self) -> None:
        """Test that file-based endpoints share the same FileSource."""
        async with GDELTClient() as client:
            events = client.events
            mentions = client.mentions
            gkg = client.gkg

            # All should use the same FileSource instance
            assert events._fetcher._file is client._file_source
            assert mentions._fetcher._file is client._file_source
            assert gkg._fetcher._file is client._file_source

    @pytest.mark.asyncio
    async def test_client_with_all_features_enabled(self) -> None:
        """Test client with BigQuery and all settings configured."""
        settings = GDELTSettings(
            bigquery_project="test-project",
            bigquery_credentials="/fake/path.json",
            timeout=60,
            max_retries=5,
            fallback_to_bigquery=True,
            validate_codes=True,
        )

        with patch("py_gdelt.client.BigQuerySource"):
            async with GDELTClient(settings=settings) as client:
                # All features should be accessible
                assert client.events is not None
                assert client.doc is not None
                assert client.lookups is not None


class TestGDELTClientBigQueryProperty:
    """Test client.bigquery property access."""

    @pytest.mark.asyncio
    async def test_bigquery_property_returns_source(self) -> None:
        """Test that client.bigquery returns BigQuerySource when configured."""
        settings = GDELTSettings(
            bigquery_project="test-project",
            bigquery_credentials="/fake/path.json",
        )

        mock_bq_instance = MagicMock()
        with patch("py_gdelt.client.BigQuerySource", return_value=mock_bq_instance):
            async with GDELTClient(settings=settings) as client:
                assert client.bigquery is mock_bq_instance

    @pytest.mark.asyncio
    async def test_bigquery_property_returns_none(self) -> None:
        """Test that client.bigquery returns None when not configured."""
        async with GDELTClient() as client:
            assert client.bigquery is None
