"""Domain types for the analytics layer.

This module provides enums and configuration for analytics queries:

- **TimeGranularity**: Time bucketing granularity for time-series queries.
- **EventMetric**: Pre-defined metrics for Events table analytics.
- **MetricConfig**: Mapping from EventMetric to BigQuery aggregation expression.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final, NamedTuple


class TimeGranularity(StrEnum):
    """Time bucketing granularity for time-series queries."""

    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    QUARTER = "QUARTER"
    YEAR = "YEAR"


class EventMetric(StrEnum):
    """Pre-defined metrics for Events table analytics."""

    COUNT = "count"
    AVG_GOLDSTEIN = "avg_goldstein"
    AVG_TONE = "avg_tone"
    AVG_NUM_MENTIONS = "avg_num_mentions"
    AVG_NUM_SOURCES = "avg_num_sources"
    AVG_NUM_ARTICLES = "avg_num_articles"
    STDDEV_GOLDSTEIN = "stddev_goldstein"


class MetricConfig(NamedTuple):
    """Maps an EventMetric to a BigQuery aggregation expression.

    Args:
        agg_func: SQL aggregation function name (e.g., COUNT, AVG, STDDEV).
        bq_column: BigQuery column name to aggregate (use ``"*"`` for COUNT).
    """

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
