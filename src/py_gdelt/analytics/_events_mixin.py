"""Events analytics mixin providing prebuilt BigQuery analytics methods.

This mixin is composed into :class:`~py_gdelt.endpoints.events.EventsEndpoint`
to add analytics methods alongside existing ``query()``, ``stream()``, and
``aggregate()`` methods.
"""

from __future__ import annotations

import asyncio
import datetime
import math
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from py_gdelt.analytics._builders import (
    build_comparison_sql,
    build_dyad_sql,
    build_extremes_sql,
    build_time_series_sql,
    build_top_n_per_group_sql,
    build_trend_sql,
)
from py_gdelt.analytics.results import (
    ComparisonResult,
    DyadResult,
    ExtremeEventsResult,
    PartitionedTopNResult,
    TimeSeriesResult,
    TrendResult,
)
from py_gdelt.analytics.types import EventMetric, TimeGranularity


if TYPE_CHECKING:
    from collections.abc import Collection

    from py_gdelt.filters import EventFilter
    from py_gdelt.sources.bigquery import BigQuerySource
    from py_gdelt.sources.fetcher import DataFetcher


@runtime_checkable
class _HasFetcher(Protocol):
    """Protocol for classes that provide a DataFetcher."""

    _fetcher: DataFetcher


def _serialize_value(v: object) -> object:
    """Convert BigQuery result values to JSON-serializable types.

    Args:
        v: A value from a BigQuery result row.

    Returns:
        JSON-serializable representation of the value.
    """
    if isinstance(v, datetime.date):
        return v.isoformat()
    return v


def _approx_p_value(r_squared: float, n: int) -> float | None:
    """Approximate p-value from R-squared and sample size.

    Uses a t-distribution approximation based on the relationship between
    the correlation coefficient and the t-statistic. The approximation
    is rough but sufficient for trend classification purposes.

    Args:
        r_squared: Coefficient of determination (0-1).
        n: Number of data points.

    Returns:
        Approximate two-tailed p-value, or None if insufficient data.
    """
    if n < 3 or r_squared >= 1.0:
        return None
    t_squared = r_squared * (n - 2) / (1.0 - r_squared)
    t_stat = math.sqrt(t_squared)
    # Rough two-tailed p-value approximation using exponential decay
    # (valid for large n, approximate for small n)
    df = n - 2
    if df < 3:
        return None
    p = 2.0 * math.exp(-0.717 * t_stat - 0.416 * t_stat * t_stat)
    return min(max(p, 0.0), 1.0)


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


class EventsAnalyticsMixin:
    """Analytics methods for the Events table.

    Provides prebuilt BigQuery analytics methods. Composed into
    :class:`~py_gdelt.endpoints.events.EventsEndpoint` via multiple
    inheritance.
    """

    # ── Async analytics methods ────────────────────────────────────────

    async def time_series(
        self: _HasFetcher,
        filter_obj: EventFilter,
        *,
        granularity: TimeGranularity = TimeGranularity.DAY,
        metrics: Collection[EventMetric] = (EventMetric.COUNT,),
        moving_average_window: int | None = None,
        limit: int | None = None,
    ) -> TimeSeriesResult:
        """Compute a time-series of event metrics bucketed by time period.

        Args:
            filter_obj: Event filter with date range and query parameters.
            granularity: Time bucketing granularity.
            metrics: Metrics to compute per bucket.
            moving_average_window: Window size for moving averages (None to skip).
            limit: Maximum number of buckets to return.

        Returns:
            TimeSeriesResult with ordered time buckets.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
        """
        bq = _require_bigquery(self)
        metrics_tuple = tuple(metrics)
        sql, params = build_time_series_sql(
            filter_obj,
            granularity=granularity,
            metrics=metrics_tuple,
            moving_average_window=moving_average_window,
            limit=limit,
        )
        rows, _ = await bq._execute_query_batch(sql, params)  # noqa: SLF001
        meta = bq.last_query_metadata
        return TimeSeriesResult(
            buckets=[{k: _serialize_value(v) for k, v in row.items()} for row in rows],
            granularity=granularity.value,
            metrics=[m.value for m in metrics_tuple],
            moving_average_window=moving_average_window,
            meta=meta,
            sql=sql,
        )

    async def extremes(
        self: _HasFetcher,
        filter_obj: EventFilter,
        *,
        criterion: str = "GoldsteinScale",
        most_negative: int = 10,
        most_positive: int = 10,
    ) -> ExtremeEventsResult:
        """Retrieve the most extreme events by a numeric criterion.

        Args:
            filter_obj: Event filter with date range and query parameters.
            criterion: Column name to rank by (validated against allowlist).
            most_negative: Number of lowest-valued rows to return.
            most_positive: Number of highest-valued rows to return.

        Returns:
            ExtremeEventsResult with most_negative and most_positive lists.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
        """
        bq = _require_bigquery(self)
        sql, params = build_extremes_sql(
            filter_obj,
            criterion=criterion,
            most_negative=most_negative,
            most_positive=most_positive,
        )
        rows, _ = await bq._execute_query_batch(sql, params)  # noqa: SLF001
        meta = bq.last_query_metadata

        negative_rows: list[dict[str, Any]] = []
        positive_rows: list[dict[str, Any]] = []
        for row in rows:
            extreme_type = row.get("_extreme_type")
            cleaned: dict[str, Any] = {
                k: _serialize_value(v) for k, v in row.items() if k != "_extreme_type"
            }
            if extreme_type == "negative":
                negative_rows.append(cleaned)
            else:
                positive_rows.append(cleaned)

        return ExtremeEventsResult(
            most_negative=negative_rows,
            most_positive=positive_rows,
            criterion=criterion,
            requested_negative=most_negative,
            requested_positive=most_positive,
            meta=meta,
            sql=sql,
        )

    async def compare(
        self: _HasFetcher,
        filter_obj: EventFilter,
        *,
        compare_by: str,
        values: list[str],
        metric: EventMetric = EventMetric.COUNT,
        granularity: TimeGranularity = TimeGranularity.DAY,
    ) -> ComparisonResult:
        """Compare a metric across category values over time.

        Args:
            filter_obj: Event filter with date range and query parameters.
            compare_by: Column name to compare across (validated against allowlist).
            values: List of category values to pivot on (2-10 entries, no duplicates).
            metric: Metric to compute per category.
            granularity: Time bucketing granularity.

        Returns:
            ComparisonResult with per-value metric columns.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
            ValueError: If values has fewer than 2 or more than 10 entries, or
                contains duplicates.
        """
        if len(values) < 2 or len(values) > 10:
            msg = f"values must have 2-10 entries, got {len(values)}"
            raise ValueError(msg)
        if len(values) != len(set(values)):
            msg = "values must not contain duplicates"
            raise ValueError(msg)

        bq = _require_bigquery(self)
        sql, params = build_comparison_sql(
            filter_obj,
            compare_by=compare_by,
            values=values,
            metric=metric,
            granularity=granularity,
        )
        rows, _ = await bq._execute_query_batch(sql, params)  # noqa: SLF001
        meta = bq.last_query_metadata

        return ComparisonResult(
            rows=[{k: _serialize_value(v) for k, v in row.items()} for row in rows],
            compare_by=compare_by,
            values=values,
            metric=metric.value,
            granularity=granularity.value,
            meta=meta,
            sql=sql,
        )

    async def trend(
        self: _HasFetcher,
        filter_obj: EventFilter,
        *,
        metric: EventMetric = EventMetric.AVG_GOLDSTEIN,
        granularity: TimeGranularity = TimeGranularity.DAY,
    ) -> TrendResult:
        """Detect a linear trend in a metric over time.

        Args:
            filter_obj: Event filter with date range and query parameters.
            metric: Metric to analyse for trend.
            granularity: Time bucketing granularity.

        Returns:
            TrendResult with slope, R-squared, direction, and p-value.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
            ValueError: If there are fewer than 2 data points for regression.
        """
        bq = _require_bigquery(self)
        sql, params = build_trend_sql(
            filter_obj,
            metric=metric,
            granularity=granularity,
        )
        rows, _ = await bq._execute_query_batch(sql, params)  # noqa: SLF001
        meta = bq.last_query_metadata

        if not rows:
            msg = "Trend requires at least 2 data points"
            raise ValueError(msg)

        row = rows[0]
        slope: float = float(row.get("slope") or 0.0)
        r_squared: float = float(row.get("r_squared") or 0.0)
        data_points: int = int(row.get("data_points") or 0)

        if data_points < 2:
            msg = "Trend requires at least 2 data points"
            raise ValueError(msg)

        # Determine direction from slope
        if abs(slope) < 1e-10:
            direction = "stable"
        elif slope > 0:
            direction = "escalating"
        else:
            direction = "de-escalating"

        p_value = _approx_p_value(r_squared, data_points)

        return TrendResult(
            slope=slope,
            r_squared=r_squared,
            direction=direction,
            p_value=p_value,
            data_points=data_points,
            metric=metric.value,
            granularity=granularity.value,
            meta=meta,
            sql=sql,
        )

    async def dyad_analysis(
        self: _HasFetcher,
        filter_obj: EventFilter,
        *,
        actor_a: str,
        actor_b: str,
        granularity: TimeGranularity = TimeGranularity.DAY,
        metrics: Collection[EventMetric] = (EventMetric.COUNT, EventMetric.AVG_GOLDSTEIN),
    ) -> DyadResult:
        """Analyse bilateral interactions between two country actors.

        Args:
            filter_obj: Event filter with date range and query parameters.
            actor_a: Country code for Actor A.
            actor_b: Country code for Actor B.
            granularity: Time bucketing granularity.
            metrics: Metrics to compute per direction.

        Returns:
            DyadResult with a_to_b and b_to_a time-series.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
        """
        bq = _require_bigquery(self)
        metrics_tuple = tuple(metrics)
        sql, params = build_dyad_sql(
            filter_obj,
            actor_a=actor_a,
            actor_b=actor_b,
            granularity=granularity,
            metrics=metrics_tuple,
        )
        rows, _ = await bq._execute_query_batch(sql, params)  # noqa: SLF001
        meta = bq.last_query_metadata

        a_to_b_rows: list[dict[str, Any]] = []
        b_to_a_rows: list[dict[str, Any]] = []
        for row in rows:
            a_row: dict[str, Any] = {"bucket": _serialize_value(row["bucket"])}
            b_row: dict[str, Any] = {"bucket": _serialize_value(row["bucket"])}
            for key, val in row.items():
                if key == "bucket":
                    continue
                if key.startswith("a_to_b_"):
                    a_row[key.removeprefix("a_to_b_")] = _serialize_value(val)
                elif key.startswith("b_to_a_"):
                    b_row[key.removeprefix("b_to_a_")] = _serialize_value(val)
            a_to_b_rows.append(a_row)
            b_to_a_rows.append(b_row)

        return DyadResult(
            a_to_b=a_to_b_rows,
            b_to_a=b_to_a_rows,
            actor_a=actor_a,
            actor_b=actor_b,
            granularity=granularity.value,
            metrics=[m.value for m in metrics_tuple],
            meta=meta,
            sql=sql,
        )

    async def top_n_per_group(
        self: _HasFetcher,
        filter_obj: EventFilter,
        *,
        partition_by: str,
        order_by: str,
        n: int = 10,
        ascending: bool = False,
    ) -> PartitionedTopNResult:
        """Retrieve the top N events per group.

        Args:
            filter_obj: Event filter with date range and query parameters.
            partition_by: Column to partition by (validated against allowlist).
            order_by: Column to rank within each partition (validated against allowlist).
            n: Number of rows to keep per group.
            ascending: If True, rank in ascending order.

        Returns:
            PartitionedTopNResult with groups mapping.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
        """
        bq = _require_bigquery(self)
        sql, params = build_top_n_per_group_sql(
            filter_obj,
            partition_by=partition_by,
            order_by=order_by,
            n=n,
            ascending=ascending,
        )
        rows, _ = await bq._execute_query_batch(sql, params)  # noqa: SLF001
        meta = bq.last_query_metadata

        groups: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            group_key = str(row.get(partition_by, ""))
            cleaned = {k: _serialize_value(v) for k, v in row.items()}
            groups.setdefault(group_key, []).append(cleaned)

        return PartitionedTopNResult(
            groups=groups,
            partition_by=partition_by,
            order_by=order_by,
            n=n,
            ascending=ascending,
            meta=meta,
            sql=sql,
        )

    # ── Sync wrappers ──────────────────────────────────────────────────

    def time_series_sync(
        self: _HasFetcher,
        filter_obj: EventFilter,
        *,
        granularity: TimeGranularity = TimeGranularity.DAY,
        metrics: Collection[EventMetric] = (EventMetric.COUNT,),
        moving_average_window: int | None = None,
        limit: int | None = None,
    ) -> TimeSeriesResult:
        """Synchronous wrapper for time_series().

        Args:
            filter_obj: Event filter with date range and query parameters.
            granularity: Time bucketing granularity.
            metrics: Metrics to compute per bucket.
            moving_average_window: Window size for moving averages (None to skip).
            limit: Maximum number of buckets to return.

        Returns:
            TimeSeriesResult with ordered time buckets.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
            RuntimeError: If called from within an already running event loop.
        """
        return asyncio.run(  # type: ignore[no-any-return]
            self.time_series(  # type: ignore[attr-defined]
                filter_obj,
                granularity=granularity,
                metrics=metrics,
                moving_average_window=moving_average_window,
                limit=limit,
            ),
        )

    def extremes_sync(
        self: _HasFetcher,
        filter_obj: EventFilter,
        *,
        criterion: str = "GoldsteinScale",
        most_negative: int = 10,
        most_positive: int = 10,
    ) -> ExtremeEventsResult:
        """Synchronous wrapper for extremes().

        Args:
            filter_obj: Event filter with date range and query parameters.
            criterion: Column name to rank by (validated against allowlist).
            most_negative: Number of lowest-valued rows to return.
            most_positive: Number of highest-valued rows to return.

        Returns:
            ExtremeEventsResult with most_negative and most_positive lists.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
            RuntimeError: If called from within an already running event loop.
        """
        return asyncio.run(  # type: ignore[no-any-return]
            self.extremes(  # type: ignore[attr-defined]
                filter_obj,
                criterion=criterion,
                most_negative=most_negative,
                most_positive=most_positive,
            ),
        )

    def compare_sync(
        self: _HasFetcher,
        filter_obj: EventFilter,
        *,
        compare_by: str,
        values: list[str],
        metric: EventMetric = EventMetric.COUNT,
        granularity: TimeGranularity = TimeGranularity.DAY,
    ) -> ComparisonResult:
        """Synchronous wrapper for compare().

        Args:
            filter_obj: Event filter with date range and query parameters.
            compare_by: Column name to compare across (validated against allowlist).
            values: List of category values to pivot on (2-10 entries, no duplicates).
            metric: Metric to compute per category.
            granularity: Time bucketing granularity.

        Returns:
            ComparisonResult with per-value metric columns.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
            ValueError: If values has fewer than 2 or more than 10 entries, or
                contains duplicates.
            RuntimeError: If called from within an already running event loop.
        """
        return asyncio.run(  # type: ignore[no-any-return]
            self.compare(  # type: ignore[attr-defined]
                filter_obj,
                compare_by=compare_by,
                values=values,
                metric=metric,
                granularity=granularity,
            ),
        )

    def trend_sync(
        self: _HasFetcher,
        filter_obj: EventFilter,
        *,
        metric: EventMetric = EventMetric.AVG_GOLDSTEIN,
        granularity: TimeGranularity = TimeGranularity.DAY,
    ) -> TrendResult:
        """Synchronous wrapper for trend().

        Args:
            filter_obj: Event filter with date range and query parameters.
            metric: Metric to analyse for trend.
            granularity: Time bucketing granularity.

        Returns:
            TrendResult with slope, R-squared, direction, and p-value.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
            ValueError: If there are fewer than 2 data points for regression.
            RuntimeError: If called from within an already running event loop.
        """
        return asyncio.run(  # type: ignore[no-any-return]
            self.trend(  # type: ignore[attr-defined]
                filter_obj,
                metric=metric,
                granularity=granularity,
            ),
        )

    def dyad_analysis_sync(
        self: _HasFetcher,
        filter_obj: EventFilter,
        *,
        actor_a: str,
        actor_b: str,
        granularity: TimeGranularity = TimeGranularity.DAY,
        metrics: Collection[EventMetric] = (EventMetric.COUNT, EventMetric.AVG_GOLDSTEIN),
    ) -> DyadResult:
        """Synchronous wrapper for dyad_analysis().

        Args:
            filter_obj: Event filter with date range and query parameters.
            actor_a: Country code for Actor A.
            actor_b: Country code for Actor B.
            granularity: Time bucketing granularity.
            metrics: Metrics to compute per direction.

        Returns:
            DyadResult with a_to_b and b_to_a time-series.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
            RuntimeError: If called from within an already running event loop.
        """
        return asyncio.run(  # type: ignore[no-any-return]
            self.dyad_analysis(  # type: ignore[attr-defined]
                filter_obj,
                actor_a=actor_a,
                actor_b=actor_b,
                granularity=granularity,
                metrics=metrics,
            ),
        )

    def top_n_per_group_sync(
        self: _HasFetcher,
        filter_obj: EventFilter,
        *,
        partition_by: str,
        order_by: str,
        n: int = 10,
        ascending: bool = False,
    ) -> PartitionedTopNResult:
        """Synchronous wrapper for top_n_per_group().

        Args:
            filter_obj: Event filter with date range and query parameters.
            partition_by: Column to partition by (validated against allowlist).
            order_by: Column to rank within each partition (validated against allowlist).
            n: Number of rows to keep per group.
            ascending: If True, rank in ascending order.

        Returns:
            PartitionedTopNResult with groups mapping.

        Raises:
            ConfigurationError: If BigQuery credentials are not configured.
            BigQueryError: If the query fails.
            RuntimeError: If called from within an already running event loop.
        """
        return asyncio.run(  # type: ignore[no-any-return]
            self.top_n_per_group(  # type: ignore[attr-defined]
                filter_obj,
                partition_by=partition_by,
                order_by=order_by,
                n=n,
                ascending=ascending,
            ),
        )
