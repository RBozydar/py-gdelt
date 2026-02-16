"""Column-wise conversion from ``_Raw*`` dataclasses to Arrow RecordBatches.

Each public converter materialises an ``Iterable`` of raw dataclass records
into a single ``pa.RecordBatch`` by iterating the records once and building
one Python list per column.  This column-wise approach is substantially
faster than ``pa.Table.from_pylist()`` because it avoids per-row dict
overhead and lets Arrow do a single bulk conversion per column.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

import pyarrow as pa

from py_gdelt.parquet._schemas import EVENTS_SCHEMA, GKG_SCHEMA, MENTIONS_SCHEMA


if TYPE_CHECKING:
    from collections.abc import Iterable

    from py_gdelt.models._internal import _RawEvent, _RawGKG, _RawMention


__all__ = [
    "events_to_batch",
    "gkg_to_batch",
    "mentions_to_batch",
]


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _parse_date32(val: str) -> date | None:
    """Parse a ``YYYYMMDD`` string into a :class:`datetime.date`.

    Args:
        val: Date string in ``YYYYMMDD`` format.

    Returns:
        Parsed date or ``None`` for malformed / zero-padded dates.
    """
    if not val or len(val) != 8:
        return None
    try:
        return date(int(val[:4]), int(val[4:6]), int(val[6:8]))
    except ValueError:
        return None


def _parse_timestamp(val: str) -> datetime | None:
    """Parse ``YYYYMMDDHHMMSS`` (14 chars) or ``YYYYMMDD`` (8 chars) into a UTC datetime.

    Args:
        val: Timestamp string in either 8- or 14-character format.

    Returns:
        Parsed UTC datetime or ``None`` for empty / malformed strings.
    """
    if not val:
        return None
    try:
        if len(val) == 14:
            return datetime(
                int(val[:4]),
                int(val[4:6]),
                int(val[6:8]),
                int(val[8:10]),
                int(val[10:12]),
                int(val[12:14]),
                tzinfo=UTC,
            )
        if len(val) == 8:
            return datetime(
                int(val[:4]),
                int(val[4:6]),
                int(val[6:8]),
                tzinfo=UTC,
            )
    except ValueError:
        return None
    return None


def _safe_int(val: str | None) -> int | None:
    """Convert a string to ``int``, returning ``None`` for empty / malformed values.

    Args:
        val: Numeric string or ``None``.

    Returns:
        Parsed integer or ``None``.
    """
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        return None


def _safe_float(val: str | None) -> float | None:
    """Convert a string to ``float``, returning ``None`` for empty / malformed values.

    Args:
        val: Numeric string or ``None``.

    Returns:
        Parsed float or ``None``.
    """
    if not val:
        return None
    try:
        return float(val)
    except ValueError:
        return None


def _safe_bool(val: str) -> bool | None:
    """Convert ``"1"`` / ``"0"`` to ``bool``, returning ``None`` for empty strings.

    Using ``bool(val)`` directly is incorrect because ``bool("0")`` is
    ``True`` in Python.

    Args:
        val: A string expected to be ``"1"`` or ``"0"``.

    Returns:
        ``True``, ``False``, or ``None``.
    """
    if val == "1":
        return True
    if val == "0":
        return False
    return None


# ---------------------------------------------------------------------------
# Events converter
# ---------------------------------------------------------------------------


def _append_event_core(columns: dict[str, list[object]], r: _RawEvent) -> None:
    """Append core (non-geography) fields for a single event.

    Args:
        columns: Mutable dict of field name to value lists.
        r: A raw event record.
    """
    columns["global_event_id"].append(_safe_int(r.global_event_id))
    columns["sql_date"].append(_parse_date32(r.sql_date))
    columns["month_year"].append(_safe_int(r.month_year))
    columns["year"].append(_safe_int(r.year))
    columns["fraction_date"].append(_safe_float(r.fraction_date))

    columns["is_root_event"].append(_safe_bool(r.is_root_event))
    columns["event_code"].append(r.event_code)
    columns["event_base_code"].append(r.event_base_code)
    columns["event_root_code"].append(r.event_root_code)
    columns["quad_class"].append(_safe_int(r.quad_class))
    columns["goldstein_scale"].append(_safe_float(r.goldstein_scale))
    columns["num_mentions"].append(_safe_int(r.num_mentions))
    columns["num_sources"].append(_safe_int(r.num_sources))
    columns["num_articles"].append(_safe_int(r.num_articles))
    columns["avg_tone"].append(_safe_float(r.avg_tone))

    columns["date_added"].append(_parse_timestamp(r.date_added))

    columns["actor1_code"].append(r.actor1_code)
    columns["actor1_name"].append(r.actor1_name)
    columns["actor1_country_code"].append(r.actor1_country_code)
    columns["actor1_known_group_code"].append(r.actor1_known_group_code)
    columns["actor1_ethnic_code"].append(r.actor1_ethnic_code)
    columns["actor1_religion1_code"].append(r.actor1_religion1_code)
    columns["actor1_religion2_code"].append(r.actor1_religion2_code)
    columns["actor1_type1_code"].append(r.actor1_type1_code)
    columns["actor1_type2_code"].append(r.actor1_type2_code)
    columns["actor1_type3_code"].append(r.actor1_type3_code)

    columns["actor2_code"].append(r.actor2_code)
    columns["actor2_name"].append(r.actor2_name)
    columns["actor2_country_code"].append(r.actor2_country_code)
    columns["actor2_known_group_code"].append(r.actor2_known_group_code)
    columns["actor2_ethnic_code"].append(r.actor2_ethnic_code)
    columns["actor2_religion1_code"].append(r.actor2_religion1_code)
    columns["actor2_religion2_code"].append(r.actor2_religion2_code)
    columns["actor2_type1_code"].append(r.actor2_type1_code)
    columns["actor2_type2_code"].append(r.actor2_type2_code)
    columns["actor2_type3_code"].append(r.actor2_type3_code)

    columns["source_url"].append(r.source_url)
    columns["is_translated"].append(r.is_translated)


def _append_event_geo(columns: dict[str, list[object]], r: _RawEvent) -> None:
    """Append geography fields for a single event.

    Args:
        columns: Mutable dict of field name to value lists.
        r: A raw event record.
    """
    columns["actor1_geo_type"].append(_safe_int(r.actor1_geo_type))
    columns["actor1_geo_fullname"].append(r.actor1_geo_fullname)
    columns["actor1_geo_country_code"].append(r.actor1_geo_country_code)
    columns["actor1_geo_adm1_code"].append(r.actor1_geo_adm1_code)
    columns["actor1_geo_adm2_code"].append(r.actor1_geo_adm2_code)
    columns["actor1_geo_lat"].append(_safe_float(r.actor1_geo_lat))
    columns["actor1_geo_lon"].append(_safe_float(r.actor1_geo_lon))
    columns["actor1_geo_feature_id"].append(r.actor1_geo_feature_id)

    columns["actor2_geo_type"].append(_safe_int(r.actor2_geo_type))
    columns["actor2_geo_fullname"].append(r.actor2_geo_fullname)
    columns["actor2_geo_country_code"].append(r.actor2_geo_country_code)
    columns["actor2_geo_adm1_code"].append(r.actor2_geo_adm1_code)
    columns["actor2_geo_adm2_code"].append(r.actor2_geo_adm2_code)
    columns["actor2_geo_lat"].append(_safe_float(r.actor2_geo_lat))
    columns["actor2_geo_lon"].append(_safe_float(r.actor2_geo_lon))
    columns["actor2_geo_feature_id"].append(r.actor2_geo_feature_id)

    columns["action_geo_type"].append(_safe_int(r.action_geo_type))
    columns["action_geo_fullname"].append(r.action_geo_fullname)
    columns["action_geo_country_code"].append(r.action_geo_country_code)
    columns["action_geo_adm1_code"].append(r.action_geo_adm1_code)
    columns["action_geo_adm2_code"].append(r.action_geo_adm2_code)
    columns["action_geo_lat"].append(_safe_float(r.action_geo_lat))
    columns["action_geo_lon"].append(_safe_float(r.action_geo_lon))
    columns["action_geo_feature_id"].append(r.action_geo_feature_id)


def events_to_batch(records: Iterable[_RawEvent]) -> pa.RecordBatch:
    """Convert an iterable of ``_RawEvent`` into a single Arrow RecordBatch.

    Args:
        records: Raw event records to convert.

    Returns:
        A ``pa.RecordBatch`` conforming to :data:`EVENTS_SCHEMA`.
    """
    rows = list(records)
    if not rows:
        return pa.RecordBatch.from_pydict({f.name: [] for f in EVENTS_SCHEMA}, schema=EVENTS_SCHEMA)

    columns: dict[str, list[object]] = {f.name: [] for f in EVENTS_SCHEMA}
    for r in rows:
        _append_event_core(columns, r)
        _append_event_geo(columns, r)

    arrays = [pa.array(columns[f.name], type=f.type) for f in EVENTS_SCHEMA]
    return pa.RecordBatch.from_arrays(arrays, schema=EVENTS_SCHEMA)


# ---------------------------------------------------------------------------
# GKG converter
# ---------------------------------------------------------------------------


def gkg_to_batch(records: Iterable[_RawGKG]) -> pa.RecordBatch:
    """Convert an iterable of ``_RawGKG`` into a single Arrow RecordBatch.

    Args:
        records: Raw GKG records to convert.

    Returns:
        A ``pa.RecordBatch`` conforming to :data:`GKG_SCHEMA`.
    """
    rows = list(records)
    if not rows:
        return pa.RecordBatch.from_pydict({f.name: [] for f in GKG_SCHEMA}, schema=GKG_SCHEMA)

    columns: dict[str, list[object]] = {f.name: [] for f in GKG_SCHEMA}

    for r in rows:
        columns["gkg_record_id"].append(r.gkg_record_id)
        columns["date"].append(_parse_timestamp(r.date))
        columns["source_collection_id"].append(_safe_int(r.source_collection_id))
        columns["source_common_name"].append(r.source_common_name)
        columns["document_identifier"].append(r.document_identifier)

        columns["counts_v1"].append(r.counts_v1)
        columns["counts_v2"].append(r.counts_v2)

        columns["themes_v1"].append(r.themes_v1)
        columns["themes_v2_enhanced"].append(r.themes_v2_enhanced)

        columns["locations_v1"].append(r.locations_v1)
        columns["locations_v2_enhanced"].append(r.locations_v2_enhanced)

        columns["persons_v1"].append(r.persons_v1)
        columns["persons_v2_enhanced"].append(r.persons_v2_enhanced)
        columns["organizations_v1"].append(r.organizations_v1)
        columns["organizations_v2_enhanced"].append(r.organizations_v2_enhanced)

        columns["tone"].append(r.tone)
        columns["dates_v2"].append(r.dates_v2)
        columns["gcam"].append(r.gcam)

        columns["sharing_image"].append(r.sharing_image)
        columns["related_images"].append(r.related_images)
        columns["social_image_embeds"].append(r.social_image_embeds)
        columns["social_video_embeds"].append(r.social_video_embeds)

        columns["quotations"].append(r.quotations)
        columns["all_names"].append(r.all_names)
        columns["amounts"].append(r.amounts)

        columns["translation_info"].append(r.translation_info)
        columns["extras_xml"].append(r.extras_xml)
        columns["is_translated"].append(r.is_translated)

    arrays = [pa.array(columns[f.name], type=f.type) for f in GKG_SCHEMA]
    return pa.RecordBatch.from_arrays(arrays, schema=GKG_SCHEMA)


# ---------------------------------------------------------------------------
# Mentions converter
# ---------------------------------------------------------------------------


def mentions_to_batch(records: Iterable[_RawMention]) -> pa.RecordBatch:
    """Convert an iterable of ``_RawMention`` into a single Arrow RecordBatch.

    Args:
        records: Raw mention records to convert.

    Returns:
        A ``pa.RecordBatch`` conforming to :data:`MENTIONS_SCHEMA`.
    """
    rows = list(records)
    if not rows:
        return pa.RecordBatch.from_pydict(
            {f.name: [] for f in MENTIONS_SCHEMA}, schema=MENTIONS_SCHEMA
        )

    columns: dict[str, list[object]] = {f.name: [] for f in MENTIONS_SCHEMA}

    for r in rows:
        columns["global_event_id"].append(_safe_int(r.global_event_id))

        columns["event_time_date"].append(_parse_date32(r.event_time_date))
        columns["event_time_full"].append(_parse_timestamp(r.event_time_full))
        columns["mention_time_date"].append(_parse_date32(r.mention_time_date))
        columns["mention_time_full"].append(_parse_timestamp(r.mention_time_full))

        columns["mention_type"].append(_safe_int(r.mention_type))
        columns["mention_source_name"].append(r.mention_source_name)
        columns["mention_identifier"].append(r.mention_identifier)

        columns["sentence_id"].append(_safe_int(r.sentence_id))
        columns["actor1_char_offset"].append(_safe_int(r.actor1_char_offset))
        columns["actor2_char_offset"].append(_safe_int(r.actor2_char_offset))
        columns["action_char_offset"].append(_safe_int(r.action_char_offset))
        columns["in_raw_text"].append(_safe_int(r.in_raw_text))

        columns["confidence"].append(_safe_int(r.confidence))
        columns["mention_doc_length"].append(_safe_int(r.mention_doc_length))
        columns["mention_doc_tone"].append(_safe_float(r.mention_doc_tone))

        columns["mention_doc_translation_info"].append(r.mention_doc_translation_info)
        columns["extras"].append(r.extras)

    arrays = [pa.array(columns[f.name], type=f.type) for f in MENTIONS_SCHEMA]
    return pa.RecordBatch.from_arrays(arrays, schema=MENTIONS_SCHEMA)
