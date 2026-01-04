"""Comprehensive tests for common models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from py_gdelt.models.common import (
    EntityMention,
    FailedRequest,
    FetchResult,
    Location,
    ToneScores,
)


class TestLocation:
    """Tests for Location model."""

    def test_as_tuple_with_valid_coordinates(self) -> None:
        """Test as_tuple() returns correct tuple with valid coordinates."""
        location = Location(lat=40.7128, lon=-74.0060)
        result = location.as_tuple()
        assert result == (40.7128, -74.0060)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_as_tuple_raises_when_lat_is_none(self) -> None:
        """Test as_tuple() raises ValueError when lat is None."""
        location = Location(lat=None, lon=-74.0060)
        with pytest.raises(ValueError, match="Cannot create tuple: lat or lon is None"):
            location.as_tuple()

    def test_as_tuple_raises_when_lon_is_none(self) -> None:
        """Test as_tuple() raises ValueError when lon is None."""
        location = Location(lat=40.7128, lon=None)
        with pytest.raises(ValueError, match="Cannot create tuple: lat or lon is None"):
            location.as_tuple()

    def test_as_tuple_raises_when_both_none(self) -> None:
        """Test as_tuple() raises ValueError when both lat and lon are None."""
        location = Location(lat=None, lon=None)
        with pytest.raises(ValueError, match="Cannot create tuple: lat or lon is None"):
            location.as_tuple()

    def test_as_wkt_returns_correct_format(self) -> None:
        """Test as_wkt() returns correct WKT POINT format."""
        location = Location(lat=40.7128, lon=-74.0060)
        result = location.as_wkt()
        # WKT format is POINT(lon lat) - note the order!
        assert result == "POINT(-74.006 40.7128)"

    def test_as_wkt_raises_when_coords_missing(self) -> None:
        """Test as_wkt() raises ValueError when coordinates are missing."""
        location = Location(lat=None, lon=-74.0060)
        with pytest.raises(ValueError, match="Cannot create WKT: lat or lon is None"):
            location.as_wkt()

    def test_has_coordinates_property_true(self) -> None:
        """Test has_coordinates returns True when both lat/lon present."""
        location = Location(lat=40.7128, lon=-74.0060)
        assert location.has_coordinates is True

    def test_has_coordinates_property_false_no_lat(self) -> None:
        """Test has_coordinates returns False when lat is None."""
        location = Location(lat=None, lon=-74.0060)
        assert location.has_coordinates is False

    def test_has_coordinates_property_false_no_lon(self) -> None:
        """Test has_coordinates returns False when lon is None."""
        location = Location(lat=40.7128, lon=None)
        assert location.has_coordinates is False

    def test_has_coordinates_property_false_both_none(self) -> None:
        """Test has_coordinates returns False when both are None."""
        location = Location()
        assert location.has_coordinates is False

    def test_serialization_full_data(self) -> None:
        """Test Location can be serialized and deserialized with all fields."""
        original = Location(
            lat=40.7128,
            lon=-74.0060,
            feature_id="NYC123",
            name="New York City",
            country_code="US",
            adm1_code="NY",
            adm2_code="061",
            geo_type=3,
        )
        # Serialize to dict
        data = original.model_dump()
        # Deserialize back
        restored = Location(**data)
        assert restored.lat == original.lat
        assert restored.lon == original.lon
        assert restored.feature_id == original.feature_id
        assert restored.name == original.name
        assert restored.country_code == original.country_code
        assert restored.adm1_code == original.adm1_code
        assert restored.adm2_code == original.adm2_code
        assert restored.geo_type == original.geo_type

    def test_serialization_minimal_data(self) -> None:
        """Test Location with only coordinates can be serialized."""
        original = Location(lat=40.7128, lon=-74.0060)
        data = original.model_dump()
        restored = Location(**data)
        assert restored.lat == 40.7128
        assert restored.lon == -74.0060
        assert restored.feature_id is None
        assert restored.name is None

    def test_json_serialization(self) -> None:
        """Test Location can be serialized to JSON."""
        location = Location(lat=40.7128, lon=-74.0060, name="NYC")
        json_str = location.model_dump_json()
        # Deserialize from JSON
        restored = Location.model_validate_json(json_str)
        assert restored.lat == 40.7128
        assert restored.lon == -74.0060
        assert restored.name == "NYC"


class TestToneScores:
    """Tests for ToneScores model."""

    def test_creation_with_valid_values(self) -> None:
        """Test ToneScores can be created with valid values."""
        tone = ToneScores(
            tone=5.5,
            positive_score=10.2,
            negative_score=-8.3,
            polarity=12.5,
            activity_reference_density=3.2,
            self_group_reference_density=1.8,
            word_count=500,
        )
        assert tone.tone == 5.5
        assert tone.positive_score == 10.2
        assert tone.negative_score == -8.3
        assert tone.polarity == 12.5
        assert tone.activity_reference_density == 3.2
        assert tone.self_group_reference_density == 1.8
        assert tone.word_count == 500

    def test_tone_range_validation_at_min(self) -> None:
        """Test tone accepts -100."""
        tone = ToneScores(
            tone=-100.0,
            positive_score=0.0,
            negative_score=100.0,
            polarity=0.0,
            activity_reference_density=0.0,
            self_group_reference_density=0.0,
        )
        assert tone.tone == -100.0

    def test_tone_range_validation_at_max(self) -> None:
        """Test tone accepts +100."""
        tone = ToneScores(
            tone=100.0,
            positive_score=100.0,
            negative_score=0.0,
            polarity=0.0,
            activity_reference_density=0.0,
            self_group_reference_density=0.0,
        )
        assert tone.tone == 100.0

    def test_tone_range_validation_below_min(self) -> None:
        """Test tone validation fails for values below -100."""
        with pytest.raises(ValidationError) as exc_info:
            ToneScores(
                tone=-100.1,
                positive_score=0.0,
                negative_score=0.0,
                polarity=0.0,
                activity_reference_density=0.0,
                self_group_reference_density=0.0,
            )
        errors = exc_info.value.errors()
        assert any("greater than or equal to -100" in str(e) for e in errors)

    def test_tone_range_validation_above_max(self) -> None:
        """Test tone validation fails for values above +100."""
        with pytest.raises(ValidationError) as exc_info:
            ToneScores(
                tone=100.1,
                positive_score=0.0,
                negative_score=0.0,
                polarity=0.0,
                activity_reference_density=0.0,
                self_group_reference_density=0.0,
            )
        errors = exc_info.value.errors()
        assert any("less than or equal to 100" in str(e) for e in errors)

    def test_word_count_optional(self) -> None:
        """Test word_count is optional and defaults to None."""
        tone = ToneScores(
            tone=0.0,
            positive_score=0.0,
            negative_score=0.0,
            polarity=0.0,
            activity_reference_density=0.0,
            self_group_reference_density=0.0,
        )
        assert tone.word_count is None

    def test_serialization(self) -> None:
        """Test ToneScores serialization and deserialization."""
        original = ToneScores(
            tone=5.5,
            positive_score=10.2,
            negative_score=-8.3,
            polarity=12.5,
            activity_reference_density=3.2,
            self_group_reference_density=1.8,
            word_count=500,
        )
        data = original.model_dump()
        restored = ToneScores(**data)
        assert restored.tone == original.tone
        assert restored.positive_score == original.positive_score
        assert restored.negative_score == original.negative_score
        assert restored.polarity == original.polarity
        assert restored.activity_reference_density == original.activity_reference_density
        assert restored.self_group_reference_density == original.self_group_reference_density
        assert restored.word_count == original.word_count


class TestEntityMention:
    """Tests for EntityMention model."""

    def test_creation_with_required_fields(self) -> None:
        """Test EntityMention can be created with only required fields."""
        entity = EntityMention(entity_type="PERSON", name="John Doe")
        assert entity.entity_type == "PERSON"
        assert entity.name == "John Doe"
        assert entity.offset is None
        assert entity.confidence is None

    def test_creation_with_optional_fields(self) -> None:
        """Test EntityMention with all optional fields."""
        entity = EntityMention(
            entity_type="ORG",
            name="Acme Corp",
            offset=150,
            confidence=0.95,
        )
        assert entity.entity_type == "ORG"
        assert entity.name == "Acme Corp"
        assert entity.offset == 150
        assert entity.confidence == 0.95

    def test_entity_types(self) -> None:
        """Test various entity types."""
        types = ["PERSON", "ORG", "LOCATION", "GPE", "DATE", "MISC"]
        for entity_type in types:
            entity = EntityMention(entity_type=entity_type, name="Test")
            assert entity.entity_type == entity_type

    def test_serialization(self) -> None:
        """Test EntityMention serialization and deserialization."""
        original = EntityMention(
            entity_type="LOCATION",
            name="Paris",
            offset=42,
            confidence=0.99,
        )
        data = original.model_dump()
        restored = EntityMention(**data)
        assert restored.entity_type == original.entity_type
        assert restored.name == original.name
        assert restored.offset == original.offset
        assert restored.confidence == original.confidence

    def test_json_serialization(self) -> None:
        """Test EntityMention JSON serialization."""
        entity = EntityMention(entity_type="PERSON", name="Jane Smith", offset=10)
        json_str = entity.model_dump_json()
        restored = EntityMention.model_validate_json(json_str)
        assert restored.entity_type == "PERSON"
        assert restored.name == "Jane Smith"
        assert restored.offset == 10


class TestFailedRequest:
    """Tests for FailedRequest dataclass."""

    def test_creation_with_required_fields(self) -> None:
        """Test FailedRequest with only required fields."""
        failed = FailedRequest(url="https://example.com", error="Connection timeout")
        assert failed.url == "https://example.com"
        assert failed.error == "Connection timeout"
        assert failed.status_code is None
        assert failed.retry_after is None

    def test_creation_with_optional_fields(self) -> None:
        """Test FailedRequest with all fields."""
        failed = FailedRequest(
            url="https://api.gdelt.org/data",
            error="Rate limit exceeded",
            status_code=429,
            retry_after=60,
        )
        assert failed.url == "https://api.gdelt.org/data"
        assert failed.error == "Rate limit exceeded"
        assert failed.status_code == 429
        assert failed.retry_after == 60

    def test_slots_are_used(self) -> None:
        """Test that slots are used (no __dict__)."""
        failed = FailedRequest(url="https://example.com", error="Test")
        # With slots=True, instances should not have __dict__
        assert not hasattr(failed, "__dict__")

    def test_immutable_after_creation(self) -> None:
        """Test that fields can be modified (dataclass is mutable by default)."""
        failed = FailedRequest(url="https://example.com", error="Test")
        # dataclass without frozen=True allows modification
        failed.status_code = 500
        assert failed.status_code == 500


class TestFetchResult:
    """Tests for FetchResult generic dataclass."""

    def test_complete_property_no_failures(self) -> None:
        """Test complete returns True when no requests failed."""
        result = FetchResult(data=[1, 2, 3], failed=[])
        assert result.complete is True

    def test_complete_property_with_failures(self) -> None:
        """Test complete returns False when there are failures."""
        failed = FailedRequest(url="https://example.com", error="Error")
        result = FetchResult(data=[1, 2, 3], failed=[failed])
        assert result.complete is False

    def test_partial_property_some_failures_some_data(self) -> None:
        """Test partial returns True when some failed but data exists."""
        failed = FailedRequest(url="https://example.com", error="Error")
        result = FetchResult(data=[1, 2, 3], failed=[failed])
        assert result.partial is True

    def test_partial_property_no_failures(self) -> None:
        """Test partial returns False when no failures."""
        result = FetchResult(data=[1, 2, 3], failed=[])
        assert result.partial is False

    def test_partial_property_no_data_with_failures(self) -> None:
        """Test partial returns False when no data but failures exist."""
        failed = FailedRequest(url="https://example.com", error="Error")
        result = FetchResult(data=[], failed=[failed])
        assert result.partial is False

    def test_empty_data_with_failures_not_complete(self) -> None:
        """Test empty data with failures is neither complete nor partial."""
        failed = FailedRequest(url="https://example.com", error="Error")
        result = FetchResult(data=[], failed=[failed])
        assert result.complete is False
        assert result.partial is False

    def test_total_failed_property(self) -> None:
        """Test total_failed returns correct count."""
        failed1 = FailedRequest(url="https://example1.com", error="Error 1")
        failed2 = FailedRequest(url="https://example2.com", error="Error 2")
        result = FetchResult(data=[1, 2], failed=[failed1, failed2])
        assert result.total_failed == 2

    def test_iter_allows_direct_iteration(self) -> None:
        """Test __iter__ allows direct iteration over data."""
        result = FetchResult(data=[1, 2, 3, 4, 5])
        items = list(result)
        assert items == [1, 2, 3, 4, 5]

    def test_iter_with_typed_data(self) -> None:
        """Test iteration with typed data."""
        locations = [
            Location(lat=40.7128, lon=-74.0060, name="NYC"),
            Location(lat=34.0522, lon=-118.2437, name="LA"),
        ]
        result = FetchResult[Location](data=locations)
        for idx, location in enumerate(result):
            assert location == locations[idx]

    def test_len_returns_data_count(self) -> None:
        """Test __len__ returns count of data items."""
        result = FetchResult(data=[1, 2, 3, 4, 5])
        assert len(result) == 5

    def test_len_with_empty_data(self) -> None:
        """Test __len__ returns 0 for empty data."""
        result = FetchResult(data=[])
        assert len(result) == 0

    def test_with_typed_location_data(self) -> None:
        """Test FetchResult with Location type."""
        locations = [
            Location(lat=40.7128, lon=-74.0060, name="NYC"),
            Location(lat=34.0522, lon=-118.2437, name="LA"),
        ]
        result = FetchResult[Location](data=locations)
        assert len(result) == 2
        assert result.complete is True
        assert all(isinstance(loc, Location) for loc in result)

    def test_with_typed_data_and_failures(self) -> None:
        """Test FetchResult with typed data and failures."""
        tones = [
            ToneScores(
                tone=5.5,
                positive_score=10.2,
                negative_score=-8.3,
                polarity=12.5,
                activity_reference_density=3.2,
                self_group_reference_density=1.8,
            ),
        ]
        failed = FailedRequest(url="https://example.com", error="Timeout")
        result = FetchResult[ToneScores](data=tones, failed=[failed])
        assert len(result) == 1
        assert result.partial is True
        assert result.total_failed == 1

    def test_default_factory_for_failed(self) -> None:
        """Test that failed list uses default_factory."""
        result1 = FetchResult(data=[1, 2, 3])
        result2 = FetchResult(data=[4, 5, 6])
        # Each should have its own empty list
        assert result1.failed is not result2.failed
        assert result1.failed == []
        assert result2.failed == []
