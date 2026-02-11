# Endpoints API

## File-Based Endpoints

### EventsEndpoint

### `EventsEndpoint`

Endpoint for querying GDELT Events data.

This endpoint orchestrates querying GDELT Events data from multiple sources (files and BigQuery) using a DataFetcher. It handles:

- Source selection and fallback logic
- Type conversion from internal \_RawEvent to public Event models
- Optional deduplication
- Both streaming and batch query modes

The endpoint uses dependency injection to receive source instances, making it easy to test and configure.

Parameters:

| Name               | Type             | Description                                               | Default                                               |
| ------------------ | ---------------- | --------------------------------------------------------- | ----------------------------------------------------- |
| `file_source`      | `FileSource`     | FileSource instance for downloading GDELT files           | *required*                                            |
| `bigquery_source`  | \`BigQuerySource | None\`                                                    | Optional BigQuerySource instance for fallback queries |
| `fallback_enabled` | `bool`           | Whether to fallback to BigQuery on errors (default: True) | `True`                                                |

Note

BigQuery fallback only activates if both fallback_enabled=True AND bigquery_source is provided AND credentials are configured.

Example

> > > from py_gdelt.sources import FileSource from py_gdelt.filters import DateRange, EventFilter from datetime import date
> > >
> > > async with FileSource() as file_source: ... endpoint = EventsEndpoint(file_source=file_source) ... filter_obj = EventFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... actor1_country="USA", ... ) ... # Batch query ... result = await endpoint.query(filter_obj, deduplicate=True) ... for event in result: ... print(event.global_event_id) ... # Streaming query ... async for event in endpoint.stream(filter_obj): ... process(event)

Source code in `src/py_gdelt/endpoints/events.py`

```
class EventsEndpoint:
    """Endpoint for querying GDELT Events data.

    This endpoint orchestrates querying GDELT Events data from multiple sources
    (files and BigQuery) using a DataFetcher. It handles:
    - Source selection and fallback logic
    - Type conversion from internal _RawEvent to public Event models
    - Optional deduplication
    - Both streaming and batch query modes

    The endpoint uses dependency injection to receive source instances, making
    it easy to test and configure.

    Args:
        file_source: FileSource instance for downloading GDELT files
        bigquery_source: Optional BigQuerySource instance for fallback queries
        fallback_enabled: Whether to fallback to BigQuery on errors (default: True)

    Note:
        BigQuery fallback only activates if both fallback_enabled=True AND
        bigquery_source is provided AND credentials are configured.

    Example:
        >>> from py_gdelt.sources import FileSource
        >>> from py_gdelt.filters import DateRange, EventFilter
        >>> from datetime import date
        >>>
        >>> async with FileSource() as file_source:
        ...     endpoint = EventsEndpoint(file_source=file_source)
        ...     filter_obj = EventFilter(
        ...         date_range=DateRange(start=date(2024, 1, 1)),
        ...         actor1_country="USA",
        ...     )
        ...     # Batch query
        ...     result = await endpoint.query(filter_obj, deduplicate=True)
        ...     for event in result:
        ...         print(event.global_event_id)
        ...     # Streaming query
        ...     async for event in endpoint.stream(filter_obj):
        ...         process(event)
    """

    def __init__(
        self,
        file_source: FileSource,
        bigquery_source: BigQuerySource | None = None,
        *,
        fallback_enabled: bool = True,
    ) -> None:
        # Import DataFetcher here to avoid circular imports
        from py_gdelt.sources.fetcher import DataFetcher

        self._fetcher: DataFetcher = DataFetcher(
            file_source=file_source,
            bigquery_source=bigquery_source,
            fallback_enabled=fallback_enabled,
        )

        logger.debug(
            "EventsEndpoint initialized (fallback_enabled=%s)",
            fallback_enabled,
        )

    async def query(
        self,
        filter_obj: EventFilter,
        *,
        deduplicate: bool = False,
        dedupe_strategy: DedupeStrategy | None = None,
        use_bigquery: bool = False,
    ) -> FetchResult[Event]:
        """Query GDELT Events with automatic fallback.

        This is a batch query method that materializes all results into memory.
        For large datasets, prefer stream() for memory-efficient iteration.

        Files are always tried first (free, no credentials), with automatic fallback
        to BigQuery on rate limit/error if credentials are configured.

        Args:
            filter_obj: Event filter with date range and query parameters
            deduplicate: If True, deduplicate events based on dedupe_strategy
            dedupe_strategy: Deduplication strategy (default: URL_DATE_LOCATION)
            use_bigquery: If True, skip files and use BigQuery directly

        Returns:
            FetchResult containing Event instances. Use .data to access the list,
            .failed to see any failed requests, and .complete to check if all
            requests succeeded.

        Raises:
            RateLimitError: If rate limited and fallback not available
            APIError: If download fails and fallback not available
            ConfigurationError: If BigQuery requested but not configured

        Example:
            >>> filter_obj = EventFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     actor1_country="USA",
            ... )
            >>> result = await endpoint.query(filter_obj, deduplicate=True)
            >>> print(f"Found {len(result)} unique events")
            >>> for event in result:
            ...     print(event.global_event_id)
        """
        # Default dedupe strategy
        if deduplicate and dedupe_strategy is None:
            dedupe_strategy = DedupeStrategy.URL_DATE_LOCATION

        # Fetch raw events first (for deduplication)
        raw_events_list: list[_RawEvent] = [
            raw_event
            async for raw_event in self._fetcher.fetch_events(
                filter_obj,
                use_bigquery=use_bigquery,
            )
        ]

        logger.info("Fetched %d raw events from sources", len(raw_events_list))

        # Apply deduplication on raw events if requested
        # Deduplication happens on _RawEvent which implements HasDedupeFields protocol
        if deduplicate and dedupe_strategy is not None:
            original_count = len(raw_events_list)
            # Convert to iterator, deduplicate, then back to list
            raw_events_list = list(apply_dedup(iter(raw_events_list), dedupe_strategy))
            logger.info(
                "Deduplicated %d events to %d unique (strategy=%s)",
                original_count,
                len(raw_events_list),
                dedupe_strategy,
            )

        # Convert _RawEvent to Event models after deduplication
        events: list[Event] = []
        for raw_event in raw_events_list:
            event = Event.from_raw(raw_event)
            events.append(event)

        logger.info("Converted %d events to Event models", len(events))

        # Return as FetchResult (no failed requests tracked yet)
        return FetchResult(data=events)

    async def stream(
        self,
        filter_obj: EventFilter,
        *,
        deduplicate: bool = False,
        dedupe_strategy: DedupeStrategy | None = None,
        use_bigquery: bool = False,
    ) -> AsyncIterator[Event]:
        """Stream GDELT Events with memory-efficient iteration.

        This is a streaming method that yields events one at a time, making it
        suitable for large datasets. Memory usage is constant regardless of
        result size.

        Files are always tried first (free, no credentials), with automatic fallback
        to BigQuery on rate limit/error if credentials are configured.

        Args:
            filter_obj: Event filter with date range and query parameters
            deduplicate: If True, deduplicate events based on dedupe_strategy
            dedupe_strategy: Deduplication strategy (default: URL_DATE_LOCATION)
            use_bigquery: If True, skip files and use BigQuery directly

        Yields:
            Event: Individual Event instances matching the filter

        Raises:
            RateLimitError: If rate limited and fallback not available
            APIError: If download fails and fallback not available
            ConfigurationError: If BigQuery requested but not configured

        Example:
            >>> filter_obj = EventFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
            ...     actor1_country="USA",
            ... )
            >>> count = 0
            >>> async for event in endpoint.stream(filter_obj, deduplicate=True):
            ...     print(event.global_event_id)
            ...     count += 1
            >>> print(f"Streamed {count} unique events")
        """
        # Default dedupe strategy
        if deduplicate and dedupe_strategy is None:
            dedupe_strategy = DedupeStrategy.URL_DATE_LOCATION

        # Fetch raw events from DataFetcher
        raw_events = self._fetcher.fetch_events(
            filter_obj,
            use_bigquery=use_bigquery,
        )

        # Apply deduplication if requested
        if deduplicate and dedupe_strategy is not None:
            logger.debug("Applying deduplication (strategy=%s)", dedupe_strategy)
            raw_events = apply_dedup_async(raw_events, dedupe_strategy)

        # Convert _RawEvent to Event at yield boundary
        count = 0
        async for raw_event in raw_events:
            event = Event.from_raw(raw_event)
            yield event
            count += 1

        logger.info("Streamed %d events", count)

    def query_sync(
        self,
        filter_obj: EventFilter,
        *,
        deduplicate: bool = False,
        dedupe_strategy: DedupeStrategy | None = None,
        use_bigquery: bool = False,
    ) -> FetchResult[Event]:
        """Synchronous wrapper for query().

        This is a convenience method that runs the async query() method
        in a new event loop. Prefer using the async version when possible.

        Args:
            filter_obj: Event filter with date range and query parameters
            deduplicate: If True, deduplicate events based on dedupe_strategy
            dedupe_strategy: Deduplication strategy (default: URL_DATE_LOCATION)
            use_bigquery: If True, skip files and use BigQuery directly

        Returns:
            FetchResult containing Event instances

        Raises:
            RateLimitError: If rate limited and fallback not available
            APIError: If download fails and fallback not available
            ConfigurationError: If BigQuery requested but not configured
            RuntimeError: If called from within an already running event loop

        Example:
            >>> filter_obj = EventFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     actor1_country="USA",
            ... )
            >>> result = endpoint.query_sync(filter_obj)
            >>> for event in result:
            ...     print(event.global_event_id)
        """
        return asyncio.run(
            self.query(
                filter_obj,
                deduplicate=deduplicate,
                dedupe_strategy=dedupe_strategy,
                use_bigquery=use_bigquery,
            ),
        )

    def stream_sync(
        self,
        filter_obj: EventFilter,
        *,
        deduplicate: bool = False,
        dedupe_strategy: DedupeStrategy | None = None,
        use_bigquery: bool = False,
    ) -> Iterator[Event]:
        """Synchronous wrapper for stream().

        This method provides a synchronous iterator interface over async streaming.
        It internally manages the event loop and yields events one at a time,
        providing true streaming behavior with memory efficiency.

        Note: This creates a new event loop for each iteration, which has some overhead.
        For better performance, use the async stream() method directly if possible.

        Args:
            filter_obj: Event filter with date range and query parameters
            deduplicate: If True, deduplicate events based on dedupe_strategy
            dedupe_strategy: Deduplication strategy (default: URL_DATE_LOCATION)
            use_bigquery: If True, skip files and use BigQuery directly

        Returns:
            Iterator that yields Event instances for each matching event

        Raises:
            RateLimitError: If rate limited and fallback not available
            APIError: If download fails and fallback not available
            ConfigurationError: If BigQuery requested but not configured
            RuntimeError: If called from within an already running event loop

        Example:
            >>> filter_obj = EventFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     actor1_country="USA",
            ... )
            >>> for event in endpoint.stream_sync(filter_obj, deduplicate=True):
            ...     print(event.global_event_id)
        """

        async def _async_generator() -> AsyncIterator[Event]:
            """Internal async generator for sync wrapper."""
            async for event in self.stream(
                filter_obj,
                deduplicate=deduplicate,
                dedupe_strategy=dedupe_strategy,
                use_bigquery=use_bigquery,
            ):
                yield event

        # Run async generator and yield results synchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async_gen = _async_generator()
            while True:
                try:
                    event = loop.run_until_complete(async_gen.__anext__())
                    yield event
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

    async def _build_url(self, **kwargs: Any) -> str:
        """Build URL for events endpoint.

        Note: Events endpoint doesn't use URLs since it fetches from files/BigQuery.
        This method is provided for compatibility with BaseEndpoint pattern but
        is not used in practice.

        Args:
            **kwargs: Unused, but kept for interface consistency.

        Returns:
            Empty string (not used for file/BigQuery sources).
        """
        return ""
```

#### `query(filter_obj, *, deduplicate=False, dedupe_strategy=None, use_bigquery=False)`

Query GDELT Events with automatic fallback.

This is a batch query method that materializes all results into memory. For large datasets, prefer stream() for memory-efficient iteration.

Files are always tried first (free, no credentials), with automatic fallback to BigQuery on rate limit/error if credentials are configured.

Parameters:

| Name              | Type             | Description                                          | Default                                             |
| ----------------- | ---------------- | ---------------------------------------------------- | --------------------------------------------------- |
| `filter_obj`      | `EventFilter`    | Event filter with date range and query parameters    | *required*                                          |
| `deduplicate`     | `bool`           | If True, deduplicate events based on dedupe_strategy | `False`                                             |
| `dedupe_strategy` | \`DedupeStrategy | None\`                                               | Deduplication strategy (default: URL_DATE_LOCATION) |
| `use_bigquery`    | `bool`           | If True, skip files and use BigQuery directly        | `False`                                             |

Returns:

| Type                 | Description                                                           |
| -------------------- | --------------------------------------------------------------------- |
| `FetchResult[Event]` | FetchResult containing Event instances. Use .data to access the list, |
| `FetchResult[Event]` | .failed to see any failed requests, and .complete to check if all     |
| `FetchResult[Event]` | requests succeeded.                                                   |

Raises:

| Type                 | Description                                  |
| -------------------- | -------------------------------------------- |
| `RateLimitError`     | If rate limited and fallback not available   |
| `APIError`           | If download fails and fallback not available |
| `ConfigurationError` | If BigQuery requested but not configured     |

Example

> > > filter_obj = EventFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... actor1_country="USA", ... ) result = await endpoint.query(filter_obj, deduplicate=True) print(f"Found {len(result)} unique events") for event in result: ... print(event.global_event_id)

Source code in `src/py_gdelt/endpoints/events.py`

```
async def query(
    self,
    filter_obj: EventFilter,
    *,
    deduplicate: bool = False,
    dedupe_strategy: DedupeStrategy | None = None,
    use_bigquery: bool = False,
) -> FetchResult[Event]:
    """Query GDELT Events with automatic fallback.

    This is a batch query method that materializes all results into memory.
    For large datasets, prefer stream() for memory-efficient iteration.

    Files are always tried first (free, no credentials), with automatic fallback
    to BigQuery on rate limit/error if credentials are configured.

    Args:
        filter_obj: Event filter with date range and query parameters
        deduplicate: If True, deduplicate events based on dedupe_strategy
        dedupe_strategy: Deduplication strategy (default: URL_DATE_LOCATION)
        use_bigquery: If True, skip files and use BigQuery directly

    Returns:
        FetchResult containing Event instances. Use .data to access the list,
        .failed to see any failed requests, and .complete to check if all
        requests succeeded.

    Raises:
        RateLimitError: If rate limited and fallback not available
        APIError: If download fails and fallback not available
        ConfigurationError: If BigQuery requested but not configured

    Example:
        >>> filter_obj = EventFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1)),
        ...     actor1_country="USA",
        ... )
        >>> result = await endpoint.query(filter_obj, deduplicate=True)
        >>> print(f"Found {len(result)} unique events")
        >>> for event in result:
        ...     print(event.global_event_id)
    """
    # Default dedupe strategy
    if deduplicate and dedupe_strategy is None:
        dedupe_strategy = DedupeStrategy.URL_DATE_LOCATION

    # Fetch raw events first (for deduplication)
    raw_events_list: list[_RawEvent] = [
        raw_event
        async for raw_event in self._fetcher.fetch_events(
            filter_obj,
            use_bigquery=use_bigquery,
        )
    ]

    logger.info("Fetched %d raw events from sources", len(raw_events_list))

    # Apply deduplication on raw events if requested
    # Deduplication happens on _RawEvent which implements HasDedupeFields protocol
    if deduplicate and dedupe_strategy is not None:
        original_count = len(raw_events_list)
        # Convert to iterator, deduplicate, then back to list
        raw_events_list = list(apply_dedup(iter(raw_events_list), dedupe_strategy))
        logger.info(
            "Deduplicated %d events to %d unique (strategy=%s)",
            original_count,
            len(raw_events_list),
            dedupe_strategy,
        )

    # Convert _RawEvent to Event models after deduplication
    events: list[Event] = []
    for raw_event in raw_events_list:
        event = Event.from_raw(raw_event)
        events.append(event)

    logger.info("Converted %d events to Event models", len(events))

    # Return as FetchResult (no failed requests tracked yet)
    return FetchResult(data=events)
```

#### `stream(filter_obj, *, deduplicate=False, dedupe_strategy=None, use_bigquery=False)`

Stream GDELT Events with memory-efficient iteration.

This is a streaming method that yields events one at a time, making it suitable for large datasets. Memory usage is constant regardless of result size.

Files are always tried first (free, no credentials), with automatic fallback to BigQuery on rate limit/error if credentials are configured.

Parameters:

| Name              | Type             | Description                                          | Default                                             |
| ----------------- | ---------------- | ---------------------------------------------------- | --------------------------------------------------- |
| `filter_obj`      | `EventFilter`    | Event filter with date range and query parameters    | *required*                                          |
| `deduplicate`     | `bool`           | If True, deduplicate events based on dedupe_strategy | `False`                                             |
| `dedupe_strategy` | \`DedupeStrategy | None\`                                               | Deduplication strategy (default: URL_DATE_LOCATION) |
| `use_bigquery`    | `bool`           | If True, skip files and use BigQuery directly        | `False`                                             |

Yields:

| Name    | Type                   | Description                                    |
| ------- | ---------------------- | ---------------------------------------------- |
| `Event` | `AsyncIterator[Event]` | Individual Event instances matching the filter |

Raises:

| Type                 | Description                                  |
| -------------------- | -------------------------------------------- |
| `RateLimitError`     | If rate limited and fallback not available   |
| `APIError`           | If download fails and fallback not available |
| `ConfigurationError` | If BigQuery requested but not configured     |

Example

> > > filter_obj = EventFilter( ... date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)), ... actor1_country="USA", ... ) count = 0 async for event in endpoint.stream(filter_obj, deduplicate=True): ... print(event.global_event_id) ... count += 1 print(f"Streamed {count} unique events")

Source code in `src/py_gdelt/endpoints/events.py`

```
async def stream(
    self,
    filter_obj: EventFilter,
    *,
    deduplicate: bool = False,
    dedupe_strategy: DedupeStrategy | None = None,
    use_bigquery: bool = False,
) -> AsyncIterator[Event]:
    """Stream GDELT Events with memory-efficient iteration.

    This is a streaming method that yields events one at a time, making it
    suitable for large datasets. Memory usage is constant regardless of
    result size.

    Files are always tried first (free, no credentials), with automatic fallback
    to BigQuery on rate limit/error if credentials are configured.

    Args:
        filter_obj: Event filter with date range and query parameters
        deduplicate: If True, deduplicate events based on dedupe_strategy
        dedupe_strategy: Deduplication strategy (default: URL_DATE_LOCATION)
        use_bigquery: If True, skip files and use BigQuery directly

    Yields:
        Event: Individual Event instances matching the filter

    Raises:
        RateLimitError: If rate limited and fallback not available
        APIError: If download fails and fallback not available
        ConfigurationError: If BigQuery requested but not configured

    Example:
        >>> filter_obj = EventFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
        ...     actor1_country="USA",
        ... )
        >>> count = 0
        >>> async for event in endpoint.stream(filter_obj, deduplicate=True):
        ...     print(event.global_event_id)
        ...     count += 1
        >>> print(f"Streamed {count} unique events")
    """
    # Default dedupe strategy
    if deduplicate and dedupe_strategy is None:
        dedupe_strategy = DedupeStrategy.URL_DATE_LOCATION

    # Fetch raw events from DataFetcher
    raw_events = self._fetcher.fetch_events(
        filter_obj,
        use_bigquery=use_bigquery,
    )

    # Apply deduplication if requested
    if deduplicate and dedupe_strategy is not None:
        logger.debug("Applying deduplication (strategy=%s)", dedupe_strategy)
        raw_events = apply_dedup_async(raw_events, dedupe_strategy)

    # Convert _RawEvent to Event at yield boundary
    count = 0
    async for raw_event in raw_events:
        event = Event.from_raw(raw_event)
        yield event
        count += 1

    logger.info("Streamed %d events", count)
```

#### `query_sync(filter_obj, *, deduplicate=False, dedupe_strategy=None, use_bigquery=False)`

Synchronous wrapper for query().

This is a convenience method that runs the async query() method in a new event loop. Prefer using the async version when possible.

Parameters:

| Name              | Type             | Description                                          | Default                                             |
| ----------------- | ---------------- | ---------------------------------------------------- | --------------------------------------------------- |
| `filter_obj`      | `EventFilter`    | Event filter with date range and query parameters    | *required*                                          |
| `deduplicate`     | `bool`           | If True, deduplicate events based on dedupe_strategy | `False`                                             |
| `dedupe_strategy` | \`DedupeStrategy | None\`                                               | Deduplication strategy (default: URL_DATE_LOCATION) |
| `use_bigquery`    | `bool`           | If True, skip files and use BigQuery directly        | `False`                                             |

Returns:

| Type                 | Description                            |
| -------------------- | -------------------------------------- |
| `FetchResult[Event]` | FetchResult containing Event instances |

Raises:

| Type                 | Description                                         |
| -------------------- | --------------------------------------------------- |
| `RateLimitError`     | If rate limited and fallback not available          |
| `APIError`           | If download fails and fallback not available        |
| `ConfigurationError` | If BigQuery requested but not configured            |
| `RuntimeError`       | If called from within an already running event loop |

Example

> > > filter_obj = EventFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... actor1_country="USA", ... ) result = endpoint.query_sync(filter_obj) for event in result: ... print(event.global_event_id)

Source code in `src/py_gdelt/endpoints/events.py`

```
def query_sync(
    self,
    filter_obj: EventFilter,
    *,
    deduplicate: bool = False,
    dedupe_strategy: DedupeStrategy | None = None,
    use_bigquery: bool = False,
) -> FetchResult[Event]:
    """Synchronous wrapper for query().

    This is a convenience method that runs the async query() method
    in a new event loop. Prefer using the async version when possible.

    Args:
        filter_obj: Event filter with date range and query parameters
        deduplicate: If True, deduplicate events based on dedupe_strategy
        dedupe_strategy: Deduplication strategy (default: URL_DATE_LOCATION)
        use_bigquery: If True, skip files and use BigQuery directly

    Returns:
        FetchResult containing Event instances

    Raises:
        RateLimitError: If rate limited and fallback not available
        APIError: If download fails and fallback not available
        ConfigurationError: If BigQuery requested but not configured
        RuntimeError: If called from within an already running event loop

    Example:
        >>> filter_obj = EventFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1)),
        ...     actor1_country="USA",
        ... )
        >>> result = endpoint.query_sync(filter_obj)
        >>> for event in result:
        ...     print(event.global_event_id)
    """
    return asyncio.run(
        self.query(
            filter_obj,
            deduplicate=deduplicate,
            dedupe_strategy=dedupe_strategy,
            use_bigquery=use_bigquery,
        ),
    )
```

#### `stream_sync(filter_obj, *, deduplicate=False, dedupe_strategy=None, use_bigquery=False)`

Synchronous wrapper for stream().

This method provides a synchronous iterator interface over async streaming. It internally manages the event loop and yields events one at a time, providing true streaming behavior with memory efficiency.

Note: This creates a new event loop for each iteration, which has some overhead. For better performance, use the async stream() method directly if possible.

Parameters:

| Name              | Type             | Description                                          | Default                                             |
| ----------------- | ---------------- | ---------------------------------------------------- | --------------------------------------------------- |
| `filter_obj`      | `EventFilter`    | Event filter with date range and query parameters    | *required*                                          |
| `deduplicate`     | `bool`           | If True, deduplicate events based on dedupe_strategy | `False`                                             |
| `dedupe_strategy` | \`DedupeStrategy | None\`                                               | Deduplication strategy (default: URL_DATE_LOCATION) |
| `use_bigquery`    | `bool`           | If True, skip files and use BigQuery directly        | `False`                                             |

Returns:

| Type              | Description                                                  |
| ----------------- | ------------------------------------------------------------ |
| `Iterator[Event]` | Iterator that yields Event instances for each matching event |

Raises:

| Type                 | Description                                         |
| -------------------- | --------------------------------------------------- |
| `RateLimitError`     | If rate limited and fallback not available          |
| `APIError`           | If download fails and fallback not available        |
| `ConfigurationError` | If BigQuery requested but not configured            |
| `RuntimeError`       | If called from within an already running event loop |

Example

> > > filter_obj = EventFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... actor1_country="USA", ... ) for event in endpoint.stream_sync(filter_obj, deduplicate=True): ... print(event.global_event_id)

Source code in `src/py_gdelt/endpoints/events.py`

```
def stream_sync(
    self,
    filter_obj: EventFilter,
    *,
    deduplicate: bool = False,
    dedupe_strategy: DedupeStrategy | None = None,
    use_bigquery: bool = False,
) -> Iterator[Event]:
    """Synchronous wrapper for stream().

    This method provides a synchronous iterator interface over async streaming.
    It internally manages the event loop and yields events one at a time,
    providing true streaming behavior with memory efficiency.

    Note: This creates a new event loop for each iteration, which has some overhead.
    For better performance, use the async stream() method directly if possible.

    Args:
        filter_obj: Event filter with date range and query parameters
        deduplicate: If True, deduplicate events based on dedupe_strategy
        dedupe_strategy: Deduplication strategy (default: URL_DATE_LOCATION)
        use_bigquery: If True, skip files and use BigQuery directly

    Returns:
        Iterator that yields Event instances for each matching event

    Raises:
        RateLimitError: If rate limited and fallback not available
        APIError: If download fails and fallback not available
        ConfigurationError: If BigQuery requested but not configured
        RuntimeError: If called from within an already running event loop

    Example:
        >>> filter_obj = EventFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1)),
        ...     actor1_country="USA",
        ... )
        >>> for event in endpoint.stream_sync(filter_obj, deduplicate=True):
        ...     print(event.global_event_id)
    """

    async def _async_generator() -> AsyncIterator[Event]:
        """Internal async generator for sync wrapper."""
        async for event in self.stream(
            filter_obj,
            deduplicate=deduplicate,
            dedupe_strategy=dedupe_strategy,
            use_bigquery=use_bigquery,
        ):
            yield event

    # Run async generator and yield results synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        async_gen = _async_generator()
        while True:
            try:
                event = loop.run_until_complete(async_gen.__anext__())
                yield event
            except StopAsyncIteration:
                break
    finally:
        loop.close()
```

### MentionsEndpoint

### `MentionsEndpoint`

Endpoint for querying GDELT Mentions data.

Mentions track individual occurrences of events across different news sources. Each mention links to an event in the Events table via GlobalEventID and contains metadata about the source, timing, document position, and confidence.

This endpoint uses DataFetcher for multi-source orchestration:

- Primary: File downloads (free, no credentials needed)
- Fallback: BigQuery (on rate limit/error, if credentials configured)

Parameters:

| Name               | Type             | Description                                                         | Default                                                                                                   |
| ------------------ | ---------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `file_source`      | `FileSource`     | FileSource instance for downloading GDELT files                     | *required*                                                                                                |
| `bigquery_source`  | \`BigQuerySource | None\`                                                              | Optional BigQuerySource instance for fallback queries                                                     |
| `settings`         | \`GDELTSettings  | None\`                                                              | Optional GDELTSettings for configuration (currently unused but reserved for future features like caching) |
| `fallback_enabled` | `bool`           | Whether to fallback to BigQuery on errors (default: True)           | `True`                                                                                                    |
| `error_policy`     | `ErrorPolicy`    | How to handle errors - 'raise', 'warn', or 'skip' (default: 'warn') | `'warn'`                                                                                                  |

Note

Mentions queries require BigQuery as files don't support event-specific filtering. File downloads would require fetching entire date ranges and filtering client-side, which is inefficient for single-event queries. BigQuery fallback only activates if both fallback_enabled=True AND bigquery_source is provided AND credentials are configured.

Example

> > > from datetime import date from py_gdelt.filters import DateRange, EventFilter from py_gdelt.sources import FileSource, BigQuerySource from py_gdelt.sources.fetcher import DataFetcher
> > >
> > > async with FileSource() as file_source: ... bq_source = BigQuerySource() ... fetcher = DataFetcher(file_source=file_source, bigquery_source=bq_source) ... endpoint = MentionsEndpoint(fetcher=fetcher) ... ... filter_obj = EventFilter( ... date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)) ... ) ... ... # Batch query ... result = await endpoint.query(global_event_id="123456789", filter_obj=filter_obj) ... print(f"Found {len(result)} mentions") ... for mention in result: ... print(mention.source_name) ... ... # Streaming query ... async for mention in endpoint.stream(global_event_id="123456789", filter_obj=filter_obj): ... print(mention.source_name)

Source code in `src/py_gdelt/endpoints/mentions.py`

```
class MentionsEndpoint:
    """Endpoint for querying GDELT Mentions data.

    Mentions track individual occurrences of events across different news sources.
    Each mention links to an event in the Events table via GlobalEventID and contains
    metadata about the source, timing, document position, and confidence.

    This endpoint uses DataFetcher for multi-source orchestration:
    - Primary: File downloads (free, no credentials needed)
    - Fallback: BigQuery (on rate limit/error, if credentials configured)

    Args:
        file_source: FileSource instance for downloading GDELT files
        bigquery_source: Optional BigQuerySource instance for fallback queries
        settings: Optional GDELTSettings for configuration (currently unused but
            reserved for future features like caching)
        fallback_enabled: Whether to fallback to BigQuery on errors (default: True)
        error_policy: How to handle errors - 'raise', 'warn', or 'skip' (default: 'warn')

    Note:
        Mentions queries require BigQuery as files don't support event-specific filtering.
        File downloads would require fetching entire date ranges and filtering client-side,
        which is inefficient for single-event queries.
        BigQuery fallback only activates if both fallback_enabled=True AND
        bigquery_source is provided AND credentials are configured.

    Example:
        >>> from datetime import date
        >>> from py_gdelt.filters import DateRange, EventFilter
        >>> from py_gdelt.sources import FileSource, BigQuerySource
        >>> from py_gdelt.sources.fetcher import DataFetcher
        >>>
        >>> async with FileSource() as file_source:
        ...     bq_source = BigQuerySource()
        ...     fetcher = DataFetcher(file_source=file_source, bigquery_source=bq_source)
        ...     endpoint = MentionsEndpoint(fetcher=fetcher)
        ...
        ...     filter_obj = EventFilter(
        ...         date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7))
        ...     )
        ...
        ...     # Batch query
        ...     result = await endpoint.query(global_event_id="123456789", filter_obj=filter_obj)
        ...     print(f"Found {len(result)} mentions")
        ...     for mention in result:
        ...         print(mention.source_name)
        ...
        ...     # Streaming query
        ...     async for mention in endpoint.stream(global_event_id="123456789", filter_obj=filter_obj):
        ...         print(mention.source_name)
    """

    def __init__(
        self,
        file_source: FileSource,
        bigquery_source: BigQuerySource | None = None,
        *,
        settings: GDELTSettings | None = None,
        fallback_enabled: bool = True,
        error_policy: ErrorPolicy = "warn",
    ) -> None:
        from py_gdelt.sources.fetcher import DataFetcher

        self._settings = settings
        self._fetcher: DataFetcher = DataFetcher(
            file_source=file_source,
            bigquery_source=bigquery_source,
            fallback_enabled=fallback_enabled,
            error_policy=error_policy,
        )

        logger.debug(
            "MentionsEndpoint initialized (fallback_enabled=%s, error_policy=%s)",
            fallback_enabled,
            error_policy,
        )

    async def query(
        self,
        global_event_id: int,
        filter_obj: EventFilter,
        *,
        use_bigquery: bool = True,
    ) -> FetchResult[Mention]:
        """Query mentions for a specific event and return all results.

        This method collects all mentions into memory and returns them as a FetchResult.
        For large result sets or memory-constrained environments, use stream() instead.

        Args:
            global_event_id: Global event ID to fetch mentions for (integer)
            filter_obj: Filter with date range for the query window
            use_bigquery: If True, use BigQuery directly (default: True, recommended for mentions)

        Returns:
            FetchResult[Mention]: Container with list of Mention objects and failure tracking

        Raises:
            ConfigurationError: If BigQuery not configured but required
            ValueError: If date range is invalid or too large

        Example:
            >>> filter_obj = EventFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7))
            ... )
            >>> result = await endpoint.query(123456789, filter_obj)
            >>> print(f"Complete: {result.complete}, Count: {len(result)}")
            >>> for mention in result:
            ...     print(f"{mention.source_name}: {mention.confidence}%")
        """
        logger.info(
            "Querying mentions for event %s (date_range=%s to %s, use_bigquery=%s)",
            global_event_id,
            filter_obj.date_range.start,
            filter_obj.date_range.end or filter_obj.date_range.start,
            use_bigquery,
        )

        # Collect all mentions
        mentions: list[Mention] = [
            mention
            async for mention in self.stream(
                global_event_id=global_event_id,
                filter_obj=filter_obj,
                use_bigquery=use_bigquery,
            )
        ]

        logger.info(
            "Query complete: fetched %d mentions for event %s",
            len(mentions),
            global_event_id,
        )

        # For now, return FetchResult with no failures
        # In future, we could track file-level failures if using file source
        return FetchResult(data=mentions, failed=[])

    async def stream(
        self,
        global_event_id: int,
        filter_obj: EventFilter,
        *,
        use_bigquery: bool = True,
    ) -> AsyncIterator[Mention]:
        """Stream mentions for a specific event.

        This method yields mentions one at a time, converting from internal _RawMention
        to public Mention model at the yield boundary. Memory-efficient for large result sets.

        Args:
            global_event_id: Global event ID to fetch mentions for (integer)
            filter_obj: Filter with date range for the query window
            use_bigquery: If True, use BigQuery directly (default: True, recommended for mentions)

        Yields:
            Mention: Individual mention records with full type safety

        Raises:
            ConfigurationError: If BigQuery not configured but required
            ValueError: If date range is invalid or too large

        Example:
            >>> filter_obj = EventFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7))
            ... )
            >>> async for mention in endpoint.stream(123456789, filter_obj):
            ...     if mention.confidence >= 80:
            ...         print(f"High confidence: {mention.source_name}")
        """
        logger.debug(
            "Streaming mentions for event %s (date_range=%s to %s)",
            global_event_id,
            filter_obj.date_range.start,
            filter_obj.date_range.end or filter_obj.date_range.start,
        )

        mentions_count = 0

        # Use DataFetcher to query mentions
        # Note: fetch_mentions() returns AsyncIterator[_RawMention] (or dict from BigQuery)
        raw_mentions: AsyncIterator[_RawMention | dict[str, Any]] = self._fetcher.fetch_mentions(
            global_event_id=global_event_id,
            filter_obj=filter_obj,
            use_bigquery=use_bigquery,
        )

        # Convert _RawMention to Mention at yield boundary
        async for raw_mention in raw_mentions:
            # DataFetcher.fetch_mentions() returns dicts from BigQuery
            # We need to convert them to Mention
            # For now, assume BigQuery returns compatible dict structure
            if isinstance(raw_mention, dict):
                # BigQuery returns dict - convert to Mention directly
                # This is a simplified implementation - in production, we'd need proper BigQuery row mapping
                mention = self._dict_to_mention(raw_mention)
            else:
                # File source would return _RawMention (though mentions don't come from files typically)
                mention = Mention.from_raw(raw_mention)

            mentions_count += 1
            yield mention

        logger.debug("Streamed %d mentions for event %s", mentions_count, global_event_id)

    def _dict_to_mention(self, row: dict[str, Any]) -> Mention:
        """Convert BigQuery row dict to Mention model.

        This is a helper to bridge the gap between BigQuery result dicts and our Pydantic models.
        BigQuery returns rows as dictionaries, which we need to map to our internal structure.

        Args:
            row: BigQuery row as dictionary

        Returns:
            Mention: Validated Mention instance

        Note:
            This is a temporary implementation. In production, we'd use a proper BigQuery row mapper
            that handles field name translations and type conversions.
        """
        # Import here to avoid circular dependency
        from py_gdelt.models._internal import _RawMention

        # Map BigQuery column names to _RawMention fields
        # BigQuery uses different naming (e.g., EventTimeDate vs event_time_date)
        raw_mention = _RawMention(
            global_event_id=str(row.get("GlobalEventID", "")),
            event_time_date=str(row.get("EventTimeDate", "")),
            event_time_full=str(row.get("EventTimeFullDate", "")),
            mention_time_date=str(row.get("MentionTimeDate", "")),
            mention_time_full=str(row.get("MentionTimeFullDate", "")),
            mention_type=str(row.get("MentionType", "1")),
            mention_source_name=str(row.get("MentionSourceName", "")),
            mention_identifier=str(row.get("MentionIdentifier", "")),
            sentence_id=str(row.get("SentenceID", "0")),
            actor1_char_offset=str(row.get("Actor1CharOffset", "")),
            actor2_char_offset=str(row.get("Actor2CharOffset", "")),
            action_char_offset=str(row.get("ActionCharOffset", "")),
            in_raw_text=str(row.get("InRawText", "0")),
            confidence=str(row.get("Confidence", "50")),
            mention_doc_length=str(row.get("MentionDocLen", "0")),
            mention_doc_tone=str(row.get("MentionDocTone", "0.0")),
            mention_doc_translation_info=row.get("MentionDocTranslationInfo"),
            extras=row.get("Extras"),
        )

        return Mention.from_raw(raw_mention)

    def query_sync(
        self,
        global_event_id: int,
        filter_obj: EventFilter,
        *,
        use_bigquery: bool = True,
    ) -> FetchResult[Mention]:
        """Synchronous wrapper for query().

        This is a convenience method for synchronous code. It runs the async query()
        method in a new event loop. For better performance, use the async version directly.

        Args:
            global_event_id: Global event ID to fetch mentions for (integer)
            filter_obj: Filter with date range for the query window
            use_bigquery: If True, use BigQuery directly (default: True)

        Returns:
            FetchResult[Mention]: Container with list of Mention objects

        Raises:
            ConfigurationError: If BigQuery not configured but required
            ValueError: If date range is invalid

        Example:
            >>> filter_obj = EventFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7))
            ... )
            >>> result = endpoint.query_sync(123456789, filter_obj)
            >>> for mention in result:
            ...     print(mention.source_name)
        """
        return asyncio.run(
            self.query(
                global_event_id=global_event_id,
                filter_obj=filter_obj,
                use_bigquery=use_bigquery,
            ),
        )

    def stream_sync(
        self,
        global_event_id: int,
        filter_obj: EventFilter,
        *,
        use_bigquery: bool = True,
    ) -> Iterator[Mention]:
        """Synchronous wrapper for stream().

        This method provides a synchronous iterator interface over async streaming.
        It internally manages the event loop and yields mentions one at a time,
        providing true streaming behavior with memory efficiency.

        Note: This creates a new event loop for each iteration, which has some overhead.
        For better performance, use the async stream() method directly if possible.

        Args:
            global_event_id: Global event ID to fetch mentions for (integer)
            filter_obj: Filter with date range for the query window
            use_bigquery: If True, use BigQuery directly (default: True)

        Returns:
            Iterator of individual Mention records

        Raises:
            ConfigurationError: If BigQuery not configured but required
            ValueError: If date range is invalid
            RuntimeError: If called from within an already running event loop

        Example:
            >>> filter_obj = EventFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7))
            ... )
            >>> for mention in endpoint.stream_sync(123456789, filter_obj):
            ...     print(mention.source_name)
        """

        async def _async_generator() -> AsyncIterator[Mention]:
            """Internal async generator for sync wrapper."""
            async for mention in self.stream(
                global_event_id=global_event_id,
                filter_obj=filter_obj,
                use_bigquery=use_bigquery,
            ):
                yield mention

        # Run async generator and yield results synchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async_gen = _async_generator()
            while True:
                try:
                    mention = loop.run_until_complete(async_gen.__anext__())
                    yield mention
                except StopAsyncIteration:
                    break
        finally:
            loop.close()
```

#### `query(global_event_id, filter_obj, *, use_bigquery=True)`

Query mentions for a specific event and return all results.

This method collects all mentions into memory and returns them as a FetchResult. For large result sets or memory-constrained environments, use stream() instead.

Parameters:

| Name              | Type          | Description                                                              | Default    |
| ----------------- | ------------- | ------------------------------------------------------------------------ | ---------- |
| `global_event_id` | `int`         | Global event ID to fetch mentions for (integer)                          | *required* |
| `filter_obj`      | `EventFilter` | Filter with date range for the query window                              | *required* |
| `use_bigquery`    | `bool`        | If True, use BigQuery directly (default: True, recommended for mentions) | `True`     |

Returns:

| Type                   | Description                                                                         |
| ---------------------- | ----------------------------------------------------------------------------------- |
| `FetchResult[Mention]` | FetchResult\[Mention\]: Container with list of Mention objects and failure tracking |

Raises:

| Type                 | Description                             |
| -------------------- | --------------------------------------- |
| `ConfigurationError` | If BigQuery not configured but required |
| `ValueError`         | If date range is invalid or too large   |

Example

> > > filter_obj = EventFilter( ... date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)) ... ) result = await endpoint.query(123456789, filter_obj) print(f"Complete: {result.complete}, Count: {len(result)}") for mention in result: ... print(f"{mention.source_name}: {mention.confidence}%")

Source code in `src/py_gdelt/endpoints/mentions.py`

```
async def query(
    self,
    global_event_id: int,
    filter_obj: EventFilter,
    *,
    use_bigquery: bool = True,
) -> FetchResult[Mention]:
    """Query mentions for a specific event and return all results.

    This method collects all mentions into memory and returns them as a FetchResult.
    For large result sets or memory-constrained environments, use stream() instead.

    Args:
        global_event_id: Global event ID to fetch mentions for (integer)
        filter_obj: Filter with date range for the query window
        use_bigquery: If True, use BigQuery directly (default: True, recommended for mentions)

    Returns:
        FetchResult[Mention]: Container with list of Mention objects and failure tracking

    Raises:
        ConfigurationError: If BigQuery not configured but required
        ValueError: If date range is invalid or too large

    Example:
        >>> filter_obj = EventFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7))
        ... )
        >>> result = await endpoint.query(123456789, filter_obj)
        >>> print(f"Complete: {result.complete}, Count: {len(result)}")
        >>> for mention in result:
        ...     print(f"{mention.source_name}: {mention.confidence}%")
    """
    logger.info(
        "Querying mentions for event %s (date_range=%s to %s, use_bigquery=%s)",
        global_event_id,
        filter_obj.date_range.start,
        filter_obj.date_range.end or filter_obj.date_range.start,
        use_bigquery,
    )

    # Collect all mentions
    mentions: list[Mention] = [
        mention
        async for mention in self.stream(
            global_event_id=global_event_id,
            filter_obj=filter_obj,
            use_bigquery=use_bigquery,
        )
    ]

    logger.info(
        "Query complete: fetched %d mentions for event %s",
        len(mentions),
        global_event_id,
    )

    # For now, return FetchResult with no failures
    # In future, we could track file-level failures if using file source
    return FetchResult(data=mentions, failed=[])
```

#### `stream(global_event_id, filter_obj, *, use_bigquery=True)`

Stream mentions for a specific event.

This method yields mentions one at a time, converting from internal \_RawMention to public Mention model at the yield boundary. Memory-efficient for large result sets.

Parameters:

| Name              | Type          | Description                                                              | Default    |
| ----------------- | ------------- | ------------------------------------------------------------------------ | ---------- |
| `global_event_id` | `int`         | Global event ID to fetch mentions for (integer)                          | *required* |
| `filter_obj`      | `EventFilter` | Filter with date range for the query window                              | *required* |
| `use_bigquery`    | `bool`        | If True, use BigQuery directly (default: True, recommended for mentions) | `True`     |

Yields:

| Name      | Type                     | Description                                      |
| --------- | ------------------------ | ------------------------------------------------ |
| `Mention` | `AsyncIterator[Mention]` | Individual mention records with full type safety |

Raises:

| Type                 | Description                             |
| -------------------- | --------------------------------------- |
| `ConfigurationError` | If BigQuery not configured but required |
| `ValueError`         | If date range is invalid or too large   |

Example

> > > filter_obj = EventFilter( ... date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)) ... ) async for mention in endpoint.stream(123456789, filter_obj): ... if mention.confidence >= 80: ... print(f"High confidence: {mention.source_name}")

Source code in `src/py_gdelt/endpoints/mentions.py`

```
async def stream(
    self,
    global_event_id: int,
    filter_obj: EventFilter,
    *,
    use_bigquery: bool = True,
) -> AsyncIterator[Mention]:
    """Stream mentions for a specific event.

    This method yields mentions one at a time, converting from internal _RawMention
    to public Mention model at the yield boundary. Memory-efficient for large result sets.

    Args:
        global_event_id: Global event ID to fetch mentions for (integer)
        filter_obj: Filter with date range for the query window
        use_bigquery: If True, use BigQuery directly (default: True, recommended for mentions)

    Yields:
        Mention: Individual mention records with full type safety

    Raises:
        ConfigurationError: If BigQuery not configured but required
        ValueError: If date range is invalid or too large

    Example:
        >>> filter_obj = EventFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7))
        ... )
        >>> async for mention in endpoint.stream(123456789, filter_obj):
        ...     if mention.confidence >= 80:
        ...         print(f"High confidence: {mention.source_name}")
    """
    logger.debug(
        "Streaming mentions for event %s (date_range=%s to %s)",
        global_event_id,
        filter_obj.date_range.start,
        filter_obj.date_range.end or filter_obj.date_range.start,
    )

    mentions_count = 0

    # Use DataFetcher to query mentions
    # Note: fetch_mentions() returns AsyncIterator[_RawMention] (or dict from BigQuery)
    raw_mentions: AsyncIterator[_RawMention | dict[str, Any]] = self._fetcher.fetch_mentions(
        global_event_id=global_event_id,
        filter_obj=filter_obj,
        use_bigquery=use_bigquery,
    )

    # Convert _RawMention to Mention at yield boundary
    async for raw_mention in raw_mentions:
        # DataFetcher.fetch_mentions() returns dicts from BigQuery
        # We need to convert them to Mention
        # For now, assume BigQuery returns compatible dict structure
        if isinstance(raw_mention, dict):
            # BigQuery returns dict - convert to Mention directly
            # This is a simplified implementation - in production, we'd need proper BigQuery row mapping
            mention = self._dict_to_mention(raw_mention)
        else:
            # File source would return _RawMention (though mentions don't come from files typically)
            mention = Mention.from_raw(raw_mention)

        mentions_count += 1
        yield mention

    logger.debug("Streamed %d mentions for event %s", mentions_count, global_event_id)
```

#### `query_sync(global_event_id, filter_obj, *, use_bigquery=True)`

Synchronous wrapper for query().

This is a convenience method for synchronous code. It runs the async query() method in a new event loop. For better performance, use the async version directly.

Parameters:

| Name              | Type          | Description                                     | Default    |
| ----------------- | ------------- | ----------------------------------------------- | ---------- |
| `global_event_id` | `int`         | Global event ID to fetch mentions for (integer) | *required* |
| `filter_obj`      | `EventFilter` | Filter with date range for the query window     | *required* |
| `use_bigquery`    | `bool`        | If True, use BigQuery directly (default: True)  | `True`     |

Returns:

| Type                   | Description                                                    |
| ---------------------- | -------------------------------------------------------------- |
| `FetchResult[Mention]` | FetchResult\[Mention\]: Container with list of Mention objects |

Raises:

| Type                 | Description                             |
| -------------------- | --------------------------------------- |
| `ConfigurationError` | If BigQuery not configured but required |
| `ValueError`         | If date range is invalid                |

Example

> > > filter_obj = EventFilter( ... date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)) ... ) result = endpoint.query_sync(123456789, filter_obj) for mention in result: ... print(mention.source_name)

Source code in `src/py_gdelt/endpoints/mentions.py`

```
def query_sync(
    self,
    global_event_id: int,
    filter_obj: EventFilter,
    *,
    use_bigquery: bool = True,
) -> FetchResult[Mention]:
    """Synchronous wrapper for query().

    This is a convenience method for synchronous code. It runs the async query()
    method in a new event loop. For better performance, use the async version directly.

    Args:
        global_event_id: Global event ID to fetch mentions for (integer)
        filter_obj: Filter with date range for the query window
        use_bigquery: If True, use BigQuery directly (default: True)

    Returns:
        FetchResult[Mention]: Container with list of Mention objects

    Raises:
        ConfigurationError: If BigQuery not configured but required
        ValueError: If date range is invalid

    Example:
        >>> filter_obj = EventFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7))
        ... )
        >>> result = endpoint.query_sync(123456789, filter_obj)
        >>> for mention in result:
        ...     print(mention.source_name)
    """
    return asyncio.run(
        self.query(
            global_event_id=global_event_id,
            filter_obj=filter_obj,
            use_bigquery=use_bigquery,
        ),
    )
```

#### `stream_sync(global_event_id, filter_obj, *, use_bigquery=True)`

Synchronous wrapper for stream().

This method provides a synchronous iterator interface over async streaming. It internally manages the event loop and yields mentions one at a time, providing true streaming behavior with memory efficiency.

Note: This creates a new event loop for each iteration, which has some overhead. For better performance, use the async stream() method directly if possible.

Parameters:

| Name              | Type          | Description                                     | Default    |
| ----------------- | ------------- | ----------------------------------------------- | ---------- |
| `global_event_id` | `int`         | Global event ID to fetch mentions for (integer) | *required* |
| `filter_obj`      | `EventFilter` | Filter with date range for the query window     | *required* |
| `use_bigquery`    | `bool`        | If True, use BigQuery directly (default: True)  | `True`     |

Returns:

| Type                | Description                            |
| ------------------- | -------------------------------------- |
| `Iterator[Mention]` | Iterator of individual Mention records |

Raises:

| Type                 | Description                                         |
| -------------------- | --------------------------------------------------- |
| `ConfigurationError` | If BigQuery not configured but required             |
| `ValueError`         | If date range is invalid                            |
| `RuntimeError`       | If called from within an already running event loop |

Example

> > > filter_obj = EventFilter( ... date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)) ... ) for mention in endpoint.stream_sync(123456789, filter_obj): ... print(mention.source_name)

Source code in `src/py_gdelt/endpoints/mentions.py`

```
def stream_sync(
    self,
    global_event_id: int,
    filter_obj: EventFilter,
    *,
    use_bigquery: bool = True,
) -> Iterator[Mention]:
    """Synchronous wrapper for stream().

    This method provides a synchronous iterator interface over async streaming.
    It internally manages the event loop and yields mentions one at a time,
    providing true streaming behavior with memory efficiency.

    Note: This creates a new event loop for each iteration, which has some overhead.
    For better performance, use the async stream() method directly if possible.

    Args:
        global_event_id: Global event ID to fetch mentions for (integer)
        filter_obj: Filter with date range for the query window
        use_bigquery: If True, use BigQuery directly (default: True)

    Returns:
        Iterator of individual Mention records

    Raises:
        ConfigurationError: If BigQuery not configured but required
        ValueError: If date range is invalid
        RuntimeError: If called from within an already running event loop

    Example:
        >>> filter_obj = EventFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7))
        ... )
        >>> for mention in endpoint.stream_sync(123456789, filter_obj):
        ...     print(mention.source_name)
    """

    async def _async_generator() -> AsyncIterator[Mention]:
        """Internal async generator for sync wrapper."""
        async for mention in self.stream(
            global_event_id=global_event_id,
            filter_obj=filter_obj,
            use_bigquery=use_bigquery,
        ):
            yield mention

    # Run async generator and yield results synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        async_gen = _async_generator()
        while True:
            try:
                mention = loop.run_until_complete(async_gen.__anext__())
                yield mention
            except StopAsyncIteration:
                break
    finally:
        loop.close()
```

### GKGEndpoint

### `GKGEndpoint`

GKG (Global Knowledge Graph) endpoint for querying GDELT enriched content data.

The GKGEndpoint provides access to GDELT's Global Knowledge Graph, which contains rich content analysis including themes, people, organizations, locations, counts, tone, and other metadata extracted from news articles.

This endpoint uses DataFetcher to orchestrate source selection:

- Files are ALWAYS primary (free, no credentials needed)
- BigQuery is FALLBACK ONLY (on 429/error, if credentials configured)

Parameters:

| Name               | Type             | Description                                                         | Default                                                                                                   |
| ------------------ | ---------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `file_source`      | `FileSource`     | FileSource instance for downloading GDELT files                     | *required*                                                                                                |
| `bigquery_source`  | \`BigQuerySource | None\`                                                              | Optional BigQuerySource instance for fallback queries                                                     |
| `settings`         | \`GDELTSettings  | None\`                                                              | Optional GDELTSettings for configuration (currently unused but reserved for future features like caching) |
| `fallback_enabled` | `bool`           | Whether to fallback to BigQuery on errors (default: True)           | `True`                                                                                                    |
| `error_policy`     | `ErrorPolicy`    | How to handle errors - 'raise', 'warn', or 'skip' (default: 'warn') | `'warn'`                                                                                                  |

Note

BigQuery fallback only activates if both fallback_enabled=True AND bigquery_source is provided AND credentials are configured.

Example

Basic GKG query:

> > > from datetime import date from py_gdelt.filters import GKGFilter, DateRange from py_gdelt.endpoints.gkg import GKGEndpoint from py_gdelt.sources.files import FileSource
> > >
> > > async def main(): ... async with FileSource() as file_source: ... endpoint = GKGEndpoint(file_source=file_source) ... filter_obj = GKGFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... themes=["ENV_CLIMATECHANGE"] ... ) ... result = await endpoint.query(filter_obj) ... for record in result: ... print(record.record_id, record.source_url)

Streaming large result sets:

> > > async def stream_example(): ... async with FileSource() as file_source: ... endpoint = GKGEndpoint(file_source=file_source) ... filter_obj = GKGFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... country="USA" ... ) ... async for record in endpoint.stream(filter_obj): ... print(record.record_id, record.primary_theme)

Synchronous usage:

> > > endpoint = GKGEndpoint(file_source=file_source) result = endpoint.query_sync(filter_obj) for record in result: ... print(record.record_id)

Source code in `src/py_gdelt/endpoints/gkg.py`

```
class GKGEndpoint:
    """GKG (Global Knowledge Graph) endpoint for querying GDELT enriched content data.

    The GKGEndpoint provides access to GDELT's Global Knowledge Graph, which contains
    rich content analysis including themes, people, organizations, locations, counts,
    tone, and other metadata extracted from news articles.

    This endpoint uses DataFetcher to orchestrate source selection:
    - Files are ALWAYS primary (free, no credentials needed)
    - BigQuery is FALLBACK ONLY (on 429/error, if credentials configured)

    Args:
        file_source: FileSource instance for downloading GDELT files
        bigquery_source: Optional BigQuerySource instance for fallback queries
        settings: Optional GDELTSettings for configuration (currently unused but
            reserved for future features like caching)
        fallback_enabled: Whether to fallback to BigQuery on errors (default: True)
        error_policy: How to handle errors - 'raise', 'warn', or 'skip' (default: 'warn')

    Note:
        BigQuery fallback only activates if both fallback_enabled=True AND
        bigquery_source is provided AND credentials are configured.

    Example:
        Basic GKG query:

        >>> from datetime import date
        >>> from py_gdelt.filters import GKGFilter, DateRange
        >>> from py_gdelt.endpoints.gkg import GKGEndpoint
        >>> from py_gdelt.sources.files import FileSource
        >>>
        >>> async def main():
        ...     async with FileSource() as file_source:
        ...         endpoint = GKGEndpoint(file_source=file_source)
        ...         filter_obj = GKGFilter(
        ...             date_range=DateRange(start=date(2024, 1, 1)),
        ...             themes=["ENV_CLIMATECHANGE"]
        ...         )
        ...         result = await endpoint.query(filter_obj)
        ...         for record in result:
        ...             print(record.record_id, record.source_url)

        Streaming large result sets:

        >>> async def stream_example():
        ...     async with FileSource() as file_source:
        ...         endpoint = GKGEndpoint(file_source=file_source)
        ...         filter_obj = GKGFilter(
        ...             date_range=DateRange(start=date(2024, 1, 1)),
        ...             country="USA"
        ...         )
        ...         async for record in endpoint.stream(filter_obj):
        ...             print(record.record_id, record.primary_theme)

        Synchronous usage:

        >>> endpoint = GKGEndpoint(file_source=file_source)
        >>> result = endpoint.query_sync(filter_obj)
        >>> for record in result:
        ...     print(record.record_id)
    """

    def __init__(
        self,
        file_source: FileSource,
        bigquery_source: BigQuerySource | None = None,
        *,
        settings: GDELTSettings | None = None,
        fallback_enabled: bool = True,
        error_policy: ErrorPolicy = "warn",
    ) -> None:
        from py_gdelt.sources.fetcher import DataFetcher

        self._settings = settings
        self._fetcher: Any = DataFetcher(
            file_source=file_source,
            bigquery_source=bigquery_source,
            fallback_enabled=fallback_enabled,
            error_policy=error_policy,
        )

        logger.debug(
            "GKGEndpoint initialized (fallback_enabled=%s, error_policy=%s)",
            fallback_enabled,
            error_policy,
        )

    async def query(
        self,
        filter_obj: GKGFilter,
        *,
        use_bigquery: bool = False,
    ) -> FetchResult[GKGRecord]:
        """Query GKG data with automatic fallback and return all results.

        This method fetches all matching GKG records and returns them as a FetchResult
        container. For large result sets, consider using stream() instead to avoid
        loading everything into memory.

        Files are always tried first (free, no credentials), with automatic fallback
        to BigQuery on rate limit/error if credentials are configured.

        Args:
            filter_obj: GKG filter with date range and query parameters
            use_bigquery: If True, skip files and use BigQuery directly (default: False)

        Returns:
            FetchResult[GKGRecord] containing all matching records and any failures

        Raises:
            RateLimitError: If rate limited and fallback not available/enabled
            APIError: If download fails and fallback not available/enabled
            ConfigurationError: If BigQuery requested but not configured

        Example:
            >>> from datetime import date
            >>> from py_gdelt.filters import GKGFilter, DateRange
            >>>
            >>> filter_obj = GKGFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     themes=["ECON_STOCKMARKET"],
            ...     min_tone=0.0,  # Only positive tone
            ... )
            >>> result = await endpoint.query(filter_obj)
            >>> print(f"Fetched {len(result)} records")
            >>> if not result.complete:
            ...     print(f"Warning: {result.total_failed} requests failed")
            >>> for record in result:
            ...     print(record.record_id, record.tone.tone if record.tone else None)
        """
        records: list[GKGRecord] = [
            record async for record in self.stream(filter_obj, use_bigquery=use_bigquery)
        ]

        logger.info("GKG query completed: %d records fetched", len(records))

        # Return FetchResult (failures tracked by DataFetcher error policy)
        return FetchResult(data=records, failed=[])

    async def stream(
        self,
        filter_obj: GKGFilter,
        *,
        use_bigquery: bool = False,
    ) -> AsyncIterator[GKGRecord]:
        """Stream GKG records with automatic fallback.

        This method streams GKG records one at a time, which is memory-efficient for
        large result sets. Records are converted from internal _RawGKG dataclass to
        public GKGRecord Pydantic model at the yield boundary.

        Files are always tried first (free, no credentials), with automatic fallback
        to BigQuery on rate limit/error if credentials are configured.

        Args:
            filter_obj: GKG filter with date range and query parameters
            use_bigquery: If True, skip files and use BigQuery directly (default: False)

        Yields:
            GKGRecord: Individual GKG records matching the filter criteria

        Raises:
            RateLimitError: If rate limited and fallback not available/enabled
            APIError: If download fails and fallback not available/enabled
            ConfigurationError: If BigQuery requested but not configured

        Example:
            >>> from datetime import date
            >>> from py_gdelt.filters import GKGFilter, DateRange
            >>>
            >>> filter_obj = GKGFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
            ...     organizations=["United Nations"],
            ... )
            >>> count = 0
            >>> async for record in endpoint.stream(filter_obj):
            ...     print(f"Processing {record.record_id}")
            ...     count += 1
            ...     if count >= 1000:
            ...         break  # Stop after 1000 records
        """
        logger.debug("Starting GKG stream for filter: %s", filter_obj)

        # Use DataFetcher to fetch raw GKG records
        async for raw_gkg in self._fetcher.fetch_gkg(filter_obj, use_bigquery=use_bigquery):
            # Convert _RawGKG to GKGRecord at yield boundary
            try:
                record = GKGRecord.from_raw(raw_gkg)
                yield record
            except Exception as e:  # noqa: BLE001
                # Error boundary: log conversion errors but continue processing other records
                logger.warning("Failed to convert raw GKG record to GKGRecord: %s", e)
                continue

    def query_sync(
        self,
        filter_obj: GKGFilter,
        *,
        use_bigquery: bool = False,
    ) -> FetchResult[GKGRecord]:
        """Synchronous wrapper for query().

        This is a convenience method for synchronous code that internally uses
        asyncio.run() to execute the async query() method.

        Args:
            filter_obj: GKG filter with date range and query parameters
            use_bigquery: If True, skip files and use BigQuery directly (default: False)

        Returns:
            FetchResult[GKGRecord] containing all matching records and any failures

        Raises:
            RateLimitError: If rate limited and fallback not available/enabled
            APIError: If download fails and fallback not available/enabled
            ConfigurationError: If BigQuery requested but not configured
            RuntimeError: If called from within an existing event loop

        Example:
            >>> from datetime import date
            >>> from py_gdelt.filters import GKGFilter, DateRange
            >>>
            >>> # Synchronous usage (no async/await needed)
            >>> endpoint = GKGEndpoint(file_source=file_source)
            >>> filter_obj = GKGFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1))
            ... )
            >>> result = endpoint.query_sync(filter_obj)
            >>> for record in result:
            ...     print(record.record_id)
        """
        return asyncio.run(self.query(filter_obj, use_bigquery=use_bigquery))

    def stream_sync(
        self,
        filter_obj: GKGFilter,
        *,
        use_bigquery: bool = False,
    ) -> Iterator[GKGRecord]:
        """Synchronous wrapper for stream().

        This method provides a synchronous iterator interface over async streaming.
        It internally manages the event loop and yields records one at a time.

        Note: This creates a new event loop for each iteration, which has some overhead.
        For better performance, use the async stream() method directly if possible.

        Args:
            filter_obj: GKG filter with date range and query parameters
            use_bigquery: If True, skip files and use BigQuery directly (default: False)

        Returns:
            Iterator of GKGRecord instances for each matching record

        Raises:
            RateLimitError: If rate limited and fallback not available/enabled
            APIError: If download fails and fallback not available/enabled
            ConfigurationError: If BigQuery requested but not configured
            RuntimeError: If called from within an existing event loop

        Example:
            >>> from datetime import date
            >>> from py_gdelt.filters import GKGFilter, DateRange
            >>>
            >>> # Synchronous streaming (no async/await needed)
            >>> endpoint = GKGEndpoint(file_source=file_source)
            >>> filter_obj = GKGFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1))
            ... )
            >>> for record in endpoint.stream_sync(filter_obj):
            ...     print(record.record_id)
            ...     if record.has_quotations:
            ...         print(f"  {len(record.quotations)} quotations found")
        """

        async def _async_generator() -> AsyncIterator[GKGRecord]:
            """Internal async generator for sync wrapper."""
            async for record in self.stream(filter_obj, use_bigquery=use_bigquery):
                yield record

        # Run async generator and yield results synchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async_gen = _async_generator()
            while True:
                try:
                    record = loop.run_until_complete(async_gen.__anext__())
                    yield record
                except StopAsyncIteration:
                    break
        finally:
            loop.close()
```

#### `query(filter_obj, *, use_bigquery=False)`

Query GKG data with automatic fallback and return all results.

This method fetches all matching GKG records and returns them as a FetchResult container. For large result sets, consider using stream() instead to avoid loading everything into memory.

Files are always tried first (free, no credentials), with automatic fallback to BigQuery on rate limit/error if credentials are configured.

Parameters:

| Name           | Type        | Description                                                    | Default    |
| -------------- | ----------- | -------------------------------------------------------------- | ---------- |
| `filter_obj`   | `GKGFilter` | GKG filter with date range and query parameters                | *required* |
| `use_bigquery` | `bool`      | If True, skip files and use BigQuery directly (default: False) | `False`    |

Returns:

| Type                     | Description                                                             |
| ------------------------ | ----------------------------------------------------------------------- |
| `FetchResult[GKGRecord]` | FetchResult[GKGRecord] containing all matching records and any failures |

Raises:

| Type                 | Description                                          |
| -------------------- | ---------------------------------------------------- |
| `RateLimitError`     | If rate limited and fallback not available/enabled   |
| `APIError`           | If download fails and fallback not available/enabled |
| `ConfigurationError` | If BigQuery requested but not configured             |

Example

> > > from datetime import date from py_gdelt.filters import GKGFilter, DateRange
> > >
> > > filter_obj = GKGFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... themes=["ECON_STOCKMARKET"], ... min_tone=0.0, # Only positive tone ... ) result = await endpoint.query(filter_obj) print(f"Fetched {len(result)} records") if not result.complete: ... print(f"Warning: {result.total_failed} requests failed") for record in result: ... print(record.record_id, record.tone.tone if record.tone else None)

Source code in `src/py_gdelt/endpoints/gkg.py`

```
async def query(
    self,
    filter_obj: GKGFilter,
    *,
    use_bigquery: bool = False,
) -> FetchResult[GKGRecord]:
    """Query GKG data with automatic fallback and return all results.

    This method fetches all matching GKG records and returns them as a FetchResult
    container. For large result sets, consider using stream() instead to avoid
    loading everything into memory.

    Files are always tried first (free, no credentials), with automatic fallback
    to BigQuery on rate limit/error if credentials are configured.

    Args:
        filter_obj: GKG filter with date range and query parameters
        use_bigquery: If True, skip files and use BigQuery directly (default: False)

    Returns:
        FetchResult[GKGRecord] containing all matching records and any failures

    Raises:
        RateLimitError: If rate limited and fallback not available/enabled
        APIError: If download fails and fallback not available/enabled
        ConfigurationError: If BigQuery requested but not configured

    Example:
        >>> from datetime import date
        >>> from py_gdelt.filters import GKGFilter, DateRange
        >>>
        >>> filter_obj = GKGFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1)),
        ...     themes=["ECON_STOCKMARKET"],
        ...     min_tone=0.0,  # Only positive tone
        ... )
        >>> result = await endpoint.query(filter_obj)
        >>> print(f"Fetched {len(result)} records")
        >>> if not result.complete:
        ...     print(f"Warning: {result.total_failed} requests failed")
        >>> for record in result:
        ...     print(record.record_id, record.tone.tone if record.tone else None)
    """
    records: list[GKGRecord] = [
        record async for record in self.stream(filter_obj, use_bigquery=use_bigquery)
    ]

    logger.info("GKG query completed: %d records fetched", len(records))

    # Return FetchResult (failures tracked by DataFetcher error policy)
    return FetchResult(data=records, failed=[])
```

#### `stream(filter_obj, *, use_bigquery=False)`

Stream GKG records with automatic fallback.

This method streams GKG records one at a time, which is memory-efficient for large result sets. Records are converted from internal \_RawGKG dataclass to public GKGRecord Pydantic model at the yield boundary.

Files are always tried first (free, no credentials), with automatic fallback to BigQuery on rate limit/error if credentials are configured.

Parameters:

| Name           | Type        | Description                                                    | Default    |
| -------------- | ----------- | -------------------------------------------------------------- | ---------- |
| `filter_obj`   | `GKGFilter` | GKG filter with date range and query parameters                | *required* |
| `use_bigquery` | `bool`      | If True, skip files and use BigQuery directly (default: False) | `False`    |

Yields:

| Name        | Type                       | Description                                         |
| ----------- | -------------------------- | --------------------------------------------------- |
| `GKGRecord` | `AsyncIterator[GKGRecord]` | Individual GKG records matching the filter criteria |

Raises:

| Type                 | Description                                          |
| -------------------- | ---------------------------------------------------- |
| `RateLimitError`     | If rate limited and fallback not available/enabled   |
| `APIError`           | If download fails and fallback not available/enabled |
| `ConfigurationError` | If BigQuery requested but not configured             |

Example

> > > from datetime import date from py_gdelt.filters import GKGFilter, DateRange
> > >
> > > filter_obj = GKGFilter( ... date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)), ... organizations=["United Nations"], ... ) count = 0 async for record in endpoint.stream(filter_obj): ... print(f"Processing {record.record_id}") ... count += 1 ... if count >= 1000: ... break # Stop after 1000 records

Source code in `src/py_gdelt/endpoints/gkg.py`

```
async def stream(
    self,
    filter_obj: GKGFilter,
    *,
    use_bigquery: bool = False,
) -> AsyncIterator[GKGRecord]:
    """Stream GKG records with automatic fallback.

    This method streams GKG records one at a time, which is memory-efficient for
    large result sets. Records are converted from internal _RawGKG dataclass to
    public GKGRecord Pydantic model at the yield boundary.

    Files are always tried first (free, no credentials), with automatic fallback
    to BigQuery on rate limit/error if credentials are configured.

    Args:
        filter_obj: GKG filter with date range and query parameters
        use_bigquery: If True, skip files and use BigQuery directly (default: False)

    Yields:
        GKGRecord: Individual GKG records matching the filter criteria

    Raises:
        RateLimitError: If rate limited and fallback not available/enabled
        APIError: If download fails and fallback not available/enabled
        ConfigurationError: If BigQuery requested but not configured

    Example:
        >>> from datetime import date
        >>> from py_gdelt.filters import GKGFilter, DateRange
        >>>
        >>> filter_obj = GKGFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
        ...     organizations=["United Nations"],
        ... )
        >>> count = 0
        >>> async for record in endpoint.stream(filter_obj):
        ...     print(f"Processing {record.record_id}")
        ...     count += 1
        ...     if count >= 1000:
        ...         break  # Stop after 1000 records
    """
    logger.debug("Starting GKG stream for filter: %s", filter_obj)

    # Use DataFetcher to fetch raw GKG records
    async for raw_gkg in self._fetcher.fetch_gkg(filter_obj, use_bigquery=use_bigquery):
        # Convert _RawGKG to GKGRecord at yield boundary
        try:
            record = GKGRecord.from_raw(raw_gkg)
            yield record
        except Exception as e:  # noqa: BLE001
            # Error boundary: log conversion errors but continue processing other records
            logger.warning("Failed to convert raw GKG record to GKGRecord: %s", e)
            continue
```

#### `query_sync(filter_obj, *, use_bigquery=False)`

Synchronous wrapper for query().

This is a convenience method for synchronous code that internally uses asyncio.run() to execute the async query() method.

Parameters:

| Name           | Type        | Description                                                    | Default    |
| -------------- | ----------- | -------------------------------------------------------------- | ---------- |
| `filter_obj`   | `GKGFilter` | GKG filter with date range and query parameters                | *required* |
| `use_bigquery` | `bool`      | If True, skip files and use BigQuery directly (default: False) | `False`    |

Returns:

| Type                     | Description                                                             |
| ------------------------ | ----------------------------------------------------------------------- |
| `FetchResult[GKGRecord]` | FetchResult[GKGRecord] containing all matching records and any failures |

Raises:

| Type                 | Description                                          |
| -------------------- | ---------------------------------------------------- |
| `RateLimitError`     | If rate limited and fallback not available/enabled   |
| `APIError`           | If download fails and fallback not available/enabled |
| `ConfigurationError` | If BigQuery requested but not configured             |
| `RuntimeError`       | If called from within an existing event loop         |

Example

> > > from datetime import date from py_gdelt.filters import GKGFilter, DateRange
> > >
> > > ##### Synchronous usage (no async/await needed)
> > >
> > > endpoint = GKGEndpoint(file_source=file_source) filter_obj = GKGFilter( ... date_range=DateRange(start=date(2024, 1, 1)) ... ) result = endpoint.query_sync(filter_obj) for record in result: ... print(record.record_id)

Source code in `src/py_gdelt/endpoints/gkg.py`

```
def query_sync(
    self,
    filter_obj: GKGFilter,
    *,
    use_bigquery: bool = False,
) -> FetchResult[GKGRecord]:
    """Synchronous wrapper for query().

    This is a convenience method for synchronous code that internally uses
    asyncio.run() to execute the async query() method.

    Args:
        filter_obj: GKG filter with date range and query parameters
        use_bigquery: If True, skip files and use BigQuery directly (default: False)

    Returns:
        FetchResult[GKGRecord] containing all matching records and any failures

    Raises:
        RateLimitError: If rate limited and fallback not available/enabled
        APIError: If download fails and fallback not available/enabled
        ConfigurationError: If BigQuery requested but not configured
        RuntimeError: If called from within an existing event loop

    Example:
        >>> from datetime import date
        >>> from py_gdelt.filters import GKGFilter, DateRange
        >>>
        >>> # Synchronous usage (no async/await needed)
        >>> endpoint = GKGEndpoint(file_source=file_source)
        >>> filter_obj = GKGFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1))
        ... )
        >>> result = endpoint.query_sync(filter_obj)
        >>> for record in result:
        ...     print(record.record_id)
    """
    return asyncio.run(self.query(filter_obj, use_bigquery=use_bigquery))
```

#### `stream_sync(filter_obj, *, use_bigquery=False)`

Synchronous wrapper for stream().

This method provides a synchronous iterator interface over async streaming. It internally manages the event loop and yields records one at a time.

Note: This creates a new event loop for each iteration, which has some overhead. For better performance, use the async stream() method directly if possible.

Parameters:

| Name           | Type        | Description                                                    | Default    |
| -------------- | ----------- | -------------------------------------------------------------- | ---------- |
| `filter_obj`   | `GKGFilter` | GKG filter with date range and query parameters                | *required* |
| `use_bigquery` | `bool`      | If True, skip files and use BigQuery directly (default: False) | `False`    |

Returns:

| Type                  | Description                                              |
| --------------------- | -------------------------------------------------------- |
| `Iterator[GKGRecord]` | Iterator of GKGRecord instances for each matching record |

Raises:

| Type                 | Description                                          |
| -------------------- | ---------------------------------------------------- |
| `RateLimitError`     | If rate limited and fallback not available/enabled   |
| `APIError`           | If download fails and fallback not available/enabled |
| `ConfigurationError` | If BigQuery requested but not configured             |
| `RuntimeError`       | If called from within an existing event loop         |

Example

> > > from datetime import date from py_gdelt.filters import GKGFilter, DateRange
> > >
> > > ##### Synchronous streaming (no async/await needed)
> > >
> > > endpoint = GKGEndpoint(file_source=file_source) filter_obj = GKGFilter( ... date_range=DateRange(start=date(2024, 1, 1)) ... ) for record in endpoint.stream_sync(filter_obj): ... print(record.record_id) ... if record.has_quotations: ... print(f" {len(record.quotations)} quotations found")

Source code in `src/py_gdelt/endpoints/gkg.py`

```
def stream_sync(
    self,
    filter_obj: GKGFilter,
    *,
    use_bigquery: bool = False,
) -> Iterator[GKGRecord]:
    """Synchronous wrapper for stream().

    This method provides a synchronous iterator interface over async streaming.
    It internally manages the event loop and yields records one at a time.

    Note: This creates a new event loop for each iteration, which has some overhead.
    For better performance, use the async stream() method directly if possible.

    Args:
        filter_obj: GKG filter with date range and query parameters
        use_bigquery: If True, skip files and use BigQuery directly (default: False)

    Returns:
        Iterator of GKGRecord instances for each matching record

    Raises:
        RateLimitError: If rate limited and fallback not available/enabled
        APIError: If download fails and fallback not available/enabled
        ConfigurationError: If BigQuery requested but not configured
        RuntimeError: If called from within an existing event loop

    Example:
        >>> from datetime import date
        >>> from py_gdelt.filters import GKGFilter, DateRange
        >>>
        >>> # Synchronous streaming (no async/await needed)
        >>> endpoint = GKGEndpoint(file_source=file_source)
        >>> filter_obj = GKGFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1))
        ... )
        >>> for record in endpoint.stream_sync(filter_obj):
        ...     print(record.record_id)
        ...     if record.has_quotations:
        ...         print(f"  {len(record.quotations)} quotations found")
    """

    async def _async_generator() -> AsyncIterator[GKGRecord]:
        """Internal async generator for sync wrapper."""
        async for record in self.stream(filter_obj, use_bigquery=use_bigquery):
            yield record

    # Run async generator and yield results synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        async_gen = _async_generator()
        while True:
            try:
                record = loop.run_until_complete(async_gen.__anext__())
                yield record
            except StopAsyncIteration:
                break
    finally:
        loop.close()
```

### NGramsEndpoint

### `NGramsEndpoint`

Endpoint for querying GDELT NGrams 3.0 data.

Provides access to GDELT's NGrams dataset, which tracks word and phrase occurrences across global news with contextual information. NGrams are file-based only (no BigQuery support).

The endpoint uses DataFetcher for orchestrated file downloads with automatic retry, error handling, and intelligent caching. Internal \_RawNGram dataclass instances are converted to Pydantic NGramRecord models at the yield boundary.

Parameters:

| Name          | Type            | Description | Default                                                                                                                 |
| ------------- | --------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------- |
| `settings`    | \`GDELTSettings | None\`      | Configuration settings. If None, uses defaults.                                                                         |
| `file_source` | \`FileSource    | None\`      | Optional shared FileSource. If None, creates owned instance. When provided, the source lifecycle is managed externally. |

Example

Batch query with filtering:

> > > from py_gdelt.filters import NGramsFilter, DateRange from datetime import date async with NGramsEndpoint() as endpoint: ... filter_obj = NGramsFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... language="en", ... ngram="climate", ... ) ... result = await endpoint.query(filter_obj) ... print(f"Found {len(result)} records")

Streaming for large datasets:

> > > async with NGramsEndpoint() as endpoint: ... filter_obj = NGramsFilter( ... date_range=DateRange( ... start=date(2024, 1, 1), ... end=date(2024, 1, 7) ... ), ... language="en", ... ) ... async for record in endpoint.stream(filter_obj): ... if record.is_early_in_article: ... print(f"Early: {record.ngram} in {record.url}")

Source code in `src/py_gdelt/endpoints/ngrams.py`

```
class NGramsEndpoint:
    """Endpoint for querying GDELT NGrams 3.0 data.

    Provides access to GDELT's NGrams dataset, which tracks word and phrase
    occurrences across global news with contextual information. NGrams are
    file-based only (no BigQuery support).

    The endpoint uses DataFetcher for orchestrated file downloads with automatic
    retry, error handling, and intelligent caching. Internal _RawNGram dataclass
    instances are converted to Pydantic NGramRecord models at the yield boundary.

    Args:
        settings: Configuration settings. If None, uses defaults.
        file_source: Optional shared FileSource. If None, creates owned instance.
                    When provided, the source lifecycle is managed externally.

    Example:
        Batch query with filtering:

        >>> from py_gdelt.filters import NGramsFilter, DateRange
        >>> from datetime import date
        >>> async with NGramsEndpoint() as endpoint:
        ...     filter_obj = NGramsFilter(
        ...         date_range=DateRange(start=date(2024, 1, 1)),
        ...         language="en",
        ...         ngram="climate",
        ...     )
        ...     result = await endpoint.query(filter_obj)
        ...     print(f"Found {len(result)} records")

        Streaming for large datasets:

        >>> async with NGramsEndpoint() as endpoint:
        ...     filter_obj = NGramsFilter(
        ...         date_range=DateRange(
        ...             start=date(2024, 1, 1),
        ...             end=date(2024, 1, 7)
        ...         ),
        ...         language="en",
        ...     )
        ...     async for record in endpoint.stream(filter_obj):
        ...         if record.is_early_in_article:
        ...             print(f"Early: {record.ngram} in {record.url}")
    """

    def __init__(
        self,
        settings: GDELTSettings | None = None,
        file_source: FileSource | None = None,
    ) -> None:
        self.settings = settings or GDELTSettings()

        if file_source is not None:
            self._file_source = file_source
            self._owns_sources = False
        else:
            self._file_source = FileSource(settings=self.settings)
            self._owns_sources = True

        # Create DataFetcher with file source only (NGrams don't support BigQuery)
        self._fetcher = DataFetcher(
            file_source=self._file_source,
            bigquery_source=None,
            fallback_enabled=False,
            error_policy="warn",
        )

        # Create parser instance
        self._parser = NGramsParser()

    async def close(self) -> None:
        """Close resources if we own them.

        Only closes resources that were created by this instance.
        Shared resources are not closed to allow reuse.
        """
        if self._owns_sources:
            # FileSource uses context manager protocol, manually call __aexit__
            await self._file_source.__aexit__(None, None, None)

    async def __aenter__(self) -> NGramsEndpoint:
        """Async context manager entry.

        Returns:
            Self for use in async with statement.
        """
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit - close resources.

        Args:
            *args: Exception info (unused, but required by protocol).
        """
        await self.close()

    async def query(self, filter_obj: NGramsFilter) -> FetchResult[NGramRecord]:
        """Query NGrams data and return all results.

        Fetches all NGram records matching the filter criteria and returns them
        as a FetchResult. This method collects all records in memory before returning,
        so use stream() for large result sets to avoid memory issues.

        Args:
            filter_obj: Filter with date range and optional ngram/language constraints

        Returns:
            FetchResult containing list of NGramRecord instances and any failed requests

        Raises:
            RateLimitError: If rate limited and retries exhausted
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> filter_obj = NGramsFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     language="en",
            ...     min_position=0,
            ...     max_position=20,
            ... )
            >>> result = await endpoint.query(filter_obj)
            >>> print(f"Found {len(result)} records in article headlines")
        """
        # Stream all records and collect them
        records: list[NGramRecord] = [record async for record in self.stream(filter_obj)]

        logger.info("Collected %d NGram records from query", len(records))

        # Return FetchResult (no failed tracking for now - DataFetcher handles errors)
        return FetchResult(data=records, failed=[])

    async def stream(self, filter_obj: NGramsFilter) -> AsyncIterator[NGramRecord]:
        """Stream NGrams data record by record.

        Yields NGram records one at a time, converting internal _RawNGram dataclass
        instances to Pydantic NGramRecord models at the yield boundary. This method
        is memory-efficient for large result sets.

        Client-side filtering is applied for ngram text, language, and position
        constraints since file downloads provide all records for a date range.

        Args:
            filter_obj: Filter with date range and optional ngram/language constraints

        Yields:
            NGramRecord: Individual NGram records matching the filter criteria

        Raises:
            RateLimitError: If rate limited and retries exhausted
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> filter_obj = NGramsFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     ngram="climate",
            ...     language="en",
            ... )
            >>> async for record in endpoint.stream(filter_obj):
            ...     print(f"{record.ngram}: {record.context}")
        """
        # Use DataFetcher's fetch_ngrams method to get raw records
        async for raw_record in self._fetcher.fetch_ngrams(filter_obj):
            # Convert _RawNGram to NGramRecord (type conversion happens here)
            try:
                record = NGramRecord.from_raw(raw_record)
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    "Failed to convert raw ngram to NGramRecord: %s - Skipping",
                    e,
                )
                continue

            # Apply client-side filtering
            if not self._matches_filter(record, filter_obj):
                continue

            yield record

    def _matches_filter(self, record: NGramRecord, filter_obj: NGramsFilter) -> bool:
        """Check if record matches filter criteria.

        Applies client-side filtering for ngram text, language, and position
        constraints. Date filtering is handled by DataFetcher (file selection).

        Args:
            record: NGramRecord to check
            filter_obj: Filter criteria

        Returns:
            True if record matches all filter criteria, False otherwise
        """
        # Filter by ngram text (case-insensitive substring match)
        if filter_obj.ngram is not None and filter_obj.ngram.lower() not in record.ngram.lower():
            return False

        # Filter by language (exact match)
        if filter_obj.language is not None and record.language != filter_obj.language:
            return False

        # Filter by position (article decile)
        if filter_obj.min_position is not None and record.position < filter_obj.min_position:
            return False

        return not (
            filter_obj.max_position is not None and record.position > filter_obj.max_position
        )

    def query_sync(self, filter_obj: NGramsFilter) -> FetchResult[NGramRecord]:
        """Synchronous wrapper for query().

        Runs the async query() method in a new event loop. This is a convenience
        method for synchronous code, but async methods are preferred when possible.

        Args:
            filter_obj: Filter with date range and optional constraints

        Returns:
            FetchResult containing list of NGramRecord instances

        Raises:
            RateLimitError: If rate limited and retries exhausted
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> filter_obj = NGramsFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     language="en",
            ... )
            >>> result = endpoint.query_sync(filter_obj)
            >>> print(f"Found {len(result)} records")
        """
        return asyncio.run(self.query(filter_obj))

    def stream_sync(self, filter_obj: NGramsFilter) -> Iterator[NGramRecord]:
        """Synchronous wrapper for stream().

        Yields NGram records from the async stream() method in a blocking manner.
        This is a convenience method for synchronous code, but async methods are
        preferred when possible.

        Args:
            filter_obj: Filter with date range and optional constraints

        Yields:
            NGramRecord: Individual NGram records matching the filter criteria

        Raises:
            RuntimeError: If called from within a running event loop.
            RateLimitError: If rate limited and retries exhausted.
            APIError: If downloads fail.
            DataError: If file parsing fails.

        Note:
            This method cannot be called from within an async context (e.g., inside
            an async function or running event loop). Doing so will raise RuntimeError.
            Use the async stream() method instead. This method creates its own event
            loop internally.

        Example:
            >>> filter_obj = NGramsFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     ngram="climate",
            ... )
            >>> for record in endpoint.stream_sync(filter_obj):
            ...     print(f"{record.ngram}: {record.url}")
        """
        # Manual event loop management is required for async generators.
        # Unlike query_sync() which uses asyncio.run() for a single coroutine,
        # stream_sync() must iterate through an async generator step-by-step.
        # asyncio.run() cannot handle async generators - it expects a coroutine
        # that returns a value, not one that yields multiple values.

        # Check if we're already in an async context - this would cause issues
        try:
            asyncio.get_running_loop()
            has_running_loop = True
        except RuntimeError:
            has_running_loop = False

        if has_running_loop:
            msg = "stream_sync() cannot be called from a running event loop. Use stream() instead."
            raise RuntimeError(msg)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async_gen = self.stream(filter_obj)
            while True:
                try:
                    record = loop.run_until_complete(async_gen.__anext__())
                    yield record
                except StopAsyncIteration:
                    break
        finally:
            loop.close()
```

#### `close()`

Close resources if we own them.

Only closes resources that were created by this instance. Shared resources are not closed to allow reuse.

Source code in `src/py_gdelt/endpoints/ngrams.py`

```
async def close(self) -> None:
    """Close resources if we own them.

    Only closes resources that were created by this instance.
    Shared resources are not closed to allow reuse.
    """
    if self._owns_sources:
        # FileSource uses context manager protocol, manually call __aexit__
        await self._file_source.__aexit__(None, None, None)
```

#### `__aenter__()`

Async context manager entry.

Returns:

| Type             | Description                           |
| ---------------- | ------------------------------------- |
| `NGramsEndpoint` | Self for use in async with statement. |

Source code in `src/py_gdelt/endpoints/ngrams.py`

```
async def __aenter__(self) -> NGramsEndpoint:
    """Async context manager entry.

    Returns:
        Self for use in async with statement.
    """
    return self
```

#### `__aexit__(*args)`

Async context manager exit - close resources.

Parameters:

| Name    | Type     | Description                                        | Default |
| ------- | -------- | -------------------------------------------------- | ------- |
| `*args` | `object` | Exception info (unused, but required by protocol). | `()`    |

Source code in `src/py_gdelt/endpoints/ngrams.py`

```
async def __aexit__(self, *args: object) -> None:
    """Async context manager exit - close resources.

    Args:
        *args: Exception info (unused, but required by protocol).
    """
    await self.close()
```

#### `query(filter_obj)`

Query NGrams data and return all results.

Fetches all NGram records matching the filter criteria and returns them as a FetchResult. This method collects all records in memory before returning, so use stream() for large result sets to avoid memory issues.

Parameters:

| Name         | Type           | Description                                                    | Default    |
| ------------ | -------------- | -------------------------------------------------------------- | ---------- |
| `filter_obj` | `NGramsFilter` | Filter with date range and optional ngram/language constraints | *required* |

Returns:

| Type                       | Description                                                                  |
| -------------------------- | ---------------------------------------------------------------------------- |
| `FetchResult[NGramRecord]` | FetchResult containing list of NGramRecord instances and any failed requests |

Raises:

| Type             | Description                           |
| ---------------- | ------------------------------------- |
| `RateLimitError` | If rate limited and retries exhausted |
| `APIError`       | If downloads fail                     |
| `DataError`      | If file parsing fails                 |

Example

> > > filter_obj = NGramsFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... language="en", ... min_position=0, ... max_position=20, ... ) result = await endpoint.query(filter_obj) print(f"Found {len(result)} records in article headlines")

Source code in `src/py_gdelt/endpoints/ngrams.py`

```
async def query(self, filter_obj: NGramsFilter) -> FetchResult[NGramRecord]:
    """Query NGrams data and return all results.

    Fetches all NGram records matching the filter criteria and returns them
    as a FetchResult. This method collects all records in memory before returning,
    so use stream() for large result sets to avoid memory issues.

    Args:
        filter_obj: Filter with date range and optional ngram/language constraints

    Returns:
        FetchResult containing list of NGramRecord instances and any failed requests

    Raises:
        RateLimitError: If rate limited and retries exhausted
        APIError: If downloads fail
        DataError: If file parsing fails

    Example:
        >>> filter_obj = NGramsFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1)),
        ...     language="en",
        ...     min_position=0,
        ...     max_position=20,
        ... )
        >>> result = await endpoint.query(filter_obj)
        >>> print(f"Found {len(result)} records in article headlines")
    """
    # Stream all records and collect them
    records: list[NGramRecord] = [record async for record in self.stream(filter_obj)]

    logger.info("Collected %d NGram records from query", len(records))

    # Return FetchResult (no failed tracking for now - DataFetcher handles errors)
    return FetchResult(data=records, failed=[])
```

#### `stream(filter_obj)`

Stream NGrams data record by record.

Yields NGram records one at a time, converting internal \_RawNGram dataclass instances to Pydantic NGramRecord models at the yield boundary. This method is memory-efficient for large result sets.

Client-side filtering is applied for ngram text, language, and position constraints since file downloads provide all records for a date range.

Parameters:

| Name         | Type           | Description                                                    | Default    |
| ------------ | -------------- | -------------------------------------------------------------- | ---------- |
| `filter_obj` | `NGramsFilter` | Filter with date range and optional ngram/language constraints | *required* |

Yields:

| Name          | Type                         | Description                                           |
| ------------- | ---------------------------- | ----------------------------------------------------- |
| `NGramRecord` | `AsyncIterator[NGramRecord]` | Individual NGram records matching the filter criteria |

Raises:

| Type             | Description                           |
| ---------------- | ------------------------------------- |
| `RateLimitError` | If rate limited and retries exhausted |
| `APIError`       | If downloads fail                     |
| `DataError`      | If file parsing fails                 |

Example

> > > filter_obj = NGramsFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... ngram="climate", ... language="en", ... ) async for record in endpoint.stream(filter_obj): ... print(f"{record.ngram}: {record.context}")

Source code in `src/py_gdelt/endpoints/ngrams.py`

```
async def stream(self, filter_obj: NGramsFilter) -> AsyncIterator[NGramRecord]:
    """Stream NGrams data record by record.

    Yields NGram records one at a time, converting internal _RawNGram dataclass
    instances to Pydantic NGramRecord models at the yield boundary. This method
    is memory-efficient for large result sets.

    Client-side filtering is applied for ngram text, language, and position
    constraints since file downloads provide all records for a date range.

    Args:
        filter_obj: Filter with date range and optional ngram/language constraints

    Yields:
        NGramRecord: Individual NGram records matching the filter criteria

    Raises:
        RateLimitError: If rate limited and retries exhausted
        APIError: If downloads fail
        DataError: If file parsing fails

    Example:
        >>> filter_obj = NGramsFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1)),
        ...     ngram="climate",
        ...     language="en",
        ... )
        >>> async for record in endpoint.stream(filter_obj):
        ...     print(f"{record.ngram}: {record.context}")
    """
    # Use DataFetcher's fetch_ngrams method to get raw records
    async for raw_record in self._fetcher.fetch_ngrams(filter_obj):
        # Convert _RawNGram to NGramRecord (type conversion happens here)
        try:
            record = NGramRecord.from_raw(raw_record)
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "Failed to convert raw ngram to NGramRecord: %s - Skipping",
                e,
            )
            continue

        # Apply client-side filtering
        if not self._matches_filter(record, filter_obj):
            continue

        yield record
```

#### `query_sync(filter_obj)`

Synchronous wrapper for query().

Runs the async query() method in a new event loop. This is a convenience method for synchronous code, but async methods are preferred when possible.

Parameters:

| Name         | Type           | Description                                     | Default    |
| ------------ | -------------- | ----------------------------------------------- | ---------- |
| `filter_obj` | `NGramsFilter` | Filter with date range and optional constraints | *required* |

Returns:

| Type                       | Description                                          |
| -------------------------- | ---------------------------------------------------- |
| `FetchResult[NGramRecord]` | FetchResult containing list of NGramRecord instances |

Raises:

| Type             | Description                           |
| ---------------- | ------------------------------------- |
| `RateLimitError` | If rate limited and retries exhausted |
| `APIError`       | If downloads fail                     |
| `DataError`      | If file parsing fails                 |

Example

> > > filter_obj = NGramsFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... language="en", ... ) result = endpoint.query_sync(filter_obj) print(f"Found {len(result)} records")

Source code in `src/py_gdelt/endpoints/ngrams.py`

```
def query_sync(self, filter_obj: NGramsFilter) -> FetchResult[NGramRecord]:
    """Synchronous wrapper for query().

    Runs the async query() method in a new event loop. This is a convenience
    method for synchronous code, but async methods are preferred when possible.

    Args:
        filter_obj: Filter with date range and optional constraints

    Returns:
        FetchResult containing list of NGramRecord instances

    Raises:
        RateLimitError: If rate limited and retries exhausted
        APIError: If downloads fail
        DataError: If file parsing fails

    Example:
        >>> filter_obj = NGramsFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1)),
        ...     language="en",
        ... )
        >>> result = endpoint.query_sync(filter_obj)
        >>> print(f"Found {len(result)} records")
    """
    return asyncio.run(self.query(filter_obj))
```

#### `stream_sync(filter_obj)`

Synchronous wrapper for stream().

Yields NGram records from the async stream() method in a blocking manner. This is a convenience method for synchronous code, but async methods are preferred when possible.

Parameters:

| Name         | Type           | Description                                     | Default    |
| ------------ | -------------- | ----------------------------------------------- | ---------- |
| `filter_obj` | `NGramsFilter` | Filter with date range and optional constraints | *required* |

Yields:

| Name          | Type          | Description                                           |
| ------------- | ------------- | ----------------------------------------------------- |
| `NGramRecord` | `NGramRecord` | Individual NGram records matching the filter criteria |

Raises:

| Type             | Description                                 |
| ---------------- | ------------------------------------------- |
| `RuntimeError`   | If called from within a running event loop. |
| `RateLimitError` | If rate limited and retries exhausted.      |
| `APIError`       | If downloads fail.                          |
| `DataError`      | If file parsing fails.                      |

Note

This method cannot be called from within an async context (e.g., inside an async function or running event loop). Doing so will raise RuntimeError. Use the async stream() method instead. This method creates its own event loop internally.

Example

> > > filter_obj = NGramsFilter( ... date_range=DateRange(start=date(2024, 1, 1)), ... ngram="climate", ... ) for record in endpoint.stream_sync(filter_obj): ... print(f"{record.ngram}: {record.url}")

Source code in `src/py_gdelt/endpoints/ngrams.py`

```
def stream_sync(self, filter_obj: NGramsFilter) -> Iterator[NGramRecord]:
    """Synchronous wrapper for stream().

    Yields NGram records from the async stream() method in a blocking manner.
    This is a convenience method for synchronous code, but async methods are
    preferred when possible.

    Args:
        filter_obj: Filter with date range and optional constraints

    Yields:
        NGramRecord: Individual NGram records matching the filter criteria

    Raises:
        RuntimeError: If called from within a running event loop.
        RateLimitError: If rate limited and retries exhausted.
        APIError: If downloads fail.
        DataError: If file parsing fails.

    Note:
        This method cannot be called from within an async context (e.g., inside
        an async function or running event loop). Doing so will raise RuntimeError.
        Use the async stream() method instead. This method creates its own event
        loop internally.

    Example:
        >>> filter_obj = NGramsFilter(
        ...     date_range=DateRange(start=date(2024, 1, 1)),
        ...     ngram="climate",
        ... )
        >>> for record in endpoint.stream_sync(filter_obj):
        ...     print(f"{record.ngram}: {record.url}")
    """
    # Manual event loop management is required for async generators.
    # Unlike query_sync() which uses asyncio.run() for a single coroutine,
    # stream_sync() must iterate through an async generator step-by-step.
    # asyncio.run() cannot handle async generators - it expects a coroutine
    # that returns a value, not one that yields multiple values.

    # Check if we're already in an async context - this would cause issues
    try:
        asyncio.get_running_loop()
        has_running_loop = True
    except RuntimeError:
        has_running_loop = False

    if has_running_loop:
        msg = "stream_sync() cannot be called from a running event loop. Use stream() instead."
        raise RuntimeError(msg)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        async_gen = self.stream(filter_obj)
        while True:
            try:
                record = loop.run_until_complete(async_gen.__anext__())
                yield record
            except StopAsyncIteration:
                break
    finally:
        loop.close()
```

## REST API Endpoints

### DocEndpoint

### `DocEndpoint`

Bases: `BaseEndpoint`

DOC 2.0 API endpoint for searching GDELT articles.

The DOC API provides full-text search across GDELT's monitored news sources with support for various output modes (article lists, timelines, galleries) and flexible filtering by time, source, language, and relevance.

Attributes:

| Name       | Type | Description                       |
| ---------- | ---- | --------------------------------- |
| `BASE_URL` |      | Base URL for the DOC API endpoint |

Example

Basic article search:

> > > async with DocEndpoint() as doc: ... articles = await doc.search("climate change", max_results=100) ... for article in articles: ... print(article.title, article.url)

Using filters for advanced queries:

> > > from py_gdelt.filters import DocFilter async with DocEndpoint() as doc: ... filter = DocFilter( ... query="elections", ... timespan="7d", ... source_country="US", ... sort_by="relevance" ... ) ... articles = await doc.query(filter)

Getting timeline data:

> > > async with DocEndpoint() as doc: ... timeline = await doc.timeline("protests", timespan="30d") ... for point in timeline.points: ... print(point.date, point.value)

Source code in `src/py_gdelt/endpoints/doc.py`

```
class DocEndpoint(BaseEndpoint):
    """
    DOC 2.0 API endpoint for searching GDELT articles.

    The DOC API provides full-text search across GDELT's monitored news sources
    with support for various output modes (article lists, timelines, galleries)
    and flexible filtering by time, source, language, and relevance.

    Attributes:
        BASE_URL: Base URL for the DOC API endpoint

    Example:
        Basic article search:

        >>> async with DocEndpoint() as doc:
        ...     articles = await doc.search("climate change", max_results=100)
        ...     for article in articles:
        ...         print(article.title, article.url)

        Using filters for advanced queries:

        >>> from py_gdelt.filters import DocFilter
        >>> async with DocEndpoint() as doc:
        ...     filter = DocFilter(
        ...         query="elections",
        ...         timespan="7d",
        ...         source_country="US",
        ...         sort_by="relevance"
        ...     )
        ...     articles = await doc.query(filter)

        Getting timeline data:

        >>> async with DocEndpoint() as doc:
        ...     timeline = await doc.timeline("protests", timespan="30d")
        ...     for point in timeline.points:
        ...         print(point.date, point.value)
    """

    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    async def _build_url(self, **kwargs: Any) -> str:
        """Build DOC API URL.

        The DOC API uses a fixed URL with all parameters passed as query strings.

        Args:
            **kwargs: Unused, but required by BaseEndpoint interface.

        Returns:
            Base URL for DOC API requests.
        """
        return self.BASE_URL

    def _build_params(self, query_filter: DocFilter) -> dict[str, str]:
        """
        Build query parameters from DocFilter.

        Converts the DocFilter model into URL query parameters expected by
        the DOC API, including proper format conversion for dates and
        mapping of sort values to API parameter names.

        Args:
            query_filter: Query filter with search parameters.

        Returns:
            Dict of query parameters ready for API request.

        Example:
            >>> filter = DocFilter(query="test", timespan="24h", sort_by="relevance")
            >>> endpoint = DocEndpoint()
            >>> params = endpoint._build_params(filter)
            >>> params["query"]
            'test'
            >>> params["sort"]
            'rel'
        """
        params: dict[str, str] = {
            "query": query_filter.query,
            "format": "json",
            "mode": query_filter.mode,
            "maxrecords": str(query_filter.max_results),
        }

        # Map sort values to API parameter names
        sort_map = {
            "date": "date",
            "relevance": "rel",
            "tone": "tonedesc",
        }
        params["sort"] = sort_map[query_filter.sort_by]

        # Time constraints - timespan takes precedence over datetime range
        if query_filter.timespan:
            params["timespan"] = query_filter.timespan
        elif query_filter.start_datetime:
            params["startdatetime"] = query_filter.start_datetime.strftime("%Y%m%d%H%M%S")
            if query_filter.end_datetime:
                params["enddatetime"] = query_filter.end_datetime.strftime("%Y%m%d%H%M%S")

        # Source filters
        if query_filter.source_language:
            params["sourcelang"] = query_filter.source_language
        if query_filter.source_country:
            params["sourcecountry"] = query_filter.source_country

        return params

    async def search(
        self,
        query: str,
        *,
        timespan: str | None = None,
        max_results: int = 250,
        sort_by: Literal["date", "relevance", "tone"] = "date",
        source_language: str | None = None,
        source_country: str | None = None,
    ) -> list[Article]:
        """
        Search for articles matching a query.

        This is a convenience method that constructs a DocFilter internally.
        For more control over query parameters, use query() with a DocFilter directly.

        Args:
            query: Search query string (supports boolean operators, phrases).
            timespan: Time range like "24h", "7d", "30d". If None, searches all time.
            max_results: Maximum results to return (1-250, default: 250).
            sort_by: Sort order - "date", "relevance", or "tone" (default: "date").
            source_language: Filter by source language (ISO 639 code).
            source_country: Filter by source country (FIPS country code).

        Returns:
            List of Article objects matching the query.

        Raises:
            APIError: On HTTP errors or invalid responses.
            APIUnavailableError: When API is down or unreachable.
            RateLimitError: When rate limited by the API.

        Example:
            >>> async with DocEndpoint() as doc:
            ...     # Search recent articles about climate
            ...     articles = await doc.search(
            ...         "climate change",
            ...         timespan="7d",
            ...         max_results=50,
            ...         sort_by="relevance"
            ...     )
            ...     # Filter by country
            ...     us_articles = await doc.search(
            ...         "elections",
            ...         source_country="US",
            ...         timespan="24h"
            ...     )
        """
        query_filter = DocFilter(
            query=query,
            timespan=timespan,
            max_results=max_results,
            sort_by=sort_by,
            source_language=source_language,
            source_country=source_country,
        )
        return await self.query(query_filter)

    async def query(self, query_filter: DocFilter) -> list[Article]:
        """
        Query the DOC API with a filter.

        Executes a search using a pre-configured DocFilter object, providing
        full control over all query parameters.

        Args:
            query_filter: DocFilter with query parameters and constraints.

        Returns:
            List of Article objects matching the filter criteria.

        Raises:
            APIError: On HTTP errors or invalid responses.
            APIUnavailableError: When API is down or unreachable.
            RateLimitError: When rate limited by the API.

        Example:
            >>> from py_gdelt.filters import DocFilter
            >>> from datetime import datetime
            >>> async with DocEndpoint() as doc:
            ...     # Complex query with datetime range
            ...     doc_filter = DocFilter(
            ...         query='"machine learning" AND python',
            ...         start_datetime=datetime(2024, 1, 1),
            ...         end_datetime=datetime(2024, 1, 31),
            ...         source_country="US",
            ...         max_results=100,
            ...         sort_by="relevance"
            ...     )
            ...     articles = await doc.query(doc_filter)
        """
        from py_gdelt.models.articles import Article

        params = self._build_params(query_filter)
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        # Parse response - handle both empty and populated responses
        return [Article.model_validate(item) for item in data.get("articles", [])]

    async def timeline(
        self,
        query: str,
        *,
        timespan: str | None = "7d",
    ) -> Timeline:
        """
        Get timeline data for a query.

        Returns time series data showing article volume over time for a given
        search query. Useful for visualizing trends and tracking story evolution.

        Args:
            query: Search query string.
            timespan: Time range to analyze (default: "7d" - 7 days).
                     Common values: "24h", "7d", "30d", "3mon".

        Returns:
            Timeline object with time series data points.

        Raises:
            APIError: On HTTP errors or invalid responses.
            APIUnavailableError: When API is down or unreachable.
            RateLimitError: When rate limited by the API.

        Example:
            >>> async with DocEndpoint() as doc:
            ...     # Get article volume over last month
            ...     timeline = await doc.timeline("protests", timespan="30d")
            ...     for point in timeline.points:
            ...         print(f"{point.date}: {point.value} articles")
        """
        from py_gdelt.models.articles import Timeline

        query_filter = DocFilter(
            query=query,
            timespan=timespan,
            mode="timelinevol",  # GDELT API uses 'timelinevol', not 'timeline'
        )

        params = self._build_params(query_filter)
        url = await self._build_url()

        data = await self._get_json(url, params=params)
        return Timeline.model_validate(data)
```

#### `search(query, *, timespan=None, max_results=250, sort_by='date', source_language=None, source_country=None)`

Search for articles matching a query.

This is a convenience method that constructs a DocFilter internally. For more control over query parameters, use query() with a DocFilter directly.

Parameters:

| Name              | Type                                   | Description                                                    | Default                                                         |
| ----------------- | -------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------- |
| `query`           | `str`                                  | Search query string (supports boolean operators, phrases).     | *required*                                                      |
| `timespan`        | \`str                                  | None\`                                                         | Time range like "24h", "7d", "30d". If None, searches all time. |
| `max_results`     | `int`                                  | Maximum results to return (1-250, default: 250).               | `250`                                                           |
| `sort_by`         | `Literal['date', 'relevance', 'tone']` | Sort order - "date", "relevance", or "tone" (default: "date"). | `'date'`                                                        |
| `source_language` | \`str                                  | None\`                                                         | Filter by source language (ISO 639 code).                       |
| `source_country`  | \`str                                  | None\`                                                         | Filter by source country (FIPS country code).                   |

Returns:

| Type            | Description                                 |
| --------------- | ------------------------------------------- |
| `list[Article]` | List of Article objects matching the query. |

Raises:

| Type                  | Description                          |
| --------------------- | ------------------------------------ |
| `APIError`            | On HTTP errors or invalid responses. |
| `APIUnavailableError` | When API is down or unreachable.     |
| `RateLimitError`      | When rate limited by the API.        |

Example

> > > async with DocEndpoint() as doc: ... # Search recent articles about climate ... articles = await doc.search( ... "climate change", ... timespan="7d", ... max_results=50, ... sort_by="relevance" ... ) ... # Filter by country ... us_articles = await doc.search( ... "elections", ... source_country="US", ... timespan="24h" ... )

Source code in `src/py_gdelt/endpoints/doc.py`

```
async def search(
    self,
    query: str,
    *,
    timespan: str | None = None,
    max_results: int = 250,
    sort_by: Literal["date", "relevance", "tone"] = "date",
    source_language: str | None = None,
    source_country: str | None = None,
) -> list[Article]:
    """
    Search for articles matching a query.

    This is a convenience method that constructs a DocFilter internally.
    For more control over query parameters, use query() with a DocFilter directly.

    Args:
        query: Search query string (supports boolean operators, phrases).
        timespan: Time range like "24h", "7d", "30d". If None, searches all time.
        max_results: Maximum results to return (1-250, default: 250).
        sort_by: Sort order - "date", "relevance", or "tone" (default: "date").
        source_language: Filter by source language (ISO 639 code).
        source_country: Filter by source country (FIPS country code).

    Returns:
        List of Article objects matching the query.

    Raises:
        APIError: On HTTP errors or invalid responses.
        APIUnavailableError: When API is down or unreachable.
        RateLimitError: When rate limited by the API.

    Example:
        >>> async with DocEndpoint() as doc:
        ...     # Search recent articles about climate
        ...     articles = await doc.search(
        ...         "climate change",
        ...         timespan="7d",
        ...         max_results=50,
        ...         sort_by="relevance"
        ...     )
        ...     # Filter by country
        ...     us_articles = await doc.search(
        ...         "elections",
        ...         source_country="US",
        ...         timespan="24h"
        ...     )
    """
    query_filter = DocFilter(
        query=query,
        timespan=timespan,
        max_results=max_results,
        sort_by=sort_by,
        source_language=source_language,
        source_country=source_country,
    )
    return await self.query(query_filter)
```

#### `query(query_filter)`

Query the DOC API with a filter.

Executes a search using a pre-configured DocFilter object, providing full control over all query parameters.

Parameters:

| Name           | Type        | Description                                      | Default    |
| -------------- | ----------- | ------------------------------------------------ | ---------- |
| `query_filter` | `DocFilter` | DocFilter with query parameters and constraints. | *required* |

Returns:

| Type            | Description                                           |
| --------------- | ----------------------------------------------------- |
| `list[Article]` | List of Article objects matching the filter criteria. |

Raises:

| Type                  | Description                          |
| --------------------- | ------------------------------------ |
| `APIError`            | On HTTP errors or invalid responses. |
| `APIUnavailableError` | When API is down or unreachable.     |
| `RateLimitError`      | When rate limited by the API.        |

Example

> > > from py_gdelt.filters import DocFilter from datetime import datetime async with DocEndpoint() as doc: ... # Complex query with datetime range ... doc_filter = DocFilter( ... query='"machine learning" AND python', ... start_datetime=datetime(2024, 1, 1), ... end_datetime=datetime(2024, 1, 31), ... source_country="US", ... max_results=100, ... sort_by="relevance" ... ) ... articles = await doc.query(doc_filter)

Source code in `src/py_gdelt/endpoints/doc.py`

```
async def query(self, query_filter: DocFilter) -> list[Article]:
    """
    Query the DOC API with a filter.

    Executes a search using a pre-configured DocFilter object, providing
    full control over all query parameters.

    Args:
        query_filter: DocFilter with query parameters and constraints.

    Returns:
        List of Article objects matching the filter criteria.

    Raises:
        APIError: On HTTP errors or invalid responses.
        APIUnavailableError: When API is down or unreachable.
        RateLimitError: When rate limited by the API.

    Example:
        >>> from py_gdelt.filters import DocFilter
        >>> from datetime import datetime
        >>> async with DocEndpoint() as doc:
        ...     # Complex query with datetime range
        ...     doc_filter = DocFilter(
        ...         query='"machine learning" AND python',
        ...         start_datetime=datetime(2024, 1, 1),
        ...         end_datetime=datetime(2024, 1, 31),
        ...         source_country="US",
        ...         max_results=100,
        ...         sort_by="relevance"
        ...     )
        ...     articles = await doc.query(doc_filter)
    """
    from py_gdelt.models.articles import Article

    params = self._build_params(query_filter)
    url = await self._build_url()

    data = await self._get_json(url, params=params)

    # Parse response - handle both empty and populated responses
    return [Article.model_validate(item) for item in data.get("articles", [])]
```

#### `timeline(query, *, timespan='7d')`

Get timeline data for a query.

Returns time series data showing article volume over time for a given search query. Useful for visualizing trends and tracking story evolution.

Parameters:

| Name       | Type  | Description          | Default                                                                                    |
| ---------- | ----- | -------------------- | ------------------------------------------------------------------------------------------ |
| `query`    | `str` | Search query string. | *required*                                                                                 |
| `timespan` | \`str | None\`               | Time range to analyze (default: "7d" - 7 days). Common values: "24h", "7d", "30d", "3mon". |

Returns:

| Type       | Description                                   |
| ---------- | --------------------------------------------- |
| `Timeline` | Timeline object with time series data points. |

Raises:

| Type                  | Description                          |
| --------------------- | ------------------------------------ |
| `APIError`            | On HTTP errors or invalid responses. |
| `APIUnavailableError` | When API is down or unreachable.     |
| `RateLimitError`      | When rate limited by the API.        |

Example

> > > async with DocEndpoint() as doc: ... # Get article volume over last month ... timeline = await doc.timeline("protests", timespan="30d") ... for point in timeline.points: ... print(f"{point.date}: {point.value} articles")

Source code in `src/py_gdelt/endpoints/doc.py`

```
async def timeline(
    self,
    query: str,
    *,
    timespan: str | None = "7d",
) -> Timeline:
    """
    Get timeline data for a query.

    Returns time series data showing article volume over time for a given
    search query. Useful for visualizing trends and tracking story evolution.

    Args:
        query: Search query string.
        timespan: Time range to analyze (default: "7d" - 7 days).
                 Common values: "24h", "7d", "30d", "3mon".

    Returns:
        Timeline object with time series data points.

    Raises:
        APIError: On HTTP errors or invalid responses.
        APIUnavailableError: When API is down or unreachable.
        RateLimitError: When rate limited by the API.

    Example:
        >>> async with DocEndpoint() as doc:
        ...     # Get article volume over last month
        ...     timeline = await doc.timeline("protests", timespan="30d")
        ...     for point in timeline.points:
        ...         print(f"{point.date}: {point.value} articles")
    """
    from py_gdelt.models.articles import Timeline

    query_filter = DocFilter(
        query=query,
        timespan=timespan,
        mode="timelinevol",  # GDELT API uses 'timelinevol', not 'timeline'
    )

    params = self._build_params(query_filter)
    url = await self._build_url()

    data = await self._get_json(url, params=params)
    return Timeline.model_validate(data)
```

### GeoEndpoint

### `GeoEndpoint`

Bases: `BaseEndpoint`

GEO 2.0 API endpoint for geographic article data.

Returns locations mentioned in news articles matching a query. Supports time-based filtering and geographic bounds.

Example

async with GeoEndpoint() as geo: result = await geo.search("earthquake", max_points=100) for point in result.points: print(f"{point.name}: {point.count} articles")

Attributes:

| Name       | Type | Description      |
| ---------- | ---- | ---------------- |
| `BASE_URL` |      | GEO API base URL |

Source code in `src/py_gdelt/endpoints/geo.py`

```
class GeoEndpoint(BaseEndpoint):
    """GEO 2.0 API endpoint for geographic article data.

    Returns locations mentioned in news articles matching a query.
    Supports time-based filtering and geographic bounds.

    Example:
        async with GeoEndpoint() as geo:
            result = await geo.search("earthquake", max_points=100)
            for point in result.points:
                print(f"{point.name}: {point.count} articles")

    Attributes:
        BASE_URL: GEO API base URL
    """

    BASE_URL = "https://api.gdeltproject.org/api/v2/geo/geo"

    async def _build_url(self, **kwargs: Any) -> str:
        """Build GEO API URL.

        The GEO API uses a fixed base URL with query parameters.

        Args:
            **kwargs: Unused, kept for BaseEndpoint compatibility

        Returns:
            Base URL for GEO API
        """
        return self.BASE_URL

    def _build_params(self, query_filter: GeoFilter) -> dict[str, str]:
        """Build query parameters from GeoFilter.

        Args:
            query_filter: GeoFilter with query parameters

        Returns:
            Dict of URL query parameters
        """
        params: dict[str, str] = {
            "query": query_filter.query,
            "format": "GeoJSON",  # GDELT GEO API requires exact case
            "maxpoints": str(query_filter.max_results),
        }

        if query_filter.timespan:
            params["timespan"] = query_filter.timespan

        # Add bounding box if provided (format: lon1,lat1,lon2,lat2)
        if query_filter.bounding_box:
            min_lat, min_lon, max_lat, max_lon = query_filter.bounding_box
            params["BBOX"] = f"{min_lon},{min_lat},{max_lon},{max_lat}"

        return params

    async def search(
        self,
        query: str,
        *,
        timespan: str | None = None,
        max_points: int = 250,
        bounding_box: tuple[float, float, float, float] | None = None,
    ) -> GeoResult:
        """Search for geographic locations in news.

        Args:
            query: Search query (full text search)
            timespan: Time range (e.g., "24h", "7d", "1m")
            max_points: Maximum points to return (1-250)
            bounding_box: Optional (min_lat, min_lon, max_lat, max_lon)

        Returns:
            GeoResult with list of GeoPoints

        Example:
            async with GeoEndpoint() as geo:
                result = await geo.search(
                    "earthquake",
                    timespan="7d",
                    max_points=50
                )
                print(f"Found {len(result.points)} locations")
        """
        query_filter = GeoFilter(
            query=query,
            timespan=timespan,
            max_results=min(max_points, 250),  # Cap at filter max
            bounding_box=bounding_box,
        )
        return await self.query(query_filter)

    async def query(self, query_filter: GeoFilter) -> GeoResult:
        """Query the GEO API with a filter.

        Args:
            query_filter: GeoFilter with query parameters

        Returns:
            GeoResult containing geographic points

        Raises:
            APIError: On request failure
            RateLimitError: On rate limit
            APIUnavailableError: On server error
        """
        params = self._build_params(query_filter)
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        # Parse GeoJSON features or raw points
        points: list[GeoPoint] = []

        if "features" in data:
            # GeoJSON format
            for feature in data["features"]:
                coords = feature.get("geometry", {}).get("coordinates", [])
                props = feature.get("properties", {})
                if len(coords) >= 2:
                    points.append(
                        GeoPoint(
                            lon=coords[0],
                            lat=coords[1],
                            name=props.get("name"),
                            count=props.get("count", 1),
                            url=props.get("url"),
                        ),
                    )
        elif "points" in data:
            # Plain JSON format
            points.extend([GeoPoint.model_validate(item) for item in data["points"]])

        return GeoResult(
            points=points,
            total_count=data.get("count", len(points)),
        )

    async def to_geojson(
        self,
        query: str,
        *,
        timespan: str | None = None,
        max_points: int = 250,
    ) -> dict[str, Any]:
        """Get raw GeoJSON response.

        Useful for direct use with mapping libraries (Leaflet, Folium, etc).

        Args:
            query: Search query
            timespan: Time range (e.g., "24h", "7d")
            max_points: Maximum points (1-250)

        Returns:
            Raw GeoJSON dict (FeatureCollection)

        Example:
            async with GeoEndpoint() as geo:
                geojson = await geo.to_geojson("climate change", timespan="30d")
                # Pass directly to mapping library
                folium.GeoJson(geojson).add_to(map)
        """
        query_filter = GeoFilter(
            query=query,
            timespan=timespan,
            max_results=min(max_points, 250),
        )

        params = self._build_params(query_filter)
        params["format"] = "geojson"
        url = await self._build_url()

        result = await self._get_json(url, params=params)
        return cast("dict[str, Any]", result)
```

#### `search(query, *, timespan=None, max_points=250, bounding_box=None)`

Search for geographic locations in news.

Parameters:

| Name           | Type                                | Description                      | Default                                       |
| -------------- | ----------------------------------- | -------------------------------- | --------------------------------------------- |
| `query`        | `str`                               | Search query (full text search)  | *required*                                    |
| `timespan`     | \`str                               | None\`                           | Time range (e.g., "24h", "7d", "1m")          |
| `max_points`   | `int`                               | Maximum points to return (1-250) | `250`                                         |
| `bounding_box` | \`tuple[float, float, float, float] | None\`                           | Optional (min_lat, min_lon, max_lat, max_lon) |

Returns:

| Type        | Description                      |
| ----------- | -------------------------------- |
| `GeoResult` | GeoResult with list of GeoPoints |

Example

async with GeoEndpoint() as geo: result = await geo.search( "earthquake", timespan="7d", max_points=50 ) print(f"Found {len(result.points)} locations")

Source code in `src/py_gdelt/endpoints/geo.py`

```
async def search(
    self,
    query: str,
    *,
    timespan: str | None = None,
    max_points: int = 250,
    bounding_box: tuple[float, float, float, float] | None = None,
) -> GeoResult:
    """Search for geographic locations in news.

    Args:
        query: Search query (full text search)
        timespan: Time range (e.g., "24h", "7d", "1m")
        max_points: Maximum points to return (1-250)
        bounding_box: Optional (min_lat, min_lon, max_lat, max_lon)

    Returns:
        GeoResult with list of GeoPoints

    Example:
        async with GeoEndpoint() as geo:
            result = await geo.search(
                "earthquake",
                timespan="7d",
                max_points=50
            )
            print(f"Found {len(result.points)} locations")
    """
    query_filter = GeoFilter(
        query=query,
        timespan=timespan,
        max_results=min(max_points, 250),  # Cap at filter max
        bounding_box=bounding_box,
    )
    return await self.query(query_filter)
```

#### `query(query_filter)`

Query the GEO API with a filter.

Parameters:

| Name           | Type        | Description                     | Default    |
| -------------- | ----------- | ------------------------------- | ---------- |
| `query_filter` | `GeoFilter` | GeoFilter with query parameters | *required* |

Returns:

| Type        | Description                            |
| ----------- | -------------------------------------- |
| `GeoResult` | GeoResult containing geographic points |

Raises:

| Type                  | Description        |
| --------------------- | ------------------ |
| `APIError`            | On request failure |
| `RateLimitError`      | On rate limit      |
| `APIUnavailableError` | On server error    |

Source code in `src/py_gdelt/endpoints/geo.py`

```
async def query(self, query_filter: GeoFilter) -> GeoResult:
    """Query the GEO API with a filter.

    Args:
        query_filter: GeoFilter with query parameters

    Returns:
        GeoResult containing geographic points

    Raises:
        APIError: On request failure
        RateLimitError: On rate limit
        APIUnavailableError: On server error
    """
    params = self._build_params(query_filter)
    url = await self._build_url()

    data = await self._get_json(url, params=params)

    # Parse GeoJSON features or raw points
    points: list[GeoPoint] = []

    if "features" in data:
        # GeoJSON format
        for feature in data["features"]:
            coords = feature.get("geometry", {}).get("coordinates", [])
            props = feature.get("properties", {})
            if len(coords) >= 2:
                points.append(
                    GeoPoint(
                        lon=coords[0],
                        lat=coords[1],
                        name=props.get("name"),
                        count=props.get("count", 1),
                        url=props.get("url"),
                    ),
                )
    elif "points" in data:
        # Plain JSON format
        points.extend([GeoPoint.model_validate(item) for item in data["points"]])

    return GeoResult(
        points=points,
        total_count=data.get("count", len(points)),
    )
```

#### `to_geojson(query, *, timespan=None, max_points=250)`

Get raw GeoJSON response.

Useful for direct use with mapping libraries (Leaflet, Folium, etc).

Parameters:

| Name         | Type  | Description            | Default                        |
| ------------ | ----- | ---------------------- | ------------------------------ |
| `query`      | `str` | Search query           | *required*                     |
| `timespan`   | \`str | None\`                 | Time range (e.g., "24h", "7d") |
| `max_points` | `int` | Maximum points (1-250) | `250`                          |

Returns:

| Type             | Description                          |
| ---------------- | ------------------------------------ |
| `dict[str, Any]` | Raw GeoJSON dict (FeatureCollection) |

Example

async with GeoEndpoint() as geo: geojson = await geo.to_geojson("climate change", timespan="30d")

# Pass directly to mapping library

folium.GeoJson(geojson).add_to(map)

Source code in `src/py_gdelt/endpoints/geo.py`

```
async def to_geojson(
    self,
    query: str,
    *,
    timespan: str | None = None,
    max_points: int = 250,
) -> dict[str, Any]:
    """Get raw GeoJSON response.

    Useful for direct use with mapping libraries (Leaflet, Folium, etc).

    Args:
        query: Search query
        timespan: Time range (e.g., "24h", "7d")
        max_points: Maximum points (1-250)

    Returns:
        Raw GeoJSON dict (FeatureCollection)

    Example:
        async with GeoEndpoint() as geo:
            geojson = await geo.to_geojson("climate change", timespan="30d")
            # Pass directly to mapping library
            folium.GeoJson(geojson).add_to(map)
    """
    query_filter = GeoFilter(
        query=query,
        timespan=timespan,
        max_results=min(max_points, 250),
    )

    params = self._build_params(query_filter)
    params["format"] = "geojson"
    url = await self._build_url()

    result = await self._get_json(url, params=params)
    return cast("dict[str, Any]", result)
```

### ContextEndpoint

### `ContextEndpoint`

Bases: `BaseEndpoint`

Context 2.0 API endpoint for contextual analysis.

Provides contextual information about search terms including related themes, entities, and sentiment analysis.

Attributes:

| Name       | Type | Description                           |
| ---------- | ---- | ------------------------------------- |
| `BASE_URL` |      | Base URL for the Context API endpoint |

Example

async with ContextEndpoint() as ctx: result = await ctx.analyze("climate change") for theme in result.themes\[:5\]: print(f"{theme.theme}: {theme.count} mentions")

Source code in `src/py_gdelt/endpoints/context.py`

```
class ContextEndpoint(BaseEndpoint):
    """Context 2.0 API endpoint for contextual analysis.

    Provides contextual information about search terms including
    related themes, entities, and sentiment analysis.

    Attributes:
        BASE_URL: Base URL for the Context API endpoint

    Example:
        async with ContextEndpoint() as ctx:
            result = await ctx.analyze("climate change")
            for theme in result.themes[:5]:
                print(f"{theme.theme}: {theme.count} mentions")
    """

    BASE_URL = "https://api.gdeltproject.org/api/v2/context/context"

    async def __aenter__(self) -> ContextEndpoint:
        """Async context manager entry.

        Returns:
            Self for use in async with statement.
        """
        await super().__aenter__()
        return self

    async def _build_url(self, **kwargs: Any) -> str:
        """Build Context API URL.

        The Context API uses a single endpoint URL with query parameters.

        Args:
            **kwargs: Unused, included for BaseEndpoint compatibility.

        Returns:
            Base URL for Context API.
        """
        return self.BASE_URL

    def _build_params(
        self,
        query: str,
        timespan: str | None = None,
    ) -> dict[str, str]:
        """Build query parameters for Context API request.

        Args:
            query: Search term to analyze
            timespan: Time range (e.g., "24h", "7d", "30d")

        Returns:
            Dictionary of query parameters for the API request.
        """
        params: dict[str, str] = {
            "query": query,
            "format": "json",
            "mode": "artlist",  # GDELT Context API only supports 'artlist' mode
        }

        if timespan:
            params["timespan"] = timespan

        return params

    async def analyze(
        self,
        query: str,
        *,
        timespan: str | None = None,
    ) -> ContextResult:
        """Get contextual analysis for a search term.

        Retrieves comprehensive contextual information including themes, entities,
        tone analysis, and related queries for the specified search term.

        Args:
            query: Search term to analyze
            timespan: Time range (e.g., "24h", "7d", "30d")

        Returns:
            ContextResult with themes, entities, and tone analysis

        Raises:
            RateLimitError: On 429 response
            APIUnavailableError: On 5xx response or connection error
            APIError: On other HTTP errors or invalid JSON
        """
        params = self._build_params(query, timespan)
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        # Parse themes
        themes: list[ContextTheme] = [
            ContextTheme(
                theme=item.get("theme", ""),
                count=item.get("count", 0),
                score=item.get("score"),
            )
            for item in data.get("themes", [])
        ]

        # Parse entities
        entities: list[ContextEntity] = [
            ContextEntity(
                name=item.get("name", ""),
                entity_type=item.get("type", "UNKNOWN"),
                count=item.get("count", 0),
            )
            for item in data.get("entities", [])
        ]

        # Parse tone
        tone: ContextTone | None = None
        if "tone" in data:
            t = data["tone"]
            tone = ContextTone(
                average_tone=t.get("average", 0.0),
                positive_count=t.get("positive", 0),
                negative_count=t.get("negative", 0),
                neutral_count=t.get("neutral", 0),
            )

        # Parse related queries
        related = data.get("related_queries", [])
        related_queries = [str(q) for q in related] if isinstance(related, list) else []

        return ContextResult(
            query=query,
            article_count=data.get("article_count", 0),
            themes=themes,
            entities=entities,
            tone=tone,
            related_queries=related_queries,
        )

    async def get_themes(
        self,
        query: str,
        *,
        timespan: str | None = None,
        limit: int = 10,
    ) -> list[ContextTheme]:
        """Get top themes for a search term.

        Convenience method that returns just themes sorted by count.

        Args:
            query: Search term
            timespan: Time range
            limit: Max themes to return

        Returns:
            List of top themes sorted by count (descending)

        Raises:
            RateLimitError: On 429 response
            APIUnavailableError: On 5xx response or connection error
            APIError: On other HTTP errors or invalid JSON
        """
        result = await self.analyze(query, timespan=timespan)
        sorted_themes = sorted(result.themes, key=lambda t: t.count, reverse=True)
        return sorted_themes[:limit]

    async def get_entities(
        self,
        query: str,
        *,
        timespan: str | None = None,
        entity_type: str | None = None,
        limit: int = 10,
    ) -> list[ContextEntity]:
        """Get top entities for a search term.

        Convenience method that returns entities, optionally filtered by type
        and sorted by count.

        Args:
            query: Search term
            timespan: Time range
            entity_type: Filter by type (PERSON, ORG, LOCATION)
            limit: Max entities to return

        Returns:
            List of top entities sorted by count (descending)

        Raises:
            RateLimitError: On 429 response
            APIUnavailableError: On 5xx response or connection error
            APIError: On other HTTP errors or invalid JSON
        """
        result = await self.analyze(query, timespan=timespan)

        entities = result.entities
        if entity_type:
            entities = [e for e in entities if e.entity_type == entity_type]

        sorted_entities = sorted(entities, key=lambda e: e.count, reverse=True)
        return sorted_entities[:limit]
```

#### `__aenter__()`

Async context manager entry.

Returns:

| Type              | Description                           |
| ----------------- | ------------------------------------- |
| `ContextEndpoint` | Self for use in async with statement. |

Source code in `src/py_gdelt/endpoints/context.py`

```
async def __aenter__(self) -> ContextEndpoint:
    """Async context manager entry.

    Returns:
        Self for use in async with statement.
    """
    await super().__aenter__()
    return self
```

#### `analyze(query, *, timespan=None)`

Get contextual analysis for a search term.

Retrieves comprehensive contextual information including themes, entities, tone analysis, and related queries for the specified search term.

Parameters:

| Name       | Type  | Description            | Default                               |
| ---------- | ----- | ---------------------- | ------------------------------------- |
| `query`    | `str` | Search term to analyze | *required*                            |
| `timespan` | \`str | None\`                 | Time range (e.g., "24h", "7d", "30d") |

Returns:

| Type            | Description                                            |
| --------------- | ------------------------------------------------------ |
| `ContextResult` | ContextResult with themes, entities, and tone analysis |

Raises:

| Type                  | Description                          |
| --------------------- | ------------------------------------ |
| `RateLimitError`      | On 429 response                      |
| `APIUnavailableError` | On 5xx response or connection error  |
| `APIError`            | On other HTTP errors or invalid JSON |

Source code in `src/py_gdelt/endpoints/context.py`

```
async def analyze(
    self,
    query: str,
    *,
    timespan: str | None = None,
) -> ContextResult:
    """Get contextual analysis for a search term.

    Retrieves comprehensive contextual information including themes, entities,
    tone analysis, and related queries for the specified search term.

    Args:
        query: Search term to analyze
        timespan: Time range (e.g., "24h", "7d", "30d")

    Returns:
        ContextResult with themes, entities, and tone analysis

    Raises:
        RateLimitError: On 429 response
        APIUnavailableError: On 5xx response or connection error
        APIError: On other HTTP errors or invalid JSON
    """
    params = self._build_params(query, timespan)
    url = await self._build_url()

    data = await self._get_json(url, params=params)

    # Parse themes
    themes: list[ContextTheme] = [
        ContextTheme(
            theme=item.get("theme", ""),
            count=item.get("count", 0),
            score=item.get("score"),
        )
        for item in data.get("themes", [])
    ]

    # Parse entities
    entities: list[ContextEntity] = [
        ContextEntity(
            name=item.get("name", ""),
            entity_type=item.get("type", "UNKNOWN"),
            count=item.get("count", 0),
        )
        for item in data.get("entities", [])
    ]

    # Parse tone
    tone: ContextTone | None = None
    if "tone" in data:
        t = data["tone"]
        tone = ContextTone(
            average_tone=t.get("average", 0.0),
            positive_count=t.get("positive", 0),
            negative_count=t.get("negative", 0),
            neutral_count=t.get("neutral", 0),
        )

    # Parse related queries
    related = data.get("related_queries", [])
    related_queries = [str(q) for q in related] if isinstance(related, list) else []

    return ContextResult(
        query=query,
        article_count=data.get("article_count", 0),
        themes=themes,
        entities=entities,
        tone=tone,
        related_queries=related_queries,
    )
```

#### `get_themes(query, *, timespan=None, limit=10)`

Get top themes for a search term.

Convenience method that returns just themes sorted by count.

Parameters:

| Name       | Type  | Description          | Default    |
| ---------- | ----- | -------------------- | ---------- |
| `query`    | `str` | Search term          | *required* |
| `timespan` | \`str | None\`               | Time range |
| `limit`    | `int` | Max themes to return | `10`       |

Returns:

| Type                 | Description                                     |
| -------------------- | ----------------------------------------------- |
| `list[ContextTheme]` | List of top themes sorted by count (descending) |

Raises:

| Type                  | Description                          |
| --------------------- | ------------------------------------ |
| `RateLimitError`      | On 429 response                      |
| `APIUnavailableError` | On 5xx response or connection error  |
| `APIError`            | On other HTTP errors or invalid JSON |

Source code in `src/py_gdelt/endpoints/context.py`

```
async def get_themes(
    self,
    query: str,
    *,
    timespan: str | None = None,
    limit: int = 10,
) -> list[ContextTheme]:
    """Get top themes for a search term.

    Convenience method that returns just themes sorted by count.

    Args:
        query: Search term
        timespan: Time range
        limit: Max themes to return

    Returns:
        List of top themes sorted by count (descending)

    Raises:
        RateLimitError: On 429 response
        APIUnavailableError: On 5xx response or connection error
        APIError: On other HTTP errors or invalid JSON
    """
    result = await self.analyze(query, timespan=timespan)
    sorted_themes = sorted(result.themes, key=lambda t: t.count, reverse=True)
    return sorted_themes[:limit]
```

#### `get_entities(query, *, timespan=None, entity_type=None, limit=10)`

Get top entities for a search term.

Convenience method that returns entities, optionally filtered by type and sorted by count.

Parameters:

| Name          | Type  | Description            | Default                                |
| ------------- | ----- | ---------------------- | -------------------------------------- |
| `query`       | `str` | Search term            | *required*                             |
| `timespan`    | \`str | None\`                 | Time range                             |
| `entity_type` | \`str | None\`                 | Filter by type (PERSON, ORG, LOCATION) |
| `limit`       | `int` | Max entities to return | `10`                                   |

Returns:

| Type                  | Description                                       |
| --------------------- | ------------------------------------------------- |
| `list[ContextEntity]` | List of top entities sorted by count (descending) |

Raises:

| Type                  | Description                          |
| --------------------- | ------------------------------------ |
| `RateLimitError`      | On 429 response                      |
| `APIUnavailableError` | On 5xx response or connection error  |
| `APIError`            | On other HTTP errors or invalid JSON |

Source code in `src/py_gdelt/endpoints/context.py`

```
async def get_entities(
    self,
    query: str,
    *,
    timespan: str | None = None,
    entity_type: str | None = None,
    limit: int = 10,
) -> list[ContextEntity]:
    """Get top entities for a search term.

    Convenience method that returns entities, optionally filtered by type
    and sorted by count.

    Args:
        query: Search term
        timespan: Time range
        entity_type: Filter by type (PERSON, ORG, LOCATION)
        limit: Max entities to return

    Returns:
        List of top entities sorted by count (descending)

    Raises:
        RateLimitError: On 429 response
        APIUnavailableError: On 5xx response or connection error
        APIError: On other HTTP errors or invalid JSON
    """
    result = await self.analyze(query, timespan=timespan)

    entities = result.entities
    if entity_type:
        entities = [e for e in entities if e.entity_type == entity_type]

    sorted_entities = sorted(entities, key=lambda e: e.count, reverse=True)
    return sorted_entities[:limit]
```

### TVEndpoint

### `TVEndpoint`

Bases: `BaseEndpoint`

TV API endpoint for television news monitoring.

Searches transcripts from major US television networks including CNN, Fox News, MSNBC, and others. Provides three query modes:

- Clip gallery: Individual video clips matching query
- Timeline: Time series of mention frequency
- Station chart: Breakdown by network

The endpoint handles date formatting, parameter building, and response parsing automatically.

Attributes:

| Name       | Type | Description                     |
| ---------- | ---- | ------------------------------- |
| `BASE_URL` |      | API endpoint URL for TV queries |

Example

async with TVEndpoint() as tv: clips = await tv.search("election", station="CNN") for clip in clips: print(f"{clip.show_name}: {clip.snippet}")

Source code in `src/py_gdelt/endpoints/tv.py`

```
class TVEndpoint(BaseEndpoint):
    """TV API endpoint for television news monitoring.

    Searches transcripts from major US television networks including CNN,
    Fox News, MSNBC, and others. Provides three query modes:
    - Clip gallery: Individual video clips matching query
    - Timeline: Time series of mention frequency
    - Station chart: Breakdown by network

    The endpoint handles date formatting, parameter building, and response
    parsing automatically.

    Attributes:
        BASE_URL: API endpoint URL for TV queries

    Example:
        async with TVEndpoint() as tv:
            clips = await tv.search("election", station="CNN")
            for clip in clips:
                print(f"{clip.show_name}: {clip.snippet}")
    """

    BASE_URL = "https://api.gdeltproject.org/api/v2/tv/tv"

    async def _build_url(self, **kwargs: Any) -> str:
        """Build the request URL.

        TV API uses a fixed URL with query parameters.

        Args:
            **kwargs: Unused, but required by BaseEndpoint interface.

        Returns:
            The base TV API URL.
        """
        return self.BASE_URL

    def _build_params(self, query_filter: TVFilter) -> dict[str, str]:
        """Build query parameters from TVFilter.

        Constructs query parameters for the TV API from a TVFilter object.
        Handles both timespan and datetime range parameters, station/market
        filtering, and output mode selection.

        Note: GDELT TV API requires station to be in the query string itself
        (e.g., "election station:CNN") rather than as a separate parameter.

        Args:
            query_filter: Validated TV filter object

        Returns:
            Dictionary of query parameters ready for HTTP request
        """
        # Build query string - GDELT TV API requires station in query
        query = query_filter.query
        if query_filter.station:
            query = f"{query} station:{query_filter.station}"
        if query_filter.market:
            query = f"{query} market:{query_filter.market}"

        params: dict[str, str] = {
            "query": query,
            "format": "json",
            "mode": query_filter.mode,
            "maxrecords": str(query_filter.max_results),
        }

        # Convert timespan to explicit datetime range (GDELT TV API TIMESPAN is unreliable)
        if query_filter.timespan:
            delta = _parse_timespan(query_filter.timespan)
            if delta:
                end_dt = datetime.now(UTC)
                start_dt = end_dt - delta
                params["STARTDATETIME"] = start_dt.strftime("%Y%m%d%H%M%S")
                params["ENDDATETIME"] = end_dt.strftime("%Y%m%d%H%M%S")
        elif query_filter.start_datetime:
            params["STARTDATETIME"] = query_filter.start_datetime.strftime("%Y%m%d%H%M%S")
            if query_filter.end_datetime:
                params["ENDDATETIME"] = query_filter.end_datetime.strftime("%Y%m%d%H%M%S")

        return params

    async def search(
        self,
        query: str,
        *,
        timespan: str | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        station: str | None = None,
        market: str | None = None,
        max_results: int = 250,
    ) -> list[TVClip]:
        """Search TV transcripts for clips.

        Searches television news transcripts and returns matching video clips
        with metadata and text excerpts.

        Args:
            query: Search query (keywords, phrases, or boolean expressions)
            timespan: Time range (e.g., "24h", "7d", "30d")
            start_datetime: Start of date range (alternative to timespan)
            end_datetime: End of date range (alternative to timespan)
            station: Filter by station (CNN, FOXNEWS, MSNBC, etc.)
            market: Filter by market (National, Philadelphia, etc.)
            max_results: Maximum clips to return (1-250)

        Returns:
            List of TVClip objects matching the query

        Raises:
            APIError: If the API returns an error
            RateLimitError: If rate limit is exceeded
            APIUnavailableError: If the API is unavailable

        Example:
            clips = await tv.search("climate change", station="CNN", timespan="7d")
        """
        query_filter = TVFilter(
            query=query,
            timespan=timespan,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            station=station,
            market=market,
            max_results=max_results,
            mode="ClipGallery",
        )
        return await self.query_clips(query_filter)

    async def query_clips(self, query_filter: TVFilter) -> list[TVClip]:
        """Query for TV clips with a filter.

        Lower-level method that accepts a TVFilter object for more control
        over query parameters.

        Args:
            query_filter: TVFilter object with query parameters

        Returns:
            List of TVClip objects

        Raises:
            APIError: If the API returns an error
            RateLimitError: If rate limit is exceeded
            APIUnavailableError: If the API is unavailable
        """
        params = self._build_params(query_filter)
        params["mode"] = "ClipGallery"
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        clips: list[TVClip] = [
            TVClip(
                station=item.get("station", ""),
                show_name=item.get("show"),
                clip_url=item.get("url"),
                preview_url=item.get("preview"),
                date=try_parse_gdelt_datetime(item.get("date")),
                duration_seconds=item.get("duration"),
                snippet=item.get("snippet"),
            )
            for item in data.get("clips", [])
        ]

        return clips

    async def timeline(
        self,
        query: str,
        *,
        timespan: str | None = "7d",
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        station: str | None = None,
    ) -> TVTimeline:
        """Get timeline of TV mentions.

        Returns a time series showing when a topic was mentioned on television,
        useful for tracking coverage patterns over time.

        Args:
            query: Search query
            timespan: Time range (default: "7d")
            start_datetime: Start of date range (alternative to timespan)
            end_datetime: End of date range (alternative to timespan)
            station: Optional station filter

        Returns:
            TVTimeline with time series data

        Raises:
            APIError: If the API returns an error
            RateLimitError: If rate limit is exceeded
            APIUnavailableError: If the API is unavailable

        Example:
            timeline = await tv.timeline("election", timespan="30d")
            for point in timeline.points:
                print(f"{point.date}: {point.count} mentions")
        """
        query_filter = TVFilter(
            query=query,
            timespan=timespan if not start_datetime else None,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            station=station,
            mode="TimelineVol",
        )

        params = self._build_params(query_filter)
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        points: list[TVTimelinePoint] = [
            TVTimelinePoint(
                date=item.get("date", ""),
                station=item.get("station"),
                count=item.get("count", 0),
            )
            for item in data.get("timeline", [])
        ]

        return TVTimeline(points=points)

    async def station_chart(
        self,
        query: str,
        *,
        timespan: str | None = "7d",
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> TVStationChart:
        """Get station comparison chart.

        Shows which stations covered a topic the most, useful for understanding
        which networks are focusing on particular stories.

        Args:
            query: Search query
            timespan: Time range (default: "7d")
            start_datetime: Start of date range (alternative to timespan)
            end_datetime: End of date range (alternative to timespan)

        Returns:
            TVStationChart with station breakdown

        Raises:
            APIError: If the API returns an error
            RateLimitError: If rate limit is exceeded
            APIUnavailableError: If the API is unavailable

        Example:
            chart = await tv.station_chart("healthcare")
            for station in chart.stations:
                print(f"{station.station}: {station.percentage}%")
        """
        query_filter = TVFilter(
            query=query,
            timespan=timespan if not start_datetime else None,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            mode="StationChart",
        )

        params = self._build_params(query_filter)
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        stations: list[TVStationData] = []
        if "stations" in data:
            total = sum(s.get("count", 0) for s in data["stations"])
            for item in data["stations"]:
                count = item.get("count", 0)
                stations.append(
                    TVStationData(
                        station=item.get("station", ""),
                        count=count,
                        percentage=count / total * 100 if total > 0 else None,
                    ),
                )

        return TVStationChart(stations=stations)
```

#### `search(query, *, timespan=None, start_datetime=None, end_datetime=None, station=None, market=None, max_results=250)`

Search TV transcripts for clips.

Searches television news transcripts and returns matching video clips with metadata and text excerpts.

Parameters:

| Name             | Type       | Description                                              | Default                                         |
| ---------------- | ---------- | -------------------------------------------------------- | ----------------------------------------------- |
| `query`          | `str`      | Search query (keywords, phrases, or boolean expressions) | *required*                                      |
| `timespan`       | \`str      | None\`                                                   | Time range (e.g., "24h", "7d", "30d")           |
| `start_datetime` | \`datetime | None\`                                                   | Start of date range (alternative to timespan)   |
| `end_datetime`   | \`datetime | None\`                                                   | End of date range (alternative to timespan)     |
| `station`        | \`str      | None\`                                                   | Filter by station (CNN, FOXNEWS, MSNBC, etc.)   |
| `market`         | \`str      | None\`                                                   | Filter by market (National, Philadelphia, etc.) |
| `max_results`    | `int`      | Maximum clips to return (1-250)                          | `250`                                           |

Returns:

| Type           | Description                               |
| -------------- | ----------------------------------------- |
| `list[TVClip]` | List of TVClip objects matching the query |

Raises:

| Type                  | Description                 |
| --------------------- | --------------------------- |
| `APIError`            | If the API returns an error |
| `RateLimitError`      | If rate limit is exceeded   |
| `APIUnavailableError` | If the API is unavailable   |

Example

clips = await tv.search("climate change", station="CNN", timespan="7d")

Source code in `src/py_gdelt/endpoints/tv.py`

```
async def search(
    self,
    query: str,
    *,
    timespan: str | None = None,
    start_datetime: datetime | None = None,
    end_datetime: datetime | None = None,
    station: str | None = None,
    market: str | None = None,
    max_results: int = 250,
) -> list[TVClip]:
    """Search TV transcripts for clips.

    Searches television news transcripts and returns matching video clips
    with metadata and text excerpts.

    Args:
        query: Search query (keywords, phrases, or boolean expressions)
        timespan: Time range (e.g., "24h", "7d", "30d")
        start_datetime: Start of date range (alternative to timespan)
        end_datetime: End of date range (alternative to timespan)
        station: Filter by station (CNN, FOXNEWS, MSNBC, etc.)
        market: Filter by market (National, Philadelphia, etc.)
        max_results: Maximum clips to return (1-250)

    Returns:
        List of TVClip objects matching the query

    Raises:
        APIError: If the API returns an error
        RateLimitError: If rate limit is exceeded
        APIUnavailableError: If the API is unavailable

    Example:
        clips = await tv.search("climate change", station="CNN", timespan="7d")
    """
    query_filter = TVFilter(
        query=query,
        timespan=timespan,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        station=station,
        market=market,
        max_results=max_results,
        mode="ClipGallery",
    )
    return await self.query_clips(query_filter)
```

#### `query_clips(query_filter)`

Query for TV clips with a filter.

Lower-level method that accepts a TVFilter object for more control over query parameters.

Parameters:

| Name           | Type       | Description                           | Default    |
| -------------- | ---------- | ------------------------------------- | ---------- |
| `query_filter` | `TVFilter` | TVFilter object with query parameters | *required* |

Returns:

| Type           | Description            |
| -------------- | ---------------------- |
| `list[TVClip]` | List of TVClip objects |

Raises:

| Type                  | Description                 |
| --------------------- | --------------------------- |
| `APIError`            | If the API returns an error |
| `RateLimitError`      | If rate limit is exceeded   |
| `APIUnavailableError` | If the API is unavailable   |

Source code in `src/py_gdelt/endpoints/tv.py`

```
async def query_clips(self, query_filter: TVFilter) -> list[TVClip]:
    """Query for TV clips with a filter.

    Lower-level method that accepts a TVFilter object for more control
    over query parameters.

    Args:
        query_filter: TVFilter object with query parameters

    Returns:
        List of TVClip objects

    Raises:
        APIError: If the API returns an error
        RateLimitError: If rate limit is exceeded
        APIUnavailableError: If the API is unavailable
    """
    params = self._build_params(query_filter)
    params["mode"] = "ClipGallery"
    url = await self._build_url()

    data = await self._get_json(url, params=params)

    clips: list[TVClip] = [
        TVClip(
            station=item.get("station", ""),
            show_name=item.get("show"),
            clip_url=item.get("url"),
            preview_url=item.get("preview"),
            date=try_parse_gdelt_datetime(item.get("date")),
            duration_seconds=item.get("duration"),
            snippet=item.get("snippet"),
        )
        for item in data.get("clips", [])
    ]

    return clips
```

#### `timeline(query, *, timespan='7d', start_datetime=None, end_datetime=None, station=None)`

Get timeline of TV mentions.

Returns a time series showing when a topic was mentioned on television, useful for tracking coverage patterns over time.

Parameters:

| Name             | Type       | Description  | Default                                       |
| ---------------- | ---------- | ------------ | --------------------------------------------- |
| `query`          | `str`      | Search query | *required*                                    |
| `timespan`       | \`str      | None\`       | Time range (default: "7d")                    |
| `start_datetime` | \`datetime | None\`       | Start of date range (alternative to timespan) |
| `end_datetime`   | \`datetime | None\`       | End of date range (alternative to timespan)   |
| `station`        | \`str      | None\`       | Optional station filter                       |

Returns:

| Type         | Description                      |
| ------------ | -------------------------------- |
| `TVTimeline` | TVTimeline with time series data |

Raises:

| Type                  | Description                 |
| --------------------- | --------------------------- |
| `APIError`            | If the API returns an error |
| `RateLimitError`      | If rate limit is exceeded   |
| `APIUnavailableError` | If the API is unavailable   |

Example

timeline = await tv.timeline("election", timespan="30d") for point in timeline.points: print(f"{point.date}: {point.count} mentions")

Source code in `src/py_gdelt/endpoints/tv.py`

```
async def timeline(
    self,
    query: str,
    *,
    timespan: str | None = "7d",
    start_datetime: datetime | None = None,
    end_datetime: datetime | None = None,
    station: str | None = None,
) -> TVTimeline:
    """Get timeline of TV mentions.

    Returns a time series showing when a topic was mentioned on television,
    useful for tracking coverage patterns over time.

    Args:
        query: Search query
        timespan: Time range (default: "7d")
        start_datetime: Start of date range (alternative to timespan)
        end_datetime: End of date range (alternative to timespan)
        station: Optional station filter

    Returns:
        TVTimeline with time series data

    Raises:
        APIError: If the API returns an error
        RateLimitError: If rate limit is exceeded
        APIUnavailableError: If the API is unavailable

    Example:
        timeline = await tv.timeline("election", timespan="30d")
        for point in timeline.points:
            print(f"{point.date}: {point.count} mentions")
    """
    query_filter = TVFilter(
        query=query,
        timespan=timespan if not start_datetime else None,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        station=station,
        mode="TimelineVol",
    )

    params = self._build_params(query_filter)
    url = await self._build_url()

    data = await self._get_json(url, params=params)

    points: list[TVTimelinePoint] = [
        TVTimelinePoint(
            date=item.get("date", ""),
            station=item.get("station"),
            count=item.get("count", 0),
        )
        for item in data.get("timeline", [])
    ]

    return TVTimeline(points=points)
```

#### `station_chart(query, *, timespan='7d', start_datetime=None, end_datetime=None)`

Get station comparison chart.

Shows which stations covered a topic the most, useful for understanding which networks are focusing on particular stories.

Parameters:

| Name             | Type       | Description  | Default                                       |
| ---------------- | ---------- | ------------ | --------------------------------------------- |
| `query`          | `str`      | Search query | *required*                                    |
| `timespan`       | \`str      | None\`       | Time range (default: "7d")                    |
| `start_datetime` | \`datetime | None\`       | Start of date range (alternative to timespan) |
| `end_datetime`   | \`datetime | None\`       | End of date range (alternative to timespan)   |

Returns:

| Type             | Description                           |
| ---------------- | ------------------------------------- |
| `TVStationChart` | TVStationChart with station breakdown |

Raises:

| Type                  | Description                 |
| --------------------- | --------------------------- |
| `APIError`            | If the API returns an error |
| `RateLimitError`      | If rate limit is exceeded   |
| `APIUnavailableError` | If the API is unavailable   |

Example

chart = await tv.station_chart("healthcare") for station in chart.stations: print(f"{station.station}: {station.percentage}%")

Source code in `src/py_gdelt/endpoints/tv.py`

```
async def station_chart(
    self,
    query: str,
    *,
    timespan: str | None = "7d",
    start_datetime: datetime | None = None,
    end_datetime: datetime | None = None,
) -> TVStationChart:
    """Get station comparison chart.

    Shows which stations covered a topic the most, useful for understanding
    which networks are focusing on particular stories.

    Args:
        query: Search query
        timespan: Time range (default: "7d")
        start_datetime: Start of date range (alternative to timespan)
        end_datetime: End of date range (alternative to timespan)

    Returns:
        TVStationChart with station breakdown

    Raises:
        APIError: If the API returns an error
        RateLimitError: If rate limit is exceeded
        APIUnavailableError: If the API is unavailable

    Example:
        chart = await tv.station_chart("healthcare")
        for station in chart.stations:
            print(f"{station.station}: {station.percentage}%")
    """
    query_filter = TVFilter(
        query=query,
        timespan=timespan if not start_datetime else None,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        mode="StationChart",
    )

    params = self._build_params(query_filter)
    url = await self._build_url()

    data = await self._get_json(url, params=params)

    stations: list[TVStationData] = []
    if "stations" in data:
        total = sum(s.get("count", 0) for s in data["stations"])
        for item in data["stations"]:
            count = item.get("count", 0)
            stations.append(
                TVStationData(
                    station=item.get("station", ""),
                    count=count,
                    percentage=count / total * 100 if total > 0 else None,
                ),
            )

    return TVStationChart(stations=stations)
```

### TVAIEndpoint

### `TVAIEndpoint`

Bases: `BaseEndpoint`

TVAI API endpoint for AI-enhanced TV analysis.

Similar to TVEndpoint but uses AI-powered features for enhanced analysis. Uses the same data models and similar interface as TVEndpoint.

Attributes:

| Name       | Type | Description                       |
| ---------- | ---- | --------------------------------- |
| `BASE_URL` |      | API endpoint URL for TVAI queries |

Example

async with TVAIEndpoint() as tvai: clips = await tvai.search("artificial intelligence")

Source code in `src/py_gdelt/endpoints/tv.py`

```
class TVAIEndpoint(BaseEndpoint):
    """TVAI API endpoint for AI-enhanced TV analysis.

    Similar to TVEndpoint but uses AI-powered features for enhanced analysis.
    Uses the same data models and similar interface as TVEndpoint.

    Attributes:
        BASE_URL: API endpoint URL for TVAI queries

    Example:
        async with TVAIEndpoint() as tvai:
            clips = await tvai.search("artificial intelligence")
    """

    BASE_URL = "https://api.gdeltproject.org/api/v2/tvai/tvai"

    async def _build_url(self, **kwargs: Any) -> str:
        """Build the request URL.

        TVAI API uses a fixed URL with query parameters.

        Args:
            **kwargs: Unused, but required by BaseEndpoint interface.

        Returns:
            The base TVAI API URL.
        """
        return self.BASE_URL

    async def search(
        self,
        query: str,
        *,
        timespan: str | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        station: str | None = None,
        max_results: int = 250,
    ) -> list[TVClip]:
        """Search using AI-enhanced analysis.

        Searches television transcripts using AI-powered analysis for potentially
        better semantic matching and relevance.

        Args:
            query: Search query
            timespan: Time range (e.g., "24h", "7d")
            start_datetime: Start of date range (alternative to timespan)
            end_datetime: End of date range (alternative to timespan)
            station: Filter by station
            max_results: Maximum clips to return (1-250)

        Returns:
            List of TVClip objects

        Raises:
            APIError: If the API returns an error
            RateLimitError: If rate limit is exceeded
            APIUnavailableError: If the API is unavailable

        Example:
            clips = await tvai.search("machine learning", timespan="7d")
        """
        # Build query string - GDELT TV API requires station in query
        query_str = query
        if station:
            query_str = f"{query} station:{station}"

        params: dict[str, str] = {
            "query": query_str,
            "format": "json",
            "mode": "ClipGallery",
            "maxrecords": str(max_results),
        }

        # Use explicit datetime range if provided, otherwise convert timespan
        if start_datetime:
            params["STARTDATETIME"] = start_datetime.strftime("%Y%m%d%H%M%S")
            if end_datetime:
                params["ENDDATETIME"] = end_datetime.strftime("%Y%m%d%H%M%S")
        elif timespan:
            delta = _parse_timespan(timespan)
            if delta:
                end_dt = datetime.now(UTC)
                start_dt = end_dt - delta
                params["STARTDATETIME"] = start_dt.strftime("%Y%m%d%H%M%S")
                params["ENDDATETIME"] = end_dt.strftime("%Y%m%d%H%M%S")

        url = await self._build_url()
        data = await self._get_json(url, params=params)

        clips: list[TVClip] = [
            TVClip(
                station=item.get("station", ""),
                show_name=item.get("show"),
                clip_url=item.get("url"),
                preview_url=item.get("preview"),
                date=try_parse_gdelt_datetime(item.get("date")),
                duration_seconds=item.get("duration"),
                snippet=item.get("snippet"),
            )
            for item in data.get("clips", [])
        ]

        return clips
```

#### `search(query, *, timespan=None, start_datetime=None, end_datetime=None, station=None, max_results=250)`

Search using AI-enhanced analysis.

Searches television transcripts using AI-powered analysis for potentially better semantic matching and relevance.

Parameters:

| Name             | Type       | Description                     | Default                                       |
| ---------------- | ---------- | ------------------------------- | --------------------------------------------- |
| `query`          | `str`      | Search query                    | *required*                                    |
| `timespan`       | \`str      | None\`                          | Time range (e.g., "24h", "7d")                |
| `start_datetime` | \`datetime | None\`                          | Start of date range (alternative to timespan) |
| `end_datetime`   | \`datetime | None\`                          | End of date range (alternative to timespan)   |
| `station`        | \`str      | None\`                          | Filter by station                             |
| `max_results`    | `int`      | Maximum clips to return (1-250) | `250`                                         |

Returns:

| Type           | Description            |
| -------------- | ---------------------- |
| `list[TVClip]` | List of TVClip objects |

Raises:

| Type                  | Description                 |
| --------------------- | --------------------------- |
| `APIError`            | If the API returns an error |
| `RateLimitError`      | If rate limit is exceeded   |
| `APIUnavailableError` | If the API is unavailable   |

Example

clips = await tvai.search("machine learning", timespan="7d")

Source code in `src/py_gdelt/endpoints/tv.py`

```
async def search(
    self,
    query: str,
    *,
    timespan: str | None = None,
    start_datetime: datetime | None = None,
    end_datetime: datetime | None = None,
    station: str | None = None,
    max_results: int = 250,
) -> list[TVClip]:
    """Search using AI-enhanced analysis.

    Searches television transcripts using AI-powered analysis for potentially
    better semantic matching and relevance.

    Args:
        query: Search query
        timespan: Time range (e.g., "24h", "7d")
        start_datetime: Start of date range (alternative to timespan)
        end_datetime: End of date range (alternative to timespan)
        station: Filter by station
        max_results: Maximum clips to return (1-250)

    Returns:
        List of TVClip objects

    Raises:
        APIError: If the API returns an error
        RateLimitError: If rate limit is exceeded
        APIUnavailableError: If the API is unavailable

    Example:
        clips = await tvai.search("machine learning", timespan="7d")
    """
    # Build query string - GDELT TV API requires station in query
    query_str = query
    if station:
        query_str = f"{query} station:{station}"

    params: dict[str, str] = {
        "query": query_str,
        "format": "json",
        "mode": "ClipGallery",
        "maxrecords": str(max_results),
    }

    # Use explicit datetime range if provided, otherwise convert timespan
    if start_datetime:
        params["STARTDATETIME"] = start_datetime.strftime("%Y%m%d%H%M%S")
        if end_datetime:
            params["ENDDATETIME"] = end_datetime.strftime("%Y%m%d%H%M%S")
    elif timespan:
        delta = _parse_timespan(timespan)
        if delta:
            end_dt = datetime.now(UTC)
            start_dt = end_dt - delta
            params["STARTDATETIME"] = start_dt.strftime("%Y%m%d%H%M%S")
            params["ENDDATETIME"] = end_dt.strftime("%Y%m%d%H%M%S")

    url = await self._build_url()
    data = await self._get_json(url, params=params)

    clips: list[TVClip] = [
        TVClip(
            station=item.get("station", ""),
            show_name=item.get("show"),
            clip_url=item.get("url"),
            preview_url=item.get("preview"),
            date=try_parse_gdelt_datetime(item.get("date")),
            duration_seconds=item.get("duration"),
            snippet=item.get("snippet"),
        )
        for item in data.get("clips", [])
    ]

    return clips
```
