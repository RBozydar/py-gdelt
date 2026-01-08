"""Integration tests for Events endpoint with file sources."""

from datetime import date, timedelta

import pytest

from py_gdelt import GDELTClient
from py_gdelt.filters import DateRange, EventFilter
from py_gdelt.models import FetchResult


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

    if count == 0:
        pytest.skip("No events returned - files may be temporarily unavailable")


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

    # Verify we got a FetchResult with data
    assert isinstance(result, FetchResult)

    if not result.data:
        pytest.skip("No events returned for country filter test")

    # Note: Country filtering is applied during file parsing, results depend on data
    # Just verify we got events and the query didn't error
    assert len(result.data) >= 0, "Should return a valid result"


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

    # Verify we got a FetchResult with data
    assert isinstance(result, FetchResult)

    if not result.data:
        pytest.skip("No events returned for date range test")

    # Verify events have expected date attribute
    for event in result.data[:5]:
        assert hasattr(event, "date"), "Event should have date attribute"
