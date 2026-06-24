"""Optional-free BigQuery row conversion helpers.

These helpers translate BigQuery row dictionaries into the internal raw
dataclasses used by file parsers. They intentionally avoid importing the
Google SDK so file-based code can reuse them without requiring the BigQuery
optional dependency.
"""

from __future__ import annotations

from dataclasses import MISSING, fields
from typing import Any, Final

from py_gdelt.models._internal import _RawEvent, _RawGKG, _RawMention


# BigQuery column -> _Raw* field mappings.
_BQ_EVENT_MAP: Final[dict[str, str]] = {
    "GLOBALEVENTID": "global_event_id",
    "SQLDATE": "sql_date",
    "MonthYear": "month_year",
    "Year": "year",
    "FractionDate": "fraction_date",
    "Actor1Code": "actor1_code",
    "Actor1Name": "actor1_name",
    "Actor1CountryCode": "actor1_country_code",
    "Actor1KnownGroupCode": "actor1_known_group_code",
    "Actor1EthnicCode": "actor1_ethnic_code",
    "Actor1Religion1Code": "actor1_religion1_code",
    "Actor1Religion2Code": "actor1_religion2_code",
    "Actor1Type1Code": "actor1_type1_code",
    "Actor1Type2Code": "actor1_type2_code",
    "Actor1Type3Code": "actor1_type3_code",
    "Actor2Code": "actor2_code",
    "Actor2Name": "actor2_name",
    "Actor2CountryCode": "actor2_country_code",
    "Actor2KnownGroupCode": "actor2_known_group_code",
    "Actor2EthnicCode": "actor2_ethnic_code",
    "Actor2Religion1Code": "actor2_religion1_code",
    "Actor2Religion2Code": "actor2_religion2_code",
    "Actor2Type1Code": "actor2_type1_code",
    "Actor2Type2Code": "actor2_type2_code",
    "Actor2Type3Code": "actor2_type3_code",
    "IsRootEvent": "is_root_event",
    "EventCode": "event_code",
    "EventBaseCode": "event_base_code",
    "EventRootCode": "event_root_code",
    "QuadClass": "quad_class",
    "GoldsteinScale": "goldstein_scale",
    "NumMentions": "num_mentions",
    "NumSources": "num_sources",
    "NumArticles": "num_articles",
    "AvgTone": "avg_tone",
    "Actor1Geo_Type": "actor1_geo_type",
    "Actor1Geo_FullName": "actor1_geo_fullname",
    "Actor1Geo_CountryCode": "actor1_geo_country_code",
    "Actor1Geo_ADM1Code": "actor1_geo_adm1_code",
    "Actor1Geo_ADM2Code": "actor1_geo_adm2_code",
    "Actor1Geo_Lat": "actor1_geo_lat",
    "Actor1Geo_Long": "actor1_geo_lon",
    "Actor1Geo_FeatureID": "actor1_geo_feature_id",
    "Actor2Geo_Type": "actor2_geo_type",
    "Actor2Geo_FullName": "actor2_geo_fullname",
    "Actor2Geo_CountryCode": "actor2_geo_country_code",
    "Actor2Geo_ADM1Code": "actor2_geo_adm1_code",
    "Actor2Geo_ADM2Code": "actor2_geo_adm2_code",
    "Actor2Geo_Lat": "actor2_geo_lat",
    "Actor2Geo_Long": "actor2_geo_lon",
    "Actor2Geo_FeatureID": "actor2_geo_feature_id",
    "ActionGeo_Type": "action_geo_type",
    "ActionGeo_FullName": "action_geo_fullname",
    "ActionGeo_CountryCode": "action_geo_country_code",
    "ActionGeo_ADM1Code": "action_geo_adm1_code",
    "ActionGeo_ADM2Code": "action_geo_adm2_code",
    "ActionGeo_Lat": "action_geo_lat",
    "ActionGeo_Long": "action_geo_lon",
    "ActionGeo_FeatureID": "action_geo_feature_id",
    "DATEADDED": "date_added",
    "SOURCEURL": "source_url",
}

_BQ_GKG_MAP: Final[dict[str, str]] = {
    "GKGRECORDID": "gkg_record_id",
    "DATE": "date",
    "SourceCollectionIdentifier": "source_collection_id",
    "SourceCommonName": "source_common_name",
    "DocumentIdentifier": "document_identifier",
    "Counts": "counts_v1",
    "V2Counts": "counts_v2",
    "Themes": "themes_v1",
    "V2Themes": "themes_v2_enhanced",
    "Locations": "locations_v1",
    "V2Locations": "locations_v2_enhanced",
    "Persons": "persons_v1",
    "V2Persons": "persons_v2_enhanced",
    "Organizations": "organizations_v1",
    "V2Organizations": "organizations_v2_enhanced",
    "V2Tone": "tone",
    "Dates": "dates_v2",
    "GCAM": "gcam",
    "SharingImage": "sharing_image",
    "RelatedImages": "related_images",
    "SocialImageEmbeds": "social_image_embeds",
    "SocialVideoEmbeds": "social_video_embeds",
    "Quotations": "quotations",
    "AllNames": "all_names",
    "Amounts": "amounts",
    "TranslationInfo": "translation_info",
    "Extras": "extras_xml",
}

_BQ_MENTION_MAP: Final[dict[str, str]] = {
    "GLOBALEVENTID": "global_event_id",
    "EventTimeDate": "event_time_date",
    "MentionTimeDate": "mention_time_date",
    "MentionType": "mention_type",
    "MentionSourceName": "mention_source_name",
    "MentionIdentifier": "mention_identifier",
    "SentenceID": "sentence_id",
    "Actor1CharOffset": "actor1_char_offset",
    "Actor2CharOffset": "actor2_char_offset",
    "ActionCharOffset": "action_char_offset",
    "InRawText": "in_raw_text",
    "Confidence": "confidence",
    "MentionDocLen": "mention_doc_length",
    "MentionDocTone": "mention_doc_tone",
    "MentionDocTranslationInfo": "mention_doc_translation_info",
    "Extras": "extras",
}


def _required_raw_field_names(
    raw_model: type[_RawEvent] | type[_RawGKG] | type[_RawMention],
) -> frozenset[str]:
    """Return dataclass fields that must be populated with strings."""
    return frozenset(
        field.name
        for field in fields(raw_model)
        if field.default is MISSING and field.default_factory is MISSING
    )


# Required fields (str, not str | None) on each _Raw* dataclass.
_RAW_EVENT_REQUIRED: Final[frozenset[str]] = _required_raw_field_names(_RawEvent)
_RAW_GKG_REQUIRED: Final[frozenset[str]] = _required_raw_field_names(_RawGKG)
_RAW_MENTION_REQUIRED: Final[frozenset[str]] = _required_raw_field_names(_RawMention)


def _bq_row_to_raw_event(row: dict[str, Any]) -> _RawEvent:
    """Convert a BigQuery row dict to a ``_RawEvent`` dataclass.

    Args:
        row: BigQuery result row as a dictionary with BigQuery column keys.

    Returns:
        Populated raw event dataclass ready for ``Event.from_raw()``.
    """
    kwargs: dict[str, Any] = {}
    for bq_col, raw_field in _BQ_EVENT_MAP.items():
        value = row.get(bq_col)
        if value is None and raw_field in _RAW_EVENT_REQUIRED:
            kwargs[raw_field] = ""
        elif value is None:
            kwargs[raw_field] = None
        else:
            kwargs[raw_field] = str(value)
    return _RawEvent(**kwargs)


def _bq_row_to_raw_gkg(row: dict[str, Any]) -> _RawGKG:
    """Convert a BigQuery row dict to a ``_RawGKG`` dataclass.

    Args:
        row: BigQuery result row as a dictionary with BigQuery column keys.

    Returns:
        Populated raw GKG dataclass ready for ``GKGRecord.from_raw()``.
    """
    kwargs: dict[str, Any] = {}
    for bq_col, raw_field in _BQ_GKG_MAP.items():
        value = row.get(bq_col)
        if value is None and raw_field in _RAW_GKG_REQUIRED:
            kwargs[raw_field] = ""
        elif value is None:
            kwargs[raw_field] = None
        else:
            kwargs[raw_field] = str(value)
    return _RawGKG(**kwargs)


def _bq_row_to_raw_mention(row: dict[str, Any]) -> _RawMention:
    """Convert a BigQuery row dict to a ``_RawMention`` dataclass.

    Args:
        row: BigQuery result row as a dictionary with BigQuery column keys.

    Returns:
        Populated raw mention dataclass ready for ``Mention.from_raw()``.
    """
    kwargs: dict[str, Any] = {}
    for bq_col, raw_field in _BQ_MENTION_MAP.items():
        value = row.get(bq_col)
        if value is None and raw_field in _RAW_MENTION_REQUIRED:
            kwargs[raw_field] = ""
        elif value is None:
            kwargs[raw_field] = None
        else:
            kwargs[raw_field] = str(value)

    kwargs["event_time_full"] = kwargs["event_time_date"]
    kwargs["mention_time_full"] = kwargs["mention_time_date"]

    return _RawMention(**kwargs)
