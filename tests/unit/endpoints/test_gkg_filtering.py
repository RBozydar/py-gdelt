"""Unit tests for GKGEndpoint client-side filtering."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest

from py_gdelt.endpoints.gkg import GKGEndpoint
from py_gdelt.filters import DateRange, GKGFilter
from py_gdelt.models.common import EntityMention, Location, ToneScores
from py_gdelt.models.gkg import GKGRecord


def make_gkg_record(
    *,
    themes: list[str] | None = None,
    persons: list[str] | None = None,
    organizations: list[str] | None = None,
    locations: list[str] | None = None,
    tone: float | None = None,
) -> GKGRecord:
    """Create a test GKGRecord with specified fields.

    Args:
        themes: List of theme names to include.
        persons: List of person names to include.
        organizations: List of organization names to include.
        locations: List of country codes for locations.
        tone: Overall tone value for ToneScores.

    Returns:
        GKGRecord instance with specified field values.
    """
    tone_scores: ToneScores | None = None
    if tone is not None:
        tone_scores = ToneScores(
            tone=tone,
            positive_score=0.0,
            negative_score=0.0,
            polarity=0.0,
            activity_reference_density=0.0,
            self_group_reference_density=0.0,
        )

    return GKGRecord(
        record_id="20240101120000-1",
        date=datetime(2024, 1, 1, 12, 0, 0),
        source_url="https://example.com/article",
        source_name="Example News",
        source_collection=1,
        themes=[EntityMention(entity_type="THEME", name=t) for t in (themes or [])],
        persons=[EntityMention(entity_type="PERSON", name=p) for p in (persons or [])],
        organizations=[EntityMention(entity_type="ORG", name=o) for o in (organizations or [])],
        locations=[Location(country_code=c) for c in (locations or [])],
        tone=tone_scores,
    )


class TestGKGClientSideFiltering:
    """Test client-side filtering for GKGEndpoint."""

    @pytest.fixture
    def endpoint(self) -> GKGEndpoint:
        """Create a GKGEndpoint for testing.

        Returns:
            GKGEndpoint instance with mocked fetcher.
        """
        endpoint = GKGEndpoint.__new__(GKGEndpoint)
        endpoint._fetcher = MagicMock()
        return endpoint

    @pytest.fixture
    def base_filter(self) -> GKGFilter:
        """Create a base GKGFilter with only date_range set.

        Returns:
            GKGFilter with date_range starting 2024-01-01.
        """
        return GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))

    def test_matches_filter_themes_exact(self, endpoint: GKGEndpoint) -> None:
        """Themes filter matches exact theme codes (case-insensitive)."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            themes=["ENV_CLIMATE"],
        )

        record_match = make_gkg_record(themes=["ENV_CLIMATE", "TAX_FNCACT"])
        record_match_lower = make_gkg_record(themes=["env_climate"])
        record_no_match = make_gkg_record(themes=["TAX_FNCACT", "ECON_COST_OF_LIVING"])

        assert endpoint._matches_filter(record_match, filter_obj) is True
        assert endpoint._matches_filter(record_match_lower, filter_obj) is True
        assert endpoint._matches_filter(record_no_match, filter_obj) is False

    def test_matches_filter_themes_or_logic(self, endpoint: GKGEndpoint) -> None:
        """Themes filter uses OR logic."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            themes=["ENV_CLIMATE", "TAX_FNCACT"],
        )

        record_first = make_gkg_record(themes=["ENV_CLIMATE"])
        record_second = make_gkg_record(themes=["TAX_FNCACT"])
        record_both = make_gkg_record(themes=["ENV_CLIMATE", "TAX_FNCACT"])
        record_neither = make_gkg_record(themes=["ECON_COST_OF_LIVING"])

        assert endpoint._matches_filter(record_first, filter_obj) is True
        assert endpoint._matches_filter(record_second, filter_obj) is True
        assert endpoint._matches_filter(record_both, filter_obj) is True
        assert endpoint._matches_filter(record_neither, filter_obj) is False

    def test_matches_filter_theme_prefix(self, endpoint: GKGEndpoint) -> None:
        """Theme prefix filter matches case-insensitively."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            theme_prefix="ENV_",
        )

        record_match = make_gkg_record(themes=["ENV_CLIMATE"])
        record_match_lower = make_gkg_record(themes=["env_water"])
        record_no_match = make_gkg_record(themes=["TAX_FNCACT"])

        assert endpoint._matches_filter(record_match, filter_obj) is True
        assert endpoint._matches_filter(record_match_lower, filter_obj) is True
        assert endpoint._matches_filter(record_no_match, filter_obj) is False

    def test_matches_filter_persons_case_insensitive(
        self,
        endpoint: GKGEndpoint,
    ) -> None:
        """Persons filter matches case-insensitively."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            persons=["obama"],
        )

        record_upper = make_gkg_record(persons=["Barack Obama"])
        record_lower = make_gkg_record(persons=["barack obama"])
        record_mixed = make_gkg_record(persons=["OBAMA"])
        record_no_match = make_gkg_record(persons=["Joe Biden"])

        assert endpoint._matches_filter(record_upper, filter_obj) is True
        assert endpoint._matches_filter(record_lower, filter_obj) is True
        assert endpoint._matches_filter(record_mixed, filter_obj) is True
        assert endpoint._matches_filter(record_no_match, filter_obj) is False

    def test_matches_filter_persons_substring(self, endpoint: GKGEndpoint) -> None:
        """Persons filter does substring matching."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            persons=["Obama"],
        )

        record_barack = make_gkg_record(persons=["Barack Obama"])
        record_michelle = make_gkg_record(persons=["Michelle Obama"])
        record_no_match = make_gkg_record(persons=["Joe Biden"])

        assert endpoint._matches_filter(record_barack, filter_obj) is True
        assert endpoint._matches_filter(record_michelle, filter_obj) is True
        assert endpoint._matches_filter(record_no_match, filter_obj) is False

    def test_matches_filter_persons_or_logic(self, endpoint: GKGEndpoint) -> None:
        """Persons filter uses OR logic."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            persons=["Obama", "Biden"],
        )

        record_first = make_gkg_record(persons=["Barack Obama"])
        record_second = make_gkg_record(persons=["Joe Biden"])
        record_both = make_gkg_record(persons=["Barack Obama", "Joe Biden"])
        record_neither = make_gkg_record(persons=["Donald Trump"])

        assert endpoint._matches_filter(record_first, filter_obj) is True
        assert endpoint._matches_filter(record_second, filter_obj) is True
        assert endpoint._matches_filter(record_both, filter_obj) is True
        assert endpoint._matches_filter(record_neither, filter_obj) is False

    def test_matches_filter_organizations_case_insensitive(
        self,
        endpoint: GKGEndpoint,
    ) -> None:
        """Organizations filter matches case-insensitively."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            organizations=["united nations"],
        )

        record_upper = make_gkg_record(organizations=["United Nations"])
        record_mixed = make_gkg_record(organizations=["UNITED NATIONS"])
        record_no_match = make_gkg_record(organizations=["World Bank"])

        assert endpoint._matches_filter(record_upper, filter_obj) is True
        assert endpoint._matches_filter(record_mixed, filter_obj) is True
        assert endpoint._matches_filter(record_no_match, filter_obj) is False

    def test_matches_filter_organizations_substring(
        self,
        endpoint: GKGEndpoint,
    ) -> None:
        """Organizations filter does substring matching."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            organizations=["Nations"],
        )

        record_match = make_gkg_record(organizations=["United Nations"])
        record_no_match = make_gkg_record(organizations=["World Bank"])

        assert endpoint._matches_filter(record_match, filter_obj) is True
        assert endpoint._matches_filter(record_no_match, filter_obj) is False

    def test_matches_filter_organizations_or_logic(
        self,
        endpoint: GKGEndpoint,
    ) -> None:
        """Organizations filter uses OR logic."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            organizations=["United Nations", "World Bank"],
        )

        record_first = make_gkg_record(organizations=["United Nations"])
        record_second = make_gkg_record(organizations=["World Bank"])
        record_both = make_gkg_record(
            organizations=["United Nations", "World Bank"],
        )
        record_neither = make_gkg_record(organizations=["IMF"])

        assert endpoint._matches_filter(record_first, filter_obj) is True
        assert endpoint._matches_filter(record_second, filter_obj) is True
        assert endpoint._matches_filter(record_both, filter_obj) is True
        assert endpoint._matches_filter(record_neither, filter_obj) is False

    def test_matches_filter_country(self, endpoint: GKGEndpoint) -> None:
        """Country filter matches FIPS code in any location."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            country="US",
        )

        record_match = make_gkg_record(locations=["US"])
        record_multiple = make_gkg_record(locations=["UK", "US", "FR"])
        record_no_match = make_gkg_record(locations=["UK", "FR"])
        record_empty = make_gkg_record(locations=[])

        assert endpoint._matches_filter(record_match, filter_obj) is True
        assert endpoint._matches_filter(record_multiple, filter_obj) is True
        assert endpoint._matches_filter(record_no_match, filter_obj) is False
        assert endpoint._matches_filter(record_empty, filter_obj) is False

    def test_matches_filter_min_tone(self, endpoint: GKGEndpoint) -> None:
        """Filter by min_tone works client-side."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            min_tone=0.0,
        )

        record_positive = make_gkg_record(tone=5.0)
        record_zero = make_gkg_record(tone=0.0)
        record_negative = make_gkg_record(tone=-5.0)
        record_none = make_gkg_record(tone=None)

        assert endpoint._matches_filter(record_positive, filter_obj) is True
        assert endpoint._matches_filter(record_zero, filter_obj) is True
        assert endpoint._matches_filter(record_negative, filter_obj) is False
        assert endpoint._matches_filter(record_none, filter_obj) is False

    def test_matches_filter_max_tone(self, endpoint: GKGEndpoint) -> None:
        """Filter by max_tone works client-side."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            max_tone=0.0,
        )

        record_positive = make_gkg_record(tone=5.0)
        record_zero = make_gkg_record(tone=0.0)
        record_negative = make_gkg_record(tone=-5.0)
        record_none = make_gkg_record(tone=None)

        assert endpoint._matches_filter(record_positive, filter_obj) is False
        assert endpoint._matches_filter(record_zero, filter_obj) is True
        assert endpoint._matches_filter(record_negative, filter_obj) is True
        assert endpoint._matches_filter(record_none, filter_obj) is False

    def test_matches_filter_tone_range(self, endpoint: GKGEndpoint) -> None:
        """Tone filters work with min and max."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            min_tone=-2.0,
            max_tone=2.0,
        )

        record_in_range = make_gkg_record(tone=0.0)
        record_at_min = make_gkg_record(tone=-2.0)
        record_at_max = make_gkg_record(tone=2.0)
        record_below = make_gkg_record(tone=-5.0)
        record_above = make_gkg_record(tone=5.0)
        record_none = make_gkg_record(tone=None)

        assert endpoint._matches_filter(record_in_range, filter_obj) is True
        assert endpoint._matches_filter(record_at_min, filter_obj) is True
        assert endpoint._matches_filter(record_at_max, filter_obj) is True
        assert endpoint._matches_filter(record_below, filter_obj) is False
        assert endpoint._matches_filter(record_above, filter_obj) is False
        assert endpoint._matches_filter(record_none, filter_obj) is False

    def test_matches_filter_empty_record_lists(self, endpoint: GKGEndpoint) -> None:
        """Filter handles empty persons/orgs/themes lists on records."""
        filter_persons = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            persons=["Obama"],
        )

        filter_orgs = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            organizations=["UN"],
        )

        filter_themes = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            themes=["ENV_CLIMATE"],
        )

        record_empty = make_gkg_record(persons=[], organizations=[], themes=[])

        assert endpoint._matches_filter(record_empty, filter_persons) is False
        assert endpoint._matches_filter(record_empty, filter_orgs) is False
        assert endpoint._matches_filter(record_empty, filter_themes) is False

    def test_matches_filter_none_values_skip(
        self,
        endpoint: GKGEndpoint,
        base_filter: GKGFilter,
    ) -> None:
        """None filter values skip that criterion."""
        record = make_gkg_record(
            themes=["TAX_FNCACT"],
            persons=["Joe Biden"],
            tone=5.0,
        )

        # Should match because no filter criteria are set
        assert endpoint._matches_filter(record, base_filter) is True

    def test_matches_filter_all_fields(self, endpoint: GKGEndpoint) -> None:
        """All filter fields applied together."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            themes=["ENV_CLIMATE"],
            persons=["Obama"],
            organizations=["United Nations"],
            country="US",
            min_tone=-1.0,
            max_tone=1.0,
        )

        # Record that matches all criteria
        record_match = make_gkg_record(
            themes=["ENV_CLIMATE"],
            persons=["Barack Obama"],
            organizations=["United Nations"],
            locations=["US"],
            tone=0.0,
        )

        # Record that fails one criterion (wrong theme)
        record_wrong_theme = make_gkg_record(
            themes=["TAX_FNCACT"],  # Wrong
            persons=["Barack Obama"],
            organizations=["United Nations"],
            locations=["US"],
            tone=0.0,
        )

        assert endpoint._matches_filter(record_match, filter_obj) is True
        assert endpoint._matches_filter(record_wrong_theme, filter_obj) is False

    def test_matches_filter_theme_prefix_with_themes(
        self,
        endpoint: GKGEndpoint,
    ) -> None:
        """Theme prefix and themes can both be specified."""
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            themes=["TAX_FNCACT"],
            theme_prefix="ENV_",
        )

        # Needs to match both: one of the themes AND the prefix
        record_has_both = make_gkg_record(themes=["TAX_FNCACT", "ENV_CLIMATE"])
        record_theme_only = make_gkg_record(themes=["TAX_FNCACT"])
        record_prefix_only = make_gkg_record(themes=["ENV_CLIMATE"])

        assert endpoint._matches_filter(record_has_both, filter_obj) is True
        assert endpoint._matches_filter(record_theme_only, filter_obj) is False
        assert endpoint._matches_filter(record_prefix_only, filter_obj) is False

    def test_matches_filter_empty_filter_lists(self, endpoint: GKGEndpoint) -> None:
        """Empty filter lists (not None) should not filter anything."""
        # When filter has empty list, it becomes None after validation
        # but we can test the _matches_filter behavior directly
        base = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))
        # Manually set empty lists (bypassing validation which converts [] to None)
        modified_filter: Any = base.model_copy()
        object.__setattr__(modified_filter, "themes", [])
        object.__setattr__(modified_filter, "persons", [])
        object.__setattr__(modified_filter, "organizations", [])

        record = make_gkg_record(
            themes=["ENV_CLIMATE"],
            persons=["Obama"],
            organizations=["UN"],
        )

        # Empty lists should match (no filtering)
        assert endpoint._matches_filter(record, modified_filter) is True

    def test_matches_filter_country_accepts_both_fips_and_iso3(
        self,
        endpoint: GKGEndpoint,
    ) -> None:
        """Both FIPS and ISO3 country codes work in country filter.

        Users can pass either 'US' (FIPS) or 'USA' (ISO3) and both
        should filter records correctly. The filter normalizes ISO3
        to FIPS internally.
        """
        # Record with FIPS code (as in real GDELT data)
        record = make_gkg_record(locations=["US"])

        # Filter with ISO3 should match (normalized to FIPS)
        filter_iso3 = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            country="USA",  # ISO3
        )
        assert endpoint._matches_filter(record, filter_iso3) is True

        # Filter with FIPS should also match
        filter_fips = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            country="US",  # FIPS
        )
        assert endpoint._matches_filter(record, filter_fips) is True

        # Test with other country codes too
        record_uk = make_gkg_record(locations=["UK"])
        filter_gbr = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            country="GBR",  # ISO3 for UK
        )
        assert endpoint._matches_filter(record_uk, filter_gbr) is True
