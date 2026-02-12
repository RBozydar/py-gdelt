"""
Tests for py_gdelt.filters module.

Tests cover validation logic for all filter models including date ranges,
country codes, CAMEO codes, GKG themes, and various filter constraints.
"""

from __future__ import annotations

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.filters import (
    DateRange,
    DocFilter,
    EventFilter,
    GeoFilter,
    GKGFilter,
    TVFilter,
    TVGKGFilter,
)


class TestDateRange:
    """Tests for DateRange filter model."""

    def test_single_day_range(self) -> None:
        """Test valid single day range (end=None)."""
        dr = DateRange(start=date(2024, 1, 1))
        assert dr.start == date(2024, 1, 1)
        assert dr.end is None
        assert dr.days == 1

    def test_multi_day_range(self) -> None:
        """Test valid multi-day range."""
        dr = DateRange(start=date(2024, 1, 1), end=date(2024, 1, 10))
        assert dr.start == date(2024, 1, 1)
        assert dr.end == date(2024, 1, 10)
        assert dr.days == 10

    def test_invalid_range_end_before_start(self) -> None:
        """Test that end < start raises ValueError."""
        with pytest.raises(ValidationError, match="end date must be >= start date"):
            DateRange(start=date(2024, 1, 10), end=date(2024, 1, 1))

    def test_large_date_range_allowed(self) -> None:
        """Test that large date ranges are allowed (no enforced limit)."""
        # Multiple years should work for file-based sources
        dr = DateRange(start=date(2020, 1, 1), end=date(2025, 1, 1))
        assert dr.days > 1800  # ~5 years, inclusive

    def test_multi_year_range_allowed(self) -> None:
        """Test that multi-year date ranges work for historical queries."""
        # Events v1 goes back to 1979, so large ranges should be supported
        dr = DateRange(start=date(2015, 1, 1), end=date(2024, 12, 31))
        assert dr.days > 3600  # ~10 years, inclusive

    def test_days_property_with_end_none(self) -> None:
        """Test days property when end is None."""
        dr = DateRange(start=date(2024, 1, 1))
        assert dr.days == 1

    def test_days_property_calculation(self) -> None:
        """Test days property calculation."""
        dr = DateRange(start=date(2024, 1, 1), end=date(2024, 1, 5))
        assert dr.days == 5  # Inclusive of both start and end


class TestEventFilter:
    """Tests for EventFilter model."""

    def test_valid_filter_creation(self) -> None:
        """Test creating a valid event filter with all options."""
        ef = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor1_country="US",
            actor2_country="UK",
            event_code="01",
            min_tone=-5.0,
            max_tone=5.0,
            action_country="FR",
            include_translated=False,
        )
        assert ef.actor1_country == "US"
        assert ef.actor2_country == "UK"
        assert ef.event_code == "01"
        assert ef.min_tone == -5.0
        assert ef.max_tone == 5.0
        assert ef.action_country == "FR"
        assert ef.include_translated is False

    def test_invalid_country_code_raises_error(self) -> None:
        """Test that invalid country code raises InvalidCodeError."""
        with pytest.raises(InvalidCodeError) as exc_info:
            EventFilter(
                date_range=DateRange(start=date(2024, 1, 1)),
                actor1_country="INVALID",
            )
        assert exc_info.value.code == "INVALID"
        assert exc_info.value.code_type == "country"

    def test_invalid_cameo_code_raises_error(self) -> None:
        """Test that invalid CAMEO code raises InvalidCodeError."""
        with pytest.raises(InvalidCodeError) as exc_info:
            EventFilter(
                date_range=DateRange(start=date(2024, 1, 1)),
                event_code="9999",
            )
        assert exc_info.value.code == "9999"
        assert exc_info.value.code_type == "CAMEO"

    def test_country_codes_normalized_to_uppercase(self) -> None:
        """Test that country codes are normalized to uppercase."""
        ef = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor1_country="us",
            actor2_country="uk",
            action_country="fr",
        )
        assert ef.actor1_country == "US"
        assert ef.actor2_country == "UK"
        assert ef.action_country == "FR"

    def test_optional_fields_default_to_none(self) -> None:
        """Test that optional fields default to None."""
        ef = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
        assert ef.actor1_country is None
        assert ef.actor2_country is None
        assert ef.event_code is None
        assert ef.event_root_code is None
        assert ef.event_base_code is None
        assert ef.min_tone is None
        assert ef.max_tone is None
        assert ef.action_country is None
        assert ef.include_translated is True


class TestGKGFilter:
    """Tests for GKGFilter model."""

    def test_valid_filter_with_themes(self) -> None:
        """Test creating a valid GKG filter with themes."""
        gf = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            themes=["ENV_CLIMATECHANGE", "HEALTH_PANDEMIC"],
            country="US",
            min_tone=-5.0,
            max_tone=5.0,
            include_translated=False,
        )
        assert gf.themes == ["ENV_CLIMATECHANGE", "HEALTH_PANDEMIC"]
        assert gf.country == "US"
        assert gf.min_tone == -5.0
        assert gf.max_tone == 5.0
        assert gf.include_translated is False

    def test_invalid_theme_raises_error(self) -> None:
        """Test that invalid theme format raises InvalidCodeError."""
        with pytest.raises(InvalidCodeError) as exc_info:
            GKGFilter(
                date_range=DateRange(start=date(2024, 1, 1)),
                themes=["invalid-theme"],  # lowercase with dash is invalid format
            )
        assert exc_info.value.code == "invalid-theme"
        assert exc_info.value.code_type == "GKG theme"

    def test_theme_list_validation(self) -> None:
        """Test that all themes in list are validated."""
        with pytest.raises(InvalidCodeError) as exc_info:
            GKGFilter(
                date_range=DateRange(start=date(2024, 1, 1)),
                themes=["ENV_CLIMATECHANGE", "invalid-theme", "HEALTH_PANDEMIC"],  # invalid format
            )
        assert exc_info.value.code == "invalid-theme"

    def test_country_normalized_to_uppercase(self) -> None:
        """Test that country code is normalized to uppercase."""
        gf = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            country="us",
        )
        assert gf.country == "US"

    def test_invalid_country_raises_error(self) -> None:
        """Test that invalid country code raises InvalidCodeError."""
        with pytest.raises(InvalidCodeError) as exc_info:
            GKGFilter(
                date_range=DateRange(start=date(2024, 1, 1)),
                country="INVALID",
            )
        assert exc_info.value.code == "INVALID"
        assert exc_info.value.code_type == "country"

    def test_optional_fields_default_to_none(self) -> None:
        """Test that optional fields default to None."""
        gf = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))
        assert gf.themes is None
        assert gf.theme_prefix is None
        assert gf.persons is None
        assert gf.organizations is None
        assert gf.country is None
        assert gf.min_tone is None
        assert gf.max_tone is None
        assert gf.include_translated is True

    def test_gkg_filter_themes_uppercased(self) -> None:
        """Test that themes are normalized to uppercase."""
        gf = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            themes=["env_climatechange"],
        )
        assert gf.themes == ["ENV_CLIMATECHANGE"]


class TestDocFilter:
    """Tests for DocFilter model."""

    def test_valid_filter_creation(self) -> None:
        """Test creating a valid DOC filter."""
        df = DocFilter(
            query="climate change",
            timespan="24h",
            source_country="US",
            source_language="en",
            max_results=100,
            sort_by="relevance",
            mode="timelinevol",
        )
        assert df.query == "climate change"
        assert df.timespan == "24h"
        assert df.source_country == "US"
        assert df.source_language == "en"
        assert df.max_results == 100
        assert df.sort_by == "relevance"
        assert df.mode == "timelinevol"

    def test_cannot_use_both_timespan_and_datetime_range(self) -> None:
        """Test that timespan and datetime range are mutually exclusive."""
        with pytest.raises(
            ValidationError,
            match="Cannot specify both timespan and datetime range",
        ):
            DocFilter(
                query="test",
                timespan="24h",
                start_datetime=datetime(2024, 1, 1),
            )

    def test_max_results_bounds_validation(self) -> None:
        """Test that max_results must be between 1 and 250."""
        # Too low
        with pytest.raises(ValidationError):
            DocFilter(query="test", max_results=0)

        # Too high
        with pytest.raises(ValidationError):
            DocFilter(query="test", max_results=251)

        # Valid boundaries
        df_min = DocFilter(query="test", max_results=1)
        assert df_min.max_results == 1

        df_max = DocFilter(query="test", max_results=250)
        assert df_max.max_results == 250

    def test_default_values(self) -> None:
        """Test default values for optional fields."""
        df = DocFilter(query="test")
        assert df.timespan is None
        assert df.start_datetime is None
        assert df.end_datetime is None
        assert df.source_country is None
        assert df.source_language is None
        assert df.max_results == 250
        assert df.sort_by == "date"
        assert df.mode == "artlist"

    def test_source_country_normalized_to_uppercase(self) -> None:
        """Test that source_country is normalized to uppercase."""
        df = DocFilter(query="test", source_country="us")
        assert df.source_country == "US"

    def test_invalid_source_country_raises_error(self) -> None:
        """Test that invalid source_country raises InvalidCodeError."""
        with pytest.raises(InvalidCodeError) as exc_info:
            DocFilter(query="test", source_country="INVALID")
        assert exc_info.value.code == "INVALID"
        assert exc_info.value.code_type == "country"


class TestGeoFilter:
    """Tests for GeoFilter model."""

    def test_valid_bounding_box(self) -> None:
        """Test creating a filter with valid bounding box."""
        gf = GeoFilter(
            query="earthquake",
            bounding_box=(40.0, -120.0, 45.0, -115.0),
            timespan="7d",
            max_results=100,
        )
        assert gf.query == "earthquake"
        assert gf.bounding_box == (40.0, -120.0, 45.0, -115.0)
        assert gf.timespan == "7d"
        assert gf.max_results == 100

    def test_invalid_latitude_range(self) -> None:
        """Test that latitude outside -90 to 90 raises ValueError."""
        with pytest.raises(ValidationError, match="Latitude must be between -90 and 90"):
            GeoFilter(query="test", bounding_box=(91.0, 0.0, 95.0, 10.0))

        with pytest.raises(ValidationError, match="Latitude must be between -90 and 90"):
            GeoFilter(query="test", bounding_box=(-91.0, 0.0, -85.0, 10.0))

    def test_invalid_longitude_range(self) -> None:
        """Test that longitude outside -180 to 180 raises ValueError."""
        with pytest.raises(ValidationError, match="Longitude must be between -180 and 180"):
            GeoFilter(query="test", bounding_box=(0.0, 181.0, 10.0, 185.0))

        with pytest.raises(ValidationError, match="Longitude must be between -180 and 180"):
            GeoFilter(query="test", bounding_box=(0.0, -181.0, 10.0, -175.0))

    def test_invalid_bbox_ordering_lat(self) -> None:
        """Test that min_lat > max_lat raises ValueError."""
        with pytest.raises(ValidationError, match="min_lat must be <= max_lat"):
            GeoFilter(query="test", bounding_box=(45.0, -120.0, 40.0, -115.0))

    def test_invalid_bbox_ordering_lon(self) -> None:
        """Test that min_lon > max_lon raises ValueError."""
        with pytest.raises(ValidationError, match="min_lon must be <= max_lon"):
            GeoFilter(query="test", bounding_box=(40.0, -115.0, 45.0, -120.0))

    def test_bounding_box_none_allowed(self) -> None:
        """Test that bounding_box can be None."""
        gf = GeoFilter(query="test")
        assert gf.bounding_box is None

    def test_default_values(self) -> None:
        """Test default values for optional fields."""
        gf = GeoFilter(query="test")
        assert gf.bounding_box is None
        assert gf.timespan is None
        assert gf.max_results == 250


class TestTVFilter:
    """Tests for TVFilter model."""

    def test_basic_creation(self) -> None:
        """Test creating a basic TV filter."""
        tf = TVFilter(
            query="presidential debate",
            timespan="24h",
            station="CNN",
            market="National",
            max_results=100,
            mode="TimelineVol",
        )
        assert tf.query == "presidential debate"
        assert tf.timespan == "24h"
        assert tf.station == "CNN"
        assert tf.market == "National"
        assert tf.max_results == 100
        assert tf.mode == "TimelineVol"

    def test_mode_validation(self) -> None:
        """Test that mode accepts only valid values."""
        # Valid modes (PascalCase required by GDELT TV API)
        tf1 = TVFilter(query="test", mode="ClipGallery")
        assert tf1.mode == "ClipGallery"

        tf2 = TVFilter(query="test", mode="TimelineVol")
        assert tf2.mode == "TimelineVol"

        tf3 = TVFilter(query="test", mode="StationChart")
        assert tf3.mode == "StationChart"

        # Invalid mode - Pydantic will validate at runtime
        with pytest.raises(ValidationError):
            TVFilter(query="test", mode="invalid_mode")  # type: ignore[arg-type]

    def test_default_values(self) -> None:
        """Test default values for optional fields."""
        tf = TVFilter(query="test")
        assert tf.timespan is None
        assert tf.start_datetime is None
        assert tf.end_datetime is None
        assert tf.station is None
        assert tf.market is None
        assert tf.max_results == 250
        assert tf.mode == "ClipGallery"

    def test_datetime_range(self) -> None:
        """Test using datetime range instead of timespan."""
        tf = TVFilter(
            query="test",
            start_datetime=datetime(2024, 1, 1, 12, 0),
            end_datetime=datetime(2024, 1, 2, 12, 0),
        )
        assert tf.start_datetime == datetime(2024, 1, 1, 12, 0)
        assert tf.end_datetime == datetime(2024, 1, 2, 12, 0)
        assert tf.timespan is None


class TestTVGKGFilter:
    """Tests for TVGKGFilter model."""

    def test_valid_filter_with_themes(self) -> None:
        """Test creating a valid TV-GKG filter with themes."""
        tvgf = TVGKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            themes=["ENV_CLIMATECHANGE", "HEALTH_PANDEMIC"],
            station="CNN",
        )
        assert tvgf.themes == ["ENV_CLIMATECHANGE", "HEALTH_PANDEMIC"]
        assert tvgf.station == "CNN"

    def test_invalid_theme_format_raises_error(self) -> None:
        """Test that invalid theme format raises InvalidCodeError.

        Note: GKGThemes.validate() uses relaxed validation - it accepts any
        well-formed theme (uppercase with underscores) even if unknown, because
        GDELT has 59,000+ themes. Only invalid FORMAT triggers an error.
        """
        with pytest.raises(InvalidCodeError) as exc_info:
            TVGKGFilter(
                date_range=DateRange(start=date(2024, 1, 1)),
                themes=["invalid-theme"],  # lowercase with dash = invalid format
            )
        assert exc_info.value.code == "invalid-theme"
        assert exc_info.value.code_type == "GKG theme"

    def test_theme_list_validation(self) -> None:
        """Test that all themes in list are validated for format."""
        with pytest.raises(InvalidCodeError) as exc_info:
            TVGKGFilter(
                date_range=DateRange(start=date(2024, 1, 1)),
                themes=["ENV_CLIMATECHANGE", "bad format!", "HEALTH_PANDEMIC"],
            )
        assert exc_info.value.code == "bad format!"

    def test_station_normalized_to_uppercase(self) -> None:
        """Test that station name is normalized to uppercase."""
        tvgf = TVGKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            station="cnn",
        )
        assert tvgf.station == "CNN"

    def test_optional_fields_default_to_none(self) -> None:
        """Test that optional fields default to None."""
        tvgf = TVGKGFilter(date_range=DateRange(start=date(2024, 1, 1)))
        assert tvgf.themes is None
        assert tvgf.station is None
