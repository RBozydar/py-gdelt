"""Unit tests for GDELT Graph Datasets.

Tests cover:
- Pydantic model validation for all graph datasets
- Date parsing (GDELT format and ISO format)
- Parser functions (JSON-NL and TSV)
- Gzip decompression
- Filter validation
- Schema evolution warnings
"""

from __future__ import annotations

import gzip
import warnings
from datetime import date, datetime

import pytest
from pydantic import ValidationError

from py_gdelt.filters import (
    DateRange,
    GALFilter,
    GEGFilter,
    GEMGFilter,
    GFGFilter,
    GGGFilter,
    GQGFilter,
)
from py_gdelt.models._internal import _RawGFGRecord
from py_gdelt.models.graphs import (
    Entity,
    GALRecord,
    GEGRecord,
    GEMGRecord,
    GFGRecord,
    GGGRecord,
    GQGRecord,
    MetaTag,
    Quote,
    _warned_fields,
)
from py_gdelt.parsers.graphs import (
    parse_gal,
    parse_geg,
    parse_gemg,
    parse_gfg,
    parse_ggg,
    parse_gqg,
)


class TestGraphModels:
    """Tests for graph dataset Pydantic models."""

    def test_quote_model(self) -> None:
        """Test Quote model creation."""
        data = {"pre": "He said", "quote": "Hello world", "post": "to everyone"}
        quote = Quote.model_validate(data)
        assert quote.pre == "He said"
        assert quote.quote == "Hello world"
        assert quote.post == "to everyone"

    def test_gqg_record_from_dict(self) -> None:
        """Test GQGRecord creation from dict."""
        data = {
            "date": "20250120103000",
            "url": "https://example.com/article",
            "lang": "en",
            "quotes": [{"pre": "He said", "quote": "Hello world", "post": "to everyone"}],
        }
        record = GQGRecord.model_validate(data)
        assert record.url == "https://example.com/article"
        assert record.lang == "en"
        assert len(record.quotes) == 1
        assert record.quotes[0].quote == "Hello world"

    def test_gqg_record_date_parsing_gdelt_format(self) -> None:
        """Test GQGRecord parses GDELT date format."""
        data = {"date": "20250120103000", "url": "https://example.com", "lang": "en"}
        record = GQGRecord.model_validate(data)
        assert record.date.year == 2025
        assert record.date.month == 1
        assert record.date.day == 20
        assert record.date.hour == 10
        assert record.date.minute == 30
        assert record.date.second == 0

    def test_gqg_record_date_parsing_iso_format(self) -> None:
        """Test GQGRecord parses ISO date format."""
        data = {"date": "2025-01-20T10:30:00Z", "url": "https://example.com", "lang": "en"}
        record = GQGRecord.model_validate(data)
        assert record.date.year == 2025
        assert record.date.month == 1
        assert record.date.day == 20
        assert record.date.hour == 10
        assert record.date.minute == 30

    def test_gqg_record_date_parsing_invalid_format(self) -> None:
        """Test GQGRecord raises error on invalid date format."""
        data = {"date": "invalid-date", "url": "https://example.com", "lang": "en"}
        with pytest.raises(ValidationError):
            GQGRecord.model_validate(data)

    def test_gqg_record_empty_quotes_default(self) -> None:
        """Test GQGRecord defaults quotes to empty list."""
        data = {"date": "20250120103000", "url": "https://example.com", "lang": "en"}
        record = GQGRecord.model_validate(data)
        assert record.quotes == []

    def test_geg_record_with_entities(self) -> None:
        """Test GEGRecord with entities."""
        data = {
            "date": "20250120103000",
            "url": "https://example.com",
            "lang": "en",
            "entities": [{"name": "United Nations", "type": "ORGANIZATION", "salience": 0.8}],
        }
        record = GEGRecord.model_validate(data)
        assert len(record.entities) == 1
        assert record.entities[0].name == "United Nations"
        assert record.entities[0].entity_type == "ORGANIZATION"
        assert record.entities[0].salience == 0.8

    def test_entity_alias_fields(self) -> None:
        """Test Entity model field aliases."""
        # Test with alias 'type'
        data = {"name": "Test", "type": "PERSON", "mid": "/m/12345"}
        entity = Entity.model_validate(data)
        assert entity.entity_type == "PERSON"
        assert entity.knowledge_graph_mid == "/m/12345"

        # Test with actual field name 'entity_type'
        data2 = {"name": "Test", "entity_type": "LOCATION"}
        entity2 = Entity.model_validate(data2)
        assert entity2.entity_type == "LOCATION"

    def test_entity_optional_fields(self) -> None:
        """Test Entity model optional fields."""
        data = {"name": "Test", "type": "PERSON"}
        entity = Entity.model_validate(data)
        assert entity.salience is None
        assert entity.wikipedia_url is None
        assert entity.knowledge_graph_mid is None

    def test_gfg_record_from_raw(self) -> None:
        """Test GFGRecord.from_raw() conversion."""
        raw = _RawGFGRecord(
            date="20250120100000",
            from_frontpage_url="https://news.example.com",
            link_url="https://example.com/article",
            link_text="Breaking News",
            page_position="5",
            lang="en",
        )
        record = GFGRecord.from_raw(raw)
        assert record.from_frontpage_url == "https://news.example.com"
        assert record.link_url == "https://example.com/article"
        assert record.link_text == "Breaking News"
        assert record.page_position == 5
        assert record.lang == "en"
        assert record.date.hour == 10

    def test_gfg_record_empty_page_position(self) -> None:
        """Test GFGRecord handles empty page_position."""
        raw = _RawGFGRecord(
            date="20250120100000",
            from_frontpage_url="https://example.com",
            link_url="https://example.com/article",
            link_text="Test",
            page_position="",
            lang="en",
        )
        record = GFGRecord.from_raw(raw)
        assert record.page_position == 0

    def test_gfg_record_invalid_page_position(self) -> None:
        """Test GFGRecord handles invalid page_position string."""
        raw = _RawGFGRecord(
            date="20250120100000",
            from_frontpage_url="https://example.com",
            link_url="https://example.com/article",
            link_text="Test",
            page_position="invalid",
            lang="en",
        )
        record = GFGRecord.from_raw(raw)
        assert record.page_position == 0

    def test_ggg_record(self) -> None:
        """Test GGGRecord with coordinates."""
        data = {
            "date": "20250120103000",
            "url": "https://example.com",
            "location_name": "New York",
            "lat": 40.7128,
            "lon": -74.0060,
            "context": "Event in New York City",
        }
        record = GGGRecord.model_validate(data)
        assert record.location_name == "New York"
        assert record.lat == 40.7128
        assert record.lon == -74.0060
        assert record.context == "Event in New York City"

    def test_ggg_record_valid_coordinates(self) -> None:
        """Test GGGRecord accepts valid coordinates."""
        data = {
            "date": "20250120103000",
            "url": "https://example.com",
            "location_name": "Portland",
            "lat": 45.0,
            "lon": -122.0,
            "context": "Event in Portland",
        }
        record = GGGRecord.model_validate(data)
        assert record.lat == 45.0
        assert record.lon == -122.0

    def test_ggg_record_edge_case_coordinates(self) -> None:
        """Test GGGRecord accepts edge case coordinates (poles and date line)."""
        # North pole
        data_north = {
            "date": "20250120103000",
            "url": "https://example.com",
            "location_name": "North Pole",
            "lat": 90.0,
            "lon": 0.0,
            "context": "At the North Pole",
        }
        record_north = GGGRecord.model_validate(data_north)
        assert record_north.lat == 90.0

        # South pole
        data_south = {
            "date": "20250120103000",
            "url": "https://example.com",
            "location_name": "South Pole",
            "lat": -90.0,
            "lon": 0.0,
            "context": "At the South Pole",
        }
        record_south = GGGRecord.model_validate(data_south)
        assert record_south.lat == -90.0

        # Date line east
        data_east = {
            "date": "20250120103000",
            "url": "https://example.com",
            "location_name": "Date Line East",
            "lat": 0.0,
            "lon": 180.0,
            "context": "At the date line",
        }
        record_east = GGGRecord.model_validate(data_east)
        assert record_east.lon == 180.0

        # Date line west
        data_west = {
            "date": "20250120103000",
            "url": "https://example.com",
            "location_name": "Date Line West",
            "lat": 0.0,
            "lon": -180.0,
            "context": "At the date line",
        }
        record_west = GGGRecord.model_validate(data_west)
        assert record_west.lon == -180.0

    def test_ggg_record_invalid_latitude_too_high(self) -> None:
        """Test GGGRecord rejects latitude > 90."""
        data = {
            "date": "20250120103000",
            "url": "https://example.com",
            "location_name": "Invalid",
            "lat": 91.0,
            "lon": 0.0,
            "context": "Invalid latitude",
        }
        with pytest.raises(ValidationError, match="Latitude must be between -90 and 90"):
            GGGRecord.model_validate(data)

    def test_ggg_record_invalid_latitude_too_low(self) -> None:
        """Test GGGRecord rejects latitude < -90."""
        data = {
            "date": "20250120103000",
            "url": "https://example.com",
            "location_name": "Invalid",
            "lat": -91.0,
            "lon": 0.0,
            "context": "Invalid latitude",
        }
        with pytest.raises(ValidationError, match="Latitude must be between -90 and 90"):
            GGGRecord.model_validate(data)

    def test_ggg_record_invalid_longitude_too_high(self) -> None:
        """Test GGGRecord rejects longitude > 180."""
        data = {
            "date": "20250120103000",
            "url": "https://example.com",
            "location_name": "Invalid",
            "lat": 0.0,
            "lon": 181.0,
            "context": "Invalid longitude",
        }
        with pytest.raises(ValidationError, match="Longitude must be between -180 and 180"):
            GGGRecord.model_validate(data)

    def test_ggg_record_invalid_longitude_too_low(self) -> None:
        """Test GGGRecord rejects longitude < -180."""
        data = {
            "date": "20250120103000",
            "url": "https://example.com",
            "location_name": "Invalid",
            "lat": 0.0,
            "lon": -181.0,
            "context": "Invalid longitude",
        }
        with pytest.raises(ValidationError, match="Longitude must be between -180 and 180"):
            GGGRecord.model_validate(data)

    def test_metatag_model(self) -> None:
        """Test MetaTag model with type alias."""
        data = {"key": "og:title", "type": "property", "value": "Test Article"}
        metatag = MetaTag.model_validate(data)
        assert metatag.key == "og:title"
        assert metatag.tag_type == "property"
        assert metatag.value == "Test Article"

    def test_gemg_record_with_metatags(self) -> None:
        """Test GEMGRecord with metatags."""
        data = {
            "date": "20250120103000",
            "url": "https://example.com",
            "lang": "en",
            "metatags": [{"key": "og:title", "type": "property", "value": "Test Article"}],
            "jsonld": ['{"@type": "NewsArticle"}'],
        }
        record = GEMGRecord.model_validate(data)
        assert len(record.metatags) == 1
        assert record.metatags[0].tag_type == "property"
        assert len(record.jsonld) == 1

    def test_gemg_record_optional_title(self) -> None:
        """Test GEMGRecord with optional title."""
        data = {
            "date": "20250120103000",
            "url": "https://example.com",
            "lang": "en",
            "title": "Article Title",
        }
        record = GEMGRecord.model_validate(data)
        assert record.title == "Article Title"

    def test_gal_record(self) -> None:
        """Test GALRecord with optional fields."""
        data = {
            "date": "20250120103000",
            "url": "https://example.com",
            "lang": "en",
            "title": "Test Article",
            "author": "John Doe",
            "description": "Article description",
            "image": "https://example.com/image.jpg",
        }
        record = GALRecord.model_validate(data)
        assert record.title == "Test Article"
        assert record.author == "John Doe"
        assert record.description == "Article description"
        assert record.image == "https://example.com/image.jpg"

    def test_gal_record_optional_fields_none(self) -> None:
        """Test GALRecord with None optional fields."""
        data = {
            "date": "20250120103000",
            "url": "https://example.com",
            "lang": "en",
        }
        record = GALRecord.model_validate(data)
        assert record.title is None
        assert record.author is None
        assert record.description is None
        assert record.image is None

    def test_schema_evolution_mixin_warns_on_unknown_field(self) -> None:
        """Test SchemaEvolutionMixin warns about unknown fields."""
        # Clear warned fields cache
        _warned_fields.clear()

        data = {
            "date": "20250120103000",
            "url": "https://example.com",
            "lang": "en",
            "unknown_new_field": "some value",
        }

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            record = GQGRecord.model_validate(data)

            # Should have warning about unknown field
            assert len(w) == 1
            assert "schema change" in str(w[0].message).lower()
            assert "unknown_new_field" in str(w[0].message)
            assert record.url == "https://example.com"

    def test_schema_evolution_mixin_no_duplicate_warnings(self) -> None:
        """Test SchemaEvolutionMixin doesn't warn twice for same field."""
        _warned_fields.clear()

        data = {
            "date": "20250120103000",
            "url": "https://example.com",
            "lang": "en",
            "new_field": "value",
        }

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            GQGRecord.model_validate(data)
            GQGRecord.model_validate(data)  # Second time

            # Should only have 1 warning, not 2
            schema_warnings = [x for x in w if "schema change" in str(x.message).lower()]
            assert len(schema_warnings) == 1

    def test_schema_evolution_different_models_separate_warnings(self) -> None:
        """Test that different models can have separate warnings for same field name."""
        _warned_fields.clear()

        data1 = {
            "date": "20250120103000",
            "url": "https://example.com",
            "lang": "en",
            "new_field": "value",
        }

        data2 = {
            "date": "20250120103000",
            "url": "https://example.com",
            "lang": "en",
            "new_field": "value",
        }

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            GQGRecord.model_validate(data1)
            GALRecord.model_validate(data2)

            # Should have 2 warnings (one for each model)
            schema_warnings = [x for x in w if "schema change" in str(x.message).lower()]
            assert len(schema_warnings) == 2


class TestGraphParsers:
    """Tests for graph dataset parser functions."""

    def test_parse_gqg_valid_jsonl(self) -> None:
        """Test parse_gqg with valid JSON-NL."""
        data = b'{"date": "20250120103000", "url": "https://example.com", "lang": "en", "quotes": []}\n'
        records = list(parse_gqg(data))
        assert len(records) == 1
        assert records[0].url == "https://example.com"

    def test_parse_gqg_multiple_lines(self) -> None:
        """Test parse_gqg with multiple JSON-NL lines."""
        data = b'{"date": "20250120103000", "url": "https://example.com", "lang": "en"}\n{"date": "20250120103000", "url": "https://example2.com", "lang": "es"}\n'
        records = list(parse_gqg(data))
        assert len(records) == 2
        assert records[0].url == "https://example.com"
        assert records[1].url == "https://example2.com"

    def test_parse_gqg_gzipped(self) -> None:
        """Test parse_gqg handles gzipped data."""
        raw = b'{"date": "20250120103000", "url": "https://example.com", "lang": "en"}\n'
        data = gzip.compress(raw)
        records = list(parse_gqg(data))
        assert len(records) == 1
        assert records[0].url == "https://example.com"

    def test_parse_gqg_skips_malformed_lines(self) -> None:
        """Test parse_gqg skips malformed JSON lines."""
        data = b'{"date": "20250120103000", "url": "https://example.com", "lang": "en"}\n{invalid json\n{"date": "20250120103000", "url": "https://example2.com", "lang": "en"}\n'
        records = list(parse_gqg(data))
        assert len(records) == 2  # Skipped the malformed line

    def test_parse_gqg_skips_empty_lines(self) -> None:
        """Test parse_gqg skips empty lines."""
        data = b'{"date": "20250120103000", "url": "https://example.com", "lang": "en"}\n\n\n{"date": "20250120103000", "url": "https://example2.com", "lang": "en"}\n'
        records = list(parse_gqg(data))
        assert len(records) == 2

    def test_parse_gqg_empty_input(self) -> None:
        """Test parse_gqg with empty input."""
        records = list(parse_gqg(b""))
        assert len(records) == 0

    def test_parse_gqg_whitespace_only(self) -> None:
        """Test parse_gqg with whitespace-only input."""
        records = list(parse_gqg(b"   \n  \n  "))
        assert len(records) == 0

    def test_parse_gfg_valid_tsv(self) -> None:
        """Test parse_gfg with valid TSV data."""
        data = b"20250120100000\thttps://news.com\thttps://article.com\tHeadline\t1\ten\n"
        records = list(parse_gfg(data))
        assert len(records) == 1
        assert records[0].from_frontpage_url == "https://news.com"
        assert records[0].link_url == "https://article.com"
        assert records[0].link_text == "Headline"
        assert records[0].page_position == 1
        assert records[0].lang == "en"

    def test_parse_gfg_multiple_rows(self) -> None:
        """Test parse_gfg with multiple TSV rows."""
        data = b"20250120100000\thttps://news.com\thttps://article1.com\tHeadline 1\t1\ten\n20250120110000\thttps://news.com\thttps://article2.com\tHeadline 2\t2\tes\n"
        records = list(parse_gfg(data))
        assert len(records) == 2
        assert records[0].link_text == "Headline 1"
        assert records[1].link_text == "Headline 2"

    def test_parse_gfg_skips_incomplete_rows(self) -> None:
        """Test parse_gfg skips rows with insufficient columns."""
        data = b"20250120100000\thttps://news.com\thttps://article.com\n"  # Only 3 columns
        records = list(parse_gfg(data))
        assert len(records) == 0

    def test_parse_gfg_skips_empty_rows(self) -> None:
        """Test parse_gfg skips empty rows."""
        data = b"\n\n20250120100000\thttps://news.com\thttps://article.com\tHeadline\t1\ten\n\n"
        records = list(parse_gfg(data))
        assert len(records) == 1

    def test_parse_gfg_gzipped(self) -> None:
        """Test parse_gfg handles gzipped data."""
        raw = b"20250120100000\thttps://news.com\thttps://article.com\tHeadline\t1\ten\n"
        data = gzip.compress(raw)
        records = list(parse_gfg(data))
        assert len(records) == 1
        assert records[0].link_text == "Headline"

    def test_parse_gfg_empty_page_position(self) -> None:
        """Test parse_gfg handles empty page_position field."""
        data = b"20250120100000\thttps://news.com\thttps://article.com\tHeadline\t\ten\n"
        records = list(parse_gfg(data))
        assert len(records) == 1
        assert records[0].page_position == 0

    def test_parse_geg_valid(self) -> None:
        """Test parse_geg with valid data."""
        data = b'{"date": "20250120103000", "url": "https://example.com", "lang": "en", "entities": []}\n'
        records = list(parse_geg(data))
        assert len(records) == 1
        assert records[0].url == "https://example.com"

    def test_parse_geg_with_entities(self) -> None:
        """Test parse_geg with entities."""
        data = b'{"date": "20250120103000", "url": "https://example.com", "lang": "en", "entities": [{"name": "Test", "type": "PERSON"}]}\n'
        records = list(parse_geg(data))
        assert len(records) == 1
        assert len(records[0].entities) == 1

    def test_parse_ggg_valid(self) -> None:
        """Test parse_ggg with valid data."""
        data = b'{"date": "20250120103000", "url": "https://example.com", "location_name": "NYC", "lat": 40.7, "lon": -74.0, "context": "test"}\n'
        records = list(parse_ggg(data))
        assert len(records) == 1
        assert records[0].location_name == "NYC"
        assert records[0].lat == 40.7
        assert records[0].lon == -74.0

    def test_parse_gemg_valid(self) -> None:
        """Test parse_gemg with valid data."""
        data = b'{"date": "20250120103000", "url": "https://example.com", "lang": "en", "metatags": [], "jsonld": []}\n'
        records = list(parse_gemg(data))
        assert len(records) == 1
        assert records[0].url == "https://example.com"

    def test_parse_gemg_with_metatags(self) -> None:
        """Test parse_gemg with metatags."""
        data = b'{"date": "20250120103000", "url": "https://example.com", "lang": "en", "metatags": [{"key": "og:title", "type": "property", "value": "Test"}]}\n'
        records = list(parse_gemg(data))
        assert len(records) == 1
        assert len(records[0].metatags) == 1

    def test_parse_gal_valid(self) -> None:
        """Test parse_gal with valid data."""
        data = b'{"date": "20250120103000", "url": "https://example.com", "lang": "en"}\n'
        records = list(parse_gal(data))
        assert len(records) == 1
        assert records[0].url == "https://example.com"

    def test_parse_gal_with_optional_fields(self) -> None:
        """Test parse_gal with all optional fields."""
        data = b'{"date": "20250120103000", "url": "https://example.com", "lang": "en", "title": "Test", "author": "John Doe", "description": "Desc", "image": "https://example.com/img.jpg"}\n'
        records = list(parse_gal(data))
        assert len(records) == 1
        assert records[0].title == "Test"
        assert records[0].author == "John Doe"


class TestGraphFilters:
    """Tests for graph dataset filters."""

    def test_gqg_filter_valid(self) -> None:
        """Test GQGFilter with valid date range."""
        filter_obj = GQGFilter(date_range=DateRange(start=date(2025, 1, 20)))
        assert filter_obj.date_range.start == date(2025, 1, 20)
        assert filter_obj.date_range.days == 1

    def test_gqg_filter_with_languages(self) -> None:
        """Test GQGFilter with language list."""
        filter_obj = GQGFilter(
            date_range=DateRange(start=date(2025, 1, 20)),
            languages=["en", "es"],
        )
        assert filter_obj.languages == ["en", "es"]

    def test_gqg_filter_accepts_large_date_range(self) -> None:
        """Test GQGFilter accepts large date ranges (file-based, no limit)."""
        filter_obj = GQGFilter(date_range=DateRange(start=date(2024, 1, 1), end=date(2025, 1, 1)))
        assert filter_obj.date_range.days > 365  # Inclusive, so > 365

    def test_geg_filter_accepts_large_date_range(self) -> None:
        """Test GEGFilter accepts large date ranges (file-based, no limit)."""
        filter_obj = GEGFilter(date_range=DateRange(start=date(2024, 1, 1), end=date(2025, 1, 1)))
        assert filter_obj.date_range.days > 365

    def test_gfg_filter_accepts_large_date_range(self) -> None:
        """Test GFGFilter accepts large date ranges (file-based, no limit)."""
        filter_obj = GFGFilter(date_range=DateRange(start=date(2024, 1, 1), end=date(2025, 1, 1)))
        assert filter_obj.date_range.days > 365

    def test_ggg_filter_accepts_large_date_range(self) -> None:
        """Test GGGFilter accepts large date ranges (file-based, no limit)."""
        filter_obj = GGGFilter(date_range=DateRange(start=date(2024, 1, 1), end=date(2025, 1, 1)))
        assert filter_obj.date_range.days > 365

    def test_gemg_filter_accepts_large_date_range(self) -> None:
        """Test GEMGFilter accepts large date ranges (file-based, no limit)."""
        filter_obj = GEMGFilter(date_range=DateRange(start=date(2024, 1, 1), end=date(2025, 1, 1)))
        assert filter_obj.date_range.days > 365

    def test_gal_filter_accepts_large_date_range(self) -> None:
        """Test GALFilter accepts large date ranges (file-based, no limit)."""
        filter_obj = GALFilter(date_range=DateRange(start=date(2024, 1, 1), end=date(2025, 1, 1)))
        assert filter_obj.date_range.days > 365

    def test_filter_with_languages(self) -> None:
        """Test filter with language list."""
        filter_obj = GQGFilter(
            date_range=DateRange(start=date(2025, 1, 20)),
            languages=["en", "es", "fr"],
        )
        assert filter_obj.languages == ["en", "es", "fr"]

    def test_filter_languages_none(self) -> None:
        """Test filter with languages=None."""
        filter_obj = GQGFilter(date_range=DateRange(start=date(2025, 1, 20)))
        assert filter_obj.languages is None


class TestDateParsing:
    """Tests for date parsing across all graph models."""

    def test_datetime_object_passthrough(self) -> None:
        """Test that datetime objects are converted to UTC."""
        dt = datetime(2025, 1, 20, 10, 30, 0)
        data = {"date": dt, "url": "https://example.com", "lang": "en"}
        record = GQGRecord.model_validate(data)
        # Naive datetimes are converted to UTC by parse_gdelt_datetime
        assert record.date.year == dt.year
        assert record.date.month == dt.month
        assert record.date.day == dt.day
        assert record.date.hour == dt.hour
        assert record.date.minute == dt.minute
        assert record.date.tzinfo is not None  # Now UTC-aware

    def test_iso_format_with_z_suffix(self) -> None:
        """Test ISO format with Z timezone suffix."""
        data = {"date": "2025-01-20T10:30:00Z", "url": "https://example.com", "lang": "en"}
        record = GQGRecord.model_validate(data)
        assert record.date.year == 2025
        assert record.date.hour == 10

    def test_iso_format_with_offset(self) -> None:
        """Test ISO format with timezone offset."""
        data = {
            "date": "2025-01-20T10:30:00+00:00",
            "url": "https://example.com",
            "lang": "en",
        }
        record = GQGRecord.model_validate(data)
        assert record.date.year == 2025
        assert record.date.hour == 10

    def test_gdelt_format_complete(self) -> None:
        """Test complete GDELT date format (YYYYMMDDHHMMSS)."""
        data = {"date": "20250120153045", "url": "https://example.com", "lang": "en"}
        record = GQGRecord.model_validate(data)
        assert record.date.year == 2025
        assert record.date.month == 1
        assert record.date.day == 20
        assert record.date.hour == 15
        assert record.date.minute == 30
        assert record.date.second == 45

    def test_all_models_support_both_date_formats(self) -> None:
        """Test that all graph models support both GDELT and ISO date formats."""
        gdelt_date = "20250120103000"
        iso_date = "2025-01-20T10:30:00Z"

        # Test all models with GDELT format
        gqg = GQGRecord.model_validate(
            {"date": gdelt_date, "url": "https://example.com", "lang": "en"}
        )
        assert gqg.date.year == 2025

        geg = GEGRecord.model_validate(
            {"date": gdelt_date, "url": "https://example.com", "lang": "en"}
        )
        assert geg.date.year == 2025

        ggg = GGGRecord.model_validate(
            {
                "date": gdelt_date,
                "url": "https://example.com",
                "location_name": "NYC",
                "lat": 40.7,
                "lon": -74.0,
                "context": "test",
            }
        )
        assert ggg.date.year == 2025

        gemg = GEMGRecord.model_validate(
            {"date": gdelt_date, "url": "https://example.com", "lang": "en"}
        )
        assert gemg.date.year == 2025

        gal = GALRecord.model_validate(
            {"date": gdelt_date, "url": "https://example.com", "lang": "en"}
        )
        assert gal.date.year == 2025

        # Test all models with ISO format
        gqg_iso = GQGRecord.model_validate(
            {"date": iso_date, "url": "https://example.com", "lang": "en"}
        )
        assert gqg_iso.date.year == 2025

        geg_iso = GEGRecord.model_validate(
            {"date": iso_date, "url": "https://example.com", "lang": "en"}
        )
        assert geg_iso.date.year == 2025


class TestThreadSafety:
    """Tests for thread-safety of schema evolution warnings."""

    def test_concurrent_schema_warnings_thread_safe(self) -> None:
        """Test that concurrent validation with unknown fields is thread-safe."""
        import concurrent.futures

        _warned_fields.clear()

        # Create test data with unknown fields
        def validate_with_unknown_field(thread_id: int) -> None:
            """Validate a record with an unknown field in a thread."""
            data = {
                "date": "20250120103000",
                "url": f"https://example{thread_id}.com",
                "lang": "en",
                "unknown_field_thread_test": f"value_{thread_id}",
            }
            # Suppress warnings in this test
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                GQGRecord.model_validate(data)

        # Run validations concurrently in multiple threads
        num_threads = 20
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(validate_with_unknown_field, i) for i in range(num_threads)]
            # Wait for all threads to complete
            concurrent.futures.wait(futures)

        # Verify that the warning was only registered once despite concurrent access
        # The key should be ("GQGRecord", "unknown_field_thread_test")
        assert ("GQGRecord", "unknown_field_thread_test") in _warned_fields
        # Verify the set has exactly one entry for this field
        matching_keys = [
            k for k in _warned_fields if k == ("GQGRecord", "unknown_field_thread_test")
        ]
        assert len(matching_keys) == 1

    def test_concurrent_different_fields_thread_safe(self) -> None:
        """Test concurrent validation with different unknown fields is thread-safe."""
        import concurrent.futures

        _warned_fields.clear()

        def validate_with_unique_field(field_num: int) -> None:
            """Validate a record with a unique unknown field."""
            data = {
                "date": "20250120103000",
                "url": "https://example.com",
                "lang": "en",
                f"unknown_field_{field_num}": f"value_{field_num}",
            }
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                GQGRecord.model_validate(data)

        # Run validations with different unknown fields concurrently
        num_fields = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_fields) as executor:
            futures = [executor.submit(validate_with_unique_field, i) for i in range(num_fields)]
            concurrent.futures.wait(futures)

        # Verify all unique fields were registered exactly once
        for i in range(num_fields):
            assert ("GQGRecord", f"unknown_field_{i}") in _warned_fields

        # Verify we have exactly num_fields warnings
        gqg_warnings = [k for k in _warned_fields if k[0] == "GQGRecord"]
        assert len(gqg_warnings) == num_fields
