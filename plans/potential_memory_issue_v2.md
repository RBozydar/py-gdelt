# Memory Issue V2: Sliding Window Fix

**Date:** 2026-01-04
**Status:** Proposed fix after first attempt failed (20GB OOM)

---

## Why First Fix Failed

The `asyncio.as_completed()` fix still creates ALL tasks upfront:

```python
tasks = [asyncio.create_task(bounded_download(url)) for url in urls]  # ALL 673 created
```

**Problem:** No backpressure. Downloads complete faster than caller consumes results.
- 7 days = 673 files × ~50MB = **33GB potential accumulation**
- Semaphore limits concurrent downloads but results pile up

---

## Proposed Fix: Sliding Window

Only maintain N tasks. Create new task only when one completes.

```python
async def stream_files(
    self,
    urls: Iterable[str],
    *,
    max_concurrent: int | None = None,
) -> AsyncIterator[tuple[str, bytes]]:
    """Stream file downloads with bounded memory via sliding window."""
    import itertools

    limit = max_concurrent or self.settings.max_concurrent_downloads
    url_iter = iter(urls)
    pending: set[asyncio.Task[tuple[str, bytes] | None]] = set()

    # Prime with initial batch (only N tasks)
    for url in itertools.islice(url_iter, limit):
        task = asyncio.create_task(self._safe_download_and_extract(url))
        pending.add(task)

    while pending:
        # Wait for ANY task to complete
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            result = task.result()
            if result is not None:
                yield result  # Caller must consume before loop continues
                # ^^^ This is the backpressure point

            # Replenish from iterator
            try:
                url = next(url_iter)
                new_task = asyncio.create_task(self._safe_download_and_extract(url))
                pending.add(new_task)
            except StopIteration:
                pass
```

---

## Key Mechanism: Backpressure via Yield

The critical insight is that `yield result` **blocks the async generator** until the caller consumes it:

```python
async for url, data in source.stream_files(urls):
    process(data)  # Generator is paused here until this returns
```

With sliding window:
1. Generator yields result
2. Generator PAUSES until caller does `async for` next iteration
3. Only THEN does the loop continue and potentially start new downloads

This naturally throttles downloads to caller's consumption rate.

---

## Memory Analysis

| Scenario | Old (TaskGroup) | as_completed | Sliding Window |
|----------|-----------------|--------------|----------------|
| Tasks in memory | 673 | 673 | 10 |
| Max concurrent downloads | 10 | 10 | 10 |
| Result accumulation | All 673 | Up to 673 | 0-10 |
| **Memory bound** | 673 × 50MB | 673 × 50MB | **10 × 50MB** |
| **Worst case** | 33GB | 33GB | **500MB** |

---

## File to Modify

`src/py_gdelt/sources/files.py`
- Method: `stream_files()` (lines ~358-397)
- Replace current `asyncio.as_completed()` implementation

---

## Questions to Verify

1. Is `yield` truly blocking in async generators? (Yes, async generator pauses at yield)
2. Does `asyncio.wait(FIRST_COMPLETED)` work correctly with a set? (Yes)
3. What if `_safe_download_and_extract` raises? (Task.result() will re-raise)
4. What about cancellation? (Need to add cleanup in finally block)

---

## Potential Issue: Error Handling

Current code has try/except in `_safe_download_and_extract`. But if an exception escapes:
- `task.result()` will raise
- Need to decide: skip and continue, or propagate?

Suggestion: Wrap in try/except, log error, continue to next URL.

---

## Potential Issue: Cancellation

If caller cancels iteration early:
- Pending tasks will continue running
- Need `finally` block to cancel pending tasks

```python
try:
    while pending:
        # ... main loop
finally:
    for task in pending:
        task.cancel()
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)
```
