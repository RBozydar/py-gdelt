# Linting Cleanup Plan v2

**Date:** 2026-01-05
**Status:** Ready for implementation

## Summary

Reduce global lint ignores by fixing 147 actual violations (not 1,228 as documented).

## Current State

| Category | Documented | Actual |
|----------|------------|--------|
| PERMANENT | 12 | **12** |
| MAJOR DEBT | 992 | **90** |
| INCREMENTAL | 224 | **45** |
| **Total** | 1,228 | **147** |

---

## Phase 1: Fix Incremental Debt (45 violations)

**Effort: ~45 minutes**

### 1.1 Fix PERF401 (12 violations) - 15 min

Replace manual list building with comprehensions/extend.

```bash
uvx ruff check --select PERF401 src/ --fix --unsafe-fixes
```

**Files affected:**
- `src/py_gdelt/endpoints/context.py`
- `src/py_gdelt/endpoints/doc.py`
- `src/py_gdelt/endpoints/events.py`
- `src/py_gdelt/endpoints/geo.py`
- `src/py_gdelt/endpoints/tv.py`
- `src/py_gdelt/utils/streaming.py`

### 1.2 Fix EM101/EM102 (33 violations) - 30 min

Extract exception message strings to variables.

**Before:**
```python
raise APIError(f"HTTP error from {url}: {e}")
```

**After:**
```python
msg = f"HTTP error from {url}: {e}"
raise APIError(msg)
```

**Files affected:**
- `src/py_gdelt/endpoints/base.py` (12 violations)
- `src/py_gdelt/sources/files.py` (8 violations)
- `src/py_gdelt/sources/bigquery.py` (6 violations)
- `src/py_gdelt/parsers/*.py` (4 violations)
- `src/py_gdelt/utils/streaming.py` (3 violations)

---

## Phase 2: Fix PLR2004 Magic Values (15 violations)

**Effort: ~20 minutes**

Create HTTP status constants in a single location.

**Create `src/py_gdelt/constants.py`:**
```python
# HTTP Status Codes
HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_TOO_MANY_REQUESTS = 429
HTTP_SERVER_ERROR = 500
HTTP_SERVER_ERROR_MAX = 600

# Cache limits
CACHE_FILENAME_MAX_LENGTH = 200
```

**Files to update:**
- `src/py_gdelt/endpoints/base.py` (6 violations)
- `src/py_gdelt/sources/files.py` (4 violations)
- `src/py_gdelt/cache.py` (1 violation)

---

## Phase 3: Address TRY400 (17 violations)

**Effort: ~15 minutes**

Two sub-categories:

### 3.1 Swallowed exceptions - Fix with `.exception()`

These log errors but don't re-raise, losing the traceback:

- `src/py_gdelt/cache.py:221` - no re-raise
- `src/py_gdelt/sources/fetcher.py:200, 215, 294, 563` - error boundaries
- `src/py_gdelt/sources/files.py:409` - error boundary

### 3.2 Re-raised exceptions - Add `# noqa: TRY400`

All others follow the `error + raise` pattern which is intentional:
- Traceback appears at top-level handler
- Intermediate logs stay clean

---

## Phase 4: Keep TRY003 Globally Ignored

**Decision:** Keep ignored, add to backlog

TRY003 wants custom exception classes with default messages. Current approach (descriptive raise messages) is clearer for this project.

**Backlog item:** Consider custom exception hierarchy with default messages in future refactor.

---

## Phase 5: Update pyproject.toml

After fixes, update the ignore list:

```toml
ignore = [
    # === PERMANENT - Justified by Architecture ===
    "ARG002",   # unused-method-argument (8 - protocol compliance)
    "S608",     # hardcoded-sql-expression (3 - BigQuery safe builders)
    "PLR0913",  # too-many-arguments (1 - could also use line noqa)

    # === KEPT IGNORED - Intentional Style ===
    "TRY003",   # raise-vanilla-args (verbose messages preferred)

    # === CONFIGURATION ===
    "E501",     # line-too-long (handled by formatter)
    "COM812",   # missing-trailing-comma (conflicts with formatter)
]
```

**Remove from global ignore:**
- `PLR2004` (after adding constants)
- `TRY400` (after fixing + per-line noqa)
- `PERF401` (after fixing)
- `EM101` (after fixing)
- `EM102` (after fixing)

---

## Phase 6: Update Documentation

### 6.1 Fix `scripts/lint_progress.sh`

The grep patterns are broken - counts show "0\n0" instead of numbers.

**Issue:** Script checks `src/` but violations report with full paths.

### 6.2 Update pyproject.toml comments

Replace outdated violation counts with accurate numbers.

### 6.3 Create/update backlog.md

Add TRY003 refactoring as future task.

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/py_gdelt/constants.py` | CREATE - HTTP status constants |
| `src/py_gdelt/endpoints/base.py` | EM102 fixes, PLR2004 constants |
| `src/py_gdelt/endpoints/context.py` | PERF401 fix |
| `src/py_gdelt/endpoints/doc.py` | PERF401 fix |
| `src/py_gdelt/endpoints/events.py` | PERF401 fix |
| `src/py_gdelt/endpoints/geo.py` | PERF401 fix |
| `src/py_gdelt/endpoints/tv.py` | PERF401 fix |
| `src/py_gdelt/sources/files.py` | EM102 fixes, PLR2004 constants |
| `src/py_gdelt/sources/bigquery.py` | EM102 fixes |
| `src/py_gdelt/sources/fetcher.py` | TRY400 fixes |
| `src/py_gdelt/cache.py` | TRY400 fix, PLR2004 constant |
| `src/py_gdelt/parsers/mentions.py` | EM101 fix |
| `src/py_gdelt/parsers/ngrams.py` | TRY400 noqa |
| `src/py_gdelt/utils/streaming.py` | PERF401 fix, EM102 fixes |
| `pyproject.toml` | Update ignore list and comments |
| `scripts/lint_progress.sh` | Fix grep patterns |

---

## Verification

```bash
# After all changes:
make ci  # Must pass

# Verify no new violations:
uvx ruff check src/
```

---

## Outcome

After implementation:
- **6 rules removed** from global ignore
- **4 rules remain** (3 permanent + 1 intentional style)
- **Accurate documentation** of actual violation counts
- **Working lint scripts** for tracking
