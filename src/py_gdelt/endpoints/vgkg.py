"""VGKG endpoint for Visual Global Knowledge Graph data.

This module provides the VGKGEndpoint class for accessing GDELT's VGKG data,
which contains Google Cloud Vision API analysis of images extracted from
news articles, including labels, logos, faces, OCR text, and safe search scores.

VGKG is file-based only (no BigQuery support) and uses the FileSource for
orchestrated downloads with automatic retry and error handling.

Example:
    >>> from py_gdelt.endpoints import VGKGEndpoint
    >>> from py_gdelt.filters import VGKGFilter, DateRange
    >>> from datetime import date
    >>>
    >>> async with VGKGEndpoint() as vgkg:
    ...     filter_obj = VGKGFilter(
    ...         date_range=DateRange(start=date(2024, 1, 1)),
    ...         domain="cnn.com",
    ...         min_label_confidence=0.8,
    ...     )
    ...     result = await vgkg.query(filter_obj)
    ...     for record in result:
    ...         print(record.image_url, len(record.labels))
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Final

from pydantic import ValidationError

from py_gdelt.config import GDELTSettings
from py_gdelt.models.common import FetchResult
from py_gdelt.models.vgkg import VGKGRecord
from py_gdelt.parsers.vgkg import VGKGParser
from py_gdelt.sources.files import FileSource


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from py_gdelt.filters import VGKGFilter

__all__ = ["VGKGEndpoint"]

logger = logging.getLogger(__name__)


# VGKG data URLs
VGKG_LAST_UPDATE_URL: Final[str] = "http://data.gdeltproject.org/gdeltv3/vgkg/lastupdate.txt"
VGKG_BASE_URL: Final[str] = "http://data.gdeltproject.org/gdeltv3/vgkg/"


class VGKGEndpoint:
    """Endpoint for VGKG (Visual Global Knowledge Graph) data.

    VGKG provides Google Cloud Vision API analysis of images from news articles,
    including:
    - Labels (what objects/concepts are in the image)
    - Logos (brand/company logo detection)
    - Web entities (what the image is about)
    - Safe search scores (adult/violence/medical content)
    - Face detection (pose angles, confidence)
    - OCR text (text visible in the image)
    - Landmark detection (famous places)

    VGKG is file-based only (no BigQuery support). Files are generated every 15
    minutes and are available at http://data.gdeltproject.org/gdeltv3/vgkg/.

    Args:
        settings: Configuration settings. If None, uses defaults.
        file_source: Optional shared FileSource. If None, creates owned instance.
                    When provided, the source lifecycle is managed externally.

    Example:
        Batch query with filtering:

        >>> from py_gdelt.filters import VGKGFilter, DateRange
        >>> from datetime import date
        >>> async with VGKGEndpoint() as endpoint:
        ...     filter_obj = VGKGFilter(
        ...         date_range=DateRange(start=date(2024, 1, 1)),
        ...         domain="cnn.com",
        ...         min_label_confidence=0.8,
        ...     )
        ...     result = await endpoint.query(filter_obj)
        ...     print(f"Found {len(result)} records")

        Streaming for large datasets:

        >>> async with VGKGEndpoint() as endpoint:
        ...     filter_obj = VGKGFilter(
        ...         date_range=DateRange(
        ...             start=date(2024, 1, 1),
        ...             end=date(2024, 1, 2)
        ...         ),
        ...         domain="bbc.com",
        ...     )
        ...     async for record in endpoint.stream(filter_obj):
        ...         if record.labels:
        ...             print(f"Image: {record.image_url} - Labels: {len(record.labels)}")

        Get latest VGKG records:

        >>> async with VGKGEndpoint() as endpoint:
        ...     latest = await endpoint.get_latest()
        ...     print(f"Latest update has {len(latest)} records")
    """

    def __init__(
        self,
        settings: GDELTSettings | None = None,
        file_source: FileSource | None = None,
    ) -> None:
        self.settings = settings or GDELTSettings()

        if file_source is not None:
            self._file_source = file_source
            self._owns_sources = False
        else:
            self._file_source = FileSource(settings=self.settings)
            self._owns_sources = True

        # Create parser instance
        self._parser = VGKGParser()

    async def close(self) -> None:
        """Close resources if we own them.

        Only closes resources that were created by this instance.
        Shared resources are not closed to allow reuse.
        """
        if self._owns_sources:
            # FileSource uses context manager protocol, manually call __aexit__
            await self._file_source.__aexit__(None, None, None)

    async def __aenter__(self) -> VGKGEndpoint:
        """Async context manager entry.

        Returns:
            Self for use in async with statement.
        """
        # Ensure FileSource is initialized
        if self._owns_sources:
            await self._file_source.__aenter__()
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit - close resources.

        Args:
            *args: Exception info (unused, but required by protocol).
        """
        await self.close()

    async def query(self, filter_obj: VGKGFilter) -> FetchResult[VGKGRecord]:
        """Query VGKG data and return all results.

        Fetches all VGKG records matching the filter criteria and returns them
        as a FetchResult. This method collects all records in memory before returning,
        so use stream() for large result sets to avoid memory issues.

        Args:
            filter_obj: Filter with date range, domain, and confidence threshold

        Returns:
            FetchResult containing list of VGKGRecord instances and any failed requests

        Raises:
            RateLimitError: If rate limited and retries exhausted
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> filter_obj = VGKGFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     domain="reuters.com",
            ...     min_label_confidence=0.9,
            ... )
            >>> result = await endpoint.query(filter_obj)
            >>> print(f"Found {len(result)} high-confidence records from Reuters")
        """
        # Stream all records and collect them
        records: list[VGKGRecord] = [record async for record in self.stream(filter_obj)]

        logger.info("Collected %d VGKG records from query", len(records))

        # Return FetchResult (no failed tracking for now - FileSource handles errors)
        return FetchResult(data=records, failed=[])

    async def stream(self, filter_obj: VGKGFilter) -> AsyncIterator[VGKGRecord]:
        """Stream VGKG data record by record.

        Yields VGKG records one at a time, converting internal _RawVGKG dataclass
        instances to Pydantic VGKGRecord models at the yield boundary. This method
        is memory-efficient for large result sets.

        Client-side filtering is applied for domain and label confidence constraints
        since file downloads provide all records for a date/time range.

        Args:
            filter_obj: Filter with date range, domain, and confidence threshold

        Yields:
            VGKGRecord: Individual VGKG records matching the filter criteria

        Raises:
            RateLimitError: If rate limited and retries exhausted
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> filter_obj = VGKGFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     domain="nytimes.com",
            ...     min_label_confidence=0.85,
            ... )
            >>> async for record in endpoint.stream(filter_obj):
            ...     print(f"Image: {record.image_url}")
            ...     for label in record.labels:
            ...         if label["confidence"] >= 0.85:
            ...             print(f"  - {label['description']}: {label['confidence']:.2f}")
        """
        logger.debug("Starting VGKG stream for filter: %s", filter_obj)

        # Build URLs for the date range
        urls = self._build_urls(filter_obj)
        logger.debug("Generated %d VGKG URLs", len(urls))

        # Stream files and parse records
        async for _url, data in self._file_source.stream_files(urls):
            for raw_record in self._parser.parse(data):
                # Convert _RawVGKG to VGKGRecord (type conversion happens here)
                try:
                    record = VGKGRecord.from_raw(raw_record)
                except (ValueError, ValidationError) as e:
                    logger.warning("Failed to parse VGKG record: %s - Skipping", e)
                    continue

                # Apply client-side filtering
                if not self._matches_filter(record, filter_obj):
                    continue

                yield record

    async def get_latest(self) -> list[VGKGRecord]:
        """Get the most recent VGKG records.

        Fetches the lastupdate.txt file to find the most recent data file,
        then parses and returns all records from that file.

        Returns:
            List of VGKGRecord from the most recent update.

        Raises:
            APIError: If fetching or parsing fails.

        Example:
            >>> async with VGKGEndpoint() as endpoint:
            ...     latest = await endpoint.get_latest()
            ...     if latest:
            ...         print(f"Latest update: {latest[0].date}")
            ...         print(f"Total records: {len(latest)}")
        """
        # Fetch lastupdate.txt using FileSource's shared client
        response = await self._file_source.client.get(VGKG_LAST_UPDATE_URL)
        response.raise_for_status()

        # Parse to find VGKG file URL (format: size hash url)
        vgkg_url = None
        for line in response.text.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 3 and "vgkg" in parts[2].lower():
                vgkg_url = parts[2]
                break

        if not vgkg_url:
            logger.warning("No VGKG file found in lastupdate.txt")
            return []

        # Download and parse
        records: list[VGKGRecord] = []
        async for _url, data in self._file_source.stream_files([vgkg_url]):
            for raw_record in self._parser.parse(data):
                try:
                    records.append(VGKGRecord.from_raw(raw_record))
                except (ValueError, ValidationError) as e:
                    logger.warning("Failed to parse VGKG record: %s - Skipping", e)

        logger.info("Retrieved %d records from latest VGKG update", len(records))
        return records

    def _build_urls(self, filter_obj: VGKGFilter) -> list[str]:
        """Build file URLs for the filter parameters.

        VGKG files are named: YYYYMMDDHHMMSS.vgkg.csv.gz
        Files are generated every 15 minutes.

        Args:
            filter_obj: Filter with date range.

        Returns:
            List of URLs to download.

        Note:
            Unlike RadioNGramsEndpoint, URL validation is not needed here because
            URLs are constructed entirely from trusted internal constants (BASE_URL)
            and validated filter parameters (date_range). No external input
            influences the URL structure, eliminating SSRF risk.
        """
        from datetime import UTC, datetime, timedelta

        urls: list[str] = []

        # Convert dates to datetimes for 15-min iteration
        start = datetime.combine(
            filter_obj.date_range.start,
            datetime.min.time(),
            tzinfo=UTC,
        )
        end_date = filter_obj.date_range.end or filter_obj.date_range.start
        end = datetime.combine(end_date, datetime.max.time(), tzinfo=UTC)

        current = start
        delta = timedelta(minutes=15)

        while current <= end:
            timestamp = current.strftime("%Y%m%d%H%M%S")
            url = f"{VGKG_BASE_URL}{timestamp}.vgkg.csv.gz"
            urls.append(url)
            current += delta

        logger.debug(
            "Generated %d VGKG URLs for date range %s to %s",
            len(urls),
            start,
            end,
        )
        return urls

    def _matches_filter(self, record: VGKGRecord, filter_obj: VGKGFilter) -> bool:
        """Check if record matches filter criteria.

        Applies client-side filtering for domain and label confidence constraints.
        Date filtering is handled by URL generation (_build_urls).

        Args:
            record: VGKGRecord to check
            filter_obj: Filter criteria

        Returns:
            True if record matches all filter criteria, False otherwise
        """
        # Filter by domain (case-insensitive)
        if filter_obj.domain and record.domain.lower() != filter_obj.domain.lower():
            return False

        # Filter by label confidence (check if ANY label meets threshold)
        if filter_obj.min_label_confidence > 0 and record.labels:
            has_confident_label = any(
                label["confidence"] >= filter_obj.min_label_confidence for label in record.labels
            )
            if not has_confident_label:
                return False

        return True

    def query_sync(self, filter_obj: VGKGFilter) -> FetchResult[VGKGRecord]:
        """Synchronous wrapper for query().

        Runs the async query() method in a new event loop. This is a convenience
        method for synchronous code, but async methods are preferred when possible.

        Args:
            filter_obj: Filter with date range and optional constraints

        Returns:
            FetchResult containing list of VGKGRecord instances

        Raises:
            RateLimitError: If rate limited and retries exhausted
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> filter_obj = VGKGFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     domain="cnn.com",
            ... )
            >>> result = endpoint.query_sync(filter_obj)
            >>> print(f"Found {len(result)} records")
        """
        return asyncio.run(self.query(filter_obj))

    def stream_sync(self, filter_obj: VGKGFilter) -> Iterator[VGKGRecord]:
        """Synchronous wrapper for stream().

        Yields VGKG records from the async stream() method in a blocking manner.
        This is a convenience method for synchronous code, but async methods are
        preferred when possible.

        Args:
            filter_obj: Filter with date range and optional constraints

        Yields:
            VGKGRecord: Individual VGKG records matching the filter criteria

        Raises:
            RuntimeError: If called from within a running event loop.
            RateLimitError: If rate limited and retries exhausted.
            APIError: If downloads fail.
            DataError: If file parsing fails.

        Note:
            This method cannot be called from within an async context (e.g., inside
            an async function or running event loop). Doing so will raise RuntimeError.
            Use the async stream() method instead. This method creates its own event
            loop internally.

        Example:
            >>> filter_obj = VGKGFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     min_label_confidence=0.9,
            ... )
            >>> for record in endpoint.stream_sync(filter_obj):
            ...     print(f"{record.image_url}: {len(record.labels)} labels")
        """
        # Manual event loop management is required for async generators.
        # Unlike query_sync() which uses asyncio.run() for a single coroutine,
        # stream_sync() must iterate through an async generator step-by-step.
        # asyncio.run() cannot handle async generators - it expects a coroutine
        # that returns a value, not one that yields multiple values.

        # Check if we're already in an async context - this would cause issues
        try:
            asyncio.get_running_loop()
            has_running_loop = True
        except RuntimeError:
            has_running_loop = False

        if has_running_loop:
            msg = "stream_sync() cannot be called from a running event loop. Use stream() instead."
            raise RuntimeError(msg)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async_gen = self.stream(filter_obj)
            while True:
                try:
                    record = loop.run_until_complete(async_gen.__anext__())
                    yield record
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

    def get_latest_sync(self) -> list[VGKGRecord]:
        """Synchronous wrapper for get_latest().

        Runs the async get_latest() method in a new event loop. This is a convenience
        method for synchronous code, but async methods are preferred when possible.

        Returns:
            List of VGKGRecord from the most recent update.

        Raises:
            APIError: If fetching or parsing fails.

        Example:
            >>> latest = endpoint.get_latest_sync()
            >>> if latest:
            ...     print(f"Latest update: {latest[0].date}")
            ...     print(f"Total records: {len(latest)}")
        """
        return asyncio.run(self.get_latest())
