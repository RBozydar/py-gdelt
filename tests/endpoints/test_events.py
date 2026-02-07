"""Tests for EventsEndpoint."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_gdelt.endpoints.events import EventsEndpoint
from py_gdelt.exceptions import ConfigurationError
from py_gdelt.filters import DateRange, EventFilter
from py_gdelt.models._internal import _RawEvent
from py_gdelt.models.common import FetchResult
from py_gdelt.models.events import Event
from py_gdelt.sources.metadata import QueryEstimate
from py_gdelt.utils.dedup import DedupeStrategy


if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@pytest.fixture
def mock_file_source() -> MagicMock:
    """Create a mock FileSource."""
    source = MagicMock()
    source.__aenter__ = AsyncMock(return_value=source)
    source.__aexit__ = AsyncMock()
    return source


@pytest.fixture
def mock_bigquery_source() -> MagicMock:
    """Create a mock BigQuerySource."""
    source = MagicMock()
    source.__aenter__ = AsyncMock(return_value=source)
    source.__aexit__ = AsyncMock()
    return source


@pytest.fixture
def sample_raw_event() -> _RawEvent:
    """Create a sample _RawEvent for testing."""
    return _RawEvent(
        global_event_id="123456789",
        sql_date="20240101",
        month_year="202401",
        year="2024",
        fraction_date="2024.0001",
        actor1_code="USA",
        actor1_name="UNITED STATES",
        actor1_country_code="US",
        actor2_code="RUS",
        actor2_name="RUSSIA",
        actor2_country_code="RS",
        is_root_event="1",
        event_code="010",
        event_base_code="01",
        event_root_code="01",
        quad_class="1",
        goldstein_scale="3.5",
        num_mentions="10",
        num_sources="5",
        num_articles="8",
        avg_tone="2.5",
        action_geo_fullname="Washington, District of Columbia, United States",
        action_geo_country_code="US",
        date_added="20240101120000",
        source_url="http://example.com/article",
        is_translated=False,
    )


@pytest.fixture
def sample_raw_event_duplicate() -> _RawEvent:
    """Create a duplicate sample _RawEvent for testing deduplication."""
    return _RawEvent(
        global_event_id="987654321",  # Different ID but same URL/date/location
        sql_date="20240101",
        month_year="202401",
        year="2024",
        fraction_date="2024.0001",
        actor1_code="USA",
        actor1_name="UNITED STATES",
        actor1_country_code="US",
        actor2_code="RUS",
        actor2_name="RUSSIA",
        actor2_country_code="RS",
        is_root_event="1",
        event_code="010",
        event_base_code="01",
        event_root_code="01",
        quad_class="1",
        goldstein_scale="3.5",
        num_mentions="10",
        num_sources="5",
        num_articles="8",
        avg_tone="2.5",
        action_geo_fullname="Washington, District of Columbia, United States",
        action_geo_country_code="US",
        date_added="20240101120000",
        source_url="http://example.com/article",  # Same URL
        is_translated=False,
    )


@pytest.fixture
def event_filter() -> EventFilter:
    """Create a sample EventFilter."""
    return EventFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
        actor1_country="USA",
    )


class TestEventsEndpoint:
    """Test suite for EventsEndpoint."""

    def test_init_with_file_source_only(self, mock_file_source: MagicMock) -> None:
        """Test initialization with only file source."""
        endpoint = EventsEndpoint(file_source=mock_file_source)
        assert endpoint._fetcher is not None

    def test_init_with_bigquery_fallback(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
    ) -> None:
        """Test initialization with BigQuery fallback enabled."""
        endpoint = EventsEndpoint(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
            fallback_enabled=True,
        )
        assert endpoint._fetcher is not None

    def test_init_without_fallback(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
    ) -> None:
        """Test initialization with fallback disabled."""
        endpoint = EventsEndpoint(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
            fallback_enabled=False,
        )
        assert endpoint._fetcher is not None

    @pytest.mark.asyncio
    async def test_query_basic(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_event: _RawEvent,
    ) -> None:
        """Test basic query without deduplication."""

        async def mock_fetch_events(*args, **kwargs) -> AsyncIterator[_RawEvent]:
            """Mock fetch_events that yields sample data."""
            yield sample_raw_event

        endpoint = EventsEndpoint(file_source=mock_file_source)

        # Patch the DataFetcher.fetch_events method
        with patch.object(
            endpoint._fetcher,
            "fetch_events",
            side_effect=mock_fetch_events,
        ):
            result = await endpoint.query(event_filter)

        assert isinstance(result, FetchResult)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Event)
        assert result.data[0].global_event_id == 123456789
        assert result.complete is True

    @pytest.mark.asyncio
    async def test_query_with_deduplication(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_event: _RawEvent,
        sample_raw_event_duplicate: _RawEvent,
    ) -> None:
        """Test query with deduplication enabled."""

        async def mock_fetch_events(*args, **kwargs) -> AsyncIterator[_RawEvent]:
            """Mock fetch_events that yields duplicate data."""
            yield sample_raw_event
            yield sample_raw_event_duplicate

        endpoint = EventsEndpoint(file_source=mock_file_source)

        with patch.object(
            endpoint._fetcher,
            "fetch_events",
            side_effect=mock_fetch_events,
        ):
            result = await endpoint.query(
                event_filter,
                deduplicate=True,
                dedupe_strategy=DedupeStrategy.URL_DATE_LOCATION,
            )

        # Should deduplicate from 2 to 1 (same URL, date, location)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Event)

    @pytest.mark.asyncio
    async def test_query_empty_result(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test query with empty result."""

        async def mock_fetch_events(*args, **kwargs) -> AsyncIterator[_RawEvent]:
            """Mock fetch_events that yields nothing."""
            if False:
                yield

        endpoint = EventsEndpoint(file_source=mock_file_source)

        with patch.object(
            endpoint._fetcher,
            "fetch_events",
            side_effect=mock_fetch_events,
        ):
            result = await endpoint.query(event_filter)

        assert len(result.data) == 0
        assert result.complete is True

    @pytest.mark.asyncio
    async def test_stream_basic(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_event: _RawEvent,
    ) -> None:
        """Test basic streaming without deduplication."""

        async def mock_fetch_events(*args, **kwargs) -> AsyncIterator[_RawEvent]:
            """Mock fetch_events that yields sample data."""
            yield sample_raw_event

        endpoint = EventsEndpoint(file_source=mock_file_source)

        with patch.object(
            endpoint._fetcher,
            "fetch_events",
            side_effect=mock_fetch_events,
        ):
            events = [event async for event in endpoint.stream(event_filter)]

        assert len(events) == 1
        assert isinstance(events[0], Event)
        assert events[0].global_event_id == 123456789

    @pytest.mark.asyncio
    async def test_stream_with_deduplication(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_event: _RawEvent,
        sample_raw_event_duplicate: _RawEvent,
    ) -> None:
        """Test streaming with deduplication enabled."""

        async def mock_fetch_events(*args, **kwargs) -> AsyncIterator[_RawEvent]:
            """Mock fetch_events that yields duplicate data."""
            yield sample_raw_event
            yield sample_raw_event_duplicate

        endpoint = EventsEndpoint(file_source=mock_file_source)

        with patch.object(
            endpoint._fetcher,
            "fetch_events",
            side_effect=mock_fetch_events,
        ):
            events = [
                event
                async for event in endpoint.stream(
                    event_filter,
                    deduplicate=True,
                    dedupe_strategy=DedupeStrategy.URL_DATE_LOCATION,
                )
            ]

        # Should deduplicate from 2 to 1
        assert len(events) == 1
        assert isinstance(events[0], Event)

    @pytest.mark.asyncio
    async def test_stream_empty_result(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test streaming with empty result."""

        async def mock_fetch_events(*args, **kwargs) -> AsyncIterator[_RawEvent]:
            """Mock fetch_events that yields nothing."""
            if False:
                yield

        endpoint = EventsEndpoint(file_source=mock_file_source)

        with patch.object(
            endpoint._fetcher,
            "fetch_events",
            side_effect=mock_fetch_events,
        ):
            events = [event async for event in endpoint.stream(event_filter)]

        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_query_uses_bigquery_when_requested(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_event: _RawEvent,
    ) -> None:
        """Test that use_bigquery parameter is passed through."""

        async def mock_fetch_events(*args, **kwargs) -> AsyncIterator[_RawEvent]:
            """Mock fetch_events that yields sample data."""
            yield sample_raw_event

        endpoint = EventsEndpoint(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
        )

        with patch.object(
            endpoint._fetcher,
            "fetch_events",
            side_effect=mock_fetch_events,
        ) as mock_fetch:
            await endpoint.query(event_filter, use_bigquery=True)

            # Verify use_bigquery was passed through
            mock_fetch.assert_called_once()
            call_kwargs = mock_fetch.call_args[1]
            assert call_kwargs["use_bigquery"] is True

    @pytest.mark.asyncio
    async def test_default_dedupe_strategy(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_event: _RawEvent,
    ) -> None:
        """Test that default deduplication strategy is URL_DATE_LOCATION."""

        async def mock_fetch_events(*args, **kwargs) -> AsyncIterator[_RawEvent]:
            """Mock fetch_events that yields sample data."""
            yield sample_raw_event

        endpoint = EventsEndpoint(file_source=mock_file_source)

        with patch.object(
            endpoint._fetcher,
            "fetch_events",
            side_effect=mock_fetch_events,
        ):
            # Should use URL_DATE_LOCATION when deduplicate=True without explicit strategy
            result = await endpoint.query(event_filter, deduplicate=True)

            assert len(result.data) == 1

    def test_query_sync(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_event: _RawEvent,
    ) -> None:
        """Test synchronous query wrapper."""

        async def mock_fetch_events(*args, **kwargs) -> AsyncIterator[_RawEvent]:
            """Mock fetch_events that yields sample data."""
            yield sample_raw_event

        endpoint = EventsEndpoint(file_source=mock_file_source)

        with patch.object(
            endpoint._fetcher,
            "fetch_events",
            side_effect=mock_fetch_events,
        ):
            result = endpoint.query_sync(event_filter)

        assert isinstance(result, FetchResult)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Event)

    def test_stream_sync(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_event: _RawEvent,
    ) -> None:
        """Test synchronous stream wrapper."""

        async def mock_fetch_events(*args, **kwargs) -> AsyncIterator[_RawEvent]:
            """Mock fetch_events that yields sample data."""
            yield sample_raw_event

        endpoint = EventsEndpoint(file_source=mock_file_source)

        with patch.object(
            endpoint._fetcher,
            "fetch_events",
            side_effect=mock_fetch_events,
        ):
            events = list(endpoint.stream_sync(event_filter))

        assert isinstance(events, list)
        assert len(events) == 1
        assert isinstance(events[0], Event)

    @pytest.mark.asyncio
    async def test_build_url(self, mock_file_source: MagicMock) -> None:
        """Test _build_url returns empty string (not used for file/BQ sources)."""
        endpoint = EventsEndpoint(file_source=mock_file_source)
        url = await endpoint._build_url()
        assert url == ""


class TestEventsEndpointIntegration:
    """Integration tests for EventsEndpoint with real conversion logic."""

    @pytest.mark.asyncio
    async def test_raw_event_to_event_conversion(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_event: _RawEvent,
    ) -> None:
        """Test that _RawEvent is properly converted to Event model."""

        async def mock_fetch_events(*args, **kwargs) -> AsyncIterator[_RawEvent]:
            """Mock fetch_events that yields sample data."""
            yield sample_raw_event

        endpoint = EventsEndpoint(file_source=mock_file_source)

        with patch.object(
            endpoint._fetcher,
            "fetch_events",
            side_effect=mock_fetch_events,
        ):
            result = await endpoint.query(event_filter)

        event = result.data[0]

        # Verify conversion worked correctly
        assert event.global_event_id == 123456789
        assert event.date == date(2024, 1, 1)
        assert event.event_code == "010"
        assert event.quad_class == 1
        assert event.goldstein_scale == 3.5
        assert event.num_mentions == 10
        assert event.avg_tone == 2.5

        # Verify actor conversion
        assert event.actor1 is not None
        assert event.actor1.code == "USA"
        assert event.actor1.name == "UNITED STATES"
        assert event.actor1.country_code == "US"

        assert event.actor2 is not None
        assert event.actor2.code == "RUS"
        assert event.actor2.name == "RUSSIA"

        # Verify geo conversion
        assert event.action_geo is not None
        assert event.action_geo.name == "Washington, District of Columbia, United States"
        assert event.action_geo.country_code == "US"

    @pytest.mark.asyncio
    async def test_multiple_events_conversion(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test conversion of multiple events."""

        async def mock_fetch_events(*args, **kwargs) -> AsyncIterator[_RawEvent]:
            """Mock fetch_events that yields multiple events."""
            for i in range(3):
                yield _RawEvent(
                    global_event_id=f"{i}",
                    sql_date="20240101",
                    month_year="202401",
                    year="2024",
                    fraction_date="2024.0001",
                    actor1_code="USA",
                    actor1_country_code="US",
                    is_root_event="1",
                    event_code="010",
                    event_base_code="01",
                    event_root_code="01",
                    quad_class="1",
                    goldstein_scale="3.5",
                    num_mentions="10",
                    num_sources="5",
                    num_articles="8",
                    avg_tone="2.5",
                    date_added="20240101120000",
                    is_translated=False,
                )

        endpoint = EventsEndpoint(file_source=mock_file_source)

        with patch.object(
            endpoint._fetcher,
            "fetch_events",
            side_effect=mock_fetch_events,
        ):
            result = await endpoint.query(event_filter)

        assert len(result.data) == 3
        for i, event in enumerate(result.data):
            assert event.global_event_id == i
            assert isinstance(event, Event)


class TestEventsEstimate:
    """Test EventsEndpoint.estimate() method."""

    @pytest.mark.asyncio
    async def test_estimate_raises_without_bigquery(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test that estimate() raises ConfigurationError without BigQuery."""
        endpoint = EventsEndpoint(
            file_source=mock_file_source,
            bigquery_source=None,
        )

        with pytest.raises(ConfigurationError, match="Estimate queries require BigQuery"):
            await endpoint.estimate(event_filter)

    @pytest.mark.asyncio
    async def test_estimate_delegates_to_bigquery(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test that estimate() delegates to bigquery_source.estimate_events()."""
        expected_estimate = QueryEstimate(bytes_processed=5_000_000, query="SELECT ...")
        mock_bigquery_source.estimate_events = AsyncMock(return_value=expected_estimate)

        endpoint = EventsEndpoint(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
        )

        result = await endpoint.estimate(event_filter, columns=["GLOBALEVENTID"], limit=100)

        assert isinstance(result, QueryEstimate)
        assert result.bytes_processed == 5_000_000
        mock_bigquery_source.estimate_events.assert_awaited_once_with(
            event_filter,
            columns=["GLOBALEVENTID"],
            limit=100,
        )

    def test_estimate_sync_wraps_async(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test that estimate_sync() calls estimate() internally."""
        expected_estimate = QueryEstimate(bytes_processed=3_000_000, query="SELECT ...")
        mock_bigquery_source.estimate_events = AsyncMock(return_value=expected_estimate)

        endpoint = EventsEndpoint(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
        )

        result = endpoint.estimate_sync(event_filter)

        assert isinstance(result, QueryEstimate)
        assert result.bytes_processed == 3_000_000
