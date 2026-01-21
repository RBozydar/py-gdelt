---
title: Missing query_sync() and stream_sync() Methods in TV/Radio Endpoints
priority: p2
status: completed
tags:
  - code-review
  - python
  - architecture
created: 2026-01-20
completed: 2026-01-21
---

## Problem Statement

`VGKGEndpoint` provides sync wrappers (`query_sync()` and `stream_sync()`), but `TVGKGEndpoint`, `TVNGramsEndpoint`, and `RadioNGramsEndpoint` do not. This creates API inconsistency for users who need synchronous access patterns.

## Findings

**VGKGEndpoint has sync wrappers (lines 366-432):**
```python
def query_sync(self, filter_obj: VGKGFilter) -> FetchResult[VGKGRecord]:
    return asyncio.run(self.query(filter_obj))

def stream_sync(self, filter_obj: VGKGFilter) -> Iterator[VGKGRecord]:
    loop = asyncio.new_event_loop()
    # ...
```

**Missing from:**
- `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/endpoints/tv_gkg.py` - No sync wrappers
- `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/endpoints/tv_ngrams.py` - No sync wrappers
- `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/endpoints/radio_ngrams.py` - No sync wrappers

**Identified by:** code-simplicity-reviewer, pattern-recognition-specialist, agent-native-reviewer

## Proposed Solutions

### Option 1: Add sync wrappers to all three endpoints (Recommended)
**Pros:** Consistent API with VGKGEndpoint and other existing endpoints
**Cons:** More code, sync wrappers have limitations
**Effort:** Medium
**Risk:** Low

### Option 2: Remove sync wrappers from VGKGEndpoint for consistency
**Pros:** Less code to maintain, encourages async usage
**Cons:** Breaking change for users expecting sync wrappers
**Effort:** Small
**Risk:** Medium (breaking API)

## Acceptance Criteria

- [x] All endpoints have consistent sync/async API surface
- [x] Sync wrappers properly handle event loop creation
- [x] Documentation notes limitations of sync wrappers

## Work Log

- 2026-01-20: Issue identified during code review
- 2026-01-21: Added get_latest_sync() to VGKGEndpoint and TVGKGEndpoint. TVNGrams and RadioNGrams already had sync wrappers.
