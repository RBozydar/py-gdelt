"""Integration tests for discovering schemas of new GDELT datasets.

This module downloads real files from GDELT to understand the actual schemas
of 4 new datasets that need to be integrated:
1. VGKG v2 (Visual Global Knowledge Graph)
2. TV-GKG (Television Global Knowledge Graph)
3. TV NGrams v2 (Television NGrams)
4. Radio NGrams

The tests print column counts and sample data to stdout for schema discovery.

Usage:
    Run all schema discovery tests:
        make integration-new-datasets

    Run a specific dataset test:
        uv run pytest tests/integration/test_new_datasets_schema_discovery.py::test_vgkg_schema_discovery -v -s

Note:
    - These tests require network access to data.gdeltproject.org
    - Tests will skip if files are not found (404 errors)
    - Use -s flag to see printed output (sample data)
"""

from __future__ import annotations

import gzip
import io
import logging
from typing import Final

import httpx
import pytest


logger = logging.getLogger(__name__)

# GDELT data source URLs
VGKG_LAST_UPDATE_URL: Final[str] = "http://data.gdeltproject.org/gdeltv3/vgkg/lastupdate.txt"
TV_GKG_LAST_UPDATE_URL: Final[str] = (
    "http://data.gdeltproject.org/gdeltv2_iatelevision/lastupdate.txt"
)
TV_NGRAMS_INVENTORY_URL: Final[str] = "http://data.gdeltproject.org/gdeltv3/iatv/ngramsv2/"
RADIO_NGRAMS_INVENTORY_URL: Final[str] = "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/"


def _extract_gzip(compressed_data: bytes) -> bytes:
    """Extract GZIP file content.

    Args:
        compressed_data: GZIP compressed bytes

    Returns:
        Decompressed content
    """
    result = io.BytesIO()

    with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gz:
        # Read in chunks to avoid memory issues
        chunk_size = 1024 * 1024  # 1MB chunks

        while True:
            chunk = gz.read(chunk_size)
            if not chunk:
                break
            result.write(chunk)

    return result.getvalue()


def _print_sample_data(
    dataset_name: str,
    file_url: str,
    content: bytes,
    max_rows: int = 5,
) -> None:
    """Print sample data from a TAB-delimited file for schema discovery.

    Args:
        dataset_name: Name of the dataset (for display)
        file_url: URL of the file (for display)
        content: Decompressed file content
        max_rows: Maximum number of rows to print
    """
    lines = content.decode("utf-8", errors="ignore").split("\n")
    non_empty_lines = [line for line in lines if line.strip()]

    print(f"\n{'=' * 80}")
    print(f"Dataset: {dataset_name}")
    print(f"File URL: {file_url}")
    print(f"Total lines (non-empty): {len(non_empty_lines)}")
    print(f"{'=' * 80}\n")

    for idx, line in enumerate(non_empty_lines[:max_rows], start=1):
        columns = line.split("\t")
        print(f"Row {idx}: {len(columns)} columns")
        print("-" * 80)

        # Print each column with its index and value (truncate long values)
        for col_idx, col_value in enumerate(columns):
            # Truncate very long values for readability
            display_value = col_value[:100] if len(col_value) > 100 else col_value
            if len(col_value) > 100:
                display_value += f"... (truncated, total: {len(col_value)} chars)"

            print(f"  [{col_idx:3d}] {display_value}")

        print()


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(180)  # 3 minute timeout for downloads
async def test_vgkg_schema_discovery() -> None:
    """Discover schema for VGKG v2 (Visual Global Knowledge Graph) dataset.

    Downloads a recent VGKG file and prints sample data to understand the schema.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Get the last update file to find a recent data file
        try:
            response = await client.get(VGKG_LAST_UPDATE_URL)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip(f"VGKG lastupdate.txt not found: {VGKG_LAST_UPDATE_URL}")
            raise

        # Parse the lastupdate.txt file (format: file_size hash file_url)
        lastupdate_content = response.text.strip()
        lines = lastupdate_content.split("\n")

        # Find the first VGKG data file URL (URL is in the 3rd column)
        vgkg_url = None
        for line in lines:
            parts = line.split()
            if len(parts) >= 3 and "vgkg" in parts[2].lower():
                vgkg_url = parts[2]
                break

        if vgkg_url is None:
            pytest.skip("No VGKG file URL found in lastupdate.txt")

        # Download the file
        try:
            logger.info("Downloading VGKG file: %s", vgkg_url)
            response = await client.get(vgkg_url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip(f"VGKG file not found: {vgkg_url}")
            raise

        # Decompress if gzipped
        content = response.content
        if vgkg_url.endswith(".gz"):
            content = _extract_gzip(content)

        # Print sample data
        _print_sample_data("VGKG v2", vgkg_url, content, max_rows=3)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(180)
async def test_tv_gkg_schema_discovery() -> None:
    """Discover schema for TV-GKG (Television Global Knowledge Graph) dataset.

    Downloads a recent TV-GKG file and prints sample data to understand the schema.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Get the last update file to find a recent data file
        try:
            response = await client.get(TV_GKG_LAST_UPDATE_URL)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip(f"TV-GKG lastupdate.txt not found: {TV_GKG_LAST_UPDATE_URL}")
            raise

        # Parse the lastupdate.txt file (format: file_size hash file_url)
        lastupdate_content = response.text.strip()
        lines = lastupdate_content.split("\n")

        # Find a GKG file URL (URL is in the 3rd column)
        tv_gkg_url = None
        for line in lines:
            parts = line.split()
            if len(parts) >= 3 and ".gkg." in parts[2].lower():
                tv_gkg_url = parts[2]
                break

        if tv_gkg_url is None:
            pytest.skip("No TV-GKG file URL found in lastupdate.txt")

        # Download the file
        try:
            logger.info("Downloading TV-GKG file: %s", tv_gkg_url)
            response = await client.get(tv_gkg_url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip(f"TV-GKG file not found: {tv_gkg_url}")
            raise

        # Decompress if gzipped
        content = response.content
        if tv_gkg_url.endswith(".gz"):
            content = _extract_gzip(content)

        # Print sample data
        _print_sample_data("TV-GKG", tv_gkg_url, content, max_rows=3)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(180)
async def test_tv_ngrams_schema_discovery() -> None:
    """Discover schema for TV NGrams dataset.

    Downloads a recent TV NGrams file and prints sample data to understand the schema.
    TV NGrams are TAB-delimited with 5 columns: DATE, STATION, HOUR, WORD, COUNT.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        # TV NGrams uses station-specific file lists
        # Try CNN as it's a common station
        filelist_url = "http://data.gdeltproject.org/gdeltv3/iatv/ngrams/FILELIST-CNN.TXT"

        try:
            response = await client.get(filelist_url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip(f"TV NGrams filelist not found: {filelist_url}")
            raise

        # Parse the file list (one URL per line)
        filelist_content = response.text.strip()
        lines = filelist_content.split("\n")

        # Find a recent 1gram file
        tv_ngrams_url = None
        for line in reversed(lines[-20:]):  # Check last 20 entries (most recent)
            if "1gram" in line and line.strip().endswith(".gz"):
                tv_ngrams_url = line.strip()
                break

        if not tv_ngrams_url:
            pytest.skip("No TV NGrams 1gram file found in filelist")

        # Type narrowing: after skip, tv_ngrams_url is str
        assert tv_ngrams_url is not None

        # Download the file
        try:
            logger.info("Downloading TV NGrams file: %s", tv_ngrams_url)
            response = await client.get(tv_ngrams_url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip(f"TV NGrams file not found: {tv_ngrams_url}")
            raise

        # Decompress
        content = _extract_gzip(response.content)

        # Print sample TAB-delimited records
        _print_sample_data("TV NGrams", tv_ngrams_url, content, max_rows=5)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(180)
async def test_radio_ngrams_schema_discovery() -> None:
    """Discover schema for Radio NGrams dataset.

    Downloads a Radio NGrams file and prints sample data to understand the schema.
    Radio NGrams are TAB-delimited with 6 columns: DATE, STATION, HOUR, NGRAM, COUNT, SHOW.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        # The Radio NGrams directory has daily YYYYMMDD.txt inventory files
        # Use a known working date (2023) since recent data may not be available
        inventory_url = f"{RADIO_NGRAMS_INVENTORY_URL}20230101.txt"

        try:
            response = await client.get(inventory_url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip(f"Radio NGrams inventory not found: {inventory_url}")
            raise

        # Parse inventory file (one URL per line)
        inventory_content = response.text.strip()
        lines = inventory_content.split("\n")

        # Find a 1gram file
        radio_ngrams_url = None
        for raw_line in lines:
            line = raw_line.strip()
            if "1gram" in line and line.endswith(".gz"):
                radio_ngrams_url = line
                break

        if not radio_ngrams_url:
            pytest.skip("No Radio NGrams 1gram file found in inventory")

        # Type narrowing
        assert radio_ngrams_url is not None

        # Download the file
        try:
            logger.info("Downloading Radio NGrams file: %s", radio_ngrams_url)
            response = await client.get(radio_ngrams_url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip(f"Radio NGrams file not found: {radio_ngrams_url}")
            raise

        # Decompress
        content = _extract_gzip(response.content)

        # Print sample TAB-delimited records
        _print_sample_data("Radio NGrams", radio_ngrams_url, content, max_rows=5)
