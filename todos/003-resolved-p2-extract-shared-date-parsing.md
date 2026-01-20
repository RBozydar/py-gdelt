# Extract Shared Date Parsing Logic (DRY Violation)

**ID:** 003
**Status:** pending
**Priority:** P2 (Important)
**Tags:** code-review, python, dry, refactoring

## Problem Statement

The identical `parse_date` field validator is duplicated **5 times** across different graph models, totaling ~120 lines of duplicated code. This violates DRY principles and makes maintenance harder.

## Findings

**File:** `src/py_gdelt/models/graphs.py`
**Lines:** 129-153, 199-222, 304-327, 373-396, 425-448

Affected models:
1. `GQGRecord` (lines 129-153)
2. `GEGRecord` (lines 199-222)
3. `GGGRecord` (lines 304-327)
4. `GEMGRecord` (lines 373-396)
5. `GALRecord` (lines 425-448)

Each implementation is exactly identical (24 lines each).

## Proposed Solutions

### Option 1: Extract to Module-Level Function (Recommended)
**Effort:** Low
**Risk:** Low
**Pros:** Simple, clear, follows existing patterns
**Cons:** None

```python
def _parse_gdelt_date(v: Any) -> datetime:
    """Parse date from ISO or GDELT format."""
    if isinstance(v, datetime):
        return v
    if isinstance(v, str):
        if "T" in v:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return datetime.strptime(v, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
    msg = f"Invalid date format: {v}"
    raise ValueError(msg)

# In each model:
_parse_date = field_validator("date", mode="before")(_parse_gdelt_date)
```

### Option 2: Create DateParsingMixin Class
**Effort:** Medium
**Risk:** Low
**Pros:** More Pydantic-idiomatic
**Cons:** Adds inheritance complexity

## Acceptance Criteria

- [ ] Single source of truth for date parsing logic
- [ ] All 5 models use the shared function
- [ ] All existing tests pass
- [ ] `make ci` passes

## Work Log

| Date | Author | Action |
|------|--------|--------|
| 2026-01-20 | Claude | Created from code review |
