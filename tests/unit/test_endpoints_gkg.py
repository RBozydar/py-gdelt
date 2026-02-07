"""Unit tests for GKGEndpoint.

Tests cover data fetching, streaming, source orchestration, error handling,
and sync/async wrappers for the GDELT Global Knowledge Graph endpoint.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_gdelt.endpoints.gkg import GKGEndpoint
from py_gdelt.exceptions import APIError, ConfigurationError, RateLimitError
from py_gdelt.filters import DateRange, GKGFilter
from py_gdelt.models._internal import _RawGKG
from py_gdelt.models.gkg import GKGRecord
from py_gdelt.sources.metadata import QueryEstimate


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Collection


@pytest.fixture
def mock_file_source() -> MagicMock:
    """Create mock FileSource."""
    mock = MagicMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_bigquery_source() -> MagicMock:
    """Create mock BigQuerySource."""
    mock = MagicMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def gkg_filter() -> GKGFilter:
    """Create test GKGFilter."""
    return GKGFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 2)),
        themes=["ENV_CLIMATECHANGE"],
    )


@pytest.fixture
def sample_raw_gkg() -> _RawGKG:
    """Create sample _RawGKG record for testing."""
    return _RawGKG(
        gkg_record_id="20240101120000-123",
        date="20240101120000",
        source_collection_id="1",
        source_common_name="Example News",
        document_identifier="https://example.com/article",
        counts_v1="",
        counts_v2="",
        themes_v1="",
        themes_v2_enhanced="ENV_CLIMATECHANGE,100;WB_635_ECONOMIC_ACTIVITY,200",
        locations_v1="",
        locations_v2_enhanced="1#New York#US#NY##40.7128#-74.0060#12345",
        persons_v1="",
        persons_v2_enhanced="John Doe,50;Jane Smith,150",
        organizations_v1="",
        organizations_v2_enhanced="United Nations,80",
        tone="2.5,3.0,1.0,2.0,5.5,3.2,100",
        dates_v2="",
        gcam="c2.14:3.2;c5.1:0.85",
        sharing_image="https://example.com/image.jpg",
        related_images=None,
        social_image_embeds=None,
        social_video_embeds=None,
        quotations='50|20|said|"This is a test quote"',
        all_names="John Doe;Jane Smith",
        amounts="100.5,dollars,75",
        translation_info=None,
        extras_xml=None,
        is_translated=False,
    )


class TestGKGEndpointInit:
    """Test GKGEndpoint initialization."""

    def test_init_with_file_source_only(self, mock_file_source: MagicMock) -> None:
        """Test initialization with only file source."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        assert endpoint._fetcher is not None
        assert endpoint._settings is None

    def test_init_with_both_sources(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
    ) -> None:
        """Test initialization with both file and BigQuery sources."""
        endpoint = GKGEndpoint(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
            fallback_enabled=True,
        )

        assert endpoint._fetcher is not None

    def test_init_with_fallback_disabled(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
    ) -> None:
        """Test initialization with fallback disabled."""
        endpoint = GKGEndpoint(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
            fallback_enabled=False,
        )

        assert endpoint._fetcher is not None

    def test_init_with_custom_error_policy(self, mock_file_source: MagicMock) -> None:
        """Test initialization with custom error policy."""
        endpoint = GKGEndpoint(
            file_source=mock_file_source,
            error_policy="raise",
        )

        assert endpoint._fetcher is not None


class TestGKGEndpointQuery:
    """Test the query() method."""

    @pytest.mark.asyncio
    async def test_query_basic(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test basic query returning GKG records."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        # Mock the fetcher to yield raw GKG records
        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            yield sample_raw_gkg

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg):
            result = await endpoint.query(gkg_filter)

            assert len(result) == 1
            assert isinstance(result.data[0], GKGRecord)
            assert result.data[0].record_id == "20240101120000-123"
            assert result.data[0].source_name == "Example News"
            assert result.complete is True

    @pytest.mark.asyncio
    async def test_query_multiple_records(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test query returning multiple GKG records."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        # Create multiple raw records
        raw_gkg_2 = _RawGKG(
            gkg_record_id="20240101130000-456",
            date="20240101130000",
            source_collection_id="1",
            source_common_name="Another Source",
            document_identifier="https://example.com/article2",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="ENV_CLIMATECHANGE,50",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="1.0,2.0,0.5,1.5,3.0,2.5,80",
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
            extras_xml=None,
            is_translated=False,
        )

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            yield sample_raw_gkg
            yield raw_gkg_2

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg):
            result = await endpoint.query(gkg_filter)

            assert len(result) == 2
            assert result.data[0].record_id == "20240101120000-123"
            assert result.data[1].record_id == "20240101130000-456"
            assert result.data[1].source_name == "Another Source"

    @pytest.mark.asyncio
    async def test_query_empty_results(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
    ) -> None:
        """Test query with no matching records."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            # Yield nothing
            if False:  # type: ignore[unreachable]
                yield

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg):
            result = await endpoint.query(gkg_filter)

            assert len(result) == 0
            assert result.data == []
            assert result.complete is True

    @pytest.mark.asyncio
    async def test_query_with_use_bigquery(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
        gkg_filter: GKGFilter,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test query with use_bigquery=True."""
        endpoint = GKGEndpoint(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
        )

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            yield sample_raw_gkg

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg) as mock_fetch:
            result = await endpoint.query(gkg_filter, use_bigquery=True)

            assert len(result) == 1
            # Verify use_bigquery was passed through
            mock_fetch.assert_called_once()
            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs["use_bigquery"] is True

    @pytest.mark.asyncio
    async def test_query_conversion_error_handling(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
    ) -> None:
        """Test query handles conversion errors gracefully."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        # Create a malformed raw record that will fail conversion
        bad_raw_gkg = _RawGKG(
            gkg_record_id="BAD",
            date="INVALID_DATE",  # This will cause parsing to fail
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="https://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
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
            extras_xml=None,
            is_translated=False,
        )

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            yield bad_raw_gkg

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg):
            # Should not raise, but should skip the bad record
            result = await endpoint.query(gkg_filter)
            assert len(result) == 0


class TestGKGEndpointStream:
    """Test the stream() method."""

    @pytest.mark.asyncio
    async def test_stream_basic(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test basic streaming of GKG records."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            yield sample_raw_gkg

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg):
            records = [record async for record in endpoint.stream(gkg_filter)]

            assert len(records) == 1
            assert isinstance(records[0], GKGRecord)
            assert records[0].record_id == "20240101120000-123"

    @pytest.mark.asyncio
    async def test_stream_multiple_records(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
    ) -> None:
        """Test streaming multiple GKG records."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            for i in range(5):
                raw_gkg = _RawGKG(
                    gkg_record_id=f"2024010112000{i}-{i}",
                    date=f"2024010112000{i}",
                    source_collection_id="1",
                    source_common_name=f"Source {i}",
                    document_identifier=f"https://example.com/{i}",
                    counts_v1="",
                    counts_v2="",
                    themes_v1="",
                    themes_v2_enhanced="ENV_CLIMATECHANGE,100",
                    locations_v1="",
                    locations_v2_enhanced="",
                    persons_v1="",
                    persons_v2_enhanced="",
                    organizations_v1="",
                    organizations_v2_enhanced="",
                    tone="1.0,2.0,0.5,1.5,3.0,2.5,80",
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
                    extras_xml=None,
                    is_translated=False,
                )
                yield raw_gkg

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg):
            records = [record async for record in endpoint.stream(gkg_filter)]

            assert len(records) == 5
            assert all(isinstance(r, GKGRecord) for r in records)
            assert records[0].source_name == "Source 0"
            assert records[4].source_name == "Source 4"

    @pytest.mark.asyncio
    async def test_stream_early_break(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
    ) -> None:
        """Test streaming with early break."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            for i in range(100):
                raw_gkg = _RawGKG(
                    gkg_record_id=f"20240101120000-{i}",
                    date="20240101120000",  # Fixed valid timestamp
                    source_collection_id="1",
                    source_common_name=f"Source {i}",
                    document_identifier=f"https://example.com/{i}",
                    counts_v1="",
                    counts_v2="",
                    themes_v1="",
                    themes_v2_enhanced="ENV_CLIMATECHANGE,100",  # Match filter
                    locations_v1="",
                    locations_v2_enhanced="",
                    persons_v1="",
                    persons_v2_enhanced="",
                    organizations_v1="",
                    organizations_v2_enhanced="",
                    tone="",
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
                    extras_xml=None,
                    is_translated=False,
                )
                yield raw_gkg

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg):
            records = []
            async for record in endpoint.stream(gkg_filter):
                records.append(record)
                if len(records) >= 10:
                    break

            # Should only fetch 10 records due to early break
            assert len(records) == 10

    @pytest.mark.asyncio
    async def test_stream_conversion_error_skip(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test stream skips records with conversion errors."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        # Mix of good and bad records
        bad_raw_gkg = _RawGKG(
            gkg_record_id="BAD",
            date="INVALID",
            source_collection_id="1",
            source_common_name="Bad",
            document_identifier="https://bad.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
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
            extras_xml=None,
            is_translated=False,
        )

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            yield sample_raw_gkg
            yield bad_raw_gkg  # This will fail conversion
            yield sample_raw_gkg

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg):
            records = [record async for record in endpoint.stream(gkg_filter)]

            # Should only get 2 good records (bad one skipped)
            assert len(records) == 2


class TestGKGEndpointSyncWrappers:
    """Test synchronous wrapper methods."""

    def test_query_sync(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test query_sync wrapper."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            yield sample_raw_gkg

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg):
            result = endpoint.query_sync(gkg_filter)

            assert len(result) == 1
            assert isinstance(result.data[0], GKGRecord)
            assert result.data[0].record_id == "20240101120000-123"

    def test_stream_sync(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
    ) -> None:
        """Test stream_sync wrapper."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            for i in range(3):
                raw_gkg = _RawGKG(
                    gkg_record_id=f"2024010112000{i}-{i}",
                    date=f"2024010112000{i}",
                    source_collection_id="1",
                    source_common_name=f"Source {i}",
                    document_identifier=f"https://example.com/{i}",
                    counts_v1="",
                    counts_v2="",
                    themes_v1="",
                    themes_v2_enhanced="ENV_CLIMATECHANGE,100",
                    locations_v1="",
                    locations_v2_enhanced="",
                    persons_v1="",
                    persons_v2_enhanced="",
                    organizations_v1="",
                    organizations_v2_enhanced="",
                    tone="1.0,2.0,0.5,1.5,3.0,2.5,80",
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
                    extras_xml=None,
                    is_translated=False,
                )
                yield raw_gkg

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg):
            records = []
            for record in endpoint.stream_sync(gkg_filter):
                records.append(record)

            assert len(records) == 3
            assert all(isinstance(r, GKGRecord) for r in records)


class TestGKGEndpointErrorHandling:
    """Test error handling and propagation."""

    @pytest.mark.asyncio
    async def test_query_rate_limit_error(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
    ) -> None:
        """Test query propagates rate limit errors."""
        endpoint = GKGEndpoint(file_source=mock_file_source, fallback_enabled=False)

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            msg = "Rate limited"
            raise RateLimitError(msg, retry_after=60)
            if False:  # type: ignore[unreachable]
                yield

        with (
            patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg),
            pytest.raises(RateLimitError),
        ):
            await endpoint.query(gkg_filter)

    @pytest.mark.asyncio
    async def test_query_api_error(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
    ) -> None:
        """Test query propagates API errors."""
        endpoint = GKGEndpoint(file_source=mock_file_source, fallback_enabled=False)

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            msg = "API failed"
            raise APIError(msg)
            if False:  # type: ignore[unreachable]
                yield

        with (
            patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg),
            pytest.raises(APIError),
        ):
            await endpoint.query(gkg_filter)

    @pytest.mark.asyncio
    async def test_query_configuration_error(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
    ) -> None:
        """Test query propagates configuration errors."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            msg = "BigQuery not configured"
            raise ConfigurationError(msg)
            if False:  # type: ignore[unreachable]
                yield

        with (
            patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg),
            pytest.raises(ConfigurationError),
        ):
            await endpoint.query(gkg_filter)


class TestGKGEndpointIntegration:
    """Test realistic usage scenarios."""

    @pytest.mark.asyncio
    async def test_full_workflow(
        self,
        mock_file_source: MagicMock,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test a complete GKG query workflow."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        # Create a filter
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
            themes=["ENV_CLIMATECHANGE"],
            min_tone=0.0,
        )

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            yield sample_raw_gkg

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg):
            # Query data
            result = await endpoint.query(filter_obj)

            # Verify result structure
            assert result.complete is True
            assert len(result) == 1

            # Access record data
            record = result.data[0]
            assert record.record_id == "20240101120000-123"
            assert record.source_url == "https://example.com/article"
            assert len(record.themes) > 0
            assert record.primary_theme == "ENV_CLIMATECHANGE"
            assert record.has_quotations is True
            assert record.tone is not None
            assert record.tone.tone == 2.5

    @pytest.mark.asyncio
    async def test_streaming_workflow(
        self,
        mock_file_source: MagicMock,
    ) -> None:
        """Test streaming large result sets."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            country="USA",
        )

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            for i in range(50):
                raw_gkg = _RawGKG(
                    gkg_record_id=f"2024010112{i:04d}-{i}",
                    date=f"2024010112{i:04d}",
                    source_collection_id="1",
                    source_common_name=f"Source {i}",
                    document_identifier=f"https://example.com/{i}",
                    counts_v1="",
                    counts_v2="",
                    themes_v1="",
                    themes_v2_enhanced=f"THEME_{i},100",
                    locations_v1="",
                    locations_v2_enhanced="1#New York#US#NY##40.7128#-74.0060#12345",
                    persons_v1="",
                    persons_v2_enhanced="",
                    organizations_v1="",
                    organizations_v2_enhanced="",
                    tone="1.0,2.0,0.5,1.5,3.0,2.5,80",
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
                    extras_xml=None,
                    is_translated=False,
                )
                yield raw_gkg

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg):
            # Stream and process records one at a time
            count = 0
            async for record in endpoint.stream(filter_obj):
                assert isinstance(record, GKGRecord)
                count += 1
                if count >= 25:
                    break  # Early termination

            assert count == 25

    @pytest.mark.asyncio
    async def test_filter_theme_extraction(
        self,
        mock_file_source: MagicMock,
        sample_raw_gkg: _RawGKG,
    ) -> None:
        """Test extracting and filtering by themes."""
        endpoint = GKGEndpoint(file_source=mock_file_source)

        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            themes=["ENV_CLIMATECHANGE"],
        )

        async def mock_fetch_gkg(
            filter_obj: GKGFilter,
            *,
            use_bigquery: bool = False,
            columns: Collection[str] | None = None,
            limit: int | None = None,
        ) -> AsyncIterator[_RawGKG]:
            yield sample_raw_gkg

        with patch.object(endpoint._fetcher, "fetch_gkg", side_effect=mock_fetch_gkg):
            result = await endpoint.query(filter_obj)

            record = result.data[0]
            # Check theme parsing
            assert len(record.themes) > 0
            assert any(t.name == "ENV_CLIMATECHANGE" for t in record.themes)
            assert record.primary_theme == "ENV_CLIMATECHANGE"


class TestGKGEstimate:
    """Test GKGEndpoint.estimate() method."""

    @pytest.mark.asyncio
    async def test_estimate_raises_without_bigquery(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
    ) -> None:
        """Test that estimate() raises ConfigurationError without BigQuery."""
        endpoint = GKGEndpoint(
            file_source=mock_file_source,
            bigquery_source=None,
        )

        with pytest.raises(ConfigurationError, match="Estimate queries require BigQuery"):
            await endpoint.estimate(gkg_filter)

    @pytest.mark.asyncio
    async def test_estimate_delegates_to_bigquery(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
        gkg_filter: GKGFilter,
    ) -> None:
        """Test that estimate() delegates to bigquery_source.estimate_gkg()."""
        expected_estimate = QueryEstimate(bytes_processed=8_000_000, query="SELECT ...")
        mock_bigquery_source.estimate_gkg = AsyncMock(return_value=expected_estimate)

        endpoint = GKGEndpoint(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
        )

        result = await endpoint.estimate(gkg_filter, columns=["GKGRECORDID"], limit=50)

        assert isinstance(result, QueryEstimate)
        assert result.bytes_processed == 8_000_000
        mock_bigquery_source.estimate_gkg.assert_awaited_once_with(
            gkg_filter,
            columns=["GKGRECORDID"],
            limit=50,
        )
