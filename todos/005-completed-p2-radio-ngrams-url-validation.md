---
title: Radio NGrams Inventory URL Injection Risk
priority: p2
status: completed
tags:
  - code-review
  - security
created: 2026-01-20
completed: 2026-01-21
---

## Problem Statement

The Radio NGrams endpoint fetches inventory files from GDELT and directly uses URLs from the response without validating they match expected patterns. Combined with HTTP (not HTTPS) transport, this creates a potential SSRF risk if an attacker can MITM the inventory fetch.

## Findings

**Location:** `/home/rbw/repo/py-gdelt-dev--feat-add-missing-filebased-datasets/src/py_gdelt/endpoints/radio_ngrams.py` (lines 170-189)

```python
async def _build_urls(self, filter_obj: BroadcastNGramsFilter) -> list[str]:
    # ...
    for line in response.text.strip().split("\n"):
        file_url = line.strip()
        if not file_url:
            continue

        # Filter by station if specified
        if filter_obj.station and filter_obj.station.upper() not in file_url.upper():
            continue

        # Filter by ngram size
        if ngram_type not in file_url:
            continue

        urls.append(file_url)  # Directly appends URL from external source
```

**Impact:** If attacker compromises inventory file (via MITM due to HTTP), they could inject arbitrary URLs that FileSource would fetch.

**Identified by:** security-sentinel

## Proposed Solutions

### Option 1: Add URL validation (Recommended)
**Pros:** Prevents URL injection, minimal performance impact
**Cons:** May reject valid URLs if GDELT changes patterns
**Effort:** Small
**Risk:** Low

```python
# Validate that URLs from inventory files match expected patterns
if not file_url.startswith(self.BASE_URL):
    logger.warning("Unexpected URL in inventory, skipping: %s", file_url)
    continue
```

### Option 2: Domain allowlist
**Pros:** More robust validation
**Cons:** More code to maintain
**Effort:** Medium
**Risk:** Low

## Acceptance Criteria

- [x] All URLs from inventory are validated against expected patterns
- [x] Unexpected URLs are logged and skipped
- [x] Normal operation unaffected

## Work Log

- 2026-01-20: Issue identified during security review
- 2026-01-21: Added _validate_url() method using urllib.parse to validate scheme, host, and path
