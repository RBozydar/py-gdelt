---
status: resolved
priority: p3
issue_id: "008"
tags: [code-review, refactoring, dry, graph-datasets]
dependencies: []
---

# Move model_config to SchemaEvolutionMixin

## Problem Statement

All graph models have `model_config = {"extra": "ignore"}` repeated 9 times while they also inherit from `SchemaEvolutionMixin`. The config could be defined once in the mixin.

## Findings

**From coherence-reviewer:**
- `model_config = {"extra": "ignore"}` repeated in 9 classes
- All these classes inherit from `SchemaEvolutionMixin`
- The mixin already handles unknown field warnings

## Evidence

```python
# Repeated 9 times:
class GQGRecord(SchemaEvolutionMixin, BaseModel):
    """..."""
    model_config = {"extra": "ignore"}  # Could be in mixin
```

## Proposed Solutions

### Option 1: Move to Mixin (Recommended)
**Effort:** Small
**Risk:** Low

```python
class SchemaEvolutionMixin(BaseModel):
    """Mixin for graceful handling of schema evolution."""

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _warn_unknown_fields(cls, data: Any) -> Any:
        ...
```

**Pros:** DRY, single point of configuration
**Cons:** Less explicit in each model

### Option 2: Keep Explicit
**Effort:** None
**Risk:** None

Keep `model_config` in each class for explicitness.

**Pros:** Clear what each model does
**Cons:** Repetition

## Recommended Action

Option 1 - Move `model_config` to `SchemaEvolutionMixin` since all models using the mixin need this config.

## Technical Details

**Affected File:** `src/py_gdelt/models/graphs.py`

**Changes:**
1. Add `model_config = ConfigDict(extra="ignore")` to `SchemaEvolutionMixin`
2. Remove `model_config = {"extra": "ignore"}` from 9 model classes

## Acceptance Criteria

- [ ] `model_config` defined once in `SchemaEvolutionMixin`
- [ ] Removed from individual model classes
- [ ] Tests pass (schema evolution warning tests still work)

## Work Log

| Date | Action | Result |
|------|--------|--------|
| 2026-01-24 | Identified in code review | Finding documented |

## Resources

- File: `src/py_gdelt/models/graphs.py`
