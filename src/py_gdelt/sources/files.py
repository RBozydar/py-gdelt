"""FileSource for downloading and extracting GDELT data files.

This module provides functionality for downloading GDELT data files directly from
data.gdeltproject.org. It handles:
- Master file list retrieval and parsing
- File URL generation for date ranges
- Concurrent download with bounded concurrency
- ZIP/GZ decompression
- Intelligent caching (historical files cached indefinitely, recent files TTL-based)
"""

from __future__ import annotations

import asyncio
import gzip
import io
import logging
import re
import zipfile
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Final, Literal, get_args


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterable

import httpx

from py_gdelt.cache import Cache
from py_gdelt.config import GDELTSettings
from py_gdelt.exceptions import APIError, APIUnavailableError, DataError
from py_gdelt.utils.dates import parse_gdelt_datetime


__all__ = ["CORE_FILE_TYPES", "FileSource", "FileType", "GraphFileType"]

logger = logging.getLogger(__name__)

# GDELT file list URLs
# NOTE: data.gdeltproject.org only supports HTTP (SSL cert is for *.storage.googleapis.com)
# See: https://blog.gdeltproject.org/https-now-available-for-selected-gdelt-apis-and-services/
MASTER_FILE_LIST_URL: Final[str] = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"
TRANSLATION_FILE_LIST_URL: Final[str] = (
    "http://data.gdeltproject.org/gdeltv2/masterfilelist-translation.txt"
)
LAST_UPDATE_URL: Final[str] = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

# Decompression limit to prevent gzip bombs
MAX_DECOMPRESSED_SIZE: Final[int] = 500 * 1024 * 1024  # 500MB limit

# File type patterns
FILE_TYPE_PATTERNS: Final[dict[str, str]] = {
    "export": ".export.CSV.zip",
    "mentions": ".mentions.CSV.zip",
    "gkg": ".gkg.csv.zip",
    "ngrams": ".webngrams.json.gz",
    "gqg": ".gqg.json.gz",
    "geg": ".geg.json.gz",
    "gfg": ".gfg.csv.gz",
    "ggg": ".ggg.json.gz",
    "gemg": ".gemg.json.gz",
    "gal": ".gal.json.gz",
}

# Type alias for file types
FileType = Literal["export", "mentions", "gkg", "ngrams", "gqg", "geg", "gfg", "ggg", "gemg", "gal"]
GraphFileType = Literal["gqg", "geg", "gfg", "ggg", "gemg", "gal"]

# Tuple of graph file types derived from GraphFileType Literal
GRAPH_FILE_TYPES: Final[tuple[str, ...]] = get_args(GraphFileType)

# Core file types covered by the master file list (v2 only)
CORE_FILE_TYPES: Final[frozenset[str]] = frozenset({"export", "mentions", "gkg"})


class FileSource:
    """Downloads and extracts GDELT data files.

    This class provides async methods for downloading GDELT data files with:
    - Concurrent downloads with sliding window for bounded memory usage
    - Automatic decompression (ZIP/GZ)
    - Intelligent caching (historical files permanent, recent files TTL)
    - Progress tracking and error handling

    Args:
        settings: GDELT settings (creates default if None)
        client: HTTP client (creates new one if None, caller owns lifecycle)
        cache: Cache manager (creates new one if None)

    Example:
        >>> async with httpx.AsyncClient() as client:
        ...     source = FileSource(client=client)
        ...     urls = await source.get_files_for_date_range(
        ...         start_date=datetime(2024, 1, 1),
        ...         end_date=datetime(2024, 1, 2),
        ...         file_type="export"
        ...     )
        ...     async for url, data in source.stream_files(urls):
        ...         print(f"Downloaded {url}: {len(data)} bytes")
    """

    def __init__(
        self,
        settings: GDELTSettings | None = None,
        client: httpx.AsyncClient | None = None,
        cache: Cache | None = None,
    ) -> None:
        self.settings = settings or GDELTSettings()
        self._client = client
        self._owns_client = client is None
        self.cache = cache or Cache(
            cache_dir=self.settings.cache_dir,
            default_ttl=self.settings.cache_ttl,
        )

    async def __aenter__(self) -> FileSource:
        """Async context manager entry."""
        if self._owns_client:
            limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
            self._client = httpx.AsyncClient(limits=limits, timeout=self.settings.timeout)
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, raising if not initialized."""
        if self._client is None:
            err_msg = "FileSource not initialized. Use 'async with FileSource() as source:'"
            raise RuntimeError(err_msg)
        return self._client

    async def get_master_file_list(
        self,
        include_translation: bool = False,
    ) -> list[str]:
        """Fetch and parse master file list URLs.

        Args:
            include_translation: If True, also fetch translation files

        Returns:
            List of file URLs from master file list(s)

        Raises:
            APIError: If fetching or parsing fails
        """
        urls_to_fetch = [MASTER_FILE_LIST_URL]
        if include_translation:
            urls_to_fetch.append(TRANSLATION_FILE_LIST_URL)

        all_urls: list[str] = []

        for url in urls_to_fetch:
            try:
                # Check cache first (master lists have short TTL)
                cached_data = self.cache.get(url)

                if cached_data is not None:
                    logger.debug("Using cached master file list: %s", url)
                    content = cached_data.decode("utf-8")
                else:
                    logger.info("Fetching master file list: %s", url)
                    response = await self.client.get(url)
                    response.raise_for_status()

                    content = response.text

                    # Cache with configurable TTL for master lists
                    self.cache.set(
                        url,
                        content.encode("utf-8"),
                        ttl=self.settings.master_file_list_ttl,
                    )

                # Parse URLs from content (format: "size_bytes md5_hash url")
                file_urls: list[str] = []
                for line in content.splitlines():
                    parsed_url = self._parse_master_file_line(line)
                    if parsed_url is not None:
                        file_urls.append(parsed_url)
                all_urls.extend(file_urls)

                logger.debug("Found %d URLs in %s", len(file_urls), url)

            except httpx.HTTPStatusError as e:
                logger.error("HTTP error fetching master file list %s: %s", url, e)  # noqa: TRY400
                msg = f"Failed to fetch master file list: {e}"
                raise APIUnavailableError(msg) from e
            except httpx.RequestError as e:
                logger.error("Request error fetching master file list %s: %s", url, e)  # noqa: TRY400
                msg = f"Network error fetching master file list: {e}"
                raise APIError(msg) from e
            except UnicodeDecodeError as e:
                logger.error("Invalid encoding in master file list %s: %s", url, e)  # noqa: TRY400
                msg = f"Invalid encoding in master file list: {e}"
                raise DataError(msg) from e

        return all_urls

    async def get_files_for_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        file_type: FileType,
        include_translation: bool = False,
    ) -> list[str]:
        """Get file URLs for a date range.

        For core file types (export, mentions, gkg), filters the GDELT master
        file list to return only URLs whose embedded timestamp falls within the
        requested range. For graph and ngrams types, generates URLs from
        deterministic naming patterns.

        Args:
            start_date: Start of date range (inclusive).
            end_date: End of date range (inclusive).
            file_type: Type of files to get.
            include_translation: If True, include translation files.

        Returns:
            List of file URLs for the date range.

        Raises:
            ValueError: If date range is invalid or file_type unknown.
        """
        if start_date > end_date:
            err_msg = f"start_date ({start_date}) must be <= end_date ({end_date})"
            raise ValueError(err_msg)

        if file_type not in FILE_TYPE_PATTERNS:
            valid_types = ", ".join(FILE_TYPE_PATTERNS.keys())
            err_msg = f"Unknown file_type '{file_type}'. Valid types: {valid_types}"
            raise ValueError(err_msg)

        if file_type in CORE_FILE_TYPES:
            return await self._get_files_from_master_list(
                start_date,
                end_date,
                file_type,
                include_translation,
            )

        return self._generate_pattern_urls(
            start_date,
            end_date,
            file_type,
            include_translation,
        )

    def _generate_pattern_urls(
        self,
        start_date: datetime,
        end_date: datetime,
        file_type: FileType,
        include_translation: bool,
    ) -> list[str]:
        """Generate file URLs from deterministic naming patterns.

        Used for graph datasets and ngrams where URL patterns are predictable.

        Args:
            start_date: Start of date range (inclusive).
            end_date: End of date range (inclusive).
            file_type: Type of files to generate URLs for.
            include_translation: If True, include translation file URLs.

        Returns:
            List of generated file URLs.
        """
        pattern = FILE_TYPE_PATTERNS[file_type]
        urls: list[str] = []

        # GFG (Frontpage Graph) files are published hourly, unlike other datasets
        # which are published every 15 minutes. See GDELT documentation.
        delta = timedelta(hours=1) if file_type == "gfg" else timedelta(minutes=15)

        # Generate URLs for time intervals
        current = start_date

        while current <= end_date:
            # GFG is hourly - normalize minutes to 00
            if file_type == "gfg":
                # Round down to hour
                timestamp = current.strftime("%Y%m%d%H") + "0000"
            else:
                timestamp = current.strftime("%Y%m%d%H%M%S")

            # Build URL based on file type
            # Graph datasets and ngrams use gdeltv3
            if file_type == "ngrams" or file_type in GRAPH_FILE_TYPES:
                # Graph datasets have their own subdirectory
                if file_type == "ngrams":
                    url = f"http://data.gdeltproject.org/gdeltv3/webngrams/{timestamp}{pattern}"
                else:
                    url = f"http://data.gdeltproject.org/gdeltv3/{file_type}/{timestamp}{pattern}"
            else:
                url = f"http://data.gdeltproject.org/gdeltv2/{timestamp}{pattern}"

            urls.append(url)

            # Handle translation files (not supported for graph datasets)
            if include_translation and file_type != "ngrams" and file_type not in GRAPH_FILE_TYPES:
                trans_url = url.replace(pattern, f".translation{pattern}")
                urls.append(trans_url)

            current += delta

        logger.debug(
            "Generated %d URLs for date range %s to %s (type: %s)",
            len(urls),
            start_date,
            end_date,
            file_type,
        )

        return urls

    async def _get_files_from_master_list(
        self,
        start_date: datetime,
        end_date: datetime,
        file_type: FileType,
        include_translation: bool,
    ) -> list[str]:
        """Get file URLs by filtering the master list.

        Args:
            start_date: Start of date range (inclusive).
            end_date: End of date range (inclusive).
            file_type: Type of files to get.
            include_translation: If True, include translation files.

        Returns:
            Filtered list of URLs sorted by timestamp.
        """
        master_urls = await self.get_master_file_list()
        urls = self._filter_urls_by_type_and_range(
            master_urls,
            file_type,
            start_date,
            end_date,
        )

        if include_translation:
            trans_urls = await self.get_master_file_list(include_translation=True)
            trans_pattern = f".translation{FILE_TYPE_PATTERNS[file_type]}"
            trans_filtered = [
                u
                for u in self._filter_urls_by_type_and_range(
                    trans_urls,
                    file_type,
                    start_date,
                    end_date,
                )
                if trans_pattern in u
            ]
            urls.extend(trans_filtered)

        logger.debug(
            "Filtered %d URLs from master list for date range %s to %s (type: %s)",
            len(urls),
            start_date,
            end_date,
            file_type,
        )

        return urls

    async def download_file(self, url: str) -> bytes:
        """Download a file and return raw bytes.

        Args:
            url: URL to download

        Returns:
            Raw file content as bytes

        Raises:
            APIError: If download fails
        """
        # Check cache first
        cached_data = self.cache.get(url)
        if cached_data is not None:
            logger.debug("Cache hit for URL: %s", url)
            return cached_data

        # NOTE: We use HTTP (not HTTPS) for data.gdeltproject.org because their
        # SSL certificate is for *.storage.googleapis.com, causing hostname mismatch.
        # See: https://blog.gdeltproject.org/https-now-available-for-selected-gdelt-apis-and-services/
        try:
            logger.debug("Downloading: %s", url)
            response = await self.client.get(url)
            response.raise_for_status()

            content = response.content

            # Extract file date from URL for cache TTL decision
            file_date = self._extract_date_from_url(url)

            # Cache the raw data
            self.cache.set(url, content, file_date=file_date)

            logger.debug("Downloaded %d bytes from %s", len(content), url)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Missing files are normal (not all 15-min slots exist)
                logger.debug("File not found (404): %s", url)
                msg = f"File not found: {url}"
                raise APIError(msg) from e

            logger.error("HTTP error downloading %s: %s", url, e)  # noqa: TRY400
            msg = f"Failed to download file: {e}"
            raise APIUnavailableError(msg) from e

        except httpx.RequestError as e:
            logger.error("Request error downloading %s: %s", url, e)  # noqa: TRY400
            msg = f"Network error downloading file: {e}"
            raise APIError(msg) from e
        else:
            return content

    async def download_and_extract(self, url: str) -> bytes:
        """Download and extract ZIP/GZ file, return decompressed content.

        Args:
            url: URL to download (must be .zip or .gz)

        Returns:
            Decompressed file content

        Raises:
            APIError: If download fails
            DataError: If extraction fails
        """
        # Download compressed file
        compressed_data = await self.download_file(url)

        try:
            # Determine compression type from URL
            if url.endswith(".zip"):
                decompressed_data = self._extract_zip(compressed_data)
            elif url.endswith(".gz"):
                decompressed_data = self._extract_gzip(compressed_data)
            else:
                # Not compressed, return as-is
                logger.debug("File is not compressed: %s", url)
                return compressed_data

            logger.debug(
                "Extracted %d bytes from %d compressed bytes for %s",
                len(decompressed_data),
                len(compressed_data),
                url,
            )

        except (zipfile.BadZipFile, gzip.BadGzipFile) as e:
            logger.error("Invalid archive format for %s: %s", url, e)  # noqa: TRY400
            msg = f"Invalid archive format: {e}"
            raise DataError(msg) from e
        except Exception as e:
            logger.error("Unexpected error extracting %s: %s", url, e)  # noqa: TRY400
            msg = f"Failed to extract file: {e}"
            raise DataError(msg) from e
        else:
            return decompressed_data

    async def stream_files(
        self,
        urls: Iterable[str],
        *,
        max_concurrent: int | None = None,
    ) -> AsyncIterator[tuple[str, bytes]]:
        """Stream downloads with bounded memory via sliding window.

        Memory bounded to max_concurrent * max_file_size (~500MB default).
        Natural backpressure: downloads throttle to caller's consumption rate.

        Args:
            urls: Iterable of URLs to download
            max_concurrent: Override default concurrent download limit

        Yields:
            tuple[str, bytes]: Tuple of (url, decompressed_data) for each successful download

        Note:
            Failed downloads are logged but do not stop iteration.
            This is by design as GDELT files may have gaps.
        """
        limit = (
            max_concurrent if max_concurrent is not None else self.settings.max_concurrent_downloads
        )
        url_iter = iter(urls)
        pending: set[asyncio.Task[tuple[str, bytes] | None]] = set()

        def spawn() -> None:
            """Add one task from iterator if available."""
            if (url := next(url_iter, None)) is not None:
                pending.add(asyncio.create_task(self._safe_download_and_extract(url)))

        try:
            # Prime with initial batch (only N tasks, not all URLs)
            for _ in range(limit):
                spawn()

            while pending:
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

                for task in done:
                    spawn()  # Replenish immediately (keeps pipeline full)
                    if (result := task.result()) is not None:
                        yield result  # Backpressure point - pauses until consumed
        finally:
            # CRITICAL: cleanup on early exit or error
            for task in pending:
                task.cancel()
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)

    async def _safe_download_and_extract(self, url: str) -> tuple[str, bytes] | None:
        """Download and extract file with error handling (firewall pattern).

        This method acts as a firewall, catching exceptions so that one failed
        download doesn't cancel other concurrent downloads in a TaskGroup.

        Args:
            url: URL to download

        Returns:
            Tuple of (url, data) if successful, None if failed
        """
        try:
            data = await self.download_and_extract(url)
        except APIError as e:
            # Expected errors (404, network issues) - log at debug level
            logger.debug("Failed to download %s: %s", url, e)
            return None
        except RuntimeError as e:
            # Handle client closed during shutdown (expected when breaking out of async for)
            if "client has been closed" in str(e):
                logger.debug("Client closed during download (shutdown in progress): %s", url)
                return None
            # Re-raise unexpected RuntimeErrors
            raise
        except Exception:
            # Error boundary: catch unexpected errors, log and return None
            logger.exception("Unexpected error downloading %s", url)
            return None
        else:
            return url, data

    def _extract_zip(self, compressed_data: bytes) -> bytes:
        """Extract ZIP file.

        Args:
            compressed_data: ZIP file bytes

        Returns:
            Decompressed content

        Raises:
            DataError: If ZIP contains no files
        """
        with zipfile.ZipFile(io.BytesIO(compressed_data)) as zf:
            # GDELT files should contain exactly one file
            names = zf.namelist()
            if len(names) != 1:
                logger.warning("ZIP file contains %d files (expected 1): %s", len(names), names)
                if len(names) == 0:
                    msg = "ZIP file is empty"
                    raise DataError(msg)
                # Use first file if multiple
                logger.debug("Using first file from ZIP: %s", names[0])

            return zf.read(names[0])

    def _extract_gzip(self, compressed_data: bytes) -> bytes:
        """Extract GZIP file.

        Args:
            compressed_data: GZIP file bytes

        Returns:
            Decompressed content

        Raises:
            DataError: If decompressed size exceeds limit
        """
        result = io.BytesIO()
        total_size = 0

        with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gz:
            # Read in chunks to avoid loading huge files into memory
            chunk_size = 1024 * 1024  # 1MB chunks

            while True:
                chunk = gz.read(chunk_size)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_DECOMPRESSED_SIZE:
                    msg = f"Decompressed size exceeds {MAX_DECOMPRESSED_SIZE // (1024 * 1024)}MB limit"
                    raise DataError(msg)
                result.write(chunk)

        return result.getvalue()

    @staticmethod
    def _extract_date_from_url(url: str) -> datetime | None:
        """Extract date from GDELT URL timestamp.

        Args:
            url: GDELT file URL

        Returns:
            Datetime extracted from URL, or None if not found
        """
        # GDELT URLs contain timestamps like: YYYYMMDDHHMMSS
        match = re.search(r"/(\d{14})[.]", url)
        if match:
            timestamp_str = match.group(1)
            try:
                return parse_gdelt_datetime(timestamp_str)
            except ValueError:
                logger.debug("Invalid timestamp in URL: %s", timestamp_str)
                return None
        return None

    @staticmethod
    def _parse_master_file_line(line: str) -> str | None:
        """Extract URL from a master file list line.

        GDELT master file list format: "size_bytes md5_hash url"

        Args:
            line: Raw line from master file list.

        Returns:
            Extracted URL, or None if line is blank/malformed.
        """
        stripped = line.strip()
        if not stripped:
            return None
        parts = stripped.split()
        if len(parts) >= 3:
            return parts[2]
        if stripped.startswith("http"):
            return stripped
        logger.debug("Skipping malformed master file line: %s", stripped[:100])
        return None

    def _filter_urls_by_type_and_range(
        self,
        urls: list[str],
        file_type: FileType,
        start_date: datetime,
        end_date: datetime,
    ) -> list[str]:
        """Filter master list URLs by file type suffix and timestamp range.

        Args:
            urls: URLs from master file list.
            file_type: File type to filter for.
            start_date: Start of date range (inclusive).
            end_date: End of date range (inclusive).

        Returns:
            Filtered and sorted list of matching URLs.
        """
        pattern = FILE_TYPE_PATTERNS[file_type]
        matched: list[tuple[datetime, str]] = []

        for url in urls:
            if not url.endswith(pattern):
                continue
            file_date = self._extract_date_from_url(url)
            if file_date is None:
                continue
            # _extract_date_from_url returns UTC-aware datetimes;
            # compare naive since callers pass naive datetimes
            cmp_date = file_date.replace(tzinfo=None)
            if start_date <= cmp_date <= end_date:
                matched.append((cmp_date, url))

        matched.sort(key=lambda pair: pair[0])
        return [url for _, url in matched]
