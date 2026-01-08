"""Integration tests for BigQuery data source.

These tests make real BigQuery queries against GDELT's public datasets.
Run with: pytest tests/integration/test_bigquery.py -m integration

IMPORTANT: These tests use LIMIT clauses and date filters to minimize costs.

Requirements:
- Set GDELT_BIGQUERY_PROJECT environment variable to your GCP project ID
- Authenticate with: gcloud auth application-default login
"""

import os
from datetime import date, timedelta

import pytest

from py_gdelt.filters import DateRange, EventFilter, GKGFilter
from py_gdelt.sources.bigquery import BigQuerySource


# Skip all tests if BigQuery project not configured
pytestmark = [
    pytest.mark.integration,
    pytest.mark.asyncio,
    pytest.mark.timeout(60),
    pytest.mark.skipif(
        not os.environ.get("GDELT_BIGQUERY_PROJECT"),
        reason="GDELT_BIGQUERY_PROJECT not set - BigQuery tests require GCP project",
    ),
]


@pytest.fixture
async def bigquery_source() -> BigQuerySource:
    """Create BigQuery source for testing."""
    async with BigQuerySource() as source:
        yield source


async def test_bigquery_query_events_basic(bigquery_source: BigQuerySource) -> None:
    """Test basic events query returns data."""
    # Use a recent date range (yesterday) with strict limit
    yesterday = date.today() - timedelta(days=1)

    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
    )

    rows = [row async for row in bigquery_source.query_events(event_filter, limit=5)]

    # Should get some events
    assert len(rows) > 0, "Expected at least one event from BigQuery"

    # Verify row structure
    row = rows[0]
    assert "GLOBALEVENTID" in row, "Row should have GLOBALEVENTID"
    assert "SQLDATE" in row, "Row should have SQLDATE"
    assert "EventCode" in row, "Row should have EventCode"


async def test_bigquery_query_events_with_country_filter(
    bigquery_source: BigQuerySource,
) -> None:
    """Test events query with country filter."""
    yesterday = date.today() - timedelta(days=1)

    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
        actor1_country="USA",
    )

    rows = [row async for row in bigquery_source.query_events(event_filter, limit=5)]

    # Verify country filter was applied
    if rows:
        for row in rows:
            assert row.get("Actor1CountryCode") == "USA", "Country filter should work"


async def test_bigquery_query_events_select_columns(
    bigquery_source: BigQuerySource,
) -> None:
    """Test selecting specific columns."""
    yesterday = date.today() - timedelta(days=1)

    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
    )

    # Select only specific columns
    columns = ["GLOBALEVENTID", "SQLDATE", "EventCode", "GoldsteinScale"]

    rows = [
        row async for row in bigquery_source.query_events(event_filter, columns=columns, limit=3)
    ]

    if rows:
        # Should only have the requested columns
        row = rows[0]
        assert set(row.keys()) == set(columns), f"Expected {columns}, got {row.keys()}"


async def test_bigquery_query_gkg_basic(bigquery_source: BigQuerySource) -> None:
    """Test basic GKG query returns data."""
    yesterday = date.today() - timedelta(days=1)

    gkg_filter = GKGFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
    )

    rows = [row async for row in bigquery_source.query_gkg(gkg_filter, limit=5)]

    # Should get some GKG records
    assert len(rows) > 0, "Expected at least one GKG record from BigQuery"

    # Verify row structure
    row = rows[0]
    assert "GKGRECORDID" in row, "Row should have GKGRECORDID"
    assert "DATE" in row, "Row should have DATE"


async def test_bigquery_query_mentions_basic(bigquery_source: BigQuerySource) -> None:
    """Test basic mentions query returns data.

    Note: query_mentions requires a global_event_id, so we first get an event
    and then query its mentions.
    """
    yesterday = date.today() - timedelta(days=1)

    # First get an event to use for mentions query
    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
    )

    event_id: int | None = None
    async for row in bigquery_source.query_events(event_filter, limit=1):
        event_id = int(row["GLOBALEVENTID"])
        break

    if event_id is None:
        pytest.skip("No events found to test mentions query")
        return  # For type narrowing

    # Now query mentions for this event
    rows = [
        row
        async for row in bigquery_source.query_mentions(
            global_event_id=event_id,
            date_range=DateRange(start=yesterday, end=yesterday),
        )
    ]

    # May not have mentions for this specific event
    assert isinstance(rows, list), "Should return a list"


async def test_bigquery_handles_empty_results(bigquery_source: BigQuerySource) -> None:
    """Test query handles empty results gracefully."""
    # Use a very restrictive filter that's unlikely to match
    # GDELT v2 started in 2015, so 2000 should return no results
    event_filter = EventFilter(
        date_range=DateRange(
            start=date(2000, 1, 1),
            end=date(2000, 1, 1),
        ),
    )

    rows = [row async for row in bigquery_source.query_events(event_filter, limit=5)]

    # Should return empty list, not error
    assert isinstance(rows, list), "Should return a list even if empty"
    assert len(rows) == 0, "GDELT v2 data doesn't exist before 2015"
