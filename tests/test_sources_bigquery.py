"""Tests for BigQuerySource module.

This module tests the BigQuery data source with a focus on:
- Security: Parameterized queries, column validation, path validation
- Credential handling: Validation, error messages, ADC vs explicit credentials
- Query building: WHERE clause generation, parameter binding
- Async execution: run_in_executor usage, streaming results
"""

import re
from datetime import date
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError

from py_gdelt.config import GDELTSettings
from py_gdelt.exceptions import BigQueryError, ConfigurationError, SecurityError
from py_gdelt.filters import DateRange, EventFilter, GKGFilter
from py_gdelt.sources.bigquery import (
    BigQuerySource,
    _build_where_clause_for_events,
    _build_where_clause_for_gkg,
    _validate_columns,
    _validate_credential_path,
)


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
        assert "REGEXP_CONTAINS(V2Locations, @country_code)" in where_clause
        assert "CAST(SPLIT(V2Tone, ',')[OFFSET(0)] AS FLOAT64) >= @min_tone" in where_clause

        # Verify theme pattern
        param_dict = {p.name: p for p in parameters}
        theme_value = param_dict["theme_pattern"].value
        assert isinstance(theme_value, str)
        assert "ENV_CLIMATECHANGE" in theme_value

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
