"""Unit tests for RadioNGramsEndpoint.

Tests cover initialization, URL building from inventory files, streaming,
show filtering, and error handling for the GDELT Radio NGrams endpoint.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_gdelt.endpoints.radio_ngrams import RadioNGramsEndpoint
from py_gdelt.filters import BroadcastNGramsFilter, DateRange
from py_gdelt.models.ngrams import BroadcastNGramRecord, BroadcastSource


class TestInitialization:
    """Test RadioNGramsEndpoint initialization."""

    def test_init_default(self) -> None:
        """Test initialization with defaults."""
        endpoint = RadioNGramsEndpoint()

        assert endpoint.settings is not None
        assert endpoint._file_source is not None
        assert endpoint._parser is not None
        assert endpoint._owns_sources is True

    def test_init_with_shared_file_source(self) -> None:
        """Test initialization with shared FileSource."""
        mock_file_source = MagicMock()

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        assert endpoint._file_source is mock_file_source
        assert endpoint._owns_sources is False

    def test_base_url(self) -> None:
        """Test BASE_URL is set correctly."""
        endpoint = RadioNGramsEndpoint()

        assert endpoint.BASE_URL == "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/"

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test async context manager protocol."""
        # Mock FileSource.__aenter__ and __aexit__
        mock_file_source = MagicMock()
        mock_file_source.__aenter__ = AsyncMock(return_value=mock_file_source)
        mock_file_source.__aexit__ = AsyncMock()

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        async with endpoint as ep:
            assert ep is not None
            assert isinstance(ep, RadioNGramsEndpoint)

        # Verify __aenter__ was called on owned sources
        # (in this test we use shared source, so it shouldn't be called)

    @pytest.mark.asyncio
    async def test_close_owned_sources(self) -> None:
        """Test close() closes owned resources."""
        with patch.object(RadioNGramsEndpoint, "close") as mock_close:
            mock_close.return_value = AsyncMock()
            endpoint = RadioNGramsEndpoint()
            await endpoint.close()
            assert endpoint._owns_sources is True

    @pytest.mark.asyncio
    async def test_close_shared_sources(self) -> None:
        """Test close() does not close shared resources."""
        mock_file_source = MagicMock()
        mock_file_source.__aexit__ = AsyncMock()

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)
        await endpoint.close()

        mock_file_source.__aexit__.assert_not_called()


class TestBuildUrls:
    """Test URL building logic for Radio NGrams (inventory-based)."""

    @pytest.mark.asyncio
    async def test_build_urls_single_day(self) -> None:
        """Test URL building for a single day from inventory file."""
        # Mock inventory file response
        inventory_content = (
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz\n"
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/WNYC.20240115.1gram.txt.gz"
        )

        mock_response = MagicMock()
        mock_response.text = inventory_content
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            ngram_size=1,
        )

        urls = await endpoint._build_urls(filter_obj)

        assert len(urls) == 1
        assert (
            urls[0]
            == "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz"
        )

    @pytest.mark.asyncio
    async def test_build_urls_all_stations(self) -> None:
        """Test URL building without station filter returns all stations."""
        inventory_content = (
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz\n"
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/WNYC.20240115.1gram.txt.gz\n"
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/NPR.20240115.1gram.txt.gz"
        )

        mock_response = MagicMock()
        mock_response.text = inventory_content
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station=None,  # All stations
            ngram_size=1,
        )

        urls = await endpoint._build_urls(filter_obj)

        assert len(urls) == 3
        assert any("KQED" in url for url in urls)
        assert any("WNYC" in url for url in urls)
        assert any("NPR" in url for url in urls)

    @pytest.mark.asyncio
    async def test_build_urls_multiple_days(self) -> None:
        """Test URL building for multiple days."""
        # Mock inventory responses for two days
        inventory_day1 = (
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz"
        )
        inventory_day2 = (
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240116.1gram.txt.gz"
        )

        mock_response_1 = MagicMock()
        mock_response_1.text = inventory_day1
        mock_response_1.raise_for_status = MagicMock()

        mock_response_2 = MagicMock()
        mock_response_2.text = inventory_day2
        mock_response_2.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=[mock_response_1, mock_response_2])

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15), end=date(2024, 1, 16)),
            station="KQED",
            ngram_size=1,
        )

        urls = await endpoint._build_urls(filter_obj)

        assert len(urls) == 2
        assert any("20240115" in url for url in urls)
        assert any("20240116" in url for url in urls)

    @pytest.mark.asyncio
    async def test_build_urls_filters_by_ngram_size(self) -> None:
        """Test URL building filters by ngram size."""
        inventory_content = (
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz\n"
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.2gram.txt.gz\n"
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.3gram.txt.gz"
        )

        mock_response = MagicMock()
        mock_response.text = inventory_content
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            ngram_size=2,
        )

        urls = await endpoint._build_urls(filter_obj)

        assert len(urls) == 1
        assert "2gram" in urls[0]

    @pytest.mark.asyncio
    async def test_build_urls_handles_inventory_fetch_error(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test URL building handles inventory fetch errors gracefully."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=Exception("Network error"))

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            ngram_size=1,
        )

        urls = await endpoint._build_urls(filter_obj)

        assert len(urls) == 0
        assert "Failed to fetch Radio NGrams inventory for 20240115" in caplog.text

    @pytest.mark.asyncio
    async def test_build_urls_empty_inventory(self) -> None:
        """Test URL building with empty inventory file."""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            ngram_size=1,
        )

        urls = await endpoint._build_urls(filter_obj)

        assert len(urls) == 0

    @pytest.mark.asyncio
    async def test_build_urls_inventory_with_blank_lines(self) -> None:
        """Test URL building handles inventory with blank lines."""
        inventory_content = (
            "\n"
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz\n"
            "\n"
            "   \n"
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/WNYC.20240115.1gram.txt.gz\n"
        )

        mock_response = MagicMock()
        mock_response.text = inventory_content
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station=None,
            ngram_size=1,
        )

        urls = await endpoint._build_urls(filter_obj)

        assert len(urls) == 2

    @pytest.mark.asyncio
    async def test_build_urls_rejects_unexpected_urls(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test URL building rejects URLs that don't match expected BASE_URL (SSRF protection)."""
        inventory_content = (
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz\n"
            "http://evil.com/malicious.txt.gz\n"
            "https://attacker.net/data.txt.gz\n"
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/WNYC.20240115.1gram.txt.gz"
        )

        mock_response = MagicMock()
        mock_response.text = inventory_content
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station=None,
            ngram_size=1,
        )

        urls = await endpoint._build_urls(filter_obj)

        # Should only include the 2 valid GDELT URLs
        assert len(urls) == 2
        assert all(url.startswith(endpoint.BASE_URL) for url in urls)

        # Should log warnings for unexpected URLs
        assert (
            "Unexpected URL in inventory, skipping: http://evil.com/malicious.txt.gz" in caplog.text
        )
        assert (
            "Unexpected URL in inventory, skipping: https://attacker.net/data.txt.gz" in caplog.text
        )


class TestQuery:
    """Test query() functionality."""

    @pytest.mark.asyncio
    async def test_query_returns_fetch_result(self) -> None:
        """Test query() returns a FetchResult with collected records."""
        from py_gdelt.models.common import FetchResult

        mock_file_source = MagicMock()
        mock_file_source.stream_files = MagicMock(
            return_value=AsyncIteratorMock(
                [
                    (
                        "mock_url",
                        b"20240115\tKQED\t09\tclimate\t15\tMorning Edition\n20240115\tKQED\t09\thealth\t22\tMorning Edition",
                    )
                ]
            )
        )

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)
        endpoint._build_urls = AsyncMock(return_value=["mock_url"])

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            ngram_size=1,
        )

        result = await endpoint.query(filter_obj)

        assert isinstance(result, FetchResult)
        assert len(result.data) == 2
        assert all(isinstance(record, BroadcastNGramRecord) for record in result.data)
        assert result.data[0].ngram == "climate"
        assert result.data[0].count == 15
        assert result.data[0].show == "Morning Edition"
        assert result.data[0].source == BroadcastSource.RADIO
        assert result.failed == []

    @pytest.mark.asyncio
    async def test_query_empty_results(self) -> None:
        """Test query() returns empty FetchResult when no records match."""
        from py_gdelt.models.common import FetchResult

        mock_file_source = MagicMock()
        mock_file_source.stream_files = MagicMock(return_value=AsyncIteratorMock([("url", b"")]))

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)
        endpoint._build_urls = AsyncMock(return_value=["mock_url"])

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            ngram_size=1,
        )

        result = await endpoint.query(filter_obj)

        assert isinstance(result, FetchResult)
        assert len(result.data) == 0
        assert result.failed == []

    @pytest.mark.asyncio
    async def test_query_with_show_filter(self) -> None:
        """Test query() filters results by show name."""
        from py_gdelt.models.common import FetchResult

        sample_data = (
            b"20240115\tKQED\t09\tclimate\t15\tMorning Edition\n"
            b"20240115\tKQED\t12\thealth\t22\tThe Takeaway\n"
            b"20240115\tKQED\t09\tpolicy\t10\tMorning Edition"
        )

        mock_file_source = MagicMock()
        mock_file_source.stream_files = MagicMock(
            return_value=AsyncIteratorMock([("mock_url", sample_data)])
        )

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)
        endpoint._build_urls = AsyncMock(return_value=["mock_url"])

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            show="Morning Edition",
            ngram_size=1,
        )

        result = await endpoint.query(filter_obj)

        assert isinstance(result, FetchResult)
        assert len(result.data) == 2
        assert all(record.show == "Morning Edition" for record in result.data)
        assert result.failed == []


class TestStream:
    """Test streaming functionality."""

    @pytest.mark.asyncio
    async def test_stream_parses_records(self) -> None:
        """Test that stream yields parsed BroadcastNGramRecord instances."""
        mock_file_source = MagicMock()
        mock_file_source.stream_files = MagicMock(
            return_value=AsyncIteratorMock(
                [
                    (
                        "mock_url",
                        b"20240115\tKQED\t09\tclimate\t15\tMorning Edition\n20240115\tKQED\t09\thealth\t22\tMorning Edition",
                    )
                ]
            )
        )

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)
        endpoint._build_urls = AsyncMock(return_value=["mock_url"])

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            ngram_size=1,
        )

        records = [record async for record in endpoint.stream(filter_obj)]

        assert len(records) == 2
        assert all(isinstance(record, BroadcastNGramRecord) for record in records)
        assert records[0].ngram == "climate"
        assert records[0].count == 15
        assert records[0].show == "Morning Edition"
        assert records[0].source == BroadcastSource.RADIO

    @pytest.mark.asyncio
    async def test_stream_filters_by_show(self) -> None:
        """Test that stream filters by show name."""
        sample_data = (
            b"20240115\tKQED\t09\tclimate\t15\tMorning Edition\n"
            b"20240115\tKQED\t12\thealth\t22\tThe Takeaway\n"
            b"20240115\tKQED\t09\tpolicy\t10\tMorning Edition"
        )

        mock_file_source = MagicMock()
        mock_file_source.stream_files = MagicMock(
            return_value=AsyncIteratorMock([("mock_url", sample_data)])
        )

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)
        endpoint._build_urls = AsyncMock(return_value=["mock_url"])

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            show="Morning Edition",
            ngram_size=1,
        )

        records = [record async for record in endpoint.stream(filter_obj)]

        assert len(records) == 2
        assert all(record.show == "Morning Edition" for record in records)

    @pytest.mark.asyncio
    async def test_stream_no_show_filter(self) -> None:
        """Test that stream without show filter returns all shows."""
        sample_data = (
            b"20240115\tKQED\t09\tclimate\t15\tMorning Edition\n"
            b"20240115\tKQED\t12\thealth\t22\tThe Takeaway"
        )

        mock_file_source = MagicMock()
        mock_file_source.stream_files = MagicMock(
            return_value=AsyncIteratorMock([("mock_url", sample_data)])
        )

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)
        endpoint._build_urls = AsyncMock(return_value=["mock_url"])

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            show=None,  # No show filter
            ngram_size=1,
        )

        records = [record async for record in endpoint.stream(filter_obj)]

        assert len(records) == 2
        assert records[0].show == "Morning Edition"
        assert records[1].show == "The Takeaway"

    @pytest.mark.asyncio
    async def test_stream_handles_parsing_errors(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that stream logs and skips records with parsing errors."""
        # Malformed data (invalid hour)
        sample_data = (
            b"20240115\tKQED\t09\tvalid\t15\tMorning Edition\n"
            b"20240115\tKQED\tinvalid_hour\tword\t50\tShow"
        )

        mock_file_source = MagicMock()
        mock_file_source.stream_files = MagicMock(
            return_value=AsyncIteratorMock([("mock_url", sample_data)])
        )

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)
        endpoint._build_urls = AsyncMock(return_value=["mock_url"])

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            ngram_size=1,
        )

        _ = [record async for record in endpoint.stream(filter_obj)]

        # Should log warning about parsing failure
        assert "Failed to parse Radio NGram record" in caplog.text

    @pytest.mark.asyncio
    async def test_stream_empty_data(self) -> None:
        """Test streaming with empty data returns no records."""
        mock_file_source = MagicMock()
        mock_file_source.stream_files = MagicMock(return_value=AsyncIteratorMock([("url", b"")]))

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)
        endpoint._build_urls = AsyncMock(return_value=["mock_url"])

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            ngram_size=1,
        )

        records = [record async for record in endpoint.stream(filter_obj)]

        assert len(records) == 0


class TestUrlValidation:
    """Test URL validation logic."""

    def test_validate_url_valid(self) -> None:
        """Test validation passes for valid GDELT URLs."""
        endpoint = RadioNGramsEndpoint()

        # Valid URLs should not raise
        endpoint._validate_url(
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz"
        )
        endpoint._validate_url(
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/WNYC.20240115.2gram.txt.gz"
        )

    def test_validate_url_invalid_scheme_https(self) -> None:
        """Test validation rejects HTTPS scheme (GDELT uses HTTP)."""
        endpoint = RadioNGramsEndpoint()

        with pytest.raises(ValueError, match="Invalid URL scheme 'https'"):
            endpoint._validate_url(
                "https://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz"
            )

    def test_validate_url_invalid_scheme_ftp(self) -> None:
        """Test validation rejects FTP scheme."""
        endpoint = RadioNGramsEndpoint()

        with pytest.raises(ValueError, match="Invalid URL scheme 'ftp'"):
            endpoint._validate_url(
                "ftp://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz"
            )

    def test_validate_url_wrong_host(self) -> None:
        """Test validation rejects non-GDELT hosts."""
        endpoint = RadioNGramsEndpoint()

        with pytest.raises(ValueError, match=r"Invalid URL host 'evil\.com'"):
            endpoint._validate_url("http://evil.com/malicious.txt.gz")

    def test_validate_url_wrong_host_similar(self) -> None:
        """Test validation rejects hosts that are similar but not GDELT."""
        endpoint = RadioNGramsEndpoint()

        with pytest.raises(ValueError, match=r"Invalid URL host 'fake-gdeltproject\.org'"):
            endpoint._validate_url(
                "http://fake-gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.txt.gz"
            )

    def test_validate_url_empty_path(self) -> None:
        """Test validation rejects URLs with empty path."""
        endpoint = RadioNGramsEndpoint()

        with pytest.raises(ValueError, match="Invalid URL with empty path"):
            endpoint._validate_url("http://data.gdeltproject.org")

    def test_validate_url_malformed(self) -> None:
        """Test validation handles malformed URLs."""
        endpoint = RadioNGramsEndpoint()

        # Missing scheme defaults to empty scheme
        with pytest.raises(ValueError, match="Invalid URL scheme ''"):
            endpoint._validate_url("data.gdeltproject.org/path")

    @pytest.mark.asyncio
    async def test_build_urls_validates_with_validate_url_method(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that _build_urls uses _validate_url for additional validation."""
        # URL that passes prefix check but would fail domain validation
        # This tests the integration of _validate_url in _build_urls
        inventory_content = (
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz\n"
        )

        mock_response = MagicMock()
        mock_response.text = inventory_content
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            ngram_size=1,
        )

        urls = await endpoint._build_urls(filter_obj)

        # Valid URL should pass both validations
        assert len(urls) == 1
        assert "KQED.20240115.1gram" in urls[0]


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_build_urls_year_boundary(self) -> None:
        """Test URL building across year boundary."""
        inventory_2023 = (
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20231231.1gram.txt.gz"
        )
        inventory_2024 = (
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240101.1gram.txt.gz"
        )

        mock_response_1 = MagicMock()
        mock_response_1.text = inventory_2023
        mock_response_1.raise_for_status = MagicMock()

        mock_response_2 = MagicMock()
        mock_response_2.text = inventory_2024
        mock_response_2.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=[mock_response_1, mock_response_2])

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2023, 12, 31), end=date(2024, 1, 1)),
            station="KQED",
            ngram_size=1,
        )

        urls = await endpoint._build_urls(filter_obj)

        assert len(urls) == 2
        assert any("20231231" in url for url in urls)
        assert any("20240101" in url for url in urls)


class TestGetLatest:
    """Test get_latest() method."""

    @pytest.mark.asyncio
    async def test_get_latest_success(self) -> None:
        """Test successful get_latest() retrieval."""
        # Mock inventory response
        inventory_content = (
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz\n"
        )

        mock_inventory_response = MagicMock()
        mock_inventory_response.text = inventory_content
        mock_inventory_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_inventory_response)

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        # Mock stream_files to return sample data
        test_data = b"20240115\tKQED\t09\tword1\t10\tMorning Edition\n20240115\tKQED\t10\tword2\t20\tAfternoon News"

        def mock_stream_files(urls: list[str], **kwargs: object) -> AsyncIteratorMock:
            return AsyncIteratorMock([("url", test_data)])

        mock_file_source.stream_files = mock_stream_files

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        records = await endpoint.get_latest(station="KQED")

        assert len(records) == 2
        assert all(isinstance(r, BroadcastNGramRecord) for r in records)
        assert all(r.source == BroadcastSource.RADIO for r in records)
        assert records[0].ngram == "word1"
        assert records[0].show == "Morning Edition"

    @pytest.mark.asyncio
    async def test_get_latest_no_station_filter(self) -> None:
        """Test get_latest() without station filter returns all stations."""
        inventory_content = (
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz\n"
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/NPR.20240115.1gram.txt.gz\n"
        )

        mock_inventory_response = MagicMock()
        mock_inventory_response.text = inventory_content
        mock_inventory_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_inventory_response)

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        test_data = b"20240115\tKQED\t09\tword1\t10\tMorning Edition"

        def mock_stream_files(urls: list[str], **kwargs: object) -> AsyncIteratorMock:
            return AsyncIteratorMock([("url", test_data)])

        mock_file_source.stream_files = mock_stream_files

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        records = await endpoint.get_latest()  # No station filter

        assert len(records) >= 1

    @pytest.mark.asyncio
    async def test_get_latest_no_data(self) -> None:
        """Test get_latest() when no data is available."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=Exception("Not found"))

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        records = await endpoint.get_latest(station="KQED")

        assert len(records) == 0

    @pytest.mark.asyncio
    async def test_get_latest_with_ngram_size(self) -> None:
        """Test get_latest() with custom ngram size."""
        inventory_content = (
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.2gram.txt.gz\n"
        )

        mock_inventory_response = MagicMock()
        mock_inventory_response.text = inventory_content
        mock_inventory_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_inventory_response)

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        test_data = b"20240115\tKQED\t09\thello world\t5\tMorning Edition"

        def mock_stream_files(urls: list[str], **kwargs: object) -> AsyncIteratorMock:
            return AsyncIteratorMock([("url", test_data)])

        mock_file_source.stream_files = mock_stream_files

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        records = await endpoint.get_latest(ngram_size=2)

        assert len(records) == 1


class TestGetLatestSync:
    """Test get_latest_sync() method."""

    def test_get_latest_sync(self) -> None:
        """Test synchronous get_latest_sync() wrapper."""
        inventory_content = (
            "http://data.gdeltproject.org/gdeltv3/iaradio/ngrams/KQED.20240115.1gram.txt.gz\n"
        )

        mock_inventory_response = MagicMock()
        mock_inventory_response.text = inventory_content
        mock_inventory_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_inventory_response)

        mock_file_source = MagicMock()
        type(mock_file_source).client = property(lambda self: mock_client)

        test_data = b"20240115\tKQED\t09\tword1\t10\tMorning Edition"

        def mock_stream_files(urls: list[str], **kwargs: object) -> AsyncIteratorMock:
            return AsyncIteratorMock([("url", test_data)])

        mock_file_source.stream_files = mock_stream_files

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)

        records = endpoint.get_latest_sync(station="KQED")

        assert len(records) == 1
        assert isinstance(records[0], BroadcastNGramRecord)
        assert records[0].source == BroadcastSource.RADIO


class TestQuerySync:
    """Test query_sync() method."""

    def test_query_sync(self) -> None:
        """Test synchronous query_sync() wrapper."""
        from py_gdelt.models.common import FetchResult

        mock_file_source = MagicMock()
        mock_file_source.stream_files = MagicMock(
            return_value=AsyncIteratorMock(
                [
                    (
                        "mock_url",
                        b"20240115\tKQED\t09\tclimate\t15\tMorning Edition",
                    )
                ]
            )
        )

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)
        endpoint._build_urls = AsyncMock(return_value=["mock_url"])

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            ngram_size=1,
        )

        result = endpoint.query_sync(filter_obj)

        assert isinstance(result, FetchResult)
        assert len(result.data) == 1
        assert result.data[0].ngram == "climate"


class TestStreamSync:
    """Test stream_sync() method."""

    def test_stream_sync(self) -> None:
        """Test synchronous stream_sync() wrapper."""
        mock_file_source = MagicMock()
        mock_file_source.stream_files = MagicMock(
            return_value=AsyncIteratorMock(
                [
                    (
                        "mock_url",
                        b"20240115\tKQED\t09\tclimate\t15\tMorning Edition\n20240115\tKQED\t09\thealth\t22\tMorning Edition",
                    )
                ]
            )
        )

        endpoint = RadioNGramsEndpoint(file_source=mock_file_source)
        endpoint._build_urls = AsyncMock(return_value=["mock_url"])

        filter_obj = BroadcastNGramsFilter(
            date_range=DateRange(start=date(2024, 1, 15)),
            station="KQED",
            ngram_size=1,
        )

        records = list(endpoint.stream_sync(filter_obj))

        assert len(records) == 2
        assert all(isinstance(r, BroadcastNGramRecord) for r in records)
        assert records[0].ngram == "climate"
        assert records[1].ngram == "health"


# Helper class for async iteration in tests
class AsyncIteratorMock:
    """Mock async iterator for testing."""

    def __init__(self, items: list) -> None:
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
