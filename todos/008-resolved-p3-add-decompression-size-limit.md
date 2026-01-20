# Add Decompression Size Limit (Security)

**ID:** 008
**Status:** pending
**Priority:** P3 (Nice-to-have - Security Enhancement)
**Tags:** code-review, security, performance

## Problem Statement

The `_extract_gzip` method reads gzip data in chunks but accumulates all decompressed data in memory without any size limit. A malicious or compromised GDELT server could serve a "gzip bomb."

## Findings

**File:** `src/py_gdelt/sources/files.py`
**Lines:** 474-495

```python
def _extract_gzip(self, compressed_data: bytes) -> bytes:
    result = io.BytesIO()
    with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gz:
        chunk_size = 1024 * 1024  # 1MB chunks
        while True:
            chunk = gz.read(chunk_size)
            if not chunk:
                break
            result.write(chunk)  # No size limit check!
    return result.getvalue()
```

**Impact:** Memory exhaustion leading to DoS. Requires compromising data source or MITM on HTTP.

## Proposed Solutions

### Option 1: Add Maximum Decompressed Size Limit (Recommended)
**Effort:** Low
**Risk:** Very Low
**Pros:** Prevents memory exhaustion attacks
**Cons:** Could reject legitimate large files (mitigate with configurable limit)

```python
MAX_DECOMPRESSED_SIZE = 500 * 1024 * 1024  # 500MB

def _extract_gzip(self, compressed_data: bytes) -> bytes:
    result = io.BytesIO()
    total_size = 0
    with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gz:
        chunk_size = 1024 * 1024
        while True:
            chunk = gz.read(chunk_size)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_DECOMPRESSED_SIZE:
                raise DataError(f"Decompressed size exceeds {MAX_DECOMPRESSED_SIZE} bytes")
            result.write(chunk)
    return result.getvalue()
```

## Acceptance Criteria

- [ ] Maximum decompression size limit implemented
- [ ] Clear error message when limit exceeded
- [ ] Limit is configurable via settings (optional)
- [ ] `make ci` passes

## Work Log

| Date | Author | Action |
|------|--------|--------|
| 2026-01-20 | Claude | Created from code review |
