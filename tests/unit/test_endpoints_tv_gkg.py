"""Unit tests for TVGKGEndpoint.

Tests cover initialization, URL building, embargo warnings, and data streaming
for the Television Global Knowledge Graph endpoint.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_gdelt.endpoints.tv_gkg import TVGKGEndpoint
from py_gdelt.filters import DateRange, TVGKGFilter
from py_gdelt.models._internal import _RawGKG
from py_gdelt.models.gkg import TVGKGRecord


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
def tv_gkg_filter() -> TVGKGFilter:
    """Create test TVGKGFilter."""
    return TVGKGFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 1)),
        station="CNN",
    )


@pytest.fixture
def sample_raw_gkg() -> _RawGKG:
    """Create sample _RawGKG record for TV-GKG testing."""
    return _RawGKG(
        gkg_record_id="20240101120000-123",
        date="20240101120000",
        source_collection_id="1",
        source_common_name="CNN",
        document_identifier="https://archive.org/details/CNN_20240101_120000",
        counts_v1="",
        counts_v2="",
        themes_v1="ENV_CLIMATECHANGE;WB_635_ECONOMIC_ACTIVITY",
        themes_v2_enhanced="",
        locations_v1="New York;Washington",
        locations_v2_enhanced="",
        persons_v1="John Doe;Jane Smith",
        persons_v2_enhanced="",
        organizations_v1="United Nations",
        organizations_v2_enhanced="",
        tone="2.5,3.0,1.0,2.0,5.5,3.2,100",
        dates_v2="",
        gcam="",
        sharing_image=None,
        related_images=None,
        social_image_embeds=None,
        social_video_embeds=None,
        quotations=None,
        all_names=None,
        amounts=None,
        translation_info=None,
        extras_xml="<SPECIAL>CHARTIMECODEOFFSETTOC:0:00:00:00;100:00:01:23",
        is_translated=False,
    )


class TestTVGKGEndpointInit:
    """Test TVGKGEndpoint initialization."""

    def test_init_without_arguments(self) -> None:
        """Test initialization without arguments (creates owned FileSource)."""
        endpoint = TVGKGEndpoint()

        assert endpoint._file_source is not None
        assert endpoint._owns_sources is True
        assert endpoint._parser is not None
        assert endpoint.settings is not None

    def test_init_with_file_source(self, mock_file_source: MagicMock) -> None:
        """Test initialization with shared file source."""
        endpoint = TVGKGEndpoint(file_source=mock_file_source)

        assert endpoint._file_source is mock_file_source
        assert endpoint._owns_sources is False
        assert endpoint._parser is not None

    @pytest.mark.asyncio
    async def test_async_context_manager(self, mock_file_source: MagicMock) -> None:
        """Test async context manager entry/exit."""
        endpoint = TVGKGEndpoint(file_source=mock_file_source)

        async with endpoint as ep:
            assert ep is endpoint


class TestTVGKGEndpointURLBuilding:
    """Test URL building logic."""

    def test_build_urls_single_day(self, mock_file_source: MagicMock) -> None:
        """Test URL generation for a single day."""
        endpoint = TVGKGEndpoint(file_source=mock_file_source)
        filter_obj = TVGKGFilter(
            date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 1)),
        )

        urls = endpoint._build_urls(filter_obj)

        # Should generate URLs for 24 hours * 4 (every 15 minutes) = 96 URLs
        assert len(urls) == 96
        assert all("20240101" in url for url in urls)
        assert all(url.endswith(".gkg.csv.gz") for url in urls)
        assert urls[0] == f"{endpoint.BASE_URL}20240101000000.gkg.csv.gz"

    def test_build_urls_multiple_days(self, mock_file_source: MagicMock) -> None:
        """Test URL generation for multiple days."""
        endpoint = TVGKGEndpoint(file_source=mock_file_source)
        filter_obj = TVGKGFilter(
            date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 2)),
        )

        urls = endpoint._build_urls(filter_obj)

        # Should generate URLs for 2 days * 96 = 192 URLs
        assert len(urls) == 192
        assert any("20240101" in url for url in urls)
        assert any("20240102" in url for url in urls)


class TestTVGKGEndpointEmbargoCheck:
    """Test embargo period checking."""

    def test_embargo_check_old_data_no_warning(
        self,
        mock_file_source: MagicMock,
    ) -> None:
        """Test that old data (>48 hours) does not trigger warning."""
        endpoint = TVGKGEndpoint(file_source=mock_file_source)

        # Date 30 days ago (well past embargo)
        old_date = date.today() - timedelta(days=30)
        filter_obj = TVGKGFilter(
            date_range=DateRange(start=old_date, end=old_date),
        )

        with patch("warnings.warn") as mock_warn:
            endpoint._check_embargo(filter_obj)
            mock_warn.assert_not_called()

    def test_embargo_check_recent_data_warns(
        self,
        mock_file_source: MagicMock,
    ) -> None:
        """Test that recent data (<48 hours) triggers warning."""
        endpoint = TVGKGEndpoint(file_source=mock_file_source)

        # Date today (within embargo)
        recent_date = date.today()
        filter_obj = TVGKGFilter(
            date_range=DateRange(start=recent_date, end=recent_date),
        )

        with pytest.warns(UserWarning, match="48-hour embargo"):
            endpoint._check_embargo(filter_obj)


class TestTVGKGEndpointStreaming:
    """Test data streaming functionality."""

    @pytest.mark.asyncio
    async def test_stream_basic(
        self,
        mock_file_source: MagicMock,
        tv_gkg_filter: TVGKGFilter,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test basic streaming of TV-GKG records."""
        endpoint = TVGKGEndpoint(file_source=mock_file_source)

        # Mock stream_files to return sample data
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            # Create TSV data from sample record
            line = "\t".join(
                [
                    sample_raw_gkg.gkg_record_id,
                    sample_raw_gkg.date,
                    sample_raw_gkg.source_collection_id,
                    sample_raw_gkg.source_common_name,
                    sample_raw_gkg.document_identifier,
                    sample_raw_gkg.counts_v1,
                    sample_raw_gkg.counts_v2,
                    sample_raw_gkg.themes_v1,
                    sample_raw_gkg.themes_v2_enhanced,
                    sample_raw_gkg.locations_v1,
                    sample_raw_gkg.locations_v2_enhanced,
                    sample_raw_gkg.persons_v1,
                    sample_raw_gkg.persons_v2_enhanced,
                    sample_raw_gkg.organizations_v1,
                    sample_raw_gkg.organizations_v2_enhanced,
                    sample_raw_gkg.tone,
                    sample_raw_gkg.dates_v2,
                    sample_raw_gkg.gcam,
                    sample_raw_gkg.sharing_image or "",
                    sample_raw_gkg.related_images or "",
                    sample_raw_gkg.social_image_embeds or "",
                    sample_raw_gkg.social_video_embeds or "",
                    sample_raw_gkg.quotations or "",
                    sample_raw_gkg.all_names or "",
                    sample_raw_gkg.amounts or "",
                    sample_raw_gkg.translation_info or "",
                    sample_raw_gkg.extras_xml or "",
                ]
            )
            yield ("http://test.url", line.encode("utf-8"))

        mock_file_source.stream_files = mock_stream_files

        # Suppress embargo warning
        with patch("warnings.warn"):
            records = [record async for record in endpoint.stream(tv_gkg_filter)]

        assert len(records) == 1
        assert isinstance(records[0], TVGKGRecord)
        assert records[0].gkg_record_id == sample_raw_gkg.gkg_record_id
        assert records[0].source_identifier == "CNN"

    @pytest.mark.asyncio
    async def test_stream_with_station_filter(
        self,
        mock_file_source: MagicMock,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test streaming with station filtering."""
        endpoint = TVGKGEndpoint(file_source=mock_file_source)

        # Create filter for different station
        filter_obj = TVGKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            station="MSNBC",  # Different from sample (CNN)
        )

        # Mock stream_files
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            line = "\t".join(
                [
                    sample_raw_gkg.gkg_record_id,
                    sample_raw_gkg.date,
                    sample_raw_gkg.source_collection_id,
                    sample_raw_gkg.source_common_name,
                    sample_raw_gkg.document_identifier,
                    sample_raw_gkg.counts_v1,
                    sample_raw_gkg.counts_v2,
                    sample_raw_gkg.themes_v1,
                    sample_raw_gkg.themes_v2_enhanced,
                    sample_raw_gkg.locations_v1,
                    sample_raw_gkg.locations_v2_enhanced,
                    sample_raw_gkg.persons_v1,
                    sample_raw_gkg.persons_v2_enhanced,
                    sample_raw_gkg.organizations_v1,
                    sample_raw_gkg.organizations_v2_enhanced,
                    sample_raw_gkg.tone,
                    sample_raw_gkg.dates_v2,
                    sample_raw_gkg.gcam,
                    sample_raw_gkg.sharing_image or "",
                    sample_raw_gkg.related_images or "",
                    sample_raw_gkg.social_image_embeds or "",
                    sample_raw_gkg.social_video_embeds or "",
                    sample_raw_gkg.quotations or "",
                    sample_raw_gkg.all_names or "",
                    sample_raw_gkg.amounts or "",
                    sample_raw_gkg.translation_info or "",
                    sample_raw_gkg.extras_xml or "",
                ]
            )
            yield ("http://test.url", line.encode("utf-8"))

        mock_file_source.stream_files = mock_stream_files

        # Suppress embargo warning
        with patch("warnings.warn"):
            records = [record async for record in endpoint.stream(filter_obj)]

        # Should filter out CNN record
        assert len(records) == 0


class TestTVGKGEndpointQuery:
    """Test query() functionality."""

    @pytest.mark.asyncio
    async def test_query_returns_fetch_result(
        self,
        mock_file_source: MagicMock,
        tv_gkg_filter: TVGKGFilter,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test query() returns a FetchResult with collected records."""
        from py_gdelt.models.common import FetchResult

        endpoint = TVGKGEndpoint(file_source=mock_file_source)

        # Mock stream_files to return sample data
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            line = "\t".join(
                [
                    sample_raw_gkg.gkg_record_id,
                    sample_raw_gkg.date,
                    sample_raw_gkg.source_collection_id,
                    sample_raw_gkg.source_common_name,
                    sample_raw_gkg.document_identifier,
                    sample_raw_gkg.counts_v1,
                    sample_raw_gkg.counts_v2,
                    sample_raw_gkg.themes_v1,
                    sample_raw_gkg.themes_v2_enhanced,
                    sample_raw_gkg.locations_v1,
                    sample_raw_gkg.locations_v2_enhanced,
                    sample_raw_gkg.persons_v1,
                    sample_raw_gkg.persons_v2_enhanced,
                    sample_raw_gkg.organizations_v1,
                    sample_raw_gkg.organizations_v2_enhanced,
                    sample_raw_gkg.tone,
                    sample_raw_gkg.dates_v2,
                    sample_raw_gkg.gcam,
                    sample_raw_gkg.sharing_image or "",
                    sample_raw_gkg.related_images or "",
                    sample_raw_gkg.social_image_embeds or "",
                    sample_raw_gkg.social_video_embeds or "",
                    sample_raw_gkg.quotations or "",
                    sample_raw_gkg.all_names or "",
                    sample_raw_gkg.amounts or "",
                    sample_raw_gkg.translation_info or "",
                    sample_raw_gkg.extras_xml or "",
                ]
            )
            yield ("http://test.url", line.encode("utf-8"))

        mock_file_source.stream_files = mock_stream_files

        # Suppress embargo warning
        with patch("warnings.warn"):
            result = await endpoint.query(tv_gkg_filter)

        assert isinstance(result, FetchResult)
        assert len(result.data) == 1
        assert isinstance(result.data[0], TVGKGRecord)
        assert result.data[0].gkg_record_id == sample_raw_gkg.gkg_record_id
        assert result.failed == []

    @pytest.mark.asyncio
    async def test_query_empty_results(
        self,
        mock_file_source: MagicMock,
        tv_gkg_filter: TVGKGFilter,
    ) -> None:
        """Test query() returns empty FetchResult when no records match."""
        from py_gdelt.models.common import FetchResult

        endpoint = TVGKGEndpoint(file_source=mock_file_source)

        # Mock stream_files to return no data
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            if False:  # Never yield
                yield ("", b"")

        mock_file_source.stream_files = mock_stream_files

        # Suppress embargo warning
        with patch("warnings.warn"):
            result = await endpoint.query(tv_gkg_filter)

        assert isinstance(result, FetchResult)
        assert len(result.data) == 0
        assert result.failed == []


class TestTVGKGEndpointGetLatest:
    """Test get_latest functionality."""

    @pytest.mark.asyncio
    async def test_get_latest_success(
        self,
        mock_file_source: MagicMock,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test successful retrieval of latest TV-GKG records."""
        endpoint = TVGKGEndpoint(file_source=mock_file_source)

        # Mock the FileSource client's get method
        mock_client = AsyncMock()
        lastupdate_response = MagicMock()
        lastupdate_response.text = "1024 abc123 http://test.url/20240101120000.gkg.csv.gz"
        lastupdate_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=lastupdate_response)
        mock_file_source.client = mock_client

        # Mock stream_files
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            line = "\t".join(
                [
                    sample_raw_gkg.gkg_record_id,
                    sample_raw_gkg.date,
                    sample_raw_gkg.source_collection_id,
                    sample_raw_gkg.source_common_name,
                    sample_raw_gkg.document_identifier,
                    sample_raw_gkg.counts_v1,
                    sample_raw_gkg.counts_v2,
                    sample_raw_gkg.themes_v1,
                    sample_raw_gkg.themes_v2_enhanced,
                    sample_raw_gkg.locations_v1,
                    sample_raw_gkg.locations_v2_enhanced,
                    sample_raw_gkg.persons_v1,
                    sample_raw_gkg.persons_v2_enhanced,
                    sample_raw_gkg.organizations_v1,
                    sample_raw_gkg.organizations_v2_enhanced,
                    sample_raw_gkg.tone,
                    sample_raw_gkg.dates_v2,
                    sample_raw_gkg.gcam,
                    sample_raw_gkg.sharing_image or "",
                    sample_raw_gkg.related_images or "",
                    sample_raw_gkg.social_image_embeds or "",
                    sample_raw_gkg.social_video_embeds or "",
                    sample_raw_gkg.quotations or "",
                    sample_raw_gkg.all_names or "",
                    sample_raw_gkg.amounts or "",
                    sample_raw_gkg.translation_info or "",
                    sample_raw_gkg.extras_xml or "",
                ]
            )
            yield ("http://test.url", line.encode("utf-8"))

        mock_file_source.stream_files = mock_stream_files

        records = await endpoint.get_latest()

        assert len(records) == 1
        assert isinstance(records[0], TVGKGRecord)

    @pytest.mark.asyncio
    async def test_get_latest_no_file_found(
        self,
        mock_file_source: MagicMock,
    ) -> None:
        """Test get_latest when no GKG file is in lastupdate.txt."""
        endpoint = TVGKGEndpoint(file_source=mock_file_source)

        # Mock the FileSource client's get method
        mock_client = AsyncMock()
        lastupdate_response = MagicMock()
        lastupdate_response.text = "1024 abc123 http://test.url/20240101120000.export.csv"
        lastupdate_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=lastupdate_response)
        mock_file_source.client = mock_client

        records = await endpoint.get_latest()

        assert len(records) == 0


class TestTVGKGEndpointSyncWrappers:
    """Test synchronous wrapper methods."""

    def test_query_sync(
        self,
        mock_file_source: MagicMock,
        tv_gkg_filter: TVGKGFilter,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test query_sync wrapper returns FetchResult."""
        endpoint = TVGKGEndpoint(file_source=mock_file_source)

        # Mock stream_files to return sample data
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            line = "\t".join(
                [
                    sample_raw_gkg.gkg_record_id,
                    sample_raw_gkg.date,
                    sample_raw_gkg.source_collection_id,
                    sample_raw_gkg.source_common_name,
                    sample_raw_gkg.document_identifier,
                    sample_raw_gkg.counts_v1,
                    sample_raw_gkg.counts_v2,
                    sample_raw_gkg.themes_v1,
                    sample_raw_gkg.themes_v2_enhanced,
                    sample_raw_gkg.locations_v1,
                    sample_raw_gkg.locations_v2_enhanced,
                    sample_raw_gkg.persons_v1,
                    sample_raw_gkg.persons_v2_enhanced,
                    sample_raw_gkg.organizations_v1,
                    sample_raw_gkg.organizations_v2_enhanced,
                    sample_raw_gkg.tone,
                    sample_raw_gkg.dates_v2,
                    sample_raw_gkg.gcam,
                    sample_raw_gkg.sharing_image or "",
                    sample_raw_gkg.related_images or "",
                    sample_raw_gkg.social_image_embeds or "",
                    sample_raw_gkg.social_video_embeds or "",
                    sample_raw_gkg.quotations or "",
                    sample_raw_gkg.all_names or "",
                    sample_raw_gkg.amounts or "",
                    sample_raw_gkg.translation_info or "",
                    sample_raw_gkg.extras_xml or "",
                ]
            )
            yield ("http://test.url", line.encode("utf-8"))

        mock_file_source.stream_files = mock_stream_files

        # Suppress embargo warning
        with patch("warnings.warn"):
            result = endpoint.query_sync(tv_gkg_filter)

        assert len(result) == 1
        assert isinstance(result.data[0], TVGKGRecord)
        assert result.data[0].gkg_record_id == sample_raw_gkg.gkg_record_id

    def test_stream_sync(
        self,
        mock_file_source: MagicMock,
        tv_gkg_filter: TVGKGFilter,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test stream_sync wrapper yields TVGKGRecords."""
        endpoint = TVGKGEndpoint(file_source=mock_file_source)

        # Mock stream_files to return sample data
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            line = "\t".join(
                [
                    sample_raw_gkg.gkg_record_id,
                    sample_raw_gkg.date,
                    sample_raw_gkg.source_collection_id,
                    sample_raw_gkg.source_common_name,
                    sample_raw_gkg.document_identifier,
                    sample_raw_gkg.counts_v1,
                    sample_raw_gkg.counts_v2,
                    sample_raw_gkg.themes_v1,
                    sample_raw_gkg.themes_v2_enhanced,
                    sample_raw_gkg.locations_v1,
                    sample_raw_gkg.locations_v2_enhanced,
                    sample_raw_gkg.persons_v1,
                    sample_raw_gkg.persons_v2_enhanced,
                    sample_raw_gkg.organizations_v1,
                    sample_raw_gkg.organizations_v2_enhanced,
                    sample_raw_gkg.tone,
                    sample_raw_gkg.dates_v2,
                    sample_raw_gkg.gcam,
                    sample_raw_gkg.sharing_image or "",
                    sample_raw_gkg.related_images or "",
                    sample_raw_gkg.social_image_embeds or "",
                    sample_raw_gkg.social_video_embeds or "",
                    sample_raw_gkg.quotations or "",
                    sample_raw_gkg.all_names or "",
                    sample_raw_gkg.amounts or "",
                    sample_raw_gkg.translation_info or "",
                    sample_raw_gkg.extras_xml or "",
                ]
            )
            yield ("http://test.url", line.encode("utf-8"))

        mock_file_source.stream_files = mock_stream_files

        # Suppress embargo warning
        with patch("warnings.warn"):
            records = list(endpoint.stream_sync(tv_gkg_filter))

        assert len(records) == 1
        assert isinstance(records[0], TVGKGRecord)
        assert records[0].gkg_record_id == sample_raw_gkg.gkg_record_id

    def test_get_latest_sync(
        self,
        mock_file_source: MagicMock,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test get_latest_sync wrapper returns list of TVGKGRecords."""
        endpoint = TVGKGEndpoint(file_source=mock_file_source)

        # Mock the FileSource client's get method
        mock_client = AsyncMock()
        lastupdate_response = MagicMock()
        lastupdate_response.text = "1024 abc123 http://test.url/20240101120000.gkg.csv.gz"
        lastupdate_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=lastupdate_response)
        mock_file_source.client = mock_client

        # Mock stream_files
        async def mock_stream_files(urls: list[str]) -> AsyncIterator[tuple[str, bytes]]:
            line = "\t".join(
                [
                    sample_raw_gkg.gkg_record_id,
                    sample_raw_gkg.date,
                    sample_raw_gkg.source_collection_id,
                    sample_raw_gkg.source_common_name,
                    sample_raw_gkg.document_identifier,
                    sample_raw_gkg.counts_v1,
                    sample_raw_gkg.counts_v2,
                    sample_raw_gkg.themes_v1,
                    sample_raw_gkg.themes_v2_enhanced,
                    sample_raw_gkg.locations_v1,
                    sample_raw_gkg.locations_v2_enhanced,
                    sample_raw_gkg.persons_v1,
                    sample_raw_gkg.persons_v2_enhanced,
                    sample_raw_gkg.organizations_v1,
                    sample_raw_gkg.organizations_v2_enhanced,
                    sample_raw_gkg.tone,
                    sample_raw_gkg.dates_v2,
                    sample_raw_gkg.gcam,
                    sample_raw_gkg.sharing_image or "",
                    sample_raw_gkg.related_images or "",
                    sample_raw_gkg.social_image_embeds or "",
                    sample_raw_gkg.social_video_embeds or "",
                    sample_raw_gkg.quotations or "",
                    sample_raw_gkg.all_names or "",
                    sample_raw_gkg.amounts or "",
                    sample_raw_gkg.translation_info or "",
                    sample_raw_gkg.extras_xml or "",
                ]
            )
            yield ("http://test.url", line.encode("utf-8"))

        mock_file_source.stream_files = mock_stream_files

        records = endpoint.get_latest_sync()

        assert len(records) == 1
        assert isinstance(records[0], TVGKGRecord)
