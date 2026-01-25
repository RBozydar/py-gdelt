---
status: resolved
priority: p2
issue_id: "004"
tags: [code-review, api-design, graph-datasets]
dependencies: []
---

# Remove or Document Unused bigquery_source/fallback_enabled Parameters

## Problem Statement

`GraphEndpoint.__init__` accepts `bigquery_source` and `fallback_enabled` parameters but never uses them. The docstring notes "(unused for graph datasets)" but this creates a misleading API.

## Findings

**From code-simplicity-reviewer:**
- Unused parameters kept for "interface consistency" is a YAGNI violation
- If the interface needs them later, add them later

**From coherence-reviewer:**
- Parameters are accepted, passed to DataFetcher, but graph datasets never use BigQuery fallback

**From baseline-code-reviewer:**
- Misleading API - users might expect BigQuery fallback support for graph datasets

## Evidence

```python
# src/py_gdelt/endpoints/graphs.py:92-95
def __init__(
    self,
    file_source: FileSource,
    bigquery_source: BigQuerySource | None = None,  # Unused
    *,
    fallback_enabled: bool = True,  # Unused
    error_policy: Literal["raise", "warn", "skip"] = "warn",
) -> None:
```

The docstring states:
```
bigquery_source: Optional BigQuerySource (unused for graph datasets).
fallback_enabled: Whether to fallback to BigQuery (unused for graphs).
```

## Proposed Solutions

### Option 1: Remove Unused Parameters (Recommended)
**Effort:** Small
**Risk:** Low (breaking change for direct instantiation)

Remove `bigquery_source` and `fallback_enabled` from the signature since they're never used.

```python
def __init__(
    self,
    file_source: FileSource,
    *,
    error_policy: Literal["raise", "warn", "skip"] = "warn",
) -> None:
```

**Pros:** Clean API, no misleading parameters
**Cons:** Breaking change if anyone instantiates GraphEndpoint directly (unlikely - client.py manages this)

### Option 2: Keep for Interface Consistency
**Effort:** None
**Risk:** None

Keep parameters for API consistency with other endpoints that do use BigQuery.

**Pros:** Consistent interface across all endpoints
**Cons:** Misleading - parameters suggest functionality that doesn't exist

### Option 3: Add Warning When Provided
**Effort:** Small
**Risk:** None

Log a warning if `bigquery_source` is provided to a graph endpoint.

**Pros:** Informs users their config is being ignored
**Cons:** Adds complexity for a rare case

## Recommended Action

Option 1 - Remove unused parameters. The client.py can be updated to not pass these to GraphEndpoint.

## Technical Details

**Affected Files:**
- `src/py_gdelt/endpoints/graphs.py:92-95` - Remove params
- `src/py_gdelt/client.py:562-566` - Update GraphEndpoint instantiation

## Acceptance Criteria

- [ ] `GraphEndpoint.__init__` signature doesn't include unused params
- [ ] `GDELTClient.graphs` property updated accordingly
- [ ] Tests pass

## Work Log

| Date | Action | Result |
|------|--------|--------|
| 2026-01-24 | Identified in code review | Finding documented |

## Resources

- Endpoint: `src/py_gdelt/endpoints/graphs.py`
- Client: `src/py_gdelt/client.py:537-566`
