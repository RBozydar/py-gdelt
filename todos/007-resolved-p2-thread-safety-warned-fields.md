# Fix Thread-Safety Issue with _warned_fields

**ID:** 007
**Status:** pending
**Priority:** P2 (Important)
**Tags:** code-review, performance, thread-safety, python

## Problem Statement

The module-level `_warned_fields` set used for warning deduplication is not thread-safe, which could cause race conditions in async/multi-threaded contexts.

## Findings

**File:** `src/py_gdelt/models/graphs.py`
**Lines:** 42, 78-79

```python
# Module-level set to track warned fields (avoid spam)
_warned_fields: set[tuple[str, str]] = set()

# Inside validator (line 78-79):
if warn_key not in _warned_fields:
    _warned_fields.add(warn_key)  # Race condition possible here
```

**Impact:**
- With concurrent parsing, this is a data race
- Could cause duplicate warnings or `RuntimeError: Set changed size during iteration`

## Proposed Solutions

### Option 1: Use Threading Lock (Recommended)
**Effort:** Low
**Risk:** Very Low
**Pros:** Simple, correct
**Cons:** Minor overhead (negligible)

```python
import threading

_warned_fields: set[tuple[str, str]] = set()
_warned_fields_lock = threading.Lock()

# In validator:
with _warned_fields_lock:
    if warn_key not in _warned_fields:
        _warned_fields.add(warn_key)
        # Issue warning inside lock
```

### Option 2: Use asyncio Lock
**Effort:** Medium
**Risk:** Medium (more complex)
**Pros:** More async-native
**Cons:** Requires async context management

## Acceptance Criteria

- [ ] `_warned_fields` access is thread-safe
- [ ] No duplicate warnings in concurrent scenarios
- [ ] All tests pass
- [ ] `make ci` passes

## Work Log

| Date | Author | Action |
|------|--------|--------|
| 2026-01-20 | Claude | Created from code review |
