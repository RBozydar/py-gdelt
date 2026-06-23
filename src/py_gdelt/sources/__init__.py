"""Data source modules for accessing GDELT data.

This package provides different sources for fetching GDELT data:
- FileSource: Direct download of GDELT data files from data.gdeltproject.org
- BigQuerySource: Access via Google BigQuery (fallback when APIs fail)
- DataFetcher: Orchestrator with automatic fallback between sources
"""

from typing import TYPE_CHECKING

from py_gdelt.sources.aggregation import (
    AggFunc,
    Aggregation,
    AggregationResult,
    GKGUnnestField,
)
from py_gdelt.sources.columns import EventColumns, GKGColumns, MentionColumns
from py_gdelt.sources.fetcher import DataFetcher, ErrorPolicy, Parser
from py_gdelt.sources.files import FileSource
from py_gdelt.sources.metadata import QueryEstimate, QueryMetadata


if TYPE_CHECKING:
    from py_gdelt.sources.bigquery import BigQuerySource

__all__ = [
    "AggFunc",
    "Aggregation",
    "AggregationResult",
    "BigQuerySource",
    "DataFetcher",
    "ErrorPolicy",
    "EventColumns",
    "FileSource",
    "GKGColumns",
    "GKGUnnestField",
    "MentionColumns",
    "Parser",
    "QueryEstimate",
    "QueryMetadata",
]


def __getattr__(name: str) -> object:
    """Lazily export optional BigQuery support."""
    if name != "BigQuerySource":
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)

    try:
        from py_gdelt.sources.bigquery import BigQuerySource  # noqa: PLC0415
    except ImportError as exc:
        msg = (
            "BigQuerySource requires the optional BigQuery dependency. "
            "Install it with: pip install 'gdelt-py[bigquery]'"
        )
        raise ImportError(msg) from exc
    return BigQuerySource
