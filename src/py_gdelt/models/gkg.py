"""Public Pydantic models for GDELT GKG (Global Knowledge Graph) data."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from py_gdelt.models.common import EntityMention, Location, ToneScores


if TYPE_CHECKING:
    from py_gdelt.models._internal import _RawGKG


__all__ = [
    "Amount",
    "GKGRecord",
    "Quotation",
]


logger = logging.getLogger(__name__)


class Quotation(BaseModel):
    """Quote extracted from a GKG document."""

    offset: int
    length: int
    verb: str
    quote: str


class Amount(BaseModel):
    """Numerical amount extracted from a GKG document."""

    amount: float
    object: str
    offset: int


class GKGRecord(BaseModel):
    """GDELT Global Knowledge Graph record.

    Represents enriched content analysis of a news article or document, including
    extracted themes, entities, locations, tone, and other metadata.

    Attributes:
        record_id: Unique identifier in format "YYYYMMDDHHMMSS-seq" or with "-T" suffix for translated
        date: Publication date/time
        source_url: URL of the source document
        source_name: Common name of the source
        source_collection: Source collection identifier (1=WEB, 2=Citation, etc.)
        themes: Extracted themes/topics
        persons: Extracted person names
        organizations: Extracted organization names
        locations: Extracted geographic locations
        tone: Document tone analysis scores
        gcam: GCAM emotional dimension scores as dict
        quotations: Extracted quotations (v2.1+ only)
        amounts: Extracted numerical amounts (v2.1+ only)
        sharing_image: Primary sharing image URL if any
        all_names: All extracted names as flat list
        version: GDELT version (1 or 2)
        is_translated: Whether this is a translated document
        original_record_id: Original record ID if translated
        translation_info: Translation metadata string
    """

    # Identifiers
    record_id: str
    date: datetime
    source_url: str
    source_name: str
    source_collection: int

    # Extracted entities
    themes: list[EntityMention] = Field(default_factory=list)
    persons: list[EntityMention] = Field(default_factory=list)
    organizations: list[EntityMention] = Field(default_factory=list)
    locations: list[Location] = Field(default_factory=list)

    # Tone
    tone: ToneScores | None = None

    # GCAM emotional dimensions
    gcam: dict[str, float] = Field(default_factory=dict)

    # V2.1+ fields
    quotations: list[Quotation] = Field(default_factory=list)
    amounts: list[Amount] = Field(default_factory=list)

    # Extra fields
    sharing_image: str | None = None
    all_names: list[str] = Field(default_factory=list)

    # Metadata
    version: int = 2
    is_translated: bool = False
    original_record_id: str | None = None
    translation_info: str | None = None

    @classmethod
    def from_raw(cls, raw: _RawGKG) -> GKGRecord:
        """Convert internal _RawGKG to public GKGRecord model.

        This method handles parsing the complex delimited fields from GKG v2.1 format:
        - Themes: semicolon-delimited "theme,offset" pairs
        - GCAM: semicolon-delimited "key:value" pairs
        - Quotations: pipe-delimited records with format "offset#length#verb#quote"
        - Amounts: semicolon-delimited "amount,object,offset" triples
        - Locations: semicolon-delimited with multiple sub-fields
        - Tone: comma-separated values

        Args:
            raw: Internal _RawGKG dataclass from TSV parsing

        Returns:
            Validated GKGRecord with all fields parsed and typed
        """
        # Detect translation
        is_translated = raw.gkg_record_id.endswith("-T")
        original_record_id = None
        if is_translated:
            original_record_id = raw.gkg_record_id[:-2]

        # Parse date (format: YYYYMMDDHHMMSS)
        date_str = raw.date
        date = datetime.strptime(date_str, "%Y%m%d%H%M%S").replace(tzinfo=UTC)

        # Parse themes from V2 enhanced (preferred) or V1
        themes = _parse_themes(raw.themes_v2_enhanced or raw.themes_v1)

        # Parse persons
        persons = _parse_entities(raw.persons_v2_enhanced or raw.persons_v1, entity_type="PERSON")

        # Parse organizations
        organizations = _parse_entities(
            raw.organizations_v2_enhanced or raw.organizations_v1,
            entity_type="ORG",
        )

        # Parse locations
        locations = _parse_locations(raw.locations_v2_enhanced or raw.locations_v1)

        # Parse tone
        tone = _parse_tone(raw.tone) if raw.tone else None

        # Parse GCAM
        gcam = _parse_gcam(raw.gcam) if raw.gcam else {}

        # Parse quotations (v2.1+)
        quotations = _parse_quotations(raw.quotations) if raw.quotations else []

        # Parse amounts (v2.1+)
        amounts = _parse_amounts(raw.amounts) if raw.amounts else []

        # Parse all_names
        all_names = (
            [name.strip() for name in raw.all_names.split(";") if name.strip()]
            if raw.all_names
            else []
        )

        # Determine version (if v2 enhanced fields exist, it's v2)
        version = 2 if raw.themes_v2_enhanced else 1

        return cls(
            record_id=raw.gkg_record_id,
            date=date,
            source_url=raw.document_identifier,
            source_name=raw.source_common_name,
            source_collection=int(raw.source_collection_id),
            themes=themes,
            persons=persons,
            organizations=organizations,
            locations=locations,
            tone=tone,
            gcam=gcam,
            quotations=quotations,
            amounts=amounts,
            sharing_image=raw.sharing_image,
            all_names=all_names,
            version=version,
            is_translated=is_translated,
            original_record_id=original_record_id,
            translation_info=raw.translation_info,
        )

    @property
    def primary_theme(self) -> str | None:
        """Get the first/primary theme if any.

        Returns:
            The name of the first theme, or None if no themes exist
        """
        if not self.themes:
            return None
        return self.themes[0].name

    @property
    def has_quotations(self) -> bool:
        """Check if record has extracted quotations.

        Returns:
            True if one or more quotations were extracted
        """
        return len(self.quotations) > 0


def _parse_themes(themes_str: str) -> list[EntityMention]:
    """Parse themes from semicolon-delimited 'theme,offset' pairs.

    Args:
        themes_str: Semicolon-delimited string like "THEME1,123;THEME2,456"

    Returns:
        List of EntityMention objects with entity_type="THEME"
    """
    if not themes_str:
        return []

    result: list[EntityMention] = []
    for theme_pair in themes_str.split(";"):
        if not theme_pair.strip():
            continue

        parts = theme_pair.split(",")
        if len(parts) >= 1:
            name = parts[0].strip()
            offset = None
            if len(parts) >= 2:
                try:
                    offset = int(parts[1])
                except ValueError:
                    logger.warning("Invalid offset in theme: %s", theme_pair)

            result.append(EntityMention(entity_type="THEME", name=name, offset=offset))

    return result


def _parse_entities(entities_str: str, entity_type: str) -> list[EntityMention]:
    """Parse entities from semicolon-delimited 'entity,offset' pairs.

    Args:
        entities_str: Semicolon-delimited string like "John Doe,123;Jane Smith,456"
        entity_type: Type of entity (e.g., "PERSON", "ORG")

    Returns:
        List of EntityMention objects
    """
    if not entities_str:
        return []

    result: list[EntityMention] = []
    for entity_pair in entities_str.split(";"):
        if not entity_pair.strip():
            continue

        parts = entity_pair.split(",")
        if len(parts) >= 1:
            name = parts[0].strip()
            offset = None
            if len(parts) >= 2:
                try:
                    offset = int(parts[1])
                except ValueError:
                    logger.warning("Invalid offset in entity: %s", entity_pair)

            result.append(EntityMention(entity_type=entity_type, name=name, offset=offset))

    return result


def _parse_locations(locations_str: str) -> list[Location]:
    """Parse locations from semicolon-delimited location records.

    Each location record has format: geo_type#name#country_code#adm1#adm2#lat#lon#feature_id

    Args:
        locations_str: Semicolon-delimited location records

    Returns:
        List of Location objects
    """
    if not locations_str:
        return []

    result: list[Location] = []
    for loc_record in locations_str.split(";"):
        if not loc_record.strip():
            continue

        parts = loc_record.split("#")
        if len(parts) < 8:
            logger.warning("Incomplete location record: %s", loc_record)
            continue

        try:
            geo_type = int(parts[0]) if parts[0] else None
        except ValueError:
            geo_type = None

        name = parts[1] if parts[1] else None
        country_code = parts[2] if parts[2] else None
        adm1_code = parts[3] if parts[3] else None
        adm2_code = parts[4] if parts[4] else None

        try:
            lat = float(parts[5]) if parts[5] else None
        except ValueError:
            lat = None

        try:
            lon = float(parts[6]) if parts[6] else None
        except ValueError:
            lon = None

        feature_id = parts[7] if parts[7] else None

        result.append(
            Location(
                geo_type=geo_type,
                name=name,
                country_code=country_code,
                adm1_code=adm1_code,
                adm2_code=adm2_code,
                lat=lat,
                lon=lon,
                feature_id=feature_id,
            ),
        )

    return result


def _parse_tone(tone_str: str) -> ToneScores | None:
    """Parse tone from comma-separated values.

    Format: tone,positive_score,negative_score,polarity,activity_ref_density,self_group_ref_density,word_count

    Args:
        tone_str: Comma-separated tone values

    Returns:
        ToneScores object or None if parsing fails
    """
    if not tone_str:
        return None

    parts = tone_str.split(",")
    if len(parts) < 6:
        logger.warning("Incomplete tone record: %s", tone_str)
        return None

    try:
        tone = float(parts[0])
        positive_score = float(parts[1])
        negative_score = float(parts[2])
        polarity = float(parts[3])
        activity_reference_density = float(parts[4])
        self_group_reference_density = float(parts[5])
        word_count = int(parts[6]) if len(parts) > 6 and parts[6] else None

        return ToneScores(
            tone=tone,
            positive_score=positive_score,
            negative_score=negative_score,
            polarity=polarity,
            activity_reference_density=activity_reference_density,
            self_group_reference_density=self_group_reference_density,
            word_count=word_count,
        )
    except (ValueError, IndexError) as e:
        logger.warning("Failed to parse tone '%s': %s", tone_str, e)
        return None


def _parse_gcam(gcam_str: str) -> dict[str, float]:
    """Parse GCAM from semicolon-delimited 'key:value' pairs.

    Args:
        gcam_str: Semicolon-delimited string like "c2.14:3.2;c5.1:0.85"

    Returns:
        Dict mapping GCAM dimension codes to scores
    """
    if not gcam_str:
        return {}

    result: dict[str, float] = {}
    for pair in gcam_str.split(";"):
        if not pair.strip():
            continue

        parts = pair.split(":")
        if len(parts) == 2:
            key = parts[0].strip()
            try:
                value = float(parts[1])
                result[key] = value
            except ValueError:
                logger.warning("Invalid GCAM value in pair: %s", pair)

    return result


def _parse_quotations(quotations_str: str) -> list[Quotation]:
    """Parse quotations from pipe-delimited records.

    Each record has format: offset#length#verb#quote

    Args:
        quotations_str: Pipe-delimited quotation records

    Returns:
        List of Quotation objects
    """
    if not quotations_str:
        return []

    result: list[Quotation] = []
    for quote_record in quotations_str.split("|"):
        if not quote_record.strip():
            continue

        parts = quote_record.split("#", 3)  # Split into max 4 parts
        if len(parts) < 4:
            logger.warning("Incomplete quotation record: %s", quote_record)
            continue

        try:
            offset = int(parts[0])
            length = int(parts[1])
            verb = parts[2]
            quote = parts[3]

            result.append(Quotation(offset=offset, length=length, verb=verb, quote=quote))
        except ValueError as e:
            logger.warning("Failed to parse quotation '%s': %s", quote_record, e)

    return result


def _parse_amounts(amounts_str: str) -> list[Amount]:
    """Parse amounts from semicolon-delimited 'amount,object,offset' triples.

    Args:
        amounts_str: Semicolon-delimited string like "100,dollars,50;25,people,120"

    Returns:
        List of Amount objects
    """
    if not amounts_str:
        return []

    result: list[Amount] = []
    for amount_triple in amounts_str.split(";"):
        if not amount_triple.strip():
            continue

        parts = amount_triple.split(",")
        if len(parts) < 3:
            logger.warning("Incomplete amount record: %s", amount_triple)
            continue

        try:
            amount = float(parts[0])
            obj = parts[1]
            offset = int(parts[2])

            result.append(Amount(amount=amount, object=obj, offset=offset))
        except ValueError as e:
            logger.warning("Failed to parse amount '%s': %s", amount_triple, e)

    return result
