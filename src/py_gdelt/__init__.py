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


__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Main client
    "GDELTClient",
    "GDELTSettings",
    # Exceptions
    "GDELTError",
    "APIError",
    "RateLimitError",
    "APIUnavailableError",
    "InvalidQueryError",
    "DataError",
    "ParseError",
    "ValidationError",
    "InvalidCodeError",
    "ConfigurationError",
    "BigQueryError",
]
