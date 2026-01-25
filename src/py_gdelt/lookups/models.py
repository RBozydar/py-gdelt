"""
Pydantic models for GDELT lookup data structures.

This module provides type-safe models for all lookup data used throughout the
py-gdelt library, including CAMEO codes, Goldstein scale values, countries,
and GKG themes.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


__all__ = [
    "CAMEOCodeEntry",
    "CountryEntry",
    "GCAMEntry",
    "GKGThemeEntry",
    "GoldsteinEntry",
    "LanguageEntry",
    "TagCountEntry",
]


class CAMEOCodeEntry(BaseModel):
    """
    CAMEO event code entry with full metadata.

    Attributes:
        name: Short name of the CAMEO code
        description: Detailed description of what the code represents
        usage_notes: Optional notes about when and how to use this code
        examples: Tuple of real-world example scenarios for this code
        parent: Parent code in the CAMEO hierarchy (e.g., "01" for "011")
        quad_class: Quad class classification (1-4)
        root: Whether this is a root-level code
    """

    model_config = {"frozen": True}

    name: str
    description: str
    usage_notes: str | None = None
    examples: tuple[str, ...] = ()
    parent: str | None = None
    quad_class: int
    root: bool = False


class GoldsteinEntry(BaseModel):
    """
    Goldstein scale entry for a CAMEO code.

    The Goldstein scale provides a numerical score indicating the theoretical
    potential impact of an event type on the stability of a country. Values
    range from -10 (most destabilizing/conflictual) to +10 (most
    stabilizing/cooperative).

    Attributes:
        value: Goldstein scale score (-10 to +10)
        description: Description of the CAMEO code this value applies to
    """

    model_config = {"frozen": True}

    value: float
    description: str


class CountryEntry(BaseModel):
    """
    Country code mapping with ISO standards and regional classification.

    Attributes:
        iso3: ISO 3166-1 alpha-3 country code (e.g., "USA")
        iso2: ISO 3166-1 alpha-2 country code (e.g., "US")
        name: Common country name
        full_name: Official full country name
        region: Geographic or political region classification
    """

    model_config = {"frozen": True}

    iso3: str
    iso2: str
    name: str
    full_name: str | None = None
    region: str


class GKGThemeEntry(BaseModel):
    """
    GKG (Global Knowledge Graph) theme taxonomy entry.

    GKG themes are used to categorize and tag content in GDELT's Global
    Knowledge Graph based on topical and thematic analysis.

    Attributes:
        category: Theme category or classification.
        description: Detailed description of what this theme represents.
        count: Usage frequency count across GDELT corpus.
    """

    model_config = {"frozen": True}

    category: str
    description: str
    count: int


class TagCountEntry(BaseModel):
    """Tag entry with usage frequency count.

    Used for both Cloud Vision API image tags and crowdsourced web tags.

    Attributes:
        tag: The tag label text.
        count: Usage frequency count.
    """

    model_config = {"frozen": True}

    tag: str
    count: int


class LanguageEntry(BaseModel):
    """Supported language code for GDELT DOC/GEO APIs.

    Attributes:
        code: ISO 639-3 language code (e.g., "eng", "spa", "zho").
        name: Human-readable language name.
    """

    model_config = {"frozen": True}

    code: str
    name: str


class GCAMEntry(BaseModel):
    """GCAM (Global Content Analysis Measures) dimension entry.

    Attributes:
        variable: Full variable code (e.g., "c2.14", "v42.2").
        dictionary_id: Numeric dictionary identifier.
        dimension_id: Numeric dimension within dictionary.
        data_type: Either "WORDCOUNT" or "SCOREDVALUE".
        language: ISO 639-3 language code.
        dictionary_name: Human-readable dictionary name.
        dimension_name: Human-readable dimension name.
    """

    model_config = {"frozen": True}

    variable: str
    dictionary_id: int
    dimension_id: int
    data_type: Literal["WORDCOUNT", "SCOREDVALUE"]
    language: str
    dictionary_name: str
    dimension_name: str
