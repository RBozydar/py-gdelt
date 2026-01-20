# Add Sync Wrappers to GraphEndpoint

**ID:** 005
**Status:** deferred
**Priority:** P2 (Important)
**Tags:** code-review, python, api-consistency

## Problem Statement

`GraphEndpoint` only has async methods (`query_gqg`, `stream_gqg`, etc.) but other endpoints (`EventsEndpoint`, `GKGEndpoint`) provide synchronous wrappers (`query_sync`, `stream_sync`). This breaks API consistency.

## Findings

**Comparison:**

| Endpoint | `query()` | `stream()` | `query_sync()` | `stream_sync()` |
|----------|-----------|------------|----------------|-----------------|
| EventsEndpoint | Yes | Yes | Yes | Yes |
| GKGEndpoint | Yes | Yes | Yes | Yes |
| GraphEndpoint | Yes | Yes | **Missing** | **Missing** |

**Files:**
- `src/py_gdelt/endpoints/events.py` - Lines 287-396 (has sync wrappers)
- `src/py_gdelt/endpoints/gkg.py` - Lines 229-327 (has sync wrappers)
- `src/py_gdelt/endpoints/graphs.py` - Missing sync wrappers

## Proposed Solutions

### Option 1: Add Sync Wrappers Following Existing Pattern (Recommended)
**Effort:** Medium
**Risk:** Low
**Pros:** API consistency, enables synchronous code usage
**Cons:** Code size increase

Add `query_gqg_sync()`, `stream_gqg_sync()`, etc. for all 6 datasets (12 new methods).

### Option 2: Defer to v1.2
**Effort:** None now
**Risk:** Low (plan says "Defer sync wrappers")
**Pros:** Follows plan specification
**Cons:** API inconsistency until then

Note: The implementation plan explicitly says "Defer sync wrappers - Async-first for v1.1"

## Acceptance Criteria

- [ ] Decision made on deferral vs immediate implementation
- [ ] If implementing: all 6 datasets have sync wrappers
- [ ] Tests for sync wrappers (if added)
- [ ] `make ci` passes

## Work Log

| Date | Author | Action |
|------|--------|--------|
| 2026-01-20 | Claude | Created from code review - NOTE: plan explicitly defers this |
| 2026-01-20 | Claude | Deferred per implementation plan: "Async-first for v1.1" |
