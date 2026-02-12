"""Tests for Phase 1 analytics layer foundation.

This module tests all Phase 1 analytics components:
- AggFunc extensions (APPROX_COUNT_DISTINCT, STDDEV)
- AggregationResult extensions (meta, sql fields)
- BigQuerySource._render_agg_expr for new functions
- TimeGranularity and EventMetric enums
- MetricConfig and EVENT_METRIC_CONFIG mapping
- Result models (TimeSeriesResult, ExtremeEventsResult, etc.)
- SessionCostTracker budget enforcement
- SQL builder functions for analytics queries
"""

from __future__ import annotations

import concurrent.futures
from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from py_gdelt.analytics._builders import (
    build_comparison_sql,
    build_dyad_sql,
    build_extremes_sql,
    build_gkg_approx_top_sql,
    build_time_series_sql,
    build_top_n_per_group_sql,
    build_trend_sql,
)
from py_gdelt.analytics._cost import SessionCostTracker
from py_gdelt.analytics.results import (
    ComparisonResult,
    DyadResult,
    ExtremeEventsResult,
    PartitionedTopNResult,
    TimeSeriesResult,
    TrendResult,
)
from py_gdelt.analytics.types import (
    EVENT_METRIC_CONFIG,
    EventMetric,
    MetricConfig,
    TimeGranularity,
)
from py_gdelt.exceptions import BigQueryError, BudgetExceededError
from py_gdelt.filters import DateRange, EventFilter, GKGFilter
from py_gdelt.sources.aggregation import AggFunc, Aggregation, AggregationResult
from py_gdelt.sources.bigquery import BigQuerySource
from py_gdelt.sources.metadata import QueryMetadata


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _event_filter() -> EventFilter:
    return EventFilter(date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)))


def _gkg_filter() -> GKGFilter:
    return GKGFilter(date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)))


# ---------------------------------------------------------------------------
# 1. AggFunc extensions
# ---------------------------------------------------------------------------


class TestAggFuncExtensions:
    """Tests for the two new AggFunc members."""

    def test_approx_count_distinct_value(self) -> None:
        assert AggFunc.APPROX_COUNT_DISTINCT == "APPROX_COUNT_DISTINCT"

    def test_stddev_value(self) -> None:
        assert AggFunc.STDDEV == "STDDEV"

    def test_total_member_count(self) -> None:
        assert len(AggFunc) == 8

    def test_aggregation_with_stddev(self) -> None:
        agg = Aggregation(func=AggFunc.STDDEV, column="GoldsteinScale")
        assert agg.func == AggFunc.STDDEV
        assert agg.column == "GoldsteinScale"

    def test_aggregation_with_approx_count_distinct(self) -> None:
        agg = Aggregation(func=AggFunc.APPROX_COUNT_DISTINCT, column="Actor1CountryCode")
        assert agg.func == AggFunc.APPROX_COUNT_DISTINCT
        assert agg.column == "Actor1CountryCode"

    def test_star_rejected_for_approx_count_distinct(self) -> None:
        with pytest.raises(ValidationError, match=r"column='\*' is only valid"):
            Aggregation(func=AggFunc.APPROX_COUNT_DISTINCT, column="*")

    def test_star_rejected_for_stddev(self) -> None:
        with pytest.raises(ValidationError, match=r"column='\*' is only valid"):
            Aggregation(func=AggFunc.STDDEV, column="*")


# ---------------------------------------------------------------------------
# 2. AggregationResult extensions
# ---------------------------------------------------------------------------


class TestAggregationResultExtensions:
    """Tests for meta and sql fields on AggregationResult."""

    def test_meta_defaults_to_none(self) -> None:
        result = AggregationResult(rows=[], group_by=[], total_rows=0)
        assert result.meta is None

    def test_sql_defaults_to_none(self) -> None:
        result = AggregationResult(rows=[], group_by=[], total_rows=0)
        assert result.sql is None

    def test_meta_can_be_set(self) -> None:
        meta = QueryMetadata(bytes_processed=1024, cache_hit=True)
        result = AggregationResult(rows=[], group_by=[], total_rows=0, meta=meta)
        assert result.meta is not None
        assert result.meta.bytes_processed == 1024
        assert result.meta.cache_hit is True

    def test_sql_can_be_set(self) -> None:
        result = AggregationResult(rows=[], group_by=[], total_rows=0, sql="SELECT COUNT(*) FROM t")
        assert result.sql == "SELECT COUNT(*) FROM t"


# ---------------------------------------------------------------------------
# 3. _render_agg_expr
# ---------------------------------------------------------------------------


class TestRenderAggExpr:
    """Tests for BigQuerySource._render_agg_expr with new functions."""

    def test_approx_count_distinct_rendering(self) -> None:
        agg = Aggregation(func=AggFunc.APPROX_COUNT_DISTINCT, column="Actor1CountryCode")
        result = BigQuerySource._render_agg_expr(agg)
        assert result == "APPROX_COUNT_DISTINCT(Actor1CountryCode)"

    def test_stddev_rendering(self) -> None:
        agg = Aggregation(func=AggFunc.STDDEV, column="GoldsteinScale")
        result = BigQuerySource._render_agg_expr(agg)
        assert result == "STDDEV(GoldsteinScale)"


# ---------------------------------------------------------------------------
# 4. TimeGranularity
# ---------------------------------------------------------------------------


class TestTimeGranularity:
    """Tests for the TimeGranularity enum."""

    def test_day_value(self) -> None:
        assert TimeGranularity.DAY == "DAY"

    def test_week_value(self) -> None:
        assert TimeGranularity.WEEK == "WEEK"

    def test_month_value(self) -> None:
        assert TimeGranularity.MONTH == "MONTH"

    def test_quarter_value(self) -> None:
        assert TimeGranularity.QUARTER == "QUARTER"

    def test_year_value(self) -> None:
        assert TimeGranularity.YEAR == "YEAR"

    def test_member_count(self) -> None:
        assert len(TimeGranularity) == 5


# ---------------------------------------------------------------------------
# 5. EventMetric
# ---------------------------------------------------------------------------


class TestEventMetric:
    """Tests for the EventMetric enum."""

    def test_count(self) -> None:
        assert EventMetric.COUNT == "count"

    def test_avg_goldstein(self) -> None:
        assert EventMetric.AVG_GOLDSTEIN == "avg_goldstein"

    def test_avg_tone(self) -> None:
        assert EventMetric.AVG_TONE == "avg_tone"

    def test_avg_num_mentions(self) -> None:
        assert EventMetric.AVG_NUM_MENTIONS == "avg_num_mentions"

    def test_avg_num_sources(self) -> None:
        assert EventMetric.AVG_NUM_SOURCES == "avg_num_sources"

    def test_avg_num_articles(self) -> None:
        assert EventMetric.AVG_NUM_ARTICLES == "avg_num_articles"

    def test_stddev_goldstein(self) -> None:
        assert EventMetric.STDDEV_GOLDSTEIN == "stddev_goldstein"

    def test_member_count(self) -> None:
        assert len(EventMetric) == 7


# ---------------------------------------------------------------------------
# 6. MetricConfig / EVENT_METRIC_CONFIG
# ---------------------------------------------------------------------------


class TestMetricConfig:
    """Tests for EVENT_METRIC_CONFIG completeness and correctness."""

    def test_every_metric_has_config(self) -> None:
        for metric in EventMetric:
            assert metric in EVENT_METRIC_CONFIG, f"Missing config for {metric}"

    def test_count_config(self) -> None:
        cfg = EVENT_METRIC_CONFIG[EventMetric.COUNT]
        assert cfg == MetricConfig("COUNT", "*")

    def test_avg_goldstein_config(self) -> None:
        cfg = EVENT_METRIC_CONFIG[EventMetric.AVG_GOLDSTEIN]
        assert cfg == MetricConfig("AVG", "GoldsteinScale")

    def test_avg_tone_config(self) -> None:
        cfg = EVENT_METRIC_CONFIG[EventMetric.AVG_TONE]
        assert cfg == MetricConfig("AVG", "AvgTone")

    def test_avg_num_mentions_config(self) -> None:
        cfg = EVENT_METRIC_CONFIG[EventMetric.AVG_NUM_MENTIONS]
        assert cfg == MetricConfig("AVG", "NumMentions")

    def test_avg_num_sources_config(self) -> None:
        cfg = EVENT_METRIC_CONFIG[EventMetric.AVG_NUM_SOURCES]
        assert cfg == MetricConfig("AVG", "NumSources")

    def test_avg_num_articles_config(self) -> None:
        cfg = EVENT_METRIC_CONFIG[EventMetric.AVG_NUM_ARTICLES]
        assert cfg == MetricConfig("AVG", "NumArticles")

    def test_stddev_goldstein_config(self) -> None:
        cfg = EVENT_METRIC_CONFIG[EventMetric.STDDEV_GOLDSTEIN]
        assert cfg == MetricConfig("STDDEV", "GoldsteinScale")

    def test_config_count_matches_enum(self) -> None:
        assert len(EVENT_METRIC_CONFIG) == len(EventMetric)


# ---------------------------------------------------------------------------
# 7. Result models
# ---------------------------------------------------------------------------


class TestTimeSeriesResult:
    """Tests for TimeSeriesResult model."""

    def test_minimal_construction(self) -> None:
        result = TimeSeriesResult(
            buckets=[{"bucket": "2024-01-01", "count": 10}],
            granularity="DAY",
            metrics=["count"],
        )
        assert len(result.buckets) == 1
        assert result.granularity == "DAY"
        assert result.metrics == ["count"]

    def test_to_compact_returns_string(self) -> None:
        result = TimeSeriesResult(
            buckets=[{"bucket": "2024-01-01"}],
            granularity="DAY",
            metrics=["count"],
        )
        compact = result.to_compact()
        assert isinstance(compact, str)
        assert "1 buckets" in compact
        assert "DAY" in compact

    def test_str_delegates_to_compact(self) -> None:
        result = TimeSeriesResult(buckets=[], granularity="WEEK", metrics=["avg_goldstein"])
        assert str(result) == result.to_compact()

    def test_meta_defaults_to_none(self) -> None:
        result = TimeSeriesResult(buckets=[], granularity="DAY", metrics=[])
        assert result.meta is None

    def test_sql_defaults_to_none(self) -> None:
        result = TimeSeriesResult(buckets=[], granularity="DAY", metrics=[])
        assert result.sql is None


class TestExtremeEventsResult:
    """Tests for ExtremeEventsResult model."""

    def test_minimal_construction(self) -> None:
        result = ExtremeEventsResult(
            most_negative=[{"GoldsteinScale": -10}],
            most_positive=[{"GoldsteinScale": 10}],
            criterion="GoldsteinScale",
            requested_negative=1,
            requested_positive=1,
        )
        assert len(result.most_negative) == 1
        assert len(result.most_positive) == 1

    def test_to_compact_returns_string(self) -> None:
        result = ExtremeEventsResult(
            most_negative=[],
            most_positive=[{"GoldsteinScale": 5}],
            criterion="GoldsteinScale",
            requested_negative=5,
            requested_positive=5,
        )
        compact = result.to_compact()
        assert isinstance(compact, str)
        assert "GoldsteinScale" in compact

    def test_str_delegates_to_compact(self) -> None:
        result = ExtremeEventsResult(
            most_negative=[],
            most_positive=[],
            criterion="AvgTone",
            requested_negative=3,
            requested_positive=3,
        )
        assert str(result) == result.to_compact()

    def test_meta_defaults_to_none(self) -> None:
        result = ExtremeEventsResult(
            most_negative=[],
            most_positive=[],
            criterion="X",
            requested_negative=0,
            requested_positive=0,
        )
        assert result.meta is None

    def test_sql_defaults_to_none(self) -> None:
        result = ExtremeEventsResult(
            most_negative=[],
            most_positive=[],
            criterion="X",
            requested_negative=0,
            requested_positive=0,
        )
        assert result.sql is None


class TestComparisonResult:
    """Tests for ComparisonResult model."""

    def test_minimal_construction(self) -> None:
        result = ComparisonResult(
            rows=[{"bucket": "2024-01-01", "US_count": 5}],
            compare_by="Actor1CountryCode",
            values=["US", "CH"],
            metric="count",
            granularity="DAY",
        )
        assert result.compare_by == "Actor1CountryCode"
        assert result.values == ["US", "CH"]

    def test_to_compact_returns_string(self) -> None:
        result = ComparisonResult(
            rows=[],
            compare_by="Actor1CountryCode",
            values=["US"],
            metric="count",
            granularity="DAY",
        )
        compact = result.to_compact()
        assert isinstance(compact, str)
        assert "US" in compact

    def test_str_delegates_to_compact(self) -> None:
        result = ComparisonResult(
            rows=[],
            compare_by="X",
            values=["A"],
            metric="m",
            granularity="DAY",
        )
        assert str(result) == result.to_compact()

    def test_meta_defaults_to_none(self) -> None:
        result = ComparisonResult(
            rows=[],
            compare_by="X",
            values=[],
            metric="m",
            granularity="DAY",
        )
        assert result.meta is None

    def test_sql_defaults_to_none(self) -> None:
        result = ComparisonResult(
            rows=[],
            compare_by="X",
            values=[],
            metric="m",
            granularity="DAY",
        )
        assert result.sql is None


class TestTrendResult:
    """Tests for TrendResult model."""

    def test_minimal_construction(self) -> None:
        result = TrendResult(slope=0.5, r_squared=0.8, direction="escalating")
        assert result.slope == 0.5
        assert result.r_squared == 0.8
        assert result.direction == "escalating"

    def test_to_compact_returns_string(self) -> None:
        result = TrendResult(slope=0.1, r_squared=0.5, direction="stable", data_points=30)
        compact = result.to_compact()
        assert isinstance(compact, str)
        assert "stable" in compact

    def test_str_delegates_to_compact(self) -> None:
        result = TrendResult(slope=0.0, r_squared=0.0, direction="stable")
        assert str(result) == result.to_compact()

    def test_meta_defaults_to_none(self) -> None:
        result = TrendResult(slope=0.0, r_squared=0.0, direction="stable")
        assert result.meta is None

    def test_sql_defaults_to_none(self) -> None:
        result = TrendResult(slope=0.0, r_squared=0.0, direction="stable")
        assert result.sql is None


class TestDyadResult:
    """Tests for DyadResult model."""

    def test_minimal_construction(self) -> None:
        result = DyadResult(
            a_to_b=[{"bucket": "2024-01-01", "count": 5}],
            b_to_a=[{"bucket": "2024-01-01", "count": 3}],
            actor_a="US",
            actor_b="CH",
            granularity="DAY",
            metrics=["count"],
        )
        assert result.actor_a == "US"
        assert result.actor_b == "CH"

    def test_to_compact_returns_string(self) -> None:
        result = DyadResult(
            a_to_b=[{"bucket": "2024-01-01"}],
            b_to_a=[],
            actor_a="US",
            actor_b="RS",
            granularity="DAY",
            metrics=["count"],
        )
        compact = result.to_compact()
        assert isinstance(compact, str)
        assert "US" in compact
        assert "RS" in compact

    def test_str_delegates_to_compact(self) -> None:
        result = DyadResult(
            a_to_b=[],
            b_to_a=[],
            actor_a="A",
            actor_b="B",
            granularity="DAY",
            metrics=[],
        )
        assert str(result) == result.to_compact()

    def test_meta_defaults_to_none(self) -> None:
        result = DyadResult(
            a_to_b=[],
            b_to_a=[],
            actor_a="A",
            actor_b="B",
            granularity="DAY",
            metrics=[],
        )
        assert result.meta is None

    def test_sql_defaults_to_none(self) -> None:
        result = DyadResult(
            a_to_b=[],
            b_to_a=[],
            actor_a="A",
            actor_b="B",
            granularity="DAY",
            metrics=[],
        )
        assert result.sql is None


class TestPartitionedTopNResult:
    """Tests for PartitionedTopNResult model."""

    def test_minimal_construction(self) -> None:
        result = PartitionedTopNResult(
            groups={"US": [{"GoldsteinScale": 5}]},
            partition_by="Actor1CountryCode",
            order_by="GoldsteinScale",
            n=10,
        )
        assert result.n == 10
        assert "US" in result.groups

    def test_to_compact_returns_string(self) -> None:
        result = PartitionedTopNResult(
            groups={"US": [], "CH": []},
            partition_by="Actor1CountryCode",
            order_by="GoldsteinScale",
            n=5,
        )
        compact = result.to_compact()
        assert isinstance(compact, str)
        assert "2 groups" in compact

    def test_str_delegates_to_compact(self) -> None:
        result = PartitionedTopNResult(
            groups={},
            partition_by="X",
            order_by="Y",
            n=1,
        )
        assert str(result) == result.to_compact()

    def test_meta_defaults_to_none(self) -> None:
        result = PartitionedTopNResult(
            groups={},
            partition_by="X",
            order_by="Y",
            n=1,
        )
        assert result.meta is None

    def test_sql_defaults_to_none(self) -> None:
        result = PartitionedTopNResult(
            groups={},
            partition_by="X",
            order_by="Y",
            n=1,
        )
        assert result.sql is None


# ---------------------------------------------------------------------------
# 8. SessionCostTracker
# ---------------------------------------------------------------------------


class TestSessionCostTracker:
    """Tests for SessionCostTracker budget enforcement."""

    def test_initial_state(self) -> None:
        tracker = SessionCostTracker(budget_bytes=1_000_000)
        assert tracker.cumulative_bytes == 0
        assert tracker.query_count == 0
        assert tracker.remaining_bytes == 1_000_000

    def test_record_accumulates_bytes(self) -> None:
        tracker = SessionCostTracker(budget_bytes=1_000_000)
        tracker.record(100_000)
        assert tracker.cumulative_bytes == 100_000
        assert tracker.query_count == 1

        tracker.record(200_000)
        assert tracker.cumulative_bytes == 300_000
        assert tracker.query_count == 2

    def test_remaining_bytes_decreases(self) -> None:
        tracker = SessionCostTracker(budget_bytes=500_000)
        tracker.record(100_000)
        assert tracker.remaining_bytes == 400_000

    def test_check_budget_allows_under_budget(self) -> None:
        tracker = SessionCostTracker(budget_bytes=1_000_000)
        tracker.record(500_000)
        # Should not raise
        tracker.check_budget(400_000)

    def test_check_budget_raises_for_over_budget(self) -> None:
        tracker = SessionCostTracker(budget_bytes=1_000_000)
        tracker.record(800_000)
        with pytest.raises(BudgetExceededError):
            tracker.check_budget(300_000)

    def test_record_raises_when_exceeding_budget(self) -> None:
        tracker = SessionCostTracker(budget_bytes=100)
        with pytest.raises(BudgetExceededError):
            tracker.record(200)

    def test_reset(self) -> None:
        tracker = SessionCostTracker(budget_bytes=1_000_000)
        tracker.record(500_000)
        tracker.reset()
        assert tracker.cumulative_bytes == 0
        assert tracker.query_count == 0

    def test_no_budget_no_limits(self) -> None:
        tracker = SessionCostTracker(budget_bytes=None)
        assert tracker.remaining_bytes is None
        # Should not raise even for large amounts
        tracker.record(10**15)
        tracker.check_budget(10**15)
        assert tracker.cumulative_bytes == 10**15

    def test_thread_safety_concurrent_records(self) -> None:
        tracker = SessionCostTracker(budget_bytes=None)
        num_threads = 50
        bytes_per_record = 1000

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(tracker.record, bytes_per_record) for _ in range(num_threads)
            ]
            concurrent.futures.wait(futures)
            # Check no exceptions
            for f in futures:
                f.result()

        assert tracker.cumulative_bytes == num_threads * bytes_per_record
        assert tracker.query_count == num_threads


# ---------------------------------------------------------------------------
# 9. SQL Builders
# ---------------------------------------------------------------------------


def _assert_sql_tuple(result: tuple[str, list[Any]]) -> tuple[str, list[Any]]:
    """Validate that builder returns a 2-tuple of (str, list) and return it."""
    assert isinstance(result, tuple)
    assert len(result) == 2
    sql, params = result
    assert isinstance(sql, str)
    assert isinstance(params, list)
    return sql, params


class TestBuildTimeSeriesSql:
    """Tests for build_time_series_sql builder."""

    def test_returns_tuple(self) -> None:
        _assert_sql_tuple(build_time_series_sql(_event_filter()))

    def test_simple_has_group_by(self) -> None:
        sql, _ = build_time_series_sql(_event_filter())
        assert "GROUP BY" in sql

    def test_simple_no_generate_date_array(self) -> None:
        sql, _ = build_time_series_sql(_event_filter())
        assert "GENERATE_DATE_ARRAY" not in sql

    def test_has_events_table(self) -> None:
        sql, _ = build_time_series_sql(_event_filter())
        assert "events_partitioned" in sql

    def test_params_non_empty(self) -> None:
        _, params = build_time_series_sql(_event_filter())
        assert len(params) > 0

    def test_params_contain_dates(self) -> None:
        _, params = build_time_series_sql(_event_filter())
        param_names = [p.name for p in params]
        assert "start_date" in param_names
        assert "end_date" in param_names

    def test_with_moving_average(self) -> None:
        sql, _ = build_time_series_sql(_event_filter(), moving_average_window=7)
        assert "GENERATE_DATE_ARRAY" in sql
        assert "date_spine" in sql or "spine" in sql
        assert "LEFT JOIN" in sql
        assert "_ma7" in sql

    def test_with_limit(self) -> None:
        sql, _ = build_time_series_sql(_event_filter(), limit=100)
        assert "LIMIT 100" in sql

    def test_with_multiple_metrics(self) -> None:
        sql, _ = build_time_series_sql(
            _event_filter(),
            metrics=(EventMetric.COUNT, EventMetric.AVG_GOLDSTEIN, EventMetric.AVG_TONE),
        )
        assert "count" in sql
        assert "avg_goldstein" in sql or "GoldsteinScale" in sql
        assert "avg_tone" in sql or "AvgTone" in sql

    def test_select_and_from_keywords(self) -> None:
        sql, _ = build_time_series_sql(_event_filter())
        assert "SELECT" in sql
        assert "FROM" in sql
        assert "WHERE" in sql


class TestBuildExtremesSql:
    """Tests for build_extremes_sql builder."""

    def test_returns_tuple(self) -> None:
        _assert_sql_tuple(build_extremes_sql(_event_filter()))

    def test_has_row_number(self) -> None:
        sql, _ = build_extremes_sql(_event_filter())
        assert "ROW_NUMBER" in sql

    def test_has_rank_aliases(self) -> None:
        sql, _ = build_extremes_sql(_event_filter())
        assert "_rank_asc" in sql
        assert "_rank_desc" in sql

    def test_invalid_criterion_raises(self) -> None:
        with pytest.raises(BigQueryError):
            build_extremes_sql(_event_filter(), criterion="INVALID_COLUMN_xyz")

    def test_params_include_extremes_counts(self) -> None:
        _, params = build_extremes_sql(_event_filter(), most_negative=5, most_positive=3)
        param_names = [p.name for p in params]
        assert "most_negative" in param_names
        assert "most_positive" in param_names

    def test_has_events_table(self) -> None:
        sql, _ = build_extremes_sql(_event_filter())
        assert "events_partitioned" in sql

    def test_params_contain_dates(self) -> None:
        _, params = build_extremes_sql(_event_filter())
        param_names = [p.name for p in params]
        assert "start_date" in param_names
        assert "end_date" in param_names


class TestBuildComparisonSql:
    """Tests for build_comparison_sql builder."""

    def test_returns_tuple(self) -> None:
        _assert_sql_tuple(
            build_comparison_sql(
                _event_filter(),
                compare_by="Actor1CountryCode",
                values=["US", "CH"],
            )
        )

    def test_has_case_when(self) -> None:
        sql, _ = build_comparison_sql(
            _event_filter(),
            compare_by="Actor1CountryCode",
            values=["US"],
        )
        assert "CASE WHEN" in sql

    def test_has_in_unnest(self) -> None:
        sql, _ = build_comparison_sql(
            _event_filter(),
            compare_by="Actor1CountryCode",
            values=["US"],
        )
        assert "IN UNNEST" in sql

    def test_per_value_columns(self) -> None:
        sql, _ = build_comparison_sql(
            _event_filter(),
            compare_by="Actor1CountryCode",
            values=["US", "CH"],
        )
        assert "US_count" in sql
        assert "CH_count" in sql

    def test_invalid_compare_by_raises(self) -> None:
        with pytest.raises(BigQueryError):
            build_comparison_sql(
                _event_filter(),
                compare_by="BOGUS_COLUMN",
                values=["US"],
            )

    def test_has_events_table(self) -> None:
        sql, _ = build_comparison_sql(
            _event_filter(),
            compare_by="Actor1CountryCode",
            values=["US"],
        )
        assert "events_partitioned" in sql

    def test_params_contain_dates(self) -> None:
        _, params = build_comparison_sql(
            _event_filter(),
            compare_by="Actor1CountryCode",
            values=["US"],
        )
        param_names = [p.name for p in params]
        assert "start_date" in param_names
        assert "end_date" in param_names

    def test_duplicate_alias_raises(self) -> None:
        """Values that sanitize to the same alias must raise BigQueryError."""
        with pytest.raises(BigQueryError, match="duplicate column alias"):
            build_comparison_sql(
                _event_filter(),
                compare_by="Actor1CountryCode",
                values=["US-A", "US.A"],
            )

    def test_distinct_aliases_accepted(self) -> None:
        """Values with distinct sanitized aliases should succeed."""
        sql, _ = build_comparison_sql(
            _event_filter(),
            compare_by="Actor1CountryCode",
            values=["US", "CH"],
        )
        assert "US_count" in sql
        assert "CH_count" in sql


class TestBuildTrendSql:
    """Tests for build_trend_sql builder."""

    def test_returns_tuple(self) -> None:
        _assert_sql_tuple(build_trend_sql(_event_filter()))

    def test_has_corr(self) -> None:
        sql, _ = build_trend_sql(_event_filter())
        assert "CORR" in sql

    def test_has_stddev(self) -> None:
        sql, _ = build_trend_sql(_event_filter())
        assert "STDDEV" in sql

    def test_has_safe_divide(self) -> None:
        sql, _ = build_trend_sql(_event_filter())
        assert "SAFE_DIVIDE" in sql

    def test_has_power(self) -> None:
        sql, _ = build_trend_sql(_event_filter())
        assert "POWER" in sql

    def test_has_metric_value_alias(self) -> None:
        sql, _ = build_trend_sql(_event_filter())
        assert "metric_value" in sql

    def test_has_events_table(self) -> None:
        sql, _ = build_trend_sql(_event_filter())
        assert "events_partitioned" in sql

    def test_params_contain_dates(self) -> None:
        _, params = build_trend_sql(_event_filter())
        param_names = [p.name for p in params]
        assert "start_date" in param_names
        assert "end_date" in param_names


class TestBuildDyadSql:
    """Tests for build_dyad_sql builder."""

    def test_returns_tuple(self) -> None:
        _assert_sql_tuple(build_dyad_sql(_event_filter(), actor_a="US", actor_b="RS"))

    def test_has_actor_columns(self) -> None:
        sql, _ = build_dyad_sql(_event_filter(), actor_a="US", actor_b="RS")
        assert "Actor1CountryCode" in sql
        assert "Actor2CountryCode" in sql

    def test_params_include_actors(self) -> None:
        _, params = build_dyad_sql(_event_filter(), actor_a="US", actor_b="RS")
        param_names = [p.name for p in params]
        assert "actor_a" in param_names
        assert "actor_b" in param_names

    def test_has_events_table(self) -> None:
        sql, _ = build_dyad_sql(_event_filter(), actor_a="US", actor_b="RS")
        assert "events_partitioned" in sql

    def test_params_contain_dates(self) -> None:
        _, params = build_dyad_sql(_event_filter(), actor_a="US", actor_b="RS")
        param_names = [p.name for p in params]
        assert "start_date" in param_names
        assert "end_date" in param_names


class TestBuildTopNPerGroupSql:
    """Tests for build_top_n_per_group_sql builder."""

    def test_returns_tuple(self) -> None:
        _assert_sql_tuple(
            build_top_n_per_group_sql(
                _event_filter(),
                partition_by="Actor1CountryCode",
                order_by="GoldsteinScale",
            )
        )

    def test_has_qualify(self) -> None:
        sql, _ = build_top_n_per_group_sql(
            _event_filter(),
            partition_by="Actor1CountryCode",
            order_by="GoldsteinScale",
        )
        assert "QUALIFY" in sql

    def test_has_row_number(self) -> None:
        sql, _ = build_top_n_per_group_sql(
            _event_filter(),
            partition_by="Actor1CountryCode",
            order_by="GoldsteinScale",
        )
        assert "ROW_NUMBER" in sql

    def test_has_partition_by(self) -> None:
        sql, _ = build_top_n_per_group_sql(
            _event_filter(),
            partition_by="Actor1CountryCode",
            order_by="GoldsteinScale",
        )
        assert "PARTITION BY" in sql

    def test_invalid_partition_by_raises(self) -> None:
        with pytest.raises(BigQueryError):
            build_top_n_per_group_sql(
                _event_filter(),
                partition_by="NOT_A_COLUMN",
                order_by="GoldsteinScale",
            )

    def test_ascending_true_uses_asc(self) -> None:
        sql, _ = build_top_n_per_group_sql(
            _event_filter(),
            partition_by="Actor1CountryCode",
            order_by="GoldsteinScale",
            ascending=True,
        )
        assert "ASC" in sql

    def test_ascending_false_uses_desc(self) -> None:
        sql, _ = build_top_n_per_group_sql(
            _event_filter(),
            partition_by="Actor1CountryCode",
            order_by="GoldsteinScale",
            ascending=False,
        )
        assert "DESC" in sql

    def test_has_events_table(self) -> None:
        sql, _ = build_top_n_per_group_sql(
            _event_filter(),
            partition_by="Actor1CountryCode",
            order_by="GoldsteinScale",
        )
        assert "events_partitioned" in sql

    def test_params_contain_dates(self) -> None:
        _, params = build_top_n_per_group_sql(
            _event_filter(),
            partition_by="Actor1CountryCode",
            order_by="GoldsteinScale",
        )
        param_names = [p.name for p in params]
        assert "start_date" in param_names
        assert "end_date" in param_names


class TestBuildGkgApproxTopSql:
    """Tests for build_gkg_approx_top_sql builder."""

    def test_returns_tuple(self) -> None:
        _assert_sql_tuple(build_gkg_approx_top_sql(_gkg_filter()))

    def test_has_approx_top_count(self) -> None:
        sql, _ = build_gkg_approx_top_sql(_gkg_filter())
        assert "APPROX_TOP_COUNT" in sql

    def test_n_is_inlined_as_literal(self) -> None:
        sql, _ = build_gkg_approx_top_sql(_gkg_filter(), n=42)
        # The exact integer 42 must appear in the SQL, not as a parameter
        assert "42" in sql

    def test_n_zero_raises(self) -> None:
        with pytest.raises(BigQueryError):
            build_gkg_approx_top_sql(_gkg_filter(), n=0)

    def test_n_1001_raises(self) -> None:
        with pytest.raises(BigQueryError):
            build_gkg_approx_top_sql(_gkg_filter(), n=1001)

    def test_uses_gkg_table(self) -> None:
        sql, _ = build_gkg_approx_top_sql(_gkg_filter())
        assert "gkg_partitioned" in sql

    def test_params_contain_dates(self) -> None:
        _, params = build_gkg_approx_top_sql(_gkg_filter())
        param_names = [p.name for p in params]
        assert "start_date" in param_names
        assert "end_date" in param_names

    def test_params_non_empty(self) -> None:
        _, params = build_gkg_approx_top_sql(_gkg_filter())
        assert len(params) > 0

    def test_has_select_from_where(self) -> None:
        sql, _ = build_gkg_approx_top_sql(_gkg_filter())
        assert "SELECT" in sql
        assert "FROM" in sql
        assert "WHERE" in sql
