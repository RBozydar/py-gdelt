"""MentionsEndpoint for querying GDELT event mentions.

This module provides the MentionsEndpoint class for accessing GDELT Mentions data,
which tracks individual mentions of events across different news sources. Each mention
links to an event via GlobalEventID.

The endpoint uses DataFetcher for source orchestration (files primary, BigQuery fallback)
and converts internal _RawMention dataclasses to public Mention Pydantic models at the
yield boundary.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from py_gdelt.models.common import FetchResult
from py_gdelt.models.events import Mention


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Collection, Iterator

    from py_gdelt.config import GDELTSettings
    from py_gdelt.filters import EventFilter
    from py_gdelt.models._internal import _RawMention
    from py_gdelt.sources.bigquery import BigQuerySource
    from py_gdelt.sources.fetcher import DataFetcher, ErrorPolicy
    from py_gdelt.sources.files import FileSource

__all__ = ["MentionsEndpoint"]

logger = logging.getLogger(__name__)


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
        columns: Collection[str] | None = None,
        limit: int | None = None,
    ) -> FetchResult[Mention]:
        """Query mentions for a specific event and return all results.

        This method collects all mentions into memory and returns them as a FetchResult.
        For large result sets or memory-constrained environments, use stream() instead.

        Args:
            global_event_id: Global event ID to fetch mentions for (integer)
            filter_obj: Filter with date range for the query window
            use_bigquery: If True, use BigQuery directly (default: True, recommended for mentions)
            columns: Optional collection of BigQuery column names for column projection.
                When specified, raw dicts are returned instead of Mention models.
            limit: Maximum number of mentions to return (None for unlimited)

        Returns:
            FetchResult[Mention]: Container with list of Mention objects (or raw dicts
            when ``columns`` is specified)

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

        # Column projection mode: return raw dicts, skip model conversion
        if columns is not None:
            raw_rows: list[dict[str, Any]] = [
                raw_mention  # type: ignore[misc]
                async for raw_mention in self._fetcher.fetch_mentions(
                    global_event_id=global_event_id,
                    filter_obj=filter_obj,
                    use_bigquery=use_bigquery,
                    columns=columns,
                    limit=limit,
                )
            ]
            if limit is not None:
                raw_rows = raw_rows[:limit]
            return FetchResult(data=raw_rows, failed=[])  # type: ignore[arg-type]

        # Collect all mentions
        mentions: list[Mention] = [
            mention
            async for mention in self.stream(
                global_event_id=global_event_id,
                filter_obj=filter_obj,
                use_bigquery=use_bigquery,
                limit=limit,
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
        columns: Collection[str] | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[Mention]:
        """Stream mentions for a specific event.

        This method yields mentions one at a time, converting from internal _RawMention
        to public Mention model at the yield boundary. Memory-efficient for large result sets.

        Args:
            global_event_id: Global event ID to fetch mentions for (integer)
            filter_obj: Filter with date range for the query window
            use_bigquery: If True, use BigQuery directly (default: True, recommended for mentions)
            columns: Optional collection of BigQuery column names for column projection.
                When specified, raw dicts are yielded instead of Mention models.
            limit: Maximum number of mentions to yield (None for unlimited)

        Yields:
            Mention: Individual mention records with full type safety (or raw dicts
            when ``columns`` is specified)

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

        # DataFetcher.fetch_mentions() now yields _RawMention for all sources
        raw_mentions: AsyncIterator[_RawMention] = self._fetcher.fetch_mentions(
            global_event_id=global_event_id,
            filter_obj=filter_obj,
            use_bigquery=use_bigquery,
            columns=columns,
            limit=limit,
        )

        # Convert _RawMention to Mention at yield boundary
        async for raw_mention in raw_mentions:
            if columns is not None:
                # Column projection: yield raw dict directly
                yield raw_mention  # type: ignore[misc]
                mentions_count += 1
            else:
                mention = Mention.from_raw(raw_mention)
                mentions_count += 1
                yield mention

            if limit is not None and mentions_count >= limit:
                return

        logger.debug("Streamed %d mentions for event %s", mentions_count, global_event_id)

    def query_sync(
        self,
        global_event_id: int,
        filter_obj: EventFilter,
        *,
        use_bigquery: bool = True,
        columns: Collection[str] | None = None,
        limit: int | None = None,
    ) -> FetchResult[Mention]:
        """Synchronous wrapper for query().

        This is a convenience method for synchronous code. It runs the async query()
        method in a new event loop. For better performance, use the async version directly.

        Args:
            global_event_id: Global event ID to fetch mentions for (integer)
            filter_obj: Filter with date range for the query window
            use_bigquery: If True, use BigQuery directly (default: True)
            columns: Optional collection of BigQuery column names for column projection.
                When specified, raw dicts are returned instead of Mention models.
            limit: Maximum number of mentions to return (None for unlimited)

        Returns:
            FetchResult[Mention]: Container with list of Mention objects (or raw dicts
            when ``columns`` is specified)

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
                columns=columns,
                limit=limit,
            ),
        )

    def stream_sync(
        self,
        global_event_id: int,
        filter_obj: EventFilter,
        *,
        use_bigquery: bool = True,
        columns: Collection[str] | None = None,
        limit: int | None = None,
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
            columns: Optional collection of BigQuery column names for column projection.
                When specified, raw dicts are yielded instead of Mention models.
            limit: Maximum number of mentions to yield (None for unlimited)

        Returns:
            Iterator of individual Mention records (or raw dicts when ``columns``
            is specified)

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
                columns=columns,
                limit=limit,
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
