---
title: TVGKGEndpoint Constructor Requires FileSource (Others Make It Optional)
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

`TVGKGEndpoint` requires `file_source` as a mandatory constructor argument, while all other new endpoints (`VGKGEndpoint`, `TVNGramsEndpoint`, `RadioNGramsEndpoint`) accept an optional `file_source` and create one internally if not provided. This breaks the "standalone endpoint" pattern and API consistency.

## Findings

**Location:** `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/endpoints/tv_gkg.py` (lines 83-88)

```python
# TVGKGEndpoint - INCONSISTENT
def __init__(
    self,
    file_source: FileSource,  # Required!
    *,
    client: httpx.AsyncClient | None = None,
) -> None:

# VGKGEndpoint, TVNGramsEndpoint, RadioNGramsEndpoint - Pattern
def __init__(
    self,
    settings: GDELTSettings | None = None,
    file_source: FileSource | None = None,  # Optional
) -> None:
```

**Identified by:** architecture-strategist, pattern-recognition-specialist, agent-native-reviewer

## Proposed Solutions

### Option 1: Make file_source optional in TVGKGEndpoint (Recommended)
**Pros:** Consistent API across all endpoints, works standalone
**Cons:** Adds more constructor logic
**Effort:** Small
**Risk:** Low

### Option 2: Document the difference
**Pros:** No code changes
**Cons:** API remains inconsistent, poor developer experience
**Effort:** Minimal
**Risk:** Medium (confusing API)

## Acceptance Criteria

- [x] TVGKGEndpoint can be instantiated without providing file_source
- [x] Constructor signature matches VGKGEndpoint pattern
- [x] Existing tests continue to pass
- [x] client.py integration works correctly

## Work Log

- 2026-01-20: Issue identified during code review
- 2026-01-21: Fixed by making file_source optional with internal creation when not provided
