---
title: Missing query() Method in TV-GKG, TV NGrams, Radio NGrams Endpoints
priority: p2
status: completed
tags:
  - code-review
  - architecture
  - agent-native
created: 2026-01-20
completed: 2026-01-21
---

## Problem Statement

`TVGKGEndpoint`, `TVNGramsEndpoint`, and `RadioNGramsEndpoint` only have `stream()` method. They are missing the batch `query()` method that is present in other endpoints (`VGKGEndpoint`, `NGramsEndpoint`, `GKGEndpoint`). Additionally, the client.py docstrings incorrectly show `query()` being called on these endpoints.

## Findings

**Locations:**
- `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/endpoints/tv_gkg.py` - has `stream()`, missing `query()`
- `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/endpoints/tv_ngrams.py` - has `stream()`, missing `query()`
- `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/endpoints/radio_ngrams.py` - has `stream()`, missing `query()`
- `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/client.py` (lines 441, 469, 525) - docstrings show `query()` being used

**Comparison with VGKGEndpoint (lines 155-188):**
```python
async def query(self, filter_obj: VGKGFilter) -> FetchResult[VGKGRecord]:
    records: list[VGKGRecord] = [record async for record in self.stream(filter_obj)]
    return FetchResult(data=records, failed=[])
```

**Identified by:** agent-native-reviewer, pattern-recognition-specialist, kieran-python-reviewer, architecture-strategist

## Proposed Solutions

### Option 1: Add query() method to all three endpoints (Recommended)
**Pros:** Consistent API, better developer experience, agents can use batch retrieval
**Cons:** Additional code (small amount)
**Effort:** Small (copy pattern from VGKGEndpoint)
**Risk:** Low

### Option 2: Fix docstrings only
**Pros:** Quick fix
**Cons:** API remains inconsistent, limits agent accessibility
**Effort:** Minimal
**Risk:** Medium (inconsistent API)

## Acceptance Criteria

- [x] TVGKGEndpoint has query() method returning FetchResult[TVGKGRecord]
- [x] TVNGramsEndpoint has query() method returning FetchResult[BroadcastNGramRecord]
- [x] RadioNGramsEndpoint has query() method returning FetchResult[BroadcastNGramRecord]
- [x] client.py docstring examples are accurate
- [x] Unit tests added for query() methods

## Work Log

- 2026-01-20: Issue identified during code review
- 2026-01-21: Verified query() methods already exist, fixed duplicate query() in TVGKGEndpoint, added unit tests
