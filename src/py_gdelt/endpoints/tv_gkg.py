"""TV-GKG endpoint for Television Global Knowledge Graph data.

TV-GKG provides GKG 2.0 annotations over TV closed captions from Internet Archive's
Television News Archive. Data has a 48-hour embargo before becoming available.
"""

from __future__ import annotations

import asyncio
import logging
import warnings
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Final

import httpx

from py_gdelt.config import GDELTSettings
from py_gdelt.models.common import FetchResult
from py_gdelt.models.gkg import TVGKGRecord
from py_gdelt.parsers.gkg import GKGParser
from py_gdelt.sources.files import FileSource


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from py_gdelt.filters import TVGKGFilter


__all__ = ["TVGKGEndpoint"]

logger = logging.getLogger(__name__)


TV_GKG_LAST_UPDATE_URL: Final[str] = (
    "http://data.gdeltproject.org/gdeltv2_iatelevision/lastupdate.txt"
)
TV_GKG_BASE_URL: Final[str] = "http://data.gdeltproject.org/gdeltv2_iatelevision/"

EMBARGO_HOURS: Final[int] = 48


class TVGKGEndpoint:
    """Endpoint for TV-GKG (Television Global Knowledge Graph) data.

    TV-GKG provides GKG 2.0 annotations over TV closed captions from the
    Internet Archive's Television News Archive. This includes themes, persons,
    organizations, locations, and tone extracted from TV broadcasts.

    Important:
        TV-GKG data has a 48-hour embargo. Requesting data newer than 48 hours
        will emit a warning and likely return no results.

    Special Features:
        - Timecode mappings: Maps character offsets to video timestamps
        - Station filtering: Filter by TV station (CNN, MSNBC, etc.)
        - Compatible with standard GKG parser (27 columns)

    Args:
        settings: Configuration settings. If None, uses defaults.
        file_source: Optional shared FileSource. If None, creates owned instance.
                    When provided, the source lifecycle is managed externally.

    Attributes:
        BASE_URL: Base URL for TV-GKG data files.
        EMBARGO_HOURS: Hours of embargo before data is available (48).

    Example:
        >>> from datetime import date
        >>> from py_gdelt.filters import TVGKGFilter, DateRange
        >>>
        >>> async def main():
        ...     async with TVGKGEndpoint() as endpoint:
        ...         filter_obj = TVGKGFilter(
        ...             date_range=DateRange(start=date(2024, 1, 1)),
        ...             station="CNN",
        ...         )
        ...         async for record in endpoint.stream(filter_obj):
        ...             print(record.gkg_record_id, record.timecode_mappings)
    """

    BASE_URL = TV_GKG_BASE_URL
    EMBARGO_HOURS = EMBARGO_HOURS

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

        self._client = self._create_client()
        self._owns_client = True

        self._parser = GKGParser()

        logger.debug("TVGKGEndpoint initialized")

    def _create_client(self) -> httpx.AsyncClient:
        """Create a new HTTP client with proper configuration.

        Returns:
            Configured httpx.AsyncClient with timeouts and redirect following.
        """
        return httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,
                read=30.0,
                write=10.0,
                pool=5.0,
            ),
            follow_redirects=True,
        )

    async def close(self) -> None:
        """Close resources if we own them.

        Only closes resources that were created by this instance.
        Shared resources are not closed to allow reuse.
        """
        if self._owns_client and self._client is not None:
            await self._client.aclose()

        if self._owns_sources:
            await self._file_source.__aexit__(None, None, None)

    async def __aenter__(self) -> TVGKGEndpoint:
        """Async context manager entry.

        Returns:
            Self for use in async with statement.
        """
        # Ensure FileSource is initialized
        if self._owns_sources:
            await self._file_source.__aenter__()
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit.

        Args:
            *args: Exception info (unused, but required by protocol).
        """
        await self.close()

    async def query(self, filter_obj: TVGKGFilter) -> FetchResult[TVGKGRecord]:
        """Query TV-GKG data and return all results.

        Fetches all TV-GKG records matching the filter criteria and returns them
        as a FetchResult. This method collects all records in memory before returning,
        so use stream() for large result sets to avoid memory issues.

        Args:
            filter_obj: Filter with date range, themes, and station constraints

        Returns:
            FetchResult containing list of TVGKGRecord instances and any failed requests

        Raises:
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> from datetime import date
            >>> from py_gdelt.filters import TVGKGFilter, DateRange
            >>> filter_obj = TVGKGFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     station="CNN",
            ... )
            >>> result = await endpoint.query(filter_obj)
            >>> print(f"Found {len(result)} records from CNN")
        """
        # Stream all records and collect them
        records: list[TVGKGRecord] = [record async for record in self.stream(filter_obj)]

        logger.info("Collected %d TV-GKG records from query", len(records))

        # Return FetchResult (no failed tracking for now - FileSource handles errors)
        return FetchResult(data=records, failed=[])

    async def stream(
        self,
        filter_obj: TVGKGFilter,
    ) -> AsyncIterator[TVGKGRecord]:
        """Stream TV-GKG data matching the filter.

        Args:
            filter_obj: Filter specifying date range, themes, and station.

        Yields:
            TVGKGRecord: Parsed TV-GKG records with timecode mappings.

        Warns:
            UserWarning: If date range is within the 48-hour embargo period.

        Note:
            TV-GKG uses GKG 2.0 format (27 columns). The timecode mappings
            are extracted from the CHARTIMECODEOFFSETTOC field in extras.
        """
        self._check_embargo(filter_obj)

        urls = self._build_urls(filter_obj)

        async for _url, data in self._file_source.stream_files(urls):
            for raw in self._parser.parse(data):
                try:
                    record = TVGKGRecord.from_raw(raw)
                except Exception as e:  # noqa: BLE001
                    logger.warning("Failed to parse TV-GKG record: %s - Skipping", e)
                    continue

                # Apply client-side filtering
                if filter_obj.station:
                    station_upper = filter_obj.station.upper()
                    if station_upper not in record.source_identifier.upper():
                        continue

                if filter_obj.themes:
                    record_themes_lower = [t.lower() for t in record.themes]
                    if not any(t.lower() in record_themes_lower for t in filter_obj.themes):
                        continue

                yield record

    def _check_embargo(self, filter_obj: TVGKGFilter) -> None:
        """Check if date range is within embargo period and warn.

        Args:
            filter_obj: Filter with date range to check.
        """
        now = datetime.now(UTC)
        embargo_cutoff = now - timedelta(hours=EMBARGO_HOURS)

        end_date = filter_obj.date_range.end or filter_obj.date_range.start
        end_datetime = datetime.combine(end_date, datetime.max.time(), tzinfo=UTC)

        if end_datetime > embargo_cutoff:
            warnings.warn(
                f"TV-GKG has a {EMBARGO_HOURS}-hour embargo. "
                f"Data after {embargo_cutoff.strftime('%Y-%m-%d %H:%M')} UTC "
                f"may not be available yet.",
                UserWarning,
                stacklevel=3,
            )

    def _build_urls(self, filter_obj: TVGKGFilter) -> list[str]:
        """Build file URLs for the filter parameters.

        TV-GKG files are named: YYYYMMDDHHMMSS.gkg.csv.gz
        Files are generated every 15 minutes.

        Args:
            filter_obj: Filter with date range and optional station.

        Returns:
            List of URLs to download.
        """
        urls: list[str] = []

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
            url = f"{self.BASE_URL}{timestamp}.gkg.csv.gz"
            urls.append(url)
            current += delta

        logger.debug(
            "Generated %d TV-GKG URLs for date range %s to %s",
            len(urls),
            start,
            end,
        )
        return urls

    async def get_latest(self) -> list[TVGKGRecord]:
        """Get the most recent TV-GKG records (respecting embargo).

        Fetches the lastupdate.txt file to find the most recent data file,
        then parses and returns all records from that file.

        Returns:
            List of TVGKGRecord from the most recent available update.

        Note:
            Due to the 48-hour embargo, "latest" means the most recent
            data that has cleared the embargo period.
        """
        response = await self._client.get(TV_GKG_LAST_UPDATE_URL)
        response.raise_for_status()

        gkg_url = None
        for line in response.text.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 3 and ".gkg." in parts[2].lower():
                gkg_url = parts[2]
                break

        if not gkg_url:
            logger.warning("No TV-GKG file found in lastupdate.txt")
            return []

        records: list[TVGKGRecord] = []
        async for _url, data in self._file_source.stream_files([gkg_url]):
            for raw in self._parser.parse(data):
                try:
                    records.append(TVGKGRecord.from_raw(raw))
                except Exception as e:  # noqa: BLE001
                    logger.warning("Failed to parse TV-GKG record: %s - Skipping", e)

        return records

    def query_sync(self, filter_obj: TVGKGFilter) -> FetchResult[TVGKGRecord]:
        """Synchronous wrapper for query().

        Runs the async query() method in a new event loop. This is a convenience
        method for synchronous code, but async methods are preferred when possible.

        Args:
            filter_obj: Filter with date range, themes, and station constraints

        Returns:
            FetchResult containing list of TVGKGRecord instances

        Raises:
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> from datetime import date
            >>> from py_gdelt.filters import TVGKGFilter, DateRange
            >>> filter_obj = TVGKGFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     station="CNN",
            ... )
            >>> result = endpoint.query_sync(filter_obj)
            >>> print(f"Found {len(result)} records")
        """
        return asyncio.run(self.query(filter_obj))

    def stream_sync(self, filter_obj: TVGKGFilter) -> Iterator[TVGKGRecord]:
        """Synchronous wrapper for stream().

        Yields TV-GKG records from the async stream() method in a blocking manner.
        This is a convenience method for synchronous code, but async methods are
        preferred when possible.

        Args:
            filter_obj: Filter with date range, themes, and station constraints

        Yields:
            TVGKGRecord: Individual TV-GKG records matching the filter criteria

        Raises:
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> from datetime import date
            >>> from py_gdelt.filters import TVGKGFilter, DateRange
            >>> filter_obj = TVGKGFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     station="MSNBC",
            ... )
            >>> for record in endpoint.stream_sync(filter_obj):
            ...     print(f"{record.gkg_record_id}: {record.themes}")
        """
        # Create a new event loop for the sync wrapper
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

    def get_latest_sync(self) -> list[TVGKGRecord]:
        """Synchronous wrapper for get_latest().

        Runs the async get_latest() method in a new event loop. This is a convenience
        method for synchronous code, but async methods are preferred when possible.

        Returns:
            List of TVGKGRecord from the most recent available update.

        Raises:
            APIError: If fetching or parsing fails.

        Note:
            Due to the 48-hour embargo, "latest" means the most recent
            data that has cleared the embargo period.

        Example:
            >>> latest = endpoint.get_latest_sync()
            >>> if latest:
            ...     print(f"Latest update has {len(latest)} records")
        """
        return asyncio.run(self.get_latest())
