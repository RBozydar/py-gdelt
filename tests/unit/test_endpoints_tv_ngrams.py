"""Unit tests for TVNGramsEndpoint.

Tests cover initialization, URL building, streaming, and error handling
for the GDELT TV NGrams endpoint.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from py_gdelt.endpoints.tv_ngrams import TVNGramsEndpoint
from py_gdelt.filters import BroadcastNGramsFilter, DateRange
from py_gdelt.models.ngrams import BroadcastNGramRecord, BroadcastSource


class TestInitialization:
    """Test TVNGramsEndpoint initialization."""

    def test_init_default(self) -> None:
        """Test initialization with defaults."""
        endpoint = TVNGramsEndpoint()

        assert endpoint.settings is not None
        assert endpoint._file_source is not None
        assert endpoint._parser is not None
        assert endpoint._owns_sources is True

    def test_init_with_shared_file_source(self) -> None:
        """Test initialization with shared FileSource."""
        mock_file_source = MagicMock()

        endpoint = TVNGramsEndpoint(file_source=mock_file_source)

        assert endpoint._file_source is mock_file_source
        assert endpoint._owns_sources is False

    def test_base_url(self) -> None:
        """Test BASE_URL is set correctly."""
        endpoint = TVNGramsEndpoint()

        assert endpoint.BASE_URL == "http://data.gdeltproject.org/gdeltv3/iatv/ngramsv2/"

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test async context manager protocol."""
        async with TVNGramsEndpoint() as endpoint:
            assert endpoint is not None
            assert isinstance(endpoint, TVNGramsEndpoint)

    @pytest.mark.asyncio
    async def test_close_owned_sources(self) -> None:
        """Test close() closes owned resources."""
        endpoint = TVNGramsEndpoint()
        endpoint._file_source.__aexit__ = AsyncMock()  # type: ignore[method-assign]

        await endpoint.close()

        endpoint._file_source.__aexit__.assert_called_once_with(None, None, None)

    @pytest.mark.asyncio
    async def test_close_shared_sources(self) -> None:
        """Test close() does not close shared resources."""
        mock_file_source = MagicMock()
        mock_file_source.__aexit__ = AsyncMock()

        endpoint = TVNGramsEndpoint(file_source=mock_file_source)
        await endpoint.close()

        mock_file_source.__aexit__.assert_not_called()


class TestBuildUrls:
    """Test URL building logic for TV NGrams."""

    def test_build_urls_single_day(self) -> None:
        """Test URL building for a single day."""
        endpoint = TVNGramsEndpoint()

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="CNN",
            ngram_size=1,
        )

        urls = endpoint._build_urls(filter_obj)

        assert len(urls) == 1
        assert (
            urls[0]
            == "http://data.gdeltproject.org/gdeltv3/iatv/ngramsv2/CNN.20240115.1gram.txt.gz"
        )

    def test_build_urls_multiple_days(self) -> None:
        """Test URL building for multiple days."""
        endpoint = TVNGramsEndpoint()

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15), end=date(2024, 1, 17)),
            station="CNN",
            ngram_size=1,
        )

        urls = endpoint._build_urls(filter_obj)

        assert len(urls) == 3
        assert (
            urls[0]
            == "http://data.gdeltproject.org/gdeltv3/iatv/ngramsv2/CNN.20240115.1gram.txt.gz"
        )
        assert (
            urls[1]
            == "http://data.gdeltproject.org/gdeltv3/iatv/ngramsv2/CNN.20240116.1gram.txt.gz"
        )
        assert (
            urls[2]
            == "http://data.gdeltproject.org/gdeltv3/iatv/ngramsv2/CNN.20240117.1gram.txt.gz"
        )

    def test_build_urls_different_ngram_sizes(self) -> None:
        """Test URL building for different ngram sizes."""
        endpoint = TVNGramsEndpoint()

        for ngram_size, expected_type in [(1, "1gram"), (2, "2gram"), (3, "3gram"), (5, "5gram")]:
            filter_obj = BroadcastNGramsFilter(
                date_range=DateRange(start=date(2024, 1, 15)),
                station="CNN",
                ngram_size=ngram_size,
            )

            urls = endpoint._build_urls(filter_obj)

            assert len(urls) == 1
            assert (
                urls[0]
                == f"http://data.gdeltproject.org/gdeltv3/iatv/ngramsv2/CNN.20240115.{expected_type}.txt.gz"
            )

    def test_build_urls_station_uppercase(self) -> None:
        """Test station name is converted to uppercase in URLs."""
        endpoint = TVNGramsEndpoint()

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="cnn",  # lowercase
            ngram_size=1,
        )

        urls = endpoint._build_urls(filter_obj)

        assert "CNN.20240115" in urls[0]

    def test_build_urls_different_stations(self) -> None:
        """Test URL building for different stations."""
        endpoint = TVNGramsEndpoint()

        for station in ["CNN", "MSNBC", "FOX", "BBC"]:
            filter_obj = BroadcastNGramsFilter(
                date_range=DateRange(start=date(2024, 1, 15)),
                station=station,
                ngram_size=1,
            )

            urls = endpoint._build_urls(filter_obj)

            assert len(urls) == 1
            assert f"/{station}.20240115.1gram.txt.gz" in urls[0]


class TestQuery:
    """Test query() functionality."""

    @pytest.mark.asyncio
    async def test_query_returns_fetch_result(self) -> None:
        """Test query() returns a FetchResult with collected records."""
        from py_gdelt.models.common import FetchResult

        endpoint = TVNGramsEndpoint()

        # Mock FileSource.stream_files to return sample data
        sample_data = b"20240115\tCNN\t14\tpresident\t42\n20240115\tCNN\t14\telection\t28"

        def mock_stream_files(urls: list[str], **kwargs: object) -> AsyncIteratorMock:
            return AsyncIteratorMock([("mock_url", sample_data)])

        endpoint._file_source.stream_files = mock_stream_files  # type: ignore[method-assign,assignment]

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="CNN",
            ngram_size=1,
        )

        result = await endpoint.query(filter_obj)

        assert isinstance(result, FetchResult)
        assert len(result.data) == 2
        assert all(isinstance(record, BroadcastNGramRecord) for record in result.data)
        assert result.data[0].ngram == "president"
        assert result.data[0].count == 42
        assert result.data[0].source == BroadcastSource.TV
        assert result.failed == []

    @pytest.mark.asyncio
    async def test_query_empty_results(self) -> None:
        """Test query() returns empty FetchResult when no records match."""
        from py_gdelt.models.common import FetchResult

        endpoint = TVNGramsEndpoint()

        def mock_stream_files(urls: list[str], **kwargs: object) -> AsyncIteratorMock:
            return AsyncIteratorMock([("url", b"")])

        endpoint._file_source.stream_files = mock_stream_files  # type: ignore[method-assign,assignment]

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="CNN",
            ngram_size=1,
        )

        result = await endpoint.query(filter_obj)

        assert isinstance(result, FetchResult)
        assert len(result.data) == 0
        assert result.failed == []

    @pytest.mark.asyncio
    async def test_query_no_station_raises_error(self) -> None:
        """Test query() raises ValueError when station is not specified."""
        endpoint = TVNGramsEndpoint()

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station=None,
            ngram_size=1,
        )

        with pytest.raises(ValueError, match="Station filter is required for TV NGrams queries"):
            await endpoint.query(filter_obj)


class TestStream:
    """Test streaming functionality."""

    @pytest.mark.asyncio
    async def test_stream_no_station_raises_error_at_call_time(self) -> None:
        """Test that missing station raises ValueError when stream() is called.

        This verifies fail-fast behavior: validation happens synchronously when
        stream() is invoked, NOT when iteration begins. This is important for
        developer experience - errors should be immediate, not delayed.
        """
        endpoint = TVNGramsEndpoint()

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station=None,  # No station specified
            ngram_size=1,
        )

        # The error should be raised when stream() is called, NOT during iteration.
        # stream() is no longer an async generator - it's a regular method that
        # validates and returns an async iterator.
        with pytest.raises(ValueError, match="Station filter is required for TV NGrams queries"):
            endpoint.stream(filter_obj)  # Error here, synchronously

    @pytest.mark.asyncio
    async def test_stream_parses_records(self) -> None:
        """Test that stream yields parsed BroadcastNGramRecord instances."""
        endpoint = TVNGramsEndpoint()

        # Mock FileSource.stream_files to return sample data
        sample_data = b"20240115\tCNN\t14\tpresident\t42\n20240115\tCNN\t14\telection\t28"

        # Create a callable that returns an async iterator
        def mock_stream_files(urls: list[str], **kwargs: object) -> AsyncIteratorMock:
            return AsyncIteratorMock([("mock_url", sample_data)])

        endpoint._file_source.stream_files = mock_stream_files  # type: ignore[method-assign,assignment]

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="CNN",
            ngram_size=1,
        )

        records = [record async for record in endpoint.stream(filter_obj)]

        assert len(records) == 2
        assert all(isinstance(record, BroadcastNGramRecord) for record in records)
        assert records[0].ngram == "president"
        assert records[0].count == 42
        assert records[0].source == BroadcastSource.TV
        assert records[1].ngram == "election"

    @pytest.mark.asyncio
    async def test_stream_handles_parsing_errors(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that stream logs and skips records with parsing errors."""
        endpoint = TVNGramsEndpoint()

        # Create malformed data that will fail conversion
        sample_data = b"20240115\tCNN\t14\tvalid_word\t42\n20240115\tCNN\tinvalid_hour\tword\t50"

        def mock_stream_files(urls: list[str], **kwargs: object) -> AsyncIteratorMock:
            return AsyncIteratorMock([("mock_url", sample_data)])

        endpoint._file_source.stream_files = mock_stream_files  # type: ignore[method-assign,assignment]

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="CNN",
            ngram_size=1,
        )

        records = [record async for record in endpoint.stream(filter_obj)]

        # Should get 2 parsed raw records, but only 1 should convert successfully
        # Actually, both will parse as _RawBroadcastNGram (strings), but from_raw will fail
        # Let's verify the warning is logged
        assert "Failed to parse TV NGram record" in caplog.text

    @pytest.mark.asyncio
    async def test_stream_multiple_files(self) -> None:
        """Test streaming from multiple files."""
        endpoint = TVNGramsEndpoint()

        # Mock multiple file downloads
        file1_data = b"20240115\tCNN\t14\tpresident\t42"
        file2_data = b"20240116\tCNN\t15\telection\t30"

        def mock_stream_files(urls: list[str], **kwargs: object) -> AsyncIteratorMock:
            return AsyncIteratorMock(
                [
                    ("url1", file1_data),
                    ("url2", file2_data),
                ]
            )

        endpoint._file_source.stream_files = mock_stream_files  # type: ignore[method-assign,assignment]

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15), end=date(2024, 1, 16)),
            station="CNN",
            ngram_size=1,
        )

        records = [record async for record in endpoint.stream(filter_obj)]

        assert len(records) == 2
        assert records[0].ngram == "president"
        assert records[1].ngram == "election"

    @pytest.mark.asyncio
    async def test_stream_empty_data(self) -> None:
        """Test streaming with empty data returns no records."""
        endpoint = TVNGramsEndpoint()

        def mock_stream_files(urls: list[str], **kwargs: object) -> AsyncIteratorMock:
            return AsyncIteratorMock([("url", b"")])

        endpoint._file_source.stream_files = mock_stream_files  # type: ignore[method-assign,assignment]

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="CNN",
            ngram_size=1,
        )

        records = [record async for record in endpoint.stream(filter_obj)]

        assert len(records) == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_build_urls_year_boundary(self) -> None:
        """Test URL building across year boundary."""
        endpoint = TVNGramsEndpoint()

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2023, 12, 31), end=date(2024, 1, 1)),
            station="CNN",
            ngram_size=1,
        )

        urls = endpoint._build_urls(filter_obj)

        assert len(urls) == 2
        assert "20231231" in urls[0]
        assert "20240101" in urls[1]

    def test_build_urls_month_boundary(self) -> None:
        """Test URL building across month boundary."""
        endpoint = TVNGramsEndpoint()

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 31), end=date(2024, 2, 1)),
            station="CNN",
            ngram_size=1,
        )

        urls = endpoint._build_urls(filter_obj)

        assert len(urls) == 2
        assert "20240131" in urls[0]
        assert "20240201" in urls[1]


# Helper class for async iteration in tests
class AsyncIteratorMock:
    """Mock async iterator for testing."""

    def __init__(self, items: list[tuple[str, bytes]]) -> None:
        self.items = items
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item
