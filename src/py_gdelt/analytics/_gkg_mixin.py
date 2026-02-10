"""GKG analytics mixin providing prebuilt BigQuery analytics methods.

This mixin is composed into :class:`~py_gdelt.endpoints.gkg.GKGEndpoint`
to add analytics methods alongside existing ``query()``, ``stream()``, and
``aggregate()`` methods.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from py_gdelt.analytics._builders import build_gkg_approx_top_sql
from py_gdelt.sources.aggregation import AggFunc, Aggregation, AggregationResult, GKGUnnestField


if TYPE_CHECKING:
    from py_gdelt.filters import GKGFilter
    from py_gdelt.sources.bigquery import BigQuerySource
    from py_gdelt.sources.fetcher import DataFetcher


@runtime_checkable
class _HasFetcher(Protocol):
    """Protocol for classes that provide a DataFetcher."""

    _fetcher: DataFetcher


def _require_bigquery(self: _HasFetcher) -> BigQuerySource:
    """Return BigQuerySource or raise ConfigurationError.

    Args:
        self: Instance satisfying the _HasFetcher protocol.

    Returns:
        The BigQuerySource instance.

    Raises:
        ConfigurationError: If BigQuery credentials are not configured.
    """
    from py_gdelt.exceptions import ConfigurationError  # noqa: PLC0415

    bq = self._fetcher.bigquery_source
    if bq is None:
        msg = (
            "Analytics queries require BigQuery credentials. "
            "Pass bigquery_source to GDELTClient or configure "
            "GDELT_BIGQUERY_PROJECT."
        )
        raise ConfigurationError(msg)
    return bq


class GKGAnalyticsMixin:
    """Analytics methods for the GKG table.

    Provides prebuilt BigQuery analytics methods. Composed into
    :class:`~py_gdelt.endpoints.gkg.GKGEndpoint` via multiple
    inheritance.
    """

    async def aggregate_themes(
        self: _HasFetcher,
        filter_obj: GKGFilter,
        *,
        top_n: int = 50,
    ) -> AggregationResult:
        """Count theme occurrences across GKG records.

        Convenience wrapper around :meth:`aggregate_gkg` that unnests the
        semicolon-delimited themes column, counts occurrences, and returns
        the top-N themes ordered by frequency.

        Args:
            filter_obj: GKG filter with date range and query parameters.
            top_n: Number of top themes to return.

        Returns:
            AggregationResult with theme names and counts.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
        """
        bq = _require_bigquery(self)
        return await bq.aggregate_gkg(
            filter_obj,
            group_by=[GKGUnnestField.THEMES],
            aggregations=[Aggregation(func=AggFunc.COUNT, alias="count")],
            order_by="count",
            ascending=False,
            limit=top_n,
        )

    async def approx_top(
        self: _HasFetcher,
        filter_obj: GKGFilter,
        *,
        field: GKGUnnestField = GKGUnnestField.THEMES,
        n: int = 20,
    ) -> AggregationResult:
        """Approximate top-N values for a high-cardinality GKG field.

        Uses BigQuery's ``APPROX_TOP_COUNT`` for efficient approximate
        counting without full GROUP BY aggregation.

        Args:
            filter_obj: GKG filter with date range and query parameters.
            field: GKG field to count (themes, persons, or organizations).
            n: Number of top values to return (1-1000).

        Returns:
            AggregationResult with entity names and approximate counts.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
            ValueError: If n is out of range (1-1000).
        """
        bq = _require_bigquery(self)
        sql, params = build_gkg_approx_top_sql(filter_obj, field=field, n=n)
        rows, bytes_processed = await bq._execute_query_batch(sql, params)  # noqa: SLF001
        meta = bq.last_query_metadata
        return AggregationResult(
            rows=rows,
            group_by=[field.value],
            total_rows=len(rows),
            bytes_processed=bytes_processed,
            meta=meta,
            sql=sql,
        )

    def aggregate_themes_sync(
        self,
        filter_obj: GKGFilter,
        *,
        top_n: int = 50,
    ) -> AggregationResult:
        """Synchronous wrapper for aggregate_themes().

        Args:
            filter_obj: GKG filter with date range and query parameters.
            top_n: Number of top themes to return.

        Returns:
            AggregationResult with theme names and counts.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
            RuntimeError: If called from within an already running event loop.
        """
        return asyncio.run(
            self.aggregate_themes(filter_obj, top_n=top_n),  # type: ignore[misc]
        )

    def approx_top_sync(
        self,
        filter_obj: GKGFilter,
        *,
        field: GKGUnnestField = GKGUnnestField.THEMES,
        n: int = 20,
    ) -> AggregationResult:
        """Synchronous wrapper for approx_top().

        Args:
            filter_obj: GKG filter with date range and query parameters.
            field: GKG field to count (themes, persons, or organizations).
            n: Number of top values to return (1-1000).

        Returns:
            AggregationResult with entity names and approximate counts.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
            ValueError: If n is out of range (1-1000).
            RuntimeError: If called from within an already running event loop.
        """
        return asyncio.run(
            self.approx_top(filter_obj, field=field, n=n),  # type: ignore[misc]
        )
