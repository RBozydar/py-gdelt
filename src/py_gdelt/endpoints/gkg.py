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
    from collections.abc import AsyncIterator, Collection, Iterator

    from py_gdelt.config import GDELTSettings
    from py_gdelt.filters import GKGFilter
    from py_gdelt.sources.aggregation import Aggregation, AggregationResult, GKGUnnestField
    from py_gdelt.sources.bigquery import BigQuerySource
    from py_gdelt.sources.fetcher import ErrorPolicy
    from py_gdelt.sources.files import FileSource
    from py_gdelt.sources.metadata import QueryEstimate

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

    def _matches_filter(  # noqa: PLR0911
        self,
        record: GKGRecord,
        filter_obj: GKGFilter,
    ) -> bool:
        """Check if record matches filter criteria (client-side).

        Applied when using file source. BigQuery applies these server-side.
        Text fields use case-insensitive matching for better UX.

        Note:
            Multi-value filters (persons, organizations, themes) use OR logic -
            a record matches if ANY filter value is found in the record.

        Args:
            record: GKGRecord to check.
            filter_obj: Filter criteria.

        Returns:
            True if record matches all filter criteria.
        """
        # Themes exact match filter (OR logic: any theme matches, case-insensitive)
        if filter_obj.themes:
            record_themes = {t.name.upper() for t in record.themes}
            filter_themes = {t.upper() for t in filter_obj.themes}
            if not record_themes & filter_themes:  # No intersection
                return False

        # Theme prefix filter (case-insensitive prefix match)
        if filter_obj.theme_prefix:
            prefix_lower = filter_obj.theme_prefix.lower()
            if not any(t.name.lower().startswith(prefix_lower) for t in record.themes):
                return False

        # Persons filter (case-insensitive substring match, OR logic)
        if filter_obj.persons:
            filter_persons_lower = [fp.lower() for fp in filter_obj.persons]
            record_persons_lower = [p.name.lower() for p in record.persons]
            if not any(fp in rp for rp in record_persons_lower for fp in filter_persons_lower):
                return False

        # Organizations filter (case-insensitive substring match, OR logic)
        if filter_obj.organizations:
            filter_orgs_lower = [fo.lower() for fo in filter_obj.organizations]
            record_orgs_lower = [o.name.lower() for o in record.organizations]
            if not any(fo in ro for ro in record_orgs_lower for fo in filter_orgs_lower):
                return False

        # Country filter (exact match on FIPS in any location)
        if filter_obj.country and not any(
            loc.country_code == filter_obj.country for loc in record.locations
        ):
            return False

        # Tone filters (numeric range)
        tone_value = record.tone.tone if record.tone else None
        if filter_obj.min_tone is not None and (
            tone_value is None or tone_value < filter_obj.min_tone
        ):
            return False

        return not (
            filter_obj.max_tone is not None
            and (tone_value is None or tone_value > filter_obj.max_tone)
        )

    async def query(
        self,
        filter_obj: GKGFilter,
        *,
        use_bigquery: bool = False,
        columns: Collection[str] | None = None,
        limit: int | None = None,
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
            columns: Optional collection of BigQuery column names for column projection.
                When specified, raw dicts are returned instead of GKGRecord models.
                Requires ``use_bigquery=True`` for meaningful effect.
            limit: Maximum number of records to return (None for unlimited)

        Returns:
            FetchResult[GKGRecord] containing all matching records (or raw dicts
            when ``columns`` is specified)

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
        # Column projection mode: return raw dicts, skip model conversion/filter
        if columns is not None:
            raw_rows: list[dict[str, Any]] = [
                raw_gkg
                async for raw_gkg in self._fetcher.fetch_gkg(
                    filter_obj,
                    use_bigquery=use_bigquery,
                    columns=columns,
                    limit=limit,
                )
            ]
            if limit is not None:
                raw_rows = raw_rows[:limit]
            return FetchResult(data=raw_rows, failed=[])  # type: ignore[arg-type]

        records: list[GKGRecord] = [
            record
            async for record in self.stream(filter_obj, use_bigquery=use_bigquery, limit=limit)
        ]

        # Apply limit after client-side filtering
        if limit is not None:
            records = records[:limit]

        logger.info("GKG query completed: %d records fetched", len(records))

        # Return FetchResult (failures tracked by DataFetcher error policy)
        return FetchResult(data=records, failed=[])

    async def stream(
        self,
        filter_obj: GKGFilter,
        *,
        use_bigquery: bool = False,
        columns: Collection[str] | None = None,
        limit: int | None = None,
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
            columns: Optional collection of BigQuery column names for column projection.
                When specified, raw dicts are yielded instead of GKGRecord models.
                Requires ``use_bigquery=True`` for meaningful effect.
            limit: Maximum number of records to yield (None for unlimited)

        Yields:
            GKGRecord: Individual GKG records matching the filter criteria (or raw dicts
            when ``columns`` is specified)

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

        count = 0
        # Build kwargs conditionally so columns is only passed when specified
        fetch_kwargs: dict[str, Any] = {"use_bigquery": use_bigquery, "limit": limit}
        if columns is not None:
            fetch_kwargs["columns"] = columns
        # Use DataFetcher to fetch raw GKG records
        async for raw_gkg in self._fetcher.fetch_gkg(filter_obj, **fetch_kwargs):
            if columns is not None:
                # Column projection: yield raw dict directly
                yield raw_gkg
                count += 1
                if limit is not None and count >= limit:
                    return
                continue

            # Convert _RawGKG to GKGRecord at yield boundary
            try:
                record = GKGRecord.from_raw(raw_gkg)

                # Apply client-side filtering (file source doesn't filter)
                if not self._matches_filter(record, filter_obj):
                    continue

                yield record
                count += 1

                if limit is not None and count >= limit:
                    return
            except Exception as e:  # noqa: BLE001
                # Error boundary: log conversion errors but continue processing other records
                logger.warning("Failed to convert raw GKG record to GKGRecord: %s", e)
                continue

    def query_sync(
        self,
        filter_obj: GKGFilter,
        *,
        use_bigquery: bool = False,
        columns: Collection[str] | None = None,
        limit: int | None = None,
    ) -> FetchResult[GKGRecord]:
        """Synchronous wrapper for query().

        This is a convenience method for synchronous code that internally uses
        asyncio.run() to execute the async query() method.

        Args:
            filter_obj: GKG filter with date range and query parameters
            use_bigquery: If True, skip files and use BigQuery directly (default: False)
            columns: Optional collection of BigQuery column names for column projection.
                When specified, raw dicts are returned instead of GKGRecord models.
            limit: Maximum number of records to return (None for unlimited)

        Returns:
            FetchResult[GKGRecord] containing all matching records (or raw dicts
            when ``columns`` is specified)

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
        return asyncio.run(
            self.query(filter_obj, use_bigquery=use_bigquery, columns=columns, limit=limit)
        )

    def stream_sync(
        self,
        filter_obj: GKGFilter,
        *,
        use_bigquery: bool = False,
        columns: Collection[str] | None = None,
        limit: int | None = None,
    ) -> Iterator[GKGRecord]:
        """Synchronous wrapper for stream().

        This method provides a synchronous iterator interface over async streaming.
        It internally manages the event loop and yields records one at a time.

        Note: This creates a new event loop for each iteration, which has some overhead.
        For better performance, use the async stream() method directly if possible.

        Args:
            filter_obj: GKG filter with date range and query parameters
            use_bigquery: If True, skip files and use BigQuery directly (default: False)
            columns: Optional collection of BigQuery column names for column projection.
                When specified, raw dicts are yielded instead of GKGRecord models.
            limit: Maximum number of records to yield (None for unlimited)

        Returns:
            Iterator of GKGRecord instances (or raw dicts when ``columns``
            is specified)

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
            async for record in self.stream(
                filter_obj, use_bigquery=use_bigquery, columns=columns, limit=limit
            ):
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

    async def aggregate(
        self,
        filter_obj: GKGFilter,
        *,
        group_by: list[str | GKGUnnestField],
        aggregations: list[Aggregation],
        order_by: str | None = None,
        ascending: bool = False,
        limit: int | None = None,
    ) -> AggregationResult:
        """Run an aggregation query against the GDELT GKG table via BigQuery.

        Supports UNNEST(SPLIT(...)) for semicolon-delimited GKG fields such as
        themes, persons, and organizations. At most one ``GKGUnnestField`` may
        appear in ``group_by`` per query.

        Requires BigQuery credentials to be configured.

        Args:
            filter_obj: GKG filter with date range and query parameters.
            group_by: Column names or ``GKGUnnestField`` values to group by.
            aggregations: List of aggregation specifications.
            order_by: Column or alias to order results by. Defaults to the
                first aggregation alias (descending) when ``limit`` is set.
            ascending: If True, sort ascending; otherwise descending.
            limit: Maximum number of result rows.

        Returns:
            AggregationResult with rows, group_by columns, and metadata.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If column names are invalid or query execution fails.
            SecurityError: If an alias fails sanitization.

        Example:
            >>> from py_gdelt.sources.aggregation import (
            ...     AggFunc, Aggregation, GKGUnnestField,
            ... )
            >>> result = await endpoint.aggregate(
            ...     filter_obj,
            ...     group_by=[GKGUnnestField.THEMES],
            ...     aggregations=[Aggregation(func=AggFunc.COUNT, alias="cnt")],
            ...     limit=20,
            ... )
            >>> for row in result.rows:
            ...     print(row["themes"], row["cnt"])
        """
        from py_gdelt.exceptions import ConfigurationError

        bq: BigQuerySource | None = self._fetcher.bigquery_source
        if bq is None:
            msg = (
                "Aggregation queries require BigQuery credentials. "
                "Please configure GDELT_BIGQUERY_PROJECT and optionally "
                "GDELT_BIGQUERY_CREDENTIALS."
            )
            raise ConfigurationError(msg)

        return await bq.aggregate_gkg(
            filter_obj,
            group_by=group_by,
            aggregations=aggregations,
            order_by=order_by,
            ascending=ascending,
            limit=limit,
        )

    def aggregate_sync(
        self,
        filter_obj: GKGFilter,
        *,
        group_by: list[str | GKGUnnestField],
        aggregations: list[Aggregation],
        order_by: str | None = None,
        ascending: bool = False,
        limit: int | None = None,
    ) -> AggregationResult:
        """Synchronous wrapper for aggregate().

        Args:
            filter_obj: GKG filter with date range and query parameters.
            group_by: Column names or ``GKGUnnestField`` values to group by.
            aggregations: List of aggregation specifications.
            order_by: Column or alias to order results by.
            ascending: If True, sort ascending; otherwise descending.
            limit: Maximum number of result rows.

        Returns:
            AggregationResult with rows, group_by columns, and metadata.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If column names are invalid or query execution fails.
            SecurityError: If an alias fails sanitization.
            RuntimeError: If called from within an already running event loop.

        Example:
            >>> result = endpoint.aggregate_sync(
            ...     filter_obj,
            ...     group_by=[GKGUnnestField.THEMES],
            ...     aggregations=[Aggregation(func=AggFunc.COUNT, alias="cnt")],
            ...     limit=20,
            ... )
        """
        return asyncio.run(
            self.aggregate(
                filter_obj,
                group_by=group_by,
                aggregations=aggregations,
                order_by=order_by,
                ascending=ascending,
                limit=limit,
            ),
        )

    async def estimate(
        self,
        filter_obj: GKGFilter,
        *,
        columns: Collection[str] | None = None,
        limit: int | None = None,
    ) -> QueryEstimate:
        """Estimate the cost of a GKG query via a BigQuery dry run.

        Performs a BigQuery dry run to determine how many bytes the query would
        scan. No data is read and no charges are incurred.

        Args:
            filter_obj: GKG filter with date range and query parameters.
            columns: Optional column names for projection (defaults to all).
            limit: Maximum number of rows the query would return.

        Returns:
            QueryEstimate with estimated bytes and the query SQL.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If column names are invalid or the dry run fails.

        Example:
            >>> estimate = await endpoint.estimate(filter_obj, limit=1000)
            >>> print(f"Would scan {estimate.bytes_processed} bytes")
            >>> print(estimate.query)
        """
        from py_gdelt.exceptions import ConfigurationError

        bq: BigQuerySource | None = self._fetcher.bigquery_source
        if bq is None:
            msg = (
                "Estimate queries require BigQuery credentials. "
                "Please configure GDELT_BIGQUERY_PROJECT and optionally "
                "GDELT_BIGQUERY_CREDENTIALS."
            )
            raise ConfigurationError(msg)

        columns_list = list(columns) if columns is not None else None
        return await bq.estimate_gkg(
            filter_obj,
            columns=columns_list,
            limit=limit,
        )

    def estimate_sync(
        self,
        filter_obj: GKGFilter,
        *,
        columns: Collection[str] | None = None,
        limit: int | None = None,
    ) -> QueryEstimate:
        """Synchronous wrapper for estimate().

        Args:
            filter_obj: GKG filter with date range and query parameters.
            columns: Optional column names for projection (defaults to all).
            limit: Maximum number of rows the query would return.

        Returns:
            QueryEstimate with estimated bytes and the query SQL.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If column names are invalid or the dry run fails.
            RuntimeError: If called from within an already running event loop.

        Example:
            >>> estimate = endpoint.estimate_sync(filter_obj, limit=1000)
            >>> print(f"Would scan {estimate.bytes_processed} bytes")
        """
        return asyncio.run(
            self.estimate(
                filter_obj,
                columns=columns,
                limit=limit,
            ),
        )
