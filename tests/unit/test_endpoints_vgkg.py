"""Unit tests for VGKGEndpoint.

Tests cover initialization, client lifecycle, URL building, and data streaming
for the Visual Global Knowledge Graph endpoint.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest

from py_gdelt.endpoints.vgkg import VGKGEndpoint
from py_gdelt.filters import DateRange, VGKGFilter
from py_gdelt.models._internal import _RawVGKG
from py_gdelt.models.vgkg import VGKGRecord


if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@pytest.fixture
def mock_file_source() -> MagicMock:
    """Create mock FileSource."""
    mock = MagicMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def vgkg_filter() -> VGKGFilter:
    """Create test VGKGFilter."""
    return VGKGFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 1)),
        domain="cnn.com",
    )


@pytest.fixture
def sample_raw_vgkg() -> _RawVGKG:
    """Create sample _RawVGKG record for testing."""
    return _RawVGKG(
        date="20240101120000",
        document_identifier="https://www.cnn.com/article",
        image_url="https://www.cnn.com/image.jpg",
        labels="Smile<FIELD>0.95<FIELD>/m/0000<RECORD>Face<FIELD>0.90<FIELD>/m/0001",
        logos="",
        web_entities="",
        safe_search="0<FIELD>0<FIELD>0<FIELD>0",
        faces="",
        ocr_text="",
        landmark_annotations="",
        domain="cnn.com",
        raw_json="{}",
    )


class TestVGKGEndpointInit:
    """Test VGKGEndpoint initialization."""

    def test_init_without_arguments(self) -> None:
        """Test initialization without arguments (creates owned FileSource and client)."""
        endpoint = VGKGEndpoint()

        assert endpoint._file_source is not None
        assert endpoint._owns_sources is True
        assert endpoint._client is not None
        assert endpoint._owns_client is True
        assert endpoint._parser is not None
        assert endpoint.settings is not None

    def test_init_with_file_source(self, mock_file_source: MagicMock) -> None:
        """Test initialization with shared file source."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)

        assert endpoint._file_source is mock_file_source
        assert endpoint._owns_sources is False
        assert endpoint._client is not None
        assert endpoint._owns_client is True
        assert endpoint._parser is not None

    @pytest.mark.asyncio
    async def test_async_context_manager(self, mock_file_source: MagicMock) -> None:
        """Test async context manager entry/exit."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)

        async with endpoint as ep:
            assert ep is endpoint

        # Client should be closed after exit (if owned)
        assert endpoint._client is not None


class TestVGKGEndpointURLBuilding:
    """Test URL building logic."""

    def test_build_urls_single_day(self, mock_file_source: MagicMock) -> None:
        """Test URL generation for a single day."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)
        filter_obj = VGKGFilter(
            date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 1)),
        )

        urls = endpoint._build_urls(filter_obj)

        # Should generate URLs for 24 hours * 4 (every 15 minutes) = 96 URLs
        assert len(urls) == 96
        assert all("20240101" in url for url in urls)
        assert all(url.endswith(".vgkg.csv.gz") for url in urls)
        assert urls[0].endswith("20240101000000.vgkg.csv.gz")

    def test_build_urls_multiple_days(self, mock_file_source: MagicMock) -> None:
        """Test URL generation for multiple days."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)
        filter_obj = VGKGFilter(
            date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 2)),
        )

        urls = endpoint._build_urls(filter_obj)

        # Should generate URLs for 2 days * 96 = 192 URLs
        assert len(urls) == 192
        assert any("20240101" in url for url in urls)
        assert any("20240102" in url for url in urls)


class TestVGKGEndpointFiltering:
    """Test filtering logic."""

    def test_matches_filter_domain_match(
        self,
        mock_file_source: MagicMock,
        sample_raw_vgkg: _RawVGKG,
    ) -> None:
        """Test domain filtering with matching domain."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)
        record = VGKGRecord.from_raw(sample_raw_vgkg)
        filter_obj = VGKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            domain="cnn.com",
        )

        assert endpoint._matches_filter(record, filter_obj) is True

    def test_matches_filter_domain_mismatch(
        self,
        mock_file_source: MagicMock,
        sample_raw_vgkg: _RawVGKG,
    ) -> None:
        """Test domain filtering with non-matching domain."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)
        record = VGKGRecord.from_raw(sample_raw_vgkg)
        filter_obj = VGKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            domain="bbc.com",
        )

        assert endpoint._matches_filter(record, filter_obj) is False

    def test_matches_filter_label_confidence(
        self,
        mock_file_source: MagicMock,
        sample_raw_vgkg: _RawVGKG,
    ) -> None:
        """Test label confidence filtering."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)
        record = VGKGRecord.from_raw(sample_raw_vgkg)

        # Should match (has label with 0.95 confidence)
        filter_obj = VGKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            min_label_confidence=0.9,
        )
        assert endpoint._matches_filter(record, filter_obj) is True

        # Should not match (threshold too high)
        filter_obj = VGKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            min_label_confidence=0.99,
        )
        assert endpoint._matches_filter(record, filter_obj) is False


class TestVGKGEndpointStreaming:
    """Test data streaming functionality."""

    @pytest.mark.asyncio
    async def test_stream_basic(
        self,
        mock_file_source: MagicMock,
        vgkg_filter: VGKGFilter,
        sample_raw_vgkg: _RawVGKG,
    ) -> None:
        """Test basic streaming of VGKG records."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)

        # Mock stream_files to return sample data
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            # Create TSV data from sample record
            line = "\t".join(
                [
                    sample_raw_vgkg.date,
                    sample_raw_vgkg.document_identifier,
                    sample_raw_vgkg.image_url,
                    sample_raw_vgkg.labels,
                    sample_raw_vgkg.logos,
                    sample_raw_vgkg.web_entities,
                    sample_raw_vgkg.safe_search,
                    sample_raw_vgkg.faces,
                    sample_raw_vgkg.ocr_text,
                    sample_raw_vgkg.landmark_annotations,
                    sample_raw_vgkg.domain,
                    sample_raw_vgkg.raw_json,
                ]
            )
            yield ("http://test.url", line.encode("utf-8"))

        mock_file_source.stream_files = mock_stream_files

        records = [record async for record in endpoint.stream(vgkg_filter)]

        assert len(records) == 1
        assert isinstance(records[0], VGKGRecord)
        assert records[0].domain == "cnn.com"


class TestVGKGEndpointGetLatest:
    """Test get_latest functionality."""

    @pytest.mark.asyncio
    async def test_get_latest_success(
        self,
        mock_file_source: MagicMock,
        sample_raw_vgkg: _RawVGKG,
    ) -> None:
        """Test successful retrieval of latest VGKG records."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)

        # Mock the client's get method
        mock_client = AsyncMock()
        lastupdate_response = MagicMock()
        lastupdate_response.text = "1024 abc123 http://test.url/20240101120000.vgkg.csv.gz"
        lastupdate_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=lastupdate_response)
        endpoint._client = mock_client

        # Mock stream_files
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            line = "\t".join(
                [
                    sample_raw_vgkg.date,
                    sample_raw_vgkg.document_identifier,
                    sample_raw_vgkg.image_url,
                    sample_raw_vgkg.labels,
                    sample_raw_vgkg.logos,
                    sample_raw_vgkg.web_entities,
                    sample_raw_vgkg.safe_search,
                    sample_raw_vgkg.faces,
                    sample_raw_vgkg.ocr_text,
                    sample_raw_vgkg.landmark_annotations,
                    sample_raw_vgkg.domain,
                    sample_raw_vgkg.raw_json,
                ]
            )
            yield ("http://test.url", line.encode("utf-8"))

        mock_file_source.stream_files = mock_stream_files

        records = await endpoint.get_latest()

        assert len(records) == 1
        assert isinstance(records[0], VGKGRecord)

    @pytest.mark.asyncio
    async def test_get_latest_no_file_found(
        self,
        mock_file_source: MagicMock,
    ) -> None:
        """Test get_latest when no VGKG file is in lastupdate.txt."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)

        # Mock the client's get method
        mock_client = AsyncMock()
        lastupdate_response = MagicMock()
        lastupdate_response.text = "1024 abc123 http://test.url/20240101120000.export.csv"
        lastupdate_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=lastupdate_response)
        endpoint._client = mock_client

        records = await endpoint.get_latest()

        assert len(records) == 0

    @pytest.mark.asyncio
    async def test_get_latest_reuses_client(
        self,
        mock_file_source: MagicMock,
    ) -> None:
        """Test that get_latest reuses the stored client, not creating temporary ones."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)

        # Store reference to original client
        original_client = endpoint._client

        # Mock the client's get method
        mock_client = AsyncMock()
        lastupdate_response = MagicMock()
        lastupdate_response.text = "1024 abc123 http://test.url/20240101120000.vgkg.csv.gz"
        lastupdate_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=lastupdate_response)
        endpoint._client = mock_client

        # Mock stream_files to return empty
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            if False:  # Never yield
                yield ("", b"")

        mock_file_source.stream_files = mock_stream_files

        await endpoint.get_latest()

        # Verify the mock client was called (proving we used the stored client)
        mock_client.get.assert_called_once()

        # Verify we didn't replace the client
        assert endpoint._client is mock_client


class TestVGKGEndpointSyncWrappers:
    """Test synchronous wrapper methods."""

    def test_query_sync(
        self,
        mock_file_source: MagicMock,
        vgkg_filter: VGKGFilter,
        sample_raw_vgkg: _RawVGKG,
    ) -> None:
        """Test query_sync wrapper returns FetchResult."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)

        # Mock stream_files to return sample data
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            line = "\t".join(
                [
                    sample_raw_vgkg.date,
                    sample_raw_vgkg.document_identifier,
                    sample_raw_vgkg.image_url,
                    sample_raw_vgkg.labels,
                    sample_raw_vgkg.logos,
                    sample_raw_vgkg.web_entities,
                    sample_raw_vgkg.safe_search,
                    sample_raw_vgkg.faces,
                    sample_raw_vgkg.ocr_text,
                    sample_raw_vgkg.landmark_annotations,
                    sample_raw_vgkg.domain,
                    sample_raw_vgkg.raw_json,
                ]
            )
            yield ("http://test.url", line.encode("utf-8"))

        mock_file_source.stream_files = mock_stream_files

        result = endpoint.query_sync(vgkg_filter)

        assert len(result) == 1
        assert isinstance(result.data[0], VGKGRecord)
        assert result.data[0].domain == "cnn.com"

    def test_stream_sync(
        self,
        mock_file_source: MagicMock,
        vgkg_filter: VGKGFilter,
        sample_raw_vgkg: _RawVGKG,
    ) -> None:
        """Test stream_sync wrapper yields VGKGRecords."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)

        # Mock stream_files to return sample data
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            line = "\t".join(
                [
                    sample_raw_vgkg.date,
                    sample_raw_vgkg.document_identifier,
                    sample_raw_vgkg.image_url,
                    sample_raw_vgkg.labels,
                    sample_raw_vgkg.logos,
                    sample_raw_vgkg.web_entities,
                    sample_raw_vgkg.safe_search,
                    sample_raw_vgkg.faces,
                    sample_raw_vgkg.ocr_text,
                    sample_raw_vgkg.landmark_annotations,
                    sample_raw_vgkg.domain,
                    sample_raw_vgkg.raw_json,
                ]
            )
            yield ("http://test.url", line.encode("utf-8"))

        mock_file_source.stream_files = mock_stream_files

        records = list(endpoint.stream_sync(vgkg_filter))

        assert len(records) == 1
        assert isinstance(records[0], VGKGRecord)
        assert records[0].domain == "cnn.com"

    def test_get_latest_sync(
        self,
        mock_file_source: MagicMock,
        sample_raw_vgkg: _RawVGKG,
    ) -> None:
        """Test get_latest_sync wrapper returns list of VGKGRecords."""
        endpoint = VGKGEndpoint(file_source=mock_file_source)

        # Mock the client's get method
        mock_client = AsyncMock()
        lastupdate_response = MagicMock()
        lastupdate_response.text = "1024 abc123 http://test.url/20240101120000.vgkg.csv.gz"
        lastupdate_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=lastupdate_response)
        endpoint._client = mock_client

        # Mock stream_files
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            line = "\t".join(
                [
                    sample_raw_vgkg.date,
                    sample_raw_vgkg.document_identifier,
                    sample_raw_vgkg.image_url,
                    sample_raw_vgkg.labels,
                    sample_raw_vgkg.logos,
                    sample_raw_vgkg.web_entities,
                    sample_raw_vgkg.safe_search,
                    sample_raw_vgkg.faces,
                    sample_raw_vgkg.ocr_text,
                    sample_raw_vgkg.landmark_annotations,
                    sample_raw_vgkg.domain,
                    sample_raw_vgkg.raw_json,
                ]
            )
            yield ("http://test.url", line.encode("utf-8"))

        mock_file_source.stream_files = mock_stream_files

        records = endpoint.get_latest_sync()

        assert len(records) == 1
        assert isinstance(records[0], VGKGRecord)
