#!/usr/bin/env python3
"""Test runner for EventsEndpoint implementation."""

import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

from py_gdelt.endpoints.events import EventsEndpoint
from py_gdelt.filters import DateRange, EventFilter
from py_gdelt.models._internal import _RawEvent
from py_gdelt.models.events import Event


async def test_basic_query() -> None:
    """Test basic query functionality."""
    print("Testing EventsEndpoint basic query...")

    # Create mock file source
    mock_file_source = MagicMock()
    mock_file_source.__aenter__ = AsyncMock(return_value=mock_file_source)
    mock_file_source.__aexit__ = AsyncMock()

    # Create sample raw event
    sample_raw_event = _RawEvent(
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

    # Create async generator for mock
    async def mock_fetch_events(*args, **kwargs):
        yield sample_raw_event

    # Create endpoint
    endpoint = EventsEndpoint(file_source=mock_file_source)

    # Patch the DataFetcher.fetch_events method
    with patch.object(
        endpoint._fetcher,
        "fetch_events",
        side_effect=mock_fetch_events,
    ):
        # Test query
        event_filter = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor1_country="USA",
        )
        result = await endpoint.query(event_filter)

        print(f"✓ Query returned {len(result.data)} events")
        assert len(result.data) == 1
        assert isinstance(result.data[0], Event)
        print(f"✓ Event type is correct: {type(result.data[0]).__name__}")

        event = result.data[0]
        print(f"✓ Event ID: {event.global_event_id}")
        assert event.global_event_id == 123456789
        print(f"✓ Event date: {event.date}")
        assert event.date == date(2024, 1, 1)
        print(f"✓ Event code: {event.event_code}")
        assert event.event_code == "010"

        # Test actor conversion
        assert event.actor1 is not None
        print(f"✓ Actor1: {event.actor1.name} ({event.actor1.code})")
        assert event.actor1.code == "USA"

        # Test geo conversion
        assert event.action_geo is not None
        print(f"✓ Action location: {event.action_geo.name}")

    print("\n✓ All basic query tests passed!")


async def test_streaming() -> None:
    """Test streaming functionality."""
    print("\nTesting EventsEndpoint streaming...")

    # Create mock file source
    mock_file_source = MagicMock()
    mock_file_source.__aenter__ = AsyncMock(return_value=mock_file_source)
    mock_file_source.__aexit__ = AsyncMock()

    # Create async generator for mock
    async def mock_fetch_events(*args, **kwargs):
        for i in range(3):
            yield _RawEvent(
                global_event_id=f"{i}",
                sql_date="20240101",
                month_year="202401",
                year="2024",
                fraction_date="2024.0001",
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

    # Create endpoint
    endpoint = EventsEndpoint(file_source=mock_file_source)

    # Patch the DataFetcher.fetch_events method
    with patch.object(
        endpoint._fetcher,
        "fetch_events",
        side_effect=mock_fetch_events,
    ):
        # Test streaming
        event_filter = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
        )

        events = []
        async for event in endpoint.stream(event_filter):
            events.append(event)
            print(f"  Streamed event {event.global_event_id}")

        print(f"✓ Streamed {len(events)} events")
        assert len(events) == 3

    print("\n✓ All streaming tests passed!")


async def test_deduplication() -> None:
    """Test deduplication functionality."""
    print("\nTesting EventsEndpoint deduplication...")

    # Create mock file source
    mock_file_source = MagicMock()
    mock_file_source.__aenter__ = AsyncMock(return_value=mock_file_source)
    mock_file_source.__aexit__ = AsyncMock()

    # Create two events with same URL, date, location (should deduplicate)
    async def mock_fetch_events(*args, **kwargs):
        for i in range(2):
            yield _RawEvent(
                global_event_id=f"{i}",
                sql_date="20240101",
                month_year="202401",
                year="2024",
                fraction_date="2024.0001",
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
                source_url="http://example.com/article",  # Same URL
                action_geo_fullname="Washington, DC",  # Same location
                is_translated=False,
            )

    # Create endpoint
    endpoint = EventsEndpoint(file_source=mock_file_source)

    # Patch the DataFetcher.fetch_events method
    with patch.object(
        endpoint._fetcher,
        "fetch_events",
        side_effect=mock_fetch_events,
    ):
        # Test query with deduplication
        event_filter = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
        )

        result = await endpoint.query(event_filter, deduplicate=True)

        print(f"✓ Deduplicated from 2 events to {len(result.data)}")
        assert len(result.data) == 1

    print("\n✓ All deduplication tests passed!")


async def main() -> None:
    """Run all tests."""
    try:
        await test_basic_query()
        await test_streaming()
        await test_deduplication()
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
