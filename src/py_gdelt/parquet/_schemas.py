"""PyArrow schemas for GDELT Events, GKG, and Mentions tables.

Schemas are built programmatically from the internal ``_Raw*`` dataclass fields
and per-table type maps.  Fields not present in a type map default to
``pa.string()``.  Nullability is inferred from the dataclass annotation: a
field whose type is a union containing ``None`` (e.g. ``str | None``) is
nullable; all others are not.
"""

from __future__ import annotations

import types
from typing import Any, get_type_hints

import pyarrow as pa

from py_gdelt.models._internal import _RawEvent, _RawGKG, _RawMention


__all__ = [
    "EVENTS_SCHEMA",
    "GKG_SCHEMA",
    "MENTIONS_SCHEMA",
]

# ---------------------------------------------------------------------------
# Type maps -- map field names to non-default Arrow types
# ---------------------------------------------------------------------------

_EVENT_TYPE_MAP: dict[str, pa.DataType] = {
    "global_event_id": pa.int64(),
    "sql_date": pa.date32(),
    "month_year": pa.int32(),
    "year": pa.int16(),
    "fraction_date": pa.float64(),
    "is_root_event": pa.bool_(),
    "quad_class": pa.int8(),
    "goldstein_scale": pa.float64(),
    "num_mentions": pa.int32(),
    "num_sources": pa.int32(),
    "num_articles": pa.int32(),
    "avg_tone": pa.float64(),
    "actor1_geo_type": pa.int8(),
    "actor2_geo_type": pa.int8(),
    "action_geo_type": pa.int8(),
    "actor1_geo_lat": pa.float64(),
    "actor1_geo_lon": pa.float64(),
    "actor2_geo_lat": pa.float64(),
    "actor2_geo_lon": pa.float64(),
    "action_geo_lat": pa.float64(),
    "action_geo_lon": pa.float64(),
    "date_added": pa.timestamp("s", tz="UTC"),
    "is_translated": pa.bool_(),
}

_GKG_TYPE_MAP: dict[str, pa.DataType] = {
    "date": pa.timestamp("s", tz="UTC"),
    "source_collection_id": pa.int8(),
    "is_translated": pa.bool_(),
}

_MENTION_TYPE_MAP: dict[str, pa.DataType] = {
    "global_event_id": pa.int64(),
    "sentence_id": pa.int32(),
    "actor1_char_offset": pa.int32(),
    "actor2_char_offset": pa.int32(),
    "action_char_offset": pa.int32(),
    "in_raw_text": pa.int8(),
    "confidence": pa.int32(),
    "mention_doc_length": pa.int32(),
    "mention_doc_tone": pa.float64(),
    "mention_type": pa.int8(),
    "event_time_date": pa.date32(),
    "event_time_full": pa.timestamp("s", tz="UTC"),
    "mention_time_date": pa.date32(),
    "mention_time_full": pa.timestamp("s", tz="UTC"),
}


# ---------------------------------------------------------------------------
# Schema builder
# ---------------------------------------------------------------------------


def _is_nullable(annotation: Any) -> bool:
    """Return ``True`` if *annotation* is a union that includes ``None``.

    Args:
        annotation: A resolved type annotation from ``get_type_hints()``.

    Returns:
        Whether the annotation is nullable (i.e. includes ``NoneType``).
    """
    if isinstance(annotation, types.UnionType):
        return type(None) in annotation.__args__
    return False


def _build_schema(
    raw_cls: type[_RawEvent] | type[_RawGKG] | type[_RawMention],
    type_map: dict[str, pa.DataType],
) -> pa.Schema:
    """Build a ``pa.Schema`` from a ``_Raw*`` dataclass and a type map.

    For each field on *raw_cls* the Arrow type is looked up in *type_map*,
    falling back to ``pa.string()``.  Nullability is derived from the
    dataclass annotation (``str | None`` is nullable, ``str`` is not).

    Args:
        raw_cls: One of the internal raw dataclass types.
        type_map: Mapping of field name to explicit Arrow data type.

    Returns:
        A fully specified PyArrow schema.
    """
    hints = get_type_hints(raw_cls)
    fields: list[pa.Field] = []
    for name, annotation in hints.items():
        arrow_type = type_map.get(name, pa.string())
        nullable = _is_nullable(annotation)
        fields.append(pa.field(name, arrow_type, nullable=nullable))
    return pa.schema(fields)


# ---------------------------------------------------------------------------
# Public schemas
# ---------------------------------------------------------------------------

EVENTS_SCHEMA: pa.Schema = _build_schema(_RawEvent, _EVENT_TYPE_MAP)
GKG_SCHEMA: pa.Schema = _build_schema(_RawGKG, _GKG_TYPE_MAP)
MENTIONS_SCHEMA: pa.Schema = _build_schema(_RawMention, _MENTION_TYPE_MAP)
