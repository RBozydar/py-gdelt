"""FileSource for downloading and extracting GDELT data files.

This module provides functionality for downloading GDELT data files directly from
data.gdeltproject.org. It handles:
- Master file list retrieval and parsing
- File URL generation for date ranges
- Concurrent download with bounded concurrency
- ZIP/GZ decompression
- Intelligent caching (historical files cached indefinitely, recent files TTL-based)
"""

import asyncio
import gzip
import io
import logging
import re
import zipfile
from collections.abc import AsyncIterator, Iterable
from datetime import UTC, datetime, timedelta
from typing import Final, Literal

import httpx

from py_gdelt.cache import Cache
from py_gdelt.config import GDELTSettings
from py_gdelt.exceptions import APIError, APIUnavailableError, DataError


__all__ = ["FileSource", "FileType"]

logger = logging.getLogger(__name__)

# GDELT file list URLs
# NOTE: data.gdeltproject.org only supports HTTP (SSL cert is for *.storage.googleapis.com)
# See: https://blog.gdeltproject.org/https-now-available-for-selected-gdelt-apis-and-services/
MASTER_FILE_LIST_URL: Final[str] = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"
TRANSLATION_FILE_LIST_URL: Final[str] = (
    "http://data.gdeltproject.org/gdeltv2/masterfilelist-translation.txt"
)
LAST_UPDATE_URL: Final[str] = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

# File type patterns
FILE_TYPE_PATTERNS: Final[dict[str, str]] = {
    "export": ".export.CSV.zip",
    "mentions": ".mentions.CSV.zip",
    "gkg": ".gkg.csv.zip",
    "ngrams": ".webngrams.json.gz",
}

# Type alias for file types
FileType = Literal["export", "mentions", "gkg", "ngrams"]


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

    async def __aenter__(self) -> "FileSource":
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

                # Parse URLs from content (one URL per line)
                file_urls = [line.strip() for line in content.splitlines() if line.strip()]
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

        Generates URLs based on GDELT naming patterns. Note that not all
        time slots have files (15-minute granularity may have gaps).

        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            file_type: Type of files to get (export, mentions, gkg, ngrams)
            include_translation: If True, include translation files

        Returns:
            List of file URLs for the date range

        Raises:
            ValueError: If date range is invalid or file_type unknown
        """
        if start_date > end_date:
            err_msg = f"start_date ({start_date}) must be <= end_date ({end_date})"
            raise ValueError(err_msg)

        if file_type not in FILE_TYPE_PATTERNS:
            valid_types = ", ".join(FILE_TYPE_PATTERNS.keys())
            err_msg = f"Unknown file_type '{file_type}'. Valid types: {valid_types}"
            raise ValueError(err_msg)

        pattern = FILE_TYPE_PATTERNS[file_type]
        urls: list[str] = []

        # Generate URLs for 15-minute intervals
        current = start_date
        delta = timedelta(minutes=15)

        while current <= end_date:
            timestamp = current.strftime("%Y%m%d%H%M%S")

            # Build URL based on file type
            if file_type == "ngrams":
                url = f"http://data.gdeltproject.org/gdeltv3/webngrams/{timestamp}{pattern}"
            else:
                url = f"http://data.gdeltproject.org/gdeltv2/{timestamp}{pattern}"

            urls.append(url)

            # Handle translation files
            if include_translation and file_type != "ngrams":
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
        """
        result = io.BytesIO()

        with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gz:
            # Read in chunks to avoid loading huge files into memory
            chunk_size = 1024 * 1024  # 1MB chunks

            while True:
                chunk = gz.read(chunk_size)
                if not chunk:
                    break
                result.write(chunk)

        return result.getvalue()

    @staticmethod
    def _upgrade_to_https(url: str) -> str:
        """Upgrade HTTP URL to HTTPS.

        Note:
            This method is currently unused because data.gdeltproject.org only
            supports HTTP (SSL cert is for *.storage.googleapis.com). Kept for
            potential future use if GDELT fixes their SSL certificate.

        Args:
            url: URL to upgrade

        Returns:
            HTTPS version of URL
        """
        if url.startswith("http://"):
            return url.replace("http://", "https://", 1)
        return url

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
                return datetime.strptime(timestamp_str, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
            except ValueError:
                logger.debug("Invalid timestamp in URL: %s", timestamp_str)
                return None
        return None
