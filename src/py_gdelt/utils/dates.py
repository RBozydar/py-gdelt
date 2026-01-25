"""GDELT date parsing utilities.

This module provides the canonical implementation of GDELT date format parsing.
All models and endpoints should use these functions rather than inline strptime calls.

Supported formats:
- YYYYMMDDHHMMSS (14-digit GDELT timestamp)
- YYYYMMDD (8-digit GDELT date)
- ISO 8601 with time (2024-01-15T12:00:00)
- ISO 8601 date-only (2024-01-15)
- Integer timestamps (from some GDELT JSON APIs)

All datetimes are converted to UTC timezone.
"""

from __future__ import annotations

from datetime import UTC, date, datetime


__all__ = [
    "parse_gdelt_date",
    "parse_gdelt_datetime",
    "try_parse_gdelt_datetime",
]


def parse_gdelt_datetime(value: str | int | datetime) -> datetime:
    """Parse GDELT timestamp or ISO format to UTC datetime.

    Args:
        value: Date string (YYYYMMDDHHMMSS, YYYYMMDD, or ISO 8601),
            integer timestamp, or datetime object.

    Returns:
        Parsed datetime converted to UTC timezone.

    Raises:
        ValueError: If the date format is invalid.
    """
    if isinstance(value, datetime):
        # Treat naive datetime as UTC (GDELT stores timestamps in UTC)
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    if isinstance(value, int):
        value = str(value)

    # ISO format (contains 'T' or '-' delimiter)
    if "T" in value or "-" in value:
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                return dt.replace(tzinfo=UTC)
            return dt.astimezone(UTC)
        except ValueError:
            pass  # Fall through to error

    # GDELT formats: 14-digit timestamp or 8-digit date
    try:
        if len(value) == 14:
            return datetime.strptime(value, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
        if len(value) == 8:
            return datetime.strptime(value, "%Y%m%d").replace(tzinfo=UTC)
    except ValueError:
        pass  # Fall through to error

    msg = f"Invalid GDELT date format: {value!r}"
    raise ValueError(msg)


def try_parse_gdelt_datetime(value: str | int | datetime | None) -> datetime | None:
    """Parse GDELT timestamp or ISO format to UTC datetime, returning None on failure.

    Args:
        value: Date string, integer timestamp, datetime object, or None.

    Returns:
        Parsed datetime with UTC timezone, or None if parsing fails.
    """
    if value is None:
        return None
    try:
        return parse_gdelt_datetime(value)
    except (ValueError, TypeError):
        return None


def parse_gdelt_date(value: str | date | datetime) -> date:
    """Parse GDELT date format to date object.

    Args:
        value: Date string (YYYYMMDD), date object, or datetime object.

    Returns:
        Parsed date object.

    Raises:
        ValueError: If the date format is invalid.
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y%m%d").replace(tzinfo=UTC).date()
    except ValueError:
        msg = f"Invalid GDELT date format: {value!r}"
        raise ValueError(msg) from None
