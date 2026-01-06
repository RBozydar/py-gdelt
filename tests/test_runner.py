#!/usr/bin/env python3
"""Quick test runner for verifying the FileSource implementation."""

import asyncio
from datetime import datetime

from py_gdelt.sources.files import FileSource


async def test_basic_functionality() -> None:
    """Test basic FileSource functionality."""
    print("Testing FileSource basic functionality...")

    async with FileSource() as source:
        print("✓ FileSource initialized successfully")

        # Test URL generation
        urls = await source.get_files_for_date_range(
            start_date=datetime(2024, 1, 1, 0, 0, 0),
            end_date=datetime(2024, 1, 1, 0, 30, 0),
            file_type="export",
        )
        print(f"✓ Generated {len(urls)} URLs for date range")
        print(f"  First URL: {urls[0]}")

        # Test date extraction
        date = FileSource._extract_date_from_url(urls[0])
        print(f"✓ Extracted date from URL: {date}")

        # Test HTTPS upgrade
        http_url = "http://data.gdeltproject.org/test.zip"
        https_url = FileSource._upgrade_to_https(http_url)
        print(f"✓ HTTPS upgrade: {http_url} -> {https_url}")

        print("\nAll basic tests passed!")


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
