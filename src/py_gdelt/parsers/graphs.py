"""Parser functions for GDELT Graph Datasets.

This module provides module-level parser functions for all 6 GDELT graph datasets:
- GQG (Global Quotation Graph) - JSON-NL
- GEG (Global Entity Graph) - JSON-NL
- GGG (Global Geographic Graph) - JSON-NL
- GEMG (Global Embedded Metadata Graph) - JSON-NL
- GAL (Article List) - JSON-NL
- GFG (Global Frontpage Graph) - TSV

All parsers handle gzip compression detection and decompression automatically.
Malformed lines are logged and skipped to ensure processing continues.
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import logging
from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel

from py_gdelt.models._internal import _RawGFGRecord
from py_gdelt.models.graphs import (
    GALRecord,
    GEGRecord,
    GEMGRecord,
    GFGRecord,
    GGGRecord,
    GQGRecord,
)


if TYPE_CHECKING:
    from collections.abc import Iterator


__all__ = [
    "parse_gal",
    "parse_geg",
    "parse_gemg",
    "parse_gfg",
    "parse_ggg",
    "parse_gqg",
]


logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def _decompress_if_needed(data: bytes) -> bytes:
    """Decompress data if it is gzip-compressed.

    Args:
        data: Raw bytes (potentially gzipped).

    Returns:
        Decompressed bytes if gzipped, otherwise original bytes.
    """
    if data.startswith(b"\x1f\x8b"):
        return gzip.decompress(data)
    return data


def _parse_jsonl(data: bytes, model_cls: type[T]) -> Iterator[T]:
    """Parse JSON-NL data into Pydantic models.

    Args:
        data: Raw bytes (potentially gzipped).
        model_cls: Pydantic model class to validate against.

    Yields:
        Validated Pydantic model instances.
    """
    # Use streaming approach to reduce memory usage
    if data.startswith(b"\x1f\x8b"):
        # Gzipped data - use gzip.open for streaming decompression
        fileobj = io.BytesIO(data)
        with gzip.open(fileobj, "rt", encoding="utf-8", errors="replace") as reader:
            yield from _parse_lines(reader, model_cls)
    else:
        # Plain text - use StringIO for line iteration
        with io.StringIO(data.decode("utf-8", errors="replace")) as reader:
            yield from _parse_lines(reader, model_cls)


def _parse_lines(reader: io.TextIOBase, model_cls: type[T]) -> Iterator[T]:
    """Parse lines from a text reader into Pydantic models.

    Args:
        reader: Text IO reader to read lines from.
        model_cls: Pydantic model class to validate against.

    Yields:
        Validated Pydantic model instances.
    """
    for line_num, raw_line in enumerate(reader, start=1):
        stripped = raw_line.rstrip("\n\r")
        if not stripped:
            continue

        try:
            obj = json.loads(stripped)
            yield model_cls.model_validate(obj)
        except json.JSONDecodeError as e:
            logger.warning("Malformed JSON at line %d: %s", line_num, e)
            continue
        except Exception as e:  # noqa: BLE001
            logger.warning("Failed to parse line %d: %s", line_num, e)
            continue


def parse_gqg(data: bytes) -> Iterator[GQGRecord]:
    """Parse Global Quotation Graph JSON-NL data.

    Args:
        data: Raw bytes (potentially gzipped).

    Yields:
        GQGRecord: Validated quotation records.
    """
    yield from _parse_jsonl(data, GQGRecord)


def parse_geg(data: bytes) -> Iterator[GEGRecord]:
    """Parse Global Entity Graph JSON-NL data.

    Args:
        data: Raw bytes (potentially gzipped).

    Yields:
        GEGRecord: Validated entity records.
    """
    yield from _parse_jsonl(data, GEGRecord)


def parse_ggg(data: bytes) -> Iterator[GGGRecord]:
    """Parse Global Geographic Graph JSON-NL data.

    Args:
        data: Raw bytes (potentially gzipped).

    Yields:
        GGGRecord: Validated geographic records.
    """
    yield from _parse_jsonl(data, GGGRecord)


def parse_gemg(data: bytes) -> Iterator[GEMGRecord]:
    """Parse Global Embedded Metadata Graph JSON-NL data.

    Args:
        data: Raw bytes (potentially gzipped).

    Yields:
        GEMGRecord: Validated embedded metadata records.
    """
    yield from _parse_jsonl(data, GEMGRecord)


def parse_gal(data: bytes) -> Iterator[GALRecord]:
    """Parse Article List JSON-NL data.

    Args:
        data: Raw bytes (potentially gzipped).

    Yields:
        GALRecord: Validated article records.
    """
    yield from _parse_jsonl(data, GALRecord)


def parse_gfg(data: bytes) -> Iterator[GFGRecord]:
    """Parse Global Frontpage Graph tab-delimited CSV data.

    Args:
        data: Raw bytes (potentially gzipped).

    Yields:
        GFGRecord: Validated frontpage graph records.
    """
    # Decompress if needed
    decompressed = _decompress_if_needed(data)

    # Decode as UTF-8
    text = decompressed.decode("utf-8", errors="replace")

    # Parse TSV with csv.reader
    reader = csv.reader(io.StringIO(text), delimiter="\t")

    for line_num, row in enumerate(reader, start=1):
        # Skip empty rows
        if not row or not row[0].strip():
            continue

        # Validate column count
        if len(row) < 6:
            logger.warning(
                "Incomplete row at line %d: expected 6 columns, got %d",
                line_num,
                len(row),
            )
            continue

        try:
            # Create internal _RawGFGRecord
            raw = _RawGFGRecord(
                date=row[0],
                from_frontpage_url=row[1],
                link_url=row[2],
                link_text=row[3],
                page_position=row[4],
                lang=row[5],
            )

            # Convert to public GFGRecord
            yield GFGRecord.from_raw(raw)
        except Exception as e:  # noqa: BLE001
            logger.warning("Failed to parse line %d: %s", line_num, e)
            continue
