---
title: TVGKGFilter Doesn't Validate Theme Codes Like GKGFilter Does
priority: p3
status: completed
tags:
  - code-review
  - agent-native
created: 2026-01-20
completed: 2026-01-21
---

## Problem Statement

`GKGFilter` validates themes against the `GKGThemes` lookup table, but `TVGKGFilter` accepts any strings for themes. An agent might pass invalid theme codes to TV-GKG and get zero results without understanding why.

## Findings

**GKGFilter validates themes (lines 140-155):**
```python
@field_validator("themes", mode="before")
@classmethod
def validate_themes(cls, v: list[str] | None) -> list[str] | None:
    if v is None:
        return None
    from py_gdelt.lookups.themes import GKGThemes
    themes = GKGThemes()
    for theme in v:
        try:
            themes.validate(theme)
        except InvalidCodeError:
            msg = f"Invalid GKG theme: {theme!r}"
            raise InvalidCodeError(msg, code=theme, code_type="GKG theme") from None
    return v
```

**TVGKGFilter has no validation (lines 318-334):**
```python
class TVGKGFilter(BaseModel):
    date_range: DateRange
    themes: list[str] | None = None  # No validation!
    station: str | None = None
```

**Identified by:** agent-native-reviewer

## Proposed Solutions

### Option 1: Add theme validation to TVGKGFilter (Recommended)
**Pros:** Consistent validation, better UX
**Cons:** May reject valid themes if lookup is incomplete
**Effort:** Small
**Risk:** Low

### Option 2: Document that themes are not validated
**Pros:** Quick fix
**Cons:** May confuse users
**Effort:** Minimal
**Risk:** Low

## Acceptance Criteria

- [x] TVGKGFilter validates themes like GKGFilter
- [x] Invalid themes produce clear error messages

## Work Log

- 2026-01-20: Issue identified during code review
- 2026-01-21: Verified TVGKGFilter already has validate_themes field_validator matching GKGFilter pattern
