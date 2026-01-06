"""Common Pydantic models shared across py-gdelt."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel, Field


if TYPE_CHECKING:
    from collections.abc import Iterator


__all__ = [
    "EntityMention",
    "FailedRequest",
    "FetchResult",
    "Location",
    "ToneScores",
]


T = TypeVar("T")


class Location(BaseModel):
    """Geographic location from GDELT data."""

    lat: float | None = None
    lon: float | None = None
    feature_id: str | None = None  # GNIS/ADM1 code
    name: str | None = None
    country_code: str | None = None  # FIPS code
    adm1_code: str | None = None
    adm2_code: str | None = None
    geo_type: int | None = None  # 1=Country, 2=State, 3=City, 4=Coordinates

    def as_tuple(self) -> tuple[float, float]:
        """Return (lat, lon) tuple. Raises ValueError if either is None."""
        if self.lat is None or self.lon is None:
            msg = "Cannot create tuple: lat or lon is None"
            raise ValueError(msg)
        return (self.lat, self.lon)

    def as_wkt(self) -> str:
        """Return WKT POINT string for geopandas compatibility.

        Returns:
            WKT POINT string in format "POINT(lon lat)".

        Raises:
            ValueError: If lat or lon is None.
        """
        if self.lat is None or self.lon is None:
            msg = "Cannot create WKT: lat or lon is None"
            raise ValueError(msg)
        return f"POINT({self.lon} {self.lat})"

    @property
    def has_coordinates(self) -> bool:
        """Check if location has valid coordinates."""
        return self.lat is not None and self.lon is not None


class ToneScores(BaseModel):
    """Tone analysis scores from GDELT."""

    tone: float = Field(..., ge=-100, le=100)  # Overall tone (-100 to +100)
    positive_score: float
    negative_score: float
    polarity: float  # Emotional extremity
    activity_reference_density: float
    self_group_reference_density: float
    word_count: int | None = None


class EntityMention(BaseModel):
    """Entity mention from GKG records."""

    entity_type: str  # PERSON, ORG, LOCATION, etc.
    name: str
    offset: int | None = None  # Character offset in source
    confidence: float | None = None


@dataclass(slots=True)
class FailedRequest:
    """Represents a failed request in a partial result."""

    url: str
    error: str
    status_code: int | None = None
    retry_after: int | None = None  # For rate limit errors


@dataclass
class FetchResult(Generic[T]):
    """Result container with partial failure tracking."""

    data: list[T]
    failed: list[FailedRequest] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        """True if no requests failed."""
        return len(self.failed) == 0

    @property
    def partial(self) -> bool:
        """True if some but not all requests failed."""
        return len(self.failed) > 0 and len(self.data) > 0

    @property
    def total_failed(self) -> int:
        """Number of failed requests."""
        return len(self.failed)

    def __iter__(self) -> Iterator[T]:
        """Allow direct iteration over data."""
        return iter(self.data)

    def __len__(self) -> int:
        """Return count of successful items."""
        return len(self.data)
