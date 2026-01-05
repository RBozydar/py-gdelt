"""Pydantic models for GDELT DOC API responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


__all__ = ["Article", "Timeline", "TimelinePoint"]


class Article(BaseModel):
    """
    Article from GDELT DOC API.

    Represents a news article monitored by GDELT.
    """

    # Core fields (from API)
    url: str
    title: str | None = None
    seendate: str | None = None  # Raw GDELT date string (YYYYMMDDHHMMSS)

    # Source information
    domain: str | None = None
    source_country: str | None = Field(default=None, alias="sourcecountry")
    language: str | None = None

    # Content
    socialimage: str | None = None  # Preview image URL

    # Tone analysis (optional)
    tone: float | None = None

    # Sharing metrics (optional)
    share_count: int | None = Field(default=None, alias="sharecount")

    model_config = {"populate_by_name": True}

    @property
    def seen_datetime(self) -> datetime | None:
        """
        Parse seendate to datetime.

        Returns:
            datetime object or None if parsing fails
        """
        if not self.seendate:
            return None
        try:
            return datetime.strptime(self.seendate, "%Y%m%d%H%M%S")
        except ValueError:
            return None

    @property
    def is_english(self) -> bool:
        """Check if article is in English."""
        if not self.language:
            return False
        return self.language.lower() in ("english", "en")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(by_alias=True)


class TimelinePoint(BaseModel):
    """Single data point in a timeline."""

    date: str
    value: int = Field(default=0, alias="count")

    # Optional breakdown
    tone: float | None = None

    model_config = {"populate_by_name": True}

    @property
    def parsed_date(self) -> datetime | None:
        """Parse date string to datetime."""
        if not self.date:
            return None
        try:
            # Try various formats
            for fmt in ("%Y-%m-%d", "%Y%m%d", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(self.date, fmt)
                except ValueError:
                    continue
            return None
        except Exception:
            return None


class Timeline(BaseModel):
    """
    Timeline data from GDELT DOC API.

    Contains time series data for article volume.
    """

    # The timeline data
    timeline: list[TimelinePoint] = Field(default_factory=list)

    # Metadata
    query: str | None = None
    total_articles: int | None = None

    @field_validator("timeline", mode="before")
    @classmethod
    def parse_timeline(cls, v: Any) -> list[TimelinePoint]:
        """Parse timeline from various formats."""
        if v is None:
            return []
        if isinstance(v, list):
            # Already a list
            points = []
            for item in v:
                if isinstance(item, TimelinePoint):
                    points.append(item)
                elif isinstance(item, dict):
                    points.append(TimelinePoint.model_validate(item))
            return points
        return []

    @property
    def points(self) -> list[TimelinePoint]:
        """Alias for timeline for cleaner access."""
        return self.timeline

    @property
    def dates(self) -> list[str]:
        """Get list of dates."""
        return [p.date for p in self.timeline]

    @property
    def values(self) -> list[int]:
        """Get list of values."""
        return [p.value for p in self.timeline]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timeline": [p.model_dump() for p in self.timeline],
            "query": self.query,
            "total_articles": self.total_articles,
        }

    def to_series(self) -> dict[str, int]:
        """
        Convert to date:value mapping.

        Useful for quick lookups and plotting.
        """
        return {p.date: p.value for p in self.timeline}
