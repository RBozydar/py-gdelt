"""NGrams 3.0 endpoint for querying GDELT word and phrase data.

This module provides the NGramsEndpoint class for accessing GDELT NGrams 3.0 data,
which tracks word and phrase occurrences across global news coverage with contextual
information including position, language, and surrounding text.

NGrams are file-based only (no BigQuery support) and use the DataFetcher for
orchestrated downloads with automatic retry and error handling.

Example:
    >>> from py_gdelt.endpoints import NGramsEndpoint
    >>> from py_gdelt.filters import NGramsFilter, DateRange
    >>> from datetime import date
    >>>
    >>> async with NGramsEndpoint() as ngrams:
    ...     filter_obj = NGramsFilter(
    ...         date_range=DateRange(start=date(2024, 1, 1)),
    ...         language="en",
    ...         min_position=0,
    ...         max_position=20,
    ...     )
    ...     result = await ngrams.query(filter_obj)
    ...     for record in result:
    ...         print(record.ngram, record.context)
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from py_gdelt.config import GDELTSettings
from py_gdelt.models.common import FetchResult
from py_gdelt.models.ngrams import NGramRecord
from py_gdelt.parsers.ngrams import NGramsParser
from py_gdelt.sources.fetcher import DataFetcher
from py_gdelt.sources.files import FileSource


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from py_gdelt.filters import NGramsFilter

__all__ = ["NGramsEndpoint"]

logger = logging.getLogger(__name__)


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
            RateLimitError: If rate limited and retries exhausted
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> filter_obj = NGramsFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     ngram="climate",
            ... )
            >>> for record in endpoint.stream_sync(filter_obj):
            ...     print(f"{record.ngram}: {record.url}")
        """
        # Create a new event loop for the sync wrapper
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Run the async generator and yield results
            async_gen = self.stream(filter_obj)
            while True:
                try:
                    record = loop.run_until_complete(async_gen.__anext__())
                    yield record
                except StopAsyncIteration:
                    break
        finally:
            loop.close()
