"""Pydantic models for GDELT NGrams 3.0 data."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel


if TYPE_CHECKING:
    from py_gdelt.models._internal import _RawNGram


__all__ = ["NGramRecord"]


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
            date=datetime.strptime(raw.date, "%Y%m%d%H%M%S").replace(tzinfo=UTC),
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
