---
status: resolved
priority: p3
issue_id: "006"
tags: [code-review, slop, cleanup, graph-datasets]
dependencies: []
---

# Remove Unnecessary Comments (AI Slop)

## Problem Statement

Several comments in the graph datasets code state the obvious or explain code that is self-documenting. These are typical AI-generated code patterns ("slop").

## Findings

**From slop-detector:**

| File | Lines | Comment | Issue |
|------|-------|---------|-------|
| `endpoints/graphs.py` | 152, 194, 236, 276, 318, 360 | `# skip: continue silently` | Redundant - the else clause after warn is obvious |
| `parsers/graphs.py` | 187 | `# Decompress if needed` | Function name is self-documenting |
| `parsers/graphs.py` | 191-193 | `# Decode as UTF-8`, `# Parse TSV with csv.reader` | Obvious from code |
| `parsers/graphs.py` | 197, 201 | `# Skip empty rows`, `# Validate column count` | The `if` conditions explain themselves |
| `parsers/graphs.py` | 210-221 | `# Create internal _RawGFGRecord`, `# Convert to public GFGRecord` | Code intent is clear |

## Evidence

```python
# endpoints/graphs.py - repeated 6 times:
if self._error_policy == "warn":
    logger.warning("Error parsing %s: %s", url, e)
# skip: continue silently  # <-- This comment is redundant

# parsers/graphs.py:
data = _decompress_if_needed(data)  # Decompress if needed  # <-- Redundant
```

## Proposed Solutions

### Option 1: Remove All Redundant Comments (Recommended)
**Effort:** Small
**Risk:** None

Remove comments that add no value beyond what the code already expresses.

**Pros:** Cleaner code, less maintenance
**Cons:** None

### Option 2: Keep Comments
**Effort:** None
**Risk:** None

Some developers prefer comments as navigation aids.

**Pros:** May help quick scanning
**Cons:** Comments can become stale

## Recommended Action

Option 1 - Remove redundant comments to improve code cleanliness.

## Technical Details

**Affected Files:**
- `src/py_gdelt/endpoints/graphs.py`: Remove 6 `# skip: continue silently` comments
- `src/py_gdelt/parsers/graphs.py`: Remove ~8 step-by-step comments

## Acceptance Criteria

- [ ] Redundant comments removed
- [ ] Meaningful comments (format explanations, etc.) retained
- [ ] Code still readable

## Work Log

| Date | Action | Result |
|------|--------|--------|
| 2026-01-24 | Identified in code review | Finding documented |

## Resources

- Endpoint: `src/py_gdelt/endpoints/graphs.py`
- Parsers: `src/py_gdelt/parsers/graphs.py`
