"""Tests for optional-free BigQuery row conversion helpers."""

from __future__ import annotations

from dataclasses import MISSING, fields
from datetime import UTC, datetime
from typing import Any

from py_gdelt.models._internal import _RawEvent, _RawGKG, _RawMention
from py_gdelt.models.events import Mention
from py_gdelt.sources._bigquery_rows import (
    _BQ_EVENT_MAP,
    _BQ_GKG_MAP,
    _BQ_MENTION_MAP,
    _RAW_EVENT_REQUIRED,
    _RAW_GKG_REQUIRED,
    _RAW_MENTION_REQUIRED,
    _bq_row_to_raw_mention,
)


def _required_dataclass_fields(raw_model: type[Any]) -> frozenset[str]:
    """Return dataclass fields without defaults."""
    return frozenset(
        field.name
        for field in fields(raw_model)
        if field.default is MISSING and field.default_factory is MISSING
    )


def test_required_bigquery_fields_match_raw_dataclass_fields() -> None:
    """Required BigQuery fallback fields stay aligned with raw dataclasses."""
    assert _required_dataclass_fields(_RawEvent) == _RAW_EVENT_REQUIRED
    assert _required_dataclass_fields(_RawGKG) == _RAW_GKG_REQUIRED
    assert _required_dataclass_fields(_RawMention) == _RAW_MENTION_REQUIRED


def test_bigquery_maps_cover_required_raw_fields() -> None:
    """Every required raw field is sourced from BigQuery or synthesized."""
    synthesized_mention_fields = frozenset({"event_time_full", "mention_time_full"})

    assert frozenset(_BQ_EVENT_MAP.values()) >= _RAW_EVENT_REQUIRED
    assert frozenset(_BQ_GKG_MAP.values()) >= _RAW_GKG_REQUIRED
    assert frozenset(_BQ_MENTION_MAP.values()) | synthesized_mention_fields >= _RAW_MENTION_REQUIRED


def test_bigquery_mention_row_preserves_full_timestamps_for_public_model() -> None:
    """BigQuery mention rows keep parseable full event and mention timestamps."""
    raw = _bq_row_to_raw_mention(
        {
            "GLOBALEVENTID": "123",
            "EventTimeDate": "20240104120000",
            "MentionTimeDate": "20240104121530",
            "MentionType": "1",
            "MentionSourceName": "BBC",
            "MentionIdentifier": "https://example.com/story",
            "SentenceID": "5",
            "Actor1CharOffset": "10",
            "Actor2CharOffset": "20",
            "ActionCharOffset": "30",
            "InRawText": "1",
            "Confidence": "95",
            "MentionDocLen": "1000",
            "MentionDocTone": "-1.5",
        },
    )

    assert raw.event_time_full == "20240104120000"
    assert raw.mention_time_full == "20240104121530"

    mention = Mention.from_raw(raw)
    assert mention.event_time == datetime(2024, 1, 4, 12, 0, 0, tzinfo=UTC)
    assert mention.mention_time == datetime(2024, 1, 4, 12, 15, 30, tzinfo=UTC)
