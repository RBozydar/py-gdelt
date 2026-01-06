"""GKG (Global Knowledge Graph) endpoint for GDELT data.

This module provides the GKGEndpoint class for querying GDELT's Global Knowledge
Graph data through a unified interface that orchestrates between file downloads
(primary) and BigQuery (fallback).

The GKG contains enriched content analysis from news articles including themes,
entities, locations, tone, and other metadata extracted via NLP.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from py_gdelt.models.common import FetchResult
from py_gdelt.models.gkg import GKGRecord


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from py_gdelt.config import GDELTSettings
    from py_gdelt.filters import GKGFilter
    from py_gdelt.sources.bigquery import BigQuerySource
    from py_gdelt.sources.fetcher import ErrorPolicy
    from py_gdelt.sources.files import FileSource

__all__ = ["GKGEndpoint"]

logger = logging.getLogger(__name__)


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
