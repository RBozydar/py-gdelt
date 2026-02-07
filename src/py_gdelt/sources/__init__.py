"""Data source modules for accessing GDELT data.

This package provides different sources for fetching GDELT data:
- FileSource: Direct download of GDELT data files from data.gdeltproject.org
- BigQuerySource: Access via Google BigQuery (fallback when APIs fail)
- DataFetcher: Orchestrator with automatic fallback between sources
"""

from py_gdelt.sources.aggregation import (
    AggFunc,
    Aggregation,
    AggregationResult,
    GKGUnnestField,
)
from py_gdelt.sources.bigquery import BigQuerySource
from py_gdelt.sources.columns import EventColumns, GKGColumns, MentionColumns
from py_gdelt.sources.fetcher import DataFetcher, ErrorPolicy, Parser
from py_gdelt.sources.files import FileSource
from py_gdelt.sources.metadata import QueryEstimate, QueryMetadata


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
