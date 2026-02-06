"""
py-gdelt: Python client library for GDELT (Global Database of Events, Language, and Tone).

This library provides unified access to all GDELT data sources with a modern, type-safe API.
"""

from py_gdelt.client import GDELTClient
from py_gdelt.config import GDELTSettings
from py_gdelt.exceptions import (
    APIError,
    APIUnavailableError,
    BigQueryError,
    ConfigurationError,
    DataError,
    GDELTError,
    InvalidCodeError,
    InvalidQueryError,
    ParseError,
    RateLimitError,
    ValidationError,
)
from py_gdelt.sources.aggregation import (
    AggFunc,
    Aggregation,
    AggregationResult,
    GKGUnnestField,
)
from py_gdelt.sources.columns import EventColumns, GKGColumns, MentionColumns


__version__ = "0.1.3"

__all__ = [
    "APIError",
    "APIUnavailableError",
    # Aggregation types
    "AggFunc",
    "Aggregation",
    "AggregationResult",
    "BigQueryError",
    "ConfigurationError",
    "DataError",
    # Column profiles
    "EventColumns",
    # Main client
    "GDELTClient",
    # Exceptions
    "GDELTError",
    "GDELTSettings",
    "GKGColumns",
    "GKGUnnestField",
    "InvalidCodeError",
    "InvalidQueryError",
    "MentionColumns",
    "ParseError",
    "RateLimitError",
    "ValidationError",
    # Version
    "__version__",
]
