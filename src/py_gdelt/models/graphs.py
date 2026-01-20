"""Public Pydantic models for GDELT Graph Datasets.

This module contains models for all 6 GDELT graph datasets:
- GQG (Global Quotation Graph)
- GEG (Global Entity Graph)
- GFG (Global Frontpage Graph)
- GGG (Global Geographic Graph)
- GEMG (Global Embedded Metadata Graph)
- GAL (Article List)
"""

from __future__ import annotations

import logging
import warnings
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Self

from pydantic import BaseModel, Field, field_validator, model_validator


if TYPE_CHECKING:
    from py_gdelt.models._internal import _RawGFGRecord


__all__ = [
    "Entity",
    "GALRecord",
    "GEGRecord",
    "GEMGRecord",
    "GFGRecord",
    "GGGRecord",
    "GQGRecord",
    "MetaTag",
    "Quote",
]


logger = logging.getLogger(__name__)

# Module-level set to track warned fields (avoid spam)
_warned_fields: set[tuple[str, str]] = set()


class SchemaEvolutionMixin(BaseModel):
    """Mixin that warns about unknown fields from GDELT schema changes.

    This mixin uses model_validator to detect unknown fields and issue warnings
    to help users identify when GDELT adds new fields to their data formats.
    """

    @model_validator(mode="before")
    @classmethod
    def _warn_unknown_fields(cls, data: Any) -> Any:
        """Detect and warn about unknown fields from schema evolution.

        Args:
            data: Raw input data before validation.

        Returns:
            Unmodified data (warnings are side-effects only).
        """
        if not isinstance(data, dict):
            return data

        # Get all known field names (including aliases)
        known_fields = set(cls.model_fields.keys())
        for field_info in cls.model_fields.values():
            if field_info.alias:
                known_fields.add(field_info.alias)

        # Detect unknown fields
        unknown_fields = set(data.keys()) - known_fields

        # Issue warnings for new unknown fields (avoid duplicates)
        for field in unknown_fields:
            warn_key = (cls.__name__, field)
            if warn_key not in _warned_fields:
                _warned_fields.add(warn_key)
                message = (
                    f"GDELT schema change detected: {cls.__name__} has new field "
                    f"'{field}'. Consider updating py-gdelt. Field will be ignored."
                )
                warnings.warn(message, UserWarning, stacklevel=4)
                logger.warning(message)

        return data


class Quote(SchemaEvolutionMixin, BaseModel):
    """Quote extracted from GQG (Global Quotation Graph).

    Represents a single quotation with surrounding context.

    Attributes:
        model_config: Pydantic configuration
        pre: Text before the quote
        quote: The quotation text
        post: Text after the quote
    """

    model_config = {"extra": "ignore"}

    pre: str
    quote: str
    post: str


class GQGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Quotation Graph record.

    Represents a document with extracted quotations and their context.

    Attributes:
        model_config: Pydantic configuration
        date: Publication date/time
        url: Source document URL
        lang: Language code
        quotes: List of extracted quotations with context
    """

    model_config = {"extra": "ignore"}

    date: datetime
    url: str
    lang: str
    quotes: list[Quote] = Field(default_factory=list)

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> datetime:
        """Parse date from ISO or GDELT format.

        Args:
            v: Date string in ISO format (with 'T') or GDELT format (YYYYMMDDHHMMSS).

        Returns:
            Parsed datetime with UTC timezone.

        Raises:
            ValueError: If date format is invalid.
        """
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # ISO format with 'T'
            if "T" in v:
                # Handle ISO format (e.g., "2024-01-20T12:30:45Z")
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            # GDELT format (YYYYMMDDHHMMSS)
            return datetime.strptime(v, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
        msg = f"Invalid date format: {v}"
        raise ValueError(msg)


class Entity(SchemaEvolutionMixin, BaseModel):
    """Entity extracted from GEG (Global Entity Graph).

    Represents a named entity with metadata and knowledge graph links.

    Attributes:
        model_config: Pydantic configuration
        name: Entity name
        entity_type: Entity type
        salience: Salience score
        wikipedia_url: Wikipedia URL if available
        knowledge_graph_mid: Google Knowledge Graph MID if available
    """

    model_config = {"extra": "ignore", "populate_by_name": True}

    name: str
    entity_type: str = Field(alias="type")
    salience: float | None = None
    wikipedia_url: str | None = None
    knowledge_graph_mid: str | None = Field(default=None, alias="mid")


class GEGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Entity Graph record.

    Represents a document with extracted entities and their metadata.

    Attributes:
        model_config: Pydantic configuration
        date: Publication date/time
        url: Source document URL
        lang: Language code
        entities: List of extracted entities
    """

    model_config = {"extra": "ignore", "populate_by_name": True}

    date: datetime
    url: str
    lang: str
    entities: list[Entity] = Field(default_factory=list)

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> datetime:
        """Parse date from ISO or GDELT format.

        Args:
            v: Date string in ISO format (with 'T') or GDELT format (YYYYMMDDHHMMSS).

        Returns:
            Parsed datetime with UTC timezone.

        Raises:
            ValueError: If date format is invalid.
        """
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # ISO format with 'T'
            if "T" in v:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            # GDELT format (YYYYMMDDHHMMSS)
            return datetime.strptime(v, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
        msg = f"Invalid date format: {v}"
        raise ValueError(msg)


class GFGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Frontpage Graph record (TSV format).

    Represents a hyperlink from a frontpage to another URL.

    Attributes:
        model_config: Pydantic configuration
        date: Publication date/time
        from_frontpage_url: Source frontpage URL
        link_url: Destination link URL
        link_text: Anchor text of the link
        page_position: Position of link on page
        lang: Language code
    """

    model_config = {"extra": "ignore"}

    date: datetime
    from_frontpage_url: str
    link_url: str
    link_text: str
    page_position: int
    lang: str

    @classmethod
    def from_raw(cls, raw: _RawGFGRecord) -> Self:
        """Convert internal _RawGFGRecord to public GFGRecord model.

        Args:
            raw: Internal _RawGFGRecord dataclass from TSV parsing.

        Returns:
            Validated GFGRecord with all fields parsed and typed.
        """
        # Parse date from GDELT format (YYYYMMDDHHMMSS)
        date = datetime.strptime(raw.date, "%Y%m%d%H%M%S").replace(tzinfo=UTC)

        # Parse page_position (default to 0 if empty)
        page_position = 0
        if raw.page_position:
            try:
                page_position = int(raw.page_position)
            except ValueError:
                logger.warning("Invalid page_position '%s', defaulting to 0", raw.page_position)

        return cls(
            date=date,
            from_frontpage_url=raw.from_frontpage_url,
            link_url=raw.link_url,
            link_text=raw.link_text,
            page_position=page_position,
            lang=raw.lang,
        )


class GGGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Geographic Graph record.

    Represents a document with an extracted geographic location.

    Attributes:
        model_config: Pydantic configuration
        date: Publication date/time
        url: Source document URL
        location_name: Name of the location
        lat: Latitude
        lon: Longitude
        context: Surrounding text context
    """

    model_config = {"extra": "ignore"}

    date: datetime
    url: str
    location_name: str
    lat: float
    lon: float
    context: str

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> datetime:
        """Parse date from ISO or GDELT format.

        Args:
            v: Date string in ISO format (with 'T') or GDELT format (YYYYMMDDHHMMSS).

        Returns:
            Parsed datetime with UTC timezone.

        Raises:
            ValueError: If date format is invalid.
        """
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # ISO format with 'T'
            if "T" in v:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            # GDELT format (YYYYMMDDHHMMSS)
            return datetime.strptime(v, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
        msg = f"Invalid date format: {v}"
        raise ValueError(msg)


class MetaTag(SchemaEvolutionMixin, BaseModel):
    """Metadata tag extracted from GEMG (Global Embedded Metadata Graph).

    Represents a single metadata tag from HTML meta tags or JSON-LD.

    Attributes:
        model_config: Pydantic configuration
        key: Tag key/name
        tag_type: Tag type
        value: Tag value
    """

    model_config = {"extra": "ignore", "populate_by_name": True}

    key: str
    tag_type: str = Field(alias="type")
    value: str


class GEMGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Embedded Metadata Graph record.

    Represents a document with extracted metadata tags and JSON-LD.

    Attributes:
        model_config: Pydantic configuration
        date: Publication date/time
        url: Source document URL
        title: Document title if available
        lang: Language code
        metatags: List of extracted metadata tags
        jsonld: List of JSON-LD strings
    """

    model_config = {"extra": "ignore", "populate_by_name": True}

    date: datetime
    url: str
    title: str | None = None
    lang: str
    metatags: list[MetaTag] = Field(default_factory=list)
    jsonld: list[str] = Field(default_factory=list)

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> datetime:
        """Parse date from ISO or GDELT format.

        Args:
            v: Date string in ISO format (with 'T') or GDELT format (YYYYMMDDHHMMSS).

        Returns:
            Parsed datetime with UTC timezone.

        Raises:
            ValueError: If date format is invalid.
        """
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # ISO format with 'T'
            if "T" in v:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            # GDELT format (YYYYMMDDHHMMSS)
            return datetime.strptime(v, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
        msg = f"Invalid date format: {v}"
        raise ValueError(msg)


class GALRecord(SchemaEvolutionMixin, BaseModel):
    """Article List record.

    Represents a news article with basic metadata.

    Attributes:
        model_config: Pydantic configuration
        date: Publication date/time
        url: Article URL
        title: Article title if available
        image: Primary image URL if available
        description: Article description if available
        author: Article author if available
        lang: Language code
    """

    model_config = {"extra": "ignore"}

    date: datetime
    url: str
    title: str | None = None
    image: str | None = None
    description: str | None = None
    author: str | None = None
    lang: str

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> datetime:
        """Parse date from ISO or GDELT format.

        Args:
            v: Date string in ISO format (with 'T') or GDELT format (YYYYMMDDHHMMSS).

        Returns:
            Parsed datetime with UTC timezone.

        Raises:
            ValueError: If date format is invalid.
        """
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # ISO format with 'T'
            if "T" in v:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            # GDELT format (YYYYMMDDHHMMSS)
            return datetime.strptime(v, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
        msg = f"Invalid date format: {v}"
        raise ValueError(msg)
