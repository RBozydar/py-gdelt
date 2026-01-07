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


__version__ = "0.1.3"

__all__ = [
    "APIError",
    "APIUnavailableError",
    "BigQueryError",
    "ConfigurationError",
    "DataError",
    # Main client
    "GDELTClient",
    # Exceptions
    "GDELTError",
    "GDELTSettings",
    "InvalidCodeError",
    "InvalidQueryError",
    "ParseError",
    "RateLimitError",
    "ValidationError",
    # Version
    "__version__",
]
