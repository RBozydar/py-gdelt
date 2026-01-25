---
status: resolved
priority: p2
issue_id: "002"
tags: [code-review, documentation, graph-datasets]
dependencies: []
---

# Fix Incorrect Section Comment Names in GraphEndpoint

## Problem Statement

The section comments in `src/py_gdelt/endpoints/graphs.py` use incorrect acronym expansions that differ from the docstrings. This actively misleads developers reading the code.

## Findings

**From baseline-code-reviewer and coherence-reviewer:**

| Line | Current Comment | Correct Name |
|------|-----------------|--------------|
| 154 | `GEG (Global Event Graph)` | Global Entity Graph |
| 196 | `GFG (Global Facebook Graph)` | Global Frontpage Graph |
| 238 | `GGG (Global Google Graph)` | Global Geographic Graph |
| 278 | `GEMG (Global Emotion Graph)` | Global Embedded Metadata Graph |
| 320 | `GAL (Global Activity Log)` | Article List |

The docstrings in the methods and model classes use the correct names.

**From git-history-analyzer:**
- This was supposedly fixed in commit 41ed035 ("fix: resolve code review TODOs"), but the section comments were not updated
- The docstrings were corrected but section comments were missed

## Evidence

```python
# Line 154
# --- GEG (Global Event Graph) ---

async def query_geg(self, filter_obj: GEGFilter) -> FetchResult[GEGRecord]:
    """Query Global Entity Graph records.  # <-- Docstring is correct
```

## Proposed Solutions

### Option 1: Fix Comments (Recommended)
**Effort:** Small
**Risk:** None

Update the 5 section comments to use correct names.

**Pros:** Quick fix, improves documentation accuracy
**Cons:** None

### Option 2: Remove Section Comments Entirely
**Effort:** Small
**Risk:** None

The slop-detector noted these section comments aren't used in other endpoint files.

**Pros:** Removes duplication between comments and docstrings
**Cons:** Loses visual separation in the file

## Recommended Action

Option 1 - Fix the comments to match the correct names.

## Technical Details

**Affected File:** `src/py_gdelt/endpoints/graphs.py`

**Changes:**
```python
# Line 154: Change to
# --- GEG (Global Entity Graph) ---

# Line 196: Change to
# --- GFG (Global Frontpage Graph) ---

# Line 238: Change to
# --- GGG (Global Geographic Graph) ---

# Line 278: Change to
# --- GEMG (Global Embedded Metadata Graph) ---

# Line 320: Change to
# --- GAL (Global Article List) ---
```

## Acceptance Criteria

- [ ] All 5 section comments use correct dataset names
- [ ] Comments match corresponding docstrings

## Work Log

| Date | Action | Result |
|------|--------|--------|
| 2026-01-24 | Identified in code review | Finding documented |

## Resources

- File: `src/py_gdelt/endpoints/graphs.py:154,196,238,278,320`
