# Fix Incorrect Docstrings in GraphEndpoint

**ID:** 001
**Status:** pending
**Priority:** P2 (Important)
**Tags:** code-review, documentation, python

## Problem Statement

The module docstring and method docstrings in `src/py_gdelt/endpoints/graphs.py` contain incorrect acronym expansions for GDELT graph datasets.

## Findings

**File:** `src/py_gdelt/endpoints/graphs.py`
**Lines:** 1-6 (module docstring), and various method docstrings

Current incorrect naming:
- GEG = "Event Graph" (should be **Entity Graph**)
- GFG = "Facebook Graph" (should be **Frontpage Graph**)
- GGG = "Google Graph" (should be **Geographic Graph**)
- GEMG = "Emotion Graph" (should be **Embedded Metadata Graph**)
- GAL = "Activity Log" (should be **Article List**)

## Proposed Solutions

### Option 1: Update All Docstrings (Recommended)
**Effort:** Low
**Risk:** None
**Pros:** Correct documentation improves user experience
**Cons:** None

Fix the module docstring and all method docstrings with correct names.

## Acceptance Criteria

- [ ] Module docstring uses correct acronym expansions
- [ ] All method docstrings (query_geg, stream_geg, etc.) use correct names
- [ ] `make ci` passes

## Work Log

| Date | Author | Action |
|------|--------|--------|
| 2026-01-20 | Claude | Created from code review |
