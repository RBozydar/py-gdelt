---
title: Inconsistent __aenter__ Initialization Across Endpoints
priority: p2
status: completed
tags:
  - code-review
  - architecture
  - python
created: 2026-01-20
completed: 2026-01-21
---

## Problem Statement

`RadioNGramsEndpoint.__aenter__` initializes the FileSource by calling `self._file_source.__aenter__()` when owning sources, while all other new endpoints (`VGKGEndpoint`, `TVNGramsEndpoint`, `TVGKGEndpoint`) do NOT initialize FileSource in their `__aenter__`. This inconsistency could cause either:
- RadioNGramsEndpoint double-initializing FileSource when used via GDELTClient
- Other endpoints failing when used standalone

## Findings

**Location:** `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/endpoints/radio_ngrams.py` (lines 85-94)

```python
# RadioNGramsEndpoint - INCONSISTENT
async def __aenter__(self) -> RadioNGramsEndpoint:
    if self._owns_sources:
        await self._file_source.__aenter__()  # <-- Only RadioNGramsEndpoint does this
    return self

# VGKGEndpoint, TVNGramsEndpoint - Pattern
async def __aenter__(self) -> VGKGEndpoint:
    return self  # <-- No FileSource initialization
```

**Identified by:** pattern-recognition-specialist, kieran-python-reviewer, architecture-strategist

## Proposed Solutions

### Option 1: Remove FileSource initialization from RadioNGramsEndpoint (Recommended)
**Pros:** Consistent with other endpoints, simpler code
**Cons:** Need to verify FileSource doesn't require explicit initialization for standalone use
**Effort:** Small
**Risk:** Low

### Option 2: Add FileSource initialization to all endpoints
**Pros:** Ensures all endpoints work standalone
**Cons:** May cause double-initialization when used via GDELTClient
**Effort:** Medium
**Risk:** Medium

## Acceptance Criteria

- [x] All endpoints have consistent `__aenter__` behavior
- [x] Endpoints work correctly both standalone and via GDELTClient
- [x] Unit tests pass for all endpoints

## Work Log

- 2026-01-20: Issue identified during code review
- 2026-01-21: Fixed by implementing Option 2 - Added FileSource initialization to VGKGEndpoint, TVNGramsEndpoint, and TVGKGEndpoint to match RadioNGramsEndpoint pattern
