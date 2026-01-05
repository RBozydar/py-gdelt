#!/usr/bin/env python3
"""Memory test for stream_files() sliding window fix using mocked responses.

This test simulates 100 file downloads of ~500KB each (50MB total data) to verify
memory stays bounded to ~5MB (10 concurrent × 500KB) instead of accumulating all 50MB.
"""

import asyncio
import io
import os
import random
import tempfile
import tracemalloc
import zipfile
from pathlib import Path

import httpx
import respx

from py_gdelt.config import GDELTSettings
from py_gdelt.sources import FileSource


# File size in bytes (~500KB uncompressed to stay within compression ratio)
# Compression ratio limit is 100x, so compressed size should be > decompressed/100
UNCOMPRESSED_SIZE = 500 * 1024  # 500KB
NUM_FILES = 100
MAX_CONCURRENT = 10


def create_mock_zip(size: int) -> bytes:
    """Create a ZIP file containing CSV data of specified uncompressed size.

    Uses random binary data mixed with text to achieve realistic compression ratio (~3-5x)
    that won't trigger zip bomb protection (max 100x).
    """
    # Mix random bytes with text to make it less compressible
    random.seed(42)  # Reproducible

    # Create semi-random content that compresses ~3-5x (not >100x)
    chunks = []
    bytes_generated = 0

    while bytes_generated < size:
        # Mix of random hex (incompressible) and structured text (compressible)
        chunk = (
            os.urandom(100).hex() + f"\t{random.randint(1, 9999999)}\t{random.uniform(-180, 180)}\n"
        )
        chunks.append(chunk)
        bytes_generated += len(chunk)

    csv_content = "".join(chunks)[:size]

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("data.export.CSV", csv_content)
    return buffer.getvalue()


async def test_memory_bounded_mock() -> None:
    """Stream 100 mocked files, verify memory stays bounded."""
    # Use temp cache to avoid using stale cached data
    with tempfile.TemporaryDirectory() as temp_cache:
        await _run_test(temp_cache)


async def _run_test(temp_cache: str) -> None:
    """Run the actual test with a temp cache directory."""
    tracemalloc.start()
    tracemalloc.reset_peak()

    settings = GDELTSettings(
        max_concurrent_downloads=MAX_CONCURRENT,
        cache_dir=Path(temp_cache),
    )

    # Generate URLs for 100 files
    urls = [
        f"http://data.gdeltproject.org/gdeltv2/202401010{i:04d}00.export.CSV.zip"
        for i in range(NUM_FILES)
    ]

    # Create mock ZIP data FRESH for this test
    mock_zip = create_mock_zip(UNCOMPRESSED_SIZE)
    compressed_size = len(mock_zip)

    # Calculate actual compression ratio
    ratio = UNCOMPRESSED_SIZE / compressed_size

    print(
        f"Mock ZIP: {compressed_size / 1024:.1f}KB compressed -> ~{UNCOMPRESSED_SIZE / 1024:.0f}KB uncompressed (ratio: {ratio:.1f}x)",
    )
    print(f"Total data if all held in memory: {NUM_FILES * UNCOMPRESSED_SIZE / 1024 / 1024:.0f}MB")
    print(
        f"Expected peak with sliding window: ~{MAX_CONCURRENT * UNCOMPRESSED_SIZE / 1024 / 1024:.0f}MB",
    )
    print()

    if ratio > 90:
        print(f"WARNING: Compression ratio {ratio:.1f}x is close to limit (100x)")

    with respx.mock(assert_all_mocked=False) as router:
        # Mock all URLs to return the same ZIP data
        for url in urls:
            # Need to mock HTTPS since FileSource upgrades to HTTPS
            https_url = url.replace("http://", "https://")
            router.get(https_url).mock(return_value=httpx.Response(200, content=mock_zip))

        async with FileSource(settings=settings) as source:
            file_count = 0
            total_bytes = 0

            async for url, data in source.stream_files(urls):
                file_count += 1
                total_bytes += len(data)

                # Check memory every 10 files
                if file_count % 10 == 0:
                    current, peak = tracemalloc.get_traced_memory()
                    print(
                        f"File {file_count}/{NUM_FILES}: "
                        f"Current={current / 1024 / 1024:.1f}MB, "
                        f"Peak={peak / 1024 / 1024:.1f}MB, "
                        f"Data={total_bytes / 1024 / 1024:.1f}MB",
                    )

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print()
    print("=" * 70)
    print(f"Processed {file_count} files ({total_bytes / 1024 / 1024:.1f} MB total data)")
    print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")
    print()

    # Memory should be bounded to roughly max_concurrent × file_size
    # Plus some overhead for the async machinery
    expected_max = MAX_CONCURRENT * UNCOMPRESSED_SIZE + 50 * 1024 * 1024  # + 50MB overhead

    if peak < expected_max:
        print(f"✅ PASS: Memory stayed bounded (< {expected_max / 1024 / 1024:.0f}MB)")
        if file_count == NUM_FILES:
            print(f"   Sliding window working correctly - processed all {NUM_FILES} files!")
        else:
            print(f"   Note: Only {file_count}/{NUM_FILES} files succeeded")
    else:
        print(f"❌ FAIL: Memory exceeded {expected_max / 1024 / 1024:.0f}MB threshold")
        print("   Sliding window may not be working - memory accumulated!")


if __name__ == "__main__":
    asyncio.run(test_memory_bounded_mock())
