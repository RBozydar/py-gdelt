---
status: resolved
priority: p2
issue_id: "005"
tags: [code-review, refactoring, dry, graph-datasets]
dependencies: []
---

# Consider Consolidating Graph Filter Class Duplication

## Problem Statement

Six filter classes (`GQGFilter`, `GEGFilter`, `GFGFilter`, `GGGFilter`, `GEMGFilter`, `GALFilter`) have nearly identical structure with only the `max_days` validation value differing.

## Findings

**From code-simplicity-reviewer:**
- Estimated 60 LOC could be reduced
- Only differences: max day limit (7 vs 30) and whether `languages` field exists

**From coherence-reviewer:**
- Same `validate_date_range` pattern repeated 6 times
- Business rule (max days) scattered across 6 locations

**From baseline-code-reviewer:**
- If validation logic needs enhancement, 6 locations must change

## Evidence

```python
# This pattern repeats 6 times with only the number changing:
@model_validator(mode="after")
def validate_date_range(self) -> Self:
    if self.date_range.days > 7:  # 7 or 30
        msg = "GQG max date range: 7 days"
        raise ValueError(msg)
    return self
```

## Proposed Solutions

### Option 1: Factory Function (Recommended)
**Effort:** Medium
**Risk:** Low

```python
def _create_graph_filter(
    name: str,
    max_days: int,
    has_languages: bool = True
) -> type[BaseModel]:
    """Factory for graph filter classes."""
    ...

GQGFilter = _create_graph_filter("GQG", 7)
GFGFilter = _create_graph_filter("GFG", 30)
GGGFilter = _create_graph_filter("GGG", 7, has_languages=False)
```

**Pros:** DRY, easy to add new graph types
**Cons:** More complex type inference, IDE autocomplete may suffer

### Option 2: Base Class with ClassVar
**Effort:** Medium
**Risk:** Low

```python
class GraphFilterBase(BaseModel):
    MAX_DAYS: ClassVar[int]
    date_range: DateRange

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.date_range.days > self.MAX_DAYS:
            msg = f"{self.__class__.__name__} max date range: {self.MAX_DAYS} days"
            raise ValueError(msg)
        return self

class GQGFilter(GraphFilterBase):
    MAX_DAYS: ClassVar[int] = 7
    languages: list[str] | None = None
```

**Pros:** Clear inheritance, easy to understand
**Cons:** Still some repetition for `languages` field

### Option 3: Keep Current Design
**Effort:** None
**Risk:** Low

The current design is explicit and type-safe.

**Pros:** Each filter is self-contained, clear type hints
**Cons:** Duplication remains

## Recommended Action

Option 3 - Keep current design. The duplication is minor (~60 LOC), and the explicit per-filter classes provide:
1. Clear IDE autocomplete and type checking
2. Easy to understand without indirection
3. Matches the existing `EventFilter`/`GKGFilter` pattern

The plan specifically called for "Per-dataset filters following EventFilter/GKGFilter pattern" which the current implementation follows.

## Technical Details

**Affected File:** `src/py_gdelt/filters.py:364-451`

## Acceptance Criteria

- [ ] Decision documented (keep or refactor)
- [ ] If refactoring: all filters have consistent validation
- [ ] Tests pass

## Work Log

| Date | Action | Result |
|------|--------|--------|
| 2026-01-24 | Identified in code review | Recommend keeping current design |

## Resources

- File: `src/py_gdelt/filters.py`
- Pattern: `EventFilter`, `GKGFilter` in same file
