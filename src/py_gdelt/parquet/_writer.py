"""Parquet writing utilities for GDELT data.

Provides a low-level :func:`write_parquet` helper that performs atomic
writes (temp file + rename) and a high-level :func:`to_parquet` convenience
that goes from raw bytes all the way to a Parquet file on disk.
"""

from __future__ import annotations

import contextlib
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pyarrow as pa
import pyarrow.parquet as pq

from py_gdelt.parquet._converters import events_to_batch, gkg_to_batch, mentions_to_batch
from py_gdelt.parsers.events import EventsParser
from py_gdelt.parsers.gkg import GKGParser
from py_gdelt.parsers.mentions import MentionsParser


__all__ = [
    "DatasetType",
    "ExportResult",
    "to_parquet",
    "write_parquet",
]

logger = logging.getLogger(__name__)

DatasetType = Literal["events", "gkg", "mentions"]
ParquetCompression = Literal["snappy", "gzip", "brotli", "zstd", "lz4", "none"]


@dataclass(frozen=True, slots=True)
class ExportResult:
    """Result metadata from a Parquet export operation.

    Attributes:
        row_count: Number of rows written.
        byte_count: Size of the resulting Parquet file in bytes.
        output_path: Absolute path to the written file.
    """

    row_count: int
    byte_count: int
    output_path: Path


def write_parquet(
    batch: pa.RecordBatch | pa.Table,
    path: Path,
    *,
    compression: ParquetCompression = "zstd",
    compression_level: int = 3,
    row_group_size: int = 500_000,
) -> ExportResult:
    """Write an Arrow RecordBatch or Table to a Parquet file atomically.

    The write is performed to a temporary file in the same directory as
    *path* and then renamed, so readers never see a partial file.

    Args:
        batch: Arrow data to write (RecordBatch or Table).
        path: Destination file path.
        compression: Parquet compression codec.
        compression_level: Optional codec-specific compression level.
        row_group_size: Maximum number of rows per row group.

    Returns:
        An :class:`ExportResult` with row count, byte count, and output path.

    Raises:
        OSError: If the file cannot be written or renamed.
    """
    table = pa.Table.from_batches([batch]) if isinstance(batch, pa.RecordBatch) else batch
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_fd = None
    tmp_path: str | None = None
    try:
        tmp_fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
        # Close the fd immediately; pq.write_table opens the file by name
        os.close(tmp_fd)
        tmp_fd = None

        write_kwargs: dict[str, object] = {
            "write_statistics": True,
            "row_group_size": row_group_size,
        }
        if compression != "none":
            write_kwargs["compression"] = compression
            write_kwargs["compression_level"] = compression_level
        else:
            write_kwargs["compression"] = "NONE"

        pq.write_table(table, tmp_path, **write_kwargs)
        Path(tmp_path).replace(path)
        tmp_path = None  # Rename succeeded; nothing to clean up

        return ExportResult(
            row_count=table.num_rows,
            byte_count=path.stat().st_size,
            output_path=path,
        )
    finally:
        if tmp_path is not None:
            with contextlib.suppress(OSError):
                Path(tmp_path).unlink()
        if tmp_fd is not None:
            with contextlib.suppress(OSError):
                os.close(tmp_fd)


def to_parquet(
    data: bytes,
    output_path: Path,
    *,
    dataset: DatasetType,
    is_translated: bool = False,
    compression: ParquetCompression = "zstd",
    compression_level: int = 3,
) -> ExportResult:
    """Parse raw GDELT bytes and write the result as a Parquet file.

    This is a high-level convenience that chains parsing, Arrow conversion,
    and Parquet writing into a single call.

    Args:
        data: Raw bytes from a GDELT data file (TAB-delimited).
        output_path: Destination Parquet file path.
        dataset: Which GDELT table the data represents.
        is_translated: Whether the data comes from a translated feed.
        compression: Parquet compression codec.
        compression_level: Optional codec-specific compression level.

    Returns:
        An :class:`ExportResult` with row count, byte count, and output path.

    Raises:
        ValueError: If *dataset* is not a recognised dataset type.
    """
    batch: pa.RecordBatch
    if dataset == "events":
        batch = events_to_batch(EventsParser().parse(data, is_translated))
    elif dataset == "gkg":
        batch = gkg_to_batch(GKGParser().parse(data, is_translated))
    elif dataset == "mentions":
        batch = mentions_to_batch(MentionsParser().parse(data))
    else:  # pragma: no cover
        msg = f"Unknown dataset type: {dataset!r}"  # type: ignore[unreachable]
        raise ValueError(msg)

    return write_parquet(
        batch, output_path, compression=compression, compression_level=compression_level
    )
