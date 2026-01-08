"""
Pydantic filter models for GDELT query validation.

This module provides consolidated Pydantic models for validating filter parameters
across all GDELT data sources including Events, Mentions, GKG, DOC, GEO, and TV APIs.
"""

from __future__ import annotations

from datetime import date, datetime  # noqa: TC003 - Pydantic needs runtime access
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from py_gdelt.exceptions import InvalidCodeError


__all__ = [
    "DateRange",
    "DocFilter",
    "EventFilter",
    "GKGFilter",
    "GeoFilter",
    "NGramsFilter",
    "TVFilter",
]


class DateRange(BaseModel):
    """Date range filter with validation."""

    start: date
    end: date | None = None

    @model_validator(mode="after")
    def validate_range(self) -> DateRange:
        """Ensure start <= end and range not too large."""
        end = self.end or self.start
        if end < self.start:
            msg = "end date must be >= start date"
            raise ValueError(msg)
        if (end - self.start).days > 365:
            msg = "date range cannot exceed 365 days"
            raise ValueError(msg)
        return self

    @property
    def days(self) -> int:
        """Number of days in range."""
        end = self.end or self.start
        return (end - self.start).days + 1


class EventFilter(BaseModel):
    """Filter for Events/Mentions queries."""

    date_range: DateRange

    # Actor filters (CAMEO country codes validated)
    actor1_country: str | None = None
    actor2_country: str | None = None

    # Event type filters (CAMEO event codes validated)
    event_code: str | None = None
    event_root_code: str | None = None
    event_base_code: str | None = None

    # Tone filter
    min_tone: float | None = None
    max_tone: float | None = None

    # Location filters
    action_country: str | None = None

    # Options
    include_translated: bool = True

    @field_validator("actor1_country", "actor2_country", "action_country", mode="before")
    @classmethod
    def validate_country_code(cls, v: str | None) -> str | None:
        """Validate and normalize country codes."""
        if v is None:
            return None
        # Import here to avoid circular imports
        from py_gdelt.lookups.countries import Countries

        countries = Countries()
        try:
            countries.validate(v.upper())
        except InvalidCodeError:
            msg = f"Invalid country code: {v!r}"
            raise InvalidCodeError(msg, code=v, code_type="country") from None
        return v.upper()

    @field_validator("event_code", "event_root_code", "event_base_code", mode="before")
    @classmethod
    def validate_cameo_code(cls, v: str | None) -> str | None:
        """Validate CAMEO event codes."""
        if v is None:
            return None
        from py_gdelt.lookups.cameo import CAMEOCodes

        cameo = CAMEOCodes()
        try:
            cameo.validate(v)
        except InvalidCodeError:
            msg = f"Invalid CAMEO code: {v!r}"
            raise InvalidCodeError(msg, code=v, code_type="CAMEO") from None
        return v


class GKGFilter(BaseModel):
    """Filter for GKG queries."""

    date_range: DateRange

    # Theme filters (validated against GKG themes)
    themes: list[str] | None = None
    theme_prefix: str | None = None

    # Entity filters
    persons: list[str] | None = None
    organizations: list[str] | None = None

    # Location
    country: str | None = None

    # Tone
    min_tone: float | None = None
    max_tone: float | None = None

    # Options
    include_translated: bool = True

    @field_validator("themes", mode="before")
    @classmethod
    def validate_themes(cls, v: list[str] | None) -> list[str] | None:
        """Validate GKG theme codes."""
        if v is None:
            return None
        from py_gdelt.lookups.themes import GKGThemes

        themes = GKGThemes()
        for theme in v:
            try:
                themes.validate(theme)
            except InvalidCodeError:
                msg = f"Invalid GKG theme: {theme!r}"
                raise InvalidCodeError(msg, code=theme, code_type="GKG theme") from None
        return v

    @field_validator("country", mode="before")
    @classmethod
    def validate_country(cls, v: str | None) -> str | None:
        """Validate and normalize country code."""
        if v is None:
            return None
        from py_gdelt.lookups.countries import Countries

        countries = Countries()
        try:
            countries.validate(v.upper())
        except InvalidCodeError:
            msg = f"Invalid country code: {v!r}"
            raise InvalidCodeError(msg, code=v, code_type="country") from None
        return v.upper()


class DocFilter(BaseModel):
    """Filter for DOC 2.0 API queries."""

    query: str

    # Time constraints
    timespan: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None

    # Source filtering
    source_country: str | None = None
    source_language: str | None = None

    # Result options
    max_results: int = Field(default=250, ge=1, le=250)
    sort_by: Literal["date", "relevance", "tone"] = "date"

    # Output mode
    mode: Literal["artlist", "artgallery", "timelinevol"] = "artlist"

    @model_validator(mode="after")
    def validate_time_constraints(self) -> DocFilter:
        """Ensure timespan XOR datetime range, not both."""
        if self.timespan and (self.start_datetime or self.end_datetime):
            msg = "Cannot specify both timespan and datetime range"
            raise ValueError(msg)
        return self

    @field_validator("source_country", mode="before")
    @classmethod
    def validate_source_country(cls, v: str | None) -> str | None:
        """Validate and normalize source country code."""
        if v is None:
            return None
        from py_gdelt.lookups.countries import Countries

        countries = Countries()
        try:
            countries.validate(v.upper())
        except InvalidCodeError:
            msg = f"Invalid country code: {v!r}"
            raise InvalidCodeError(msg, code=v, code_type="country") from None
        return v.upper()


class GeoFilter(BaseModel):
    """Filter for GEO 2.0 API queries."""

    query: str

    # Geographic bounds (optional)
    bounding_box: tuple[float, float, float, float] | None = None

    # Time
    timespan: str | None = None

    # Result options
    max_results: int = Field(default=250, ge=1, le=250)

    @field_validator("bounding_box", mode="before")
    @classmethod
    def validate_bbox(
        cls,
        v: tuple[float, float, float, float] | None,
    ) -> tuple[float, float, float, float] | None:
        """Validate bounding box coordinates."""
        if v is None:
            return None
        min_lat, min_lon, max_lat, max_lon = v
        if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
            msg = "Latitude must be between -90 and 90"
            raise ValueError(msg)
        if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
            msg = "Longitude must be between -180 and 180"
            raise ValueError(msg)
        if min_lat > max_lat:
            msg = "min_lat must be <= max_lat"
            raise ValueError(msg)
        if min_lon > max_lon:
            msg = "min_lon must be <= max_lon"
            raise ValueError(msg)
        return v


class TVFilter(BaseModel):
    """Filter for TV API queries."""

    query: str

    # Time
    timespan: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None

    # Station filtering
    station: str | None = None
    market: str | None = None

    # Result options
    max_results: int = Field(default=250, ge=1, le=250)
    mode: Literal["ClipGallery", "TimelineVol", "StationChart"] = "ClipGallery"


class NGramsFilter(BaseModel):
    """Filter for NGrams 3.0 queries."""

    date_range: DateRange

    # NGram filtering
    ngram: str | None = None
    language: str | None = None

    # Position filtering (decile 0-90)
    min_position: int | None = Field(default=None, ge=0, le=90)
    max_position: int | None = Field(default=None, ge=0, le=90)

    @model_validator(mode="after")
    def validate_position_range(self) -> NGramsFilter:
        """Ensure min_position <= max_position."""
        if (
            self.min_position is not None
            and self.max_position is not None
            and self.min_position > self.max_position
        ):
            msg = "min_position must be <= max_position"
            raise ValueError(msg)
        return self
