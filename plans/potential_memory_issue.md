# Memory Efficiency Analysis - Spike Investigation

**Date:** 2026-01-04
**Status:** Review complete, corrected fix identified
**Reviewed by:** 5 agents (simplicity, architecture, security, kieran-python, skeptical-simplicity)

---

## Executive Summary

**ONE real bug identified:** `stream_files()` uses `TaskGroup` which materializes ALL downloads before yielding.

**The original proposed fix was WRONG** - it would kill concurrency entirely.

Most other "issues" in the original analysis were overblown or factually incorrect.

---

## The Real Bug: stream_files() TaskGroup

**File:** `src/py_gdelt/sources/files.py:382-394`

**Problem:** TaskGroup waits for ALL tasks to complete before the context manager exits:

```python
async with asyncio.TaskGroup() as tg:
    tasks = [tg.create_task(self._safe_download_and_extract(url)) for url in urls]
# ^^^ TaskGroup blocks here until ALL downloads complete

for task in tasks:  # Only runs AFTER everything downloaded
    yield url, data
```

**Impact:** For a week of GDELT data (672 files × 10-50MB) = potential 30GB+ RAM.

### WRONG Fix (from original analysis)

```python
# DON'T DO THIS - kills concurrency, 10x slower
for url in urls:
    result = await download_one(url)  # Sequential!
    if result:
        yield result
```

### CORRECT Fix: asyncio.as_completed()

Maintains parallelism while streaming results as they complete:

```python
async def stream_files(
    self,
    urls: Iterable[str],
    *,
    max_concurrent: int | None = None,
) -> AsyncIterator[tuple[str, bytes]]:
    """Stream file downloads with bounded concurrency and true streaming."""
    limit = max_concurrent or self.settings.max_concurrent_downloads
    semaphore = asyncio.Semaphore(limit)

    async def bounded_download(url: str) -> tuple[str, bytes] | None:
        async with semaphore:
            return await self._safe_download_and_extract(url)

    tasks = [asyncio.create_task(bounded_download(url)) for url in urls]

    for coro in asyncio.as_completed(tasks):
        result = await coro
        if result is not None:
            yield result
```

**Note:** This still creates all tasks upfront. For truly bounded memory with huge URL lists, use a sliding window pattern with `asyncio.wait(FIRST_COMPLETED)`.

---

## Issues Dismissed After Review

### Double Materialization (events.py) - OVERBLOWN

**Original claim:** "Doubles memory during deduplication"

**Reality:** `list(apply_dedup(iter(original_list)))` consumes the iterator incrementally. Python's GC handles the original list as it's iterated. Not a significant memory issue.

**Action:** Skip or low-priority micro-optimization.

### Bloom Filter for Dedup - YAGNI

**Original suggestion:** Use probabilistic data structure

**Problems:**
- Bloom filters have **false positives** - would incorrectly skip unique events
- Data corruption is worse than OOM
- Adds complexity and dependencies

**Action:** Don't implement. Document memory requirements instead.

### Master File List 500MB - FACTUALLY WRONG

**Original claim:** "500MB+ RAM for the list"

**Reality:**
- GDELT publishes ~35K files/year
- Each URL is ~100 chars
- 10 years = 350K × 100 = **~35MB**, not 500MB

**Action:** Non-issue.

### BigQuery Not Streaming - FACTUALLY WRONG

**Original claim:** "`query_job.result()` fetches all results"

**Reality:** BigQuery Python client's `result()` returns a **paging iterator**. It streams by default.

**Action:** Non-issue.

### Cache Size Limits - DISK ISSUE

**Original claim:** Memory issue from cache

**Reality:** This is a **disk space** issue, not memory. Users can clear cache manually.

**Action:** Low priority, maybe add `cache.prune()` convenience method later.

---

## Security Gaps to Address

Identified during security review - should be addressed regardless of memory fixes:

| Gap | Recommendation |
|-----|----------------|
| No date range limit | Add max 365 days per query |
| No URL count limit | Add max 50,000 URLs per operation |
| Missing cancellation handling | Add proper cleanup in streaming |

---

## Final Priority List

| Priority | Issue | Action | Effort |
|----------|-------|--------|--------|
| **P0** | stream_files() TaskGroup | Fix with as_completed() | Medium |
| P2 | Date/URL limits | Add safety bounds | Low |
| P3 | Cache prune method | Add convenience method | Low |
| Skip | Double materialization | Not worth fixing | - |
| Skip | Bloom filter | YAGNI | - |
| Skip | Master file list | Non-issue | - |
| Skip | BigQuery streaming | Already works | - |

---

## Implementation Notes

1. The `stream_files()` fix is the **only critical change**
2. Test with real GDELT data (week range) to verify memory improvement
3. Add integration test that monitors memory during large downloads
4. Consider adding `max_urls` parameter as safety valve

---

*Original analysis: Gemini brainstorm agent*
*Review: 5-agent parallel review (simplicity, architecture, security, kieran-python, skeptical-simplicity)*
*Conclusion: 1 real bug, 1 wrong fix corrected, 4 false positives dismissed*
