"""Tests for BigQuerySource module.

This module tests the BigQuery data source with a focus on:
- Security: Parameterized queries, column validation, path validation
- Credential handling: Validation, error messages, ADC vs explicit credentials
- Query building: WHERE clause generation, parameter binding
- SQL builder helpers: _build_events_sql, _build_gkg_sql, _build_mentions_sql
- Dry run estimation: _execute_dry_run, estimate_events, estimate_gkg, estimate_mentions
- Async execution: run_in_executor usage, streaming results
- BQ name mapping: PascalCase to snake_case conversion for _Raw* dataclasses
- Aggregation: GROUP BY queries, UNNEST, aliases, ORDER BY
- Column profiles: Predefined column subsets
- QueryMetadata / QueryEstimate model validation
- last_query_metadata lifecycle
"""

import re
from datetime import date, datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError
from pydantic import ValidationError

from py_gdelt.config import GDELTSettings
from py_gdelt.exceptions import BigQueryError, ConfigurationError, SecurityError
from py_gdelt.filters import DateRange, EventFilter, GKGFilter
from py_gdelt.sources.aggregation import (
    AggFunc,
    Aggregation,
    GKGUnnestField,
)
from py_gdelt.sources.bigquery import (
    _BQ_EVENT_MAP,
    _BQ_GKG_MAP,
    _BQ_MENTION_MAP,
    ALLOWED_COLUMNS,
    BigQuerySource,
    _bq_row_to_raw_event,
    _bq_row_to_raw_gkg,
    _bq_row_to_raw_mention,
    _build_where_clause_for_events,
    _build_where_clause_for_gkg,
    _validate_columns,
    _validate_credential_path,
)
from py_gdelt.sources.columns import EventColumns, GKGColumns, MentionColumns
from py_gdelt.sources.metadata import QueryEstimate, QueryMetadata


@pytest.fixture
def mock_settings_with_credentials(tmp_path: Path) -> GDELTSettings:
    """Create test settings with explicit credentials."""
    # Create a dummy credentials file
    creds_file = tmp_path / "credentials.json"
    creds_file.write_text('{"type": "service_account", "project_id": "test-project"}')

    return GDELTSettings(
        bigquery_project="test-project",
        bigquery_credentials=str(creds_file),
    )


@pytest.fixture
def mock_settings_with_adc() -> GDELTSettings:
    """Create test settings for Application Default Credentials."""
    return GDELTSettings(
        bigquery_project="test-project",
        bigquery_credentials=None,
    )


@pytest.fixture
def mock_bigquery_client() -> Mock:
    """Create a mock BigQuery client."""
    client = Mock(spec=bigquery.Client)
    return client


class TestCredentialValidation:
    """Test credential path validation and security."""

    def test_validate_credential_path_valid(self, tmp_path: Path) -> None:
        """Test validation of valid credential path."""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text('{"type": "service_account"}')

        result = _validate_credential_path(str(creds_file))
        assert result == creds_file

    def test_validate_credential_path_nonexistent(self, tmp_path: Path) -> None:
        """Test validation fails for nonexistent file."""
        creds_file = tmp_path / "nonexistent.json"

        with pytest.raises(ConfigurationError, match="not found"):
            _validate_credential_path(str(creds_file))

    def test_validate_credential_path_null_byte(self, tmp_path: Path) -> None:
        """Test validation rejects paths with null bytes."""
        malicious_path = str(tmp_path / "creds.json\x00.txt")

        with pytest.raises(SecurityError, match="null byte"):
            _validate_credential_path(malicious_path)

    def test_validate_credential_path_directory(self, tmp_path: Path) -> None:
        """Test validation rejects directories."""
        with pytest.raises(ConfigurationError, match="not a regular file"):
            _validate_credential_path(str(tmp_path))

    def test_validate_credential_path_with_expansion(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test path expansion works correctly."""
        # Create credentials in home dir
        monkeypatch.setenv("HOME", str(tmp_path))
        creds_dir = tmp_path / ".config" / "gcloud"
        creds_dir.mkdir(parents=True)
        creds_file = creds_dir / "credentials.json"
        creds_file.write_text('{"type": "service_account"}')

        # Test with ~ expansion
        result = _validate_credential_path("~/.config/gcloud/credentials.json")
        assert result == creds_file


class TestColumnValidation:
    """Test column allowlist validation."""

    def test_validate_columns_valid_events(self) -> None:
        """Test validation passes for valid events columns."""
        columns = ["GLOBALEVENTID", "Actor1CountryCode", "EventCode"]
        _validate_columns(columns, "events")  # Should not raise

    def test_validate_columns_valid_gkg(self) -> None:
        """Test validation passes for valid GKG columns."""
        columns = ["GKGRECORDID", "V2Themes", "V2Tone"]
        _validate_columns(columns, "gkg")  # Should not raise

    def test_validate_columns_invalid(self) -> None:
        """Test validation fails for invalid columns."""
        columns = ["GLOBALEVENTID", "MaliciousColumn", "DROP TABLE"]

        with pytest.raises(BigQueryError, match="Invalid columns"):
            _validate_columns(columns, "events")

    def test_validate_columns_sql_injection_attempt(self) -> None:
        """Test validation blocks SQL injection attempts."""
        columns = ["GLOBALEVENTID; DROP TABLE events; --"]

        with pytest.raises(BigQueryError, match="Invalid columns"):
            _validate_columns(columns, "events")


class TestWhereClauseBuilding:
    """Test WHERE clause generation with parameterized queries."""

    def test_build_where_clause_events_minimal(self) -> None:
        """Test building WHERE clause with minimal event filter."""
        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

        where_clause, parameters = _build_where_clause_for_events(filter_obj)

        # Should have date filters
        assert "_PARTITIONTIME >= @start_date" in where_clause
        assert "_PARTITIONTIME <= @end_date" in where_clause

        # Should have 2 parameters (start and end date)
        assert len(parameters) == 2
        assert parameters[0].name == "start_date"
        assert parameters[0].type_ == "TIMESTAMP"
        assert parameters[1].name == "end_date"
        assert parameters[1].type_ == "TIMESTAMP"

    def test_build_where_clause_events_with_filters(self) -> None:
        """Test building WHERE clause with multiple filters."""
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
            actor1_country="USA",
            actor2_country="CHN",
            event_code="141",
            min_tone=-5.0,
            max_tone=5.0,
        )

        where_clause, parameters = _build_where_clause_for_events(filter_obj)

        # Should contain all filter conditions
        assert "Actor1CountryCode = @actor1_country" in where_clause
        assert "Actor2CountryCode = @actor2_country" in where_clause
        assert "EventCode = @event_code" in where_clause
        assert "AvgTone >= @min_tone" in where_clause
        assert "AvgTone <= @max_tone" in where_clause

        # Should have 7 parameters (2 dates + 5 filters)
        assert len(parameters) == 7

        # Verify parameter types and values
        # Note: ISO3 codes (USA, CHN) are normalized to FIPS (US, CH)
        param_dict = {p.name: p for p in parameters}
        assert param_dict["actor1_country"].value == "US"
        assert param_dict["actor2_country"].value == "CH"
        assert param_dict["event_code"].value == "141"
        assert param_dict["min_tone"].value == -5.0
        assert param_dict["max_tone"].value == 5.0

    def test_build_where_clause_gkg_minimal(self) -> None:
        """Test building WHERE clause with minimal GKG filter."""
        filter_obj = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))

        where_clause, parameters = _build_where_clause_for_gkg(filter_obj)

        # Should have date filters
        assert "_PARTITIONTIME >= @start_date" in where_clause
        assert "_PARTITIONTIME <= @end_date" in where_clause

        # Should have 2 parameters
        assert len(parameters) == 2

    def test_build_where_clause_gkg_with_filters(self) -> None:
        """Test building WHERE clause with GKG filters."""
        # Note: Using only basic filters without validation to test WHERE clause building
        # Full validation is tested in the Pydantic filter tests
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            themes=["ENV_CLIMATECHANGE"],  # Using single valid theme
            country="USA",
            min_tone=-2.0,
            max_tone=2.0,
        )

        where_clause, parameters = _build_where_clause_for_gkg(filter_obj)

        # Should contain all filter conditions
        assert "REGEXP_CONTAINS(V2Themes, @theme_pattern)" in where_clause
        assert "REGEXP_CONTAINS(V2Locations, @country_pattern)" in where_clause
        assert (
            "SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(0)] AS FLOAT64) >= @min_tone" in where_clause
        )

        # Verify theme pattern
        param_dict = {p.name: p for p in parameters}
        theme_value = param_dict["theme_pattern"].value
        assert isinstance(theme_value, str)
        assert "ENV_CLIMATECHANGE" in theme_value

        # Verify country pattern uses delimited matching
        country_value = param_dict["country_pattern"].value
        assert isinstance(country_value, str)
        assert country_value == "#US#"

    def test_theme_prefix_no_substring_match(self) -> None:
        """Verify theme_prefix doesn't match substrings in the middle of themes.

        The pattern (^|;)prefix should only match when prefix appears at the
        start of the string or immediately after a semicolon delimiter.
        This prevents "water" from matching "freshwater".

        Note: Pattern is lowercased for case-insensitive matching (LOWER() is
        applied to the column in the SQL query).
        """
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            theme_prefix="WATER",
        )

        _, parameters = _build_where_clause_for_gkg(filter_obj)

        # Verify the pattern anchors at theme boundaries and is lowercased
        param_dict = {p.name: p for p in parameters}
        pattern_value = param_dict["theme_prefix_pattern"].value
        assert isinstance(pattern_value, str)
        assert pattern_value == r"(^|;)water"

        # Test with actual regex to confirm behavior (using lowercase since
        # LOWER() is applied to the column data in the actual SQL query)
        assert re.search(pattern_value, "water;other")  # Should match (at start)
        assert re.search(pattern_value, "water_supply")  # Should match (at start, prefix)
        assert re.search(pattern_value, "other;water")  # Should match (after semicolon)
        assert re.search(pattern_value, "other;water_security")  # Should match (after semicolon)
        assert not re.search(pattern_value, "freshwater")  # Should NOT match (in middle)
        assert not re.search(pattern_value, "other;freshwater")  # Should NOT match (in middle)
        assert not re.search(pattern_value, "dewater")  # Should NOT match (in middle)


class TestBigQuerySourceInit:
    """Test BigQuerySource initialization."""

    def test_init_with_defaults(self) -> None:
        """Test initialization with default parameters."""
        source = BigQuerySource()

        assert source.settings is not None
        assert source._client is None
        assert source._owns_client is True

    def test_init_with_custom_settings(
        self,
        mock_settings_with_credentials: GDELTSettings,
    ) -> None:
        """Test initialization with custom settings."""
        source = BigQuerySource(settings=mock_settings_with_credentials)

        assert source.settings is mock_settings_with_credentials

    def test_init_with_external_client(self, mock_bigquery_client: Mock) -> None:
        """Test initialization with externally provided client."""
        source = BigQuerySource(client=mock_bigquery_client)

        assert source._client is mock_bigquery_client
        assert source._owns_client is False

    async def test_context_manager(self) -> None:
        """Test async context manager."""
        async with BigQuerySource() as source:
            assert source is not None

    def test_validate_credentials_no_config(self) -> None:
        """Test credential validation fails with no configuration."""
        settings = GDELTSettings(
            bigquery_project=None,
            bigquery_credentials=None,
        )
        source = BigQuerySource(settings=settings)

        with pytest.raises(ConfigurationError, match="not configured"):
            source._validate_credentials()

    def test_validate_credentials_with_adc(self, mock_settings_with_adc: GDELTSettings) -> None:
        """Test credential validation passes with ADC configuration."""
        source = BigQuerySource(settings=mock_settings_with_adc)

        # Should not raise
        source._validate_credentials()
        assert source._credentials_validated is True

    def test_validate_credentials_with_explicit_creds(
        self,
        mock_settings_with_credentials: GDELTSettings,
    ) -> None:
        """Test credential validation passes with explicit credentials."""
        source = BigQuerySource(settings=mock_settings_with_credentials)

        # Should not raise
        source._validate_credentials()
        assert source._credentials_validated is True


class TestBigQuerySourceQueries:
    """Test BigQuery query execution."""

    @pytest.mark.asyncio
    async def test_query_events_basic(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test basic events query execution."""
        # Mock query job
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_rows = 10
        mock_job.total_bytes_processed = 1024
        mock_job.__iter__ = Mock(
            return_value=iter(
                [
                    {"GLOBALEVENTID": "123", "EventCode": "141"},
                    {"GLOBALEVENTID": "456", "EventCode": "142"},
                ],
            ),
        )

        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        # Execute query
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor1_country="USA",
        )

        results = [row async for row in source.query_events(filter_obj, limit=10)]

        # Verify results
        assert len(results) == 2
        assert results[0]["GLOBALEVENTID"] == "123"
        assert results[1]["EventCode"] == "142"

        # Verify query was called with parameterized query
        assert mock_bigquery_client.query.called
        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]

        # Verify parameterized query (no direct value interpolation)
        assert "@start_date" in query
        assert "@end_date" in query
        assert "@actor1_country" in query
        assert "LIMIT 10" in query

        # Verify query parameters were passed
        job_config = call_args[1]["job_config"]
        assert len(job_config.query_parameters) >= 3  # start_date, end_date, actor1_country

    @pytest.mark.asyncio
    async def test_query_events_column_validation(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test column validation in events query."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

        # Should raise error for invalid columns
        with pytest.raises(BigQueryError, match="Invalid columns"):
            async for _ in source.query_events(
                filter_obj,
                columns=["GLOBALEVENTID", "InvalidColumn"],
            ):
                pass

    @pytest.mark.asyncio
    async def test_query_gkg_basic(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test basic GKG query execution."""
        # Mock query job
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_rows = 5
        mock_job.total_bytes_processed = 2048
        mock_job.__iter__ = Mock(
            return_value=iter(
                [
                    {"GKGRECORDID": "abc", "V2Themes": "ENV_CLIMATECHANGE"},
                ],
            ),
        )

        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        # Execute query
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            themes=["ENV_CLIMATECHANGE"],
        )

        results = [row async for row in source.query_gkg(filter_obj)]

        # Verify results
        assert len(results) == 1
        assert results[0]["GKGRECORDID"] == "abc"

        # Verify parameterized query
        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]
        assert "@theme_pattern" in query

    @pytest.mark.asyncio
    async def test_query_mentions_basic(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test basic mentions query execution."""
        # Mock query job
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_rows = 3
        mock_job.total_bytes_processed = 512
        mock_job.__iter__ = Mock(
            return_value=iter(
                [
                    {"GLOBALEVENTID": "123", "MentionSourceName": "BBC"},
                    {"GLOBALEVENTID": "123", "MentionSourceName": "CNN"},
                ],
            ),
        )

        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        # Execute query
        results = [
            row
            async for row in source.query_mentions(
                global_event_id="123",
                date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
            )
        ]

        # Verify results
        assert len(results) == 2
        assert all(r["GLOBALEVENTID"] == "123" for r in results)

        # Verify parameterized query
        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]
        assert "@event_id" in query
        assert "GLOBALEVENTID = @event_id" in query

    @pytest.mark.asyncio
    async def test_query_error_handling(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test error handling in query execution."""
        # Mock query to raise error
        mock_bigquery_client.query.side_effect = GoogleCloudError("Query failed")  # type: ignore[no-untyped-call]

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

        # Should raise BigQueryError
        with pytest.raises(BigQueryError, match="Query failed"):
            async for _ in source.query_events(filter_obj):
                pass

    @pytest.mark.asyncio
    async def test_query_without_credentials(self) -> None:
        """Test query fails without credentials configured."""
        settings = GDELTSettings(
            bigquery_project=None,
            bigquery_credentials=None,
        )
        source = BigQuerySource(settings=settings)

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

        # Should raise ConfigurationError
        with pytest.raises(ConfigurationError, match="not configured"):
            async for _ in source.query_events(filter_obj):
                pass


class TestSecurityFeatures:
    """Test security features of BigQuerySource."""

    def test_no_string_formatting_in_queries(self) -> None:
        """Test that queries use parameterized queries, not string formatting.

        Note: Pydantic validation catches invalid country codes before they reach
        the query builder. This test verifies that valid inputs are properly
        parameterized, which prevents SQL injection at the database layer.
        """
        # Test with valid input to verify parameterization
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor1_country="USA",  # Valid country code
        )

        where_clause, parameters = _build_where_clause_for_events(filter_obj)

        # Verify parameterization (no direct value in SQL)
        # Note: ISO3 "USA" is normalized to FIPS "US"
        assert "USA" not in where_clause  # Value should not be in SQL string
        assert "US" not in where_clause  # Normalized value should not be in SQL string either
        assert "@actor1_country" in where_clause  # Parameter placeholder should be present

        # Find the actor1_country parameter
        actor1_param = next(p for p in parameters if p.name == "actor1_country")
        assert actor1_param.value == "US"  # Stored safely as parameter (normalized to FIPS)

        # Test that invalid country codes are caught by Pydantic validation
        from py_gdelt.exceptions import InvalidCodeError

        with pytest.raises(InvalidCodeError):
            EventFilter(
                date_range=DateRange(start=date(2024, 1, 1)),
                actor1_country="USA'; DROP TABLE events; --",  # SQL injection attempt
            )

    def test_column_allowlist_prevents_unauthorized_access(self) -> None:
        """Test that column allowlist prevents access to non-allowed columns."""
        # Attempt to access columns not in allowlist
        with pytest.raises(BigQueryError, match="Invalid columns"):
            _validate_columns(["SecretColumn", "HiddenData"], "events")

    def test_mandatory_partition_filter(self) -> None:
        """Test that all queries include mandatory partition filters."""
        # Events query
        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
        where_clause, _ = _build_where_clause_for_events(filter_obj)

        # Must include partition filter
        assert "_PARTITIONTIME >= @start_date" in where_clause
        assert "_PARTITIONTIME <= @end_date" in where_clause

        # GKG query
        gkg_filter = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))
        where_clause, _ = _build_where_clause_for_gkg(gkg_filter)

        assert "_PARTITIONTIME >= @start_date" in where_clause
        assert "_PARTITIONTIME <= @end_date" in where_clause

    def test_credentials_never_in_error_messages(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that credentials are never exposed in error messages."""
        # Mock query to raise error
        mock_bigquery_client.query.side_effect = GoogleCloudError("Authentication failed")  # type: ignore[no-untyped-call]

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

        # Error should not contain credential path or content
        try:
            results: list[dict[str, Any]] = []

            async def collect() -> None:
                nonlocal results
                results.extend([row async for row in source.query_events(filter_obj)])

            import asyncio

            asyncio.run(collect())
        except BigQueryError as e:
            error_msg = str(e)
            assert "credentials.json" not in error_msg.lower()
            assert "service_account" not in error_msg.lower()


class TestBQNameMapping:
    """Test BigQuery column name → _Raw* field name mapping."""

    def test_bq_event_map_keys_match_allowed_columns(self) -> None:
        assert set(_BQ_EVENT_MAP.keys()) == ALLOWED_COLUMNS["events"]

    def test_bq_gkg_map_keys_match_allowed_columns(self) -> None:
        assert set(_BQ_GKG_MAP.keys()) == ALLOWED_COLUMNS["gkg"]

    def test_bq_mention_map_keys_match_allowed_columns(self) -> None:
        assert set(_BQ_MENTION_MAP.keys()) == ALLOWED_COLUMNS["eventmentions"]

    def test_bq_row_to_raw_event_basic(self) -> None:
        row = {
            "GLOBALEVENTID": "123456",
            "SQLDATE": "20240101",
            "MonthYear": "202401",
            "Year": "2024",
            "FractionDate": "2024.0001",
            "Actor1Code": "USA",
            "Actor1Name": "UNITED STATES",
            "Actor1CountryCode": "US",
            "IsRootEvent": "1",
            "EventCode": "010",
            "EventBaseCode": "01",
            "EventRootCode": "01",
            "QuadClass": "1",
            "GoldsteinScale": "3.5",
            "NumMentions": "10",
            "NumSources": "5",
            "NumArticles": "8",
            "AvgTone": "2.5",
            "DATEADDED": "20240101120000",
            "SOURCEURL": "http://example.com",
        }

        raw = _bq_row_to_raw_event(row)
        assert raw.global_event_id == "123456"
        assert raw.sql_date == "20240101"
        assert raw.actor1_code == "USA"
        assert raw.actor1_name == "UNITED STATES"
        assert raw.event_code == "010"
        assert raw.avg_tone == "2.5"
        assert raw.source_url == "http://example.com"

    def test_bq_row_to_raw_event_none_required_field(self) -> None:
        row: dict[str, Any] = {
            "GLOBALEVENTID": None,
            "SQLDATE": "20240101",
            "MonthYear": "202401",
            "Year": "2024",
            "FractionDate": "2024.0001",
            "IsRootEvent": "1",
            "EventCode": "010",
            "EventBaseCode": "01",
            "EventRootCode": "01",
            "QuadClass": "1",
            "GoldsteinScale": "3.5",
            "NumMentions": "10",
            "NumSources": "5",
            "NumArticles": "8",
            "AvgTone": "2.5",
            "DATEADDED": "20240101120000",
        }

        raw = _bq_row_to_raw_event(row)
        # None on a required field should become ""
        assert raw.global_event_id == ""

    def test_bq_row_to_raw_event_none_optional_field(self) -> None:
        row: dict[str, Any] = {
            "GLOBALEVENTID": "123",
            "SQLDATE": "20240101",
            "MonthYear": "202401",
            "Year": "2024",
            "FractionDate": "2024.0001",
            "Actor1Code": None,
            "Actor1Name": None,
            "IsRootEvent": "1",
            "EventCode": "010",
            "EventBaseCode": "01",
            "EventRootCode": "01",
            "QuadClass": "1",
            "GoldsteinScale": "3.5",
            "NumMentions": "10",
            "NumSources": "5",
            "NumArticles": "8",
            "AvgTone": "2.5",
            "DATEADDED": "20240101120000",
        }

        raw = _bq_row_to_raw_event(row)
        # None on optional fields should stay None
        assert raw.actor1_code is None
        assert raw.actor1_name is None

    def test_bq_row_to_raw_event_unknown_columns_dropped(self) -> None:
        row: dict[str, Any] = {
            "GLOBALEVENTID": "123",
            "SQLDATE": "20240101",
            "MonthYear": "202401",
            "Year": "2024",
            "FractionDate": "2024.0001",
            "IsRootEvent": "1",
            "EventCode": "010",
            "EventBaseCode": "01",
            "EventRootCode": "01",
            "QuadClass": "1",
            "GoldsteinScale": "3.5",
            "NumMentions": "10",
            "NumSources": "5",
            "NumArticles": "8",
            "AvgTone": "2.5",
            "DATEADDED": "20240101120000",
            "UnknownColumn": "should_be_dropped",
            "AnotherExtra": 42,
        }

        # Should not raise despite extra keys
        raw = _bq_row_to_raw_event(row)
        assert raw.global_event_id == "123"
        # Extra keys should not appear as attributes
        assert not hasattr(raw, "unknown_column")
        assert not hasattr(raw, "another_extra")

    def test_bq_row_to_raw_gkg_basic(self) -> None:
        row = {
            "GKGRECORDID": "20240101-abc",
            "DATE": "20240101120000",
            "SourceCollectionIdentifier": "1",
            "SourceCommonName": "example.com",
            "DocumentIdentifier": "http://example.com/article",
            "Counts": "",
            "V2Counts": "",
            "Themes": "ENV_CLIMATECHANGE",
            "V2Themes": "ENV_CLIMATECHANGE,1",
            "Locations": "",
            "V2Locations": "",
            "Persons": "",
            "V2Persons": "",
            "Organizations": "",
            "V2Organizations": "",
            "V2Tone": "-2.5,3.0,5.5,1.0,10.0,5.0,200",
            "Dates": "",
            "GCAM": "",
        }

        raw = _bq_row_to_raw_gkg(row)
        assert raw.gkg_record_id == "20240101-abc"
        assert raw.source_common_name == "example.com"
        assert raw.tone == "-2.5,3.0,5.5,1.0,10.0,5.0,200"
        # Optional fields not present should be None
        assert raw.sharing_image is None
        assert raw.quotations is None

    def test_bq_row_to_raw_mention_basic(self) -> None:
        row = {
            "GLOBALEVENTID": "123456",
            "EventTimeDate": "20240101120000",
            "MentionTimeDate": "20240101130000",
            "MentionType": "1",
            "MentionSourceName": "bbc.co.uk",
            "MentionIdentifier": "http://bbc.co.uk/article",
            "SentenceID": "3",
            "Actor1CharOffset": "100",
            "Actor2CharOffset": "200",
            "ActionCharOffset": "150",
            "InRawText": "1",
            "Confidence": "80",
            "MentionDocLen": "5000",
            "MentionDocTone": "-1.5",
        }

        raw = _bq_row_to_raw_mention(row)
        assert raw.global_event_id == "123456"
        assert raw.mention_source_name == "bbc.co.uk"
        assert raw.confidence == "80"
        # Optional fields not present should be None
        assert raw.mention_doc_translation_info is None
        assert raw.extras is None

    def test_bq_row_to_raw_mention_sets_empty_time_full(self) -> None:
        row = {
            "GLOBALEVENTID": "123",
            "EventTimeDate": "20240101120000",
            "MentionTimeDate": "20240101130000",
            "MentionType": "1",
            "MentionSourceName": "cnn.com",
            "MentionIdentifier": "http://cnn.com/article",
            "SentenceID": "1",
            "Actor1CharOffset": "50",
            "Actor2CharOffset": "100",
            "ActionCharOffset": "75",
            "InRawText": "1",
            "Confidence": "90",
            "MentionDocLen": "3000",
            "MentionDocTone": "0.5",
        }

        raw = _bq_row_to_raw_mention(row)
        # BQ eventmentions table lacks these columns; they should be empty strings
        assert raw.event_time_full == ""
        assert raw.mention_time_full == ""


class TestBigQueryAggregation:
    """Test BigQuery aggregation query building and execution."""

    @pytest.mark.asyncio
    async def test_aggregate_events_basic(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_bytes_processed = 5000
        mock_job.__iter__ = Mock(
            return_value=iter(
                [
                    {"EventRootCode": "14", "cnt": 100},
                    {"EventRootCode": "01", "cnt": 50},
                ],
            ),
        )

        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
        result = await source.aggregate_events(
            filter_obj,
            group_by=["EventRootCode"],
            aggregations=[Aggregation(func=AggFunc.COUNT, alias="cnt")],
            limit=10,
        )

        assert result.total_rows == 2
        assert result.rows[0]["EventRootCode"] == "14"
        assert result.bytes_processed == 5000

        # Verify SQL structure
        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]
        assert "GROUP BY" in query
        assert "EventRootCode" in query
        assert "COUNT(*) AS cnt" in query
        assert "LIMIT 10" in query
        assert "ORDER BY" in query  # auto-order when limit set

    @pytest.mark.asyncio
    async def test_aggregate_events_invalid_group_by(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
        with pytest.raises(BigQueryError, match="Invalid columns"):
            await source.aggregate_events(
                filter_obj,
                group_by=["InvalidColumn"],
                aggregations=[Aggregation(func=AggFunc.COUNT, alias="cnt")],
            )

    @pytest.mark.asyncio
    async def test_aggregate_events_invalid_agg_column(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
        with pytest.raises(BigQueryError, match="Invalid columns"):
            await source.aggregate_events(
                filter_obj,
                group_by=["EventRootCode"],
                aggregations=[
                    Aggregation(func=AggFunc.AVG, column="NonexistentColumn", alias="avg_bad"),
                ],
            )

    @pytest.mark.asyncio
    async def test_aggregate_events_invalid_alias(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
        with pytest.raises(SecurityError, match="Invalid alias"):
            await source.aggregate_events(
                filter_obj,
                group_by=["EventRootCode"],
                aggregations=[
                    Aggregation(func=AggFunc.COUNT, alias="cnt; DROP TABLE --"),
                ],
            )

    @pytest.mark.asyncio
    async def test_aggregate_events_count_distinct(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_bytes_processed = 3000
        mock_job.__iter__ = Mock(return_value=iter([{"EventRootCode": "14", "unique_actors": 42}]))
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
        await source.aggregate_events(
            filter_obj,
            group_by=["EventRootCode"],
            aggregations=[
                Aggregation(
                    func=AggFunc.COUNT_DISTINCT,
                    column="Actor1CountryCode",
                    alias="unique_actors",
                ),
            ],
        )

        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]
        assert "COUNT(DISTINCT Actor1CountryCode)" in query

    @pytest.mark.asyncio
    async def test_aggregate_events_auto_alias(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_bytes_processed = 1000
        mock_job.__iter__ = Mock(return_value=iter([{"EventRootCode": "14", "count_star": 10}]))
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
        # No alias provided - should auto-generate
        await source.aggregate_events(
            filter_obj,
            group_by=["EventRootCode"],
            aggregations=[Aggregation(func=AggFunc.COUNT)],
        )

        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]
        # Auto-generated alias should be "count_star"
        assert "COUNT(*) AS count_star" in query

    @pytest.mark.asyncio
    async def test_aggregate_events_limit_with_default_order(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_bytes_processed = 1000
        mock_job.__iter__ = Mock(return_value=iter([]))
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
        await source.aggregate_events(
            filter_obj,
            group_by=["EventRootCode"],
            aggregations=[Aggregation(func=AggFunc.COUNT, alias="cnt")],
            limit=5,
        )

        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]
        # When limit is set and no explicit order_by, should order by first agg alias DESC
        assert "ORDER BY cnt DESC" in query
        assert "LIMIT 5" in query

    @pytest.mark.asyncio
    async def test_aggregate_events_explicit_order(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_bytes_processed = 1000
        mock_job.__iter__ = Mock(return_value=iter([]))
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
        await source.aggregate_events(
            filter_obj,
            group_by=["EventRootCode"],
            aggregations=[Aggregation(func=AggFunc.COUNT, alias="cnt")],
            order_by="cnt",
            ascending=True,
        )

        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]
        assert "ORDER BY cnt ASC" in query

    @pytest.mark.asyncio
    async def test_aggregate_gkg_flat_columns(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_bytes_processed = 2000
        mock_job.__iter__ = Mock(
            return_value=iter([{"SourceCommonName": "bbc.co.uk", "cnt": 500}]),
        )
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))
        result = await source.aggregate_gkg(
            filter_obj,
            group_by=["SourceCommonName"],
            aggregations=[Aggregation(func=AggFunc.COUNT, alias="cnt")],
        )

        assert result.total_rows == 1
        assert result.rows[0]["SourceCommonName"] == "bbc.co.uk"

        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]
        assert "GROUP BY" in query
        assert "SourceCommonName" in query
        # No UNNEST for flat columns
        assert "UNNEST" not in query

    @pytest.mark.asyncio
    async def test_aggregate_gkg_with_unnest(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_bytes_processed = 8000
        mock_job.__iter__ = Mock(
            return_value=iter(
                [
                    {"themes": "ENV_CLIMATECHANGE", "cnt": 1000},
                    {"themes": "TAX_POLICY", "cnt": 500},
                ],
            ),
        )
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))
        result = await source.aggregate_gkg(
            filter_obj,
            group_by=[GKGUnnestField.THEMES],
            aggregations=[Aggregation(func=AggFunc.COUNT, alias="cnt")],
            limit=20,
        )

        assert result.total_rows == 2
        assert result.group_by == ["themes"]

        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]
        assert "UNNEST(SPLIT(" in query
        assert "V2Themes" in query
        assert "SPLIT(item" in query

    @pytest.mark.asyncio
    async def test_aggregate_gkg_multiple_unnest_fields_error(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))
        with pytest.raises(BigQueryError, match="Only one GKGUnnestField"):
            await source.aggregate_gkg(
                filter_obj,
                group_by=[GKGUnnestField.THEMES, GKGUnnestField.PERSONS],
                aggregations=[Aggregation(func=AggFunc.COUNT, alias="cnt")],
            )

    @pytest.mark.asyncio
    async def test_aggregate_gkg_unnest_filters_empty(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_bytes_processed = 1000
        mock_job.__iter__ = Mock(return_value=iter([]))
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))
        await source.aggregate_gkg(
            filter_obj,
            group_by=[GKGUnnestField.ORGANIZATIONS],
            aggregations=[Aggregation(func=AggFunc.COUNT, alias="cnt")],
        )

        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]
        # Should filter out empty string items from UNNEST
        assert "item != ''" in query

    @pytest.mark.asyncio
    async def test_aggregate_events_empty_group_by(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that aggregate_events with empty group_by omits GROUP BY clause."""
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_bytes_processed = 1000
        mock_job.__iter__ = Mock(return_value=iter([{"total": 42}]))
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
        result = await source.aggregate_events(
            filter_obj,
            group_by=[],
            aggregations=[Aggregation(func=AggFunc.COUNT, alias="total")],
        )

        assert result.total_rows == 1
        assert result.rows[0]["total"] == 42

        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]
        assert "GROUP BY" not in query
        assert "COUNT(*) AS total" in query

    @pytest.mark.asyncio
    async def test_aggregate_gkg_empty_group_by(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that aggregate_gkg with empty group_by omits GROUP BY clause."""
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_bytes_processed = 1000
        mock_job.__iter__ = Mock(return_value=iter([{"total": 99}]))
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))
        result = await source.aggregate_gkg(
            filter_obj,
            group_by=[],
            aggregations=[Aggregation(func=AggFunc.COUNT, alias="total")],
        )

        assert result.total_rows == 1

        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]
        assert "GROUP BY" not in query

    @pytest.mark.asyncio
    async def test_aggregate_events_empty_both_raises(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that aggregate_events raises when both group_by and aggregations are empty."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
        with pytest.raises(BigQueryError, match=r"(?i)at least one"):
            await source.aggregate_events(
                filter_obj,
                group_by=[],
                aggregations=[],
            )

    @pytest.mark.asyncio
    async def test_aggregate_gkg_v2tone_auto_transforms(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """V2Tone column should be auto-transformed to extract numeric tone score."""
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_bytes_processed = 4000
        mock_job.__iter__ = Mock(
            return_value=iter(
                [{"SourceCommonName": "bbc.co.uk", "avg_tone": -2.5}],
            ),
        )
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))
        result = await source.aggregate_gkg(
            filter_obj,
            group_by=["SourceCommonName"],
            aggregations=[
                Aggregation(func=AggFunc.AVG, column="V2Tone", alias="avg_tone"),
            ],
        )

        assert result.total_rows == 1

        call_args = mock_bigquery_client.query.call_args
        query = call_args[0][0]
        # Should contain the SAFE_CAST extraction, not bare AVG(V2Tone)
        assert "SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(0)] AS FLOAT64)" in query
        assert "AVG(V2Tone)" not in query

    @pytest.mark.asyncio
    async def test_aggregate_gkg_empty_both_raises(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that aggregate_gkg raises when both group_by and aggregations are empty."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))
        with pytest.raises(BigQueryError, match=r"(?i)at least one"):
            await source.aggregate_gkg(
                filter_obj,
                group_by=[],
                aggregations=[],
            )


class TestColumnProfiles:
    """Test predefined column subsets are valid subsets of allowed columns."""

    def test_event_columns_core_subset_of_allowed(self) -> None:
        assert ALLOWED_COLUMNS["events"] >= EventColumns.CORE

    def test_event_columns_actors_subset_of_allowed(self) -> None:
        assert ALLOWED_COLUMNS["events"] >= EventColumns.ACTORS

    def test_event_columns_geography_subset_of_allowed(self) -> None:
        assert ALLOWED_COLUMNS["events"] >= EventColumns.GEOGRAPHY

    def test_event_columns_metrics_subset_of_allowed(self) -> None:
        assert ALLOWED_COLUMNS["events"] >= EventColumns.METRICS

    def test_gkg_columns_core_subset_of_allowed(self) -> None:
        assert ALLOWED_COLUMNS["gkg"] >= GKGColumns.CORE

    def test_gkg_columns_entities_subset_of_allowed(self) -> None:
        assert ALLOWED_COLUMNS["gkg"] >= GKGColumns.ENTITIES

    def test_gkg_columns_full_text_subset_of_allowed(self) -> None:
        assert ALLOWED_COLUMNS["gkg"] >= GKGColumns.FULL_TEXT

    def test_mention_columns_core_subset_of_allowed(self) -> None:
        assert ALLOWED_COLUMNS["eventmentions"] >= MentionColumns.CORE


class TestEndpointAggregateNoBigQuery:
    """Test that endpoint aggregate methods raise when BigQuery is not configured."""

    @pytest.mark.asyncio
    async def test_events_aggregate_no_bigquery_raises(self) -> None:
        from py_gdelt.endpoints.events import EventsEndpoint

        mock_file_source = MagicMock()
        endpoint = EventsEndpoint(
            file_source=mock_file_source,
            bigquery_source=None,
        )

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))
        with pytest.raises(ConfigurationError, match="Aggregation queries require BigQuery"):
            await endpoint.aggregate(
                filter_obj,
                group_by=["EventRootCode"],
                aggregations=[Aggregation(func=AggFunc.COUNT, alias="cnt")],
            )

    @pytest.mark.asyncio
    async def test_gkg_aggregate_no_bigquery_raises(self) -> None:
        from py_gdelt.endpoints.gkg import GKGEndpoint

        mock_file_source = MagicMock()
        endpoint = GKGEndpoint(file_source=mock_file_source, bigquery_source=None)

        filter_obj = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))
        with pytest.raises(ConfigurationError, match="Aggregation queries require BigQuery"):
            await endpoint.aggregate(
                filter_obj,
                group_by=["SourceCommonName"],
                aggregations=[Aggregation(func=AggFunc.COUNT, alias="cnt")],
            )


class TestBuildEventsSql:
    """Test the _build_events_sql helper."""

    def test_returns_default_columns_when_none(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that passing columns=None selects all allowed event columns."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

        query, _ = source._build_events_sql(filter_obj, columns=None, limit=None)

        for col in sorted(ALLOWED_COLUMNS["events"]):
            assert col in query

    def test_respects_explicit_columns(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that explicit columns are used in SELECT."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

        query, _ = source._build_events_sql(
            filter_obj,
            columns=["GLOBALEVENTID", "EventCode"],
            limit=None,
        )

        assert "GLOBALEVENTID" in query
        assert "EventCode" in query
        # Should not contain other columns
        assert "Actor1Name" not in query

    def test_includes_limit(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that LIMIT clause is appended when specified."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

        query, _ = source._build_events_sql(filter_obj, columns=None, limit=50)

        assert "LIMIT 50" in query

    def test_no_limit_when_none(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that no LIMIT clause when limit is None."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

        query, _ = source._build_events_sql(filter_obj, columns=None, limit=None)

        assert "LIMIT" not in query

    def test_invalid_columns_raises(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that invalid columns raise BigQueryError."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

        with pytest.raises(BigQueryError, match="Invalid columns"):
            source._build_events_sql(
                filter_obj,
                columns=["GLOBALEVENTID", "INVALID_COL"],
                limit=None,
            )

    def test_parameters_include_filters(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that query parameters include all filter values."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor1_country="USA",
        )

        query, parameters = source._build_events_sql(filter_obj, columns=None, limit=None)

        assert "@actor1_country" in query
        param_names = {p.name for p in parameters}
        assert "start_date" in param_names
        assert "end_date" in param_names
        assert "actor1_country" in param_names


class TestBuildGkgSql:
    """Test the _build_gkg_sql helper."""

    def test_returns_default_columns_when_none(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that passing columns=None selects all allowed GKG columns."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        filter_obj = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))

        query, _ = source._build_gkg_sql(filter_obj, columns=None, limit=None)

        for col in sorted(ALLOWED_COLUMNS["gkg"]):
            assert col in query

    def test_includes_theme_filter_parameters(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that GKG theme filter generates correct parameters."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            themes=["ENV_CLIMATECHANGE"],
        )

        query, parameters = source._build_gkg_sql(filter_obj, columns=None, limit=None)

        assert "@theme_pattern" in query
        param_dict = {p.name: p for p in parameters}
        assert "theme_pattern" in param_dict

    def test_invalid_columns_raises(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that invalid columns raise BigQueryError."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        filter_obj = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))

        with pytest.raises(BigQueryError, match="Invalid columns"):
            source._build_gkg_sql(
                filter_obj,
                columns=["GKGRECORDID", "INVALID_COL"],
                limit=None,
            )


class TestBuildMentionsSql:
    """Test the _build_mentions_sql helper."""

    def test_returns_default_columns_when_none(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that passing columns=None selects all allowed mention columns."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )

        query, _ = source._build_mentions_sql(
            global_event_id=123,
            columns=None,
            date_range=None,
            limit=None,
        )

        for col in sorted(ALLOWED_COLUMNS["eventmentions"]):
            assert col in query

    def test_includes_event_id_parameter(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that global_event_id is passed as INT64 parameter."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )

        query, parameters = source._build_mentions_sql(
            global_event_id=999,
            columns=None,
            date_range=None,
            limit=None,
        )

        assert "GLOBALEVENTID = @event_id" in query
        param_dict = {p.name: p for p in parameters}
        assert param_dict["event_id"].type_ == "INT64"
        assert param_dict["event_id"].value == 999

    def test_includes_date_range_parameters(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that date_range adds partition time parameters."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )

        query, parameters = source._build_mentions_sql(
            global_event_id=123,
            columns=None,
            date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
            limit=None,
        )

        assert "_PARTITIONTIME >= @start_date" in query
        assert "_PARTITIONTIME <= @end_date" in query
        param_names = {p.name for p in parameters}
        assert "start_date" in param_names
        assert "end_date" in param_names

    def test_no_date_range_parameters_when_none(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that no partition parameters when date_range is None."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )

        query, parameters = source._build_mentions_sql(
            global_event_id=123,
            columns=None,
            date_range=None,
            limit=None,
        )

        assert "_PARTITIONTIME" not in query
        param_names = {p.name for p in parameters}
        assert "start_date" not in param_names

    def test_invalid_columns_raises(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that invalid columns raise BigQueryError."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )

        with pytest.raises(BigQueryError, match="Invalid columns"):
            source._build_mentions_sql(
                global_event_id=123,
                columns=["GLOBALEVENTID", "INVALID_COL"],
                date_range=None,
                limit=None,
            )


class TestExecuteDryRun:
    """Test the _execute_dry_run method."""

    @pytest.mark.asyncio
    async def test_returns_query_estimate(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that dry run returns a QueryEstimate with bytes and SQL."""
        mock_job = Mock()
        mock_job.total_bytes_processed = 1_048_576
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        result = await source._execute_dry_run("SELECT 1", [])

        assert isinstance(result, QueryEstimate)
        assert result.bytes_processed == 1_048_576
        assert result.query == "SELECT 1"

    @pytest.mark.asyncio
    async def test_strips_query_whitespace(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that the query string is stripped in the estimate."""
        mock_job = Mock()
        mock_job.total_bytes_processed = 500
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        result = await source._execute_dry_run("  SELECT 1  \n", [])

        assert result.query == "SELECT 1"

    @pytest.mark.asyncio
    async def test_uses_dry_run_config(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that job config sets dry_run=True and use_query_cache=False."""
        mock_job = Mock()
        mock_job.total_bytes_processed = 100
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        await source._execute_dry_run("SELECT 1", [])

        call_args = mock_bigquery_client.query.call_args
        job_config = call_args[1]["job_config"]
        assert job_config.dry_run is True
        assert job_config.use_query_cache is False

    @pytest.mark.asyncio
    async def test_does_not_apply_maximum_bytes_billed(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that dry run does not set maximum_bytes_billed."""
        mock_job = Mock()
        mock_job.total_bytes_processed = 100
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
            maximum_bytes_billed=1_000_000,
        )
        source._credentials_validated = True

        await source._execute_dry_run("SELECT 1", [])

        call_args = mock_bigquery_client.query.call_args
        job_config = call_args[1]["job_config"]
        assert job_config.maximum_bytes_billed is None

    @pytest.mark.asyncio
    async def test_handles_none_bytes_processed(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that None total_bytes_processed defaults to 0."""
        mock_job = Mock()
        mock_job.total_bytes_processed = None
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        result = await source._execute_dry_run("SELECT 1", [])

        assert result.bytes_processed == 0

    @pytest.mark.asyncio
    async def test_google_cloud_error_raises_bigquery_error(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that GoogleCloudError is wrapped as BigQueryError."""
        mock_bigquery_client.query.side_effect = GoogleCloudError("Dry run failed")  # type: ignore[no-untyped-call]

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        with pytest.raises(BigQueryError, match="dry run failed"):
            await source._execute_dry_run("SELECT 1", [])


class TestEstimateMethods:
    """Test estimate_events, estimate_gkg, and estimate_mentions."""

    @pytest.mark.asyncio
    async def test_estimate_events_calls_builder_and_dry_run(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that estimate_events uses _build_events_sql and _execute_dry_run."""
        mock_job = Mock()
        mock_job.total_bytes_processed = 2_000_000
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            actor1_country="USA",
        )

        result = await source.estimate_events(filter_obj, limit=100)

        assert isinstance(result, QueryEstimate)
        assert result.bytes_processed == 2_000_000
        assert "@start_date" in result.query
        assert "@actor1_country" in result.query
        assert "LIMIT 100" in result.query

        # Verify dry_run config was used
        call_args = mock_bigquery_client.query.call_args
        job_config = call_args[1]["job_config"]
        assert job_config.dry_run is True

    @pytest.mark.asyncio
    async def test_estimate_events_with_columns(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test estimate_events with explicit column list."""
        mock_job = Mock()
        mock_job.total_bytes_processed = 500_000
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

        result = await source.estimate_events(
            filter_obj,
            columns=["GLOBALEVENTID", "EventCode"],
        )

        assert "GLOBALEVENTID" in result.query
        assert "EventCode" in result.query

    @pytest.mark.asyncio
    async def test_estimate_events_invalid_columns_raises(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that invalid columns raise BigQueryError before dry run."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

        with pytest.raises(BigQueryError, match="Invalid columns"):
            await source.estimate_events(filter_obj, columns=["INVALID_COL"])

        # Client should not have been called
        mock_bigquery_client.query.assert_not_called()

    @pytest.mark.asyncio
    async def test_estimate_gkg_calls_builder_and_dry_run(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that estimate_gkg uses _build_gkg_sql and _execute_dry_run."""
        mock_job = Mock()
        mock_job.total_bytes_processed = 3_000_000
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            themes=["ENV_CLIMATECHANGE"],
        )

        result = await source.estimate_gkg(filter_obj, limit=50)

        assert isinstance(result, QueryEstimate)
        assert result.bytes_processed == 3_000_000
        assert "@theme_pattern" in result.query
        assert "LIMIT 50" in result.query

    @pytest.mark.asyncio
    async def test_estimate_gkg_invalid_columns_raises(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that invalid GKG columns raise BigQueryError."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        filter_obj = GKGFilter(date_range=DateRange(start=date(2024, 1, 1)))

        with pytest.raises(BigQueryError, match="Invalid columns"):
            await source.estimate_gkg(filter_obj, columns=["INVALID_COL"])

    @pytest.mark.asyncio
    async def test_estimate_mentions_calls_builder_and_dry_run(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that estimate_mentions uses _build_mentions_sql and _execute_dry_run."""
        mock_job = Mock()
        mock_job.total_bytes_processed = 1_500_000
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        result = await source.estimate_mentions(
            global_event_id=123456789,
            date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
            limit=100,
        )

        assert isinstance(result, QueryEstimate)
        assert result.bytes_processed == 1_500_000
        assert "@event_id" in result.query
        assert "@start_date" in result.query
        assert "LIMIT 100" in result.query

    @pytest.mark.asyncio
    async def test_estimate_mentions_without_date_range(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test estimate_mentions without a date range."""
        mock_job = Mock()
        mock_job.total_bytes_processed = 800_000
        mock_bigquery_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        result = await source.estimate_mentions(global_event_id=123)

        assert isinstance(result, QueryEstimate)
        assert "_PARTITIONTIME" not in result.query

    @pytest.mark.asyncio
    async def test_estimate_mentions_invalid_columns_raises(
        self,
        mock_settings_with_credentials: GDELTSettings,
        mock_bigquery_client: Mock,
    ) -> None:
        """Test that invalid mention columns raise BigQueryError."""
        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_bigquery_client,
        )
        source._credentials_validated = True

        with pytest.raises(BigQueryError, match="Invalid columns"):
            await source.estimate_mentions(
                global_event_id=123,
                columns=["INVALID_COL"],
            )

    @pytest.mark.asyncio
    async def test_estimate_without_credentials_raises(self) -> None:
        """Test that estimate raises ConfigurationError without credentials."""
        settings = GDELTSettings(
            bigquery_project=None,
            bigquery_credentials=None,
        )
        source = BigQuerySource(settings=settings)

        filter_obj = EventFilter(date_range=DateRange(start=date(2024, 1, 1)))

        with pytest.raises(ConfigurationError, match="not configured"):
            await source.estimate_events(filter_obj)


class TestQueryMetadata:
    """Test QueryMetadata Pydantic model."""

    def test_default_values(self) -> None:
        """Test that all fields are None by default."""
        meta = QueryMetadata()
        assert meta.bytes_processed is None
        assert meta.bytes_billed is None
        assert meta.cache_hit is None
        assert meta.slot_millis is None
        assert meta.total_rows is None
        assert meta.started is None
        assert meta.ended is None
        assert meta.statement_type is None

    def test_full_construction(self) -> None:
        """Test construction with all fields populated."""
        started = datetime(2024, 1, 1, 12, 0, 0)
        ended = datetime(2024, 1, 1, 12, 0, 5)

        meta = QueryMetadata(
            bytes_processed=1_000_000,
            bytes_billed=10_485_760,
            cache_hit=False,
            slot_millis=5000,
            total_rows=42,
            started=started,
            ended=ended,
            statement_type="SELECT",
        )

        assert meta.bytes_processed == 1_000_000
        assert meta.bytes_billed == 10_485_760
        assert meta.cache_hit is False
        assert meta.slot_millis == 5000
        assert meta.total_rows == 42
        assert meta.started == started
        assert meta.ended == ended
        assert meta.statement_type == "SELECT"

    def test_partial_construction(self) -> None:
        """Test construction with only some fields populated."""
        meta = QueryMetadata(
            bytes_processed=500,
            cache_hit=True,
        )

        assert meta.bytes_processed == 500
        assert meta.cache_hit is True
        assert meta.bytes_billed is None
        assert meta.slot_millis is None
        assert meta.total_rows is None
        assert meta.started is None
        assert meta.ended is None
        assert meta.statement_type is None


class TestQueryEstimateModel:
    """Test QueryEstimate Pydantic model."""

    def test_construction(self) -> None:
        """Test construction with required fields."""
        estimate = QueryEstimate(
            bytes_processed=2_000_000,
            query="SELECT * FROM table WHERE x = @param",
        )

        assert estimate.bytes_processed == 2_000_000
        assert estimate.query == "SELECT * FROM table WHERE x = @param"

    def test_bytes_processed_required(self) -> None:
        """Test that bytes_processed is required."""
        with pytest.raises(ValidationError):
            QueryEstimate(query="SELECT 1")  # type: ignore[call-arg]

    def test_query_required(self) -> None:
        """Test that query is required."""
        with pytest.raises(ValidationError):
            QueryEstimate(bytes_processed=100)  # type: ignore[call-arg]


class TestLastQueryMetadata:
    """Test last_query_metadata lifecycle on BigQuerySource."""

    def test_none_before_any_query(self) -> None:
        """Test that last_query_metadata is None before any query."""
        source = BigQuerySource()
        assert source.last_query_metadata is None

    @pytest.mark.asyncio
    async def test_populated_after_execute_query(
        self,
        mock_settings_with_credentials: GDELTSettings,
    ) -> None:
        """Test that last_query_metadata is populated after _execute_query."""
        # Build a mock query job with metadata attributes
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_bytes_processed = 1000
        mock_job.total_bytes_billed = 10_485_760
        mock_job.cache_hit = True
        mock_job.slot_millis = 250
        mock_job.total_rows = 5
        mock_job.started = datetime(2024, 1, 1, 12, 0, 0)
        mock_job.ended = datetime(2024, 1, 1, 12, 0, 1)
        mock_job.statement_type = "SELECT"
        mock_job.__iter__ = Mock(return_value=iter([]))

        mock_client = Mock(spec=bigquery.Client)
        mock_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_client,
        )
        source._credentials_validated = True

        # Verify metadata is None before query
        assert source.last_query_metadata is None

        # Execute a query (consume the async generator)
        _ = [row async for row in source._execute_query("SELECT 1", [])]

        # Verify metadata is now populated
        meta = source.last_query_metadata
        assert meta is not None
        assert meta.bytes_processed == 1000
        assert meta.bytes_billed == 10_485_760
        assert meta.cache_hit is True
        assert meta.slot_millis == 250
        assert meta.total_rows == 5
        assert meta.started == datetime(2024, 1, 1, 12, 0, 0)
        assert meta.ended == datetime(2024, 1, 1, 12, 0, 1)
        assert meta.statement_type == "SELECT"

    @pytest.mark.asyncio
    async def test_populated_after_execute_query_batch(
        self,
        mock_settings_with_credentials: GDELTSettings,
    ) -> None:
        """Test that last_query_metadata is populated after _execute_query_batch."""
        mock_job = Mock()
        mock_job.result.return_value = None
        mock_job.total_bytes_processed = 2000
        mock_job.total_bytes_billed = 10_485_760
        mock_job.cache_hit = False
        mock_job.slot_millis = 500
        mock_job.total_rows = 10
        mock_job.started = datetime(2024, 1, 1, 13, 0, 0)
        mock_job.ended = datetime(2024, 1, 1, 13, 0, 2)
        mock_job.statement_type = "SELECT"
        mock_job.__iter__ = Mock(return_value=iter([]))

        mock_client = Mock(spec=bigquery.Client)
        mock_client.query.return_value = mock_job

        source = BigQuerySource(
            settings=mock_settings_with_credentials,
            client=mock_client,
        )
        source._credentials_validated = True

        # Verify metadata is None before query
        assert source.last_query_metadata is None

        # Execute a batch query
        _rows, _bytes_processed = await source._execute_query_batch("SELECT 1", [])

        # Verify metadata is now populated
        meta = source.last_query_metadata
        assert meta is not None
        assert meta.bytes_processed == 2000
        assert meta.bytes_billed == 10_485_760
        assert meta.cache_hit is False
        assert meta.slot_millis == 500
        assert meta.total_rows == 10
        assert meta.statement_type == "SELECT"
