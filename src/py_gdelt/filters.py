"""
Pydantic filter models for GDELT query validation.

This module provides consolidated Pydantic models for validating filter parameters
across all GDELT data sources including Events, Mentions, GKG, DOC, GEO, and TV APIs.
"""

from __future__ import annotations

from datetime import date, datetime  # noqa: TC003 - Pydantic needs runtime access
from typing import Literal, TypeAlias

from pydantic import BaseModel, Field, field_validator, model_validator

from py_gdelt.exceptions import InvalidCodeError


__all__ = [
    "BroadcastNGramsFilter",
    "DateRange",
    "DocFilter",
    "EventFilter",
    "GALFilter",
    "GEGFilter",
    "GEMGFilter",
    "GFGFilter",
    "GGGFilter",
    "GKGFilter",
    "GKGGeoJSONFilter",
    "GQGFilter",
    "GeoFilter",
    "LowerThirdFilter",
    "NGramsFilter",
    "RadioNGramsFilter",
    "TVFilter",
    "TVGKGFilter",
    "TVNGramsFilter",
    "VGKGFilter",
]


class DateRange(BaseModel):
    """Date range filter with validation.

    Note:
        There is no enforced date range limit. File-based datasets (Events, GKG,
        Mentions, etc.) can span years of data. Use streaming methods for large
        date ranges to avoid memory issues.

        REST APIs have their own limits enforced server-side:
        - DOC 2.0: 1 year (with timespan=1y)
        - GEO 2.0: 7 days
        - Context 2.0: 72 hours
    """

    start: date
    end: date | None = None

    @model_validator(mode="after")
    def validate_range(self) -> DateRange:
        """Ensure start <= end."""
        end = self.end or self.start
        if end < self.start:
            msg = "end date must be >= start date"
            raise ValueError(msg)
        return self

    @property
    def days(self) -> int:
        """Number of days in range."""
        end = self.end or self.start
        return (end - self.start).days + 1


class EventFilter(BaseModel):
    """Filter for Events/Mentions queries.

    All filter fields work with both file downloads and BigQuery:
    - File source: Filters applied client-side after download
    - BigQuery: Filters applied server-side for efficiency

    Country codes (actor1_country, actor2_country, action_country) accept
    both FIPS and ISO3 formats and are normalized to FIPS automatically.

    Event codes are validated against CAMEO codebook.

    Args:
        date_range: Required date range for query.
        actor1_country: Filter by Actor1 country (FIPS or ISO3).
        actor2_country: Filter by Actor2 country (FIPS or ISO3).
        event_code: Filter by CAMEO event code.
        event_root_code: Filter by CAMEO root event code.
        event_base_code: Filter by CAMEO base event code.
        min_tone: Minimum average tone threshold.
        max_tone: Maximum average tone threshold.
        action_country: Filter by action location country (FIPS or ISO3).
        include_translated: Include machine-translated articles (default: True).
    """

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
        """Validate and normalize country codes (accepts FIPS or ISO3)."""
        if v is None:
            return None
        from py_gdelt.lookups.countries import Countries

        countries = Countries()
        return countries.normalize(v)  # Returns FIPS, raises InvalidCodeError if invalid

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
    """Filter for GKG queries.

    All filter fields work with both file downloads and BigQuery:
    - File source: Filters applied client-side after download
    - BigQuery: Filters applied server-side for efficiency

    Text fields (persons, organizations, theme_prefix) use **case-insensitive
    matching** - "Obama" matches "OBAMA", "obama", "Barack Obama", etc.

    Multi-value filters use **OR logic** - a record matches if ANY value
    in the list is found. For example, `persons=["Obama", "Biden"]` matches
    records containing either "Obama" OR "Biden" (or both).

    Args:
        date_range: Required date range for query.
        themes: List of exact GKG theme codes to match (OR logic, case-insensitive).
        theme_prefix: Match themes starting with prefix (case-insensitive).
        persons: Match records containing these person names (OR logic, case-insensitive substring).
        organizations: Match records containing these org names (OR logic, case-insensitive substring).
        country: Filter by country code (FIPS or ISO3, normalized to FIPS).
        min_tone: Minimum tone threshold.
        max_tone: Maximum tone threshold.
        include_translated: Include machine-translated articles (default: True).
    """

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
        """Validate and normalize country code (accepts FIPS or ISO3)."""
        if v is None:
            return None
        from py_gdelt.lookups.countries import Countries

        countries = Countries()
        return countries.normalize(v)  # Returns FIPS, raises InvalidCodeError if invalid


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
        """Validate and normalize source country code (accepts FIPS or ISO3)."""
        if v is None:
            return None
        from py_gdelt.lookups.countries import Countries

        countries = Countries()
        return countries.normalize(v)  # Returns FIPS, raises InvalidCodeError if invalid


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


class LowerThirdFilter(BaseModel):
    """Filter for LowerThird (Chyron) API queries.

    Attributes:
        query: Search terms. Supports exact phrases, boolean operators,
            show filters (show:"name"), station filters (station:CNN).
        timespan: Time offset (e.g., "24h", "7d", "1w"). Mutually exclusive
            with start_datetime/end_datetime.
        start_datetime: Start of date range (YYYYMMDDHHMMSS format internally).
        end_datetime: End of date range.
        mode: Output mode - ClipGallery, TimelineVol, StationChart.
        max_results: Max records (1-3000, default 250).
        sort: Sort order - DateDesc, DateAsc, or None for relevance.
    """

    query: str
    timespan: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    mode: Literal["ClipGallery", "TimelineVol", "StationChart"] = "ClipGallery"
    max_results: int = Field(default=250, ge=1, le=3000)
    sort: Literal["DateDesc", "DateAsc"] | None = None

    @model_validator(mode="after")
    def validate_time_constraints(self) -> LowerThirdFilter:
        """Validate that timespan and datetime range are mutually exclusive."""
        if self.timespan and (self.start_datetime or self.end_datetime):
            msg = "Cannot specify both timespan and datetime range"
            raise ValueError(msg)
        return self


class GKGGeoJSONFilter(BaseModel):
    """Filter for GKG GeoJSON API (v1.0 Legacy).

    Note:
        This is a v1.0 API that uses UPPERCASE parameter names.
        The timespan is limited to 1440 minutes (24 hours).

    Attributes:
        query: Theme, person, or organization to search.
        timespan: Minutes of data to include (1-1440, default 60).
    """

    query: str
    timespan: int = Field(default=60, ge=1, le=1440)


class VGKGFilter(BaseModel):
    """Filter for VGKG (Visual GKG) queries."""

    date_range: DateRange
    domain: str | None = None  # Filter by source domain
    min_label_confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str | None) -> str | None:
        """Normalize domain to lowercase."""
        return v.lower() if v else None


class TVGKGFilter(BaseModel):
    """Filter for TV-GKG (Television Global Knowledge Graph) queries.

    Note:
        TV-GKG uses standard GKG 2.0 format but has a 48-hour embargo.
        The embargo is handled in the endpoint layer, not the filter.
    """

    date_range: DateRange
    themes: list[str] | None = None
    station: str | None = None  # TV station filter

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

    @field_validator("station")
    @classmethod
    def validate_station(cls, v: str | None) -> str | None:
        """Normalize station name to uppercase."""
        return v.upper() if v else None


class BroadcastNGramsFilter(BaseModel):
    """Filter for TV/Radio NGrams queries."""

    date_range: DateRange
    station: str | None = None
    show: str | None = None  # Radio only
    ngram_size: int = Field(default=1, ge=1, le=5)  # 1-5 grams

    @field_validator("station")
    @classmethod
    def validate_station(cls, v: str | None) -> str | None:
        """Normalize station name to uppercase."""
        return v.upper() if v else None


# Type aliases for clarity
TVNGramsFilter: TypeAlias = BroadcastNGramsFilter
RadioNGramsFilter: TypeAlias = BroadcastNGramsFilter


class GQGFilter(BaseModel):
    """Filter for Global Quotation Graph queries.

    Note:
        The ``languages`` filter is applied client-side after download.
        All records for the date range are fetched, then filtered by language.
        Multi-value filters use OR logic.

    Args:
        date_range: Required date range for query.
        languages: Filter by language codes (client-side, OR logic).
    """

    date_range: DateRange
    languages: list[str] | None = None


class GEGFilter(BaseModel):
    """Filter for Global Entity Graph queries.

    Note:
        The ``languages`` filter is applied client-side after download.
        All records for the date range are fetched, then filtered by language.
        Multi-value filters use OR logic.

    Args:
        date_range: Required date range for query.
        languages: Filter by language codes (client-side, OR logic).
    """

    date_range: DateRange
    languages: list[str] | None = None


class GFGFilter(BaseModel):
    """Filter for Global Frontpage Graph queries.

    Note:
        The ``languages`` filter is applied client-side after download.
        All records for the date range are fetched, then filtered by language.
        Multi-value filters use OR logic.

    Args:
        date_range: Required date range for query.
        languages: Filter by language codes (client-side, OR logic).
    """

    date_range: DateRange
    languages: list[str] | None = None


class GGGFilter(BaseModel):
    """Filter for Global Geographic Graph queries.

    Note:
        GGG is a file-based dataset with no inherent date range limit.
        Large date ranges will produce large result sets - use streaming
        methods (``stream_ggg``) for memory efficiency.

        Unlike other graph filters, GGGFilter does not have a ``languages`` field
        because GGG records contain geographic data without language metadata.
    """

    date_range: DateRange


class GEMGFilter(BaseModel):
    """Filter for Global Embedded Metadata Graph queries.

    Note:
        The ``languages`` filter is applied client-side after download.
        All records for the date range are fetched, then filtered by language.
        Multi-value filters use OR logic.

    Args:
        date_range: Required date range for query.
        languages: Filter by language codes (client-side, OR logic).
    """

    date_range: DateRange
    languages: list[str] | None = None


class GALFilter(BaseModel):
    """Filter for Article List queries.

    Note:
        The ``languages`` filter is applied client-side after download.
        All records for the date range are fetched, then filtered by language.
        Multi-value filters use OR logic.

    Args:
        date_range: Required date range for query.
        languages: Filter by language codes (client-side, OR logic).
    """

    date_range: DateRange
    languages: list[str] | None = None
