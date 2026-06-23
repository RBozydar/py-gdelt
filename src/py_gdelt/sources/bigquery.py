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
from collections.abc import AsyncIterator, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any, Final, Literal, NamedTuple


try:
    from google.cloud import bigquery
    from google.cloud.exceptions import GoogleCloudError
    from google.oauth2 import service_account
except ImportError as exc:
    msg = (
        "BigQuerySource requires the optional BigQuery dependency. "
        "Install it with: pip install 'gdelt-py[bigquery]'"
    )
    raise ImportError(msg) from exc
from pydantic import ValidationError

from py_gdelt.config import GDELTSettings
from py_gdelt.exceptions import BigQueryError, ConfigurationError, SecurityError
from py_gdelt.filters import DateRange, EventFilter, GKGFilter
from py_gdelt.sources._bigquery_rows import (
    _BQ_EVENT_MAP,
    _BQ_GKG_MAP,
    _BQ_MENTION_MAP,
    _bq_row_to_raw_event,
    _bq_row_to_raw_gkg,
    _bq_row_to_raw_mention,
)
from py_gdelt.sources.aggregation import (
    _ALIAS_PATTERN,
    GKG_UNNEST_CONFIG,
    AggFunc,
    Aggregation,
    AggregationResult,
    GKGUnnestField,
)
from py_gdelt.sources.metadata import QueryEstimate, QueryMetadata


__all__ = [
    "_BQ_EVENT_MAP",
    "_BQ_GKG_MAP",
    "_BQ_MENTION_MAP",
    "BigQuerySource",
    "TableType",
    "_bq_row_to_raw_event",
    "_bq_row_to_raw_gkg",
    "_bq_row_to_raw_mention",
]

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
# GKG columns that need SQL-level rewriting when used in aggregation expressions.
# V2Tone is a comma-delimited STRING with 7 subfields: tone, positive, negative,
# polarity, activity_ref_density, self_ref_density, word_count.
# All are cast to FLOAT64 so they work uniformly with AVG/STDDEV/etc.
_GKG_COLUMN_TRANSFORMS: Final[dict[str, str]] = {
    "V2Tone": "SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(0)] AS FLOAT64)",
    "V2Tone_Positive": "SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(1)] AS FLOAT64)",
    "V2Tone_Negative": "SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(2)] AS FLOAT64)",
    "V2Tone_Polarity": "SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(3)] AS FLOAT64)",
    "V2Tone_ActivityDensity": "SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(4)] AS FLOAT64)",
    "V2Tone_SelfDensity": "SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(5)] AS FLOAT64)",
    "V2Tone_WordCount": "SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(6)] AS FLOAT64)",
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
            "V2Tone_Positive",
            "V2Tone_Negative",
            "V2Tone_Polarity",
            "V2Tone_ActivityDensity",
            "V2Tone_SelfDensity",
            "V2Tone_WordCount",
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
        conditions.append("REGEXP_CONTAINS(V2Locations, @country_pattern)")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "country_pattern", "STRING", f"#{re.escape(filter_obj.country)}#"
            ),
        )

    # Optional: Tone filters (V2Tone format: tone,positive,negative,polarity,activity_ref_density,self_ref_density,word_count)
    # We extract the first field (tone) from the comma-delimited string
    if filter_obj.min_tone is not None:
        conditions.append("SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(0)] AS FLOAT64) >= @min_tone")
        parameters.append(bigquery.ScalarQueryParameter("min_tone", "FLOAT64", filter_obj.min_tone))

    if filter_obj.max_tone is not None:
        conditions.append("SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(0)] AS FLOAT64) <= @max_tone")
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
        self._last_query_metadata: QueryMetadata | None = None

    @property
    def last_query_metadata(self) -> QueryMetadata | None:
        """Metadata from the most recently completed query.

        Returns ``None`` if no query has been executed yet.  After any
        successful call to ``_execute_query`` or ``_execute_query_batch``,
        this property exposes timing, cost, and row-count statistics
        captured from the BigQuery ``QueryJob``.

        Returns:
            QueryMetadata | None: Captured metadata, or None before first query.
        """
        return self._last_query_metadata

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

    # ── SQL builder helpers ─────────────────────────────────────────────────
    #
    # Each ``_build_*_sql`` method constructs the full SQL string and
    # parameter list for a given table.  They are pure (non-async, no I/O)
    # and are shared by both ``query_*`` and ``estimate_*`` methods.

    def _build_events_sql(
        self,
        filter_obj: EventFilter,
        columns: list[str] | None,
        limit: int | None,
    ) -> tuple[str, list[bigquery.ScalarQueryParameter]]:
        """Build SQL and parameters for an Events table query.

        Args:
            filter_obj: Event filter with query parameters.
            columns: List of columns to select (defaults to all allowed columns).
            limit: Maximum number of rows to return (None for unlimited).

        Returns:
            Tuple of (query_string, query_parameters).

        Raises:
            BigQueryError: If any column is not in the events allowlist.
        """
        if columns is None:
            columns = sorted(ALLOWED_COLUMNS["events"])

        _validate_columns(columns, "events")

        where_clause, parameters = _build_where_clause_for_events(filter_obj)
        column_list = ", ".join(columns)

        query = f"""
            SELECT {column_list}
            FROM `{TABLES["events"]}`
            WHERE {where_clause}
        """

        if limit is not None:
            query += f"\nLIMIT {limit:d}"

        return query, parameters

    def _build_gkg_sql(
        self,
        filter_obj: GKGFilter,
        columns: list[str] | None,
        limit: int | None,
    ) -> tuple[str, list[bigquery.ScalarQueryParameter]]:
        """Build SQL and parameters for a GKG table query.

        Args:
            filter_obj: GKG filter with query parameters.
            columns: List of columns to select (defaults to all allowed columns).
            limit: Maximum number of rows to return (None for unlimited).

        Returns:
            Tuple of (query_string, query_parameters).

        Raises:
            BigQueryError: If any column is not in the GKG allowlist.
        """
        if columns is None:
            columns = sorted(ALLOWED_COLUMNS["gkg"])

        _validate_columns(columns, "gkg")

        where_clause, parameters = _build_where_clause_for_gkg(filter_obj)
        column_list = ", ".join(columns)

        query = f"""
            SELECT {column_list}
            FROM `{TABLES["gkg"]}`
            WHERE {where_clause}
        """

        if limit is not None:
            query += f"\nLIMIT {limit:d}"

        return query, parameters

    def _build_mentions_sql(
        self,
        global_event_id: int,
        columns: list[str] | None,
        date_range: DateRange | None,
        limit: int | None,
    ) -> tuple[str, list[bigquery.ScalarQueryParameter]]:
        """Build SQL and parameters for an EventMentions table query.

        Args:
            global_event_id: Global event ID to query mentions for (INT64).
            columns: List of columns to select (defaults to all allowed columns).
            date_range: Optional date range for partition pruning.
            limit: Maximum number of rows to return (None for unlimited).

        Returns:
            Tuple of (query_string, query_parameters).

        Raises:
            BigQueryError: If any column is not in the eventmentions allowlist.
        """
        if columns is None:
            columns = sorted(ALLOWED_COLUMNS["eventmentions"])

        _validate_columns(columns, "eventmentions")

        conditions: list[str] = ["GLOBALEVENTID = @event_id"]
        parameters: list[bigquery.ScalarQueryParameter] = [
            bigquery.ScalarQueryParameter("event_id", "INT64", global_event_id),
        ]

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

        query = f"""
            SELECT {column_list}
            FROM `{TABLES["eventmentions"]}`
            WHERE {where_clause}
        """

        if limit is not None:
            query += f"\nLIMIT {limit:d}"

        return query, parameters

    # ── Public query methods ─────────────────────────────────────────────

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
        query, parameters = self._build_events_sql(filter_obj, columns, limit)

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
        query, parameters = self._build_gkg_sql(filter_obj, columns, limit)

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
        query, parameters = self._build_mentions_sql(global_event_id, columns, date_range, limit)

        async for row in self._execute_query(query, parameters):
            yield row

    # ── Public estimate methods ──────────────────────────────────────────

    async def estimate_events(
        self,
        filter_obj: EventFilter,
        columns: list[str] | None = None,
        limit: int | None = None,
    ) -> QueryEstimate:
        """Estimate the cost of an Events table query without executing it.

        Performs a BigQuery dry run to determine how many bytes the query
        would scan.  No data is read and no charges are incurred.

        Args:
            filter_obj: Event filter with query parameters.
            columns: List of columns to select (defaults to all allowed columns).
            limit: Maximum number of rows to return (None for unlimited).

        Returns:
            QueryEstimate with estimated bytes and the query SQL.

        Raises:
            BigQueryError: If column names are invalid or dry run fails.
            ConfigurationError: If credentials are not configured.
        """
        query, parameters = self._build_events_sql(filter_obj, columns, limit)
        return await self._execute_dry_run(query, parameters)

    async def estimate_gkg(
        self,
        filter_obj: GKGFilter,
        columns: list[str] | None = None,
        limit: int | None = None,
    ) -> QueryEstimate:
        """Estimate the cost of a GKG table query without executing it.

        Performs a BigQuery dry run to determine how many bytes the query
        would scan.  No data is read and no charges are incurred.

        Args:
            filter_obj: GKG filter with query parameters.
            columns: List of columns to select (defaults to all allowed columns).
            limit: Maximum number of rows to return (None for unlimited).

        Returns:
            QueryEstimate with estimated bytes and the query SQL.

        Raises:
            BigQueryError: If column names are invalid or dry run fails.
            ConfigurationError: If credentials are not configured.
        """
        query, parameters = self._build_gkg_sql(filter_obj, columns, limit)
        return await self._execute_dry_run(query, parameters)

    async def estimate_mentions(
        self,
        global_event_id: int,
        columns: list[str] | None = None,
        date_range: DateRange | None = None,
        limit: int | None = None,
    ) -> QueryEstimate:
        """Estimate the cost of a Mentions table query without executing it.

        Performs a BigQuery dry run to determine how many bytes the query
        would scan.  No data is read and no charges are incurred.

        Args:
            global_event_id: Global event ID to query mentions for (INT64).
            columns: List of columns to select (defaults to all allowed columns).
            date_range: Optional date range for partition pruning.
            limit: Maximum number of rows to return (None for unlimited).

        Returns:
            QueryEstimate with estimated bytes and the query SQL.

        Raises:
            BigQueryError: If column names are invalid or dry run fails.
            ConfigurationError: If credentials are not configured.
        """
        query, parameters = self._build_mentions_sql(global_event_id, columns, date_range, limit)
        return await self._execute_dry_run(query, parameters)

    @staticmethod
    def _extract_query_metadata(query_job: bigquery.QueryJob) -> QueryMetadata | None:
        """Extract metadata from a completed BigQuery query job.

        Uses ``getattr`` with ``None`` defaults for all attributes since
        BigQuery may not populate every statistic for all query types.
        Construction is wrapped in a try/except so that unexpected attribute
        types never disrupt query execution.

        Args:
            query_job: A completed BigQuery query job.

        Returns:
            QueryMetadata | None: Captured metadata, or None if extraction fails.
        """
        try:
            return QueryMetadata(
                bytes_processed=getattr(query_job, "total_bytes_processed", None),
                bytes_billed=getattr(query_job, "total_bytes_billed", None),
                cache_hit=getattr(query_job, "cache_hit", None),
                slot_millis=getattr(query_job, "slot_millis", None),
                total_rows=getattr(query_job, "total_rows", None),
                started=getattr(query_job, "started", None),
                ended=getattr(query_job, "ended", None),
                statement_type=getattr(query_job, "statement_type", None),
            )
        except ValidationError:
            logger.warning("Failed to extract query metadata from job")
            return None

    async def _execute_dry_run(
        self,
        query: str,
        parameters: list[bigquery.ScalarQueryParameter],
    ) -> QueryEstimate:
        """Execute a BigQuery dry run and return the cost estimate.

        A dry run validates the query and reports how many bytes would be
        scanned without actually executing it.  No data is read and no
        charges are incurred.

        Args:
            query: SQL query string (should use parameterized placeholders).
            parameters: List of query parameters.

        Returns:
            QueryEstimate with estimated bytes and the query SQL.

        Raises:
            BigQueryError: If the dry run fails.
        """
        client = self._get_or_create_client()

        job_config = bigquery.QueryJobConfig(
            dry_run=True,
            use_query_cache=False,
            query_parameters=parameters,
        )

        try:
            loop = asyncio.get_event_loop()
            query_job = await loop.run_in_executor(
                None,
                lambda: client.query(query, job_config=job_config),
            )

            return QueryEstimate(
                bytes_processed=query_job.total_bytes_processed or 0,
                query=query.strip(),
            )
        except GoogleCloudError as e:
            logger.error("BigQuery dry run failed: %s", e)  # noqa: TRY400
            msg = f"BigQuery dry run failed: {e}"
            raise BigQueryError(msg) from e

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

            # Capture query metadata
            self._last_query_metadata = self._extract_query_metadata(query_job)

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
        parameters: Sequence[bigquery.ScalarQueryParameter | bigquery.ArrayQueryParameter],
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
            # Capture query metadata
            self._last_query_metadata = self._extract_query_metadata(query_job)

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

        if not group_by and not aggregations:
            msg = "At least one of group_by or aggregations must be non-empty"
            raise BigQueryError(msg)

        # Validate aggregation columns against allowlist (except "*")
        agg_columns = [a.column for a in aggregations if a.column != "*"]
        if agg_columns:
            _validate_columns(agg_columns, "events")

        # Build SELECT expressions
        select_parts = list(group_by)
        agg_aliases = self._build_agg_select(aggregations, select_parts)

        select_clause = ", ".join(select_parts)

        # Build WHERE clause
        where_clause, parameters = _build_where_clause_for_events(filter_obj)

        # Build ORDER BY
        order_clause = self._build_order_clause(order_by, ascending, limit, agg_aliases)

        # Build complete query
        query = f"SELECT {select_clause} FROM `{TABLES['events']}` WHERE {where_clause} "
        if group_by:
            query += f"GROUP BY {', '.join(group_by)} "
        query += order_clause

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

        virtual_in_group = [
            str(g) for g in group_by if isinstance(g, str) and g in _GKG_COLUMN_TRANSFORMS
        ]
        if virtual_in_group:
            msg = (
                f"Virtual columns cannot be used in GROUP BY: {virtual_in_group}. "
                f"Use them only in aggregations (e.g., Aggregation(func=AggFunc.AVG, "
                f"column='V2Tone_Positive'))."
            )
            raise BigQueryError(msg)

        if not group_by and not aggregations:
            msg = "At least one of group_by or aggregations must be non-empty"
            raise BigQueryError(msg)

        # Validate aggregation columns (except "*")
        agg_columns = [a.column for a in aggregations if a.column != "*"]
        if agg_columns:
            _validate_columns(agg_columns, "gkg")

        # Rewrite GKG columns that require SQL-level extraction (e.g. V2Tone)
        transformed_aggs = [
            Aggregation(
                func=agg.func,
                column=_GKG_COLUMN_TRANSFORMS.get(agg.column, agg.column),
                alias=agg.alias,
            )
            if agg.column in _GKG_COLUMN_TRANSFORMS
            else agg
            for agg in aggregations
        ]

        # Build aggregation expressions
        agg_aliases = self._build_agg_select(transformed_aggs, parsed.select_parts)

        select_clause = ", ".join(parsed.select_parts)

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
        )
        if parsed.group_refs:
            query += f"GROUP BY {', '.join(parsed.group_refs)} "
        query += order_clause

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
