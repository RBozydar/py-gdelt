"""Public Pydantic models for GDELT Events data.

This module contains the public API models for GDELT Events and Mentions.
These models are converted from internal _RawEvent and _RawMention dataclasses
after parsing from TAB-delimited files.
"""

from __future__ import annotations

from contextlib import suppress
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from py_gdelt.models.common import Location


if TYPE_CHECKING:
    from py_gdelt.models._internal import _RawEvent, _RawMention


__all__ = ["Actor", "Event", "Mention"]


class Actor(BaseModel):
    """Actor in a GDELT event.

    Represents an entity (person, organization, country, etc.) participating in an event.
    Uses CAMEO actor codes for classification.
    """

    code: str | None = None
    name: str | None = None
    country_code: str | None = None  # FIPS code
    known_group_code: str | None = None
    ethnic_code: str | None = None
    religion1_code: str | None = None
    religion2_code: str | None = None
    type1_code: str | None = None
    type2_code: str | None = None
    type3_code: str | None = None

    @property
    def is_state_actor(self) -> bool:
        """Check if actor is a state/government actor.

        Returns:
            True if actor has a country code but no known group code,
            indicating a state-level actor.
        """
        return self.country_code is not None and self.known_group_code is None


class Event(BaseModel):
    """GDELT Event record.

    Represents a single event in the GDELT Events database. Events capture
    who did what to whom, when, where, and how it was reported.
    """

    # Identifiers
    global_event_id: int
    date: date  # Event date
    date_added: datetime | None = None  # When first recorded (UTC)
    source_url: str | None = None

    # Actors
    actor1: Actor | None = None
    actor2: Actor | None = None

    # Action
    event_code: str  # CAMEO code (string, not int, to preserve leading zeros)
    event_base_code: str
    event_root_code: str
    quad_class: int = Field(..., ge=1, le=4)  # 1-4
    goldstein_scale: float = Field(..., ge=-10, le=10)  # -10 to +10

    # Metrics
    num_mentions: int = Field(default=0, ge=0)
    num_sources: int = Field(default=0, ge=0)
    num_articles: int = Field(default=0, ge=0)
    avg_tone: float = 0.0
    is_root_event: bool = False

    # Geography (use Location from common.py)
    actor1_geo: Location | None = None
    actor2_geo: Location | None = None
    action_geo: Location | None = None

    # Metadata
    version: int = Field(default=2, ge=1, le=2)  # 1 or 2
    is_translated: bool = False
    original_record_id: str | None = None  # For translated records

    @classmethod
    def from_raw(cls, raw: _RawEvent) -> Event:
        """Convert internal _RawEvent to public Event model.

        Args:
            raw: Internal _RawEvent dataclass from TAB-delimited parsing.

        Returns:
            Event: Public Event model with proper type conversion.

        Raises:
            ValueError: If required fields are missing or invalid.
        """

        # Helper to safely parse int
        def _parse_int(value: str | None, default: int = 0) -> int:
            if not value or value == "":
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        # Helper to safely parse float
        def _parse_float(value: str | None, default: float = 0.0) -> float:
            if not value or value == "":
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        # Helper to safely parse bool
        def _parse_bool(value: str | None) -> bool:
            if not value or value == "":
                return False
            return value.strip() == "1"

        # Helper to create Location from geo fields
        def _make_location(
            geo_type: str | None,
            name: str | None,
            country_code: str | None,
            adm1_code: str | None,
            adm2_code: str | None,
            lat: str | None,
            lon: str | None,
            feature_id: str | None,
        ) -> Location | None:
            # If no geo data, return None
            if not any(
                [
                    geo_type,
                    name,
                    country_code,
                    adm1_code,
                    adm2_code,
                    lat,
                    lon,
                    feature_id,
                ],
            ):
                return None

            return Location(
                lat=_parse_float(lat) if lat else None,
                lon=_parse_float(lon) if lon else None,
                feature_id=feature_id if feature_id else None,
                name=name if name else None,
                country_code=country_code if country_code else None,
                adm1_code=adm1_code if adm1_code else None,
                adm2_code=adm2_code if adm2_code else None,
                geo_type=_parse_int(geo_type) if geo_type else None,
            )

        # Helper to create Actor
        def _make_actor(
            code: str | None,
            name: str | None,
            country_code: str | None,
            known_group_code: str | None,
            ethnic_code: str | None,
            religion1_code: str | None,
            religion2_code: str | None,
            type1_code: str | None,
            type2_code: str | None,
            type3_code: str | None,
        ) -> Actor | None:
            # If no actor data, return None
            if not any(
                [
                    code,
                    name,
                    country_code,
                    known_group_code,
                    ethnic_code,
                    religion1_code,
                    religion2_code,
                    type1_code,
                    type2_code,
                    type3_code,
                ],
            ):
                return None

            return Actor(
                code=code if code else None,
                name=name if name else None,
                country_code=country_code if country_code else None,
                known_group_code=known_group_code if known_group_code else None,
                ethnic_code=ethnic_code if ethnic_code else None,
                religion1_code=religion1_code if religion1_code else None,
                religion2_code=religion2_code if religion2_code else None,
                type1_code=type1_code if type1_code else None,
                type2_code=type2_code if type2_code else None,
                type3_code=type3_code if type3_code else None,
            )

        # Parse date from sql_date (YYYYMMDD)
        event_date = datetime.strptime(raw.sql_date, "%Y%m%d").replace(tzinfo=UTC).date()

        # Parse date_added (YYYYMMDDHHMMSS)
        date_added_dt: datetime | None = None
        if raw.date_added:
            with suppress(ValueError):
                date_added_dt = datetime.strptime(raw.date_added, "%Y%m%d%H%M%S").replace(
                    tzinfo=UTC,
                )

        # Create actors
        actor1 = _make_actor(
            raw.actor1_code,
            raw.actor1_name,
            raw.actor1_country_code,
            raw.actor1_known_group_code,
            raw.actor1_ethnic_code,
            raw.actor1_religion1_code,
            raw.actor1_religion2_code,
            raw.actor1_type1_code,
            raw.actor1_type2_code,
            raw.actor1_type3_code,
        )

        actor2 = _make_actor(
            raw.actor2_code,
            raw.actor2_name,
            raw.actor2_country_code,
            raw.actor2_known_group_code,
            raw.actor2_ethnic_code,
            raw.actor2_religion1_code,
            raw.actor2_religion2_code,
            raw.actor2_type1_code,
            raw.actor2_type2_code,
            raw.actor2_type3_code,
        )

        # Create locations
        actor1_geo = _make_location(
            raw.actor1_geo_type,
            raw.actor1_geo_fullname,
            raw.actor1_geo_country_code,
            raw.actor1_geo_adm1_code,
            raw.actor1_geo_adm2_code,
            raw.actor1_geo_lat,
            raw.actor1_geo_lon,
            raw.actor1_geo_feature_id,
        )

        actor2_geo = _make_location(
            raw.actor2_geo_type,
            raw.actor2_geo_fullname,
            raw.actor2_geo_country_code,
            raw.actor2_geo_adm1_code,
            raw.actor2_geo_adm2_code,
            raw.actor2_geo_lat,
            raw.actor2_geo_lon,
            raw.actor2_geo_feature_id,
        )

        action_geo = _make_location(
            raw.action_geo_type,
            raw.action_geo_fullname,
            raw.action_geo_country_code,
            raw.action_geo_adm1_code,
            raw.action_geo_adm2_code,
            raw.action_geo_lat,
            raw.action_geo_lon,
            raw.action_geo_feature_id,
        )

        return cls(
            global_event_id=_parse_int(raw.global_event_id),
            date=event_date,
            date_added=date_added_dt,
            source_url=raw.source_url if raw.source_url else None,
            actor1=actor1,
            actor2=actor2,
            event_code=raw.event_code,  # Keep as string to preserve leading zeros
            event_base_code=raw.event_base_code,
            event_root_code=raw.event_root_code,
            quad_class=_parse_int(raw.quad_class, default=1),
            goldstein_scale=_parse_float(raw.goldstein_scale, default=0.0),
            num_mentions=_parse_int(raw.num_mentions, default=0),
            num_sources=_parse_int(raw.num_sources, default=0),
            num_articles=_parse_int(raw.num_articles, default=0),
            avg_tone=_parse_float(raw.avg_tone, default=0.0),
            is_root_event=_parse_bool(raw.is_root_event),
            actor1_geo=actor1_geo,
            actor2_geo=actor2_geo,
            action_geo=action_geo,
            version=2,  # Default to v2, can be overridden
            is_translated=raw.is_translated,
            original_record_id=None,  # Not in raw data
        )

    @property
    def is_conflict(self) -> bool:
        """Check if event is conflict (quad_class 3 or 4).

        Returns:
            True if event is material conflict (3) or verbal conflict (4).
        """
        return self.quad_class in (3, 4)

    @property
    def is_cooperation(self) -> bool:
        """Check if event is cooperation (quad_class 1 or 2).

        Returns:
            True if event is verbal cooperation (1) or material cooperation (2).
        """
        return self.quad_class in (1, 2)


class Mention(BaseModel):
    """Mention of a GDELT event in a source.

    Represents a single mention of an event in a news article. Each event
    can have many mentions across different sources and times.
    """

    global_event_id: int
    event_time: datetime
    mention_time: datetime
    mention_type: int  # 1=WEB, 2=Citation, 3=CORE, etc.
    source_name: str
    identifier: str  # URL, DOI, or citation
    sentence_id: int
    actor1_char_offset: int | None = None
    actor2_char_offset: int | None = None
    action_char_offset: int | None = None
    in_raw_text: bool = False
    confidence: int = Field(..., ge=10, le=100)  # 10-100
    doc_length: int = Field(default=0, ge=0)
    doc_tone: float = 0.0
    translation_info: str | None = None

    @classmethod
    def from_raw(cls, raw: _RawMention) -> Mention:
        """Convert internal _RawMention to public Mention model.

        Args:
            raw: Internal _RawMention dataclass from TAB-delimited parsing.

        Returns:
            Mention: Public Mention model with proper type conversion.

        Raises:
            ValueError: If required fields are missing or invalid.
        """

        # Helper to safely parse int
        def _parse_int(value: str | None, default: int = 0) -> int:
            if not value or value == "":
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        # Helper to safely parse float
        def _parse_float(value: str | None, default: float = 0.0) -> float:
            if not value or value == "":
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        # Helper to safely parse bool
        def _parse_bool(value: str | None) -> bool:
            if not value or value == "":
                return False
            return value.strip() == "1"

        # Parse event_time (YYYYMMDDHHMMSS)
        event_time = datetime.strptime(raw.event_time_full, "%Y%m%d%H%M%S").replace(tzinfo=UTC)

        # Parse mention_time (YYYYMMDDHHMMSS)
        mention_time = datetime.strptime(raw.mention_time_full, "%Y%m%d%H%M%S").replace(tzinfo=UTC)

        # Parse char offsets (can be empty string)
        actor1_offset = (
            _parse_int(raw.actor1_char_offset)
            if raw.actor1_char_offset and raw.actor1_char_offset != ""
            else None
        )
        actor2_offset = (
            _parse_int(raw.actor2_char_offset)
            if raw.actor2_char_offset and raw.actor2_char_offset != ""
            else None
        )
        action_offset = (
            _parse_int(raw.action_char_offset)
            if raw.action_char_offset and raw.action_char_offset != ""
            else None
        )

        return cls(
            global_event_id=_parse_int(raw.global_event_id),
            event_time=event_time,
            mention_time=mention_time,
            mention_type=_parse_int(raw.mention_type, default=1),
            source_name=raw.mention_source_name,
            identifier=raw.mention_identifier,
            sentence_id=_parse_int(raw.sentence_id, default=0),
            actor1_char_offset=actor1_offset,
            actor2_char_offset=actor2_offset,
            action_char_offset=action_offset,
            in_raw_text=_parse_bool(raw.in_raw_text),
            confidence=_parse_int(raw.confidence, default=50),
            doc_length=_parse_int(raw.mention_doc_length, default=0),
            doc_tone=_parse_float(raw.mention_doc_tone, default=0.0),
            translation_info=(
                raw.mention_doc_translation_info if raw.mention_doc_translation_info else None
            ),
        )
