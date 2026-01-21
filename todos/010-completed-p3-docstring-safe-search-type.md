---
title: Incorrect Docstring - _RawVGKG.safe_search Type Description
priority: p3
status: completed
tags:
  - code-review
  - documentation
created: 2026-01-20
completed: 2026-01-21
---

## Problem Statement

The `_RawVGKG` docstring states `safe_search` contains "floats 0-1", but the actual data and model implementation use integers (-1 to 4).

## Findings

**Location:** `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/models/_internal.py` (lines 289, 303)

```python
safe_search: str  # [6] adult<FIELD>spoof<FIELD>medical<FIELD>violence (floats 0-1)  # WRONG!
```

**Correct information from plan and SafeSearchDict:**
```python
# SafeSearch uses integers from Cloud Vision API:
# - UNKNOWN = -1
# - VERY_UNLIKELY = 0
# - UNLIKELY = 1
# - POSSIBLE = 2
# - LIKELY = 3
# - VERY_LIKELY = 4
```

**Identified by:** architecture-strategist

## Proposed Solutions

### Option 1: Fix the docstring (Recommended)
**Pros:** Accurate documentation
**Cons:** None
**Effort:** Minimal
**Risk:** None

```python
safe_search: str  # [6] adult<FIELD>spoof<FIELD>medical<FIELD>violence (integers -1 to 4)
```

## Acceptance Criteria

- [x] Docstring correctly describes SafeSearch as integers
- [x] Comment matches SafeSearchDict documentation

## Work Log

- 2026-01-20: Issue identified during code review
- 2026-01-21: Verified fix already in place - both the Attributes docstring (line 289) and inline comment (line 303) correctly state "integers -1 to 4"
