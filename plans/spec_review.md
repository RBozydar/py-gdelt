# API Spec v1 vs Implementation Review

## Overview

This document compares the API specification (`plans/api_spec_v1.md`) against the current py-gdelt implementation to identify gaps, differences, and issues.

---

## 1. Client Structure

### Spec vs Implementation

| Aspect | Spec | Implementation | Status |
|--------|------|----------------|--------|
| Main class | `GDELTClient` | `GDELTClient` | ✅ Match |
| Context manager | Both async/sync | Both async/sync | ✅ Match |
| Async pattern | Async-first, sync wrapper | Async-first | ✅ Match |
| HTTP client | httpx | httpx | ✅ Match |

### Endpoint Namespaces

| Spec Namespace | Implementation | Status |
|----------------|----------------|--------|
| `client.doc` | `DocEndpoint` | ✅ |
| `client.geo` | `GeoEndpoint` | ✅ |
| `client.context` | `ContextEndpoint` | ✅ |
| `client.tv` | `TVEndpoint` | ✅ |
| `client.tv_ai` | `TVAIEndpoint` | ✅ |
| `client.events` | `EventsEndpoint` | ✅ |
| `client.mentions` | `MentionsEndpoint` | ✅ |
| `client.gkg` | `GKGEndpoint` | ✅ |
| `client.ngrams` | `NGramsEndpoint` | ✅ |
| `client.lookups` | `Lookups` | ✅ |

---

## 2. Data Models

### Core Models

| Spec Model | Implementation | Differences |
|------------|----------------|-------------|
| `Location` | ✅ `Location` | Has `has_coordinates` property (bonus). `as_wkt()` present. |
| `ToneScores` | ✅ `ToneScores` | Field name differs: `activity_reference_density` vs spec's `activity_density` |
| `EntityMention` | ✅ `EntityMention` | Has `entity_type` and `confidence` (spec only has `name`, `offset`) |
| `Event` | ✅ `Event` | Matches spec. Has `is_conflict`/`is_cooperation` properties |
| `Actor` | ✅ `Actor` | Matches spec. Has `is_state_actor` property |
| `Mention` | ✅ `Mention` | Matches spec |
| `GKGRecord` | ✅ `GKGRecord` | Has additional fields: `sharing_image`, `all_names`, `primary_theme` property |
| `Quotation` | ✅ `Quotation` | Matches spec |
| `Amount` | ✅ `Amount` | Matches spec |
| `Article` | ✅ `Article` | Minor naming: `seendate` vs `seen_date`, `socialimage` vs `social_image` |
| `Timeline` | ✅ `Timeline` | Different structure: `timeline` list vs `data` list |
| `TimelinePoint` | ✅ `TimelinePoint` | Has `tone` field (spec only has `date`, `value`) |
| `NGramRecord` | ✅ `NGramRecord` | Matches spec |

### Issues Found

1. **ToneScores field naming**: `activity_reference_density` vs spec's `activity_density`
2. **Article field naming**: Uses raw GDELT names (`seendate`, `socialimage`) instead of Pythonic (`seen_date`, `social_image`)
3. **Timeline structure**: Uses `timeline` instead of `data` for the points list
4. **EntityMention**: Implementation has more fields than spec (entity_type, confidence)

---

## 3. Filter Objects

| Spec Filter | Implementation | Differences |
|-------------|----------------|-------------|
| `EventsFilter` | `EventFilter` | Name differs (plural vs singular). Implementation missing: `cameo_codes`, `min_goldstein`, `max_goldstein`, `quad_class`, `source_domains`, `deduplicate`, `dedupe_strategy` |
| `GKGFilter` | ✅ `GKGFilter` | Implementation missing: `source_domains` |
| `DocFilter` | ✅ `DocFilter` | Implementation missing: `raw_query` support. Uses `timespan` vs datetime range |
| `NGramsFilter` | ✅ `NGramsFilter` | Implementation missing: `bigram`, `trigram` support |
| `GeoFilter` | ✅ `GeoFilter` | Not explicitly in spec but implemented |
| `TVFilter` | ✅ `TVFilter` | Not explicitly in spec but implemented |

### Missing Filter Features (EventFilter)

Per spec, `EventsFilter` should have:
- `cameo_codes` - list of CAMEO codes
- `min_goldstein` / `max_goldstein`
- `quad_class` - list of quad classes (1-4)
- `source_domains` - list of domains
- `deduplicate` - bool
- `dedupe_strategy` - string

### Missing Filter Features (DocFilter)

Per spec:
- `raw_query` - for power users to use raw GDELT syntax
- Structured fields like `domain`, `theme`, `tone_min`, `tone_max`

---

## 4. Result Containers

| Spec | Implementation | Status |
|------|----------------|--------|
| `ResultStream[T]` | ✅ `ResultStream[T]` | Has `to_list()`, `to_dataframe()`, iteration |
| `FetchResult[T]` | ✅ `FetchResult[T]` | Has `data`, `failed`, `complete`, `partial` properties |
| `FailedRequest` | ✅ `FailedRequest` | Implementation has additional `status_code`, `retry_after` fields |

---

## 5. Lookups

| Spec Lookup | Implementation | Status |
|-------------|----------------|--------|
| `client.lookups.cameo` | ✅ `CAMEOCodes` | ✅ |
| `client.lookups.themes` | ✅ `GKGThemes` | ✅ |
| `client.lookups.countries` | ✅ `Countries` | ✅ Has both `fips_to_iso3()` AND `fips_to_iso2()` |
| `client.lookups.goldstein` | Integrated in CAMEOCodes | Different structure |

### Lookup Method Differences

| Spec Method | Implementation | Notes |
|-------------|----------------|-------|
| `cameo.get_description("142")` | `cameo["142"].description` | Access pattern differs |
| `cameo.get_goldstein("14")` | `cameo["14"].goldstein` or separate lookup | |
| `themes.search("climate")` | ✅ `themes.search()` | |
| `countries.fips_to_iso("US")` | ✅ `fips_to_iso3()` + `fips_to_iso2()` | Has BOTH versions |
| `countries.iso_to_fips("USA")` | ✅ `iso_to_fips("USA")` | Matches spec! |
| `countries.get_name("US")` | ✅ `get_name()` | Matches spec |
| `validate_cameo("999")` | Via filter validation | Not standalone on client.lookups |
| `countries.validate()` | ✅ `validate()` method exists | Works for FIPS or ISO |

---

## 6. Configuration

| Spec Option | Implementation | Status |
|-------------|----------------|--------|
| `bigquery_project` | ✅ | |
| `bigquery_credentials` | ✅ | |
| `cache_dir` | ✅ | |
| `cache_ttl` | ✅ | |
| `max_retries` | ✅ | |
| `timeout` | ✅ | |
| `fallback_to_bigquery` | ✅ | |
| `max_concurrent_requests` | ✅ `max_concurrent_downloads` | Name differs |

### Additional Implementation Settings (not in spec)
- `master_file_list_ttl` - TTL for master file list cache
- `validate_codes` - Enable/disable code validation

---

## 7. Error Handling

### Exception Hierarchy

| Spec Exception | Implementation | Status |
|----------------|----------------|--------|
| `GDELTError` | ✅ | |
| `APIError` | ✅ | |
| `RateLimitError` | ✅ | Has `retry_after` |
| `APIUnavailableError` | ✅ | |
| `InvalidQueryError` | ✅ | |
| `DataError` | ✅ | |
| `ParseError` | ✅ | Has `raw_data` |
| `ValidationError` | ✅ | |
| `InvalidCodeError` | ✅ | Has `code`, `code_type` |
| `ConfigurationError` | ✅ | |
| `BigQueryError` | ✅ | |

### Additional Implementation Exceptions
- `SecurityError` - Not in spec but implemented

---

## 8. Utilities

### Deduplication

| Spec | Implementation | Status |
|------|----------------|--------|
| `deduplicate(events, strategy)` | ✅ Exists in `utils/dedup.py` | |
| Via query parameter | ⚠️ Not in EventFilter | Missing `deduplicate` param |

### Strategies per Spec
- `url_only` ✅
- `url_date` ✅
- `url_date_location` (default) ✅
- `url_date_location_actors` ✅
- `aggressive` ✅

**Status**: All 5 strategies are implemented in `DedupeStrategy` enum. Both sync (`deduplicate()`) and async (`deduplicate_async()`) functions exist.

### Caching

| Spec | Implementation | Status |
|------|----------------|--------|
| `client.cache.clear()` | ⚠️ No public cache API | Missing |
| `client.cache.size()` | ⚠️ No public cache API | Missing |
| Historical caching | ✅ | |
| TTL caching | ✅ | |

---

## 9. Streaming Architecture

| Spec | Implementation | Status |
|------|----------------|--------|
| Generator-based iteration | ✅ `ResultStream` with `__aiter__` | |
| `to_list()` | ✅ | |
| `to_dataframe()` | ✅ (requires pandas) | |
| `to_json()` | ⚠️ Not found | Missing |
| `to_csv()` | ⚠️ Not found | Missing |

---

## 10. API-Specific Features

### DOC API

| Spec Mode | Implementation | Status |
|-----------|----------------|--------|
| `artlist` | ✅ | |
| `timelinevol` | ✅ | |
| `timelinevolraw` | Need to verify | |
| `timelinetone` | Need to verify | |
| `timelinelang` | Need to verify | |
| `timelinesourcecountry` | Need to verify | |
| `imagecollage` | Need to verify | |
| `tonechart` | Need to verify | |

---

## Summary of Gaps

### Critical Gaps (Functionality Missing)

| Gap | Severity | Notes |
|-----|----------|-------|
| EventFilter missing `cameo_codes` (list) | High | Currently only single `event_code` |
| EventFilter missing `min_goldstein`/`max_goldstein` | High | No Goldstein scale filtering |
| EventFilter missing `quad_class` (list) | Medium | No quad class filtering |
| EventFilter missing `source_domains` | Medium | No domain filtering |
| EventFilter missing `deduplicate`/`dedupe_strategy` | Medium | Dedup exists but not in filter |
| No public cache management API | Low | `client.cache.clear()`, `size()` |
| ResultStream missing `to_json()`, `to_csv()` | Low | Only has `to_list()`, `to_dataframe()` |
| DocFilter missing `raw_query` | Low | Power user feature |
| NGramsFilter missing `bigram`/`trigram` | Low | Only single ngram support |

### Naming Inconsistencies

| Spec | Implementation | Breaking? |
|------|----------------|-----------|
| `EventsFilter` (plural) | `EventFilter` | No (different name is fine) |
| `fips_to_iso()` | `fips_to_iso3()` + `fips_to_iso2()` | No (richer API) |
| `max_concurrent_requests` | `max_concurrent_downloads` | No (config internal) |
| `activity_density` | `activity_reference_density` | Minor (field name) |

### Model Field Differences

| Issue | Details | Impact |
|-------|---------|--------|
| Article field names | Uses GDELT raw names: `seendate`, `socialimage` | Low - has `seen_datetime` property |
| Timeline field name | Uses `timeline` vs spec's `data` | Low - has `points` property alias |
| TimelinePoint extra field | Has `tone` field (spec doesn't) | None - extra is fine |
| Article has aliases | `source_country` aliased from `sourcecountry` | None |

### What's Working Well ✅

- All 9 endpoints implemented (DOC, GEO, Context, TV, TVAI, Events, Mentions, GKG, NGrams)
- All 5 deduplication strategies implemented
- BigQuery fallback with security hardening
- Countries lookup has all methods from spec + extras
- Exception hierarchy matches spec
- Streaming architecture with `ResultStream`
- Configuration system complete
- All core models present (Event, Actor, Mention, GKGRecord, Article, etc.)

---

## Recommendations

### Priority 1 - High Value (EventFilter Enhancements)
1. Add `cameo_codes: list[str]` - for filtering by multiple CAMEO codes
2. Add `min_goldstein`/`max_goldstein: float` - for scale-based filtering
3. Add `quad_class: list[int]` - for cooperation/conflict classification
4. Add `source_domains: list[str]` - for source filtering
5. Add `deduplicate: bool` + `dedupe_strategy: DedupeStrategy` - integrate existing dedup

**Files to modify**: `src/py_gdelt/filters.py`

### Priority 2 - Medium Value (Utility Methods)
1. Add `to_json()` and `to_csv()` to `ResultStream`
2. Add public cache API: `client.cache.clear()`, `client.cache.size()`
3. Add `raw_query` support to `DocFilter`

**Files to modify**:
- `src/py_gdelt/utils/streaming.py`
- `src/py_gdelt/cache.py`
- `src/py_gdelt/client.py`

### Priority 3 - Low Value (Polish)
1. Add `bigram`/`trigram` to `NGramsFilter`
2. Document intentional differences from spec
3. Consider adding `GKGFilter.source_domains`

---

## Implementation Checklist

### Priority 1 - EventFilter Enhancements
**File**: `src/py_gdelt/filters.py`

- [ ] Add `cameo_codes: list[str] | None = None` field
- [ ] Add `min_goldstein: float | None = None` field
- [ ] Add `max_goldstein: float | None = None` field
- [ ] Add `quad_class: list[int] | None = None` field (values 1-4)
- [ ] Add `source_domains: list[str] | None = None` field
- [ ] Add `deduplicate: bool = False` field
- [ ] Add `dedupe_strategy: DedupeStrategy = DedupeStrategy.URL_DATE_LOCATION` field
- [ ] Add validators for `quad_class` (1-4 only)
- [ ] Add validators for `goldstein` (-10 to +10)
- [ ] Update endpoints to use new filter fields

**File**: `src/py_gdelt/endpoints/events.py`
- [ ] Apply deduplication when `filter.deduplicate=True`

### Priority 2 - Utility Methods
**File**: `src/py_gdelt/utils/streaming.py`

- [ ] Add `to_json(path: str | Path) -> None` method
- [ ] Add `to_csv(path: str | Path) -> None` method

**File**: `src/py_gdelt/cache.py`

- [ ] Add `clear(before: date | None = None) -> int` method (returns count cleared)
- [ ] Add `size() -> int` method (returns total cached bytes)

**File**: `src/py_gdelt/client.py`

- [ ] Expose cache via `client.cache` property

**File**: `src/py_gdelt/filters.py`

- [ ] Add `raw_query: str | None = None` to `DocFilter`
- [ ] Validate that `raw_query` is mutually exclusive with `query`

**File**: `src/py_gdelt/endpoints/doc.py`

- [ ] Handle `raw_query` parameter in API call construction

### Priority 3 - Polish
**File**: `src/py_gdelt/filters.py`

- [ ] Add `bigram: tuple[str, str] | None = None` to `NGramsFilter`
- [ ] Add `trigram: tuple[str, str, str] | None = None` to `NGramsFilter`
- [ ] Add `source_domains: list[str] | None = None` to `GKGFilter`

**File**: `src/py_gdelt/endpoints/ngrams.py`

- [ ] Handle `bigram`/`trigram` in query construction

**File**: `src/py_gdelt/endpoints/gkg.py`

- [ ] Handle `source_domains` in query construction

---

## Files Summary

| File | Changes Needed |
|------|----------------|
| `src/py_gdelt/filters.py` | EventFilter fields, DocFilter.raw_query, NGramsFilter bigram/trigram, GKGFilter.source_domains |
| `src/py_gdelt/utils/streaming.py` | to_json(), to_csv() methods |
| `src/py_gdelt/cache.py` | clear(), size() methods |
| `src/py_gdelt/client.py` | Expose cache property |
| `src/py_gdelt/endpoints/events.py` | Apply deduplication from filter |
| `src/py_gdelt/endpoints/doc.py` | raw_query support |
| `src/py_gdelt/endpoints/ngrams.py` | bigram/trigram support |
| `src/py_gdelt/endpoints/gkg.py` | source_domains support |

---

## Intentional Deviations from Spec (Keep As-Is)

These differences are acceptable and should NOT be changed:

1. **`EventFilter` vs `EventsFilter`** - Singular is Pythonic for a single filter object
2. **`fips_to_iso3()`** - Richer than spec (has both iso2 and iso3)
3. **Article raw field names** - Has property aliases, works with GDELT API responses
4. **Timeline `timeline` field** - Has `points` property alias for compatibility
5. **Extra fields in models** - TimelinePoint.tone, FailedRequest.status_code - extras are fine

---

*Generated: January 2026*
*Status: Documentation complete, ready for implementation*
