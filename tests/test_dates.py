"""Tests for GDELT date parsing utilities."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta, timezone

import pytest

from py_gdelt.utils.dates import (
    parse_gdelt_date,
    parse_gdelt_datetime,
    try_parse_gdelt_datetime,
)


class TestParseGdeltDatetime:
    """Tests for parse_gdelt_datetime (strict)."""

    def test_gdelt_14_digit_format(self) -> None:
        result = parse_gdelt_datetime("20240115120000")
        assert result == datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

    def test_gdelt_8_digit_format(self) -> None:
        result = parse_gdelt_datetime("20240115")
        assert result == datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC)

    def test_integer_input(self) -> None:
        result = parse_gdelt_datetime(20240115120000)
        assert result == datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

    def test_integer_8_digit_input(self) -> None:
        """8-digit integer should parse as date at midnight UTC."""
        result = parse_gdelt_datetime(20240115)
        assert result == datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC)

    def test_iso_format_with_t(self) -> None:
        result = parse_gdelt_datetime("2024-01-15T12:00:00")
        assert result == datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

    def test_iso_format_with_z(self) -> None:
        result = parse_gdelt_datetime("2024-01-15T12:00:00Z")
        assert result == datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

    def test_iso_format_with_offset(self) -> None:
        # Input is +05:00, should convert to UTC (7:00 AM UTC)
        result = parse_gdelt_datetime("2024-01-15T12:00:00+05:00")
        assert result == datetime(2024, 1, 15, 7, 0, 0, tzinfo=UTC)

    def test_iso_format_with_microseconds(self) -> None:
        result = parse_gdelt_datetime("2024-01-15T12:00:00.123456")
        assert result.microsecond == 123456

    def test_iso_date_only(self) -> None:
        result = parse_gdelt_datetime("2024-01-15")
        assert result == datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC)

    def test_datetime_with_utc_passthrough(self) -> None:
        dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)
        result = parse_gdelt_datetime(dt)
        assert result == dt
        assert result.tzinfo == UTC

    def test_naive_datetime_gets_utc(self) -> None:
        dt = datetime(2024, 1, 15, 12, 0, 0)
        result = parse_gdelt_datetime(dt)
        assert result.tzinfo == UTC

    def test_aware_datetime_converted_to_utc(self) -> None:
        # Create datetime with +05:00 offset
        tz_plus5 = timezone(timedelta(hours=5))
        dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=tz_plus5)
        result = parse_gdelt_datetime(dt)
        # Should be converted to 7:00 AM UTC
        assert result == datetime(2024, 1, 15, 7, 0, 0, tzinfo=UTC)

    def test_invalid_format_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid GDELT date format"):
            parse_gdelt_datetime("invalid")

    def test_empty_string_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid GDELT date format"):
            parse_gdelt_datetime("")

    def test_partial_format_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid GDELT date format"):
            parse_gdelt_datetime("2024011512")  # 10 digits


class TestTryParseGdeltDatetime:
    """Tests for try_parse_gdelt_datetime (lenient)."""

    def test_valid_format_returns_datetime(self) -> None:
        result = try_parse_gdelt_datetime("20240115120000")
        assert result == datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

    def test_none_returns_none(self) -> None:
        assert try_parse_gdelt_datetime(None) is None

    def test_invalid_format_returns_none(self) -> None:
        assert try_parse_gdelt_datetime("invalid") is None

    def test_empty_string_returns_none(self) -> None:
        assert try_parse_gdelt_datetime("") is None

    def test_integer_input(self) -> None:
        result = try_parse_gdelt_datetime(20240115120000)
        assert result == datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)


class TestParseGdeltDate:
    """Tests for parse_gdelt_date (strict)."""

    def test_gdelt_format(self) -> None:
        result = parse_gdelt_date("20240115")
        assert result == date(2024, 1, 15)

    def test_date_passthrough(self) -> None:
        d = date(2024, 1, 15)
        assert parse_gdelt_date(d) is d

    def test_datetime_extracts_date(self) -> None:
        dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)
        assert parse_gdelt_date(dt) == date(2024, 1, 15)

    def test_invalid_format_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid GDELT date format"):
            parse_gdelt_date("invalid")

    def test_empty_string_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid GDELT date format"):
            parse_gdelt_date("")

    def test_14_digit_string_raises(self) -> None:
        """14-digit timestamp format should fail for date-only parsing."""
        with pytest.raises(ValueError, match="Invalid GDELT date format"):
            parse_gdelt_date("20240115120000")
