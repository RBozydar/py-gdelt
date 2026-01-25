---
status: resolved
priority: p3
issue_id: "009"
tags: [code-review, documentation, graph-datasets]
dependencies: []
---

# Document Why GGGFilter Lacks languages Field

## Problem Statement

`GGGFilter` is the only graph filter without a `languages` field. This is intentional (GGGRecord doesn't have a `lang` field), but it creates API inconsistency that should be documented.

## Findings

**From coherence-reviewer:**
- All graph filters except GGGFilter have `languages: list[str] | None = None`
- This is correct - GGGRecord has no `lang` field (geographic data doesn't have language)
- But the inconsistency is not documented

**From kieran-python-reviewer:**
- The inconsistency is intentional but undocumented

## Evidence

```python
class GGGFilter(BaseModel):
    """Filter for Global Geographic Graph queries (max 7 days)."""
    date_range: DateRange
    # No languages field - should document why

class GGGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Geographic Graph record."""
    date: datetime
    url: str
    location_name: str
    lat: float
    lon: float
    context: str
    # No lang field - geographic data doesn't have language
```

## Proposed Solutions

### Option 1: Add Documentation (Recommended)
**Effort:** Small
**Risk:** None

Add a note to `GGGFilter` docstring explaining why `languages` is absent.

```python
class GGGFilter(BaseModel):
    """Filter for Global Geographic Graph queries (max 7 days).

    Note:
        Unlike other graph filters, GGGFilter does not have a `languages` field
        because GGG records contain geographic data without language metadata.
    """
```

**Pros:** Explains the design decision
**Cons:** None

## Recommended Action

Option 1 - Add documentation explaining the intentional difference.

## Technical Details

**Affected Files:**
- `src/py_gdelt/filters.py:409-420` - Add note to GGGFilter docstring

## Acceptance Criteria

- [ ] GGGFilter docstring explains why `languages` is absent
- [ ] Optionally: GGGRecord docstring notes lack of `lang` field

## Work Log

| Date | Action | Result |
|------|--------|--------|
| 2026-01-24 | Identified in code review | Finding documented |

## Resources

- Filter: `src/py_gdelt/filters.py:409-420`
- Model: `src/py_gdelt/models/graphs.py:284-305`
