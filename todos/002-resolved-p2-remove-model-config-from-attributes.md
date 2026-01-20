# Remove model_config from Attributes Sections

**ID:** 002
**Status:** pending
**Priority:** P2 (Important)
**Tags:** code-review, documentation, python, pydantic

## Problem Statement

The `model_config` class variable is documented in the `Attributes:` section of 9 model classes. Per project conventions (CLAUDE.md), the Attributes section should only document public class/instance attributes that are part of the API, not internal Pydantic machinery.

## Findings

**File:** `src/py_gdelt/models/graphs.py`
**Lines:** 96, 114, 162, 184, 232, 284, 335, 354, 404

Affected classes:
1. `Quote` (line 96)
2. `GQGRecord` (line 114)
3. `Entity` (line 162)
4. `GEGRecord` (line 184)
5. `GFGRecord` (line 232)
6. `GGGRecord` (line 284)
7. `MetaTag` (line 335)
8. `GEMGRecord` (line 354)
9. `GALRecord` (line 404)

## Proposed Solutions

### Option 1: Remove model_config from All Attributes Sections (Recommended)
**Effort:** Low
**Risk:** None
**Pros:** Follows project conventions, cleaner documentation
**Cons:** None

Remove the `model_config: Pydantic configuration` line from all 9 Attributes sections.

## Acceptance Criteria

- [ ] `model_config` removed from all Attributes sections
- [ ] `make ci` passes (including doc checks)

## Work Log

| Date | Author | Action |
|------|--------|--------|
| 2026-01-20 | Claude | Created from code review |
