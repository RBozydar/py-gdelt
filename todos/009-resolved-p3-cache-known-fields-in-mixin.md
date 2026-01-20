# Cache known_fields in SchemaEvolutionMixin

**ID:** 009
**Status:** pending
**Priority:** P3 (Nice-to-have - Performance)
**Tags:** code-review, performance, python

## Problem Statement

The `SchemaEvolutionMixin._warn_unknown_fields` validator creates temporary sets on every record validation, causing unnecessary allocations.

## Findings

**File:** `src/py_gdelt/models/graphs.py`
**Lines:** 67-73

```python
@model_validator(mode="before")
@classmethod
def _warn_unknown_fields(cls, data: Any) -> Any:
    # ...
    known_fields = set(cls.model_fields.keys())  # Set created every time
    for field_info in cls.model_fields.values():  # Iteration every time
        if field_info.alias:
            known_fields.add(field_info.alias)
    unknown_fields = set(data.keys()) - known_fields  # Another set operation
```

**Impact:**
- For 1M records: ~3M temporary set allocations
- ~2-3x slower validation per record

## Proposed Solutions

### Option 1: Cache known_fields as ClassVar (Recommended)
**Effort:** Low
**Risk:** Very Low
**Pros:** ~2-3x faster validation
**Cons:** Slight memory increase (negligible - one set per model class)

```python
from typing import ClassVar

class SchemaEvolutionMixin(BaseModel):
    _known_fields_cache: ClassVar[dict[type, set[str]]] = {}

    @model_validator(mode="before")
    @classmethod
    def _warn_unknown_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # Cache known fields per class
        if cls not in cls._known_fields_cache:
            known = set(cls.model_fields.keys())
            for field_info in cls.model_fields.values():
                if field_info.alias:
                    known.add(field_info.alias)
            cls._known_fields_cache[cls] = known

        known_fields = cls._known_fields_cache[cls]
        unknown_fields = data.keys() - known_fields  # dict_keys supports set operations
        # ...
```

## Acceptance Criteria

- [ ] known_fields computed once per model class
- [ ] No performance regression
- [ ] All tests pass
- [ ] `make ci` passes

## Work Log

| Date | Author | Action |
|------|--------|--------|
| 2026-01-20 | Claude | Created from code review |
