"""Analytics layer for BigQuery-powered GDELT queries.

This package provides prebuilt analytics methods that push computation
to BigQuery SQL, including time-series analysis, trend detection,
comparison pivots, and approximate aggregations.
"""

from py_gdelt.analytics._cost import SessionCostTracker
from py_gdelt.analytics.results import (
    ComparisonResult,
    DyadResult,
    ExtremeEventsResult,
    PartitionedTopNResult,
    TimeSeriesResult,
    TrendResult,
)
from py_gdelt.analytics.types import EventMetric, TimeGranularity


__all__ = [
    "ComparisonResult",
    "DyadResult",
    "EventMetric",
    "ExtremeEventsResult",
    "PartitionedTopNResult",
    "SessionCostTracker",
    "TimeGranularity",
    "TimeSeriesResult",
    "TrendResult",
]
