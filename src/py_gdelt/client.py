"""Main GDELT client for unified access to all endpoints.

This module provides the GDELTClient class, which is the primary entry point
for accessing all GDELT data sources:
- Events, Mentions, GKG (via files or BigQuery)
- NGrams (files only)
- DOC, GEO, Context, TV, TVAI (REST APIs)

The client manages lifecycle of all dependencies (HTTP client, file source,
BigQuery source) and provides convenient namespace access to endpoints.

Example:
    Basic async usage:

    >>> from py_gdelt import GDELTClient
    >>> from py_gdelt.filters import EventFilter, DateRange
    >>> from datetime import date
    >>>
    >>> async with GDELTClient() as client:
    ...     # Query events
    ...     filter_obj = EventFilter(
    ...         date_range=DateRange(start=date(2024, 1, 1)),
    ...         actor1_country="USA"
    ...     )
    ...     events = await client.events.query(filter_obj)
    ...
    ...     # Search articles
    ...     articles = await client.doc.search("climate change")
    ...
    ...     # Access lookups
    ...     event_entry = client.lookups.cameo["14"]
    ...     event_name = event_entry.name  # "PROTEST"

    With custom configuration:

    >>> from pathlib import Path
    >>> settings = GDELTSettings(
    ...     config_path=Path("gdelt.toml"),
    ...     bigquery_project="my-project",
    ...     bigquery_credentials="/path/to/credentials.json"
    ... )
    >>> async with GDELTClient(settings=settings) as client:
    ...     events = await client.events.query(filter_obj)

    Synchronous usage:

    >>> with GDELTClient() as client:
    ...     events = client.events.query_sync(filter_obj)
"""

from __future__ import annotations

import asyncio
import logging
from functools import cached_property
from typing import TYPE_CHECKING, Any

import httpx

from py_gdelt.config import GDELTSettings
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
from py_gdelt.sources import BigQuerySource, FileSource


if TYPE_CHECKING:
    from pathlib import Path


__all__ = ["GDELTClient"]

logger = logging.getLogger(__name__)


class GDELTClient:
    """Main client for accessing all GDELT data sources.

    This is the primary entry point for the py-gdelt library. It manages the
    lifecycle of all dependencies (HTTP client, file source, BigQuery source)
    and provides convenient namespace access to all endpoints.

    The client can be used as either an async or sync context manager, and
    supports dependency injection for testing.

    Args:
        settings: Optional GDELTSettings instance. If None, creates default settings.
        config_path: Optional path to TOML configuration file. Only used if
            settings is None. If both are provided, settings takes precedence.
        http_client: Optional shared HTTP client for testing. If None, client
            creates and owns its own HTTP client. If provided, the lifecycle
            is managed externally and the client will not be closed on exit.

    Example:
        >>> async with GDELTClient() as client:
        ...     events = await client.events.query(filter_obj)
        ...     articles = await client.doc.search("climate")
        ...     theme = client.lookups.themes.get_category("ENV_CLIMATECHANGE")

        >>> # With config file
        >>> async with GDELTClient(config_path=Path("gdelt.toml")) as client:
        ...     pass

        >>> # With custom settings
        >>> settings = GDELTSettings(timeout=60, max_retries=5)
        >>> async with GDELTClient(settings=settings) as client:
        ...     pass

        >>> # With dependency injection for testing
        >>> async with httpx.AsyncClient() as http_client:
        ...     async with GDELTClient(http_client=http_client) as client:
        ...         pass
    """

    def __init__(
        self,
        settings: GDELTSettings | None = None,
        config_path: Path | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        # Initialize settings
        if settings is not None:
            self.settings = settings
        elif config_path is not None:
            self.settings = GDELTSettings(config_path=config_path)
        else:
            self.settings = GDELTSettings()

        # HTTP client management
        self._http_client = http_client
        self._owns_http_client = http_client is None

        # Source instances (created lazily)
        self._file_source: FileSource | None = None
        self._bigquery_source: BigQuerySource | None = None
        self._owns_sources = True

        # Lifecycle state
        self._initialized = False

    async def _initialize(self) -> None:
        """Initialize sources and HTTP client.

        Called automatically on first use via context manager.
        Creates HTTP client (if not injected) and initializes file source.
        BigQuery source is created only if credentials are configured.
        """
        if self._initialized:
            return

        # Create HTTP client if not injected
        if self._owns_http_client:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=self.settings.timeout,
                    write=10.0,
                    pool=5.0,
                ),
                follow_redirects=True,
            )

        # Initialize file source
        self._file_source = FileSource(
            settings=self.settings,
            client=self._http_client,
        )
        await self._file_source.__aenter__()

        # Initialize BigQuery source if credentials are configured
        if self.settings.bigquery_project and self.settings.bigquery_credentials:
            try:
                self._bigquery_source = BigQuerySource(settings=self.settings)
                logger.debug(
                    "Initialized BigQuerySource with project %s",
                    self.settings.bigquery_project,
                )
            except ImportError as e:
                # google-cloud-bigquery package not installed
                logger.warning(
                    "BigQuery package not installed: %s. "
                    "Install with: pip install py-gdelt[bigquery]",
                    e,
                )
                self._bigquery_source = None
            except (OSError, FileNotFoundError) as e:
                # Credentials file not found or not readable
                logger.warning(
                    "BigQuery credentials file error: %s. BigQuery fallback will be unavailable.",
                    e,
                )
                self._bigquery_source = None
            except Exception as e:  # noqa: BLE001
                # Catch all Google SDK errors without importing optional dependency
                # This is an error boundary - BigQuery is optional, errors should not crash
                logger.warning(
                    "Failed to initialize BigQuerySource (%s): %s. "
                    "BigQuery fallback will be unavailable.",
                    type(e).__name__,
                    e,
                )
                self._bigquery_source = None

        self._initialized = True
        logger.debug("GDELTClient initialized successfully")

    async def _cleanup(self) -> None:
        """Clean up resources.

        Closes file source, BigQuery source (if created), and HTTP client (if owned).
        """
        if not self._initialized:
            return

        # Close file source
        if self._file_source is not None:
            await self._file_source.__aexit__(None, None, None)
            self._file_source = None

        # BigQuery source doesn't need explicit cleanup (no persistent connections)
        self._bigquery_source = None

        # Close HTTP client if we own it
        if self._owns_http_client and self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

        self._initialized = False
        logger.debug("GDELTClient cleaned up successfully")

    async def __aenter__(self) -> GDELTClient:
        """Async context manager entry.

        Returns:
            Self for use in async with statement.

        Example:
            >>> async with GDELTClient() as client:
            ...     events = await client.events.query(filter_obj)
        """
        await self._initialize()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit.

        Cleans up all owned resources.

        Args:
            *args: Exception info (unused, but required by protocol).
        """
        await self._cleanup()

    def __enter__(self) -> GDELTClient:
        """Sync context manager entry.

        This provides synchronous (blocking) access to the client for use in
        non-async code. It uses asyncio.run() internally to manage the event loop.

        Important Limitations:
            - MUST be called from outside any existing async context/event loop.
              Calling from within an async function will raise RuntimeError.
            - Creates a new event loop for each context manager entry.
            - Use the async context manager (async with) when possible for
              better performance and compatibility.

        Returns:
            Self for use in with statement.

        Raises:
            RuntimeError: If called from within an already running event loop.

        Example:
            >>> # Correct: Used from synchronous code
            >>> with GDELTClient() as client:
            ...     events = client.events.query_sync(filter_obj)
            ...
            >>> # Wrong: Don't use from async code - use 'async with' instead
            >>> async def bad_example():
            ...     with GDELTClient() as client:  # RuntimeError!
            ...         pass
        """
        asyncio.run(self._initialize())
        return self

    def __exit__(self, *args: Any) -> None:
        """Sync context manager exit.

        Cleans up all owned resources. Uses asyncio.run() internally.

        Args:
            *args: Exception info (unused, but required by protocol).

        Raises:
            RuntimeError: If called from within an already running event loop.
        """
        asyncio.run(self._cleanup())

    # Endpoint namespaces (lazy initialization via cached_property)

    @cached_property
    def events(self) -> EventsEndpoint:
        """Access the Events endpoint.

        Provides methods for querying GDELT Events data from files or BigQuery.

        Returns:
            EventsEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
            ...     events = await client.events.query(filter_obj)
        """
        if self._file_source is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return EventsEndpoint(
            file_source=self._file_source,
            bigquery_source=self._bigquery_source,
            fallback_enabled=self.settings.fallback_to_bigquery,
        )

    @cached_property
    def mentions(self) -> MentionsEndpoint:
        """Access the Mentions endpoint.

        Provides methods for querying GDELT Mentions data from files or BigQuery.

        Returns:
            MentionsEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
            ...     mentions = await client.mentions.query("123456789", filter_obj)
        """
        if self._file_source is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return MentionsEndpoint(
            file_source=self._file_source,
            bigquery_source=self._bigquery_source,
            fallback_enabled=self.settings.fallback_to_bigquery,
        )

    @cached_property
    def gkg(self) -> GKGEndpoint:
        """Access the GKG (Global Knowledge Graph) endpoint.

        Provides methods for querying GDELT GKG data from files or BigQuery.

        Returns:
            GKGEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     filter_obj = GKGFilter(
            ...         date_range=DateRange(start=date(2024, 1, 1)),
            ...         themes=["ENV_CLIMATECHANGE"]
            ...     )
            ...     records = await client.gkg.query(filter_obj)
        """
        if self._file_source is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return GKGEndpoint(
            file_source=self._file_source,
            bigquery_source=self._bigquery_source,
            fallback_enabled=self.settings.fallback_to_bigquery,
        )

    @cached_property
    def ngrams(self) -> NGramsEndpoint:
        """Access the NGrams endpoint.

        Provides methods for querying GDELT NGrams data (files only).

        Returns:
            NGramsEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     filter_obj = NGramsFilter(
            ...         date_range=DateRange(start=date(2024, 1, 1)),
            ...         language="en"
            ...     )
            ...     records = await client.ngrams.query(filter_obj)
        """
        if self._file_source is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return NGramsEndpoint(
            settings=self.settings,
            file_source=self._file_source,
        )

    @cached_property
    def doc(self) -> DocEndpoint:
        """Access the DOC 2.0 API endpoint.

        Provides methods for searching GDELT articles via the DOC API.

        Returns:
            DocEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     articles = await client.doc.search("climate change", max_results=100)
        """
        if self._http_client is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return DocEndpoint(
            settings=self.settings,
            client=self._http_client,
        )

    @cached_property
    def geo(self) -> GeoEndpoint:
        """Access the GEO 2.0 API endpoint.

        Provides methods for querying geographic locations from news articles.

        Returns:
            GeoEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     result = await client.geo.search("earthquake", max_points=100)
        """
        if self._http_client is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return GeoEndpoint(
            settings=self.settings,
            client=self._http_client,
        )

    @cached_property
    def context(self) -> ContextEndpoint:
        """Access the Context 2.0 API endpoint.

        Provides methods for contextual analysis of search terms.

        Returns:
            ContextEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     result = await client.context.analyze("climate change")
        """
        if self._http_client is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return ContextEndpoint(
            settings=self.settings,
            client=self._http_client,
        )

    @cached_property
    def tv(self) -> TVEndpoint:
        """Access the TV API endpoint.

        Provides methods for querying television news transcripts.

        Returns:
            TVEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     clips = await client.tv.search("climate change", station="CNN")
        """
        if self._http_client is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return TVEndpoint(
            settings=self.settings,
            client=self._http_client,
        )

    @cached_property
    def tv_ai(self) -> TVAIEndpoint:
        """Access the TVAI API endpoint.

        Provides methods for AI-enhanced television news analysis.

        Returns:
            TVAIEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     result = await client.tv_ai.analyze("election coverage")
        """
        if self._http_client is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return TVAIEndpoint(
            settings=self.settings,
            client=self._http_client,
        )

    @cached_property
    def lookups(self) -> Lookups:
        """Access lookup tables for CAMEO codes, themes, and countries.

        Provides access to all GDELT lookup tables with lazy loading.

        Returns:
            Lookups instance for code/theme/country lookups.

        Example:
            >>> async with GDELTClient() as client:
            ...     # CAMEO codes
            ...     event_entry = client.lookups.cameo["14"]
            ...     event_name = event_entry.name  # "PROTEST"
            ...
            ...     # GKG themes
            ...     category = client.lookups.themes.get_category("ENV_CLIMATECHANGE")
            ...
            ...     # Country codes
            ...     iso_code = client.lookups.countries.fips_to_iso3("US")  # "USA"
        """
        return Lookups()
