---
title: VGKGEndpoint.get_latest() Creates Temporary HTTP Client
priority: p3
status: completed
tags:
  - code-review
  - performance
created: 2026-01-20
completed: 2026-01-21
---

## Problem Statement

`VGKGEndpoint.get_latest()` creates a new temporary HTTP client just to fetch `lastupdate.txt`, while `TVGKGEndpoint.get_latest()` reuses its injected client. This is inefficient and inconsistent.

## Findings

**Location:** `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/endpoints/vgkg.py` (lines 267-284)

```python
async def get_latest(self) -> list[VGKGRecord]:
    # Create a temporary HTTP client to fetch lastupdate.txt
    async with httpx.AsyncClient(timeout=self.settings.timeout) as client:
        response = await client.get(VGKG_LAST_UPDATE_URL)
        # ...
```

**TVGKGEndpoint.get_latest()** reuses `self._client` (line 259):
```python
response = await self._client.get(TV_GKG_LAST_UPDATE_URL)
```

**Identified by:** code-simplicity-reviewer, pattern-recognition-specialist

## Proposed Solutions

### Option 1: Use FileSource's client if available
**Pros:** Reuses existing connection pool
**Cons:** Need to verify FileSource exposes client
**Effort:** Small
**Risk:** Low

### Option 2: Store client reference in VGKGEndpoint
**Pros:** Consistent with TVGKGEndpoint pattern
**Cons:** Requires constructor change
**Effort:** Medium
**Risk:** Low

## Acceptance Criteria

- [x] VGKGEndpoint.get_latest() doesn't create temporary client
- [x] HTTP connection pooling is properly utilized

## Work Log

- 2026-01-20: Issue identified during code review
- 2026-01-21: Verified VGKGEndpoint.get_latest() already uses self._client correctly
