"""Radio NGrams endpoint for Radio broadcast word frequency data.

Radio NGrams provides word frequency analysis from radio transcripts,
with additional show-level metadata not available in TV NGrams.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from pydantic import ValidationError

from py_gdelt.config import GDELTSettings
from py_gdelt.models.common import FetchResult
from py_gdelt.models.ngrams import BroadcastNGramRecord, BroadcastSource
from py_gdelt.parsers.broadcast_ngrams import BroadcastNGramsParser
from py_gdelt.sources.files import FileSource


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from py_gdelt.filters import BroadcastNGramsFilter


__all__ = ["RadioNGramsEndpoint"]

logger = logging.getLogger(__name__)


class RadioNGramsEndpoint:
    """Endpoint for Radio NGrams data (Radio word frequency).

    Radio NGrams provides word frequency analysis from radio transcripts.
    Unlike TV NGrams, Radio includes show-level metadata (SHOW column).

    Args:
        settings: Configuration settings. If None, uses defaults.
        file_source: Optional shared FileSource. If None, creates owned instance.
                    When provided, the source lifecycle is managed externally.

    Attributes:
        BASE_URL: Base URL for Radio NGrams inventory files.

    Example:
        >>> from py_gdelt.filters import BroadcastNGramsFilter, DateRange
        >>> from datetime import date
        >>> async with RadioNGramsEndpoint() as endpoint:
        ...     filter = BroadcastNGramsFilter(
        ...         date_range=DateRange(start=date(2024, 1, 1)),
        ...         station="KQED",
        ...         ngram_size=1,
        ...     )
        ...     async for record in endpoint.stream(filter):
        ...         print(record.ngram, record.count, record.show)
    """

    BASE_URL = "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/"

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

        self._parser = BroadcastNGramsParser()

    async def close(self) -> None:
        """Close resources if we own them.

        Only closes resources that were created by this instance.
        Shared resources are not closed to allow reuse.
        """
        if self._owns_sources:
            # FileSource uses context manager protocol, manually call __aexit__
            await self._file_source.__aexit__(None, None, None)

    async def __aenter__(self) -> RadioNGramsEndpoint:
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

    async def query(self, filter_obj: BroadcastNGramsFilter) -> FetchResult[BroadcastNGramRecord]:
        """Query Radio NGrams data and return all results.

        Fetches all Radio NGrams records matching the filter criteria and returns them
        as a FetchResult. This method collects all records in memory before returning,
        so use stream() for large result sets to avoid memory issues.

        Args:
            filter_obj: Filter with date range, optional station, show, and ngram size

        Returns:
            FetchResult containing list of BroadcastNGramRecord instances

        Raises:
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> from datetime import date
            >>> from py_gdelt.filters import BroadcastNGramsFilter, DateRange
            >>> filter_obj = BroadcastNGramsFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     station="KQED",
            ...     ngram_size=1,
            ... )
            >>> result = await endpoint.query(filter_obj)
            >>> print(f"Found {len(result)} ngram records from KQED")
        """
        # Stream all records and collect them
        records: list[BroadcastNGramRecord] = [record async for record in self.stream(filter_obj)]

        logger.info("Collected %d Radio NGrams records from query", len(records))

        # Return FetchResult (no failed tracking for now - FileSource handles errors)
        return FetchResult(data=records, failed=[])

    async def get_latest(
        self,
        station: str | None = None,
        ngram_size: int = 1,
    ) -> list[BroadcastNGramRecord]:
        """Get the most recent Radio NGrams records.

        Fetches the most recent day's inventory and returns records from the
        latest available files. Tries today first, then falls back to previous
        days if no data is available.

        Args:
            station: Optional station filter (e.g., "KQED", "NPR"). If None,
                    returns records from all stations.
            ngram_size: Size of ngrams to retrieve (1, 2, or 3). Defaults to 1.

        Returns:
            List of BroadcastNGramRecord from the most recent available data.

        Example:
            >>> async with RadioNGramsEndpoint() as endpoint:
            ...     # Get latest from all stations
            ...     latest = await endpoint.get_latest()
            ...     # Or filter by station
            ...     latest = await endpoint.get_latest(station="NPR")
        """
        ngram_type = f"{ngram_size}gram"
        records: list[BroadcastNGramRecord] = []

        # Try today first, then previous days (data may have delay)
        for days_ago in range(3):
            target_date = datetime.now(tz=UTC).date() - timedelta(days=days_ago)
            date_str = target_date.strftime("%Y%m%d")
            inventory_url = f"{self.BASE_URL}{date_str}.txt"

            try:
                # Fetch inventory file
                response = await self._file_source.client.get(inventory_url)
                response.raise_for_status()

                # Parse inventory for matching files
                urls: list[str] = []
                for line in response.text.strip().split("\n"):
                    file_url = line.strip()
                    if not file_url:
                        continue

                    # Validate URL (security check)
                    if not file_url.startswith(self.BASE_URL):
                        continue
                    try:
                        self._validate_url(file_url)
                    except ValueError:
                        continue

                    # Filter by station if specified
                    if station and station.upper() not in file_url.upper():
                        continue

                    # Filter by ngram size
                    if ngram_type not in file_url:
                        continue

                    urls.append(file_url)

                if not urls:
                    logger.debug("No matching files in inventory for %s", target_date)
                    continue

                # Download and parse files
                async for _url, data in self._file_source.stream_files(
                    urls[:10]
                ):  # Limit for get_latest
                    for raw in self._parser.parse(data):
                        try:
                            records.append(
                                BroadcastNGramRecord.from_raw(raw, BroadcastSource.RADIO)
                            )
                        except (ValueError, ValidationError) as e:
                            logger.warning("Failed to parse Radio NGrams record: %s", e)

                if records:
                    logger.info(
                        "Retrieved %d Radio NGrams records from %s (station=%s)",
                        len(records),
                        target_date,
                        station or "ALL",
                    )
                    return records

            except Exception as e:  # noqa: BLE001
                logger.debug("No Radio NGrams inventory for %s: %s", target_date, e)

        logger.warning("No recent Radio NGrams data found (station=%s)", station or "ALL")
        return records

    def get_latest_sync(
        self,
        station: str | None = None,
        ngram_size: int = 1,
    ) -> list[BroadcastNGramRecord]:
        """Synchronous wrapper for get_latest().

        Args:
            station: Optional station filter.
            ngram_size: Size of ngrams to retrieve (1, 2, or 3). Defaults to 1.

        Returns:
            List of BroadcastNGramRecord from the most recent available data.
        """
        return asyncio.run(self.get_latest(station, ngram_size))

    async def stream(
        self,
        filter_obj: BroadcastNGramsFilter,
    ) -> AsyncIterator[BroadcastNGramRecord]:
        """Stream Radio NGrams data matching the filter.

        Args:
            filter_obj: Filter specifying date range, station, show, and ngram size.

        Yields:
            BroadcastNGramRecord: Parsed Radio NGram records.

        Note:
            Radio NGrams uses daily inventory files (YYYYMMDD.txt) listing
            available data files for that day. Files are filtered by station
            and show if specified.

        Example:
            >>> filter = BroadcastNGramsFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     station="KQED",
            ...     show="Morning Edition",
            ... )
            >>> async for record in endpoint.stream(filter):
            ...     print(record.show, record.ngram, record.count)
        """
        urls = await self._build_urls(filter_obj)

        async for _url, data in self._file_source.stream_files(urls):
            for raw in self._parser.parse(data):
                # Apply show filter if specified
                if filter_obj.show and raw.show != filter_obj.show:
                    continue
                try:
                    yield BroadcastNGramRecord.from_raw(raw, BroadcastSource.RADIO)
                except (ValueError, ValidationError) as e:
                    logger.warning("Failed to parse Radio NGram record: %s - Skipping", e)
                    continue

    def _validate_url(self, url: str) -> None:
        """Validate URL is well-formed and points to expected GDELT domain.

        Args:
            url: The URL to validate.

        Raises:
            ValueError: If the URL is malformed or does not point to the expected GDELT domain.
        """
        parsed = urlparse(url)
        if parsed.scheme != "http":
            msg = f"Invalid URL scheme '{parsed.scheme}', expected 'http': {url}"
            raise ValueError(msg)
        # Check for exact domain or subdomain of gdeltproject.org
        # Must end with "gdeltproject.org" and either be exactly that or have "." before it
        netloc = parsed.netloc
        if not (netloc == "gdeltproject.org" or netloc.endswith(".gdeltproject.org")):
            msg = f"Invalid URL host '{netloc}', expected 'gdeltproject.org': {url}"
            raise ValueError(msg)
        if not parsed.path:
            msg = f"Invalid URL with empty path: {url}"
            raise ValueError(msg)

    async def _build_urls(self, filter_obj: BroadcastNGramsFilter) -> list[str]:
        """Build file URLs by fetching daily inventory files.

        Radio NGrams uses inventory files that list available data files for each day.
        This method fetches these inventory files and extracts URLs matching the filter.

        Args:
            filter_obj: Filter with date range, station, and ngram size.

        Returns:
            List of URLs to download.

        Note:
            Station filter is optional for Radio NGrams. If not specified,
            all stations will be included.
        """
        urls: list[str] = []
        ngram_type = f"{filter_obj.ngram_size}gram"

        # Generate inventory URLs for each day in range
        current = filter_obj.date_range.start
        end = filter_obj.date_range.end or filter_obj.date_range.start

        while current <= end:
            date_str = current.strftime("%Y%m%d")
            inventory_url = f"{self.BASE_URL}{date_str}.txt"

            try:
                # Fetch inventory file
                response = await self._file_source.client.get(inventory_url)
                response.raise_for_status()

                # Parse inventory for matching files
                for line in response.text.strip().split("\n"):
                    file_url = line.strip()
                    if not file_url:
                        continue

                    # Validate URL to prevent SSRF attacks (prefix check)
                    if not file_url.startswith(self.BASE_URL):
                        logger.warning("Unexpected URL in inventory, skipping: %s", file_url)
                        continue

                    # Validate URL is well-formed and points to expected domain
                    try:
                        self._validate_url(file_url)
                    except ValueError as e:
                        logger.warning("Malformed URL in inventory, skipping: %s", e)
                        continue

                    # Filter by station if specified
                    if filter_obj.station and filter_obj.station.upper() not in file_url.upper():
                        continue

                    # Filter by ngram size
                    if ngram_type not in file_url:
                        continue

                    urls.append(file_url)

            except Exception as e:  # noqa: BLE001
                logger.warning(
                    "Failed to fetch Radio NGrams inventory for %s: %s",
                    date_str,
                    e,
                )

            current += timedelta(days=1)

        logger.info(
            "Built %d Radio NGrams URLs for station=%s, ngram_size=%d, date_range=%s-%s",
            len(urls),
            filter_obj.station or "ALL",
            filter_obj.ngram_size,
            filter_obj.date_range.start,
            end,
        )

        return urls

    def query_sync(self, filter_obj: BroadcastNGramsFilter) -> FetchResult[BroadcastNGramRecord]:
        """Synchronous wrapper for query().

        Runs the async query() method in a new event loop. This is a convenience
        method for synchronous code, but async methods are preferred when possible.

        Args:
            filter_obj: Filter with date range, optional station, show, and ngram size

        Returns:
            FetchResult containing list of BroadcastNGramRecord instances

        Raises:
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> from datetime import date
            >>> from py_gdelt.filters import BroadcastNGramsFilter, DateRange
            >>> filter_obj = BroadcastNGramsFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     station="KQED",
            ...     ngram_size=1,
            ... )
            >>> result = endpoint.query_sync(filter_obj)
            >>> print(f"Found {len(result)} records")
        """
        return asyncio.run(self.query(filter_obj))

    def stream_sync(self, filter_obj: BroadcastNGramsFilter) -> Iterator[BroadcastNGramRecord]:
        """Synchronous wrapper for stream().

        Yields Radio NGrams records from the async stream() method in a blocking manner.
        This is a convenience method for synchronous code, but async methods are
        preferred when possible.

        Args:
            filter_obj: Filter with date range, optional station, show, and ngram size

        Yields:
            BroadcastNGramRecord: Individual Radio NGram records matching the filter criteria

        Raises:
            APIError: If downloads fail
            DataError: If file parsing fails

        Note:
            Do not call this method from within an async context (e.g., inside
            an async function or running event loop). Use the async stream()
            method instead. This method creates its own event loop internally.

        Example:
            >>> from datetime import date
            >>> from py_gdelt.filters import BroadcastNGramsFilter, DateRange
            >>> filter_obj = BroadcastNGramsFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     station="KQED",
            ...     show="Morning Edition",
            ... )
            >>> for record in endpoint.stream_sync(filter_obj):
            ...     print(f"{record.show} - {record.ngram}: {record.count}")
        """
        # Manual event loop management is required for async generators.
        # Unlike query_sync() which uses asyncio.run() for a single coroutine,
        # stream_sync() must iterate through an async generator step-by-step.
        # asyncio.run() cannot handle async generators - it expects a coroutine
        # that returns a value, not one that yields multiple values.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Run the async generator and yield results
            async_gen = self.stream(filter_obj)
            while True:
                try:
                    record = loop.run_until_complete(async_gen.__anext__())
                    yield record
                except StopAsyncIteration:
                    break
        finally:
            loop.close()
