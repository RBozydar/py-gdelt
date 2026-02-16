"""Export GDELT data for a single day to typed Parquet files.

Downloads events, GKG, and mentions for 2026-02-01 (first hour),
writes per-slot Parquet files + a compacted daily file, and verifies
readability with PyArrow.

Usage:
    uv run python examples/parquet_export.py
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from py_gdelt.parquet import (
    events_to_batch,
    gkg_to_batch,
    mentions_to_batch,
    to_parquet,
    write_parquet,
)
from py_gdelt.parsers.events import EventsParser
from py_gdelt.parsers.gkg import GKGParser
from py_gdelt.parsers.mentions import MentionsParser
from py_gdelt.sources.files import FileSource

OUTPUT_DIR = Path("examples/output/parquet")

# Map FileSource file_type → parquet DatasetType
FILE_TYPE_TO_DATASET = {
    "export": "events",
    "gkg": "gkg",
    "mentions": "mentions",
}

BATCH_BUILDERS = {
    "events": lambda data: events_to_batch(EventsParser().parse(data)),
    "gkg": lambda data: gkg_to_batch(GKGParser().parse(data)),
    "mentions": lambda data: mentions_to_batch(MentionsParser().parse(data)),
}


async def main() -> None:
    target_date = datetime(2026, 2, 1)
    end_date = datetime(2026, 2, 1, 1, 0, 0)  # First hour only (4 slots)

    for file_type in ("export", "gkg", "mentions"):
        dataset = FILE_TYPE_TO_DATASET[file_type]
        print(f"\n{'=' * 60}")
        print(f"Dataset: {file_type} -> {dataset}")
        print(f"{'=' * 60}")

        out_dir = OUTPUT_DIR / dataset / f"dt={target_date:%Y-%m-%d}"
        out_dir.mkdir(parents=True, exist_ok=True)

        async with FileSource() as source:
            urls = await source.get_files_for_date_range(
                start_date=target_date,
                end_date=end_date,
                file_type=file_type,  # type: ignore[arg-type]
            )
            print(f"  URLs generated: {len(urls)}")

            file_count = 0
            total_rows = 0
            batches: list[pa.RecordBatch] = []

            async for url, data in source.stream_files(urls, max_concurrent=3):
                file_count += 1
                filename = url.split("/")[-1].split(".")[0]

                # Write individual per-slot Parquet file
                slot_path = out_dir / f"{filename}.parquet"
                result = to_parquet(
                    data,
                    slot_path,
                    dataset=dataset,  # type: ignore[arg-type]
                )
                total_rows += result.row_count
                print(
                    f"  [{file_count}] {filename}: {result.row_count} rows, "
                    f"{result.byte_count:,} bytes"
                )

                # Collect batches for daily compaction
                batches.append(BATCH_BUILDERS[dataset](data))

            print(f"\n  Total: {file_count} files, {total_rows} rows")

            # Write compacted daily file (recommended for large datasets)
            if batches:
                table = pa.concat_tables([pa.Table.from_batches([b]) for b in batches])
                compacted_path = out_dir / "part-0.parquet"
                compact_result = write_parquet(table, compacted_path)
                print(
                    f"  Compacted: {compact_result.row_count} rows, "
                    f"{compact_result.byte_count:,} bytes -> {compacted_path}"
                )

                # Verify readability
                read_back = pq.read_table(compacted_path)
                print(f"  Read-back: {read_back.num_rows} rows, {read_back.num_columns} columns")
                print(f"  Schema sample: {read_back.schema.names[:5]}...")

    print(f"\n{'=' * 60}")
    print("All done! Files at:", OUTPUT_DIR)
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
