"""Parquet export module for converting GDELT data to typed Parquet files.

Requires pyarrow. Install with: pip install gdelt-py[parquet]
"""

from __future__ import annotations


try:
    import pyarrow as pa  # noqa: F401
except ImportError:
    msg = "The parquet module requires pyarrow. Install with: pip install gdelt-py[parquet]"
    raise ImportError(msg) from None

from py_gdelt.parquet._converters import (
    events_to_batch,
    gkg_to_batch,
    mentions_to_batch,
)
from py_gdelt.parquet._schemas import EVENTS_SCHEMA, GKG_SCHEMA, MENTIONS_SCHEMA
from py_gdelt.parquet._writer import (
    DatasetType,
    ExportResult,
    to_parquet,
    write_parquet,
)


__all__ = [
    "EVENTS_SCHEMA",
    "GKG_SCHEMA",
    "MENTIONS_SCHEMA",
    "DatasetType",
    "ExportResult",
    "events_to_batch",
    "gkg_to_batch",
    "mentions_to_batch",
    "to_parquet",
    "write_parquet",
]
