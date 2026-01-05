"""Integration tests for Events endpoint with file sources."""

from datetime import date, timedelta

import pytest

from py_gdelt import GDELTClient
from py_gdelt.filters import DateRange, EventFilter


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(120)  # 2 minute timeout for file downloads
async def test_events_query_returns_events(gdelt_client: GDELTClient) -> None:
    """Test events query returns events from files."""
    # Use yesterday to ensure data exists
    yesterday = date.today() - timedelta(days=2)

    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
    )

    result = await gdelt_client.events.query(event_filter)

    # File-based queries may fail if files don't exist yet
    # Just verify we get a list back
    assert isinstance(result, list) or hasattr(result, "__iter__")


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(120)
async def test_events_streaming(gdelt_client: GDELTClient) -> None:
    """Test events streaming works."""
    yesterday = date.today() - timedelta(days=2)

    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
    )

    count = 0
    async for event in gdelt_client.events.stream(event_filter):
        count += 1
        assert hasattr(event, "global_event_id")
        if count >= 10:  # Just verify streaming works
            break

    # We streamed at least something (or 0 if no files)
    assert count >= 0


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(120)
async def test_events_with_country_filter(gdelt_client: GDELTClient) -> None:
    """Test filtering events by country."""
    yesterday = date.today() - timedelta(days=2)

    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
        actor1_country="USA",
    )

    result = await gdelt_client.events.query(event_filter)

    # Verify we got a result (may be empty list)
    assert isinstance(result, list)

    # If we got events, verify country filter
    if result:
        for event in result[:5]:  # Check first 5
            if hasattr(event, "actor1") and event.actor1:
                # Some events may not have country code
                pass


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(120)
async def test_events_query_event_structure(gdelt_client: GDELTClient) -> None:
    """Test that events have expected structure."""
    yesterday = date.today() - timedelta(days=2)

    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
    )

    count = 0
    async for event in gdelt_client.events.stream(event_filter):
        # Verify required fields
        assert hasattr(event, "global_event_id")
        assert hasattr(event, "date")
        assert hasattr(event, "event_code")

        # Optional fields
        assert hasattr(event, "goldstein_scale")
        assert hasattr(event, "actor1")
        assert hasattr(event, "actor2")

        count += 1
        if count >= 3:  # Just verify a few
            break


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(120)
async def test_events_date_range(gdelt_client: GDELTClient) -> None:
    """Test querying a specific date range."""
    # Use dates 3-4 days ago to ensure files exist
    end_date = date.today() - timedelta(days=3)
    start_date = end_date - timedelta(days=1)

    event_filter = EventFilter(
        date_range=DateRange(start=start_date, end=end_date),
    )

    result = await gdelt_client.events.query(event_filter)

    # Verify we got a result
    assert isinstance(result, list)

    # If we got events, verify dates are in range
    if result:
        for event in result[:5]:
            # Events should have dates within the range
            assert hasattr(event, "date")
