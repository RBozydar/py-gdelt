---
status: resolved
priority: p3
issue_id: "007"
tags: [code-review, dead-code, cleanup]
dependencies: []
---

# Remove Dead Code

## Problem Statement

Two pieces of dead code exist in the codebase:
1. `_decompress_if_needed` in parsers is only used once (could be inlined)
2. `_upgrade_to_https` in FileSource is completely unused

## Findings

**From code-simplicity-reviewer:**
- `_decompress_if_needed` function defined but only used in `parse_gfg`
- `_parse_jsonl` duplicates the gzip detection logic inline
- `_upgrade_to_https` method is unused with comment "currently unused"

**From coherence-reviewer:**
- `_decompress_if_needed` only called from one location
- Could be inlined or used consistently

## Evidence

```python
# src/py_gdelt/parsers/graphs.py:56-67 - only used once at line 188
def _decompress_if_needed(data: bytes) -> bytes:
    """Decompress data if it is gzip-compressed."""
    if data.startswith(b"\x1f\x8b"):
        return gzip.decompress(data)
    return data

# src/py_gdelt/sources/files.py:508-525 - never used
@staticmethod
def _upgrade_to_https(url: str) -> str:
    """Upgrade HTTP URL to HTTPS.

    Note:
        This method is currently unused because data.gdeltproject.org only
        supports HTTP...
    """
```

## Proposed Solutions

### Option 1: Remove Both (Recommended)
**Effort:** Small
**Risk:** None

- Remove `_upgrade_to_https` (YAGNI - if needed later, add it then)
- Either inline `_decompress_if_needed` into `parse_gfg` or use it in `_parse_jsonl` too

**Pros:** Cleaner codebase, no misleading code
**Cons:** None

### Option 2: Keep _decompress_if_needed
**Effort:** Small
**Risk:** None

The function has a clear purpose and might be useful for consistency.

**Pros:** Reusable utility
**Cons:** Currently only used once

## Recommended Action

Option 1 - Remove `_upgrade_to_https` and inline `_decompress_if_needed` into `parse_gfg`.

## Technical Details

**Affected Files:**
- `src/py_gdelt/sources/files.py:508-525` - Remove `_upgrade_to_https`
- `src/py_gdelt/parsers/graphs.py:56-67` - Inline into `parse_gfg` or use in `_parse_jsonl`

**Estimated LOC reduction:** 30 lines

## Acceptance Criteria

- [ ] No unused functions in the codebase
- [ ] Tests pass
- [ ] No functionality change

## Work Log

| Date | Action | Result |
|------|--------|--------|
| 2026-01-24 | Identified in code review | Finding documented |

## Resources

- FileSource: `src/py_gdelt/sources/files.py`
- Parsers: `src/py_gdelt/parsers/graphs.py`
