"""Events endpoint for querying GDELT Events and Mentions data.

This module provides the EventsEndpoint class for querying GDELT Events data
from both file sources and BigQuery. It supports filtering, deduplication,
and both streaming and batch query modes.

Key features:
- Automatic source selection (files primary, BigQuery fallback)
- Deduplication support with multiple strategies
- Streaming and batch query modes
- Type conversion from internal _RawEvent to public Event models
- Sync and async interfaces

Example:
    Basic event query:

    >>> from datetime import date
    >>> from py_gdelt.filters import DateRange, EventFilter
    >>> from py_gdelt.endpoints import EventsEndpoint
    >>> from py_gdelt.sources import FileSource
    >>>
    >>> async def main():
    ...     async with FileSource() as file_source:
    ...         endpoint = EventsEndpoint(file_source=file_source)
    ...         filter_obj = EventFilter(
    ...             date_range=DateRange(start=date(2024, 1, 1)),
    ...             actor1_country="USA",
    ...         )
    ...         result = await endpoint.query(filter_obj)
    ...         print(f"Found {len(result)} events")

    Streaming with deduplication:

    >>> async def stream_example():
    ...     async with FileSource() as file_source:
    ...         endpoint = EventsEndpoint(file_source=file_source)
    ...         filter_obj = EventFilter(
    ...             date_range=DateRange(start=date(2024, 1, 1))
    ...         )
    ...         async for event in endpoint.stream(filter_obj, deduplicate=True):
    ...             print(event.global_event_id)
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from py_gdelt.models.common import FetchResult
from py_gdelt.models.events import Event
from py_gdelt.utils.dedup import (
    DedupeStrategy,
)
from py_gdelt.utils.dedup import (
    deduplicate as apply_dedup,
)
from py_gdelt.utils.dedup import (
    deduplicate_async as apply_dedup_async,
)


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from py_gdelt.filters import EventFilter
    from py_gdelt.models._internal import _RawEvent
    from py_gdelt.sources.bigquery import BigQuerySource
    from py_gdelt.sources.fetcher import DataFetcher
    from py_gdelt.sources.files import FileSource

__all__ = ["EventsEndpoint"]

logger = logging.getLogger(__name__)


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
