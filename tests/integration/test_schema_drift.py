"""Integration tests for schema drift detection.

These tests validate that live GDELT data matches our model expectations
and lookup tables. They emit warnings (not failures) when drift is detected,
allowing us to identify when GDELT introduces new codes or fields.

Run these tests:
    pytest tests/integration/test_schema_drift.py -m integration
"""

from __future__ import annotations

import warnings
from datetime import date, timedelta
from typing import TYPE_CHECKING

import pytest

from py_gdelt.filters import DateRange, EventFilter, GKGFilter
from py_gdelt.lookups import CAMEOCodes, Countries, GKGThemes


if TYPE_CHECKING:
    from py_gdelt import GDELTClient


class SchemaDriftWarning(UserWarning):
    """Warning emitted when GDELT data schema drift is detected.

    Indicates that GDELT has added new fields or changed the structure of
    responses in a way not reflected in our models.
    """


class UnknownCodeWarning(UserWarning):
    """Warning emitted when unknown CAMEO/country/theme codes are found.

    Indicates that GDELT is using codes not present in our lookup tables,
    suggesting the tables may need updating.
    """


def get_drift(expected_fields: set[str], actual_fields: set[str]) -> tuple[set[str], set[str]]:
    """Calculate schema drift between expected and actual fields.

    Args:
        expected_fields: Set of field names we expect to see
        actual_fields: Set of field names actually present in data

    Returns:
        Tuple of (missing_fields, extra_fields) where:
            - missing_fields: Expected fields not found in actual data
            - extra_fields: Actual fields not in our expected set
    """
    missing = expected_fields - actual_fields
    extra = actual_fields - expected_fields
    return missing, extra


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_doc_api_schema_drift(gdelt_client: GDELTClient) -> None:
    """Test DOC API response fields match Article model.

    Validates that Article objects returned from the DOC API contain
    all expected fields and warns if new fields appear.
    """
    # Search for recent articles
    articles = await gdelt_client.doc.search(query="test", timespan="24h", max_results=10)

    if not articles:
        pytest.skip("No articles returned from DOC API")

    # Expected fields from Article model
    expected_fields = {
        "url",
        "title",
        "seendate",
        "domain",
        "source_country",
        "language",
        "socialimage",
        "tone",
        "share_count",
    }

    # Check first article for schema drift
    article = articles[0]
    actual_fields = set(article.model_dump().keys())

    missing, extra = get_drift(expected_fields, actual_fields)

    if missing:
        warnings.warn(
            f"DOC API missing expected fields: {sorted(missing)}",
            SchemaDriftWarning,
            stacklevel=2,
        )

    if extra:
        warnings.warn(
            f"DOC API has new fields not in Article model: {sorted(extra)}",
            SchemaDriftWarning,
            stacklevel=2,
        )

    # Basic validation - core fields should exist
    assert article.url is not None, "Article should have a URL"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(120)
async def test_events_file_schema_drift(gdelt_client: GDELTClient) -> None:
    """Test Events file download fields match Event model.

    Validates that Event objects parsed from downloaded files contain
    all expected fields and warns if new fields appear.
    """
    # Use recent date to ensure data exists
    yesterday = date.today() - timedelta(days=2)

    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
    )

    # Stream a few events to check schema
    count = 0
    events_to_check = []
    async for event in gdelt_client.events.stream(event_filter):
        events_to_check.append(event)
        count += 1
        if count >= 5:
            break

    if not events_to_check:
        pytest.skip("No events returned - files may be temporarily unavailable")

    # Expected top-level fields from Event model
    expected_fields = {
        "global_event_id",
        "date",
        "date_added",
        "source_url",
        "actor1",
        "actor2",
        "event_code",
        "event_base_code",
        "event_root_code",
        "quad_class",
        "goldstein_scale",
        "num_mentions",
        "num_sources",
        "num_articles",
        "avg_tone",
        "is_root_event",
        "actor1_geo",
        "actor2_geo",
        "action_geo",
        "version",
        "is_translated",
        "original_record_id",
    }

    # Check first event for schema drift
    event = events_to_check[0]
    actual_fields = set(event.model_dump().keys())

    missing, extra = get_drift(expected_fields, actual_fields)

    if missing:
        warnings.warn(
            f"Events file missing expected fields: {sorted(missing)}",
            SchemaDriftWarning,
            stacklevel=2,
        )

    if extra:
        warnings.warn(
            f"Events file has new fields not in Event model: {sorted(extra)}",
            SchemaDriftWarning,
            stacklevel=2,
        )

    # Basic validation - core fields should exist
    assert event.global_event_id > 0
    assert event.event_code is not None


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(120)
async def test_gkg_file_schema_drift(gdelt_client: GDELTClient) -> None:
    """Test GKG file download fields match GKGRecord model.

    Validates that GKGRecord objects parsed from downloaded files contain
    all expected fields and warns if new fields appear.
    """
    # Use recent date to ensure data exists
    yesterday = date.today() - timedelta(days=2)

    gkg_filter = GKGFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
    )

    # Stream a few records to check schema
    count = 0
    records_to_check = []
    async for record in gdelt_client.gkg.stream(gkg_filter):
        records_to_check.append(record)
        count += 1
        if count >= 5:
            break

    if not records_to_check:
        pytest.skip("No GKG records returned - files may be temporarily unavailable")

    # Expected top-level fields from GKGRecord model
    expected_fields = {
        "record_id",
        "date",
        "source_url",
        "source_name",
        "source_collection",
        "themes",
        "persons",
        "organizations",
        "locations",
        "tone",
        "gcam",
        "quotations",
        "amounts",
        "sharing_image",
        "all_names",
        "version",
        "is_translated",
        "original_record_id",
        "translation_info",
    }

    # Check first record for schema drift
    record = records_to_check[0]
    actual_fields = set(record.model_dump().keys())

    missing, extra = get_drift(expected_fields, actual_fields)

    if missing:
        warnings.warn(
            f"GKG file missing expected fields: {sorted(missing)}",
            SchemaDriftWarning,
            stacklevel=2,
        )

    if extra:
        warnings.warn(
            f"GKG file has new fields not in GKGRecord model: {sorted(extra)}",
            SchemaDriftWarning,
            stacklevel=2,
        )

    # Basic validation - core fields should exist
    assert record.record_id is not None
    assert record.source_url is not None


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(120)
async def test_cameo_codes_coverage(gdelt_client: GDELTClient) -> None:
    """Test that CAMEO codes in live data exist in lookup tables.

    Collects CAMEO event codes from live events and validates them
    against our lookup table, warning if unknown codes are found.
    """
    # Use recent date to ensure data exists
    yesterday = date.today() - timedelta(days=2)

    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
    )

    # Collect event codes from live data
    event_codes = set()
    count = 0
    async for event in gdelt_client.events.stream(event_filter):
        if event.event_code:
            event_codes.add(event.event_code)
        if event.event_base_code:
            event_codes.add(event.event_base_code)
        if event.event_root_code:
            event_codes.add(event.event_root_code)
        count += 1
        if count >= 100:
            break

    if not event_codes:
        pytest.skip("No event codes collected from live data")

    # Check against lookup table
    cameo = CAMEOCodes()
    unknown_codes = [code for code in sorted(event_codes) if code not in cameo]

    if unknown_codes:
        warnings.warn(
            f"Unknown CAMEO codes found in live data: {unknown_codes}",
            UnknownCodeWarning,
            stacklevel=2,
        )

    # Should find at least some known codes
    known_codes = [code for code in event_codes if code in cameo]
    assert len(known_codes) > 0, "Expected to find at least some known CAMEO codes"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(120)
async def test_country_codes_coverage(gdelt_client: GDELTClient) -> None:
    """Test that country codes in live data exist in lookup tables.

    Collects country codes from live events and validates them
    against our lookup table, warning if unknown codes are found.
    """
    # Use recent date to ensure data exists
    yesterday = date.today() - timedelta(days=2)

    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
    )

    # Collect country codes from live data
    country_codes = set()
    count = 0
    async for event in gdelt_client.events.stream(event_filter):
        # Access country codes via nested Actor objects
        if event.actor1 and event.actor1.country_code:
            country_codes.add(event.actor1.country_code)
        if event.actor2 and event.actor2.country_code:
            country_codes.add(event.actor2.country_code)

        # Also check geo country codes
        if event.actor1_geo and event.actor1_geo.country_code:
            country_codes.add(event.actor1_geo.country_code)
        if event.actor2_geo and event.actor2_geo.country_code:
            country_codes.add(event.actor2_geo.country_code)
        if event.action_geo and event.action_geo.country_code:
            country_codes.add(event.action_geo.country_code)

        count += 1
        if count >= 100:
            break

    if not country_codes:
        pytest.skip("No country codes collected from live data")

    # Check against lookup table
    countries = Countries()
    unknown_codes = [code for code in sorted(country_codes) if code not in countries]

    if unknown_codes:
        warnings.warn(
            f"Unknown country codes found in live data: {unknown_codes}",
            UnknownCodeWarning,
            stacklevel=2,
        )

    # Should find at least some known codes
    known_codes = [code for code in country_codes if code in countries]
    assert len(known_codes) > 0, "Expected to find at least some known country codes"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(120)
async def test_gkg_themes_coverage(gdelt_client: GDELTClient) -> None:
    """Test that GKG themes in live data exist in lookup tables.

    Collects GKG theme codes from live data and validates them
    against our lookup table, warning if unknown themes are found.
    """
    # Use recent date to ensure data exists
    yesterday = date.today() - timedelta(days=2)

    gkg_filter = GKGFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
    )

    # Collect theme codes from live data
    theme_codes = set()
    count = 0
    async for record in gdelt_client.gkg.stream(gkg_filter):
        # Themes is list[EntityMention], access theme names via .name
        for theme in record.themes:
            if theme.name:
                theme_codes.add(theme.name)

        count += 1
        if count >= 50:
            break

    if not theme_codes:
        pytest.skip("No GKG themes collected from live data")

    # Check against lookup table
    themes = GKGThemes()
    unknown_themes = [theme_code for theme_code in sorted(theme_codes) if theme_code not in themes]

    if unknown_themes:
        # Only warn about first 20 to avoid overwhelming output
        warning_list = unknown_themes[:20]
        if len(unknown_themes) > 20:
            warning_list.append(f"... and {len(unknown_themes) - 20} more")

        warnings.warn(
            f"Unknown GKG themes found in live data: {warning_list}",
            UnknownCodeWarning,
            stacklevel=2,
        )

    # Should find at least some known themes
    known_themes = [theme for theme in theme_codes if theme in themes]
    assert len(known_themes) > 0, "Expected to find at least some known GKG themes"
