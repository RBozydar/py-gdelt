"""Pydantic models for GDELT DOC API responses."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


logger = logging.getLogger(__name__)


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
            return datetime.strptime(self.seendate, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
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
    value: float = Field(default=0, alias="count")

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
                    return datetime.strptime(self.date, fmt).replace(tzinfo=UTC)
                except ValueError:
                    continue
        except Exception:  # noqa: BLE001
            return None
        else:
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
        """Parse timeline from various formats.

        Handles both flat format and nested series format from timelinevol API:
        - Flat: [{"date": "...", "value": ...}, ...]
        - Nested: [{"series": "...", "data": [{"date": "...", "value": ...}]}]
        """
        if v is None:
            return []
        if isinstance(v, list):
            points: list[TimelinePoint] = []
            for item in v:
                if isinstance(item, TimelinePoint):
                    points.append(item)
                elif isinstance(item, dict):
                    # Check for nested series/data structure from timelinevol API
                    if "data" in item and isinstance(item["data"], list):
                        for dp in item["data"]:
                            if isinstance(dp, dict):
                                points.append(TimelinePoint.model_validate(dp))
                            else:
                                logger.warning(
                                    "Skipping non-dict timeline data point: %s", type(dp).__name__
                                )
                    else:
                        # Flat structure with date/value directly
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
    def values(self) -> list[float]:
        """Get list of values."""
        return [p.value for p in self.timeline]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timeline": [p.model_dump() for p in self.timeline],
            "query": self.query,
            "total_articles": self.total_articles,
        }

    def to_series(self) -> dict[str, float]:
        """
        Convert to date:value mapping.

        Useful for quick lookups and plotting.
        """
        return {p.date: p.value for p in self.timeline}
