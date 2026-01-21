---
title: TV NGrams Station Requirement Error Raised Too Late
priority: p2
status: completed
tags:
  - code-review
  - agent-native
  - python
created: 2026-01-20
completed: 2026-01-21
---

## Problem Statement

TV NGrams requires a station filter, but this validation happens deep in `_build_urls()` rather than at the filter level or start of `stream()`. Agents won't know station is required until runtime, after the filter has been accepted.

## Findings

**Location:** `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/endpoints/tv_ngrams.py` (lines 147-149)

```python
def _build_urls(self, filter_obj: BroadcastNGramsFilter) -> list[str]:
    if not filter_obj.station:
        msg = "Station filter is required for TV NGrams queries"
        raise ValueError(msg)
```

**Contrast with filter validation:** The `BroadcastNGramsFilter` doesn't require station at the model level since Radio NGrams makes it optional.

**Identified by:** agent-native-reviewer

## Proposed Solutions

### Option 1: Validate at start of stream() method (Recommended)
**Pros:** Fails fast, clear error location
**Cons:** Still runtime validation
**Effort:** Small
**Risk:** Low

```python
async def stream(self, filter_obj: BroadcastNGramsFilter) -> AsyncIterator[BroadcastNGramRecord]:
    if not filter_obj.station:
        raise ValueError("Station filter is required for TV NGrams queries")
    # ...
```

### Option 2: Create separate TVNGramsFilter with required station
**Pros:** Compile-time type safety
**Cons:** More filter classes, breaks type alias pattern
**Effort:** Medium
**Risk:** Low

### Option 3: Document prominently in docstring
**Pros:** Quick fix
**Cons:** Error still raised late
**Effort:** Minimal
**Risk:** Medium (poor UX)

## Acceptance Criteria

- [x] Station requirement is validated early (not in _build_urls)
- [x] Error message is clear
- [x] Documentation mentions requirement

## Work Log

- 2026-01-20: Issue identified during code review
- 2026-01-21: Refactored stream() to validate station synchronously at call time, before iteration begins
