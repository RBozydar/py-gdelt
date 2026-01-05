#!/usr/bin/env python3
"""Example: Download GDELT data files.

This example demonstrates how to use FileSource to download GDELT data files
for a specific date range, with proper error handling and progress tracking.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

from py_gdelt.config import GDELTSettings
from py_gdelt.exceptions import APIError, DataError, SecurityError
from py_gdelt.sources import FileSource


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def download_recent_events() -> None:
    """Download recent GDELT events data.

    Downloads events from the last 2 hours and saves them to disk.
    """
    # Configure settings
    settings = GDELTSettings(
        cache_dir=Path.home() / ".cache" / "gdelt",
        cache_ttl=3600,  # 1 hour
        max_concurrent_downloads=10,
    )

    # Calculate date range (2 hours on Jan 1, 2026)
    start_date = datetime(2026, 1, 1, 0, 0, 0)
    end_date = datetime(2026, 1, 1, 2, 0, 0)

    logger.info("Downloading GDELT events from %s to %s", start_date, end_date)

    async with FileSource(settings=settings) as source:
        try:
            # Get file URLs for date range
            urls = await source.get_files_for_date_range(
                start_date=start_date,
                end_date=end_date,
                file_type="export",
            )

            logger.info("Found %d potential files to download", len(urls))

            # Download and process files
            file_count = 0
            total_bytes = 0

            async for url, data in source.stream_files(urls):
                file_count += 1
                total_bytes += len(data)

                # Extract timestamp from URL
                timestamp = url.split("/")[-1].split(".")[0]
                logger.info(
                    "Downloaded file %d: %s (%d bytes)",
                    file_count,
                    timestamp,
                    len(data),
                )

                # Process the data (TAB-delimited CSV)
                lines = data.decode("utf-8").splitlines()
                logger.info("  Contains %d events", len(lines))

            logger.info(
                "\nDownload complete: %d files, %d total bytes (%.2f MB)",
                file_count,
                total_bytes,
                total_bytes / (1024 * 1024),
            )

        except APIError as e:
            logger.error("API error: %s", e)
        except DataError as e:
            logger.error("Data error: %s", e)
        except SecurityError as e:
            logger.error("Security error: %s", e)


async def download_specific_file() -> None:
    """Download a specific GDELT file by URL."""
    url = "https://data.gdeltproject.org/gdeltv2/20260101000000.export.CSV.zip"

    logger.info("Downloading specific file: %s", url)

    async with FileSource() as source:
        try:
            # Download and extract the file
            data = await source.download_and_extract(url)

            logger.info("Downloaded %d bytes", len(data))

            # Parse CSV data (TAB-delimited)
            lines = data.decode("utf-8").splitlines()
            logger.info("Contains %d events", len(lines))

            # Show first event (if any)
            if lines:
                first_event = lines[0].split("\t")
                logger.info("First event has %d fields", len(first_event))

        except APIError as e:
            logger.error("Download failed: %s", e)


async def list_available_files() -> None:
    """List all available GDELT files from master file list."""
    logger.info("Fetching master file list...")

    async with FileSource() as source:
        try:
            # Get master file list
            urls = await source.get_master_file_list(include_translation=False)

            logger.info("Found %d files in master list", len(urls))

            # Show recent files (last 10)
            recent_files = urls[-10:]
            logger.info("\nMost recent files:")
            for url in recent_files:
                filename = url.split("/")[-1]
                logger.info("  %s", filename)

        except APIError as e:
            logger.error("Failed to fetch master file list: %s", e)


async def download_with_custom_concurrency() -> None:
    """Download files with custom concurrency limits."""
    start_date = datetime(2026, 1, 1, 0, 0, 0)
    end_date = datetime(2026, 1, 1, 1, 0, 0)  # 1 hour of data

    logger.info("Downloading with custom concurrency limit")

    async with FileSource() as source:
        urls = await source.get_files_for_date_range(
            start_date=start_date,
            end_date=end_date,
            file_type="export",
        )

        logger.info("Downloading %d files with max 3 concurrent requests", len(urls))

        file_count = 0
        async for _url, data in source.stream_files(urls, max_concurrent=3):
            file_count += 1
            logger.info("Downloaded file %d/%d: %d bytes", file_count, len(urls), len(data))


def main() -> None:
    """Run examples."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python download_gdelt_files.py <example>")
        print("\nAvailable examples:")
        print("  recent      - Download recent events (last 2 hours)")
        print("  specific    - Download a specific file")
        print("  list        - List available files from master list")
        print("  concurrent  - Download with custom concurrency")
        sys.exit(1)

    example = sys.argv[1]

    if example == "recent":
        asyncio.run(download_recent_events())
    elif example == "specific":
        asyncio.run(download_specific_file())
    elif example == "list":
        asyncio.run(list_available_files())
    elif example == "concurrent":
        asyncio.run(download_with_custom_concurrency())
    else:
        print(f"Unknown example: {example}")
        sys.exit(1)


if __name__ == "__main__":
    main()
