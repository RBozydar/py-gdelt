---
status: resolved
priority: p1
issue_id: "001"
tags: [code-review, testing, graph-datasets]
dependencies: []
---

# Missing GraphEndpoint Unit Tests

## Problem Statement

The `GraphEndpoint` class (`src/py_gdelt/endpoints/graphs.py`) has **no unit tests**. The test file `tests/unit/test_graphs.py` only covers models, parsers, and filters but has zero coverage for the endpoint itself.

This is a critical gap because `GraphEndpoint` contains:
- Error handling logic (`raise`/`warn`/`skip` policies)
- Language filtering logic
- Integration with `DataFetcher`

**Coverage report shows only 13.29%** for `src/py_gdelt/endpoints/graphs.py` - the lowest of any endpoint.

## Findings

**From kieran-python-reviewer:**
- The test file only covers models, parsers, and filters
- Other endpoint tests (e.g., `test_endpoints_vgkg.py`) include initialization, streaming, and error policy tests
- This pattern should be followed for `GraphEndpoint`

**From git-history-analyzer:**
- The endpoint was implemented in a single commit without corresponding tests
- This matches the pattern of rapid AI-assisted development without test-first approach

## Evidence

```
src/py_gdelt/endpoints/graphs.py    100     79     58      0  13.29%
```

Compare to other endpoints:
```
src/py_gdelt/endpoints/vgkg.py      115     11     30      4  89.66%
src/py_gdelt/endpoints/tv_gkg.py    124     13     32      5  87.18%
```

## Proposed Solutions

### Option 1: Add Comprehensive Tests (Recommended)
**Effort:** Medium
**Risk:** Low

Create `tests/unit/test_endpoints_graphs.py` following the pattern in `test_endpoints_vgkg.py`:

```python
class TestGraphEndpointInit:
    """Test GraphEndpoint initialization."""
    def test_init_default(self): ...
    def test_init_with_error_policy(self): ...

class TestGraphEndpointStreaming:
    """Test streaming with mocked fetcher."""
    def test_stream_gqg_yields_records(self): ...
    def test_stream_gqg_filters_by_language(self): ...

class TestGraphEndpointErrorPolicies:
    """Test error_policy='raise', 'warn', 'skip'."""
    def test_error_policy_raise(self): ...
    def test_error_policy_warn(self): ...
    def test_error_policy_skip(self): ...
```

**Pros:** Ensures behavior is tested, catches regressions
**Cons:** Requires time investment

### Option 2: Minimal Coverage Tests
**Effort:** Small
**Risk:** Medium

Add only initialization and basic happy-path tests.

**Pros:** Quick win for coverage
**Cons:** Doesn't test error handling or edge cases

## Recommended Action

Option 1 - Add comprehensive tests following the existing `test_endpoints_vgkg.py` pattern.

## Technical Details

**Affected Files:**
- Create: `tests/unit/test_endpoints_graphs.py`

**Test Categories Needed:**
1. Initialization tests
2. Async context manager tests
3. Streaming tests with mocked `DataFetcher`
4. Language filtering tests
5. Error policy tests (`raise`, `warn`, `skip`)

## Acceptance Criteria

- [ ] `GraphEndpoint` has unit tests covering initialization
- [ ] Tests verify streaming yields correct record types
- [ ] Tests verify language filtering works correctly
- [ ] Tests verify all three error policies behave correctly
- [ ] Coverage for `graphs.py` exceeds 85%

## Work Log

| Date | Action | Result |
|------|--------|--------|
| 2026-01-24 | Identified in code review | Finding documented |

## Resources

- Pattern file: `tests/unit/test_endpoints_vgkg.py`
- Target file: `src/py_gdelt/endpoints/graphs.py`
