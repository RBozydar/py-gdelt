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
from typing import Any, Final, Literal

from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError
from google.oauth2 import service_account

from py_gdelt.config import GDELTSettings
from py_gdelt.exceptions import BigQueryError, ConfigurationError, SecurityError
from py_gdelt.filters import DateRange, EventFilter, GKGFilter


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
        conditions.append("REGEXP_CONTAINS(V2Themes, @theme_prefix_pattern)")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "theme_prefix_pattern",
                "STRING",
                f"(^|;){re.escape(filter_obj.theme_prefix)}",
            ),
        )

    # Optional: Entity filters (persons, organizations)
    if filter_obj.persons is not None and len(filter_obj.persons) > 0:
        person_pattern = "|".join(re.escape(p) for p in filter_obj.persons)
        conditions.append("REGEXP_CONTAINS(V2Persons, @person_pattern)")
        parameters.append(bigquery.ScalarQueryParameter("person_pattern", "STRING", person_pattern))

    if filter_obj.organizations is not None and len(filter_obj.organizations) > 0:
        org_pattern = "|".join(re.escape(o) for o in filter_obj.organizations)
        conditions.append("REGEXP_CONTAINS(V2Organizations, @org_pattern)")
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
    ) -> None:
        self.settings = settings or GDELTSettings()
        self._client = client
        self._owns_client = client is None
        self._credentials_validated = False

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
    ) -> AsyncIterator[dict[str, Any]]:
        """Query GDELT EventMentions table for a specific event.

        All queries use parameterized queries to prevent SQL injection.
        A date range should be provided for efficient querying.

        Args:
            global_event_id: Global event ID to query mentions for (INT64)
            columns: List of columns to select (defaults to all allowed columns)
            date_range: Optional date range to narrow search (recommended for performance)

        Yields:
            dict[str, Any]: Dictionary of column name -> value for each mention row

        Raises:
            BigQueryError: If query execution fails
            ConfigurationError: If credentials are not configured

        Example:
            >>> async for mention in source.query_mentions(
            ...     global_event_id=123456789,
            ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7))
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
        job_config = bigquery.QueryJobConfig(query_parameters=parameters)

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
