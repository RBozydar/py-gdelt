---
status: resolved
priority: p2
issue_id: "003"
tags: [code-review, refactoring, dry, graph-datasets]
dependencies: []
---

# Extract Duplicated Error Handling in GraphEndpoint Stream Methods

## Problem Statement

The same error handling logic is copy-pasted 6 times across all `stream_*` methods in `GraphEndpoint`. This violates DRY and makes maintenance error-prone.

## Findings

**From code-simplicity-reviewer:**
- Estimated 150+ LOC could be reduced to ~60 lines with a generic method
- All 6 stream methods have identical try/except blocks

**From architecture-strategist:**
- Violates DRY principle
- If error policy logic needs to change, 6 locations must be updated

**From coherence-reviewer:**
- Same error handling pattern repeated at lines 147-152, 189-194, 231-236, 271-276, 313-318, 355-360

## Evidence

```python
# This exact block appears 6 times:
except Exception as e:
    if self._error_policy == "raise":
        raise
    if self._error_policy == "warn":
        logger.warning("Error parsing %s: %s", url, e)
    # skip: continue silently
```

## Proposed Solutions

### Option 1: Extract Error Handler Method (Recommended)
**Effort:** Small
**Risk:** Low

```python
def _handle_parse_error(self, url: str, error: Exception) -> None:
    """Handle parsing errors according to error policy."""
    if self._error_policy == "raise":
        raise error
    if self._error_policy == "warn":
        logger.warning("Error parsing %s: %s", url, error)
    # skip: continue silently
```

**Pros:** Simple extraction, easy to understand
**Cons:** Still requires try/except in each method

### Option 2: Extract Generic Stream Method
**Effort:** Medium
**Risk:** Low

```python
async def _stream_generic(
    self,
    graph_type: str,
    date_range: DateRange,
    parser: Callable[[bytes], Iterator[T]],
    languages: list[str] | None,
) -> AsyncIterator[T]:
    """Generic streaming with error handling and language filtering."""
    async for url, data in self._fetcher.fetch_graph_files(graph_type, date_range):
        try:
            for record in parser(data):
                if languages and hasattr(record, "lang") and record.lang not in languages:
                    continue
                yield record
        except Exception as e:
            self._handle_parse_error(url, e)
```

**Pros:** Maximum DRY, single point of change
**Cons:** More complex type hints, may affect readability

### Option 3: Keep Current Design
**Effort:** None
**Risk:** Low

The current design preserves per-method type safety.

**Pros:** Each method is self-contained, type-safe
**Cons:** Code duplication remains

## Recommended Action

Option 1 - Extract error handler method. This is the minimal change that achieves DRY without overcomplicating the code.

## Technical Details

**Affected File:** `src/py_gdelt/endpoints/graphs.py`

**Lines to refactor:**
- 147-152, 189-194, 231-236, 271-276, 313-318, 355-360

## Acceptance Criteria

- [ ] Error handling logic exists in exactly one place
- [ ] All 6 stream methods use the shared error handler
- [ ] Tests pass
- [ ] No change in behavior

## Work Log

| Date | Action | Result |
|------|--------|--------|
| 2026-01-24 | Identified in code review | Finding documented |

## Resources

- File: `src/py_gdelt/endpoints/graphs.py`
