"""Unit tests for deduplication utilities.

Tests cover all deduplication strategies and edge cases.
"""

from dataclasses import dataclass

from py_gdelt.utils.dedup import DedupeStrategy, deduplicate, get_dedup_key


@dataclass
class MockRecord:
    """Mock record for testing deduplication."""

    source_url: str | None = None
    sql_date: str | None = None
    action_geo_fullname: str | None = None
    actor1_code: str | None = None
    actor2_code: str | None = None
    event_root_code: str | None = None


class TestDedupeStrategy:
    """Test the DedupeStrategy enum."""

    def test_strategy_values(self) -> None:
        """Verify all strategy enum values."""
        assert DedupeStrategy.URL_ONLY == "url_only"
        assert DedupeStrategy.URL_DATE == "url_date"
        assert DedupeStrategy.URL_DATE_LOCATION == "url_date_location"
        assert DedupeStrategy.URL_DATE_LOCATION_ACTORS == "url_date_location_actors"
        assert DedupeStrategy.AGGRESSIVE == "aggressive"

    def test_default_strategy(self) -> None:
        """Verify URL_DATE_LOCATION is intended as default."""
        # This test documents the intended default
        assert DedupeStrategy.URL_DATE_LOCATION.value == "url_date_location"


class TestGetDedupKey:
    """Test the get_dedup_key function."""

    def test_url_only_strategy(self) -> None:
        """URL_ONLY uses only source_url."""
        record = MockRecord(
            source_url="http://example.com",
            sql_date="2024-01-01",
            action_geo_fullname="New York",
        )
        key = get_dedup_key(record, DedupeStrategy.URL_ONLY)
        assert key == ("http://example.com",)

    def test_url_date_strategy(self) -> None:
        """URL_DATE uses source_url and sql_date."""
        record = MockRecord(
            source_url="http://example.com",
            sql_date="2024-01-01",
            action_geo_fullname="New York",
        )
        key = get_dedup_key(record, DedupeStrategy.URL_DATE)
        assert key == ("http://example.com", "2024-01-01")

    def test_url_date_location_strategy(self) -> None:
        """URL_DATE_LOCATION uses source_url, sql_date, and action_geo_fullname."""
        record = MockRecord(
            source_url="http://example.com",
            sql_date="2024-01-01",
            action_geo_fullname="New York",
            actor1_code="USA",
        )
        key = get_dedup_key(record, DedupeStrategy.URL_DATE_LOCATION)
        assert key == ("http://example.com", "2024-01-01", "New York")

    def test_url_date_location_actors_strategy(self) -> None:
        """URL_DATE_LOCATION_ACTORS adds actor codes."""
        record = MockRecord(
            source_url="http://example.com",
            sql_date="2024-01-01",
            action_geo_fullname="New York",
            actor1_code="USA",
            actor2_code="CHN",
            event_root_code="14",
        )
        key = get_dedup_key(record, DedupeStrategy.URL_DATE_LOCATION_ACTORS)
        assert key == ("http://example.com", "2024-01-01", "New York", "USA", "CHN")

    def test_aggressive_strategy(self) -> None:
        """AGGRESSIVE adds event_root_code."""
        record = MockRecord(
            source_url="http://example.com",
            sql_date="2024-01-01",
            action_geo_fullname="New York",
            actor1_code="USA",
            actor2_code="CHN",
            event_root_code="14",
        )
        key = get_dedup_key(record, DedupeStrategy.AGGRESSIVE)
        assert key == (
            "http://example.com",
            "2024-01-01",
            "New York",
            "USA",
            "CHN",
            "14",
        )

    def test_none_values_treated_as_empty_string(self) -> None:
        """None values should be normalized to empty strings."""
        record = MockRecord(
            source_url=None,
            sql_date=None,
            action_geo_fullname=None,
        )
        key = get_dedup_key(record, DedupeStrategy.URL_DATE_LOCATION)
        assert key == ("", "", "")

    def test_mixed_none_and_values(self) -> None:
        """Mixed None and actual values handled correctly."""
        record = MockRecord(
            source_url="http://example.com",
            sql_date=None,
            action_geo_fullname="New York",
        )
        key = get_dedup_key(record, DedupeStrategy.URL_DATE_LOCATION)
        assert key == ("http://example.com", "", "New York")


class TestDeduplicate:
    """Test the deduplicate function."""

    def test_empty_input(self) -> None:
        """Empty iterable returns empty result."""
        result = list(deduplicate([], DedupeStrategy.URL_ONLY))
        assert result == []

    def test_single_record(self) -> None:
        """Single record passes through unchanged."""
        records = [MockRecord(source_url="http://example.com")]
        result = list(deduplicate(records, DedupeStrategy.URL_ONLY))
        assert len(result) == 1
        assert result[0].source_url == "http://example.com"

    def test_no_duplicates(self) -> None:
        """All unique records pass through."""
        records = [
            MockRecord(source_url="http://example1.com"),
            MockRecord(source_url="http://example2.com"),
            MockRecord(source_url="http://example3.com"),
        ]
        result = list(deduplicate(records, DedupeStrategy.URL_ONLY))
        assert len(result) == 3

    def test_url_only_deduplication(self) -> None:
        """URL_ONLY removes records with same URL."""
        records = [
            MockRecord(source_url="http://example.com", sql_date="2024-01-01"),
            MockRecord(source_url="http://example.com", sql_date="2024-01-02"),
            MockRecord(source_url="http://other.com", sql_date="2024-01-01"),
        ]
        result = list(deduplicate(records, DedupeStrategy.URL_ONLY))
        assert len(result) == 2
        assert result[0].sql_date == "2024-01-01"  # First occurrence kept
        assert result[1].source_url == "http://other.com"

    def test_url_date_deduplication(self) -> None:
        """URL_DATE considers both URL and date."""
        records = [
            MockRecord(source_url="http://example.com", sql_date="2024-01-01"),
            MockRecord(source_url="http://example.com", sql_date="2024-01-01"),
            MockRecord(source_url="http://example.com", sql_date="2024-01-02"),
        ]
        result = list(deduplicate(records, DedupeStrategy.URL_DATE))
        assert len(result) == 2
        # Same URL+date removed, different date kept
        assert result[0].sql_date == "2024-01-01"
        assert result[1].sql_date == "2024-01-02"

    def test_url_date_location_deduplication(self) -> None:
        """URL_DATE_LOCATION considers URL, date, and location."""
        records = [
            MockRecord(
                source_url="http://example.com",
                sql_date="2024-01-01",
                action_geo_fullname="New York",
            ),
            MockRecord(
                source_url="http://example.com",
                sql_date="2024-01-01",
                action_geo_fullname="New York",
            ),
            MockRecord(
                source_url="http://example.com",
                sql_date="2024-01-01",
                action_geo_fullname="London",
            ),
        ]
        result = list(deduplicate(records, DedupeStrategy.URL_DATE_LOCATION))
        assert len(result) == 2
        assert result[0].action_geo_fullname == "New York"
        assert result[1].action_geo_fullname == "London"

    def test_url_date_location_actors_deduplication(self) -> None:
        """URL_DATE_LOCATION_ACTORS considers actors."""
        records = [
            MockRecord(
                source_url="http://example.com",
                sql_date="2024-01-01",
                action_geo_fullname="New York",
                actor1_code="USA",
                actor2_code="CHN",
            ),
            MockRecord(
                source_url="http://example.com",
                sql_date="2024-01-01",
                action_geo_fullname="New York",
                actor1_code="USA",
                actor2_code="CHN",
            ),
            MockRecord(
                source_url="http://example.com",
                sql_date="2024-01-01",
                action_geo_fullname="New York",
                actor1_code="USA",
                actor2_code="RUS",
            ),
        ]
        result = list(deduplicate(records, DedupeStrategy.URL_DATE_LOCATION_ACTORS))
        assert len(result) == 2
        assert result[0].actor2_code == "CHN"
        assert result[1].actor2_code == "RUS"

    def test_aggressive_deduplication(self) -> None:
        """AGGRESSIVE considers event_root_code as well."""
        records = [
            MockRecord(
                source_url="http://example.com",
                sql_date="2024-01-01",
                action_geo_fullname="New York",
                actor1_code="USA",
                actor2_code="CHN",
                event_root_code="14",
            ),
            MockRecord(
                source_url="http://example.com",
                sql_date="2024-01-01",
                action_geo_fullname="New York",
                actor1_code="USA",
                actor2_code="CHN",
                event_root_code="14",
            ),
            MockRecord(
                source_url="http://example.com",
                sql_date="2024-01-01",
                action_geo_fullname="New York",
                actor1_code="USA",
                actor2_code="CHN",
                event_root_code="15",
            ),
        ]
        result = list(deduplicate(records, DedupeStrategy.AGGRESSIVE))
        assert len(result) == 2
        assert result[0].event_root_code == "14"
        assert result[1].event_root_code == "15"

    def test_order_preserved(self) -> None:
        """First occurrence is kept, subsequent duplicates removed."""
        records = [
            MockRecord(source_url="http://a.com", sql_date="2024-01-01"),
            MockRecord(source_url="http://b.com", sql_date="2024-01-02"),
            MockRecord(source_url="http://a.com", sql_date="2024-01-03"),
            MockRecord(source_url="http://c.com", sql_date="2024-01-04"),
            MockRecord(source_url="http://b.com", sql_date="2024-01-05"),
        ]
        result = list(deduplicate(records, DedupeStrategy.URL_ONLY))
        assert len(result) == 3
        # First occurrences in order
        assert result[0].sql_date == "2024-01-01"  # a.com
        assert result[1].sql_date == "2024-01-02"  # b.com
        assert result[2].sql_date == "2024-01-04"  # c.com

    def test_none_values_handled(self) -> None:
        """None values don't cause errors and are deduplicated."""
        records = [
            MockRecord(source_url=None, sql_date=None),
            MockRecord(source_url=None, sql_date=None),
            MockRecord(source_url="http://example.com", sql_date=None),
        ]
        result = list(deduplicate(records, DedupeStrategy.URL_DATE))
        assert len(result) == 2
        # Two unique combinations: (None, None) and ("http://example.com", None)

    def test_generator_behavior(self) -> None:
        """Function returns an iterator, not a list."""
        records = [MockRecord(source_url="http://example.com")]
        result = deduplicate(records, DedupeStrategy.URL_ONLY)
        # Should be an iterator
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

    def test_large_dataset_memory_efficiency(self) -> None:
        """Generator doesn't consume all memory upfront."""

        # Create a large generator
        def record_generator():
            for i in range(1000):
                yield MockRecord(source_url=f"http://example{i % 100}.com")

        result = deduplicate(record_generator(), DedupeStrategy.URL_ONLY)
        # Take first 10, shouldn't process all 1000
        first_10 = list(zip(range(10), result))
        assert len(first_10) == 10

    def test_default_strategy(self) -> None:
        """Default strategy is URL_DATE_LOCATION."""
        records = [
            MockRecord(
                source_url="http://example.com",
                sql_date="2024-01-01",
                action_geo_fullname="New York",
            ),
            MockRecord(
                source_url="http://example.com",
                sql_date="2024-01-01",
                action_geo_fullname="New York",
            ),
        ]
        # Not passing strategy should use default
        result = list(deduplicate(records))
        assert len(result) == 1
