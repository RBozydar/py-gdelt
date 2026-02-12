"""SQL builder functions for analytics queries.

Each builder returns a ``(sql, params)`` tuple. All column references are
validated against the per-table allowlists defined in
:mod:`py_gdelt.sources.bigquery`.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Final

from google.cloud import bigquery

from py_gdelt.analytics.types import EVENT_METRIC_CONFIG, EventMetric, TimeGranularity
from py_gdelt.exceptions import BigQueryError
from py_gdelt.sources.aggregation import GKG_UNNEST_CONFIG, GKGUnnestField
from py_gdelt.sources.bigquery import (
    TABLES,
    _build_where_clause_for_events,
    _build_where_clause_for_gkg,
    _validate_columns,
)


if TYPE_CHECKING:
    from py_gdelt.filters import EventFilter, GKGFilter

QueryParam = bigquery.ScalarQueryParameter | bigquery.ArrayQueryParameter

_SAFE_ALIAS_RE: Final[re.Pattern[str]] = re.compile(r"[^a-zA-Z0-9_]")

_GRANULARITY_INTERVAL: Final[dict[TimeGranularity, str]] = {
    TimeGranularity.DAY: "INTERVAL 1 DAY",
    TimeGranularity.WEEK: "INTERVAL 1 WEEK",
    TimeGranularity.MONTH: "INTERVAL 1 MONTH",
    TimeGranularity.QUARTER: "INTERVAL 3 MONTH",
    TimeGranularity.YEAR: "INTERVAL 1 YEAR",
}

# Metrics that represent averages / standard deviations should be left as NULL
# when there is no data in a date-spine bucket, rather than coalesced to 0.
_NULLABLE_AGG_FUNCS: Final[frozenset[str]] = frozenset({"AVG", "STDDEV"})

_DATE_TRUNC_EXPR: Final[str] = (
    "DATE_TRUNC(PARSE_DATE('%Y%m%d', CAST(SQLDATE AS STRING)), {granularity})"
)


def _sanitize_alias(value: str) -> str:
    """Convert a value to a safe SQL alias.

    Replaces non-alphanumeric characters with underscores and prepends ``v_``
    when the result starts with a digit or is empty.

    Args:
        value: Raw string value to sanitize.

    Returns:
        A string safe for use as a SQL column alias.
    """
    sanitized = _SAFE_ALIAS_RE.sub("_", value)
    if not sanitized or sanitized[0].isdigit():
        sanitized = f"v_{sanitized}"
    return sanitized


def _build_metric_expr(metric: EventMetric) -> str:
    """Build a SQL aggregation expression for a single metric.

    Args:
        metric: The event metric to build an expression for.

    Returns:
        SQL fragment like ``COUNT(*) AS count``.
    """
    cfg = EVENT_METRIC_CONFIG[metric]
    if cfg.bq_column == "*":
        return f"{cfg.agg_func}(*) AS {metric.value}"
    return f"{cfg.agg_func}({cfg.bq_column}) AS {metric.value}"


def build_time_series_sql(
    filter_obj: EventFilter,
    *,
    granularity: TimeGranularity = TimeGranularity.DAY,
    metrics: tuple[EventMetric, ...] = (EventMetric.COUNT,),
    moving_average_window: int | None = None,
    limit: int | None = None,
) -> tuple[str, list[bigquery.ScalarQueryParameter]]:
    """Build a time-series aggregation query for the Events table.

    Groups events into time buckets and computes the requested metrics.
    Optionally adds moving-average window columns by generating a dense
    date-spine CTE.

    Args:
        filter_obj: Event filter with mandatory date range.
        granularity: Time bucket granularity.
        metrics: Tuple of event metrics to compute per bucket.
        moving_average_window: If set, number of buckets for moving average.
        limit: Maximum number of rows to return.

    Returns:
        Tuple of (SQL string, list of query parameters).
    """
    where_clause, params = _build_where_clause_for_events(filter_obj)
    bucket_expr = _DATE_TRUNC_EXPR.format(granularity=granularity.value)
    metric_exprs = [_build_metric_expr(m) for m in metrics]

    if moving_average_window is None:
        # Simple GROUP BY query
        select_metrics = ",\n        ".join(metric_exprs)
        sql = (
            f"SELECT\n"
            f"    {bucket_expr} AS bucket,\n"
            f"        {select_metrics}\n"
            f"FROM `{TABLES['events']}`\n"
            f"WHERE {where_clause}\n"
            f"GROUP BY 1\n"
            f"ORDER BY bucket"
        )
        if limit is not None:
            sql += f"\nLIMIT {limit:d}"
        return sql, params

    # Moving-average path: build CTEs
    interval = _GRANULARITY_INTERVAL[granularity]
    select_metrics = ",\n            ".join(metric_exprs)

    # CTE 1: raw aggregation
    raw_cte = (
        f"raw AS (\n"
        f"        SELECT\n"
        f"            {bucket_expr} AS bucket,\n"
        f"            {select_metrics}\n"
        f"        FROM `{TABLES['events']}`\n"
        f"        WHERE {where_clause}\n"
        f"        GROUP BY 1\n"
        f"    )"
    )

    # CTE 2: dense date spine
    spine_cte = (
        f"spine AS (\n"
        f"        SELECT bucket\n"
        f"        FROM UNNEST(\n"
        f"            GENERATE_DATE_ARRAY(\n"
        f"                (SELECT MIN(bucket) FROM raw),\n"
        f"                (SELECT MAX(bucket) FROM raw),\n"
        f"                {interval}\n"
        f"            )\n"
        f"        ) AS bucket\n"
        f"    )"
    )

    # CTE 3: fill gaps with COALESCE for COUNT metrics, NULL for AVG/STDDEV
    coalesce_parts: list[str] = []
    for m in metrics:
        cfg = EVENT_METRIC_CONFIG[m]
        if cfg.agg_func in _NULLABLE_AGG_FUNCS:
            coalesce_parts.append(f"raw.{m.value}")
        else:
            coalesce_parts.append(f"COALESCE(raw.{m.value}, 0) AS {m.value}")

    coalesce_select = ",\n            ".join(coalesce_parts)
    filled_cte = (
        f"filled AS (\n"
        f"        SELECT\n"
        f"            spine.bucket,\n"
        f"            {coalesce_select}\n"
        f"        FROM spine\n"
        f"        LEFT JOIN raw USING (bucket)\n"
        f"    )"
    )

    # Final SELECT with window functions
    window_n = moving_average_window - 1
    final_parts: list[str] = ["bucket"]
    for m in metrics:
        final_parts.append(m.value)
        window_expr = (
            f"AVG({m.value}) OVER "
            f"(ORDER BY bucket ROWS BETWEEN {window_n} PRECEDING AND CURRENT ROW) "
            f"AS {m.value}_ma{moving_average_window}"
        )
        final_parts.append(window_expr)

    final_select = ",\n    ".join(final_parts)

    sql = (
        f"WITH\n"
        f"    {raw_cte},\n"
        f"    {spine_cte},\n"
        f"    {filled_cte}\n"
        f"SELECT\n"
        f"    {final_select}\n"
        f"FROM filled\n"
        f"ORDER BY bucket"
    )
    if limit is not None:
        sql += f"\nLIMIT {limit:d}"

    return sql, params


def build_extremes_sql(
    filter_obj: EventFilter,
    *,
    criterion: str = "GoldsteinScale",
    most_negative: int = 10,
    most_positive: int = 10,
) -> tuple[str, list[bigquery.ScalarQueryParameter]]:
    """Build a query that retrieves extreme-valued events.

    Uses ``ROW_NUMBER`` window functions to rank events by the specified
    criterion and returns both the most negative and most positive rows.

    Args:
        filter_obj: Event filter with mandatory date range.
        criterion: Column name to rank by (validated against allowlist).
        most_negative: Number of lowest-valued rows to return.
        most_positive: Number of highest-valued rows to return.

    Returns:
        Tuple of (SQL string, list of query parameters).

    Raises:
        BigQueryError: If the criterion column is not in the events allowlist.
    """
    _validate_columns([criterion], "events")
    where_clause, params = _build_where_clause_for_events(filter_obj)

    params.extend(
        [
            bigquery.ScalarQueryParameter("most_negative", "INT64", most_negative),
            bigquery.ScalarQueryParameter("most_positive", "INT64", most_positive),
        ],
    )

    sql = (
        f"WITH ranked AS (\n"
        f"    SELECT *,\n"
        f"        ROW_NUMBER() OVER (ORDER BY {criterion} ASC) AS _rank_asc,\n"
        f"        ROW_NUMBER() OVER (ORDER BY {criterion} DESC) AS _rank_desc\n"
        f"    FROM `{TABLES['events']}`\n"
        f"    WHERE {where_clause}\n"
        f")\n"
        f"SELECT * EXCEPT(_rank_asc, _rank_desc),\n"
        f"    CASE WHEN _rank_asc <= @most_negative THEN 'negative' ELSE 'positive' END"
        f" AS _extreme_type\n"
        f"FROM ranked\n"
        f"WHERE _rank_asc <= @most_negative OR _rank_desc <= @most_positive\n"
        f"ORDER BY {criterion} ASC"
    )

    return sql, params


def build_comparison_sql(
    filter_obj: EventFilter,
    *,
    compare_by: str,
    values: list[str],
    metric: EventMetric = EventMetric.COUNT,
    granularity: TimeGranularity = TimeGranularity.DAY,
) -> tuple[str, list[QueryParam]]:
    """Build a comparison query that pivots a metric by category values.

    For each value in ``values``, generates a CASE-WHEN column so the caller
    can compare the metric side-by-side across categories over time.

    Args:
        filter_obj: Event filter with mandatory date range.
        compare_by: Column name to compare across (validated against allowlist).
        values: List of category values to pivot on.
        metric: Metric to compute per category.
        granularity: Time bucket granularity.

    Returns:
        Tuple of (SQL string, list of query parameters).

    Raises:
        BigQueryError: If the compare_by column is not in the events allowlist,
            or if values produce duplicate column aliases after sanitization.
    """
    _validate_columns([compare_by], "events")
    where_clause, scalar_params = _build_where_clause_for_events(filter_obj)
    params: list[QueryParam] = list(scalar_params)

    # Add the IN UNNEST filter
    where_clause += f" AND {compare_by} IN UNNEST(@compare_values)"
    params.append(
        bigquery.ArrayQueryParameter("compare_values", "STRING", values),
    )

    bucket_expr = _DATE_TRUNC_EXPR.format(granularity=granularity.value)
    cfg = EVENT_METRIC_CONFIG[metric]

    # Build per-value CASE columns
    case_parts: list[str] = []
    seen_aliases: set[str] = set()
    for i, val in enumerate(values):
        param_name = f"val_{i}"
        params.append(bigquery.ScalarQueryParameter(param_name, "STRING", val))
        alias = f"{_sanitize_alias(val)}_{metric.value}"
        if alias in seen_aliases:
            msg = (
                f"Values {values!r} produce duplicate column alias {alias!r} "
                f"after sanitization. Use values with more distinct alphanumeric characters."
            )
            raise BigQueryError(msg)
        seen_aliases.add(alias)

        if cfg.bq_column == "*":
            expr = f"{cfg.agg_func}(CASE WHEN {compare_by} = @{param_name} THEN 1 END)"
        else:
            expr = (
                f"{cfg.agg_func}(CASE WHEN {compare_by} = @{param_name} THEN {cfg.bq_column} END)"
            )
        case_parts.append(f"{expr} AS {alias}")

    case_select = ",\n    ".join(case_parts)

    sql = (
        f"SELECT\n"
        f"    {bucket_expr} AS bucket,\n"
        f"    {case_select}\n"
        f"FROM `{TABLES['events']}`\n"
        f"WHERE {where_clause}\n"
        f"GROUP BY 1\n"
        f"ORDER BY bucket"
    )

    return sql, params


def build_trend_sql(
    filter_obj: EventFilter,
    *,
    metric: EventMetric = EventMetric.AVG_GOLDSTEIN,
    granularity: TimeGranularity = TimeGranularity.DAY,
) -> tuple[str, list[bigquery.ScalarQueryParameter]]:
    """Build a linear-trend analysis query for a single metric.

    Computes Pearson correlation between a sequential index and the metric
    value, then derives the slope and R-squared of the trend line.

    Args:
        filter_obj: Event filter with mandatory date range.
        metric: Metric to analyse for trend.
        granularity: Time bucket granularity.

    Returns:
        Tuple of (SQL string, list of query parameters).
    """
    where_clause, params = _build_where_clause_for_events(filter_obj)
    bucket_expr = _DATE_TRUNC_EXPR.format(granularity=granularity.value)
    cfg = EVENT_METRIC_CONFIG[metric]

    agg_expr = f"{cfg.agg_func}(*)" if cfg.bq_column == "*" else f"{cfg.agg_func}({cfg.bq_column})"

    sql = (
        f"WITH daily AS (\n"
        f"    SELECT\n"
        f"        {bucket_expr} AS bucket,\n"
        f"        {agg_expr} AS metric_value\n"
        f"    FROM `{TABLES['events']}`\n"
        f"    WHERE {where_clause}\n"
        f"    GROUP BY 1\n"
        f"),\n"
        f"indexed AS (\n"
        f"    SELECT *,\n"
        f"        ROW_NUMBER() OVER (ORDER BY bucket) AS day_index\n"
        f"    FROM daily\n"
        f")\n"
        f"SELECT\n"
        f"    SAFE_DIVIDE(\n"
        f"        CORR(day_index, metric_value) * STDDEV(metric_value),\n"
        f"        STDDEV(CAST(day_index AS FLOAT64))\n"
        f"    ) AS slope,\n"
        f"    POWER(CORR(day_index, metric_value), 2) AS r_squared,\n"
        f"    COUNT(*) AS data_points\n"
        f"FROM indexed"
    )

    return sql, params


def build_dyad_sql(
    filter_obj: EventFilter,
    *,
    actor_a: str,
    actor_b: str,
    granularity: TimeGranularity = TimeGranularity.DAY,
    metrics: tuple[EventMetric, ...] = (EventMetric.COUNT, EventMetric.AVG_GOLDSTEIN),
) -> tuple[str, list[bigquery.ScalarQueryParameter]]:
    """Build a dyadic-interaction query between two country actors.

    Adds directional columns (a-to-b vs b-to-a) for each metric so
    that the caller can compare bilateral event patterns over time.

    Args:
        filter_obj: Event filter with mandatory date range.
        actor_a: Country code for Actor A.
        actor_b: Country code for Actor B.
        granularity: Time bucket granularity.
        metrics: Tuple of event metrics to compute per direction.

    Returns:
        Tuple of (SQL string, list of query parameters).
    """
    where_clause, params = _build_where_clause_for_events(filter_obj)

    # Add actor pair condition
    where_clause += (
        " AND ((Actor1CountryCode = @actor_a AND Actor2CountryCode = @actor_b)"
        " OR (Actor1CountryCode = @actor_b AND Actor2CountryCode = @actor_a))"
    )
    params.extend(
        [
            bigquery.ScalarQueryParameter("actor_a", "STRING", actor_a),
            bigquery.ScalarQueryParameter("actor_b", "STRING", actor_b),
        ],
    )

    bucket_expr = _DATE_TRUNC_EXPR.format(granularity=granularity.value)

    # Build directional metric columns
    direction_parts: list[str] = []
    for m in metrics:
        cfg = EVENT_METRIC_CONFIG[m]
        if cfg.bq_column == "*":
            a_to_b = (
                f"{cfg.agg_func}(CASE WHEN Actor1CountryCode = @actor_a"
                f" AND Actor2CountryCode = @actor_b THEN 1 END)"
                f" AS a_to_b_{m.value}"
            )
            b_to_a = (
                f"{cfg.agg_func}(CASE WHEN Actor1CountryCode = @actor_b"
                f" AND Actor2CountryCode = @actor_a THEN 1 END)"
                f" AS b_to_a_{m.value}"
            )
        else:
            a_to_b = (
                f"{cfg.agg_func}(CASE WHEN Actor1CountryCode = @actor_a"
                f" AND Actor2CountryCode = @actor_b THEN {cfg.bq_column} END)"
                f" AS a_to_b_{m.value}"
            )
            b_to_a = (
                f"{cfg.agg_func}(CASE WHEN Actor1CountryCode = @actor_b"
                f" AND Actor2CountryCode = @actor_a THEN {cfg.bq_column} END)"
                f" AS b_to_a_{m.value}"
            )
        direction_parts.append(a_to_b)
        direction_parts.append(b_to_a)

    direction_select = ",\n    ".join(direction_parts)

    sql = (
        f"SELECT\n"
        f"    {bucket_expr} AS bucket,\n"
        f"    {direction_select}\n"
        f"FROM `{TABLES['events']}`\n"
        f"WHERE {where_clause}\n"
        f"GROUP BY 1\n"
        f"ORDER BY bucket"
    )

    return sql, params


def build_top_n_per_group_sql(
    filter_obj: EventFilter,
    *,
    partition_by: str,
    order_by: str,
    n: int = 10,
    ascending: bool = False,
) -> tuple[str, list[bigquery.ScalarQueryParameter]]:
    """Build a top-N-per-group query using ``QUALIFY``.

    Returns the top ``n`` rows within each partition, ranked by the
    specified ordering column.

    Args:
        filter_obj: Event filter with mandatory date range.
        partition_by: Column to partition by (validated against allowlist).
        order_by: Column to rank within each partition (validated against allowlist).
        n: Number of rows to keep per group.
        ascending: If True, rank in ascending order.

    Returns:
        Tuple of (SQL string, list of query parameters).

    Raises:
        BigQueryError: If partition_by or order_by are not in the events allowlist.
    """
    _validate_columns([partition_by, order_by], "events")
    where_clause, params = _build_where_clause_for_events(filter_obj)

    params.append(bigquery.ScalarQueryParameter("n", "INT64", n))

    direction = "ASC" if ascending else "DESC"

    sql = (
        f"SELECT *\n"
        f"FROM `{TABLES['events']}`\n"
        f"WHERE {where_clause}\n"
        f"QUALIFY ROW_NUMBER() OVER (\n"
        f"    PARTITION BY {partition_by}\n"
        f"    ORDER BY {order_by} {direction}\n"
        f") <= @n\n"
        f"ORDER BY {partition_by}, {order_by} {direction}"
    )

    return sql, params


def build_gkg_approx_top_sql(
    filter_obj: GKGFilter,
    *,
    field: GKGUnnestField = GKGUnnestField.THEMES,
    n: int = 20,
) -> tuple[str, list[bigquery.ScalarQueryParameter]]:
    """Build an approximate top-N query for a GKG unnest field.

    Uses ``APPROX_TOP_COUNT`` for efficient approximate counting of
    high-cardinality fields like themes, persons, and organizations.

    Note:
        BigQuery requires the second argument of ``APPROX_TOP_COUNT`` to be
        a literal integer, so ``n`` is bounds-checked and inlined directly
        into the SQL rather than parameterized.

    Args:
        filter_obj: GKG filter with mandatory date range.
        field: GKG field to count (themes, persons, or organizations).
        n: Number of top items to return (1--1000).

    Returns:
        Tuple of (SQL string, list of query parameters).

    Raises:
        BigQueryError: If n is outside the allowed range.
    """
    if not 1 <= n <= 1000:
        msg = f"n must be between 1 and 1000, got {n}"
        raise BigQueryError(msg)

    where_clause, params = _build_where_clause_for_gkg(filter_obj)
    bq_column, split_expr = GKG_UNNEST_CONFIG[field]

    sql = (
        f"WITH unnested AS (\n"
        f"    SELECT {split_expr} AS entity_name\n"
        f"    FROM `{TABLES['gkg']}`,\n"
        f"        UNNEST(SPLIT({bq_column}, ';')) AS item\n"
        f"    WHERE {where_clause}\n"
        f"        AND item != ''\n"
        f"),\n"
        f"approx AS (\n"
        f"    SELECT APPROX_TOP_COUNT(entity_name, {n:d}) AS top_items\n"
        f"    FROM unnested\n"
        f")\n"
        f"SELECT item.value AS name, item.count AS count\n"
        f"FROM approx, UNNEST(top_items) AS item\n"
        f"ORDER BY count DESC"
    )

    return sql, params
