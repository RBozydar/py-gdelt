"""BigQuery data source for GDELT Python client.

This module provides BigQuery access as a fallback when REST APIs fail or rate limit.
It uses Google Cloud BigQuery to query GDELT's public datasets with:

- **Security-first design**: All queries use parameterized queries (NO string formatting)
- **Cost awareness**: Only queries _partitioned tables with mandatory date filters
- **Column allowlisting**: All column names validated against explicit allowlists
- **Credential validation**: Paths validated, credentials never logged
- **Async interface**: Wraps sync BigQuery client using run_in_executor
- **Streaming results**: Memory-efficient iteration over large result sets

Security Features:
- Parameterized queries prevent SQL injection
- Column allowlists prevent unauthorized data access
- Path validation prevents directory traversal attacks
- Credentials validated on first use, never logged or exposed
- Partition filters required to prevent accidental full table scans
"""

import asyncio
import logging
import re
from collections.abc import AsyncIterator
from datetime import datetime
from pathlib import Path
from typing import Any, Final, Literal, NamedTuple

from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError
from google.oauth2 import service_account

from py_gdelt.config import GDELTSettings
from py_gdelt.exceptions import BigQueryError, ConfigurationError, SecurityError
from py_gdelt.filters import DateRange, EventFilter, GKGFilter
from py_gdelt.models._internal import _RawEvent, _RawGKG, _RawMention
from py_gdelt.sources.aggregation import (
    _ALIAS_PATTERN,
    GKG_UNNEST_CONFIG,
    AggFunc,
    Aggregation,
    AggregationResult,
    GKGUnnestField,
)


__all__ = ["BigQuerySource", "TableType"]

logger = logging.getLogger(__name__)

# GDELT BigQuery dataset and table names
GDELT_PROJECT: Final[str] = "gdelt-bq"
GDELT_DATASET_V2: Final[str] = "gdeltv2"

# Table type literal
TableType = Literal["events", "eventmentions", "gkg"]

# Table names (only partitioned tables for cost control)
TABLES: Final[dict[TableType, str]] = {
    "events": f"{GDELT_PROJECT}.{GDELT_DATASET_V2}.events_partitioned",
    "eventmentions": f"{GDELT_PROJECT}.{GDELT_DATASET_V2}.eventmentions_partitioned",
    "gkg": f"{GDELT_PROJECT}.{GDELT_DATASET_V2}.gkg_partitioned",
}

# Column allowlists for each table type (prevents unauthorized column access)
# Only commonly used columns are included to minimize data transfer costs
ALLOWED_COLUMNS: Final[dict[TableType, frozenset[str]]] = {
    "events": frozenset(
        {
            "GLOBALEVENTID",
            "SQLDATE",
            "MonthYear",
            "Year",
            "FractionDate",
            "Actor1Code",
            "Actor1Name",
            "Actor1CountryCode",
            "Actor1KnownGroupCode",
            "Actor1EthnicCode",
            "Actor1Religion1Code",
            "Actor1Religion2Code",
            "Actor1Type1Code",
            "Actor1Type2Code",
            "Actor1Type3Code",
            "Actor2Code",
            "Actor2Name",
            "Actor2CountryCode",
            "Actor2KnownGroupCode",
            "Actor2EthnicCode",
            "Actor2Religion1Code",
            "Actor2Religion2Code",
            "Actor2Type1Code",
            "Actor2Type2Code",
            "Actor2Type3Code",
            "IsRootEvent",
            "EventCode",
            "EventBaseCode",
            "EventRootCode",
            "QuadClass",
            "GoldsteinScale",
            "NumMentions",
            "NumSources",
            "NumArticles",
            "AvgTone",
            "Actor1Geo_Type",
            "Actor1Geo_FullName",
            "Actor1Geo_CountryCode",
            "Actor1Geo_ADM1Code",
            "Actor1Geo_ADM2Code",
            "Actor1Geo_Lat",
            "Actor1Geo_Long",
            "Actor1Geo_FeatureID",
            "Actor2Geo_Type",
            "Actor2Geo_FullName",
            "Actor2Geo_CountryCode",
            "Actor2Geo_ADM1Code",
            "Actor2Geo_ADM2Code",
            "Actor2Geo_Lat",
            "Actor2Geo_Long",
            "Actor2Geo_FeatureID",
            "ActionGeo_Type",
            "ActionGeo_FullName",
            "ActionGeo_CountryCode",
            "ActionGeo_ADM1Code",
            "ActionGeo_ADM2Code",
            "ActionGeo_Lat",
            "ActionGeo_Long",
            "ActionGeo_FeatureID",
            "DATEADDED",
            "SOURCEURL",
        },
    ),
    "eventmentions": frozenset(
        {
            "GLOBALEVENTID",
            "EventTimeDate",
            "MentionTimeDate",
            "MentionType",
            "MentionSourceName",
            "MentionIdentifier",
            "SentenceID",
            "Actor1CharOffset",
            "Actor2CharOffset",
            "ActionCharOffset",
            "InRawText",
            "Confidence",
            "MentionDocLen",
            "MentionDocTone",
            "MentionDocTranslationInfo",
            "Extras",
        },
    ),
    "gkg": frozenset(
        {
            "GKGRECORDID",
            "DATE",
            "SourceCollectionIdentifier",
            "SourceCommonName",
            "DocumentIdentifier",
            "Counts",
            "V2Counts",
            "Themes",
            "V2Themes",
            "Locations",
            "V2Locations",
            "Persons",
            "V2Persons",
            "Organizations",
            "V2Organizations",
            "V2Tone",
            "Dates",
            "GCAM",
            "SharingImage",
            "RelatedImages",
            "SocialImageEmbeds",
            "SocialVideoEmbeds",
            "Quotations",
            "AllNames",
            "Amounts",
            "TranslationInfo",
            "Extras",
        },
    ),
}

# ── BigQuery column → _Raw* field mappings ──────────────────────────────────
#
# BigQuery returns dicts with PascalCase keys (SQLDATE, Actor1Code, etc.) but
# the _Raw* dataclasses use snake_case attribute names. These maps bridge
# that gap. Each map's keys are EXACTLY the ALLOWED_COLUMNS frozenset for the
# corresponding table.

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

# Required fields (str, not str | None) on each _Raw* dataclass.
# When BQ returns None for these, we substitute empty string to avoid
# TypeError on the slots-based dataclass constructor.
_RAW_EVENT_REQUIRED: Final[frozenset[str]] = frozenset(
    {
        "global_event_id",
        "sql_date",
        "month_year",
        "year",
        "fraction_date",
        "is_root_event",
        "event_code",
        "event_base_code",
        "event_root_code",
        "quad_class",
        "goldstein_scale",
        "num_mentions",
        "num_sources",
        "num_articles",
        "avg_tone",
        "date_added",
    },
)

_RAW_GKG_REQUIRED: Final[frozenset[str]] = frozenset(
    {
        "gkg_record_id",
        "date",
        "source_collection_id",
        "source_common_name",
        "document_identifier",
        "counts_v1",
        "counts_v2",
        "themes_v1",
        "themes_v2_enhanced",
        "locations_v1",
        "locations_v2_enhanced",
        "persons_v1",
        "persons_v2_enhanced",
        "organizations_v1",
        "organizations_v2_enhanced",
        "tone",
        "dates_v2",
        "gcam",
    },
)

_RAW_MENTION_REQUIRED: Final[frozenset[str]] = frozenset(
    {
        "global_event_id",
        "event_time_date",
        "event_time_full",
        "mention_time_date",
        "mention_time_full",
        "mention_type",
        "mention_source_name",
        "mention_identifier",
        "sentence_id",
        "actor1_char_offset",
        "actor2_char_offset",
        "action_char_offset",
        "in_raw_text",
        "confidence",
        "mention_doc_length",
        "mention_doc_tone",
    },
)


def _bq_row_to_raw_event(row: dict[str, Any]) -> _RawEvent:
    """Convert a BigQuery row dict to a ``_RawEvent`` dataclass.

    Only mapped columns are passed through; unmapped keys are silently
    dropped so that ``slots=True`` dataclasses never receive unexpected
    keyword arguments.

    Args:
        row: BigQuery result row as a dictionary (PascalCase keys).

    Returns:
        _RawEvent: Populated dataclass ready for ``Event.from_raw()``.
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

    Only mapped columns are passed through; unmapped keys are silently
    dropped so that ``slots=True`` dataclasses never receive unexpected
    keyword arguments.

    Args:
        row: BigQuery result row as a dictionary (PascalCase keys).

    Returns:
        _RawGKG: Populated dataclass ready for ``GKGRecord.from_raw()``.
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

    BigQuery's ``eventmentions`` table does **not** contain the
    ``EventTimeFullDate`` or ``MentionTimeFullDate`` columns that the
    file-based parser produces. These fields (``event_time_full`` and
    ``mention_time_full``) are set to empty string by default.

    Only mapped columns are passed through; unmapped keys are silently
    dropped so that ``slots=True`` dataclasses never receive unexpected
    keyword arguments.

    Args:
        row: BigQuery result row as a dictionary (PascalCase keys).

    Returns:
        _RawMention: Populated dataclass ready for ``Mention.from_raw()``.
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

    # BQ eventmentions table lacks these columns; set required defaults
    kwargs["event_time_full"] = ""
    kwargs["mention_time_full"] = ""

    return _RawMention(**kwargs)


def _validate_credential_path(path: str) -> Path:
    """Validate credential file path and prevent directory traversal.

    Args:
        path: Path to credentials file

    Returns:
        Validated Path object

    Raises:
        SecurityError: If path is invalid or contains traversal attempts
        ConfigurationError: If file does not exist
    """
    # Check for null bytes
    if "\x00" in path:
        logger.error("Null byte detected in credential path")
        msg = "Invalid credential path: null byte detected"
        raise SecurityError(msg)

    # Convert to Path and resolve
    try:
        cred_path = Path(path).expanduser().resolve()
    except (OSError, RuntimeError) as e:
        logger.error("Failed to resolve credential path %s: %s", path, e)  # noqa: TRY400
        msg = f"Invalid credential path: {e}"
        raise SecurityError(msg) from e

    # Verify file exists
    if not cred_path.exists():
        logger.error("Credential file not found: %s", cred_path)
        msg = f"Credential file not found: {cred_path}"
        raise ConfigurationError(msg)

    # Verify it's a file, not a directory or special file
    if not cred_path.is_file():
        logger.error("Credential path is not a regular file: %s", cred_path)
        msg = f"Credential path is not a regular file: {cred_path}"
        raise ConfigurationError(msg)

    return cred_path


def _validate_columns(columns: list[str], table_type: TableType) -> None:
    """Validate that all columns are in the allowlist for the table type.

    Args:
        columns: List of column names to validate
        table_type: Type of table being queried

    Raises:
        BigQueryError: If any column is not in the allowlist
    """
    allowed = ALLOWED_COLUMNS[table_type]
    invalid_columns = [col for col in columns if col not in allowed]

    if invalid_columns:
        logger.error(
            "Invalid columns for table %s: %s (allowed: %s)",
            table_type,
            invalid_columns,
            sorted(allowed),
        )
        msg = (
            f"Invalid columns for table '{table_type}': {invalid_columns}. "
            f"Allowed columns: {sorted(allowed)}"
        )
        raise BigQueryError(msg)


def _build_where_clause_for_events(
    filter_obj: EventFilter,
) -> tuple[str, list[bigquery.ScalarQueryParameter]]:
    """Build WHERE clause and parameters for Events table queries.

    This function constructs a parameterized WHERE clause from an EventFilter.
    All values are passed as query parameters to prevent SQL injection.

    Args:
        filter_obj: Event filter with query parameters

    Returns:
        Tuple of (where_clause_sql, query_parameters)
    """
    conditions: list[str] = []
    parameters: list[bigquery.ScalarQueryParameter] = []

    # Mandatory: Date range filter on _PARTITIONTIME
    # This is REQUIRED for partitioned tables to avoid full table scans
    conditions.append("_PARTITIONTIME >= @start_date")
    conditions.append("_PARTITIONTIME <= @end_date")

    # Convert dates to datetime for TIMESTAMP comparison
    start_datetime = datetime.combine(filter_obj.date_range.start, datetime.min.time())
    end_date = filter_obj.date_range.end or filter_obj.date_range.start
    end_datetime = datetime.combine(end_date, datetime.max.time())

    parameters.extend(
        [
            bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_datetime),
            bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_datetime),
        ],
    )

    # Optional: Actor filters
    if filter_obj.actor1_country is not None:
        conditions.append("Actor1CountryCode = @actor1_country")
        parameters.append(
            bigquery.ScalarQueryParameter("actor1_country", "STRING", filter_obj.actor1_country),
        )

    if filter_obj.actor2_country is not None:
        conditions.append("Actor2CountryCode = @actor2_country")
        parameters.append(
            bigquery.ScalarQueryParameter("actor2_country", "STRING", filter_obj.actor2_country),
        )

    # Optional: Event code filters
    if filter_obj.event_code is not None:
        conditions.append("EventCode = @event_code")
        parameters.append(
            bigquery.ScalarQueryParameter("event_code", "STRING", filter_obj.event_code),
        )

    if filter_obj.event_root_code is not None:
        conditions.append("EventRootCode = @event_root_code")
        parameters.append(
            bigquery.ScalarQueryParameter("event_root_code", "STRING", filter_obj.event_root_code),
        )

    if filter_obj.event_base_code is not None:
        conditions.append("EventBaseCode = @event_base_code")
        parameters.append(
            bigquery.ScalarQueryParameter("event_base_code", "STRING", filter_obj.event_base_code),
        )

    # Optional: Tone filters
    if filter_obj.min_tone is not None:
        conditions.append("AvgTone >= @min_tone")
        parameters.append(bigquery.ScalarQueryParameter("min_tone", "FLOAT64", filter_obj.min_tone))

    if filter_obj.max_tone is not None:
        conditions.append("AvgTone <= @max_tone")
        parameters.append(bigquery.ScalarQueryParameter("max_tone", "FLOAT64", filter_obj.max_tone))

    # Optional: Location filter
    if filter_obj.action_country is not None:
        conditions.append("ActionGeo_CountryCode = @action_country")
        parameters.append(
            bigquery.ScalarQueryParameter("action_country", "STRING", filter_obj.action_country),
        )

    where_clause = " AND ".join(conditions)
    return where_clause, parameters


def _build_where_clause_for_gkg(
    filter_obj: GKGFilter,
) -> tuple[str, list[bigquery.ScalarQueryParameter]]:
    """Build WHERE clause and parameters for GKG table queries.

    This function constructs a parameterized WHERE clause from a GKGFilter.
    All values are passed as query parameters to prevent SQL injection.

    Args:
        filter_obj: GKG filter with query parameters

    Returns:
        Tuple of (where_clause_sql, query_parameters)
    """
    conditions: list[str] = []
    parameters: list[bigquery.ScalarQueryParameter] = []

    # Mandatory: Date range filter on _PARTITIONTIME
    conditions.append("_PARTITIONTIME >= @start_date")
    conditions.append("_PARTITIONTIME <= @end_date")

    # Convert dates to datetime for TIMESTAMP comparison
    start_datetime = datetime.combine(filter_obj.date_range.start, datetime.min.time())
    end_date = filter_obj.date_range.end or filter_obj.date_range.start
    end_datetime = datetime.combine(end_date, datetime.max.time())

    parameters.extend(
        [
            bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_datetime),
            bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_datetime),
        ],
    )

    # Optional: Theme filters
    if filter_obj.themes is not None and len(filter_obj.themes) > 0:
        # Use REGEXP_CONTAINS for theme matching (themes are semicolon-delimited)
        # We build a regex pattern like: (THEME1|THEME2|THEME3)
        theme_pattern = "|".join(re.escape(t) for t in filter_obj.themes)
        conditions.append("REGEXP_CONTAINS(V2Themes, @theme_pattern)")
        parameters.append(bigquery.ScalarQueryParameter("theme_pattern", "STRING", theme_pattern))

    if filter_obj.theme_prefix is not None:
        # Match themes starting with prefix (anchored to start or after semicolon delimiter)
        # Use LOWER() for case-insensitive matching (RE2 doesn't support (?i) reliably)
        conditions.append("REGEXP_CONTAINS(LOWER(V2Themes), @theme_prefix_pattern)")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "theme_prefix_pattern",
                "STRING",
                f"(^|;){re.escape(filter_obj.theme_prefix.lower())}",
            ),
        )

    # Optional: Entity filters (persons, organizations)
    # Use LOWER() for case-insensitive matching (RE2 doesn't support (?i) reliably)
    if filter_obj.persons is not None and len(filter_obj.persons) > 0:
        person_pattern = "|".join(re.escape(p.lower()) for p in filter_obj.persons)
        conditions.append("REGEXP_CONTAINS(LOWER(V2Persons), @person_pattern)")
        parameters.append(bigquery.ScalarQueryParameter("person_pattern", "STRING", person_pattern))

    if filter_obj.organizations is not None and len(filter_obj.organizations) > 0:
        org_pattern = "|".join(re.escape(o.lower()) for o in filter_obj.organizations)
        conditions.append("REGEXP_CONTAINS(LOWER(V2Organizations), @org_pattern)")
        parameters.append(bigquery.ScalarQueryParameter("org_pattern", "STRING", org_pattern))

    # Optional: Country filter
    if filter_obj.country is not None:
        conditions.append("REGEXP_CONTAINS(V2Locations, @country_code)")
        parameters.append(
            bigquery.ScalarQueryParameter("country_code", "STRING", filter_obj.country),
        )

    # Optional: Tone filters (V2Tone format: tone,positive,negative,polarity,activity_ref_density,self_ref_density,word_count)
    # We extract the first field (tone) from the comma-delimited string
    if filter_obj.min_tone is not None:
        conditions.append("CAST(SPLIT(V2Tone, ',')[OFFSET(0)] AS FLOAT64) >= @min_tone")
        parameters.append(bigquery.ScalarQueryParameter("min_tone", "FLOAT64", filter_obj.min_tone))

    if filter_obj.max_tone is not None:
        conditions.append("CAST(SPLIT(V2Tone, ',')[OFFSET(0)] AS FLOAT64) <= @max_tone")
        parameters.append(bigquery.ScalarQueryParameter("max_tone", "FLOAT64", filter_obj.max_tone))

    where_clause = " AND ".join(conditions)
    return where_clause, parameters


class _GKGGroupByParsed(NamedTuple):
    """Parsed GKG group_by columns, separating unnest fields from flat columns."""

    select_parts: list[str]
    group_refs: list[str]
    group_by_output: list[str]
    unnest_join: str
    extra_conditions: list[str]


class BigQuerySource:
    """BigQuery data source for GDELT datasets.

    This class provides async access to GDELT's BigQuery public datasets,
    serving as a fallback when REST APIs fail or rate limit. It wraps the
    synchronous BigQuery client with an async interface using run_in_executor.

    All queries use parameterized queries to prevent SQL injection, and only
    query _partitioned tables with mandatory date filters for cost control.

    Args:
        settings: GDELT settings (creates default if None)
        client: BigQuery client (creates new one if None, caller owns lifecycle)
        maximum_bytes_billed: Optional cap on bytes billed per query. When set,
            BigQuery will reject queries that would scan more than this many bytes.

    Note:
        If client is None, credentials will be loaded from settings on first query.
        Credentials are validated on first use, never logged.

    Example:
        >>> from py_gdelt.filters import EventFilter, DateRange
        >>> from datetime import date
        >>>
        >>> async with BigQuerySource() as source:
        ...     filter_obj = EventFilter(
        ...         date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 2)),
        ...         actor1_country="USA",
        ...     )
        ...     async for row in source.query_events(filter_obj):
        ...         print(row["GLOBALEVENTID"])

    Security:
        - All queries use parameterized queries (NO string formatting/interpolation)
        - Column names validated against explicit allowlists
        - Credential paths validated to prevent directory traversal
        - Credentials never logged or exposed in error messages
        - Only _partitioned tables queried to prevent accidental full scans
    """

    def __init__(
        self,
        settings: GDELTSettings | None = None,
        client: bigquery.Client | None = None,
        *,
        maximum_bytes_billed: int | None = None,
    ) -> None:
        self.settings = settings or GDELTSettings()
        self._client = client
        self._owns_client = client is None
        self._credentials_validated = False
        self._maximum_bytes_billed = maximum_bytes_billed

    async def __aenter__(self) -> "BigQuerySource":
        """Async context manager entry.

        Returns:
            Self for use in async with statement
        """
        # Client initialization is deferred to first query for lazy credential loading
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        if self._owns_client and self._client is not None:
            # BigQuery client has no close() method, just clean up reference
            self._client = None

    def _get_or_create_client(self) -> bigquery.Client:
        """Get or create BigQuery client with credential validation.

        Returns:
            Initialized BigQuery client

        Raises:
            ConfigurationError: If credentials are not configured or invalid
            BigQueryError: If client creation fails
        """
        if self._client is not None:
            return self._client

        # Validate and load credentials
        if not self._credentials_validated:
            self._validate_credentials()

        try:
            # Try to create client
            if self.settings.bigquery_credentials is not None:
                # Use explicit credentials file
                cred_path = _validate_credential_path(self.settings.bigquery_credentials)
                logger.debug("Loading BigQuery credentials from: %s", cred_path)

                credentials = service_account.Credentials.from_service_account_file(str(cred_path))  # type: ignore[no-untyped-call]

                # Get project from settings or credentials
                project = self.settings.bigquery_project or credentials.project_id
                if project is None:
                    msg = "BigQuery project not specified in settings or credentials"
                    raise ConfigurationError(msg)

                self._client = bigquery.Client(credentials=credentials, project=project)
                logger.info("BigQuery client initialized with explicit credentials")

            else:
                # Use Application Default Credentials (ADC)
                project = self.settings.bigquery_project
                if project is None:
                    msg = "BigQuery project must be specified when using Application Default Credentials"
                    raise ConfigurationError(msg)

                self._client = bigquery.Client(project=project)
                logger.info("BigQuery client initialized with Application Default Credentials")

        except GoogleCloudError as e:
            logger.error("Failed to create BigQuery client: %s", e)  # noqa: TRY400
            msg = f"Failed to create BigQuery client: {e}"
            raise BigQueryError(msg) from e
        else:
            return self._client

    def _validate_credentials(self) -> None:
        """Validate BigQuery credentials configuration.

        Raises:
            ConfigurationError: If credentials are not properly configured
        """
        # Check if credentials or ADC is configured
        has_explicit_creds = self.settings.bigquery_credentials is not None
        has_project = self.settings.bigquery_project is not None

        if not has_explicit_creds and not has_project:
            logger.error("BigQuery credentials not configured")
            msg = (
                "BigQuery credentials not configured. Set either:\n"
                "  1. GDELT_BIGQUERY_CREDENTIALS (path to credentials JSON) + GDELT_BIGQUERY_PROJECT, or\n"
                "  2. GDELT_BIGQUERY_PROJECT (uses Application Default Credentials)\n"
                "See: https://cloud.google.com/docs/authentication/application-default-credentials"
            )
            raise ConfigurationError(msg)

        if has_explicit_creds:
            # Validate credential file path
            _validate_credential_path(self.settings.bigquery_credentials)  # type: ignore[arg-type]

        self._credentials_validated = True
        logger.debug("BigQuery credentials configuration validated")

    async def query_events(
        self,
        filter_obj: EventFilter,
        columns: list[str] | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Query GDELT Events table with filters.

        All queries use parameterized queries to prevent SQL injection.
        Queries are executed against the events_partitioned table with
        mandatory date filters for cost control.

        Args:
            filter_obj: Event filter with query parameters
            columns: List of columns to select (defaults to all allowed columns)
            limit: Maximum number of rows to return (None for unlimited)

        Yields:
            dict[str, Any]: Dictionary of column name -> value for each row

        Raises:
            BigQueryError: If query execution fails
            ConfigurationError: If credentials are not configured

        Example:
            >>> filter_obj = EventFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     actor1_country="USA",
            ...     event_root_code="14",  # Protest
            ... )
            >>> async for row in source.query_events(filter_obj, limit=100):
            ...     print(row["GLOBALEVENTID"], row["EventCode"])
        """
        # Default to all allowed columns
        if columns is None:
            columns = sorted(ALLOWED_COLUMNS["events"])

        # Validate columns
        _validate_columns(columns, "events")

        # Build WHERE clause with parameters
        where_clause, parameters = _build_where_clause_for_events(filter_obj)

        # Build SELECT clause (columns are validated, safe to use directly)
        column_list = ", ".join(columns)

        # Build complete query
        query = f"""
            SELECT {column_list}
            FROM `{TABLES["events"]}`
            WHERE {where_clause}
        """

        # Add LIMIT if specified
        if limit is not None:
            query += f"\nLIMIT {limit:d}"

        # Execute query and stream results
        async for row in self._execute_query(query, parameters):
            yield row

    async def query_gkg(
        self,
        filter_obj: GKGFilter,
        columns: list[str] | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Query GDELT GKG table with filters.

        All queries use parameterized queries to prevent SQL injection.
        Queries are executed against the gkg_partitioned table with
        mandatory date filters for cost control.

        Args:
            filter_obj: GKG filter with query parameters
            columns: List of columns to select (defaults to all allowed columns)
            limit: Maximum number of rows to return (None for unlimited)

        Yields:
            dict[str, Any]: Dictionary of column name -> value for each row

        Raises:
            BigQueryError: If query execution fails
            ConfigurationError: If credentials are not configured

        Example:
            >>> filter_obj = GKGFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     themes=["ENV_CLIMATECHANGE"],
            ...     country="USA",
            ... )
            >>> async for row in source.query_gkg(filter_obj, limit=100):
            ...     print(row["GKGRECORDID"], row["V2Themes"])
        """
        # Default to all allowed columns
        if columns is None:
            columns = sorted(ALLOWED_COLUMNS["gkg"])

        # Validate columns
        _validate_columns(columns, "gkg")

        # Build WHERE clause with parameters
        where_clause, parameters = _build_where_clause_for_gkg(filter_obj)

        # Build SELECT clause (columns are validated, safe to use directly)
        column_list = ", ".join(columns)

        # Build complete query
        query = f"""
            SELECT {column_list}
            FROM `{TABLES["gkg"]}`
            WHERE {where_clause}
        """

        # Add LIMIT if specified
        if limit is not None:
            query += f"\nLIMIT {limit:d}"

        # Execute query and stream results
        async for row in self._execute_query(query, parameters):
            yield row

    async def query_mentions(
        self,
        global_event_id: int,
        columns: list[str] | None = None,
        date_range: DateRange | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Query GDELT EventMentions table for a specific event.

        All queries use parameterized queries to prevent SQL injection.
        A date range should be provided for efficient querying.

        Args:
            global_event_id: Global event ID to query mentions for (INT64)
            columns: List of columns to select (defaults to all allowed columns)
            date_range: Optional date range to narrow search (recommended for performance)
            limit: Maximum number of rows to return (None for unlimited)

        Yields:
            dict[str, Any]: Dictionary of column name -> value for each mention row

        Raises:
            BigQueryError: If query execution fails
            ConfigurationError: If credentials are not configured

        Example:
            >>> async for mention in source.query_mentions(
            ...     global_event_id=123456789,
            ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
            ...     limit=100,
            ... ):
            ...     print(mention["MentionTimeDate"], mention["MentionSourceName"])
        """
        # Default to all allowed columns
        if columns is None:
            columns = sorted(ALLOWED_COLUMNS["eventmentions"])

        # Validate columns
        _validate_columns(columns, "eventmentions")

        # Build WHERE clause
        conditions: list[str] = ["GLOBALEVENTID = @event_id"]
        parameters: list[bigquery.ScalarQueryParameter] = [
            bigquery.ScalarQueryParameter("event_id", "INT64", global_event_id),
        ]

        # Add date range filter if provided (for partition pruning)
        if date_range is not None:
            conditions.append("_PARTITIONTIME >= @start_date")
            conditions.append("_PARTITIONTIME <= @end_date")

            start_datetime = datetime.combine(date_range.start, datetime.min.time())
            end_date = date_range.end or date_range.start
            end_datetime = datetime.combine(end_date, datetime.max.time())

            parameters.extend(
                [
                    bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_datetime),
                    bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_datetime),
                ],
            )

        where_clause = " AND ".join(conditions)
        column_list = ", ".join(columns)

        # Build query
        query = f"""
            SELECT {column_list}
            FROM `{TABLES["eventmentions"]}`
            WHERE {where_clause}
        """

        # Add LIMIT if specified
        if limit is not None:
            query += f"\nLIMIT {limit:d}"

        # Execute query and stream results
        async for row in self._execute_query(query, parameters):
            yield row

    async def _execute_query(
        self,
        query: str,
        parameters: list[bigquery.ScalarQueryParameter],
    ) -> AsyncIterator[dict[str, Any]]:
        """Execute a BigQuery query and stream results asynchronously.

        This method wraps the synchronous BigQuery client with run_in_executor
        to provide an async interface. Results are streamed row-by-row for
        memory efficiency.

        Args:
            query: SQL query string (should use parameterized placeholders)
            parameters: List of query parameters

        Yields:
            dict[str, Any]: Dictionary of column name -> value for each row

        Raises:
            BigQueryError: If query execution fails
        """
        # Get or create client
        client = self._get_or_create_client()

        # Log query (but not parameters, as they may contain sensitive data)
        logger.debug("Executing BigQuery query: %s", query.strip())
        logger.debug("Query has %d parameters", len(parameters))

        # Configure query job with parameters
        job_config_kwargs: dict[str, Any] = {"query_parameters": parameters}
        if self._maximum_bytes_billed is not None:
            job_config_kwargs["maximum_bytes_billed"] = self._maximum_bytes_billed
        job_config = bigquery.QueryJobConfig(**job_config_kwargs)

        try:
            # Execute query in thread pool (BigQuery client is synchronous)
            loop = asyncio.get_event_loop()
            query_job = await loop.run_in_executor(
                None,
                lambda: client.query(query, job_config=job_config),
            )

            # Wait for query to complete
            await loop.run_in_executor(None, query_job.result)

            # Log query results (use getattr for optional attributes)
            total_rows = getattr(query_job, "total_rows", None)
            total_bytes = getattr(query_job, "total_bytes_processed", None)
            logger.info(
                "Query completed. Total rows: %s, bytes processed: %s",
                total_rows,
                total_bytes,
            )

            # Stream results row-by-row
            rows_yielded = 0
            for row in query_job:
                # Convert Row to dict
                row_dict = dict(row.items())
                yield row_dict
                rows_yielded += 1

            logger.debug("Yielded %d rows from query result", rows_yielded)

        except GoogleCloudError as e:
            logger.error("BigQuery query failed: %s", e)  # noqa: TRY400
            msg = f"BigQuery query failed: {e}"
            raise BigQueryError(msg) from e
        except Exception as e:
            logger.error("Unexpected error executing BigQuery query: %s", e)  # noqa: TRY400
            msg = f"Unexpected error executing query: {e}"
            raise BigQueryError(msg) from e

    async def _execute_query_batch(
        self,
        query: str,
        parameters: list[bigquery.ScalarQueryParameter],
    ) -> tuple[list[dict[str, Any]], int | None]:
        """Execute a BigQuery query and return all results as a batch.

        Unlike ``_execute_query`` which streams rows, this collects all results
        and returns query metadata (``bytes_processed``) for cost tracking.

        Args:
            query: SQL query string (should use parameterized placeholders).
            parameters: List of query parameters.

        Returns:
            Tuple of (rows as list of dicts, bytes_processed or None).

        Raises:
            BigQueryError: If query execution fails.
        """
        client = self._get_or_create_client()

        logger.debug("Executing BigQuery batch query: %s", query.strip())
        logger.debug("Query has %d parameters", len(parameters))

        job_config_kwargs: dict[str, Any] = {"query_parameters": parameters}
        if self._maximum_bytes_billed is not None:
            job_config_kwargs["maximum_bytes_billed"] = self._maximum_bytes_billed
        job_config = bigquery.QueryJobConfig(**job_config_kwargs)

        try:
            loop = asyncio.get_event_loop()
            query_job = await loop.run_in_executor(
                None,
                lambda: client.query(query, job_config=job_config),
            )
            await loop.run_in_executor(None, query_job.result)

        except GoogleCloudError as e:
            logger.error("BigQuery batch query failed: %s", e)  # noqa: TRY400
            msg = f"BigQuery query failed: {e}"
            raise BigQueryError(msg) from e
        except Exception as e:
            logger.error("Unexpected error in BigQuery batch query: %s", e)  # noqa: TRY400
            msg = f"Unexpected error executing query: {e}"
            raise BigQueryError(msg) from e
        else:
            rows = [dict(row.items()) for row in query_job]
            bytes_processed: int | None = getattr(query_job, "total_bytes_processed", None)

            logger.info(
                "Batch query completed. Rows: %d, bytes processed: %s",
                len(rows),
                bytes_processed,
            )

            return rows, bytes_processed

    async def aggregate_events(
        self,
        filter_obj: EventFilter,
        *,
        group_by: list[str],
        aggregations: list[Aggregation],
        order_by: str | None = None,
        ascending: bool = False,
        limit: int | None = None,
    ) -> AggregationResult:
        """Run an aggregation query against the GDELT Events table.

        Builds and executes a ``GROUP BY`` query with the specified aggregation
        functions. All column names are validated against the events allowlist,
        and aliases are sanitized to prevent SQL injection.

        Args:
            filter_obj: Event filter with date range and query parameters.
            group_by: Column names to group by (must be in events allowlist).
            aggregations: List of aggregation specifications.
            order_by: Column or alias to order results by. Defaults to the
                first aggregation alias (descending) when ``limit`` is set.
            ascending: If True, sort ascending; otherwise descending.
            limit: Maximum number of result rows.

        Returns:
            AggregationResult with rows, group_by columns, and metadata.

        Raises:
            BigQueryError: If column names are invalid or query execution fails.
            SecurityError: If an alias fails sanitization.
        """
        # Validate group_by columns against allowlist
        _validate_columns(group_by, "events")

        # Validate aggregation columns against allowlist (except "*")
        agg_columns = [a.column for a in aggregations if a.column != "*"]
        if agg_columns:
            _validate_columns(agg_columns, "events")

        # Build SELECT expressions
        select_parts = list(group_by)
        agg_aliases = self._build_agg_select(aggregations, select_parts)

        select_clause = ", ".join(select_parts)
        group_clause = ", ".join(group_by)

        # Build WHERE clause
        where_clause, parameters = _build_where_clause_for_events(filter_obj)

        # Build ORDER BY
        order_clause = self._build_order_clause(order_by, ascending, limit, agg_aliases)

        # Build complete query
        query = (
            f"SELECT {select_clause} "
            f"FROM `{TABLES['events']}` "
            f"WHERE {where_clause} "
            f"GROUP BY {group_clause} "
            f"{order_clause}"
        )

        if limit is not None:
            query += f" LIMIT {limit:d}"

        rows, bytes_processed = await self._execute_query_batch(query, parameters)

        return AggregationResult(
            rows=rows,
            group_by=group_by,
            total_rows=len(rows),
            bytes_processed=bytes_processed,
        )

    async def aggregate_gkg(
        self,
        filter_obj: GKGFilter,
        *,
        group_by: list[str | GKGUnnestField],
        aggregations: list[Aggregation],
        order_by: str | None = None,
        ascending: bool = False,
        limit: int | None = None,
    ) -> AggregationResult:
        """Run an aggregation query against the GDELT GKG table.

        Supports UNNEST(SPLIT(...)) for semicolon-delimited GKG fields such as
        themes, persons, and organizations. At most one ``GKGUnnestField`` may
        appear in ``group_by`` per query.

        Args:
            filter_obj: GKG filter with date range and query parameters.
            group_by: Column names or ``GKGUnnestField`` values to group by.
                Flat column names are validated against the GKG allowlist.
            aggregations: List of aggregation specifications.
            order_by: Column or alias to order results by. Defaults to the
                first aggregation alias (descending) when ``limit`` is set.
            ascending: If True, sort ascending; otherwise descending.
            limit: Maximum number of result rows.

        Returns:
            AggregationResult with rows, group_by columns, and metadata.

        Raises:
            BigQueryError: If column names are invalid, more than one unnest
                field is specified, or query execution fails.
            SecurityError: If an alias fails sanitization.
        """
        # Parse and validate group_by columns
        parsed = self._parse_gkg_group_by(group_by)

        # Validate aggregation columns (except "*")
        agg_columns = [a.column for a in aggregations if a.column != "*"]
        if agg_columns:
            _validate_columns(agg_columns, "gkg")

        # Build aggregation expressions
        agg_aliases = self._build_agg_select(aggregations, parsed.select_parts)

        select_clause = ", ".join(parsed.select_parts)
        group_clause = ", ".join(parsed.group_refs)

        # Build WHERE clause
        where_clause, parameters = _build_where_clause_for_gkg(filter_obj)
        if parsed.extra_conditions:
            where_clause += " AND " + " AND ".join(parsed.extra_conditions)

        # Build ORDER BY
        order_clause = self._build_order_clause(order_by, ascending, limit, agg_aliases)

        # Build complete query
        query = (
            f"SELECT {select_clause} "
            f"FROM `{TABLES['gkg']}`{parsed.unnest_join} "
            f"WHERE {where_clause} "
            f"GROUP BY {group_clause} "
            f"{order_clause}"
        )

        if limit is not None:
            query += f" LIMIT {limit:d}"

        rows, bytes_processed = await self._execute_query_batch(query, parameters)

        return AggregationResult(
            rows=rows,
            group_by=parsed.group_by_output,
            total_rows=len(rows),
            bytes_processed=bytes_processed,
        )

    @staticmethod
    def _auto_alias(agg: Aggregation) -> str:
        """Generate a default alias from an aggregation specification.

        Args:
            agg: The aggregation to generate an alias for.

        Returns:
            A safe alias string like ``count_star`` or ``avg_AvgTone``.
        """
        col_part = "star" if agg.column == "*" else agg.column
        return f"{agg.func.value.lower()}_{col_part}"

    @staticmethod
    def _validate_alias(alias: str) -> None:
        """Validate that an alias matches the safe identifier pattern.

        Args:
            alias: The alias string to validate.

        Raises:
            SecurityError: If the alias contains unsafe characters.
        """
        if not _ALIAS_PATTERN.match(alias):
            msg = (
                f"Invalid alias {alias!r}: must match [a-zA-Z_][a-zA-Z0-9_]* "
                "(alphanumeric and underscore only)"
            )
            raise SecurityError(msg)

    @staticmethod
    def _render_agg_expr(agg: Aggregation) -> str:
        """Render a SQL aggregation expression (without alias).

        Args:
            agg: The aggregation specification.

        Returns:
            SQL expression string like ``COUNT(*)`` or ``AVG(AvgTone)``.
        """
        if agg.func == AggFunc.COUNT and agg.column == "*":
            return "COUNT(*)"
        if agg.func == AggFunc.COUNT_DISTINCT:
            return f"COUNT(DISTINCT {agg.column})"
        return f"{agg.func.value}({agg.column})"

    def _build_agg_select(
        self,
        aggregations: list[Aggregation],
        select_parts: list[str],
    ) -> list[str]:
        """Build aggregation SELECT expressions and return aliases.

        Mutates ``select_parts`` in place by appending aggregation expressions.

        Args:
            aggregations: Aggregation specifications.
            select_parts: Mutable list to append SQL expressions to.

        Returns:
            List of validated alias names for the aggregation columns.
        """
        agg_aliases: list[str] = []
        for agg in aggregations:
            alias = agg.alias or self._auto_alias(agg)
            self._validate_alias(alias)
            agg_aliases.append(alias)
            select_parts.append(f"{self._render_agg_expr(agg)} AS {alias}")
        return agg_aliases

    @staticmethod
    def _build_order_clause(
        order_by: str | None,
        ascending: bool,
        limit: int | None,
        agg_aliases: list[str],
    ) -> str:
        """Build the ORDER BY clause for an aggregation query.

        When ``order_by`` is None and ``limit`` is set, defaults to the first
        aggregation alias in descending order.

        Args:
            order_by: Explicit column/alias to order by, or None.
            ascending: Sort direction.
            limit: Query row limit (triggers default ordering when set).
            agg_aliases: Available aggregation aliases for default ordering.

        Returns:
            SQL ORDER BY clause, or empty string if no ordering needed.
        """
        direction = "ASC" if ascending else "DESC"
        if order_by is not None:
            BigQuerySource._validate_alias(order_by)
            return f"ORDER BY {order_by} {direction}"
        if limit is not None and agg_aliases:
            return f"ORDER BY {agg_aliases[0]} {direction}"
        return ""

    @staticmethod
    def _parse_gkg_group_by(
        group_by: list[str | GKGUnnestField],
    ) -> _GKGGroupByParsed:
        """Parse GKG group_by into SELECT parts, GROUP BY refs, and UNNEST join.

        Separates ``GKGUnnestField`` values from flat column names, validates
        that at most one unnest field is present, and validates flat columns
        against the GKG allowlist.

        Args:
            group_by: Mixed list of column names and unnest field enums.

        Returns:
            Parsed result with SELECT parts, GROUP refs, and UNNEST SQL.

        Raises:
            BigQueryError: If more than one unnest field or invalid columns.
        """
        unnest_fields: list[GKGUnnestField] = []
        flat_columns: list[str] = []
        select_parts: list[str] = []
        group_refs: list[str] = []
        group_by_output: list[str] = []
        unnest_join = ""
        extra_conditions: list[str] = []

        for col in group_by:
            if isinstance(col, GKGUnnestField):
                unnest_fields.append(col)
                bq_column, split_expr = GKG_UNNEST_CONFIG[col]
                select_parts.append(f"{split_expr} AS {col.value}")
                group_refs.append(col.value)
                group_by_output.append(col.value)
                unnest_join = f", UNNEST(SPLIT({bq_column}, ';')) AS item"
                extra_conditions.append("item != ''")
            else:
                flat_columns.append(col)
                select_parts.append(col)
                group_refs.append(col)
                group_by_output.append(col)

        if len(unnest_fields) > 1:
            msg = (
                "Only one GKGUnnestField is allowed per query "
                f"(BigQuery cross-join limitation). Got: {[f.value for f in unnest_fields]}"
            )
            raise BigQueryError(msg)

        if flat_columns:
            _validate_columns(flat_columns, "gkg")

        return _GKGGroupByParsed(
            select_parts=select_parts,
            group_refs=group_refs,
            group_by_output=group_by_output,
            unnest_join=unnest_join,
            extra_conditions=extra_conditions,
        )
