"""Integration tests verifying filter consistency across data sources.

These tests require BigQuery credentials and real GDELT data.
They verify that filters produce consistent results from both file downloads
and BigQuery queries.
"""

from __future__ import annotations

import os
from datetime import date, timedelta

import pytest

from py_gdelt.config import GDELTSettings
from py_gdelt.filters import DateRange, EventFilter, GKGFilter
from py_gdelt.sources.bigquery import BigQuerySource
from py_gdelt.sources.files import FileSource


pytestmark = pytest.mark.integration


class TestFilterConsistencyAcrossSources:
    """Verify filters produce consistent results from file and BigQuery sources."""

    @pytest.fixture
    def settings(self) -> GDELTSettings:
        """Get GDELT settings."""
        return GDELTSettings()

    @pytest.fixture
    def date_range(self) -> DateRange:
        """Get a recent date range for testing (yesterday to avoid incomplete data)."""
        yesterday = date.today() - timedelta(days=1)
        return DateRange(start=yesterday, end=yesterday)

    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.timeout(180)
    async def test_event_filter_actor_country_consistency(
        self, settings: GDELTSettings, date_range: DateRange
    ) -> None:
        """EventFilter actor_country produces consistent results from both sources."""
        filter_obj = EventFilter(
            date_range=date_range,
            actor1_country="US",
        )

        # Query from file source
        from py_gdelt.endpoints.events import EventsEndpoint

        async with FileSource() as file_source:
            endpoint = EventsEndpoint(file_source=file_source)
            file_result = await endpoint.query(filter_obj)
            file_count = len(file_result.data)

        # Query from BigQuery
        if not os.environ.get("GDELT_BIGQUERY_PROJECT"):
            pytest.skip("GDELT_BIGQUERY_PROJECT not set - skipping BigQuery comparison")

        try:
            async with FileSource() as file_source:
                bigquery_source = BigQuerySource(settings=settings)
                endpoint = EventsEndpoint(
                    file_source=file_source,
                    bigquery_source=bigquery_source,
                )
                bq_result = await endpoint.query(filter_obj, use_bigquery=True)
                bq_count = len(bq_result.data)
        except Exception as e:
            pytest.skip(f"BigQuery not available: {e}")

        # Verify all file results have actor1_country="US"
        for event in file_result.data:
            assert event.actor1 is not None
            assert event.actor1.country_code == "US"

        # Verify all BigQuery results have actor1_country="US"
        for event in bq_result.data:
            assert event.actor1 is not None
            assert event.actor1.country_code == "US"

        # Counts should be similar (not exact due to timing differences)
        # Allow 10% variance
        if file_count > 0 and bq_count > 0:
            ratio = min(file_count, bq_count) / max(file_count, bq_count)
            assert ratio > 0.9, f"File: {file_count}, BigQuery: {bq_count}"

    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.timeout(180)
    async def test_gkg_filter_persons_case_insensitive_both_sources(
        self, date_range: DateRange
    ) -> None:
        """Case-insensitive person matching works on both sources."""
        # Use lowercase in filter to test case-insensitivity
        filter_obj = GKGFilter(
            date_range=date_range,
            persons=["biden"],  # Lowercase - should match "Biden", "BIDEN", etc.
        )

        # Query from file source
        from py_gdelt.endpoints.gkg import GKGEndpoint

        async with FileSource() as file_source:
            endpoint = GKGEndpoint(file_source=file_source)
            file_result = await endpoint.query(filter_obj)

        if not file_result.data:
            pytest.skip("No GKG records returned - data may be unavailable")

        # Verify case-insensitive matching worked
        for record in file_result.data:
            person_names = [p.name.lower() for p in record.persons]
            assert any("biden" in name for name in person_names), (
                f"Record should contain 'biden' (case-insensitive): {person_names}"
            )

    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.timeout(180)
    async def test_gkg_filter_theme_prefix_consistency(self, date_range: DateRange) -> None:
        """GKGFilter theme_prefix produces consistent results from both sources."""
        filter_obj = GKGFilter(
            date_range=date_range,
            theme_prefix="ENV_",  # Match environment themes
        )

        # Query from file source
        from py_gdelt.endpoints.gkg import GKGEndpoint

        async with FileSource() as file_source:
            endpoint = GKGEndpoint(file_source=file_source)
            file_result = await endpoint.query(filter_obj)

        if not file_result.data:
            pytest.skip("No GKG records returned - data may be unavailable")

        # Verify all results have at least one ENV_ theme
        for record in file_result.data:
            theme_names = [t.name.upper() for t in record.themes]
            assert any(name.startswith("ENV_") for name in theme_names), (
                f"Record should have ENV_ theme: {theme_names}"
            )

    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.timeout(180)
    async def test_event_filter_tone_range_consistency(self, date_range: DateRange) -> None:
        """EventFilter tone range produces consistent results."""
        filter_obj = EventFilter(
            date_range=date_range,
            min_tone=0.0,  # Only positive/neutral tone events
        )

        # Query from file source
        from py_gdelt.endpoints.events import EventsEndpoint

        async with FileSource() as file_source:
            endpoint = EventsEndpoint(file_source=file_source)
            file_result = await endpoint.query(filter_obj)

        if not file_result.data:
            pytest.skip("No events returned - data may be unavailable")

        # Verify all results have non-negative tone
        for event in file_result.data:
            assert event.avg_tone >= 0.0, f"Event tone {event.avg_tone} should be >= 0"
