---
title: "feat: Add SQL-level analytics layer for BigQuery"
type: feat
date: 2026-02-08
revision: 2
revision_note: "Incorporated 6 reviewer findings: collapsed 6 phases to 3, fixed MA gap bug, dropped AnalyticsResult base class, dropped BigQueryCache, fixed mixin typing, fixed CORR/APPROX_TOP_COUNT model issues"
---

# feat: Add SQL-level analytics layer for BigQuery

## Overview

Push analytical computation from client-side Python to BigQuery SQL. This eliminates OOM crashes, removes the 5,000-row streaming cap, and removes the 10,000 GKG entity cap in the primary consumer (`deep_research` LLM agent). The analytics layer adds prebuilt query methods to `EventsEndpoint` and `GKGEndpoint` via mixin classes, with typed result models and session cost tracking.

## Problem Statement

Today py-gdelt is an excellent data access layer, but all analytical computation happens client-side:
- Streams 5,000 raw event rows and aggregates with Python `Counter`s and heaps
- Computes Goldstein mean/stddev, quad-class breakdowns, event type distributions entirely in Python
- GKG entity counting capped at 10,000 unique entities due to memory pressure
- Had OOM crashes before implementing streaming caps
- MCP server at `src/py_gdelt/mcp_server/server.py` (lines 179-406) does ~230 lines of manual streaming aggregation

The existing `aggregate()` infrastructure provides GROUP BY queries, but lacks higher-level analytics: time-series bucketing, trend detection, comparisons, approximate aggregations, and cost safety.

## Proposed Solution

### Architecture: Methods on Endpoints with Mixins

```
Layer 1: Prebuilt Analytics    client.events.time_series(), .compare(), .trend(), .extremes()
Layer 2: Aggregation Builder   client.events.aggregate(filter, group_by, aggregations)  [existing]
Layer 3: Raw Streaming         client.events.stream(filter, use_bigquery=True)          [existing]
```

Analytics methods live on `EventsEndpoint`/`GKGEndpoint` (consistent with existing `aggregate()`). Implementation is extracted into mixin classes. SQL generation uses per-query-type builder functions.

### Key Changes from v1 (Reviewer Findings)

1. **Dropped `AnalyticsResult` base class** — extend existing `AggregationResult` with `meta` and `sql` fields instead. New result types (`TimeSeriesResult`, `ExtremeEventsResult`) stand alone as `BaseModel` subclasses; no shared hierarchy needed.

2. **Dropped `BigQueryCache`** — BigQuery already caches results for 24 hours for free. YAGNI until we measure cache miss rates. The existing file `Cache` is unmodified.

3. **Fixed moving average gap bug** — `ROWS BETWEEN N PRECEDING` operates on rows, not calendar days. When data has missing days, windows span wrong time periods. Fix: `GENERATE_DATE_ARRAY` + `LEFT JOIN` for a dense date spine before applying window functions.

4. **`CORR` removed from `AggFunc`** — `CORR(x, y)` requires two columns but `Aggregation` has single `column: str`. Trend detection uses a dedicated `build_trend_sql()` function that hardcodes the `CORR` call.

5. **`APPROX_TOP_COUNT` n inlined as literal** — BigQuery requires a literal integer, not a parameter. Validated as `int` and bounds-checked (1-1000) before safe string interpolation.

6. **Mixin typing uses Protocol** — instead of `type: ignore[assignment]`, the mixin defines a Protocol for `self` that declares `_fetcher: DataFetcher`. This passes strict mypy.

7. **`SessionCostTracker` lives on `GDELTClient`** — not on `BigQuerySource`, avoiding bidirectional dependency.

8. **`GKGEndpoint._fetcher` typed as `DataFetcher`** — fixes the `Any` typing at `gkg.py:111`.

9. **Collapsed 6 phases → 3 phases** — ship value faster with less overhead.

### File Layout

```
src/py_gdelt/
  analytics/                     # NEW package
    __init__.py                  # Public re-exports
    results.py                   # TimeSeriesResult, ExtremeEventsResult, ComparisonResult, etc.
    types.py                     # TimeGranularity, EventMetric enums, metric config
    _builders.py                 # Private: SQL generation per query type
    _cost.py                     # SessionCostTracker
    _events_mixin.py             # EventsAnalyticsMixin
    _gkg_mixin.py                # GKGAnalyticsMixin

  sources/
    aggregation.py               # MODIFY: Add APPROX_COUNT_DISTINCT, STDDEV to AggFunc
                                 #         Add meta + sql fields to AggregationResult
    bigquery.py                  # MODIFY: Update _render_agg_expr() for new AggFunc values

  endpoints/
    events.py                    # MODIFY: Compose EventsAnalyticsMixin
    gkg.py                       # MODIFY: Fix _fetcher typing, compose GKGAnalyticsMixin

  exceptions.py                  # MODIFY: Add BudgetExceededError
  __init__.py                    # MODIFY: Export new public types
```

---

## Technical Approach

### Phase 1: Foundation (Types, Results, AggFunc, Cost Tracker, SQL Builders)

**Goal**: All types, SQL builders, and cost tracking — everything except endpoint wiring.

#### 1.1 Extend Existing `AggregationResult`

Modify `src/py_gdelt/sources/aggregation.py`:

```diff
--- a/src/py_gdelt/sources/aggregation.py
+++ b/src/py_gdelt/sources/aggregation.py
@@ -33,6 +33,8 @@ class AggFunc(StrEnum):
     MAX = "MAX"
     COUNT_DISTINCT = "COUNT_DISTINCT"
+    APPROX_COUNT_DISTINCT = "APPROX_COUNT_DISTINCT"
+    STDDEV = "STDDEV"
```

Add fields to `AggregationResult`:

```diff
@@ -87,6 +89,10 @@ class AggregationResult(BaseModel):
     group_by: list[str]
     total_rows: int
     bytes_processed: int | None = None
+    # Query metadata (bytes billed, cache hit, timing)
+    meta: QueryMetadata | None = None
+    # Generated SQL for debugging (parameterized, no values inlined)
+    sql: str | None = None
```

Note: `CORR` is NOT added to `AggFunc` because it requires two columns. It's handled in the dedicated `build_trend_sql()` builder.

Update `_render_agg_expr()` in `src/py_gdelt/sources/bigquery.py` to handle `APPROX_COUNT_DISTINCT` and `STDDEV`.

#### 1.2 New Result Models

New file: `src/py_gdelt/analytics/results.py`

Each result type is a standalone `BaseModel`. No shared base class — the only shared pattern is that they all carry `meta: QueryMetadata | None` and `sql: str | None`. Each provides `to_compact() -> str` and `__str__`.

**TimeSeriesResult**:
- `buckets: list[dict[str, Any]]` — keys: `"bucket"` (ISO date str), one key per metric, optional MA keys `"{metric}_ma{window}"`
- `granularity: str`
- `metrics: list[str]`
- `moving_average_window: int | None`
- `meta: QueryMetadata | None = None`
- `sql: str | None = None`

**ExtremeEventsResult**:
- `most_negative: list[dict[str, Any]]` — full event rows (BQ PascalCase keys)
- `most_positive: list[dict[str, Any]]`
- `criterion: str`
- `requested_negative: int`
- `requested_positive: int`
- `meta: QueryMetadata | None = None`
- `sql: str | None = None`

**ComparisonResult**:
- `rows: list[dict[str, Any]]` — keys: `"bucket"`, `"{value}_{metric}"` per value
- `compare_by: str`
- `values: list[str]`
- `metric: str`
- `granularity: str`
- `meta: QueryMetadata | None = None`
- `sql: str | None = None`

**TrendResult**:
- `slope: float`
- `r_squared: float`
- `direction: str` — "escalating" / "de-escalating" / "stable"
- `p_value: float | None` — approximated client-side from R² and n, or None
- `data_points: int`
- `metric: str`
- `granularity: str`
- `meta: QueryMetadata | None = None`
- `sql: str | None = None`

**DyadResult**:
- `a_to_b: list[dict[str, Any]]` — time series buckets (Actor1=a, Actor2=b)
- `b_to_a: list[dict[str, Any]]` — time series buckets (Actor1=b, Actor2=a)
- `actor_a: str`
- `actor_b: str`
- `granularity: str`
- `metrics: list[str]`
- `meta: QueryMetadata | None = None`
- `sql: str | None = None`

**PartitionedTopNResult**:
- `groups: dict[str, list[dict[str, Any]]]` — group key → top-N rows
- `partition_by: str`
- `order_by: str`
- `n: int`
- `ascending: bool`
- `meta: QueryMetadata | None = None`
- `sql: str | None = None`

#### 1.3 Domain Types

New file: `src/py_gdelt/analytics/types.py`

```python
from __future__ import annotations

from enum import StrEnum
from typing import Final, NamedTuple


class TimeGranularity(StrEnum):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    QUARTER = "QUARTER"
    YEAR = "YEAR"


class EventMetric(StrEnum):
    COUNT = "count"
    AVG_GOLDSTEIN = "avg_goldstein"
    AVG_TONE = "avg_tone"
    AVG_NUM_MENTIONS = "avg_num_mentions"
    AVG_NUM_SOURCES = "avg_num_sources"
    AVG_NUM_ARTICLES = "avg_num_articles"
    STDDEV_GOLDSTEIN = "stddev_goldstein"


class MetricConfig(NamedTuple):
    agg_func: str
    bq_column: str


EVENT_METRIC_CONFIG: Final[dict[EventMetric, MetricConfig]] = {
    EventMetric.COUNT: MetricConfig("COUNT", "*"),
    EventMetric.AVG_GOLDSTEIN: MetricConfig("AVG", "GoldsteinScale"),
    EventMetric.AVG_TONE: MetricConfig("AVG", "AvgTone"),
    EventMetric.AVG_NUM_MENTIONS: MetricConfig("AVG", "NumMentions"),
    EventMetric.AVG_NUM_SOURCES: MetricConfig("AVG", "NumSources"),
    EventMetric.AVG_NUM_ARTICLES: MetricConfig("AVG", "NumArticles"),
    EventMetric.STDDEV_GOLDSTEIN: MetricConfig("STDDEV", "GoldsteinScale"),
}
```

#### 1.4 Session Cost Tracker

New file: `src/py_gdelt/analytics/_cost.py`

```python
class SessionCostTracker:
    """Cumulative BigQuery cost tracker for analytics sessions.

    Args:
        budget_bytes: Maximum cumulative bytes to process. None for no limit.
    """
    def __init__(self, budget_bytes: int | None = None) -> None:
        self._budget_bytes = budget_bytes
        self._cumulative_bytes: int = 0
        self._query_count: int = 0
        self._lock = threading.Lock()  # Forward-compat with free-threaded Python

    @property
    def cumulative_bytes(self) -> int: ...
    @property
    def remaining_bytes(self) -> int | None: ...
    @property
    def query_count(self) -> int: ...

    def record(self, bytes_processed: int) -> None:
        """Record bytes from completed query. Raises BudgetExceededError if over budget."""

    def check_budget(self, estimated_bytes: int) -> None:
        """Pre-flight check. Raises BudgetExceededError if estimate would exceed budget."""

    def reset(self) -> None:
        """Reset tracker to zero."""
```

**Location**: Lives on `GDELTClient` (NOT `BigQuerySource`), avoiding bidirectional dependency. Passed down to analytics mixin methods via `self._fetcher.bigquery_source`.

**Exception**: `BudgetExceededError(BigQueryError)` added to `src/py_gdelt/exceptions.py`.

#### 1.5 SQL Builder Functions

New file: `src/py_gdelt/analytics/_builders.py`

Each builder returns `tuple[str, list[ScalarQueryParameter]]`. All column names validated against `ALLOWED_COLUMNS`. All user values parameterized. Partition filters mandatory.

**`build_time_series_sql()`** — with dense date spine fix:

```sql
WITH daily AS (
    SELECT
        DATE_TRUNC(PARSE_DATE('%Y%m%d', CAST(SQLDATE AS STRING)), DAY) AS bucket,
        COUNT(*) AS count,
        AVG(GoldsteinScale) AS avg_goldstein
    FROM `gdelt-bq.gdeltv2.events_partitioned`
    WHERE _PARTITIONTIME >= @start_date AND _PARTITIONTIME <= @end_date
    GROUP BY 1
),
-- Dense date spine: ensures every calendar day has a row (NULL-filled if no data)
date_spine AS (
    SELECT d AS bucket
    FROM UNNEST(GENERATE_DATE_ARRAY(@start_date, @end_date, INTERVAL 1 DAY)) AS d
),
filled AS (
    SELECT
        s.bucket,
        COALESCE(d.count, 0) AS count,
        d.avg_goldstein
    FROM date_spine s
    LEFT JOIN daily d ON s.bucket = d.bucket
)
SELECT
    bucket,
    count,
    avg_goldstein,
    AVG(count) OVER (ORDER BY bucket ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS count_ma7,
    AVG(avg_goldstein) OVER (ORDER BY bucket ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS avg_goldstein_ma7
FROM filled
ORDER BY bucket
```

- Date spine only added when `moving_average_window` is not None (otherwise gaps are fine)
- `COALESCE(metric, 0)` for COUNT metrics; `NULL` preserved for AVG metrics (correct: missing days shouldn't be averaged as zero)
- Granularity-aware spine: `INTERVAL 1 DAY` for DAY, `INTERVAL 1 WEEK` for WEEK, etc.

**`build_extremes_sql()`** — single scan with ROW_NUMBER:

```sql
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (ORDER BY GoldsteinScale ASC) AS _rank_asc,
        ROW_NUMBER() OVER (ORDER BY GoldsteinScale DESC) AS _rank_desc
    FROM `gdelt-bq.gdeltv2.events_partitioned`
    WHERE _PARTITIONTIME >= @start_date AND _PARTITIONTIME <= @end_date
)
SELECT * EXCEPT(_rank_asc, _rank_desc),
    CASE WHEN _rank_asc <= @most_negative THEN 'negative' ELSE 'positive' END AS _extreme_type
FROM ranked
WHERE _rank_asc <= @most_negative OR _rank_desc <= @most_positive
ORDER BY GoldsteinScale ASC
```

**`build_comparison_sql()`** — CASE WHEN pivot:

```sql
SELECT
    DATE_TRUNC(PARSE_DATE('%Y%m%d', CAST(SQLDATE AS STRING)), WEEK) AS bucket,
    AVG(CASE WHEN Actor1CountryCode = @val_0 THEN GoldsteinScale END) AS USA_avg_goldstein,
    AVG(CASE WHEN Actor1CountryCode = @val_1 THEN GoldsteinScale END) AS CHN_avg_goldstein,
    COUNT(CASE WHEN Actor1CountryCode = @val_0 THEN 1 END) AS USA_count,
    COUNT(CASE WHEN Actor1CountryCode = @val_1 THEN 1 END) AS CHN_count
FROM `gdelt-bq.gdeltv2.events_partitioned`
WHERE _PARTITIONTIME >= @start_date AND _PARTITIONTIME <= @end_date
  AND Actor1CountryCode IN UNNEST(@compare_values)
GROUP BY 1
ORDER BY bucket
```

**`build_trend_sql()`** — CORR/STDDEV with SAFE_DIVIDE:

```sql
WITH daily AS (
    SELECT
        DATE_TRUNC(PARSE_DATE('%Y%m%d', CAST(SQLDATE AS STRING)), DAY) AS bucket,
        AVG(GoldsteinScale) AS metric_value
    FROM `gdelt-bq.gdeltv2.events_partitioned`
    WHERE _PARTITIONTIME >= @start_date AND _PARTITIONTIME <= @end_date
    GROUP BY 1
),
indexed AS (
    SELECT *,
        ROW_NUMBER() OVER (ORDER BY bucket) AS day_index
    FROM daily
)
SELECT
    SAFE_DIVIDE(
        CORR(day_index, metric_value) * STDDEV(metric_value),
        STDDEV(CAST(day_index AS FLOAT64))
    ) AS slope,
    POWER(CORR(day_index, metric_value), 2) AS r_squared,
    COUNT(*) AS data_points
FROM indexed
```

Note: `CORR` is hardcoded in this builder, NOT exposed via `AggFunc`. `SAFE_DIVIDE` prevents division-by-zero when all metric values are identical (STDDEV=0).

**`build_dyad_sql()`** — accepts `EventFilter` (not bare params) + actor overrides:

```python
def build_dyad_sql(
    filter_obj: EventFilter,
    actor_a: str,
    actor_b: str,
    granularity: TimeGranularity,
    metrics: list[EventMetric],
) -> tuple[str, list[ScalarQueryParameter]]:
```

Single scan with CASE WHEN pivot for both directions.

**`build_top_n_per_group_sql()`** — QUALIFY:

```sql
SELECT *
FROM `gdelt-bq.gdeltv2.events_partitioned`
WHERE _PARTITIONTIME >= @start_date AND _PARTITIONTIME <= @end_date
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY Actor1CountryCode
    ORDER BY GoldsteinScale DESC
) <= @n
ORDER BY Actor1CountryCode, GoldsteinScale DESC
```

**`build_gkg_approx_top_sql()`** — n inlined as literal:

```python
def build_gkg_approx_top_sql(
    filter_obj: GKGFilter,
    field: GKGUnnestField,
    n: int = 20,  # validated: 1 <= n <= 1000, inlined as literal
) -> tuple[str, list[ScalarQueryParameter]]:
```

```sql
WITH unnested AS (
    SELECT SPLIT(item, ',')[SAFE_OFFSET(0)] AS entity_name
    FROM `gdelt-bq.gdeltv2.gkg_partitioned`,
        UNNEST(SPLIT(V2Themes, ';')) AS item
    WHERE _PARTITIONTIME >= @start_date AND _PARTITIONTIME <= @end_date
        AND item != ''
),
approx AS (
    SELECT APPROX_TOP_COUNT(entity_name, 20) AS top_items
    FROM unnested
)
SELECT item.value AS name, item.count AS count
FROM approx, UNNEST(top_items) AS item
ORDER BY count DESC
```

Note: `n` (here `20`) is a validated integer literal, not a parameter, because BigQuery requires `APPROX_TOP_COUNT(expr, literal_int)`.

#### 1.6 Acceptance Criteria — Phase 1

- [x] `APPROX_COUNT_DISTINCT`, `STDDEV` added to `AggFunc` — `sources/aggregation.py`
- [x] `meta: QueryMetadata | None` and `sql: str | None` added to `AggregationResult` — `sources/aggregation.py`
- [x] `_render_agg_expr()` updated for new AggFunc values — `sources/bigquery.py`
- [x] 6 typed result models as standalone BaseModels — `analytics/results.py`
- [x] `to_compact()` and `__str__` on each result model
- [x] `TimeGranularity` and `EventMetric` enums with `MetricConfig` NamedTuple — `analytics/types.py`
- [x] `SessionCostTracker` with `record()`, `check_budget()`, `reset()` — `analytics/_cost.py`
- [x] `BudgetExceededError` exception — `exceptions.py`
- [x] 7 SQL builder functions — `analytics/_builders.py`
- [x] Dense date spine in `build_time_series_sql()` when `moving_average_window` is set
- [x] `CORR` handled in `build_trend_sql()` only (NOT in AggFunc)
- [x] `APPROX_TOP_COUNT` n validated and inlined as literal
- [x] `SAFE_DIVIDE` used in trend SQL
- [x] All column names validated against allowlists
- [x] All user values parameterized (except validated literal ints)
- [x] Partition filters in every generated query
- [x] `analytics/__init__.py` re-exports all public types
- [x] Unit tests for: result model serialization, enum values, AggFunc rendering, each SQL builder (structure + params + column validation), cost tracker (budget enforcement, threading, reset)
- [x] `make ci` passes

---

### Phase 2: Endpoint Mixins (Events + GKG)

**Goal**: Wire builders to endpoints via mixins. Fix `GKGEndpoint._fetcher` typing.

#### 2.1 Mixin Typing (Protocol Pattern)

Instead of `type: ignore[assignment]`, mixins use a Protocol for `self`:

```python
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from py_gdelt.sources.fetcher import DataFetcher


@runtime_checkable
class _HasFetcher(Protocol):
    """Protocol for classes that provide a DataFetcher."""
    _fetcher: DataFetcher
```

Mixin methods type `self` as `_HasFetcher`:

```python
class EventsAnalyticsMixin:
    """Analytics methods for the Events table."""

    async def time_series(
        self: _HasFetcher,
        filter_obj: EventFilter,
        *,
        granularity: TimeGranularity = TimeGranularity.DAY,
        metrics: Collection[EventMetric] = (EventMetric.COUNT,),
        moving_average_window: int | None = None,
        limit: int | None = None,
    ) -> TimeSeriesResult:
        ...
```

This passes strict mypy because `EventsEndpoint` satisfies `_HasFetcher` (it has `_fetcher: DataFetcher`).

#### 2.2 BigQuery Guard Helper

Extract repeated BigQuery availability check:

```python
def _require_bigquery(self: _HasFetcher) -> BigQuerySource:
    """Return BigQuerySource or raise ConfigurationError."""
    bq = self._fetcher.bigquery_source
    if bq is None:
        msg = "Analytics queries require BigQuery credentials. Pass bigquery_source to GDELTClient."
        raise ConfigurationError(msg)
    return bq
```

#### 2.3 EventsAnalyticsMixin

New file: `src/py_gdelt/analytics/_events_mixin.py`

Each method follows the pattern:
1. `bq = _require_bigquery(self)` → raise `ConfigurationError` if no BQ
2. Validate parameters
3. Call builder function → `(sql, params)`
4. Check session budget (if tracker configured)
5. Execute via `bq._execute_query_batch()`
6. Record cost in session tracker
7. Wrap rows into typed result model with `meta` and `sql`
8. Return

**Methods** (6 async + 6 sync = 12 total):

| Method | Parameters | Returns |
|--------|-----------|---------|
| `time_series()` | `filter_obj, *, granularity, metrics, moving_average_window, limit` | `TimeSeriesResult` |
| `extremes()` | `filter_obj, *, criterion, most_negative, most_positive` | `ExtremeEventsResult` |
| `compare()` | `filter_obj, *, compare_by, values, metric, granularity` | `ComparisonResult` |
| `trend()` | `filter_obj, *, metric, granularity` | `TrendResult` |
| `dyad_analysis()` | `filter_obj, *, actor_a, actor_b, granularity, metrics` | `DyadResult` |
| `top_n_per_group()` | `filter_obj, *, partition_by, order_by, n, ascending` | `PartitionedTopNResult` |

Sync wrappers: `time_series_sync()`, `extremes_sync()`, etc. — each calls `asyncio.run(self.method(...))`.

#### 2.4 GKGAnalyticsMixin

New file: `src/py_gdelt/analytics/_gkg_mixin.py`

**Methods** (2 async + 2 sync = 4 total):

| Method | Parameters | Returns |
|--------|-----------|---------|
| `aggregate_themes()` | `filter_obj, *, top_n` | `AggregationResult` |
| `approx_top()` | `filter_obj, *, field, n` | `AggregationResult` |

`aggregate_themes()` — thin wrapper around existing `aggregate_gkg()` with predefined UNNEST on THEMES + ORDER BY count DESC + LIMIT.

`approx_top()` — uses `APPROX_TOP_COUNT` builder for high-cardinality fields.

#### 2.5 Fix GKGEndpoint._fetcher Typing

```diff
--- a/src/py_gdelt/endpoints/gkg.py
+++ b/src/py_gdelt/endpoints/gkg.py
@@ -108,7 +108,7 @@
         from py_gdelt.sources.fetcher import DataFetcher

         self._settings = settings
-        self._fetcher: Any = DataFetcher(
+        self._fetcher: DataFetcher = DataFetcher(
```

#### 2.6 Compose Mixins into Endpoints

```diff
--- a/src/py_gdelt/endpoints/events.py
+++ b/src/py_gdelt/endpoints/events.py
@@ -79,7 +79,9 @@
-class EventsEndpoint:
+from py_gdelt.analytics._events_mixin import EventsAnalyticsMixin
+
+class EventsEndpoint(EventsAnalyticsMixin):
```

```diff
--- a/src/py_gdelt/endpoints/gkg.py
+++ b/src/py_gdelt/endpoints/gkg.py
-class GKGEndpoint:
+from py_gdelt.analytics._gkg_mixin import GKGAnalyticsMixin
+
+class GKGEndpoint(GKGAnalyticsMixin):
```

#### 2.7 Parameter Validation Rules

| Parameter | Validation | Error |
|-----------|-----------|-------|
| `granularity` | Must be `TimeGranularity` enum value | `ValueError` |
| `metrics` | Each must be `EventMetric` enum value | `ValueError` |
| `criterion` | Validated against `ALLOWED_COLUMNS["events"]` | `BigQueryError` |
| `compare_by` | Validated against `ALLOWED_COLUMNS["events"]` | `BigQueryError` |
| `values` | 2-10 entries, no duplicates, alphanumeric | `ValueError` |
| `partition_by` | Validated against `ALLOWED_COLUMNS["events"]` | `BigQueryError` |
| `order_by` | Validated against `ALLOWED_COLUMNS["events"]` | `BigQueryError` |
| `most_negative` / `most_positive` | >= 0, sum > 0 | `ValueError` |
| `n` | >= 1 (for approx_top: 1-1000) | `ValueError` |
| `moving_average_window` | >= 2 if set | `ValueError` |
| `actor_a` / `actor_b` | Non-empty string | `ValueError` |

#### 2.8 Empty Result Handling

| Method | No Data Behavior |
|--------|-----------------|
| `time_series()` | Returns `TimeSeriesResult(buckets=[], ...)` |
| `extremes()` | Returns `ExtremeEventsResult(most_negative=[], most_positive=[], ...)` |
| `compare()` | Returns `ComparisonResult(rows=[], ...)` |
| `trend()` | Raises `ValueError("Trend requires at least 2 data points")` |
| `dyad_analysis()` | Returns `DyadResult(a_to_b=[], b_to_a=[], ...)` |
| `top_n_per_group()` | Returns `PartitionedTopNResult(groups={}, ...)` |

#### 2.9 Acceptance Criteria — Phase 2

- [x] `EventsAnalyticsMixin` with 6 async + 6 sync analytics methods — `analytics/_events_mixin.py`
- [x] `GKGAnalyticsMixin` with 2 async + 2 sync methods — `analytics/_gkg_mixin.py`
- [x] Protocol-based mixin typing (no `type: ignore`) — passes strict mypy
- [x] `_require_bigquery()` helper used in all mixin methods
- [x] `EventsEndpoint` composes `EventsAnalyticsMixin` — `endpoints/events.py`
- [x] `GKGEndpoint` composes `GKGAnalyticsMixin` — `endpoints/gkg.py`
- [x] `GKGEndpoint._fetcher` typed as `DataFetcher` (not `Any`) — `endpoints/gkg.py`
- [x] All parameter validation with clear error messages
- [x] Empty result handling (empty containers, not errors, except trend)
- [x] Integration with session cost tracker (check_budget + record)
- [x] All results carry `meta: QueryMetadata` and `sql: str`
- [x] Unit tests for each analytics method (mock BigQuery, verify SQL, verify result wrapping)
- [x] Unit tests for parameter validation edge cases
- [x] Unit tests for empty result handling
- [x] `make ci` passes

---

### Phase 3: Exports, Integration Tests, Documentation

**Goal**: Wire everything together, update public API, verify end-to-end.

#### 3.1 Public API Exports

Modify `src/py_gdelt/__init__.py` to export:
- `TimeSeriesResult`, `ExtremeEventsResult`, `ComparisonResult`, `TrendResult`, `DyadResult`, `PartitionedTopNResult`
- `TimeGranularity`, `EventMetric`
- `SessionCostTracker`
- `BudgetExceededError`

#### 3.2 Integration Tests

New test file: `tests/integration/test_analytics.py`

Mark with `@pytest.mark.integration`, `@pytest.mark.asyncio`, `@pytest.mark.timeout(60)`.
Skip if `GDELT_BIGQUERY_PROJECT` not set.
Use narrow date ranges (yesterday) and `limit` to minimize cost.

Test each analytics method against live BigQuery:
- `time_series()` with day granularity, verify buckets are date-ordered
- `time_series()` with moving average, verify MA columns present and non-null
- `extremes()` with criterion="GoldsteinScale", verify ordering
- `compare()` with 2 countries, verify per-country columns
- `trend()` with enough data points for regression
- `approx_top()` on themes, verify returns top-N
- Cost tracker: verify `cumulative_bytes` increases across queries

#### 3.3 Acceptance Criteria — Phase 3

- [x] All new public types exported from `py_gdelt.__init__`
- [x] Integration tests for all analytics methods against live BigQuery
- [x] Integration tests verify cost tracker accumulates bytes across queries
- [x] `make ci` passes (full suite including integration if BQ configured)

---

## Alternative Approaches Considered

| Approach | Verdict | Reason |
|----------|---------|--------|
| `AnalyticsResult` base class | Dropped (v2) | Adds hierarchy without benefit. Result types are structurally different. Just add `meta`/`sql` to each model. |
| `BigQueryCache` (file-based SQL hash cache) | Dropped (v2) | YAGNI. BigQuery caches results for 24h for free. Add if we measure cache misses. |
| `CORR` in `AggFunc` | Dropped (v2) | `CORR(x,y)` needs two columns; `Aggregation` has one. Dedicated `build_trend_sql()` instead. |
| Fluent Builder (`SQLBuilder`) | Rejected | Analytics SQL patterns too diverse for a generic builder. |
| Separate Analytics Namespace | Rejected | Adds indirection. `aggregate()` already lives on endpoints. |
| Just extend `aggregate()` | Rejected | Dyadic analysis, extremes, trend don't fit GROUP BY. |
| Standalone functions (no mixins) | Rejected | Poor discoverability. Users must import functions and pass `BigQuerySource`. |

## Risk Analysis & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Mixin MRO complexity | Medium | Low | Simple mixin with no `__init__`, Protocol-typed self |
| Test explosion (16 new methods) | Medium | High | Parametrized tests, shared fixtures, test at builder level |
| SQL injection via column names | Critical | Low | All columns validated against `ALLOWED_COLUMNS` frozensets |
| Moving average wrong on gapped data | High | High | Dense date spine via `GENERATE_DATE_ARRAY` + `LEFT JOIN` |
| APPROX_TOP_COUNT n parameterization | Medium | Certain | Validated int, inlined as literal (BQ limitation) |
| STDDEV=0 division in trend | Medium | Medium | `SAFE_DIVIDE` wrapping |
| Thread safety of cost tracker | Low | Low | `threading.Lock` for forward-compat with free-threaded Python |

## References

### Internal
- Brainstorm: `docs/brainstorms/2026-02-08-analytics-layer-brainstorm.md`
- BigQuery refactor plan: `docs/plans/2026-02-06-bigquery-refactor.md`
- Dream features: `docs/py-gdelt-dream-features.md`
- Existing aggregation: `src/py_gdelt/sources/aggregation.py`
- BigQuery source: `src/py_gdelt/sources/bigquery.py`
- Events endpoint: `src/py_gdelt/endpoints/events.py`
- GKG endpoint: `src/py_gdelt/endpoints/gkg.py`
- MCP server: `src/py_gdelt/mcp_server/server.py`
