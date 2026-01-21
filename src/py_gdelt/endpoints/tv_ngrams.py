"""TV NGrams endpoint for Television broadcast word frequency data.

TV NGrams provides word frequency analysis from TV closed captions,
available for stations like CNN, MSNBC, Fox News, etc.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from py_gdelt.config import GDELTSettings
from py_gdelt.models.common import FetchResult
from py_gdelt.models.ngrams import BroadcastNGramRecord, BroadcastSource
from py_gdelt.parsers.broadcast_ngrams import BroadcastNGramsParser
from py_gdelt.sources.files import FileSource


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from py_gdelt.filters import BroadcastNGramsFilter


__all__ = ["TVNGramsEndpoint"]

logger = logging.getLogger(__name__)


class TVNGramsEndpoint:
    """Endpoint for TV NGrams data (Television word frequency).

    TV NGrams provides word frequency analysis from TV closed captions.
    Data is organized by station (CNN, MSNBC, Fox News, etc.) and hour.

    Args:
        settings: Configuration settings. If None, uses defaults.
        file_source: Optional shared FileSource. If None, creates owned instance.
                    When provided, the source lifecycle is managed externally.

    Attributes:
        BASE_URL: Base URL for TV NGrams data files.

    Example:
        >>> from py_gdelt.filters import BroadcastNGramsFilter, DateRange
        >>> from datetime import date
        >>> async with TVNGramsEndpoint() as endpoint:
        ...     filter = BroadcastNGramsFilter(
        ...         date_range=DateRange(start=date(2024, 1, 1)),
        ...         station="CNN",
        ...         ngram_size=1,
        ...     )
        ...     async for record in endpoint.stream(filter):
        ...         print(record.ngram, record.count)
    """

    BASE_URL = "http://data.gdeltproject.org/gdeltv3/iatv/ngramsv2/"

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

    async def __aenter__(self) -> TVNGramsEndpoint:
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
        """Query TV NGrams data and return all results.

        Fetches all TV NGrams records matching the filter criteria and returns them
        as a FetchResult. This method collects all records in memory before returning,
        so use stream() for large result sets to avoid memory issues.

        Args:
            filter_obj: Filter with date range, station (required), and ngram size

        Returns:
            FetchResult containing list of BroadcastNGramRecord instances

        Raises:
            ValueError: If station filter is not provided
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> from datetime import date
            >>> from py_gdelt.filters import BroadcastNGramsFilter, DateRange
            >>> filter_obj = BroadcastNGramsFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     station="CNN",
            ...     ngram_size=1,
            ... )
            >>> result = await endpoint.query(filter_obj)
            >>> print(f"Found {len(result)} ngram records from CNN")
        """
        # Stream all records and collect them
        records: list[BroadcastNGramRecord] = [record async for record in self.stream(filter_obj)]

        logger.info("Collected %d TV NGrams records from query", len(records))

        # Return FetchResult (no failed tracking for now - FileSource handles errors)
        return FetchResult(data=records, failed=[])

    async def get_latest(self, station: str, ngram_size: int = 1) -> list[BroadcastNGramRecord]:
        """Get the most recent TV NGrams records for a station.

        Fetches the most recent day's data for the specified station.
        Tries today first, then falls back to yesterday if no data is available.

        Args:
            station: TV station code (e.g., "CNN", "MSNBC", "FOXNEWS").
            ngram_size: Size of ngrams to retrieve (1, 2, or 3). Defaults to 1.

        Returns:
            List of BroadcastNGramRecord from the most recent available data.

        Raises:
            ValueError: If station is empty.

        Example:
            >>> async with TVNGramsEndpoint() as endpoint:
            ...     latest = await endpoint.get_latest("CNN")
            ...     if latest:
            ...         print(f"Top ngram: {latest[0].ngram} ({latest[0].count})")
        """
        if not station:
            msg = "Station is required for TV NGrams get_latest()"
            raise ValueError(msg)

        station_upper = station.upper()
        ngram_type = f"{ngram_size}gram"
        records: list[BroadcastNGramRecord] = []

        # Try today first, then yesterday (data may have delay)
        for days_ago in range(3):
            target_date = datetime.now(tz=UTC).date() - timedelta(days=days_ago)
            date_str = target_date.strftime("%Y%m%d")
            url = f"{self.BASE_URL}{station_upper}.{date_str}.{ngram_type}.txt.gz"

            try:
                async for _url, data in self._file_source.stream_files([url]):
                    for raw_record in self._parser.parse(data):
                        try:
                            records.append(
                                BroadcastNGramRecord.from_raw(raw_record, BroadcastSource.TV)
                            )
                        except Exception as e:  # noqa: BLE001
                            logger.warning("Failed to parse TV NGrams record: %s", e)

                if records:
                    logger.info(
                        "Retrieved %d TV NGrams records for %s from %s",
                        len(records),
                        station_upper,
                        target_date,
                    )
                    return records

            except Exception as e:  # noqa: BLE001
                logger.debug("No TV NGrams data for %s on %s: %s", station_upper, target_date, e)

        logger.warning("No recent TV NGrams data found for station %s", station_upper)
        return records

    def get_latest_sync(self, station: str, ngram_size: int = 1) -> list[BroadcastNGramRecord]:
        """Synchronous wrapper for get_latest().

        Args:
            station: TV station code (e.g., "CNN", "MSNBC", "FOXNEWS").
            ngram_size: Size of ngrams to retrieve (1, 2, or 3). Defaults to 1.

        Returns:
            List of BroadcastNGramRecord from the most recent available data.
        """
        return asyncio.run(self.get_latest(station, ngram_size))

    def stream(
        self,
        filter_obj: BroadcastNGramsFilter,
    ) -> AsyncIterator[BroadcastNGramRecord]:
        """Stream TV NGrams data matching the filter.

        Validation happens immediately when this method is called, before any
        iteration begins. This ensures fail-fast behavior for invalid inputs.

        Args:
            filter_obj: Filter specifying date range, station, and ngram size.
                       Station is required for TV NGrams queries.

        Returns:
            AsyncIterator yielding BroadcastNGramRecord instances.

        Raises:
            ValueError: If station filter is not provided.

        Note:
            TV NGrams files are organized by station and date.
            Each file contains word frequencies for a specific station/day.

        Example:
            >>> filter = BroadcastNGramsFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     station="CNN",
            ... )
            >>> async for record in endpoint.stream(filter):
            ...     print(record.station, record.ngram, record.count)
        """
        # Validate early - this runs immediately when stream() is called,
        # not when iteration begins, ensuring fail-fast behavior
        if not filter_obj.station:
            msg = "Station filter is required for TV NGrams queries"
            raise ValueError(msg)

        urls = self._build_urls(filter_obj)

        # Return the async generator - validation already complete
        return self._stream_records(urls)

    async def _stream_records(self, urls: list[str]) -> AsyncIterator[BroadcastNGramRecord]:
        """Stream parsed records from URLs.

        Args:
            urls: List of URLs to fetch and parse.

        Yields:
            BroadcastNGramRecord: Parsed TV NGram records.
        """
        async for _url, data in self._file_source.stream_files(urls):
            for raw in self._parser.parse(data):
                try:
                    yield BroadcastNGramRecord.from_raw(raw, BroadcastSource.TV)
                except Exception as e:  # noqa: BLE001
                    logger.warning("Failed to parse TV NGram record: %s - Skipping", e)
                    continue

    def _build_urls(self, filter_obj: BroadcastNGramsFilter) -> list[str]:
        """Build file URLs for the filter parameters.

        Args:
            filter_obj: Filter with date range, station, and ngram size.
                       Station is guaranteed to be present (validated in stream()).

        Returns:
            List of URLs to download.

        Raises:
            ValueError: If station is not set (defensive check).

        Note:
            Unlike RadioNGramsEndpoint, URL validation is not needed here because
            URLs are constructed entirely from trusted internal constants (BASE_URL)
            and validated filter parameters (station from filter). No external input
            influences the URL structure, eliminating SSRF risk.
        """
        # Defensive check - station should already be validated in stream()
        if not filter_obj.station:
            msg = "Station filter is required for TV NGrams queries"
            raise ValueError(msg)

        urls: list[str] = []
        ngram_type = f"{filter_obj.ngram_size}gram"

        # Generate URLs for each day in range
        current = filter_obj.date_range.start
        end = filter_obj.date_range.end or filter_obj.date_range.start

        while current <= end:
            date_str = current.strftime("%Y%m%d")

            # Format: {BASE_URL}{STATION}.{YYYYMMDD}.{ngram_type}.txt.gz
            # Example: http://data.gdeltproject.org/gdeltv3/iatv/ngramsv2/CNN.20240101.1gram.txt.gz
            url = f"{self.BASE_URL}{filter_obj.station.upper()}.{date_str}.{ngram_type}.txt.gz"
            urls.append(url)

            current += timedelta(days=1)

        logger.info(
            "Built %d TV NGrams URLs for station=%s, ngram_size=%d, date_range=%s-%s",
            len(urls),
            filter_obj.station,
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
            filter_obj: Filter with date range, station (required), and ngram size

        Returns:
            FetchResult containing list of BroadcastNGramRecord instances

        Raises:
            ValueError: If station filter is not provided
            APIError: If downloads fail
            DataError: If file parsing fails

        Example:
            >>> from datetime import date
            >>> from py_gdelt.filters import BroadcastNGramsFilter, DateRange
            >>> filter_obj = BroadcastNGramsFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     station="CNN",
            ...     ngram_size=1,
            ... )
            >>> result = endpoint.query_sync(filter_obj)
            >>> print(f"Found {len(result)} records")
        """
        return asyncio.run(self.query(filter_obj))

    def stream_sync(self, filter_obj: BroadcastNGramsFilter) -> Iterator[BroadcastNGramRecord]:
        """Synchronous wrapper for stream().

        Yields TV NGrams records from the async stream() method in a blocking manner.
        This is a convenience method for synchronous code, but async methods are
        preferred when possible.

        Args:
            filter_obj: Filter with date range, station (required), and ngram size

        Yields:
            BroadcastNGramRecord: Individual TV NGram records matching the filter criteria

        Raises:
            ValueError: If station filter is not provided
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
            ...     station="CNN",
            ...     ngram_size=2,
            ... )
            >>> for record in endpoint.stream_sync(filter_obj):
            ...     print(f"{record.ngram}: {record.count}")
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
