"""Data source modules for accessing GDELT data.

This package provides different sources for fetching GDELT data:
- FileSource: Direct download of GDELT data files from data.gdeltproject.org
- BigQuerySource: Access via Google BigQuery (fallback when APIs fail)
- DataFetcher: Orchestrator with automatic fallback between sources
"""

from py_gdelt.sources.bigquery import BigQuerySource
from py_gdelt.sources.fetcher import DataFetcher, ErrorPolicy, Parser
from py_gdelt.sources.files import FileSource


__all__ = ["BigQuerySource", "DataFetcher", "ErrorPolicy", "FileSource", "Parser"]
