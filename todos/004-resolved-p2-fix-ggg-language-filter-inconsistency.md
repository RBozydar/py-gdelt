# Fix GGGFilter Language Filter Inconsistency

**ID:** 004
**Status:** pending
**Priority:** P2 (Important)
**Tags:** code-review, bug, python

## Problem Statement

`GGGFilter` has a `languages` field but:
1. `GGGRecord` model has no `lang` field
2. `stream_ggg()` method doesn't apply language filtering (unlike other stream methods)

This creates an inconsistent API where the filter parameter has no effect.

## Findings

**File 1:** `src/py_gdelt/filters.py`
**Lines:** 350-362
```python
class GGGFilter(BaseModel):
    """Filter for Global Geographic Graph queries (max 7 days)."""
    date_range: DateRange
    languages: list[str] | None = None  # <-- Has languages field
```

**File 2:** `src/py_gdelt/endpoints/graphs.py`
**Lines:** 254-275
```python
async def stream_ggg(...) -> AsyncIterator[GGGRecord]:
    async for url, data in self._fetcher.fetch_graph_files("ggg", filter_obj.date_range):
        try:
            for record in graph_parsers.parse_ggg(data):
                yield record  # <-- No language filtering (unlike stream_gqg, etc.)
```

**File 3:** `src/py_gdelt/models/graphs.py`
**Lines:** 280-302
`GGGRecord` has no `lang` field (only `location_name`, `lat`, `lon`, `context`).

## Proposed Solutions

### Option 1: Remove `languages` from GGGFilter (Recommended)
**Effort:** Low
**Risk:** Low (breaking change but field was non-functional)
**Pros:** API matches actual data structure
**Cons:** Minor breaking change

### Option 2: Add `lang` field to GGGRecord and filtering to stream_ggg
**Effort:** Medium
**Risk:** Medium (requires verifying GDELT GGG data structure)
**Pros:** More filtering capability
**Cons:** May not match actual GDELT data format

## Acceptance Criteria

- [ ] Either remove `languages` from `GGGFilter` OR add `lang` to `GGGRecord` and filtering to `stream_ggg()`
- [ ] API is internally consistent
- [ ] Tests updated
- [ ] `make ci` passes

## Work Log

| Date | Author | Action |
|------|--------|--------|
| 2026-01-20 | Claude | Created from code review |
