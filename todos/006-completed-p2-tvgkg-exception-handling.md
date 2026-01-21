---
title: Inconsistent Exception Handling Across Endpoints
priority: p2
status: completed
tags:
  - code-review
  - python
created: 2026-01-20
completed: 2026-01-21
---

## Problem Statement

Endpoints have inconsistent exception handling in their `stream()` methods. VGKGEndpoint catches broad `Exception`, while TVGKGEndpoint and TVNGramsEndpoint catch only `ValueError`. This means some endpoints will propagate unexpected errors while others silently skip them.

## Findings

**VGKGEndpoint.stream() (line 235):**
```python
except Exception as e:  # noqa: BLE001
    logger.warning("Failed to convert raw VGKG to VGKGRecord: %s - Skipping", e)
    continue
```

**TVGKGEndpoint.stream() (line 182):**
```python
except ValueError as e:
    logger.warning("Failed to parse TV-GKG record: %s", e)
    continue
```

**TVNGramsEndpoint.stream() (line 131):**
```python
except ValueError as e:
    logger.warning("Failed to parse TV NGram record: %s", e)
    continue
```

**Impact:** Non-ValueError exceptions in TV/Radio endpoints will propagate and halt streaming, while VGKG will continue processing.

**Identified by:** pattern-recognition-specialist

## Proposed Solutions

### Option 1: Standardize on broad exception handling (like VGKGEndpoint)
**Pros:** Consistent error boundaries, more resilient
**Cons:** May hide bugs
**Effort:** Small
**Risk:** Low

### Option 2: Catch specific exceptions
**Pros:** More precise error handling
**Cons:** Need to identify all possible exception types
**Effort:** Medium
**Risk:** Medium

## Acceptance Criteria

- [x] All endpoints have consistent exception handling pattern
- [x] Error logging is consistent
- [x] Decision is documented in code comments

## Work Log

- 2026-01-20: Issue identified during code review
- 2026-01-21: Verified exception handling is consistent - all endpoints now use Exception with noqa: BLE001
