---
title: "fix: Replace pattern-based URL generation with master list filtering"
type: fix
date: 2026-02-20
task_list_id: 78cd2e8c-3852-4cbc-a88b-c5f4ab7d9376
---

# fix: Replace pattern-based URL generation with master list filtering

## Overview

`FileSource.get_files_for_date_range()` generates deterministic URLs from timestamp patterns (every 15 min), producing phantom URLs for time slots GDELT never published. Meanwhile, `get_master_file_list()` exists but has a parsing bug (returns full `"size hash url"` lines instead of just URLs) and isn't used for date-range selection.

This plan fixes the parsing bug and replaces pattern-based generation with master-list filtering for core types (export, mentions, gkg), making ingestion completeness checks accurate.

## Problem Statement

**Current behavior:** `get_files_for_date_range()` constructs URLs like `http://data.gdeltproject.org/gdeltv2/20240101001500.export.CSV.zip` for every 15-minute slot in the range. GDELT doesn't publish files for every slot, so downstream orchestration sees phantom 404s as "missing" data.

**Root causes:**
1. `get_master_file_list()` has a parsing bug: GDELT's master list format is `size_bytes md5_hash url` per line, but the code treats each full line as a URL
2. `get_files_for_date_range()` doesn't use the master list at all -- it generates URLs from patterns

**Impact:** False "missing" expectations in ETL completeness checks. The VGKG URL pattern bug (documented in `docs/bugreports/2026-02-14-vgkg-url-pattern-bug.md`) is another example of pattern-based generation silently breaking when GDELT changes naming.

## Proposed Solution

1. Fix `get_master_file_list()` to parse the 3-column format correctly
2. Replace pattern generation with master list filtering for core v2 types
3. Keep pattern generation only for graph/ngrams (not in master list)

### Scope

**Master list facts (verified against live data):**
- Main list: ~1.1M lines, ~115 MB, covers 2015-02-18 to present
- Translation list: ~127 MB, same format
- Format per line: `size_bytes md5_hash url` (space-separated)
- Only covers v2 core types: `export`, `mentions`, `gkg`
- Does NOT cover: `ngrams`, `gqg`, `geg`, `gfg`, `ggg`, `gemg`, `gal`

## Technical Approach

### Files to modify

- `src/py_gdelt/sources/files.py` -- Fix parsing, add filtering, replace generation
- `tests/test_sources_files.py` -- Update mocks, add new tests

### 1. Fix `get_master_file_list()` parsing

Add `_parse_master_file_line()` and fix the line parsing in `get_master_file_list()`.

```diff
--- a/src/py_gdelt/sources/files.py
+++ b/src/py_gdelt/sources/files.py
@@ -1,4 +1,5 @@
 """FileSource for downloading and extracting GDELT data files.
+from __future__ import annotations

@@ -64,6 +65,10 @@
 GRAPH_FILE_TYPES: Final[tuple[str, ...]] = get_args(GraphFileType)

+# Core file types covered by the master file list (v2 only)
+CORE_FILE_TYPES: Final[frozenset[str]] = frozenset({"export", "mentions", "gkg"})
+

@@ -170,8 +175,11 @@
-                # Parse URLs from content (one URL per line)
-                file_urls = [line.strip() for line in content.splitlines() if line.strip()]
+                # Parse URLs from content (format: "size hash url" per line)
+                file_urls = []
+                for line in content.splitlines():
+                    url = self._parse_master_file_line(line)
+                    if url is not None:
+                        file_urls.append(url)
                 all_urls.extend(file_urls)
```

```diff
--- a/src/py_gdelt/sources/files.py
+++ b/src/py_gdelt/sources/files.py
@@ -530,3 +530,22 @@
         return None

+    @staticmethod
+    def _parse_master_file_line(line: str) -> str | None:
+        """Extract URL from a master file list line.
+
+        GDELT master file list format: "size_bytes md5_hash url"
+
+        Args:
+            line: Raw line from master file list.
+
+        Returns:
+            Extracted URL, or None if line is blank/malformed.
+        """
+        stripped = line.strip()
+        if not stripped:
+            return None
+        parts = stripped.split()
+        if len(parts) >= 3:
+            return parts[2]
+        # Fallback: treat the whole line as a URL if it starts with http
+        if stripped.startswith("http"):
+            return stripped
+        logger.debug("Skipping malformed master file line: %s", stripped[:100])
+        return None
```

### 2. Add URL filtering helper

```diff
--- a/src/py_gdelt/sources/files.py
+++ b/src/py_gdelt/sources/files.py
@@ -530,3 +530,40 @@

+    def _filter_urls_by_type_and_range(
+        self,
+        urls: list[str],
+        file_type: FileType,
+        start_date: datetime,
+        end_date: datetime,
+    ) -> list[str]:
+        """Filter master list URLs by file type suffix and timestamp range.
+
+        Args:
+            urls: URLs from master file list.
+            file_type: File type to filter for.
+            start_date: Start of date range (inclusive).
+            end_date: End of date range (inclusive).
+
+        Returns:
+            Filtered and sorted list of matching URLs.
+        """
+        pattern = FILE_TYPE_PATTERNS[file_type]
+        matched: list[tuple[datetime, str]] = []
+
+        for url in urls:
+            if not url.endswith(pattern):
+                continue
+            file_date = self._extract_date_from_url(url)
+            if file_date is None:
+                continue
+            # _extract_date_from_url returns UTC-aware datetimes;
+            # compare naive if start_date/end_date are naive
+            cmp_date = file_date.replace(tzinfo=None)
+            if start_date <= cmp_date <= end_date:
+                matched.append((cmp_date, url))
+
+        # Sort by timestamp ascending for consistent ordering
+        matched.sort(key=lambda pair: pair[0])
+        return [url for _, url in matched]
```

### 3. Replace pattern generation in `get_files_for_date_range()`

```diff
--- a/src/py_gdelt/sources/files.py
+++ b/src/py_gdelt/sources/files.py
@@ -215,6 +215,27 @@
         if file_type not in FILE_TYPE_PATTERNS:
             valid_types = ", ".join(FILE_TYPE_PATTERNS.keys())
             err_msg = f"Unknown file_type '{file_type}'. Valid types: {valid_types}"
             raise ValueError(err_msg)

+        # Core types: filter from master list (source of truth)
+        if file_type in CORE_FILE_TYPES:
+            return await self._get_files_from_master_list(
+                start_date=start_date,
+                end_date=end_date,
+                file_type=file_type,
+                include_translation=include_translation,
+            )
+
+        # Graph/ngrams: use pattern generation (not in master list)
-        pattern = FILE_TYPE_PATTERNS[file_type]
+        return self._generate_pattern_urls(
+            start_date=start_date,
+            end_date=end_date,
+            file_type=file_type,
+            include_translation=include_translation,
+        )
```

Extract the existing pattern generation into `_generate_pattern_urls()` (private, unchanged logic). Add `_get_files_from_master_list()`:

```diff
+    async def _get_files_from_master_list(
+        self,
+        start_date: datetime,
+        end_date: datetime,
+        file_type: FileType,
+        include_translation: bool,
+    ) -> list[str]:
+        """Get file URLs by filtering the master list.
+
+        Args:
+            start_date: Start of date range (inclusive).
+            end_date: End of date range (inclusive).
+            file_type: Type of files to get.
+            include_translation: If True, include translation files.
+
+        Returns:
+            Filtered list of URLs sorted by timestamp.
+        """
+        master_urls = await self.get_master_file_list()
+        urls = self._filter_urls_by_type_and_range(
+            master_urls, file_type, start_date, end_date,
+        )
+
+        if include_translation:
+            trans_urls = await self.get_master_file_list(include_translation=True)
+            # Translation master list includes both regular and translation URLs,
+            # so filter for translation-specific pattern
+            trans_pattern = f".translation{FILE_TYPE_PATTERNS[file_type]}"
+            trans_filtered = [
+                u for u in self._filter_urls_by_type_and_range(
+                    trans_urls, file_type, start_date, end_date,
+                )
+                if trans_pattern in u
+            ]
+            urls.extend(trans_filtered)
+
+        return urls
```

> **WHY `_filter_urls_by_type_and_range` strips tzinfo for comparison:** `_extract_date_from_url` returns UTC-aware datetimes, but callers (DataFetcher) pass naive datetimes via `datetime.combine(date, datetime.min.time())`. Comparing naive to aware raises TypeError.

### 4. Handle translation master list correctly

The translation master list is a separate file (`masterfilelist-translation.txt`). Current `get_master_file_list(include_translation=True)` fetches both lists and combines them. This means the combined list has both regular and translation URLs. The `_get_files_from_master_list()` method handles this by:

1. First fetching the main master list and filtering for the file type
2. If `include_translation`, separately fetch with `include_translation=True` and filter for the `.translation` pattern

This avoids double-including regular URLs when translation is requested.

## Acceptance Criteria

- [x] `get_master_file_list()` returns correctly parsed URLs (not full "size hash url" lines)
- [x] `_parse_master_file_line()` handles: normal 3-column lines, blank lines, malformed lines
- [x] `get_files_for_date_range()` for export/mentions/gkg returns only URLs that exist in master list
- [x] `get_files_for_date_range()` for graph/ngrams types still uses pattern generation
- [x] Translation files are correctly filtered from the translation master list
- [x] Results are sorted by timestamp ascending
- [x] `from __future__ import annotations` added to `files.py`
- [x] `CORE_FILE_TYPES` constant exported in `__all__`
- [x] All existing tests updated for new behavior
- [x] New tests cover: master list parsing, date range filtering, mixed file types, empty results
- [x] `make ci` passes (lint + typecheck + tests)

## Dependencies & Risks

| Risk | Mitigation |
|------|------------|
| 115 MB master list download is slow on first call | Already cached with TTL (default 5 min). First call is a one-time cost per cache period. |
| Master list unavailable (network error) | `get_master_file_list()` already raises `APIError`/`APIUnavailableError` - callers handle this |
| 1.1M line parsing performance | Simple string split per line, O(n) single pass. Filtering by suffix + timestamp is also O(n). |
| Breaking change: core types now require HTTP client | `get_files_for_date_range()` is already `async` and callers always use it within initialized context |
| Master list format changes | `_parse_master_file_line()` has fallback for URL-only lines |

## References

- Bug report validating this approach: `docs/bugreports/2026-02-14-vgkg-url-pattern-bug.md`
- Current implementation: `src/py_gdelt/sources/files.py:128` (get_master_file_list), `src/py_gdelt/sources/files.py:192` (get_files_for_date_range)
- Callers: `src/py_gdelt/sources/fetcher.py:281`, `src/py_gdelt/sources/fetcher.py:599`, `src/py_gdelt/sources/fetcher.py:658`
- Existing tests: `tests/test_sources_files.py`
- Cache implementation: `src/py_gdelt/cache.py`
- Date utilities: `src/py_gdelt/utils/dates.py`

## Tasks

Run `/workflows:work` with this plan to execute. Tasks are stored in `~/.claude/tasks/78cd2e8c-3852-4cbc-a88b-c5f4ab7d9376/`.

To work on these tasks from another session:
```
skill: import-tasks 78cd2e8c-3852-4cbc-a88b-c5f4ab7d9376
```
