"""Unit tests for EventsEndpoint client-side filtering."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import pytest

from py_gdelt.endpoints.events import EventsEndpoint
from py_gdelt.filters import DateRange, EventFilter
from py_gdelt.models.common import Location
from py_gdelt.models.events import Actor, Event


def make_event(
    *,
    actor1_country: str | None = None,
    actor2_country: str | None = None,
    action_country: str | None = None,
    event_code: str = "010",
    event_root_code: str = "01",
    event_base_code: str = "010",
    avg_tone: float = 0.0,
) -> Event:
    """Create a test Event with specified fields.

    Args:
        actor1_country: FIPS country code for Actor1.
        actor2_country: FIPS country code for Actor2.
        action_country: FIPS country code for action location.
        event_code: CAMEO event code.
        event_root_code: CAMEO root event code.
        event_base_code: CAMEO base event code.
        avg_tone: Average tone value.

    Returns:
        Event instance with specified field values.
    """
    return Event(
        global_event_id=1,
        date=date(2024, 1, 1),
        actor1=Actor(country_code=actor1_country) if actor1_country else None,
        actor2=Actor(country_code=actor2_country) if actor2_country else None,
        action_geo=Location(country_code=action_country) if action_country else None,
        event_code=event_code,
        event_root_code=event_root_code,
        event_base_code=event_base_code,
        quad_class=1,
        goldstein_scale=0.0,
        avg_tone=avg_tone,
    )


class TestEventsClientSideFiltering:
    """Test client-side filtering for EventsEndpoint."""

    @pytest.fixture
    def endpoint(self) -> EventsEndpoint:
        """Create an EventsEndpoint for testing.

        Returns:
            EventsEndpoint instance with mocked fetcher.
        """
        endpoint = EventsEndpoint.__new__(EventsEndpoint)
        endpoint._fetcher = MagicMock()
        return endpoint

    @pytest.fixture
    def base_filter(self) -> EventFilter:
        """Create a base EventFilter with only date_range set.

        Returns:
            EventFilter with date_range starting 2024-01-01.
        """
        return EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

    def test_matches_filter_actor1_country(self, endpoint: EventsEndpoint) -> None:
        """Filter by actor1_country works client-side."""
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor1_country="US",
        )

        record_match = make_event(actor1_country="US")
        record_no_match = make_event(actor1_country="UK")
        record_none = make_event(actor1_country=None)

        assert endpoint._matches_filter(record_match, filter_obj) is True
        assert endpoint._matches_filter(record_no_match, filter_obj) is False
        assert endpoint._matches_filter(record_none, filter_obj) is False

    def test_matches_filter_actor2_country(self, endpoint: EventsEndpoint) -> None:
        """Filter by actor2_country works client-side."""
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor2_country="UK",
        )

        record_match = make_event(actor2_country="UK")
        record_no_match = make_event(actor2_country="US")

        assert endpoint._matches_filter(record_match, filter_obj) is True
        assert endpoint._matches_filter(record_no_match, filter_obj) is False

    def test_matches_filter_action_country(self, endpoint: EventsEndpoint) -> None:
        """Filter by action_country works client-side."""
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            action_country="FR",
        )

        record_match = make_event(action_country="FR")
        record_no_match = make_event(action_country="GM")
        record_none = make_event(action_country=None)

        assert endpoint._matches_filter(record_match, filter_obj) is True
        assert endpoint._matches_filter(record_no_match, filter_obj) is False
        assert endpoint._matches_filter(record_none, filter_obj) is False

    def test_matches_filter_event_code(self, endpoint: EventsEndpoint) -> None:
        """Filter by event_code works client-side."""
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            event_code="020",
        )

        record_match = make_event(event_code="020")
        record_no_match = make_event(event_code="010")

        assert endpoint._matches_filter(record_match, filter_obj) is True
        assert endpoint._matches_filter(record_no_match, filter_obj) is False

    def test_matches_filter_event_root_code(self, endpoint: EventsEndpoint) -> None:
        """Filter by event_root_code works client-side."""
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            event_root_code="02",
        )

        record_match = make_event(event_root_code="02")
        record_no_match = make_event(event_root_code="01")

        assert endpoint._matches_filter(record_match, filter_obj) is True
        assert endpoint._matches_filter(record_no_match, filter_obj) is False

    def test_matches_filter_event_base_code(self, endpoint: EventsEndpoint) -> None:
        """Filter by event_base_code works client-side."""
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            event_base_code="021",
        )

        record_match = make_event(event_base_code="021")
        record_no_match = make_event(event_base_code="010")

        assert endpoint._matches_filter(record_match, filter_obj) is True
        assert endpoint._matches_filter(record_no_match, filter_obj) is False

    def test_matches_filter_min_tone(self, endpoint: EventsEndpoint) -> None:
        """Filter by min_tone works client-side."""
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            min_tone=0.0,
        )

        record_positive = make_event(avg_tone=5.0)
        record_zero = make_event(avg_tone=0.0)
        record_negative = make_event(avg_tone=-5.0)

        assert endpoint._matches_filter(record_positive, filter_obj) is True
        assert endpoint._matches_filter(record_zero, filter_obj) is True
        assert endpoint._matches_filter(record_negative, filter_obj) is False

    def test_matches_filter_max_tone(self, endpoint: EventsEndpoint) -> None:
        """Filter by max_tone works client-side."""
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            max_tone=0.0,
        )

        record_positive = make_event(avg_tone=5.0)
        record_zero = make_event(avg_tone=0.0)
        record_negative = make_event(avg_tone=-5.0)

        assert endpoint._matches_filter(record_positive, filter_obj) is False
        assert endpoint._matches_filter(record_zero, filter_obj) is True
        assert endpoint._matches_filter(record_negative, filter_obj) is True

    def test_matches_filter_tone_range(self, endpoint: EventsEndpoint) -> None:
        """Filter by min_tone and max_tone together works client-side."""
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            min_tone=-2.0,
            max_tone=2.0,
        )

        record_in_range = make_event(avg_tone=0.0)
        record_at_min = make_event(avg_tone=-2.0)
        record_at_max = make_event(avg_tone=2.0)
        record_below = make_event(avg_tone=-5.0)
        record_above = make_event(avg_tone=5.0)

        assert endpoint._matches_filter(record_in_range, filter_obj) is True
        assert endpoint._matches_filter(record_at_min, filter_obj) is True
        assert endpoint._matches_filter(record_at_max, filter_obj) is True
        assert endpoint._matches_filter(record_below, filter_obj) is False
        assert endpoint._matches_filter(record_above, filter_obj) is False

    def test_matches_filter_none_values_skip(
        self,
        endpoint: EventsEndpoint,
        base_filter: EventFilter,
    ) -> None:
        """None filter values skip that criterion."""
        record = make_event(
            actor1_country="US",
            event_code="020",
            avg_tone=5.0,
        )

        # Should match because no filter criteria are set
        assert endpoint._matches_filter(record, base_filter) is True

    def test_matches_filter_all_fields(self, endpoint: EventsEndpoint) -> None:
        """All filter fields applied together."""
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor1_country="US",
            actor2_country="UK",
            action_country="FR",
            event_code="020",
            min_tone=-1.0,
            max_tone=1.0,
        )

        # Record that matches all criteria
        record_match = make_event(
            actor1_country="US",
            actor2_country="UK",
            action_country="FR",
            event_code="020",
            avg_tone=0.0,
        )

        # Record that fails one criterion (wrong actor1_country)
        record_wrong_actor = make_event(
            actor1_country="GM",
            actor2_country="UK",
            action_country="FR",
            event_code="020",
            avg_tone=0.0,
        )

        assert endpoint._matches_filter(record_match, filter_obj) is True
        assert endpoint._matches_filter(record_wrong_actor, filter_obj) is False

    def test_matches_filter_actor1_none_actor_object(
        self,
        endpoint: EventsEndpoint,
    ) -> None:
        """Filter handles None actor1 object gracefully."""
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor1_country="US",
        )

        # Record with actor1=None (not just country_code=None)
        record = Event(
            global_event_id=1,
            date=date(2024, 1, 1),
            actor1=None,
            actor2=None,
            action_geo=None,
            event_code="010",
            event_root_code="01",
            event_base_code="010",
            quad_class=1,
            goldstein_scale=0.0,
            avg_tone=0.0,
        )

        assert endpoint._matches_filter(record, filter_obj) is False

    def test_matches_filter_actor2_none_actor_object(
        self,
        endpoint: EventsEndpoint,
    ) -> None:
        """Filter handles None actor2 object gracefully."""
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor2_country="UK",
        )

        record = Event(
            global_event_id=1,
            date=date(2024, 1, 1),
            actor1=None,
            actor2=None,
            action_geo=None,
            event_code="010",
            event_root_code="01",
            event_base_code="010",
            quad_class=1,
            goldstein_scale=0.0,
            avg_tone=0.0,
        )

        assert endpoint._matches_filter(record, filter_obj) is False

    def test_matches_filter_country_accepts_both_fips_and_iso3(
        self,
        endpoint: EventsEndpoint,
    ) -> None:
        """Both FIPS and ISO3 country codes work in filter.

        Users can pass either 'US' (FIPS) or 'USA' (ISO3) and both
        should filter records correctly. The filter normalizes ISO3
        to FIPS internally.
        """
        # Record with FIPS code (as in real GDELT data)
        record = make_event(actor1_country="US")

        # Filter with ISO3 should match (normalized to FIPS)
        filter_iso3 = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor1_country="USA",  # ISO3
        )
        assert endpoint._matches_filter(record, filter_iso3) is True

        # Filter with FIPS should also match
        filter_fips = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor1_country="US",  # FIPS
        )
        assert endpoint._matches_filter(record, filter_fips) is True

        # Test with other country codes too
        record_uk = make_event(actor1_country="UK")
        filter_gbr = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor1_country="GBR",  # ISO3 for UK
        )
        assert endpoint._matches_filter(record_uk, filter_gbr) is True
