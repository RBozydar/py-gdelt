"""Tests for FileSource module."""

import gzip
import io
import zipfile
from datetime import datetime
from pathlib import Path

import httpx
import pytest
import respx

from py_gdelt.cache import Cache
from py_gdelt.config import GDELTSettings
from py_gdelt.exceptions import APIError, APIUnavailableError, DataError
from py_gdelt.sources.files import (
    MASTER_FILE_LIST_URL,
    TRANSLATION_FILE_LIST_URL,
    FileSource,
)


@pytest.fixture
def mock_settings(tmp_path: Path) -> GDELTSettings:
    """Create test settings with temporary cache."""
    return GDELTSettings(
        cache_dir=tmp_path / "cache",
        cache_ttl=3600,
        max_concurrent_downloads=5,
        timeout=30,
    )


@pytest.fixture
def mock_cache(tmp_path: Path) -> Cache:
    """Create test cache."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return Cache(cache_dir=cache_dir, default_ttl=3600)


@pytest.fixture
async def file_source(
    mock_settings: GDELTSettings,
    mock_cache: Cache,
) -> FileSource:
    """Create FileSource instance for testing."""
    async with httpx.AsyncClient() as client:
        source = FileSource(
            settings=mock_settings,
            client=client,
            cache=mock_cache,
        )
        yield source


class TestFileSourceInit:
    """Test FileSource initialization."""

    def test_init_with_defaults(self) -> None:
        """Test initialization with default parameters."""
        source = FileSource()

        assert source.settings is not None
        assert source.cache is not None
        assert source._client is None
        assert source._owns_client is True

    def test_init_with_custom_settings(self, mock_settings: GDELTSettings) -> None:
        """Test initialization with custom settings."""
        source = FileSource(settings=mock_settings)

        assert source.settings is mock_settings

    async def test_context_manager(self, mock_settings: GDELTSettings) -> None:
        """Test async context manager."""
        async with FileSource(settings=mock_settings) as source:
            assert source._client is not None
            assert source._owns_client is True

        # Client should be closed after exit
        # Note: We can't directly check if closed, but no errors should occur

    async def test_context_manager_with_external_client(
        self,
        mock_settings: GDELTSettings,
    ) -> None:
        """Test context manager with externally provided client."""
        async with httpx.AsyncClient() as client:
            async with FileSource(settings=mock_settings, client=client) as source:
                assert source._client is client
                assert source._owns_client is False

    def test_client_property_without_init(self) -> None:
        """Test accessing client property before initialization."""
        source = FileSource()

        with pytest.raises(RuntimeError, match="not initialized"):
            _ = source.client


class TestGetMasterFileList:
    """Test master file list retrieval."""

    @pytest.mark.asyncio
    async def test_get_master_file_list_success(
        self,
        file_source: FileSource,
    ) -> None:
        """Test successful master file list retrieval."""
        mock_content = (
            "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip\n"
            "http://data.gdeltproject.org/gdeltv2/20240101001500.export.CSV.zip\n"
        )

        async with respx.mock:
            respx.get(MASTER_FILE_LIST_URL).mock(
                return_value=httpx.Response(200, text=mock_content),
            )

            urls = await file_source.get_master_file_list()

            assert len(urls) == 2
            assert urls[0] == "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip"
            assert urls[1] == "http://data.gdeltproject.org/gdeltv2/20240101001500.export.CSV.zip"

    @pytest.mark.asyncio
    async def test_get_master_file_list_with_translation(
        self,
        file_source: FileSource,
    ) -> None:
        """Test master file list with translation files."""
        master_content = "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip\n"
        trans_content = (
            "http://data.gdeltproject.org/gdeltv2/20240101000000.translation.export.CSV.zip\n"
        )

        async with respx.mock:
            respx.get(MASTER_FILE_LIST_URL).mock(
                return_value=httpx.Response(200, text=master_content),
            )
            respx.get(TRANSLATION_FILE_LIST_URL).mock(
                return_value=httpx.Response(200, text=trans_content),
            )

            urls = await file_source.get_master_file_list(include_translation=True)

            assert len(urls) == 2

    @pytest.mark.asyncio
    async def test_get_master_file_list_http_error(
        self,
        file_source: FileSource,
    ) -> None:
        """Test master file list with HTTP error."""
        async with respx.mock:
            respx.get(MASTER_FILE_LIST_URL).mock(
                return_value=httpx.Response(503, text="Service Unavailable"),
            )

            with pytest.raises(APIUnavailableError):
                await file_source.get_master_file_list()

    @pytest.mark.asyncio
    async def test_get_master_file_list_network_error(
        self,
        file_source: FileSource,
    ) -> None:
        """Test master file list with network error."""
        async with respx.mock:
            respx.get(MASTER_FILE_LIST_URL).mock(
                side_effect=httpx.ConnectError("Connection failed"),
            )

            with pytest.raises(APIError, match="Network error"):
                await file_source.get_master_file_list()

    @pytest.mark.asyncio
    async def test_get_master_file_list_caching(
        self,
        file_source: FileSource,
    ) -> None:
        """Test that master file list is cached."""
        mock_content = "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip\n"

        async with respx.mock:
            mock_route = respx.get(MASTER_FILE_LIST_URL).mock(
                return_value=httpx.Response(200, text=mock_content),
            )

            # First call should hit network
            urls1 = await file_source.get_master_file_list()
            assert mock_route.called
            assert len(urls1) == 1

            # Second call should use cache
            mock_route.reset()
            urls2 = await file_source.get_master_file_list()
            assert not mock_route.called
            assert urls2 == urls1


class TestGetFilesForDateRange:
    """Test file URL generation for date ranges."""

    @pytest.mark.asyncio
    async def test_get_files_for_date_range_export(
        self,
        file_source: FileSource,
    ) -> None:
        """Test getting export files for date range."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 0, 30, 0)

        urls = await file_source.get_files_for_date_range(
            start_date=start,
            end_date=end,
            file_type="export",
        )

        # Should have 3 files (0:00, 0:15, 0:30)
        assert len(urls) == 3
        assert "20240101000000.export.CSV.zip" in urls[0]
        assert "20240101001500.export.CSV.zip" in urls[1]
        assert "20240101003000.export.CSV.zip" in urls[2]

    @pytest.mark.asyncio
    async def test_get_files_for_date_range_mentions(
        self,
        file_source: FileSource,
    ) -> None:
        """Test getting mentions files."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 0, 0, 0)

        urls = await file_source.get_files_for_date_range(
            start_date=start,
            end_date=end,
            file_type="mentions",
        )

        assert len(urls) == 1
        assert "20240101000000.mentions.CSV.zip" in urls[0]

    @pytest.mark.asyncio
    async def test_get_files_for_date_range_gkg(
        self,
        file_source: FileSource,
    ) -> None:
        """Test getting GKG files."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 0, 0, 0)

        urls = await file_source.get_files_for_date_range(
            start_date=start,
            end_date=end,
            file_type="gkg",
        )

        assert len(urls) == 1
        assert "20240101000000.gkg.csv.zip" in urls[0]

    @pytest.mark.asyncio
    async def test_get_files_for_date_range_ngrams(
        self,
        file_source: FileSource,
    ) -> None:
        """Test getting NGrams files."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 0, 0, 0)

        urls = await file_source.get_files_for_date_range(
            start_date=start,
            end_date=end,
            file_type="ngrams",
        )

        assert len(urls) == 1
        assert "20240101000000.webngrams.json.gz" in urls[0]
        assert "gdeltv3/webngrams" in urls[0]

    @pytest.mark.asyncio
    async def test_get_files_for_date_range_with_translation(
        self,
        file_source: FileSource,
    ) -> None:
        """Test getting files with translation."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 0, 0, 0)

        urls = await file_source.get_files_for_date_range(
            start_date=start,
            end_date=end,
            file_type="export",
            include_translation=True,
        )

        # Should have 2 files (regular + translation)
        assert len(urls) == 2
        assert "20240101000000.export.CSV.zip" in urls[0]
        assert "20240101000000.translation.export.CSV.zip" in urls[1]

    @pytest.mark.asyncio
    async def test_get_files_for_date_range_invalid_dates(
        self,
        file_source: FileSource,
    ) -> None:
        """Test invalid date range."""
        start = datetime(2024, 1, 2, 0, 0, 0)
        end = datetime(2024, 1, 1, 0, 0, 0)

        with pytest.raises(ValueError, match="must be <="):
            await file_source.get_files_for_date_range(
                start_date=start,
                end_date=end,
                file_type="export",
            )

    @pytest.mark.asyncio
    async def test_get_files_for_date_range_invalid_type(
        self,
        file_source: FileSource,
    ) -> None:
        """Test invalid file type."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 0, 0, 0)

        with pytest.raises(ValueError, match="Unknown file_type"):
            await file_source.get_files_for_date_range(
                start_date=start,
                end_date=end,
                file_type="invalid",  # type: ignore[arg-type]
            )


class TestDownloadFile:
    """Test file download."""

    @pytest.mark.asyncio
    async def test_download_file_success(
        self,
        file_source: FileSource,
    ) -> None:
        """Test successful file download."""
        url = "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip"
        mock_data = b"test data"

        async with respx.mock:
            respx.get(url).mock(
                return_value=httpx.Response(200, content=mock_data),
            )

            data = await file_source.download_file(url)

            assert data == mock_data

    @pytest.mark.asyncio
    async def test_download_file_404(
        self,
        file_source: FileSource,
    ) -> None:
        """Test download with 404 error."""
        url = "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip"

        async with respx.mock:
            respx.get(url).mock(
                return_value=httpx.Response(404, text="Not Found"),
            )

            with pytest.raises(APIError, match="File not found"):
                await file_source.download_file(url)

    @pytest.mark.asyncio
    async def test_download_file_server_error(
        self,
        file_source: FileSource,
    ) -> None:
        """Test download with server error."""
        url = "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip"

        async with respx.mock:
            respx.get(url).mock(
                return_value=httpx.Response(500, text="Internal Server Error"),
            )

            with pytest.raises(APIUnavailableError):
                await file_source.download_file(url)

    @pytest.mark.asyncio
    async def test_download_file_caching(
        self,
        file_source: FileSource,
    ) -> None:
        """Test that downloaded files are cached."""
        url = "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip"
        mock_data = b"test data"

        async with respx.mock:
            mock_route = respx.get(url).mock(
                return_value=httpx.Response(200, content=mock_data),
            )

            # First download
            data1 = await file_source.download_file(url)
            assert mock_route.called
            assert data1 == mock_data

            # Second download should use cache
            mock_route.reset()
            data2 = await file_source.download_file(url)
            assert not mock_route.called
            assert data2 == mock_data


class TestDownloadAndExtract:
    """Test file download and extraction."""

    @pytest.mark.asyncio
    async def test_download_and_extract_zip(
        self,
        file_source: FileSource,
    ) -> None:
        """Test downloading and extracting ZIP file."""
        url = "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip"
        original_data = b"test data content"

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("20240101000000.export.CSV", original_data)
        zip_data = zip_buffer.getvalue()

        async with respx.mock:
            respx.get(url).mock(
                return_value=httpx.Response(200, content=zip_data),
            )

            data = await file_source.download_and_extract(url)

            assert data == original_data

    @pytest.mark.asyncio
    async def test_download_and_extract_gzip(
        self,
        file_source: FileSource,
    ) -> None:
        """Test downloading and extracting GZIP file."""
        url = "http://data.gdeltproject.org/gdeltv3/webngrams/20240101000000.webngrams.json.gz"
        original_data = b'{"test": "data"}'

        # Create GZIP in memory
        gzip_buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=gzip_buffer, mode="wb") as gz:
            gz.write(original_data)
        gzip_data = gzip_buffer.getvalue()

        async with respx.mock:
            respx.get(url).mock(
                return_value=httpx.Response(200, content=gzip_data),
            )

            data = await file_source.download_and_extract(url)

            assert data == original_data

    @pytest.mark.asyncio
    async def test_download_and_extract_uncompressed(
        self,
        file_source: FileSource,
    ) -> None:
        """Test downloading uncompressed file."""
        url = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"
        original_data = b"test data"

        async with respx.mock:
            respx.get(url).mock(
                return_value=httpx.Response(200, content=original_data),
            )

            data = await file_source.download_and_extract(url)

            assert data == original_data

    @pytest.mark.asyncio
    async def test_download_and_extract_bad_zip(
        self,
        file_source: FileSource,
    ) -> None:
        """Test extraction of invalid ZIP file."""
        url = "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip"
        bad_zip_data = b"not a valid zip file"

        async with respx.mock:
            respx.get(url).mock(
                return_value=httpx.Response(200, content=bad_zip_data),
            )

            with pytest.raises(DataError, match="Invalid archive format"):
                await file_source.download_and_extract(url)


class TestStreamFiles:
    """Test concurrent file streaming."""

    @pytest.mark.asyncio
    async def test_stream_files_success(
        self,
        file_source: FileSource,
    ) -> None:
        """Test streaming multiple files successfully."""
        urls = [
            "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip",
            "http://data.gdeltproject.org/gdeltv2/20240101001500.export.CSV.zip",
        ]

        original_data = b"test data"
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("test.csv", original_data)
        zip_data = zip_buffer.getvalue()

        async with respx.mock:
            for url in urls:
                respx.get(url).mock(
                    return_value=httpx.Response(200, content=zip_data),
                )

            results = []
            async for url, data in file_source.stream_files(urls):
                results.append((url, data))

            assert len(results) == 2
            for url, data in results:
                assert url in urls
                assert data == original_data

    @pytest.mark.asyncio
    async def test_stream_files_with_failures(
        self,
        file_source: FileSource,
    ) -> None:
        """Test streaming with some failed downloads."""
        urls = [
            "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip",
            "http://data.gdeltproject.org/gdeltv2/20240101001500.export.CSV.zip",
            "http://data.gdeltproject.org/gdeltv2/20240101003000.export.CSV.zip",
        ]

        original_data = b"test data"
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("test.csv", original_data)
        zip_data = zip_buffer.getvalue()

        async with respx.mock:
            # First URL succeeds
            respx.get(urls[0]).mock(
                return_value=httpx.Response(200, content=zip_data),
            )
            # Second URL fails with 404
            respx.get(urls[1]).mock(
                return_value=httpx.Response(404, text="Not Found"),
            )
            # Third URL succeeds
            respx.get(urls[2]).mock(
                return_value=httpx.Response(200, content=zip_data),
            )

            results = []
            async for url, data in file_source.stream_files(urls):
                results.append((url, data))

            # Should only get 2 successful results (order is non-deterministic)
            assert len(results) == 2
            result_urls = {r[0] for r in results}
            assert urls[0] in result_urls  # First URL succeeded
            assert urls[1] not in result_urls  # Second URL failed (404)
            assert urls[2] in result_urls  # Third URL succeeded
            # Verify data integrity
            for url, data in results:
                assert data == original_data

    @pytest.mark.asyncio
    async def test_stream_files_custom_concurrency(
        self,
        file_source: FileSource,
    ) -> None:
        """Test streaming with custom concurrency limit."""
        urls = [
            f"http://data.gdeltproject.org/gdeltv2/2024010100{i:02d}00.export.CSV.zip"
            for i in range(10)
        ]

        original_data = b"test data"
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("test.csv", original_data)
        zip_data = zip_buffer.getvalue()

        async with respx.mock:
            for url in urls:
                respx.get(url).mock(
                    return_value=httpx.Response(200, content=zip_data),
                )

            results = []
            async for url, data in file_source.stream_files(urls, max_concurrent=2):
                results.append((url, data))

            assert len(results) == 10

    @pytest.mark.asyncio
    async def test_stream_files_yields_before_all_complete(
        self,
        file_source: FileSource,
    ) -> None:
        """Test that stream_files yields results as they complete, not after all complete.

        This verifies true streaming behavior - results should be yielded incrementally
        as downloads complete, rather than waiting for ALL downloads to finish first.
        """
        import asyncio

        urls = [
            "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip",
            "http://data.gdeltproject.org/gdeltv2/20240101001500.export.CSV.zip",
            "http://data.gdeltproject.org/gdeltv2/20240101003000.export.CSV.zip",
        ]

        original_data = b"test data"
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("test.csv", original_data)
        zip_data = zip_buffer.getvalue()

        # Track which downloads have completed
        download_completed = dict.fromkeys(urls, False)
        first_yield_time = None
        all_complete_time = None

        async def delayed_response(url: str) -> httpx.Response:
            """Simulate delayed download with different delays per URL."""
            # First URL completes quickly, last URL takes longer
            delay = 0.1 if url == urls[0] else 0.5
            await asyncio.sleep(delay)
            download_completed[url] = True
            if all(download_completed.values()):
                nonlocal all_complete_time
                all_complete_time = asyncio.get_event_loop().time()
            return httpx.Response(200, content=zip_data)

        async with respx.mock:
            for url in urls:
                respx.get(url).mock(
                    side_effect=lambda request, url=url: delayed_response(url),
                )

            results = []
            async for url, data in file_source.stream_files(urls):
                if first_yield_time is None:
                    first_yield_time = asyncio.get_event_loop().time()
                results.append((url, data))

            # Verify we got all results
            assert len(results) == 3

            # Verify true streaming: first result was yielded BEFORE all downloads completed
            # This would fail with TaskGroup which waits for all tasks before yielding
            assert first_yield_time is not None
            assert all_complete_time is not None
            assert first_yield_time < all_complete_time, (
                "First yield should happen before all downloads complete (true streaming)"
            )


class TestHelperMethods:
    """Test helper and utility methods."""

    def test_upgrade_to_https(self) -> None:
        """Test HTTP to HTTPS upgrade."""
        http_url = "http://data.gdeltproject.org/gdeltv2/file.zip"
        https_url = FileSource._upgrade_to_https(http_url)

        assert https_url == "https://data.gdeltproject.org/gdeltv2/file.zip"

    def test_upgrade_to_https_already_https(self) -> None:
        """Test HTTPS URL is not modified."""
        https_url = "https://data.gdeltproject.org/gdeltv2/file.zip"
        result = FileSource._upgrade_to_https(https_url)

        assert result == https_url

    def test_extract_date_from_url(self) -> None:
        """Test extracting date from GDELT URL."""
        url = "http://data.gdeltproject.org/gdeltv2/20240115123000.export.CSV.zip"
        date = FileSource._extract_date_from_url(url)

        assert date is not None
        assert date.year == 2024
        assert date.month == 1
        assert date.day == 15
        assert date.hour == 12
        assert date.minute == 30
        assert date.second == 0

    def test_extract_date_from_url_no_match(self) -> None:
        """Test extracting date from URL without timestamp."""
        url = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"
        date = FileSource._extract_date_from_url(url)

        assert date is None

    def test_extract_date_from_url_invalid_timestamp(self) -> None:
        """Test extracting invalid timestamp from URL."""
        url = "http://data.gdeltproject.org/gdeltv2/99999999999999.export.CSV.zip"
        date = FileSource._extract_date_from_url(url)

        assert date is None
