"""Internal dataclasses for high-performance GDELT data parsing.

These dataclasses use slots=True for faster attribute access and reduced memory footprint.
They are used internally during parsing from TAB-delimited files and are converted to
Pydantic models at the API boundary for validation and external use.

All fields are initially strings (as parsed from CSV/TSV), with type conversion
happening during Pydantic model conversion.
"""

from dataclasses import dataclass


__all__ = [
    "_RawEvent",
    "_RawGKG",
    "_RawMention",
    "_RawNGram",
]


@dataclass(slots=True)
class _RawEvent:
    """Internal representation for GDELT Events (v1/v2).

    Represents a single event record from GDELT Events table. This is the core
    data structure capturing who did what to whom, when, where, and how it was reported.

    All fields are strings as parsed from TAB-delimited files. Type conversion to
    int/float/datetime happens when converting to the public Event Pydantic model.

    Note: event_code, event_base_code, event_root_code are kept as strings to preserve
    leading zeros in CAMEO codes (e.g., "010" for "Make statement, not specified").
    """

    # Event identification (required fields)
    global_event_id: str
    sql_date: str
    month_year: str
    year: str
    fraction_date: str

    # Event attributes (required fields)
    is_root_event: str
    event_code: str
    event_base_code: str
    event_root_code: str
    quad_class: str
    goldstein_scale: str
    num_mentions: str
    num_sources: str
    num_articles: str
    avg_tone: str

    # Metadata (required fields)
    date_added: str

    # Actor 1 attributes (optional fields)
    actor1_code: str | None = None
    actor1_name: str | None = None
    actor1_country_code: str | None = None
    actor1_known_group_code: str | None = None
    actor1_ethnic_code: str | None = None
    actor1_religion1_code: str | None = None
    actor1_religion2_code: str | None = None
    actor1_type1_code: str | None = None
    actor1_type2_code: str | None = None
    actor1_type3_code: str | None = None

    # Actor 2 attributes (optional fields)
    actor2_code: str | None = None
    actor2_name: str | None = None
    actor2_country_code: str | None = None
    actor2_known_group_code: str | None = None
    actor2_ethnic_code: str | None = None
    actor2_religion1_code: str | None = None
    actor2_religion2_code: str | None = None
    actor2_type1_code: str | None = None
    actor2_type2_code: str | None = None
    actor2_type3_code: str | None = None

    # Actor1 Geography
    actor1_geo_type: str | None = None
    actor1_geo_fullname: str | None = None
    actor1_geo_country_code: str | None = None
    actor1_geo_adm1_code: str | None = None
    actor1_geo_adm2_code: str | None = None
    actor1_geo_lat: str | None = None
    actor1_geo_lon: str | None = None
    actor1_geo_feature_id: str | None = None

    # Actor2 Geography
    actor2_geo_type: str | None = None
    actor2_geo_fullname: str | None = None
    actor2_geo_country_code: str | None = None
    actor2_geo_adm1_code: str | None = None
    actor2_geo_adm2_code: str | None = None
    actor2_geo_lat: str | None = None
    actor2_geo_lon: str | None = None
    actor2_geo_feature_id: str | None = None

    # Action Geography
    action_geo_type: str | None = None
    action_geo_fullname: str | None = None
    action_geo_country_code: str | None = None
    action_geo_adm1_code: str | None = None
    action_geo_adm2_code: str | None = None
    action_geo_lat: str | None = None
    action_geo_lon: str | None = None
    action_geo_feature_id: str | None = None

    # Metadata (optional fields)
    source_url: str | None = None
    is_translated: bool = False


@dataclass(slots=True)
class _RawMention:
    """Internal representation for GDELT Mentions.

    Represents a single mention of an event in a news article. Each event in the Events
    table can have many mentions across different sources and times.

    All fields are strings as parsed from TAB-delimited files. Type conversion happens
    when converting to the public Mention Pydantic model.
    """

    # Event link
    global_event_id: str

    # Timing
    event_time_date: str
    event_time_full: str
    mention_time_date: str
    mention_time_full: str

    # Source information
    mention_type: str
    mention_source_name: str
    mention_identifier: str

    # Document position
    sentence_id: str
    actor1_char_offset: str
    actor2_char_offset: str
    action_char_offset: str
    in_raw_text: str

    # Confidence and tone
    confidence: str
    mention_doc_length: str
    mention_doc_tone: str

    # Optional fields
    mention_doc_translation_info: str | None = None
    extras: str | None = None


@dataclass(slots=True)
class _RawGKG:
    """Internal representation for GDELT GKG (Global Knowledge Graph) v2.1.

    Represents a single GKG record containing enriched content analysis including
    themes, people, organizations, locations, counts, and tone extracted from a
    news article or document.

    All fields are strings as parsed from TAB-delimited files. Complex fields
    (counts, themes, locations, etc.) are semicolon-delimited strings that will
    be parsed into structured objects during Pydantic model conversion.
    """

    # Record identification
    gkg_record_id: str
    date: str
    source_collection_id: str
    source_common_name: str
    document_identifier: str

    # Counts
    counts_v1: str
    counts_v2: str

    # Themes
    themes_v1: str
    themes_v2_enhanced: str

    # Locations
    locations_v1: str
    locations_v2_enhanced: str

    # Named entities
    persons_v1: str
    persons_v2_enhanced: str
    organizations_v1: str
    organizations_v2_enhanced: str

    # Tone and temporal
    tone: str
    dates_v2: str
    gcam: str

    # Media and social
    sharing_image: str | None = None
    related_images: str | None = None
    social_image_embeds: str | None = None
    social_video_embeds: str | None = None

    # Text analysis
    quotations: str | None = None
    all_names: str | None = None
    amounts: str | None = None

    # Metadata
    translation_info: str | None = None
    extras_xml: str | None = None
    is_translated: bool = False


@dataclass(slots=True)
class _RawNGram:
    """Internal representation for GDELT NGrams 3.0.

    Represents a single n-gram (word or phrase) occurrence in a news article,
    with contextual information about where it appeared and what surrounded it.

    All fields are strings as parsed from TAB-delimited files. Type conversion
    happens when converting to the public NGram Pydantic model.
    """

    date: str
    ngram: str
    language: str
    segment_type: str
    position: str
    pre_context: str
    post_context: str
    url: str
