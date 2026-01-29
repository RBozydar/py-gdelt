# Client API

## `GDELTClient`

Main client for accessing all GDELT data sources.

This is the primary entry point for the py-gdelt library. It manages the lifecycle of all dependencies (HTTP client, file source, BigQuery source) and provides convenient namespace access to all endpoints.

The client can be used as either an async or sync context manager, and supports dependency injection for testing.

Parameters:

| Name          | Type            | Description | Default                                                                                                                                                                                    |
| ------------- | --------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `settings`    | \`GDELTSettings | None\`      | Optional GDELTSettings instance. If None, creates default settings.                                                                                                                        |
| `config_path` | \`Path          | None\`      | Optional path to TOML configuration file. Only used if settings is None. If both are provided, settings takes precedence.                                                                  |
| `http_client` | \`AsyncClient   | None\`      | Optional shared HTTP client for testing. If None, client creates and owns its own HTTP client. If provided, the lifecycle is managed externally and the client will not be closed on exit. |

Example

> > > async with GDELTClient() as client: ... events = await client.events.query(filter_obj) ... articles = await client.doc.search("climate") ... theme = client.lookups.themes.get_category("ENV_CLIMATECHANGE")
> > >
> > > ### With config file
> > >
> > > async with GDELTClient(config_path=Path("gdelt.toml")) as client: ... pass
> > >
> > > ### With custom settings
> > >
> > > settings = GDELTSettings(timeout=60, max_retries=5) async with GDELTClient(settings=settings) as client: ... pass
> > >
> > > ### With dependency injection for testing
> > >
> > > async with httpx.AsyncClient() as http_client: ... async with GDELTClient(http_client=http_client) as client: ... pass

Source code in `src/py_gdelt/client.py`

```
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
    def tv_ngrams(self) -> TVNGramsEndpoint:
        """Access the TV NGrams endpoint.

        Provides methods for querying word frequency from TV broadcast closed captions.

        Returns:
            TVNGramsEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     filter_obj = BroadcastNGramsFilter(
            ...         date_range=DateRange(start=date(2024, 1, 1)),
            ...         station="CNN"
            ...     )
            ...     records = await client.tv_ngrams.query(filter_obj)
        """
        if self._file_source is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return TVNGramsEndpoint(
            settings=self.settings,
            file_source=self._file_source,
        )

    @cached_property
    def radio_ngrams(self) -> RadioNGramsEndpoint:
        """Access the Radio NGrams endpoint.

        Provides methods for querying word frequency from radio broadcast transcripts.

        Returns:
            RadioNGramsEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     filter_obj = BroadcastNGramsFilter(
            ...         date_range=DateRange(start=date(2024, 1, 1)),
            ...         station="NPR"
            ...     )
            ...     records = await client.radio_ngrams.query(filter_obj)
        """
        if self._file_source is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return RadioNGramsEndpoint(
            settings=self.settings,
            file_source=self._file_source,
        )

    @cached_property
    def vgkg(self) -> VGKGEndpoint:
        """Access the VGKG (Visual Global Knowledge Graph) endpoint.

        Provides methods for querying Google Cloud Vision API analysis of news images.

        Returns:
            VGKGEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     filter_obj = VGKGFilter(
            ...         date_range=DateRange(start=date(2024, 1, 1)),
            ...         domain="cnn.com"
            ...     )
            ...     records = await client.vgkg.query(filter_obj)
        """
        if self._file_source is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return VGKGEndpoint(
            settings=self.settings,
            file_source=self._file_source,
        )

    @cached_property
    def tv_gkg(self) -> TVGKGEndpoint:
        """Access the TV GKG (TV Global Knowledge Graph) endpoint.

        Provides methods for querying GKG data from TV broadcast closed captions.

        Returns:
            TVGKGEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     filter_obj = TVGKGFilter(
            ...         date_range=DateRange(start=date(2024, 1, 1)),
            ...         station="CNN"
            ...     )
            ...     records = await client.tv_gkg.query(filter_obj)
        """
        if self._file_source is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return TVGKGEndpoint(
            settings=self.settings,
            file_source=self._file_source,
        )

    @cached_property
    def graphs(self) -> GraphEndpoint:
        """Access the Graph datasets endpoint.

        Provides methods for querying GDELT Graph datasets (GQG, GEG, GFG, GGG, GEMG, GAL)
        from file downloads.

        Returns:
            GraphEndpoint instance.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     from py_gdelt.filters import GQGFilter, DateRange
            ...     filter_obj = GQGFilter(
            ...         date_range=DateRange(start=date(2025, 1, 20))
            ...     )
            ...     result = await client.graphs.query_gqg(filter_obj)
            ...     for record in result:
            ...         print(record.quotes)
        """
        if self._file_source is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return GraphEndpoint(
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
    def lowerthird(self) -> LowerThirdEndpoint:
        """Access the LowerThird (Chyron) API.

        Provides methods for searching OCR'd TV chyrons (lower-third text overlays).

        Returns:
            LowerThirdEndpoint for searching TV chyrons.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     clips = await client.lowerthird.search("breaking news")
        """
        if self._http_client is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return LowerThirdEndpoint(
            settings=self.settings,
            client=self._http_client,
        )

    @cached_property
    def tvv(self) -> TVVEndpoint:
        """Access the TV Visual (TVV) API for channel inventory.

        Provides methods for retrieving TV channel metadata.

        Returns:
            TVVEndpoint for channel metadata.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     channels = await client.tvv.get_inventory()
        """
        if self._http_client is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return TVVEndpoint(
            settings=self.settings,
            client=self._http_client,
        )

    @cached_property
    def gkg_geojson(self) -> GKGGeoJSONEndpoint:
        """Access the GKG GeoJSON API (v1.0 Legacy).

        Provides methods for querying geographic GKG data as GeoJSON.

        Returns:
            GKGGeoJSONEndpoint for geographic GKG queries.

        Raises:
            RuntimeError: If client not initialized (use context manager).

        Example:
            >>> async with GDELTClient() as client:
            ...     result = await client.gkg_geojson.search("TERROR", timespan=60)
        """
        if self._http_client is None:
            msg = "GDELTClient not initialized. Use 'async with GDELTClient() as client:'"
            raise RuntimeError(msg)
        return GKGGeoJSONEndpoint(
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
```

### `events`

Access the Events endpoint.

Provides methods for querying GDELT Events data from files or BigQuery.

Returns:

| Type             | Description              |
| ---------------- | ------------------------ |
| `EventsEndpoint` | EventsEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1))) ... events = await client.events.query(filter_obj)

### `mentions`

Access the Mentions endpoint.

Provides methods for querying GDELT Mentions data from files or BigQuery.

Returns:

| Type               | Description                |
| ------------------ | -------------------------- |
| `MentionsEndpoint` | MentionsEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1))) ... mentions = await client.mentions.query("123456789", filter_obj)

### `gkg`

Access the GKG (Global Knowledge Graph) endpoint.

Provides methods for querying GDELT GKG data from files or BigQuery.

Returns:

| Type          | Description           |
| ------------- | --------------------- |
| `GKGEndpoint` | GKGEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... filter_obj = GKGFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... themes=["ENV_CLIMATECHANGE"] ... ) ... records = await client.gkg.query(filter_obj)

### `ngrams`

Access the NGrams endpoint.

Provides methods for querying GDELT NGrams data (files only).

Returns:

| Type             | Description              |
| ---------------- | ------------------------ |
| `NGramsEndpoint` | NGramsEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... filter_obj = NGramsFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... language="en" ... ) ... records = await client.ngrams.query(filter_obj)

### `tv_ngrams`

Access the TV NGrams endpoint.

Provides methods for querying word frequency from TV broadcast closed captions.

Returns:

| Type               | Description                |
| ------------------ | -------------------------- |
| `TVNGramsEndpoint` | TVNGramsEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... filter_obj = BroadcastNGramsFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... station="CNN" ... ) ... records = await client.tv_ngrams.query(filter_obj)

### `radio_ngrams`

Access the Radio NGrams endpoint.

Provides methods for querying word frequency from radio broadcast transcripts.

Returns:

| Type                  | Description                   |
| --------------------- | ----------------------------- |
| `RadioNGramsEndpoint` | RadioNGramsEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... filter_obj = BroadcastNGramsFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... station="NPR" ... ) ... records = await client.radio_ngrams.query(filter_obj)

### `vgkg`

Access the VGKG (Visual Global Knowledge Graph) endpoint.

Provides methods for querying Google Cloud Vision API analysis of news images.

Returns:

| Type           | Description            |
| -------------- | ---------------------- |
| `VGKGEndpoint` | VGKGEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... filter_obj = VGKGFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... domain="cnn.com" ... ) ... records = await client.vgkg.query(filter_obj)

### `tv_gkg`

Access the TV GKG (TV Global Knowledge Graph) endpoint.

Provides methods for querying GKG data from TV broadcast closed captions.

Returns:

| Type            | Description             |
| --------------- | ----------------------- |
| `TVGKGEndpoint` | TVGKGEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... filter_obj = TVGKGFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... station="CNN" ... ) ... records = await client.tv_gkg.query(filter_obj)

### `graphs`

Access the Graph datasets endpoint.

Provides methods for querying GDELT Graph datasets (GQG, GEG, GFG, GGG, GEMG, GAL) from file downloads.

Returns:

| Type            | Description             |
| --------------- | ----------------------- |
| `GraphEndpoint` | GraphEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... from py_gdelt.filters import GQGFilter, DateRange ... filter_obj = GQGFilter( ... date_range=DateRange(start=date(2025, 1, 20)) ... ) ... result = await client.graphs.query_gqg(filter_obj) ... for record in result: ... print(record.quotes)

### `doc`

Access the DOC 2.0 API endpoint.

Provides methods for searching GDELT articles via the DOC API.

Returns:

| Type          | Description           |
| ------------- | --------------------- |
| `DocEndpoint` | DocEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... articles = await client.doc.search("climate change", max_results=100)

### `geo`

Access the GEO 2.0 API endpoint.

Provides methods for querying geographic locations from news articles.

Returns:

| Type          | Description           |
| ------------- | --------------------- |
| `GeoEndpoint` | GeoEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... result = await client.geo.search("earthquake", max_points=100)

### `context`

Access the Context 2.0 API endpoint.

Provides methods for contextual analysis of search terms.

Returns:

| Type              | Description               |
| ----------------- | ------------------------- |
| `ContextEndpoint` | ContextEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... result = await client.context.analyze("climate change")

### `tv`

Access the TV API endpoint.

Provides methods for querying television news transcripts.

Returns:

| Type         | Description          |
| ------------ | -------------------- |
| `TVEndpoint` | TVEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... clips = await client.tv.search("climate change", station="CNN")

### `tv_ai`

Access the TVAI API endpoint.

Provides methods for AI-enhanced television news analysis.

Returns:

| Type           | Description            |
| -------------- | ---------------------- |
| `TVAIEndpoint` | TVAIEndpoint instance. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... result = await client.tv_ai.analyze("election coverage")

### `lowerthird`

Access the LowerThird (Chyron) API.

Provides methods for searching OCR'd TV chyrons (lower-third text overlays).

Returns:

| Type                 | Description                                  |
| -------------------- | -------------------------------------------- |
| `LowerThirdEndpoint` | LowerThirdEndpoint for searching TV chyrons. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... clips = await client.lowerthird.search("breaking news")

### `tvv`

Access the TV Visual (TVV) API for channel inventory.

Provides methods for retrieving TV channel metadata.

Returns:

| Type          | Description                       |
| ------------- | --------------------------------- |
| `TVVEndpoint` | TVVEndpoint for channel metadata. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... channels = await client.tvv.get_inventory()

### `gkg_geojson`

Access the GKG GeoJSON API (v1.0 Legacy).

Provides methods for querying geographic GKG data as GeoJSON.

Returns:

| Type                 | Description                                    |
| -------------------- | ---------------------------------------------- |
| `GKGGeoJSONEndpoint` | GKGGeoJSONEndpoint for geographic GKG queries. |

Raises:

| Type           | Description                                      |
| -------------- | ------------------------------------------------ |
| `RuntimeError` | If client not initialized (use context manager). |

Example

> > > async with GDELTClient() as client: ... result = await client.gkg_geojson.search("TERROR", timespan=60)

### `lookups`

Access lookup tables for CAMEO codes, themes, and countries.

Provides access to all GDELT lookup tables with lazy loading.

Returns:

| Type      | Description                                      |
| --------- | ------------------------------------------------ |
| `Lookups` | Lookups instance for code/theme/country lookups. |

Example

> > > async with GDELTClient() as client: ... # CAMEO codes ... event_entry = client.lookups.cameo["14"] ... event_name = event_entry.name # "PROTEST" ... ... # GKG themes ... category = client.lookups.themes.get_category("ENV_CLIMATECHANGE") ... ... # Country codes ... iso_code = client.lookups.countries.fips_to_iso3("US") # "USA"

### `__aenter__()`

Async context manager entry.

Returns:

| Type          | Description                           |
| ------------- | ------------------------------------- |
| `GDELTClient` | Self for use in async with statement. |

Example

> > > async with GDELTClient() as client: ... events = await client.events.query(filter_obj)

Source code in `src/py_gdelt/client.py`

```
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
```

### `__aexit__(*args)`

Async context manager exit.

Cleans up all owned resources.

Parameters:

| Name    | Type  | Description                                        | Default |
| ------- | ----- | -------------------------------------------------- | ------- |
| `*args` | `Any` | Exception info (unused, but required by protocol). | `()`    |

Source code in `src/py_gdelt/client.py`

```
async def __aexit__(self, *args: Any) -> None:
    """Async context manager exit.

    Cleans up all owned resources.

    Args:
        *args: Exception info (unused, but required by protocol).
    """
    await self._cleanup()
```

### `__enter__()`

Sync context manager entry.

This provides synchronous (blocking) access to the client for use in non-async code. It uses asyncio.run() internally to manage the event loop.

Important Limitations

- MUST be called from outside any existing async context/event loop. Calling from within an async function will raise RuntimeError.
- Creates a new event loop for each context manager entry.
- Use the async context manager (async with) when possible for better performance and compatibility.

Returns:

| Type          | Description                     |
| ------------- | ------------------------------- |
| `GDELTClient` | Self for use in with statement. |

Raises:

| Type           | Description                                          |
| -------------- | ---------------------------------------------------- |
| `RuntimeError` | If called from within an already running event loop. |

Example

> > > #### Correct: Used from synchronous code
> > >
> > > with GDELTClient() as client: ... events = client.events.query_sync(filter_obj) ...
> > >
> > > #### Wrong: Don't use from async code - use 'async with' instead
> > >
> > > async def bad_example(): ... with GDELTClient() as client: # RuntimeError! ... pass

Source code in `src/py_gdelt/client.py`

```
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
```

### `__exit__(*args)`

Sync context manager exit.

Cleans up all owned resources. Uses asyncio.run() internally.

Parameters:

| Name    | Type  | Description                                        | Default |
| ------- | ----- | -------------------------------------------------- | ------- |
| `*args` | `Any` | Exception info (unused, but required by protocol). | `()`    |

Raises:

| Type           | Description                                          |
| -------------- | ---------------------------------------------------- |
| `RuntimeError` | If called from within an already running event loop. |

Source code in `src/py_gdelt/client.py`

```
def __exit__(self, *args: Any) -> None:
    """Sync context manager exit.

    Cleans up all owned resources. Uses asyncio.run() internally.

    Args:
        *args: Exception info (unused, but required by protocol).

    Raises:
        RuntimeError: If called from within an already running event loop.
    """
    asyncio.run(self._cleanup())
```

## `GDELTSettings`

Bases: `BaseSettings`

Configuration settings for the GDELT client library.

Settings can be configured via:

- Environment variables with GDELT\_ prefix (e.g., GDELT_TIMEOUT=60)
- TOML configuration file passed to config_path parameter
- Default values

Environment variables take precedence over TOML configuration.

Parameters:

| Name          | Type   | Description                                            | Default                                                                                                                                               |
| ------------- | ------ | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `config_path` | \`Path | None\`                                                 | Optional path to TOML configuration file. If provided and exists, settings will be loaded from it. Environment variables will override TOML settings. |
| `**kwargs`    | `Any`  | Additional keyword arguments for setting field values. | `{}`                                                                                                                                                  |

Attributes:

| Name                       | Type   | Description                                                    |
| -------------------------- | ------ | -------------------------------------------------------------- |
| `model_config`             |        | Pydantic settings configuration (env prefix, case sensitivity) |
| `bigquery_project`         | \`str  | None\`                                                         |
| `bigquery_credentials`     | \`str  | None\`                                                         |
| `cache_dir`                | `Path` | Directory for caching downloaded GDELT data                    |
| `cache_ttl`                | `int`  | Cache time-to-live in seconds                                  |
| `master_file_list_ttl`     | `int`  | Master file list cache TTL in seconds                          |
| `max_retries`              | `int`  | Maximum number of HTTP request retries                         |
| `timeout`                  | `int`  | HTTP request timeout in seconds                                |
| `max_concurrent_requests`  | `int`  | Maximum concurrent HTTP requests                               |
| `max_concurrent_downloads` | `int`  | Maximum concurrent file downloads                              |
| `fallback_to_bigquery`     | `bool` | Whether to fallback to BigQuery when APIs fail                 |
| `validate_codes`           | `bool` | Whether to validate CAMEO/country codes                        |

Example

> > > ### Using defaults
> > >
> > > settings = GDELTSettings()
> > >
> > > ### Loading from TOML file
> > >
> > > settings = GDELTSettings(config_path=Path("gdelt.toml"))
> > >
> > > ### Environment variables override TOML
> > >
> > > import os os.environ["GDELT_TIMEOUT"] = "60" settings = GDELTSettings() settings.timeout 60

Source code in `src/py_gdelt/config.py`

```
class GDELTSettings(BaseSettings):
    """Configuration settings for the GDELT client library.

    Settings can be configured via:
    - Environment variables with GDELT_ prefix (e.g., GDELT_TIMEOUT=60)
    - TOML configuration file passed to config_path parameter
    - Default values

    Environment variables take precedence over TOML configuration.

    Args:
        config_path: Optional path to TOML configuration file.
            If provided and exists, settings will be loaded from it.
            Environment variables will override TOML settings.
        **kwargs: Additional keyword arguments for setting field values.

    Attributes:
        model_config: Pydantic settings configuration (env prefix, case sensitivity)
        bigquery_project: Google Cloud project ID for BigQuery access
        bigquery_credentials: Path to Google Cloud credentials JSON file
        cache_dir: Directory for caching downloaded GDELT data
        cache_ttl: Cache time-to-live in seconds
        master_file_list_ttl: Master file list cache TTL in seconds
        max_retries: Maximum number of HTTP request retries
        timeout: HTTP request timeout in seconds
        max_concurrent_requests: Maximum concurrent HTTP requests
        max_concurrent_downloads: Maximum concurrent file downloads
        fallback_to_bigquery: Whether to fallback to BigQuery when APIs fail
        validate_codes: Whether to validate CAMEO/country codes

    Example:
        >>> # Using defaults
        >>> settings = GDELTSettings()

        >>> # Loading from TOML file
        >>> settings = GDELTSettings(config_path=Path("gdelt.toml"))

        >>> # Environment variables override TOML
        >>> import os
        >>> os.environ["GDELT_TIMEOUT"] = "60"
        >>> settings = GDELTSettings()
        >>> settings.timeout
        60
    """

    model_config = SettingsConfigDict(
        env_prefix="GDELT_",
        case_sensitive=False,
        extra="ignore",
    )

    # BigQuery settings (optional)
    bigquery_project: str | None = Field(
        default=None,
        description="Google Cloud project ID for BigQuery access",
    )
    bigquery_credentials: str | None = Field(
        default=None,
        description="Path to Google Cloud credentials JSON file",
    )

    # Cache settings
    cache_dir: Path = Field(
        default_factory=lambda: Path.home() / ".cache" / "gdelt",
        description="Directory for caching downloaded GDELT data",
    )
    cache_ttl: int = Field(
        default=3600,
        description="Cache time-to-live in seconds",
    )
    master_file_list_ttl: int = Field(
        default=300,
        description="Master file list cache TTL in seconds (default 5 minutes)",
    )

    # HTTP settings
    max_retries: int = Field(
        default=3,
        description="Maximum number of HTTP request retries",
    )
    timeout: int = Field(
        default=30,
        description="HTTP request timeout in seconds",
    )
    max_concurrent_requests: int = Field(
        default=10,
        description="Maximum concurrent HTTP requests",
    )
    max_concurrent_downloads: int = Field(
        default=10,
        description="Maximum concurrent file downloads",
    )

    # Behavior settings
    fallback_to_bigquery: bool = Field(
        default=True,
        description="Whether to fallback to BigQuery when APIs fail",
    )
    validate_codes: bool = Field(
        default=True,
        description="Whether to validate CAMEO/country codes",
    )

    # Class variable to store config_path during initialization
    _current_config_path: Path | None = None

    def __init__(self, config_path: Path | None = None, **kwargs: Any) -> None:
        # Store config_path temporarily on class for settings_customise_sources
        GDELTSettings._current_config_path = config_path
        try:
            # Initialize the parent BaseSettings
            super().__init__(**kwargs)
        finally:
            # Clean up class variable
            GDELTSettings._current_config_path = None

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        **_kwargs: Any,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize settings sources to include TOML configuration.

        The order of sources determines precedence (first source wins):
        1. Init settings (kwargs passed to __init__)
        2. Environment variables (GDELT_ prefix)
        3. TOML configuration file
        4. Default values

        Args:
            settings_cls: The settings class being customized.
            init_settings: Settings from __init__ kwargs.
            env_settings: Settings from environment variables.
            dotenv_settings: Settings from .env file (unused).
            file_secret_settings: Settings from secret files (unused).
            **_kwargs: Additional keyword arguments (unused).

        Returns:
            Tuple of settings sources in priority order.
        """
        # Get config_path from class variable set in __init__
        config_path = cls._current_config_path
        toml_source = TOMLConfigSource(settings_cls, config_path=config_path)

        # Return sources in priority order (first wins)
        return (
            init_settings,  # Highest priority: explicit kwargs
            env_settings,  # Environment variables
            toml_source,  # TOML configuration
            # Default values are handled by Pydantic automatically
        )
```

### `settings_customise_sources(settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings, **_kwargs)`

Customize settings sources to include TOML configuration.

The order of sources determines precedence (first source wins):

1. Init settings (kwargs passed to **init**)
1. Environment variables (GDELT\_ prefix)
1. TOML configuration file
1. Default values

Parameters:

| Name                   | Type                         | Description                            | Default    |
| ---------------------- | ---------------------------- | -------------------------------------- | ---------- |
| `settings_cls`         | `type[BaseSettings]`         | The settings class being customized.   | *required* |
| `init_settings`        | `PydanticBaseSettingsSource` | Settings from init kwargs.             | *required* |
| `env_settings`         | `PydanticBaseSettingsSource` | Settings from environment variables.   | *required* |
| `dotenv_settings`      | `PydanticBaseSettingsSource` | Settings from .env file (unused).      | *required* |
| `file_secret_settings` | `PydanticBaseSettingsSource` | Settings from secret files (unused).   | *required* |
| `**_kwargs`            | `Any`                        | Additional keyword arguments (unused). | `{}`       |

Returns:

| Type                                     | Description                                  |
| ---------------------------------------- | -------------------------------------------- |
| `tuple[PydanticBaseSettingsSource, ...]` | Tuple of settings sources in priority order. |

Source code in `src/py_gdelt/config.py`

```
@classmethod
def settings_customise_sources(
    cls,
    settings_cls: type[BaseSettings],
    init_settings: PydanticBaseSettingsSource,
    env_settings: PydanticBaseSettingsSource,
    dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    **_kwargs: Any,
) -> tuple[PydanticBaseSettingsSource, ...]:
    """Customize settings sources to include TOML configuration.

    The order of sources determines precedence (first source wins):
    1. Init settings (kwargs passed to __init__)
    2. Environment variables (GDELT_ prefix)
    3. TOML configuration file
    4. Default values

    Args:
        settings_cls: The settings class being customized.
        init_settings: Settings from __init__ kwargs.
        env_settings: Settings from environment variables.
        dotenv_settings: Settings from .env file (unused).
        file_secret_settings: Settings from secret files (unused).
        **_kwargs: Additional keyword arguments (unused).

    Returns:
        Tuple of settings sources in priority order.
    """
    # Get config_path from class variable set in __init__
    config_path = cls._current_config_path
    toml_source = TOMLConfigSource(settings_cls, config_path=config_path)

    # Return sources in priority order (first wins)
    return (
        init_settings,  # Highest priority: explicit kwargs
        env_settings,  # Environment variables
        toml_source,  # TOML configuration
        # Default values are handled by Pydantic automatically
    )
```
