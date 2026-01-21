---
title: Redundant Type Aliases Provide No Value
priority: p3
status: completed
tags:
  - code-review
  - code-simplicity
created: 2026-01-20
completed: 2026-01-21
---

## Problem Statement

Type aliases `TVNGramRecord`, `RadioNGramRecord`, `TVNGramsFilter`, and `RadioNGramsFilter` are simple aliases that provide no semantic distinction. They add no type safety since both aliases point to the same class.

## Findings

**Location:** `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/models/ngrams.py` (lines 151-153)
```python
TVNGramRecord = BroadcastNGramRecord
RadioNGramRecord = BroadcastNGramRecord
```

**Location:** `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/filters.py` (lines 352-354)
```python
TVNGramsFilter = BroadcastNGramsFilter
RadioNGramsFilter = BroadcastNGramsFilter
```

**Identified by:** code-simplicity-reviewer

## Proposed Solutions

### Option 1: Remove aliases, use base class directly
**Pros:** Simpler code, less confusion
**Cons:** Less semantic naming in endpoint signatures
**Effort:** Small
**Risk:** Low

### Option 2: Keep aliases, add docstrings for clarity
**Pros:** Semantic clarity for users
**Cons:** Still provides no type safety
**Effort:** Minimal
**Risk:** None

### Option 3: Use `TypeAlias` annotation (Recommended)
**Pros:** More explicit, better IDE support
**Cons:** Minor change
**Effort:** Minimal
**Risk:** None

```python
from typing import TypeAlias
TVNGramRecord: TypeAlias = BroadcastNGramRecord
```

## Acceptance Criteria

- [x] Type aliases are either removed or properly annotated
- [x] Documentation is clear about the relationship

## Work Log

- 2026-01-20: Issue identified during code review
- 2026-01-21: Verified type aliases already have TypeAlias annotation in ngrams.py
