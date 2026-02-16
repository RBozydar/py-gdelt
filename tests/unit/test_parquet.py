"""Comprehensive tests for the py_gdelt.parquet module.

Tests cover:
- Schema construction and field validation
- Converter helper functions (_parse_date32, _parse_timestamp, _safe_int, etc.)
- Events, GKG, and Mentions converters (to Arrow RecordBatch)
- Writer (write_parquet, ExportResult)
- End-to-end (to_parquet from raw TSV bytes to Parquet file on disk)
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from py_gdelt.models._internal import _RawEvent, _RawGKG, _RawMention
from py_gdelt.parquet._converters import (
    _parse_date32,
    _parse_timestamp,
    _safe_bool,
    _safe_float,
    _safe_int,
    events_to_batch,
    gkg_to_batch,
    mentions_to_batch,
)
from py_gdelt.parquet._schemas import EVENTS_SCHEMA, GKG_SCHEMA, MENTIONS_SCHEMA
from py_gdelt.parquet._writer import ExportResult, to_parquet, write_parquet


if TYPE_CHECKING:
    from pathlib import Path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_raw_event(**overrides: object) -> _RawEvent:
    """Build a realistic ``_RawEvent`` with sensible defaults.

    All required fields are populated; optional fields default to ``None``.
    Keyword arguments override any field.
    """
    defaults: dict[str, object] = {
        "global_event_id": "123456789",
        "sql_date": "20240115",
        "month_year": "202401",
        "year": "2024",
        "fraction_date": "2024.0411",
        "is_root_event": "1",
        "event_code": "010",
        "event_base_code": "01",
        "event_root_code": "01",
        "quad_class": "1",
        "goldstein_scale": "-5.0",
        "num_mentions": "10",
        "num_sources": "5",
        "num_articles": "3",
        "avg_tone": "-1.5",
        "date_added": "20240115143000",
        "actor1_code": "USA",
        "actor1_name": "UNITED STATES",
        "is_translated": False,
    }
    defaults.update(overrides)
    return _RawEvent(**defaults)  # type: ignore[arg-type]


def _make_raw_gkg(**overrides: object) -> _RawGKG:
    """Build a realistic ``_RawGKG`` with sensible defaults."""
    defaults: dict[str, object] = {
        "gkg_record_id": "20240115143000-T12345",
        "date": "20240115143000",
        "source_collection_id": "1",
        "source_common_name": "nytimes.com",
        "document_identifier": "https://example.com/article",
        "counts_v1": "",
        "counts_v2": "",
        "themes_v1": "TAX_POLICY;ECON_DEBT",
        "themes_v2_enhanced": "TAX_POLICY,123;ECON_DEBT,456",
        "locations_v1": "",
        "locations_v2_enhanced": "",
        "persons_v1": "",
        "persons_v2_enhanced": "",
        "organizations_v1": "",
        "organizations_v2_enhanced": "",
        "tone": "1.5,-2.3,3.8,1.2,5.6,7.8,100",
        "dates_v2": "",
        "gcam": "",
        "is_translated": False,
    }
    defaults.update(overrides)
    return _RawGKG(**defaults)  # type: ignore[arg-type]


def _make_raw_mention(**overrides: object) -> _RawMention:
    """Build a realistic ``_RawMention`` with sensible defaults."""
    defaults: dict[str, object] = {
        "global_event_id": "123456789",
        "event_time_date": "20240115",
        "event_time_full": "20240115143000",
        "mention_time_date": "20240115",
        "mention_time_full": "20240115150000",
        "mention_type": "1",
        "mention_source_name": "nytimes.com",
        "mention_identifier": "https://example.com/article",
        "sentence_id": "3",
        "actor1_char_offset": "100",
        "actor2_char_offset": "200",
        "action_char_offset": "150",
        "in_raw_text": "1",
        "confidence": "80",
        "mention_doc_length": "5000",
        "mention_doc_tone": "-1.5",
    }
    defaults.update(overrides)
    return _RawMention(**defaults)  # type: ignore[arg-type]


# ===================================================================
# 1. Schema tests
# ===================================================================


class TestSchemas:
    """Validate schema field counts, names, types, and nullability."""

    # -- Field count --

    def test_events_schema_field_count(self) -> None:
        """EVENTS_SCHEMA has exactly as many fields as _RawEvent dataclass."""
        expected = len(dataclasses.fields(_RawEvent))
        assert len(EVENTS_SCHEMA) == expected == 62

    def test_gkg_schema_field_count(self) -> None:
        """GKG_SCHEMA has exactly as many fields as _RawGKG dataclass."""
        expected = len(dataclasses.fields(_RawGKG))
        assert len(GKG_SCHEMA) == expected == 28

    def test_mentions_schema_field_count(self) -> None:
        """MENTIONS_SCHEMA has exactly as many fields as _RawMention dataclass."""
        expected = len(dataclasses.fields(_RawMention))
        assert len(MENTIONS_SCHEMA) == expected == 18

    # -- Field names match dataclass --

    def test_events_schema_field_names_match_dataclass(self) -> None:
        """Schema field names correspond 1-to-1 with _RawEvent field names."""
        dc_names = [f.name for f in dataclasses.fields(_RawEvent)]
        schema_names = [f.name for f in EVENTS_SCHEMA]
        assert schema_names == dc_names

    def test_gkg_schema_field_names_match_dataclass(self) -> None:
        """Schema field names correspond 1-to-1 with _RawGKG field names."""
        dc_names = [f.name for f in dataclasses.fields(_RawGKG)]
        schema_names = [f.name for f in GKG_SCHEMA]
        assert schema_names == dc_names

    def test_mentions_schema_field_names_match_dataclass(self) -> None:
        """Schema field names correspond 1-to-1 with _RawMention field names."""
        dc_names = [f.name for f in dataclasses.fields(_RawMention)]
        schema_names = [f.name for f in MENTIONS_SCHEMA]
        assert schema_names == dc_names

    # -- Key type assertions: Events --

    def test_events_global_event_id_type(self) -> None:
        assert EVENTS_SCHEMA.field("global_event_id").type == pa.int64()

    def test_events_sql_date_type(self) -> None:
        assert EVENTS_SCHEMA.field("sql_date").type == pa.date32()

    def test_events_avg_tone_type(self) -> None:
        assert EVENTS_SCHEMA.field("avg_tone").type == pa.float64()

    def test_events_is_root_event_type(self) -> None:
        assert EVENTS_SCHEMA.field("is_root_event").type == pa.bool_()

    def test_events_date_added_type(self) -> None:
        assert EVENTS_SCHEMA.field("date_added").type == pa.timestamp("s", tz="UTC")

    def test_events_actor1_code_type(self) -> None:
        assert EVENTS_SCHEMA.field("actor1_code").type == pa.string()

    def test_events_is_translated_type(self) -> None:
        assert EVENTS_SCHEMA.field("is_translated").type == pa.bool_()

    def test_events_month_year_type(self) -> None:
        assert EVENTS_SCHEMA.field("month_year").type == pa.int32()

    def test_events_year_type(self) -> None:
        assert EVENTS_SCHEMA.field("year").type == pa.int16()

    def test_events_quad_class_type(self) -> None:
        assert EVENTS_SCHEMA.field("quad_class").type == pa.int8()

    def test_events_goldstein_scale_type(self) -> None:
        assert EVENTS_SCHEMA.field("goldstein_scale").type == pa.float64()

    def test_events_actor1_geo_lat_type(self) -> None:
        assert EVENTS_SCHEMA.field("actor1_geo_lat").type == pa.float64()

    # -- Key type assertions: GKG --

    def test_gkg_tone_type_is_string(self) -> None:
        """Tone is kept as a raw delimited string, NOT split."""
        assert GKG_SCHEMA.field("tone").type == pa.string()

    def test_gkg_date_type(self) -> None:
        assert GKG_SCHEMA.field("date").type == pa.timestamp("s", tz="UTC")

    def test_gkg_source_collection_id_type(self) -> None:
        assert GKG_SCHEMA.field("source_collection_id").type == pa.int8()

    def test_gkg_is_translated_type(self) -> None:
        assert GKG_SCHEMA.field("is_translated").type == pa.bool_()

    # -- Key type assertions: Mentions --

    def test_mentions_global_event_id_type(self) -> None:
        assert MENTIONS_SCHEMA.field("global_event_id").type == pa.int64()

    def test_mentions_mention_doc_tone_type(self) -> None:
        assert MENTIONS_SCHEMA.field("mention_doc_tone").type == pa.float64()

    def test_mentions_event_time_full_type(self) -> None:
        assert MENTIONS_SCHEMA.field("event_time_full").type == pa.timestamp("s", tz="UTC")

    def test_mentions_event_time_date_type(self) -> None:
        assert MENTIONS_SCHEMA.field("event_time_date").type == pa.date32()

    def test_mentions_mention_type_type(self) -> None:
        assert MENTIONS_SCHEMA.field("mention_type").type == pa.int8()

    def test_mentions_sentence_id_type(self) -> None:
        assert MENTIONS_SCHEMA.field("sentence_id").type == pa.int32()

    def test_mentions_confidence_type(self) -> None:
        assert MENTIONS_SCHEMA.field("confidence").type == pa.int32()

    # -- Nullability assertions --

    def test_events_global_event_id_not_nullable(self) -> None:
        """global_event_id is str (not str | None) so NOT nullable."""
        assert EVENTS_SCHEMA.field("global_event_id").nullable is False

    def test_events_actor1_code_is_nullable(self) -> None:
        """actor1_code is str | None so IS nullable."""
        assert EVENTS_SCHEMA.field("actor1_code").nullable is True

    def test_events_is_translated_not_nullable(self) -> None:
        """is_translated is bool (not bool | None) so NOT nullable."""
        assert EVENTS_SCHEMA.field("is_translated").nullable is False

    def test_events_event_code_not_nullable(self) -> None:
        """event_code is str (not str | None) so NOT nullable."""
        assert EVENTS_SCHEMA.field("event_code").nullable is False

    def test_events_source_url_is_nullable(self) -> None:
        """source_url is str | None so IS nullable."""
        assert EVENTS_SCHEMA.field("source_url").nullable is True

    def test_gkg_sharing_image_is_nullable(self) -> None:
        """sharing_image is str | None so IS nullable."""
        assert GKG_SCHEMA.field("sharing_image").nullable is True

    def test_gkg_gkg_record_id_not_nullable(self) -> None:
        """gkg_record_id is str so NOT nullable."""
        assert GKG_SCHEMA.field("gkg_record_id").nullable is False

    def test_mentions_extras_is_nullable(self) -> None:
        """extras is str | None so IS nullable."""
        assert MENTIONS_SCHEMA.field("extras").nullable is True

    def test_mentions_global_event_id_not_nullable(self) -> None:
        """global_event_id is str (not str | None) so NOT nullable."""
        assert MENTIONS_SCHEMA.field("global_event_id").nullable is False


# ===================================================================
# 2. Converter helper tests
# ===================================================================


class TestConverterHelpers:
    """Test the private parsing/conversion helpers in _converters."""

    # -- _parse_date32 --

    def test_parse_date32_valid(self) -> None:
        assert _parse_date32("20240115") == date(2024, 1, 15)

    def test_parse_date32_zeroes(self) -> None:
        """All-zeroes is an invalid date."""
        assert _parse_date32("00000000") is None

    def test_parse_date32_invalid_day(self) -> None:
        """Feb 30 does not exist."""
        assert _parse_date32("20230230") is None

    def test_parse_date32_empty(self) -> None:
        assert _parse_date32("") is None

    def test_parse_date32_too_short(self) -> None:
        assert _parse_date32("2024") is None

    def test_parse_date32_too_long(self) -> None:
        assert _parse_date32("202401150") is None

    # -- _parse_timestamp --

    def test_parse_timestamp_14_chars(self) -> None:
        result = _parse_timestamp("20240115143000")
        assert result == datetime(2024, 1, 15, 14, 30, 0, tzinfo=UTC)

    def test_parse_timestamp_8_chars_midnight(self) -> None:
        result = _parse_timestamp("20240115")
        assert result == datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC)

    def test_parse_timestamp_empty(self) -> None:
        assert _parse_timestamp("") is None

    def test_parse_timestamp_non_numeric(self) -> None:
        assert _parse_timestamp("abc") is None

    def test_parse_timestamp_wrong_length(self) -> None:
        """Lengths other than 8 or 14 return None."""
        assert _parse_timestamp("20240115143") is None

    def test_parse_timestamp_invalid_month(self) -> None:
        """Month 13 is invalid."""
        assert _parse_timestamp("20241315143000") is None

    # -- _safe_int --

    def test_safe_int_valid(self) -> None:
        assert _safe_int("42") == 42

    def test_safe_int_empty(self) -> None:
        assert _safe_int("") is None

    def test_safe_int_none(self) -> None:
        assert _safe_int(None) is None

    def test_safe_int_non_numeric(self) -> None:
        assert _safe_int("abc") is None

    def test_safe_int_negative(self) -> None:
        assert _safe_int("-7") == -7

    def test_safe_int_float_string(self) -> None:
        """Float strings are not valid integers."""
        assert _safe_int("3.14") is None

    # -- _safe_float --

    def test_safe_float_valid(self) -> None:
        assert _safe_float("3.14") == pytest.approx(3.14)

    def test_safe_float_empty(self) -> None:
        assert _safe_float("") is None

    def test_safe_float_none(self) -> None:
        assert _safe_float(None) is None

    def test_safe_float_non_numeric(self) -> None:
        assert _safe_float("abc") is None

    def test_safe_float_integer_string(self) -> None:
        assert _safe_float("42") == pytest.approx(42.0)

    def test_safe_float_negative(self) -> None:
        assert _safe_float("-1.5") == pytest.approx(-1.5)

    # -- _safe_bool --

    def test_safe_bool_one(self) -> None:
        assert _safe_bool("1") is True

    def test_safe_bool_zero(self) -> None:
        assert _safe_bool("0") is False

    def test_safe_bool_empty(self) -> None:
        assert _safe_bool("") is None

    def test_safe_bool_other_value(self) -> None:
        """Anything other than '1' or '0' returns None."""
        assert _safe_bool("2") is None


# ===================================================================
# 3. Events converter tests
# ===================================================================


class TestEventsConverter:
    """Test events_to_batch conversion from _RawEvent to Arrow RecordBatch."""

    def test_two_records(self) -> None:
        """Convert two events and verify shape and schema."""
        events = [
            _make_raw_event(global_event_id="100"),
            _make_raw_event(global_event_id="200", actor1_code=None, is_root_event="0"),
        ]
        batch = events_to_batch(events)

        assert batch.num_rows == 2
        assert batch.num_columns == 62
        assert batch.schema.equals(EVENTS_SCHEMA)

    def test_global_event_id_values(self) -> None:
        """global_event_id values are converted to int64."""
        events = [
            _make_raw_event(global_event_id="100"),
            _make_raw_event(global_event_id="200"),
        ]
        batch = events_to_batch(events)

        col = batch.column("global_event_id")
        assert col.type == pa.int64()
        assert col.to_pylist() == [100, 200]

    def test_sql_date_values(self) -> None:
        """sql_date values are date32."""
        events = [_make_raw_event(sql_date="20240115")]
        batch = events_to_batch(events)

        col = batch.column("sql_date")
        assert col.type == pa.date32()
        assert col.to_pylist() == [date(2024, 1, 15)]

    def test_is_root_event_conversion(self) -> None:
        """'1' is converted to True via _safe_bool."""
        events = [_make_raw_event(is_root_event="1")]
        batch = events_to_batch(events)
        assert batch.column("is_root_event").to_pylist() == [True]

    def test_is_root_event_zero(self) -> None:
        """'0' is converted to False via _safe_bool."""
        events = [_make_raw_event(is_root_event="0")]
        batch = events_to_batch(events)
        assert batch.column("is_root_event").to_pylist() == [False]

    def test_is_translated_passthrough(self) -> None:
        """is_translated (bool on dataclass) passes through directly."""
        events = [
            _make_raw_event(is_translated=True),
            _make_raw_event(is_translated=False),
        ]
        batch = events_to_batch(events)
        assert batch.column("is_translated").to_pylist() == [True, False]

    def test_nullable_string_preserved(self) -> None:
        """actor1_code nullable string is preserved; None stays null."""
        events = [
            _make_raw_event(actor1_code="USA"),
            _make_raw_event(actor1_code=None),
        ]
        batch = events_to_batch(events)
        assert batch.column("actor1_code").to_pylist() == ["USA", None]

    def test_empty_input(self) -> None:
        """Empty iterable produces 0-row batch with correct schema."""
        batch = events_to_batch([])
        assert batch.num_rows == 0
        assert batch.schema.equals(EVENTS_SCHEMA)

    def test_none_optional_columns_produce_nulls(self) -> None:
        """Optional fields set to None produce null Arrow values."""
        event = _make_raw_event(
            actor1_code=None,
            actor1_name=None,
            source_url=None,
            actor1_geo_type=None,
            actor1_geo_lat=None,
        )
        batch = events_to_batch([event])

        assert batch.column("actor1_code").to_pylist() == [None]
        assert batch.column("actor1_name").to_pylist() == [None]
        assert batch.column("source_url").to_pylist() == [None]
        assert batch.column("actor1_geo_type").to_pylist() == [None]
        assert batch.column("actor1_geo_lat").to_pylist() == [None]

    def test_date_added_timestamp(self) -> None:
        """date_added is parsed as UTC timestamp."""
        events = [_make_raw_event(date_added="20240115143000")]
        batch = events_to_batch(events)

        col = batch.column("date_added")
        assert col.type == pa.timestamp("s", tz="UTC")
        assert col.to_pylist() == [datetime(2024, 1, 15, 14, 30, 0, tzinfo=UTC)]

    def test_numeric_conversions(self) -> None:
        """Verify int and float conversions for numeric fields."""
        events = [
            _make_raw_event(
                num_mentions="10",
                num_sources="5",
                num_articles="3",
                avg_tone="-1.5",
                goldstein_scale="-5.0",
                quad_class="1",
            )
        ]
        batch = events_to_batch(events)

        assert batch.column("num_mentions").to_pylist() == [10]
        assert batch.column("num_sources").to_pylist() == [5]
        assert batch.column("num_articles").to_pylist() == [3]
        assert batch.column("avg_tone").to_pylist() == [pytest.approx(-1.5)]
        assert batch.column("goldstein_scale").to_pylist() == [pytest.approx(-5.0)]
        assert batch.column("quad_class").to_pylist() == [1]

    def test_geo_fields_conversion(self) -> None:
        """Geography lat/lon are float64 and type is int8."""
        events = [
            _make_raw_event(
                actor1_geo_type="3",
                actor1_geo_lat="38.8951",
                actor1_geo_lon="-77.0364",
            )
        ]
        batch = events_to_batch(events)

        assert batch.column("actor1_geo_type").to_pylist() == [3]
        assert batch.column("actor1_geo_lat").to_pylist() == [pytest.approx(38.8951)]
        assert batch.column("actor1_geo_lon").to_pylist() == [pytest.approx(-77.0364)]


# ===================================================================
# 4. GKG converter tests
# ===================================================================


class TestGKGConverter:
    """Test gkg_to_batch conversion from _RawGKG to Arrow RecordBatch."""

    def test_string_fields_preserved(self) -> None:
        """String fields like themes and tone are passed through."""
        records = [_make_raw_gkg()]
        batch = gkg_to_batch(records)

        assert batch.column("themes_v1").to_pylist() == ["TAX_POLICY;ECON_DEBT"]
        assert batch.column("tone").to_pylist() == ["1.5,-2.3,3.8,1.2,5.6,7.8,100"]
        assert batch.column("gkg_record_id").to_pylist() == ["20240115143000-T12345"]

    def test_date_parsed_as_timestamp(self) -> None:
        """date field is parsed to UTC timestamp."""
        records = [_make_raw_gkg(date="20240115143000")]
        batch = gkg_to_batch(records)

        col = batch.column("date")
        assert col.type == pa.timestamp("s", tz="UTC")
        assert col.to_pylist() == [datetime(2024, 1, 15, 14, 30, 0, tzinfo=UTC)]

    def test_source_collection_id_parsed_as_int(self) -> None:
        """source_collection_id is converted to int8."""
        records = [_make_raw_gkg(source_collection_id="1")]
        batch = gkg_to_batch(records)

        col = batch.column("source_collection_id")
        assert col.type == pa.int8()
        assert col.to_pylist() == [1]

    def test_is_translated_passthrough(self) -> None:
        """is_translated (bool) passes through directly."""
        records = [
            _make_raw_gkg(is_translated=True),
            _make_raw_gkg(is_translated=False),
        ]
        batch = gkg_to_batch(records)
        assert batch.column("is_translated").to_pylist() == [True, False]

    def test_empty_input(self) -> None:
        """Empty iterable produces 0-row batch with correct schema."""
        batch = gkg_to_batch([])
        assert batch.num_rows == 0
        assert batch.schema.equals(GKG_SCHEMA)

    def test_optional_fields_nullable(self) -> None:
        """Optional fields (sharing_image, etc.) become null when None."""
        record = _make_raw_gkg(sharing_image=None, related_images=None, quotations=None)
        batch = gkg_to_batch([record])

        assert batch.column("sharing_image").to_pylist() == [None]
        assert batch.column("related_images").to_pylist() == [None]
        assert batch.column("quotations").to_pylist() == [None]

    def test_batch_shape(self) -> None:
        """Two records produce batch with 2 rows and 28 columns."""
        records = [_make_raw_gkg(), _make_raw_gkg(gkg_record_id="20240115143000-T99999")]
        batch = gkg_to_batch(records)

        assert batch.num_rows == 2
        assert batch.num_columns == 28
        assert batch.schema.equals(GKG_SCHEMA)


# ===================================================================
# 5. Mentions converter tests
# ===================================================================


class TestMentionsConverter:
    """Test mentions_to_batch conversion from _RawMention to Arrow RecordBatch."""

    def test_global_event_id_int64(self) -> None:
        """global_event_id is converted to int64."""
        records = [_make_raw_mention(global_event_id="123456789")]
        batch = mentions_to_batch(records)

        col = batch.column("global_event_id")
        assert col.type == pa.int64()
        assert col.to_pylist() == [123456789]

    def test_mention_doc_tone_float64(self) -> None:
        """mention_doc_tone is converted to float64."""
        records = [_make_raw_mention(mention_doc_tone="-1.5")]
        batch = mentions_to_batch(records)

        col = batch.column("mention_doc_tone")
        assert col.type == pa.float64()
        assert col.to_pylist() == [pytest.approx(-1.5)]

    def test_event_time_full_timestamp(self) -> None:
        """event_time_full is parsed as UTC timestamp."""
        records = [_make_raw_mention(event_time_full="20240115143000")]
        batch = mentions_to_batch(records)

        col = batch.column("event_time_full")
        assert col.type == pa.timestamp("s", tz="UTC")
        assert col.to_pylist() == [datetime(2024, 1, 15, 14, 30, 0, tzinfo=UTC)]

    def test_event_time_date_date32(self) -> None:
        """event_time_date is parsed as date32."""
        records = [_make_raw_mention(event_time_date="20240115")]
        batch = mentions_to_batch(records)

        col = batch.column("event_time_date")
        assert col.type == pa.date32()
        assert col.to_pylist() == [date(2024, 1, 15)]

    def test_mention_time_full_timestamp(self) -> None:
        """mention_time_full is parsed as UTC timestamp."""
        records = [_make_raw_mention(mention_time_full="20240115150000")]
        batch = mentions_to_batch(records)

        col = batch.column("mention_time_full")
        assert col.to_pylist() == [datetime(2024, 1, 15, 15, 0, 0, tzinfo=UTC)]

    def test_integer_conversions(self) -> None:
        """Various int fields are correctly converted."""
        records = [
            _make_raw_mention(
                sentence_id="3",
                actor1_char_offset="100",
                actor2_char_offset="200",
                action_char_offset="150",
                confidence="80",
                mention_doc_length="5000",
                mention_type="1",
                in_raw_text="1",
            )
        ]
        batch = mentions_to_batch(records)

        assert batch.column("sentence_id").to_pylist() == [3]
        assert batch.column("actor1_char_offset").to_pylist() == [100]
        assert batch.column("actor2_char_offset").to_pylist() == [200]
        assert batch.column("action_char_offset").to_pylist() == [150]
        assert batch.column("confidence").to_pylist() == [80]
        assert batch.column("mention_doc_length").to_pylist() == [5000]
        assert batch.column("mention_type").to_pylist() == [1]
        assert batch.column("in_raw_text").to_pylist() == [1]

    def test_empty_input(self) -> None:
        """Empty iterable produces 0-row batch with correct schema."""
        batch = mentions_to_batch([])
        assert batch.num_rows == 0
        assert batch.schema.equals(MENTIONS_SCHEMA)

    def test_optional_fields_nullable(self) -> None:
        """Optional fields produce null when None."""
        record = _make_raw_mention(mention_doc_translation_info=None, extras=None)
        batch = mentions_to_batch([record])

        assert batch.column("mention_doc_translation_info").to_pylist() == [None]
        assert batch.column("extras").to_pylist() == [None]

    def test_batch_shape(self) -> None:
        """Two records produce batch with correct dimensions."""
        records = [
            _make_raw_mention(global_event_id="111"),
            _make_raw_mention(global_event_id="222"),
        ]
        batch = mentions_to_batch(records)

        assert batch.num_rows == 2
        assert batch.num_columns == 18
        assert batch.schema.equals(MENTIONS_SCHEMA)


# ===================================================================
# 6. Writer tests
# ===================================================================


class TestWriter:
    """Test write_parquet and ExportResult."""

    def test_write_and_read_back(self, tmp_path: Path) -> None:
        """write_parquet creates a valid Parquet file that can be read back."""
        events = [_make_raw_event(), _make_raw_event(global_event_id="999")]
        batch = events_to_batch(events)

        output = tmp_path / "events.parquet"
        result = write_parquet(batch, output)

        table = pq.read_table(output)
        assert table.num_rows == 2

        assert result.row_count == 2
        assert result.byte_count > 0
        assert result.output_path == output

    def test_export_result_attributes(self, tmp_path: Path) -> None:
        """ExportResult carries correct metadata."""
        batch = events_to_batch([_make_raw_event()])
        output = tmp_path / "test.parquet"

        result = write_parquet(batch, output)

        assert isinstance(result, ExportResult)
        assert result.row_count == 1
        assert result.byte_count > 0
        assert result.output_path == output

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """write_parquet creates intermediate parent directories."""
        batch = events_to_batch([_make_raw_event()])
        output = tmp_path / "nested" / "deep" / "events.parquet"

        result = write_parquet(batch, output)

        assert output.exists()
        assert result.row_count == 1

    def test_compression_none(self, tmp_path: Path) -> None:
        """write_parquet with compression='none' produces valid file."""
        batch = events_to_batch([_make_raw_event()])
        output = tmp_path / "uncompressed.parquet"

        result = write_parquet(batch, output, compression="none")

        table = pq.read_table(output)
        assert table.num_rows == 1
        assert result.byte_count > 0

    def test_table_input(self, tmp_path: Path) -> None:
        """write_parquet accepts pa.Table as well as RecordBatch."""
        batch = events_to_batch([_make_raw_event()])
        table = pa.Table.from_batches([batch])
        output = tmp_path / "from_table.parquet"

        result = write_parquet(table, output)

        assert result.row_count == 1
        read_back = pq.read_table(output)
        assert read_back.num_rows == 1

    def test_empty_batch(self, tmp_path: Path) -> None:
        """write_parquet with 0-row batch writes a valid (empty) Parquet file."""
        batch = events_to_batch([])
        output = tmp_path / "empty.parquet"

        result = write_parquet(batch, output)

        assert result.row_count == 0
        table = pq.read_table(output)
        assert table.num_rows == 0


# ===================================================================
# 7. End-to-end tests
# ===================================================================


class TestToParquet:
    """End-to-end: raw TSV bytes -> to_parquet() -> read Parquet back."""

    # -- Events --

    def test_events_end_to_end(self, tmp_path: Path) -> None:
        """Build raw events TSV bytes, export to Parquet, read back."""
        # Build a v2 events line with 61 tab-separated columns
        row = [""] * 61
        row[0] = "1234567890"  # GLOBALEVENTID
        row[1] = "20240115"  # SQLDATE
        row[2] = "202401"  # MonthYear
        row[3] = "2024"  # Year
        row[4] = "2024.0411"  # FractionDate
        row[5] = "USA"  # Actor1Code
        row[6] = "UNITED STATES"  # Actor1Name
        row[25] = "1"  # IsRootEvent
        row[26] = "010"  # EventCode
        row[27] = "01"  # EventBaseCode
        row[28] = "01"  # EventRootCode
        row[29] = "1"  # QuadClass
        row[30] = "-5.0"  # GoldsteinScale
        row[31] = "10"  # NumMentions
        row[32] = "5"  # NumSources
        row[33] = "3"  # NumArticles
        row[34] = "-1.5"  # AvgTone
        row[59] = "20240115143000"  # DATEADDED
        row[60] = "http://example.com/article"  # SOURCEURL

        tsv_bytes = "\t".join(row).encode("utf-8")
        output = tmp_path / "events.parquet"

        result = to_parquet(tsv_bytes, output, dataset="events")

        assert result.row_count == 1
        assert result.byte_count > 0
        assert result.output_path == output

        table = pq.read_table(output)
        assert table.num_rows == 1
        # Parquet may coerce timestamp precision (s -> ms), so compare
        # field names rather than strict schema equality.
        assert table.column_names == [f.name for f in EVENTS_SCHEMA]

        # Spot-check converted types
        assert table.column("global_event_id").to_pylist() == [1234567890]
        assert table.column("sql_date").to_pylist() == [date(2024, 1, 15)]
        assert table.column("is_root_event").to_pylist() == [True]
        assert table.column("avg_tone").to_pylist() == [pytest.approx(-1.5)]

    def test_events_multiple_rows(self, tmp_path: Path) -> None:
        """Multiple events rows export correctly."""
        rows_data: list[str] = []
        for i in range(3):
            row = [""] * 61
            row[0] = str(100 + i)
            row[1] = "20240115"
            row[2] = "202401"
            row[3] = "2024"
            row[4] = "2024.0411"
            row[25] = "1"
            row[26] = "010"
            row[27] = "01"
            row[28] = "01"
            row[29] = "1"
            row[30] = "0.0"
            row[31] = "1"
            row[32] = "1"
            row[33] = "1"
            row[34] = "0.0"
            row[59] = "20240115143000"
            row[60] = f"http://example.com/{i}"
            rows_data.append("\t".join(row))

        tsv_bytes = "\n".join(rows_data).encode("utf-8")
        output = tmp_path / "events_multi.parquet"

        result = to_parquet(tsv_bytes, output, dataset="events")

        assert result.row_count == 3
        table = pq.read_table(output)
        assert table.column("global_event_id").to_pylist() == [100, 101, 102]

    # -- GKG --

    def test_gkg_end_to_end(self, tmp_path: Path) -> None:
        """Build raw GKG TSV bytes, export to Parquet, read back."""
        # Build a v2.1 GKG line with 27 tab-separated columns
        # The GKG parser calls line.strip() which removes trailing tabs,
        # so the last column (V2ExtrasXML at index 26) must be non-empty
        # to preserve all 27 columns.
        row = [""] * 27
        row[0] = "20240115143000-T12345"  # GKGRECORDID
        row[1] = "20240115143000"  # DATE
        row[2] = "1"  # SourceCollectionIdentifier
        row[3] = "nytimes.com"  # SourceCommonName
        row[4] = "https://example.com/article"  # DocumentIdentifier
        row[7] = "TAX_POLICY;ECON_DEBT"  # V1Themes
        row[8] = "TAX_POLICY,123;ECON_DEBT,456"  # EnhancedThemes
        row[15] = "1.5,-2.3,3.8,1.2,5.6,7.8,100"  # V1.5Tone
        row[26] = (
            "<PAGE_PRECISEPUBTIMESTAMP>20240115143000</PAGE_PRECISEPUBTIMESTAMP>"  # V2ExtrasXML
        )

        tsv_bytes = "\t".join(row).encode("utf-8")
        output = tmp_path / "gkg.parquet"

        result = to_parquet(tsv_bytes, output, dataset="gkg")

        assert result.row_count == 1
        assert result.byte_count > 0

        table = pq.read_table(output)
        assert table.num_rows == 1
        assert table.column_names == [f.name for f in GKG_SCHEMA]

        # Spot-check values
        assert table.column("gkg_record_id").to_pylist() == ["20240115143000-T12345"]
        assert table.column("date").to_pylist() == [datetime(2024, 1, 15, 14, 30, 0, tzinfo=UTC)]
        assert table.column("source_collection_id").to_pylist() == [1]
        assert table.column("tone").to_pylist() == ["1.5,-2.3,3.8,1.2,5.6,7.8,100"]

    # -- Mentions --

    def test_mentions_end_to_end(self, tmp_path: Path) -> None:
        """Build raw mentions TSV bytes, export to Parquet, read back."""
        # Mentions v2: 16 tab-separated columns
        row = [
            "123456789",  # [0] GlobalEventID
            "20240115143000",  # [1] EventTimeDate (full timestamp)
            "20240115150000",  # [2] MentionTimeDate (full timestamp)
            "1",  # [3] MentionType
            "nytimes.com",  # [4] MentionSourceName
            "https://example.com/article",  # [5] MentionIdentifier
            "3",  # [6] SentenceID
            "100",  # [7] Actor1CharOffset
            "200",  # [8] Actor2CharOffset
            "150",  # [9] ActionCharOffset
            "1",  # [10] InRawText
            "80",  # [11] Confidence
            "5000",  # [12] MentionDocLen
            "-1.5",  # [13] MentionDocTone
            "",  # [14] MentionDocTranslationInfo
            "",  # [15] Extras
        ]
        tsv_bytes = "\t".join(row).encode("utf-8")
        output = tmp_path / "mentions.parquet"

        result = to_parquet(tsv_bytes, output, dataset="mentions")

        assert result.row_count == 1
        assert result.byte_count > 0

        table = pq.read_table(output)
        assert table.num_rows == 1
        assert table.column_names == [f.name for f in MENTIONS_SCHEMA]

        # Spot-check values
        assert table.column("global_event_id").to_pylist() == [123456789]
        assert table.column("mention_doc_tone").to_pylist() == [pytest.approx(-1.5)]
        assert table.column("event_time_full").to_pylist() == [
            datetime(2024, 1, 15, 14, 30, 0, tzinfo=UTC)
        ]
        assert table.column("confidence").to_pylist() == [80]

    def test_mentions_multiple_rows(self, tmp_path: Path) -> None:
        """Multiple mention rows export correctly."""
        rows_data: list[str] = []
        for i in range(2):
            row = [
                str(100 + i),  # GlobalEventID
                "20240115143000",
                "20240115150000",
                "1",
                "source.com",
                f"https://example.com/{i}",
                "3",
                "100",
                "200",
                "150",
                "1",
                "80",
                "5000",
                "-1.5",
                "",
                "",
            ]
            rows_data.append("\t".join(row))

        tsv_bytes = "\n".join(rows_data).encode("utf-8")
        output = tmp_path / "mentions_multi.parquet"

        result = to_parquet(tsv_bytes, output, dataset="mentions")

        assert result.row_count == 2
        table = pq.read_table(output)
        assert table.column("global_event_id").to_pylist() == [100, 101]

    # -- Translated flag --

    def test_events_is_translated_flag(self, tmp_path: Path) -> None:
        """is_translated flag propagates through to_parquet for events."""
        row = [""] * 61
        row[0] = "123"
        row[1] = "20240115"
        row[2] = "202401"
        row[3] = "2024"
        row[4] = "2024.0411"
        row[25] = "1"
        row[26] = "010"
        row[27] = "01"
        row[28] = "01"
        row[29] = "1"
        row[30] = "0.0"
        row[31] = "1"
        row[32] = "1"
        row[33] = "1"
        row[34] = "0.0"
        row[59] = "20240115143000"
        row[60] = "http://example.com"

        tsv_bytes = "\t".join(row).encode("utf-8")
        output = tmp_path / "translated.parquet"

        result = to_parquet(tsv_bytes, output, dataset="events", is_translated=True)

        table = pq.read_table(output)
        assert table.column("is_translated").to_pylist() == [True]
        assert result.row_count == 1
