"""Unit tests for EventsAnalyticsMixin and GKGAnalyticsMixin.

Tests the analytics mixin methods composed into EventsEndpoint and GKGEndpoint
by mocking the BigQuerySource to return canned rows.
"""

from __future__ import annotations

from datetime import date
from typing import Any
from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from py_gdelt.analytics.results import (
    ComparisonResult,
    DyadResult,
    ExtremeEventsResult,
    PartitionedTopNResult,
    TimeSeriesResult,
    TrendResult,
)
from py_gdelt.analytics.types import EventMetric, TimeGranularity
from py_gdelt.endpoints.events import EventsEndpoint
from py_gdelt.endpoints.gkg import GKGEndpoint
from py_gdelt.exceptions import ConfigurationError
from py_gdelt.filters import DateRange, EventFilter, GKGFilter
from py_gdelt.sources.aggregation import AggregationResult, GKGUnnestField
from py_gdelt.sources.metadata import QueryMetadata


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _event_filter() -> EventFilter:
    """Create a standard EventFilter for testing."""
    return EventFilter(date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)))


def _gkg_filter() -> GKGFilter:
    """Create a standard GKGFilter for testing."""
    return GKGFilter(date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)))


def _mock_metadata() -> QueryMetadata:
    """Create mock query metadata."""
    return QueryMetadata(bytes_processed=1000, bytes_billed=2000, cache_hit=False)


def _make_events_endpoint(
    bq_rows: list[dict[str, Any]],
    metadata: QueryMetadata | None = None,
) -> EventsEndpoint:
    """Create an EventsEndpoint with a mocked BigQuery source.

    Args:
        bq_rows: Canned rows to return from _execute_query_batch.
        metadata: Optional query metadata to return.

    Returns:
        EventsEndpoint with mocked BigQuery source.
    """
    mock_bq = MagicMock()
    mock_bq._execute_query_batch = AsyncMock(return_value=(bq_rows, 1000))
    type(mock_bq).last_query_metadata = PropertyMock(return_value=metadata or _mock_metadata())

    mock_file_source = MagicMock()

    endpoint = EventsEndpoint(
        file_source=mock_file_source,
        bigquery_source=mock_bq,
    )
    return endpoint


def _make_gkg_endpoint(
    bq_rows: list[dict[str, Any]] | None = None,
    metadata: QueryMetadata | None = None,
    agg_result: AggregationResult | None = None,
) -> GKGEndpoint:
    """Create a GKGEndpoint with a mocked BigQuery source.

    Args:
        bq_rows: Optional canned rows for _execute_query_batch.
        metadata: Optional query metadata to return.
        agg_result: Optional AggregationResult to return from aggregate_gkg.

    Returns:
        GKGEndpoint with mocked BigQuery source.
    """
    mock_bq = MagicMock()
    if bq_rows is not None:
        mock_bq._execute_query_batch = AsyncMock(return_value=(bq_rows, 1000))
    if agg_result is not None:
        mock_bq.aggregate_gkg = AsyncMock(return_value=agg_result)
    type(mock_bq).last_query_metadata = PropertyMock(return_value=metadata or _mock_metadata())

    mock_file_source = MagicMock()

    endpoint = GKGEndpoint(
        file_source=mock_file_source,
        bigquery_source=mock_bq,
    )
    return endpoint


# ---------------------------------------------------------------------------
# Events: time_series
# ---------------------------------------------------------------------------


class TestEventsTimeSeries:
    """Tests for EventsAnalyticsMixin.time_series()."""

    @pytest.mark.asyncio
    async def test_time_series_basic(self) -> None:
        """Verify basic time_series returns correct result shape."""
        rows = [
            {"bucket": date(2024, 1, 1), "count": 100},
            {"bucket": date(2024, 1, 2), "count": 150},
        ]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.time_series(_event_filter())

        assert isinstance(result, TimeSeriesResult)
        assert len(result.buckets) == 2
        assert result.granularity == "DAY"
        assert result.metrics == ["count"]
        assert result.moving_average_window is None
        assert result.meta is not None
        assert result.sql is not None

    @pytest.mark.asyncio
    async def test_time_series_with_moving_average(self) -> None:
        """Verify moving_average_window is passed through to result."""
        rows = [
            {"bucket": date(2024, 1, 1), "count": 100, "count_ma7": 95.0},
        ]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.time_series(_event_filter(), moving_average_window=7)

        assert result.moving_average_window == 7

    @pytest.mark.asyncio
    async def test_time_series_serializes_dates(self) -> None:
        """Verify date objects in rows are converted to ISO strings."""
        rows = [{"bucket": date(2024, 1, 1), "count": 100}]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.time_series(_event_filter())

        assert result.buckets[0]["bucket"] == "2024-01-01"

    @pytest.mark.asyncio
    async def test_time_series_empty_result(self) -> None:
        """Verify empty rows return empty buckets."""
        endpoint = _make_events_endpoint([])
        result = await endpoint.time_series(_event_filter())

        assert result.buckets == []

    @pytest.mark.asyncio
    async def test_time_series_with_multiple_metrics(self) -> None:
        """Verify multiple metrics are reflected in the result."""
        rows = [
            {"bucket": date(2024, 1, 1), "count": 100, "avg_goldstein": 2.5},
        ]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.time_series(
            _event_filter(),
            metrics=(EventMetric.COUNT, EventMetric.AVG_GOLDSTEIN),
        )

        assert result.metrics == ["count", "avg_goldstein"]

    @pytest.mark.asyncio
    async def test_time_series_with_custom_granularity(self) -> None:
        """Verify custom granularity is passed through."""
        rows = [{"bucket": date(2024, 1, 1), "count": 500}]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.time_series(_event_filter(), granularity=TimeGranularity.WEEK)

        assert result.granularity == "WEEK"

    @pytest.mark.asyncio
    async def test_time_series_moving_average_window_zero_raises(self) -> None:
        """Verify moving_average_window=0 raises ValueError."""
        endpoint = _make_events_endpoint([])
        with pytest.raises(ValueError, match="moving_average_window must be >= 2"):
            await endpoint.time_series(_event_filter(), moving_average_window=0)

    @pytest.mark.asyncio
    async def test_time_series_moving_average_window_one_raises(self) -> None:
        """Verify moving_average_window=1 raises ValueError."""
        endpoint = _make_events_endpoint([])
        with pytest.raises(ValueError, match="moving_average_window must be >= 2"):
            await endpoint.time_series(_event_filter(), moving_average_window=1)

    @pytest.mark.asyncio
    async def test_time_series_moving_average_window_negative_raises(self) -> None:
        """Verify negative moving_average_window raises ValueError."""
        endpoint = _make_events_endpoint([])
        with pytest.raises(ValueError, match="moving_average_window must be >= 2"):
            await endpoint.time_series(_event_filter(), moving_average_window=-5)

    @pytest.mark.asyncio
    async def test_time_series_moving_average_window_two_accepted(self) -> None:
        """Verify moving_average_window=2 is the minimum accepted value."""
        rows = [
            {"bucket": date(2024, 1, 1), "count": 100, "count_ma2": 100.0},
        ]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.time_series(_event_filter(), moving_average_window=2)

        assert result.moving_average_window == 2


# ---------------------------------------------------------------------------
# Events: extremes
# ---------------------------------------------------------------------------


class TestEventsExtremes:
    """Tests for EventsAnalyticsMixin.extremes()."""

    @pytest.mark.asyncio
    async def test_extremes_basic(self) -> None:
        """Verify extremes splits rows by _extreme_type and strips the marker."""
        rows = [
            {"GoldsteinScale": -10.0, "EventCode": "190", "_extreme_type": "negative"},
            {"GoldsteinScale": -8.0, "EventCode": "180", "_extreme_type": "negative"},
            {"GoldsteinScale": 8.0, "EventCode": "040", "_extreme_type": "positive"},
            {"GoldsteinScale": 10.0, "EventCode": "050", "_extreme_type": "positive"},
        ]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.extremes(_event_filter())

        assert isinstance(result, ExtremeEventsResult)
        assert len(result.most_negative) == 2
        assert len(result.most_positive) == 2
        assert "_extreme_type" not in result.most_negative[0]
        assert "_extreme_type" not in result.most_positive[0]

    @pytest.mark.asyncio
    async def test_extremes_empty(self) -> None:
        """Verify empty rows produce empty result lists."""
        endpoint = _make_events_endpoint([])
        result = await endpoint.extremes(_event_filter())

        assert result.most_negative == []
        assert result.most_positive == []

    @pytest.mark.asyncio
    async def test_extremes_preserves_criterion(self) -> None:
        """Verify the criterion field is set correctly."""
        endpoint = _make_events_endpoint([])
        result = await endpoint.extremes(_event_filter(), criterion="AvgTone")

        assert result.criterion == "AvgTone"

    @pytest.mark.asyncio
    async def test_extremes_preserves_requested_counts(self) -> None:
        """Verify requested_negative and requested_positive are stored."""
        endpoint = _make_events_endpoint([])
        result = await endpoint.extremes(_event_filter(), most_negative=5, most_positive=3)

        assert result.requested_negative == 5
        assert result.requested_positive == 3

    @pytest.mark.asyncio
    async def test_extremes_has_metadata(self) -> None:
        """Verify meta and sql are populated."""
        endpoint = _make_events_endpoint([])
        result = await endpoint.extremes(_event_filter())

        assert result.meta is not None
        assert result.sql is not None


# ---------------------------------------------------------------------------
# Events: compare
# ---------------------------------------------------------------------------


class TestEventsCompare:
    """Tests for EventsAnalyticsMixin.compare()."""

    @pytest.mark.asyncio
    async def test_compare_basic(self) -> None:
        """Verify compare returns a ComparisonResult with correct fields."""
        rows = [
            {"bucket": date(2024, 1, 1), "USA_count": 100, "CHN_count": 50},
        ]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.compare(
            _event_filter(),
            compare_by="Actor1CountryCode",
            values=["USA", "CHN"],
        )

        assert isinstance(result, ComparisonResult)
        assert result.compare_by == "Actor1CountryCode"
        assert result.values == ["USA", "CHN"]
        assert result.metric == "count"
        assert result.granularity == "DAY"

    @pytest.mark.asyncio
    async def test_compare_serializes_dates(self) -> None:
        """Verify date values in comparison rows are serialized to ISO strings."""
        rows = [
            {"bucket": date(2024, 1, 1), "USA_count": 100, "CHN_count": 50},
        ]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.compare(
            _event_filter(),
            compare_by="Actor1CountryCode",
            values=["USA", "CHN"],
        )

        assert result.rows[0]["bucket"] == "2024-01-01"

    @pytest.mark.asyncio
    async def test_compare_too_few_values(self) -> None:
        """Verify ValueError for fewer than 2 values."""
        endpoint = _make_events_endpoint([])
        with pytest.raises(ValueError, match="2"):
            await endpoint.compare(
                _event_filter(),
                compare_by="Actor1CountryCode",
                values=["USA"],
            )

    @pytest.mark.asyncio
    async def test_compare_too_many_values(self) -> None:
        """Verify ValueError for more than 10 values."""
        endpoint = _make_events_endpoint([])
        with pytest.raises(ValueError, match="2-10"):
            await endpoint.compare(
                _event_filter(),
                compare_by="Actor1CountryCode",
                values=[f"V{i}" for i in range(11)],
            )

    @pytest.mark.asyncio
    async def test_compare_duplicate_values(self) -> None:
        """Verify ValueError for duplicate values."""
        endpoint = _make_events_endpoint([])
        with pytest.raises(ValueError, match="duplicate"):
            await endpoint.compare(
                _event_filter(),
                compare_by="Actor1CountryCode",
                values=["USA", "USA"],
            )

    @pytest.mark.asyncio
    async def test_compare_has_metadata(self) -> None:
        """Verify meta and sql are populated."""
        rows = [{"bucket": date(2024, 1, 1), "USA_count": 10, "CHN_count": 5}]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.compare(
            _event_filter(),
            compare_by="Actor1CountryCode",
            values=["USA", "CHN"],
        )

        assert result.meta is not None
        assert result.sql is not None


# ---------------------------------------------------------------------------
# Events: trend
# ---------------------------------------------------------------------------


class TestEventsTrend:
    """Tests for EventsAnalyticsMixin.trend()."""

    @pytest.mark.asyncio
    async def test_trend_escalating(self) -> None:
        """Verify positive slope yields 'escalating' direction."""
        rows = [{"slope": 0.5, "r_squared": 0.8, "data_points": 30}]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.trend(_event_filter())

        assert isinstance(result, TrendResult)
        assert result.slope == 0.5
        assert result.r_squared == 0.8
        assert result.direction == "escalating"
        assert result.data_points == 30

    @pytest.mark.asyncio
    async def test_trend_de_escalating(self) -> None:
        """Verify negative slope yields 'de-escalating' direction."""
        rows = [{"slope": -0.3, "r_squared": 0.6, "data_points": 20}]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.trend(_event_filter())

        assert result.direction == "de-escalating"

    @pytest.mark.asyncio
    async def test_trend_stable(self) -> None:
        """Verify near-zero slope yields 'stable' direction."""
        rows = [{"slope": 0.0, "r_squared": 0.0, "data_points": 15}]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.trend(_event_filter())

        assert result.direction == "stable"

    @pytest.mark.asyncio
    async def test_trend_empty_raises(self) -> None:
        """Verify empty result raises ValueError."""
        endpoint = _make_events_endpoint([])
        with pytest.raises(ValueError, match="at least 2 data points"):
            await endpoint.trend(_event_filter())

    @pytest.mark.asyncio
    async def test_trend_insufficient_data_points_raises(self) -> None:
        """Verify data_points < 2 raises ValueError."""
        rows = [{"slope": 0.1, "r_squared": 0.5, "data_points": 1}]
        endpoint = _make_events_endpoint(rows)
        with pytest.raises(ValueError, match="at least 2 data points"):
            await endpoint.trend(_event_filter())

    @pytest.mark.asyncio
    async def test_trend_has_p_value(self) -> None:
        """Verify p_value is computed for sufficient data points."""
        rows = [{"slope": 0.5, "r_squared": 0.8, "data_points": 30}]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.trend(_event_filter())

        # p_value should be computed (not None) for 30 data points
        assert result.p_value is not None

    @pytest.mark.asyncio
    async def test_trend_has_metadata(self) -> None:
        """Verify meta and sql are populated."""
        rows = [{"slope": 0.1, "r_squared": 0.5, "data_points": 10}]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.trend(_event_filter())

        assert result.meta is not None
        assert result.sql is not None

    @pytest.mark.asyncio
    async def test_trend_metric_and_granularity(self) -> None:
        """Verify metric and granularity are set in result."""
        rows = [{"slope": 0.1, "r_squared": 0.5, "data_points": 10}]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.trend(
            _event_filter(),
            metric=EventMetric.AVG_TONE,
            granularity=TimeGranularity.WEEK,
        )

        assert result.metric == "avg_tone"
        assert result.granularity == "WEEK"


# ---------------------------------------------------------------------------
# Events: dyad_analysis
# ---------------------------------------------------------------------------


class TestEventsDyad:
    """Tests for EventsAnalyticsMixin.dyad_analysis()."""

    @pytest.mark.asyncio
    async def test_dyad_basic(self) -> None:
        """Verify dyad analysis splits rows into a_to_b and b_to_a."""
        rows = [
            {
                "bucket": date(2024, 1, 1),
                "a_to_b_count": 10,
                "a_to_b_avg_goldstein": 2.5,
                "b_to_a_count": 5,
                "b_to_a_avg_goldstein": -1.0,
            },
        ]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.dyad_analysis(_event_filter(), actor_a="USA", actor_b="RUS")

        assert isinstance(result, DyadResult)
        assert len(result.a_to_b) == 1
        assert len(result.b_to_a) == 1
        assert result.a_to_b[0]["count"] == 10
        assert result.a_to_b[0]["avg_goldstein"] == 2.5
        assert result.b_to_a[0]["count"] == 5
        assert result.b_to_a[0]["avg_goldstein"] == -1.0
        assert result.actor_a == "USA"
        assert result.actor_b == "RUS"

    @pytest.mark.asyncio
    async def test_dyad_serializes_dates(self) -> None:
        """Verify bucket dates are serialized to ISO strings."""
        rows = [
            {
                "bucket": date(2024, 1, 1),
                "a_to_b_count": 10,
                "b_to_a_count": 5,
            },
        ]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.dyad_analysis(_event_filter(), actor_a="USA", actor_b="RUS")

        assert result.a_to_b[0]["bucket"] == "2024-01-01"
        assert result.b_to_a[0]["bucket"] == "2024-01-01"

    @pytest.mark.asyncio
    async def test_dyad_empty(self) -> None:
        """Verify empty rows return empty a_to_b and b_to_a."""
        endpoint = _make_events_endpoint([])
        result = await endpoint.dyad_analysis(_event_filter(), actor_a="USA", actor_b="RUS")

        assert result.a_to_b == []
        assert result.b_to_a == []

    @pytest.mark.asyncio
    async def test_dyad_granularity_and_metrics(self) -> None:
        """Verify granularity and metrics are passed through to result."""
        rows = [
            {
                "bucket": date(2024, 1, 1),
                "a_to_b_count": 10,
                "b_to_a_count": 5,
            },
        ]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.dyad_analysis(
            _event_filter(),
            actor_a="USA",
            actor_b="RUS",
            granularity=TimeGranularity.MONTH,
            metrics=(EventMetric.COUNT,),
        )

        assert result.granularity == "MONTH"
        assert result.metrics == ["count"]

    @pytest.mark.asyncio
    async def test_dyad_has_metadata(self) -> None:
        """Verify meta and sql are populated."""
        rows = [
            {
                "bucket": date(2024, 1, 1),
                "a_to_b_count": 1,
                "b_to_a_count": 1,
            },
        ]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.dyad_analysis(_event_filter(), actor_a="USA", actor_b="RUS")

        assert result.meta is not None
        assert result.sql is not None


# ---------------------------------------------------------------------------
# Events: top_n_per_group
# ---------------------------------------------------------------------------


class TestEventsTopNPerGroup:
    """Tests for EventsAnalyticsMixin.top_n_per_group()."""

    @pytest.mark.asyncio
    async def test_top_n_basic(self) -> None:
        """Verify top_n_per_group groups rows by partition column."""
        rows = [
            {"Actor1CountryCode": "USA", "GoldsteinScale": 10.0, "EventCode": "050"},
            {"Actor1CountryCode": "USA", "GoldsteinScale": 8.0, "EventCode": "040"},
            {"Actor1CountryCode": "CHN", "GoldsteinScale": 7.0, "EventCode": "030"},
        ]
        endpoint = _make_events_endpoint(rows)
        result = await endpoint.top_n_per_group(
            _event_filter(),
            partition_by="Actor1CountryCode",
            order_by="GoldsteinScale",
            n=5,
        )

        assert isinstance(result, PartitionedTopNResult)
        assert "USA" in result.groups
        assert "CHN" in result.groups
        assert len(result.groups["USA"]) == 2
        assert len(result.groups["CHN"]) == 1

    @pytest.mark.asyncio
    async def test_top_n_preserves_params(self) -> None:
        """Verify partition_by, order_by, n, and ascending are stored."""
        endpoint = _make_events_endpoint([])
        result = await endpoint.top_n_per_group(
            _event_filter(),
            partition_by="Actor1CountryCode",
            order_by="GoldsteinScale",
            n=3,
            ascending=True,
        )

        assert result.partition_by == "Actor1CountryCode"
        assert result.order_by == "GoldsteinScale"
        assert result.n == 3
        assert result.ascending is True

    @pytest.mark.asyncio
    async def test_top_n_empty(self) -> None:
        """Verify empty rows return empty groups."""
        endpoint = _make_events_endpoint([])
        result = await endpoint.top_n_per_group(
            _event_filter(),
            partition_by="Actor1CountryCode",
            order_by="GoldsteinScale",
        )

        assert result.groups == {}

    @pytest.mark.asyncio
    async def test_top_n_has_metadata(self) -> None:
        """Verify meta and sql are populated."""
        endpoint = _make_events_endpoint([])
        result = await endpoint.top_n_per_group(
            _event_filter(),
            partition_by="Actor1CountryCode",
            order_by="GoldsteinScale",
        )

        assert result.meta is not None
        assert result.sql is not None


# ---------------------------------------------------------------------------
# Events: no BigQuery configured
# ---------------------------------------------------------------------------


class TestEventsNoBigQuery:
    """Tests for analytics methods when BigQuery is not configured."""

    @pytest.mark.asyncio
    async def test_time_series_no_bigquery_raises(self) -> None:
        """Verify ConfigurationError when BigQuery source is missing."""
        mock_file_source = MagicMock()
        endpoint = EventsEndpoint(file_source=mock_file_source)
        with pytest.raises(ConfigurationError, match="BigQuery"):
            await endpoint.time_series(_event_filter())

    @pytest.mark.asyncio
    async def test_extremes_no_bigquery_raises(self) -> None:
        """Verify ConfigurationError when BigQuery source is missing."""
        mock_file_source = MagicMock()
        endpoint = EventsEndpoint(file_source=mock_file_source)
        with pytest.raises(ConfigurationError, match="BigQuery"):
            await endpoint.extremes(_event_filter())

    @pytest.mark.asyncio
    async def test_compare_no_bigquery_raises(self) -> None:
        """Verify ConfigurationError when BigQuery source is missing."""
        mock_file_source = MagicMock()
        endpoint = EventsEndpoint(file_source=mock_file_source)
        with pytest.raises(ConfigurationError, match="BigQuery"):
            await endpoint.compare(
                _event_filter(),
                compare_by="Actor1CountryCode",
                values=["USA", "CHN"],
            )

    @pytest.mark.asyncio
    async def test_trend_no_bigquery_raises(self) -> None:
        """Verify ConfigurationError when BigQuery source is missing."""
        mock_file_source = MagicMock()
        endpoint = EventsEndpoint(file_source=mock_file_source)
        with pytest.raises(ConfigurationError, match="BigQuery"):
            await endpoint.trend(_event_filter())

    @pytest.mark.asyncio
    async def test_dyad_no_bigquery_raises(self) -> None:
        """Verify ConfigurationError when BigQuery source is missing."""
        mock_file_source = MagicMock()
        endpoint = EventsEndpoint(file_source=mock_file_source)
        with pytest.raises(ConfigurationError, match="BigQuery"):
            await endpoint.dyad_analysis(_event_filter(), actor_a="USA", actor_b="RUS")

    @pytest.mark.asyncio
    async def test_top_n_no_bigquery_raises(self) -> None:
        """Verify ConfigurationError when BigQuery source is missing."""
        mock_file_source = MagicMock()
        endpoint = EventsEndpoint(file_source=mock_file_source)
        with pytest.raises(ConfigurationError, match="BigQuery"):
            await endpoint.top_n_per_group(
                _event_filter(),
                partition_by="Actor1CountryCode",
                order_by="GoldsteinScale",
            )


# ---------------------------------------------------------------------------
# GKG: aggregate_themes
# ---------------------------------------------------------------------------


class TestGKGAggregateThemes:
    """Tests for GKGAnalyticsMixin.aggregate_themes()."""

    @pytest.mark.asyncio
    async def test_aggregate_themes(self) -> None:
        """Verify aggregate_themes delegates to bq.aggregate_gkg."""
        agg_result = AggregationResult(
            rows=[{"themes": "ENV_CLIMATECHANGE", "count": 500}],
            group_by=["themes"],
            total_rows=1,
            bytes_processed=1000,
        )
        endpoint = _make_gkg_endpoint(agg_result=agg_result)
        result = await endpoint.aggregate_themes(_gkg_filter())

        assert isinstance(result, AggregationResult)
        assert result.total_rows == 1
        assert result.rows[0]["themes"] == "ENV_CLIMATECHANGE"
        assert result.rows[0]["count"] == 500

    @pytest.mark.asyncio
    async def test_aggregate_themes_with_custom_top_n(self) -> None:
        """Verify top_n parameter is forwarded correctly."""
        agg_result = AggregationResult(
            rows=[],
            group_by=["themes"],
            total_rows=0,
            bytes_processed=500,
        )
        mock_bq = MagicMock()
        mock_bq.aggregate_gkg = AsyncMock(return_value=agg_result)
        type(mock_bq).last_query_metadata = PropertyMock(return_value=_mock_metadata())
        mock_file_source = MagicMock()
        endpoint = GKGEndpoint(file_source=mock_file_source, bigquery_source=mock_bq)

        await endpoint.aggregate_themes(_gkg_filter(), top_n=10)

        # Verify the limit kwarg was forwarded
        call_kwargs = mock_bq.aggregate_gkg.call_args.kwargs
        assert call_kwargs["limit"] == 10


# ---------------------------------------------------------------------------
# GKG: approx_top
# ---------------------------------------------------------------------------


class TestGKGApproxTop:
    """Tests for GKGAnalyticsMixin.approx_top()."""

    @pytest.mark.asyncio
    async def test_approx_top(self) -> None:
        """Verify approx_top returns an AggregationResult with correct rows."""
        rows = [
            {"name": "ENV_CLIMATECHANGE", "count": 1000},
            {"name": "ECON_STOCKMARKET", "count": 800},
        ]
        endpoint = _make_gkg_endpoint(bq_rows=rows)
        result = await endpoint.approx_top(_gkg_filter())

        assert isinstance(result, AggregationResult)
        assert len(result.rows) == 2
        assert result.total_rows == 2
        assert result.group_by == ["themes"]

    @pytest.mark.asyncio
    async def test_approx_top_custom_field(self) -> None:
        """Verify approx_top with a non-default field."""
        rows = [{"name": "John Smith", "count": 100}]
        endpoint = _make_gkg_endpoint(bq_rows=rows)
        result = await endpoint.approx_top(_gkg_filter(), field=GKGUnnestField.PERSONS)

        assert result.group_by == ["persons"]

    @pytest.mark.asyncio
    async def test_approx_top_empty(self) -> None:
        """Verify approx_top with no results."""
        endpoint = _make_gkg_endpoint(bq_rows=[])
        result = await endpoint.approx_top(_gkg_filter())

        assert result.rows == []
        assert result.total_rows == 0

    @pytest.mark.asyncio
    async def test_approx_top_bytes_processed(self) -> None:
        """Verify bytes_processed is set from BQ response."""
        endpoint = _make_gkg_endpoint(bq_rows=[])
        result = await endpoint.approx_top(_gkg_filter())

        # _execute_query_batch returns (rows, 1000) in our mock
        assert result.bytes_processed == 1000


# ---------------------------------------------------------------------------
# GKG: no BigQuery configured
# ---------------------------------------------------------------------------


class TestGKGNoBigQuery:
    """Tests for GKG analytics methods when BigQuery is not configured."""

    @pytest.mark.asyncio
    async def test_aggregate_themes_no_bigquery_raises(self) -> None:
        """Verify ConfigurationError when BigQuery source is missing."""
        mock_file_source = MagicMock()
        endpoint = GKGEndpoint(file_source=mock_file_source)
        with pytest.raises(ConfigurationError, match="BigQuery"):
            await endpoint.aggregate_themes(_gkg_filter())

    @pytest.mark.asyncio
    async def test_approx_top_no_bigquery_raises(self) -> None:
        """Verify ConfigurationError when BigQuery source is missing."""
        mock_file_source = MagicMock()
        endpoint = GKGEndpoint(file_source=mock_file_source)
        with pytest.raises(ConfigurationError, match="BigQuery"):
            await endpoint.approx_top(_gkg_filter())
