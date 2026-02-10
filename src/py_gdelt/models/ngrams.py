"""Pydantic models for GDELT NGrams 3.0 data."""

from __future__ import annotations

from datetime import date as date_type  # noqa: TC003 - Pydantic needs runtime access
from datetime import datetime  # noqa: TC003 - Pydantic needs runtime access
from enum import StrEnum
from typing import TYPE_CHECKING, TypeAlias

from pydantic import BaseModel, Field

from py_gdelt.utils.dates import parse_gdelt_date, parse_gdelt_datetime


if TYPE_CHECKING:
    from py_gdelt.models._internal import _RawBroadcastNGram, _RawNGram


__all__ = [
    "BroadcastNGramRecord",
    "BroadcastSource",
    "NGramRecord",
    "RadioNGramRecord",
    "TVNGramRecord",
]


class BroadcastSource(StrEnum):
    """Source type for broadcast NGrams."""

    TV = "tv"
    RADIO = "radio"


class NGramRecord(BaseModel):
    """GDELT NGram 3.0 record.

    Represents an n-gram (word or phrase) occurrence in web content,
    including context and source information.
    """

    date: datetime
    ngram: str  # Word or character
    language: str  # ISO 639-1/2
    segment_type: int  # 1=space-delimited, 2=scriptio continua
    position: int  # Article decile (0-90, where 0 = first 10% of article)
    pre_context: str  # ~7 words before
    post_context: str  # ~7 words after
    url: str

    @classmethod
    def from_raw(cls, raw: _RawNGram) -> NGramRecord:
        """Convert internal _RawNGram to public NGramRecord model.

        Args:
            raw: Internal raw ngram representation with string fields

        Returns:
            Validated NGramRecord instance

        Raises:
            ValueError: If date parsing or type conversion fails
        """
        return cls(
            date=parse_gdelt_datetime(raw.date),
            ngram=raw.ngram,
            language=raw.language,
            segment_type=int(raw.segment_type),
            position=int(raw.position),
            pre_context=raw.pre_context,
            post_context=raw.post_context,
            url=raw.url,
        )

    @property
    def context(self) -> str:
        """Get full context (pre + ngram + post).

        Returns:
            Full context string with ngram surrounded by pre and post context
        """
        return f"{self.pre_context} {self.ngram} {self.post_context}"

    @property
    def is_early_in_article(self) -> bool:
        """Check if ngram appears in first 30% of article.

        Returns:
            True if position <= 20 (first 30% of article)
        """
        return self.position <= 20

    @property
    def is_late_in_article(self) -> bool:
        """Check if ngram appears in last 30% of article.

        Returns:
            True if position >= 70 (last 30% of article)
        """
        return self.position >= 70


class BroadcastNGramRecord(BaseModel):
    """Broadcast NGram frequency record (TV or Radio).

    Unified model for both TV and Radio NGrams since schemas are compatible.
    TV NGrams: 5 columns (DATE, STATION, HOUR, WORD, COUNT)
    Radio NGrams: 6 columns (DATE, STATION, HOUR, NGRAM, COUNT, SHOW)

    Attributes:
        date: Date of the broadcast.
        station: Station identifier (e.g., CNN, KQED).
        hour: Hour of broadcast (0-23).
        ngram: Word or phrase.
        count: Frequency count.
        show: Show name (Radio only, None for TV).
        source: Indicates origin (tv or radio).
    """

    date: date_type
    station: str
    hour: int = Field(ge=0, le=23)
    ngram: str
    count: int = Field(ge=0)
    show: str | None = None
    source: BroadcastSource

    @classmethod
    def from_raw(cls, raw: _RawBroadcastNGram, source: BroadcastSource) -> BroadcastNGramRecord:
        """Convert internal _RawBroadcastNGram to public model.

        Args:
            raw: Internal raw broadcast ngram representation.
            source: Source type (TV or Radio).

        Returns:
            Validated BroadcastNGramRecord instance.

        Raises:
            ValueError: If date parsing or type conversion fails.
        """
        return cls(
            date=parse_gdelt_date(raw.date),
            station=raw.station,
            hour=int(raw.hour),
            ngram=raw.ngram,
            count=int(raw.count),
            show=raw.show if raw.show else None,
            source=source,
        )


# Type aliases for clarity in endpoint signatures
TVNGramRecord: TypeAlias = BroadcastNGramRecord
RadioNGramRecord: TypeAlias = BroadcastNGramRecord
