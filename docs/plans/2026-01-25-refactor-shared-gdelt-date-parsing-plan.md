---
title: "refactor: extract shared GDELT date parsing utility"
type: refactor
date: 2026-01-25
task_list_id: a05c4710-19d1-41fb-bee2-ea3fe0de2320
github_issue: 67
reviewed_by:
  - code-simplicity-reviewer
  - architecture-strategist
  - kieran-python-reviewer
  - skeptical-simplicity-reviewer
  - gemini-plan-reviewer
---

# refactor: extract shared GDELT date parsing utility

## Overview

Extract duplicated GDELT date parsing logic (`%Y%m%d%H%M%S` and `%Y%m%d` formats) into a shared utility module at `src/py_gdelt/utils/dates.py`.

## Problem Statement

The same date parsing pattern is duplicated in 10+ locations across models and endpoints:
- `src/py_gdelt/models/graphs.py` - `_parse_gdelt_date()`
- `src/py_gdelt/models/gkg.py` - inline `datetime.strptime()`
- `src/py_gdelt/models/vgkg.py` - inline `datetime.strptime()`
- `src/py_gdelt/models/events.py` - inline `datetime.strptime()`
- `src/py_gdelt/models/ngrams.py` - inline `datetime.strptime()`
- `src/py_gdelt/models/articles.py` - inline `datetime.strptime()`
- `src/py_gdelt/endpoints/tv.py` - `_parse_date()`
- `src/py_gdelt/endpoints/lowerthird.py` - `_parse_date()`
- `src/py_gdelt/endpoints/tvv.py` - inline `datetime.strptime()`
- `src/py_gdelt/sources/files.py` - inline `datetime.strptime()`

This duplication:
- Makes format changes error-prone (must update multiple files)
- Creates inconsistent error handling across modules
- Obscures the GDELT-specific date format convention

## Proposed Solution

Create `src/py_gdelt/utils/dates.py` with **three functions** (reduced from four after review):

| Function | Input | Output | On Invalid |
|----------|-------|--------|------------|
| `parse_gdelt_datetime()` | `str \| int \| datetime` | `datetime` | Raises `ValueError` |
| `try_parse_gdelt_datetime()` | `str \| int \| datetime \| None` | `datetime \| None` | Returns `None` |
| `parse_gdelt_date()` | `str \| date \| datetime` | `date` | Raises `ValueError` |

**Removed:** `try_parse_gdelt_date()` - Zero callers exist in the codebase (YAGNI).

### Format Support

All functions support:
- **GDELT timestamp**: `YYYYMMDDHHMMSS` (14 digits)
- **GDELT date**: `YYYYMMDD` (8 digits)
- **ISO 8601 with time**: `2024-01-15T12:00:00` with optional timezone
- **ISO 8601 date-only**: `2024-01-15`
- **Integer timestamps**: `20240115120000` (from some GDELT JSON APIs)
- **Passthrough**: `datetime` / `date` objects converted to UTC

All returned datetimes are **converted to UTC** (not just tagged).

### Error Handling Rationale

**Strict functions** (`parse_*`) - Used by model transformations (`gkg.py`, `events.py`, etc.) where data comes from structured sources (BigQuery, files). Invalid dates indicate bugs or schema changes - fail fast.

**Lenient function** (`try_parse_gdelt_datetime`) - Used by API endpoints (`tv.py`, `lowerthird.py`) where JSON from GDELT APIs can have missing/malformed dates. Graceful degradation preferred.

## Acceptance Criteria

- [x] Create `src/py_gdelt/utils/dates.py` with three functions
- [x] Export functions from `src/py_gdelt/utils/__init__.py`
- [x] Update all 10 files to use shared utilities
- [x] Remove duplicate `_parse_date()` / `_parse_gdelt_date()` functions
- [x] Add comprehensive tests in `tests/test_dates.py`
- [x] All tests pass (`make test`)
- [x] Type checking passes (`make typecheck`)
- [x] Linting passes (`make lint`)

## Technical Approach

### Phase 1: Create Utility Module

Create `src/py_gdelt/utils/dates.py`:

```python
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
        # Convert to UTC (not just attach timezone)
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
        return datetime.strptime(value, "%Y%m%d").date()
    except ValueError:
        msg = f"Invalid GDELT date format: {value!r}"
        raise ValueError(msg) from None
```

### Phase 2: Update Models

Each model file change follows this pattern:

```diff
--- a/src/py_gdelt/models/gkg.py
+++ b/src/py_gdelt/models/gkg.py
@@ -1,6 +1,7 @@
 from datetime import UTC, datetime

+from py_gdelt.utils.dates import parse_gdelt_datetime

@@ -146,7 +147,7 @@ class GKGRecord:
         # Parse date (format: YYYYMMDDHHMMSS)
-        date_str = raw.date
-        date = datetime.strptime(date_str, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
+        date = parse_gdelt_datetime(raw.date)
```

Files to update:
- `graphs.py` - Remove `_parse_gdelt_date()`, use `parse_gdelt_datetime`
- `gkg.py:148` - Replace inline strptime
- `gkg.py:588` - Replace inline strptime
- `vgkg.py:128` - Replace inline strptime
- `events.py:215` - Use `parse_gdelt_date` for date-only
- `events.py:221-222` - Use `parse_gdelt_datetime`
- `events.py:392,395` - Use `parse_gdelt_datetime`
- `ngrams.py:63` - Use `parse_gdelt_datetime`
- `ngrams.py:141` - Use `parse_gdelt_date`
- `articles.py:57,93` - Use `parse_gdelt_datetime`

### Phase 3: Update Endpoints

```diff
--- a/src/py_gdelt/endpoints/tv.py
+++ b/src/py_gdelt/endpoints/tv.py
@@ -1,6 +1,7 @@
 from datetime import UTC, datetime, timedelta

+from py_gdelt.utils.dates import try_parse_gdelt_datetime

@@ -294,7 +295,7 @@ class TVEndpoint:
-                date=_parse_date(item.get("date")),
+                date=try_parse_gdelt_datetime(item.get("date")),

@@ -530,28 +531,0 @@
-def _parse_date(date_str: str | None) -> datetime | None:
-    ...
```

Files to update:
- `tv.py` - Remove `_parse_date()`, use `try_parse_gdelt_datetime`
- `lowerthird.py` - Remove `_parse_date()`, use `try_parse_gdelt_datetime`
- `tvv.py:76` - Use `parse_gdelt_date`
- `sources/files.py:519` - Use `parse_gdelt_datetime`

### Phase 4: Update Exports

```diff
--- a/src/py_gdelt/utils/__init__.py
+++ b/src/py_gdelt/utils/__init__.py
@@ -1,11 +1,19 @@
 """Utility functions for the py-gdelt library."""

+from py_gdelt.utils.dates import (
+    parse_gdelt_date,
+    parse_gdelt_datetime,
+    try_parse_gdelt_datetime,
+)
 from py_gdelt.utils.dedup import DedupeStrategy, deduplicate
 from py_gdelt.utils.streaming import ResultStream


 __all__ = [
     "DedupeStrategy",
     "ResultStream",
     "deduplicate",
+    "parse_gdelt_date",
+    "parse_gdelt_datetime",
+    "try_parse_gdelt_datetime",
 ]
```

### Phase 5: Add Tests

Create `tests/test_dates.py`:

```python
"""Tests for GDELT date parsing utilities."""

from __future__ import annotations

from datetime import UTC, date, datetime, timezone

import pytest

from py_gdelt.utils.dates import (
    parse_gdelt_date,
    parse_gdelt_datetime,
    try_parse_gdelt_datetime,
)


class TestParseGdeltDatetime:
    """Tests for parse_gdelt_datetime (strict)."""

    # GDELT 14-digit format
    def test_gdelt_14_digit_format(self) -> None:
        result = parse_gdelt_datetime("20240115120000")
        assert result == datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

    # GDELT 8-digit format (returns midnight UTC)
    def test_gdelt_8_digit_format(self) -> None:
        result = parse_gdelt_datetime("20240115")
        assert result == datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC)

    # Integer input (from some GDELT JSON APIs)
    def test_integer_input(self) -> None:
        result = parse_gdelt_datetime(20240115120000)
        assert result == datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

    # ISO format with T separator
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

    # ISO date-only format
    def test_iso_date_only(self) -> None:
        result = parse_gdelt_datetime("2024-01-15")
        assert result == datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC)

    # Datetime passthrough with UTC conversion
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
        tz_plus5 = timezone(datetime.timedelta(hours=5))
        dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=tz_plus5)
        result = parse_gdelt_datetime(dt)
        # Should be converted to 7:00 AM UTC
        assert result == datetime(2024, 1, 15, 7, 0, 0, tzinfo=UTC)

    # Error cases
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
```

## Review Findings Addressed

This plan incorporates feedback from five reviewers:

| Issue | Resolution |
|-------|------------|
| Missing 8-digit support in `parse_gdelt_datetime()` | Added length-based dispatch for 8 and 14 digit formats |
| Integer inputs not handled | Added `int` to type signature with string conversion |
| Brittle ISO detection (`"T" in value`) | Added `"-" in value` check for date-only ISO format |
| `try_parse_gdelt_date()` has no callers | Removed (YAGNI) - reduced from 4 to 3 functions |
| Type hint excludes `datetime` in `parse_gdelt_date` | Fixed: `str \| date \| datetime` |
| UTC not enforced for aware datetimes | Use `.astimezone(UTC)` instead of passthrough |
| Inconsistent error messages | Unified to `f"Invalid GDELT date format: {value!r}"` |
| Missing edge case tests | Added: empty string, partial formats, timezone offsets, integers |

## References

### Internal References

- Existing utility pattern: `src/py_gdelt/utils/streaming.py`
- Best implementation to extract: `src/py_gdelt/models/graphs.py:47-68` (`_parse_gdelt_date`)
- Lenient implementation pattern: `src/py_gdelt/endpoints/tv.py:530-557` (`_parse_date`)

### Related Work

- Origin: PR #66 code review (deferred as scope creep)
- GitHub Issue: #67

## Tasks

Run `/workflows:work` with this plan to execute. Tasks are stored in `~/.claude/tasks/a05c4710-19d1-41fb-bee2-ea3fe0de2320/`.

To work on these tasks from another session:
```
skill: import-tasks a05c4710-19d1-41fb-bee2-ea3fe0de2320
```
