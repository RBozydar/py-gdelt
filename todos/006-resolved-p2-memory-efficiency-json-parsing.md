# Improve Memory Efficiency in JSON-NL Parsing

**ID:** 006
**Status:** pending
**Priority:** P2 (Important)
**Tags:** code-review, performance, memory

## Problem Statement

The JSON-NL parsing implementation loads entire files into memory multiple times, contradicting the goal of "memory usage stays bounded during streaming."

## Findings

**File:** `src/py_gdelt/parsers/graphs.py`
**Lines:** 80-87

Current implementation creates 3 copies of the data in memory:
```python
def _parse_jsonl(data: bytes, model_cls: type[T]) -> Iterator[T]:
    decompressed = _decompress_if_needed(data)  # Full file in memory (copy 1)
    text = decompressed.decode("utf-8", errors="replace")  # UTF-8 string (copy 2)
    for line_num, line in enumerate(text.splitlines(), start=1):  # List of lines (copy 3)
```

**Impact:**
- A 100MB gzipped file becomes ~1.5GB in memory
- With default 10 concurrent downloads, this could cause 15GB+ memory spike

## Proposed Solutions

### Option 1: Stream Decompression and Line-by-Line Parsing (Recommended)
**Effort:** Medium
**Risk:** Low
**Pros:** 3-5x memory reduction
**Cons:** Slightly more complex code

```python
def _parse_jsonl(data: bytes, model_cls: type[T]) -> Iterator[T]:
    if data.startswith(b"\x1f\x8b"):
        fileobj = io.BytesIO(data)
        reader = gzip.open(fileobj, "rt", encoding="utf-8", errors="replace")
    else:
        reader = io.StringIO(data.decode("utf-8", errors="replace"))

    for line_num, line in enumerate(reader, start=1):
        line = line.rstrip("\n\r")
        if not line:
            continue
        # ... parse line
```

### Option 2: Use io.StringIO Instead of splitlines()
**Effort:** Low
**Risk:** Very Low
**Pros:** 30-50% memory reduction (quick win)
**Cons:** Doesn't address decompression issue

## Acceptance Criteria

- [ ] Memory usage per file is reduced
- [ ] Streaming behavior preserved
- [ ] All tests pass
- [ ] `make ci` passes

## Work Log

| Date | Author | Action |
|------|--------|--------|
| 2026-01-20 | Claude | Created from code review |
