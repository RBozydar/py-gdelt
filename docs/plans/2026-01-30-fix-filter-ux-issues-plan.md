---
title: "fix: Filter UX Issues - Silent Ignoring, Case Sensitivity, Documentation"
type: fix
date: 2026-01-30
task_list_id: f7550ab4-a8f2-4098-b038-9dfc4d299817
---

# fix: Filter UX Issues - Silent Ignoring, Case Sensitivity, Documentation

## Overview

Multiple filter UX issues where user-specified filter fields are silently ignored or behave unexpectedly. Users expect filters to work consistently regardless of data source, but several fields only work with BigQuery (fallback) and are ignored when using file downloads (primary source).

## Problem Statement

### Issue 1: Silent Filter Ignoring (HIGH)

**EventFilter** fields only work with BigQuery, silently ignored with file source:
- `actor1_country`, `actor2_country`, `action_country`
- `event_code`, `event_root_code`, `event_base_code`
- `min_tone`, `max_tone`

**GKGFilter** fields only work with BigQuery, silently ignored with file source:
- `persons`, `organizations`, `themes`
- `theme_prefix`

**Impact**: Users set filters expecting filtered results, but get ALL records from file downloads.

### Issue 2: Case Sensitivity (HIGH)

BigQuery queries use `REGEXP_CONTAINS` which is case-sensitive:
- `persons`: "barack obama" won't match "Barack Obama"
- `organizations`: "united nations" won't match "United Nations"
- `theme_prefix`: "env_climate" won't match "ENV_CLIMATE"

**Impact**: Users get empty results despite data existing.

### Issue 3: Documentation Gaps (MEDIUM)

- Filter docstrings don't document which fields work with which sources
- No warning about case sensitivity in free-text fields
- No documentation of OR vs AND logic for multi-value filters
- Graph dataset `languages` filter is client-side but not documented

## Proposed Solution

### Strategy: Client-Side Filtering + Case-Insensitive Matching

Following the established pattern from `NGramsEndpoint._matches_filter()` (`src/py_gdelt/endpoints/ngrams.py:231-258`):

1. **Add `_matches_filter()` methods** to EventsEndpoint and GKGEndpoint
2. **Apply filters client-side** after file download, before yielding records
3. **Use case-insensitive matching** for free-text fields (persons, organizations, theme_prefix)
4. **Use `LOWER()` consistently** in BigQuery for case-insensitive matching
5. **Update docstrings** to document filter behavior and OR logic

This ensures consistent behavior regardless of source while maintaining BigQuery server-side filtering for efficiency when available.

## Technical Approach

### Phase 1: EventFilter Client-Side Filtering

**File: `src/py_gdelt/endpoints/events.py`**

Add `_matches_filter()` method. **Critical corrections from review:**
- Model is `Event` (not `EventRecord`)
- Access actor country via `record.actor1.country_code if record.actor1 else None`
- Access action country via `record.action_geo.country_code if record.action_geo else None`

```python
def _matches_filter(self, record: Event, filter_obj: EventFilter) -> bool:
    """Check if record matches filter criteria (client-side).

    Applied when using file source. BigQuery applies these server-side.

    Args:
        record: Event to check
        filter_obj: Filter criteria

    Returns:
        True if record matches all filter criteria
    """
    # Actor country filters (exact match on FIPS codes - already normalized)
    actor1_country = record.actor1.country_code if record.actor1 else None
    if filter_obj.actor1_country and actor1_country != filter_obj.actor1_country:
        return False

    actor2_country = record.actor2.country_code if record.actor2 else None
    if filter_obj.actor2_country and actor2_country != filter_obj.actor2_country:
        return False

    action_country = record.action_geo.country_code if record.action_geo else None
    if filter_obj.action_country and action_country != filter_obj.action_country:
        return False

    # Event code filters (exact match)
    if filter_obj.event_code and record.event_code != filter_obj.event_code:
        return False
    if filter_obj.event_root_code and record.event_root_code != filter_obj.event_root_code:
        return False
    if filter_obj.event_base_code and record.event_base_code != filter_obj.event_base_code:
        return False

    # Tone filters (numeric range)
    if filter_obj.min_tone is not None and record.avg_tone < filter_obj.min_tone:
        return False
    if filter_obj.max_tone is not None and record.avg_tone > filter_obj.max_tone:
        return False

    return True
```

**Update `stream()` to apply filter:**

```diff
--- a/src/py_gdelt/endpoints/events.py
+++ b/src/py_gdelt/endpoints/events.py
@@ -XXX,6 +XXX,10 @@ async def stream(...):
         async for raw_event in self._fetcher.fetch_events(filter_obj, use_bigquery=use_bigquery):
             try:
                 record = Event.from_raw(raw_event)
+
+                # Apply client-side filtering (file source doesn't filter)
+                if not self._matches_filter(record, filter_obj):
+                    continue
+
                 yield record
```

**Update `query()` to apply filter:**

The `query()` method (lines 140-219) fetches raw events, applies deduplication, then converts to Event models. Filtering must be added after conversion:

```diff
--- a/src/py_gdelt/endpoints/events.py
+++ b/src/py_gdelt/endpoints/events.py
@@ -210,7 +210,11 @@ async def query(...):
         # Convert _RawEvent to Event models after deduplication
         events: list[Event] = []
         for raw_event in raw_events_list:
             event = Event.from_raw(raw_event)
+
+            # Apply client-side filtering (file source doesn't filter)
+            if not self._matches_filter(event, filter_obj):
+                continue
+
             events.append(event)
```

### Phase 2: GKGFilter Client-Side Filtering

**File: `src/py_gdelt/endpoints/gkg.py`**

Add `_matches_filter()` with case-insensitive text matching. **Critical corrections from review:**
- `record.persons` is `list[EntityMention]`, access via `p.name`
- `record.organizations` is `list[EntityMention]`, access via `o.name`
- `record.themes` is `list[EntityMention]`, access via `t.name`
- Add missing `themes` exact match filter (was only `theme_prefix`)
- Pre-compute lowercased values outside loops for efficiency

```python
def _matches_filter(self, record: GKGRecord, filter_obj: GKGFilter) -> bool:
    """Check if record matches filter criteria (client-side).

    Applied when using file source. BigQuery applies these server-side.
    Text fields use case-insensitive matching for better UX.

    Note:
        Multi-value filters (persons, organizations, themes) use OR logic -
        a record matches if ANY filter value is found in the record.

    Args:
        record: GKGRecord to check
        filter_obj: Filter criteria

    Returns:
        True if record matches all filter criteria
    """
    # Themes exact match filter (OR logic: any theme matches)
    if filter_obj.themes:
        record_themes = {t.name.upper() for t in record.themes}
        filter_themes = {t.upper() for t in filter_obj.themes}
        if not record_themes & filter_themes:  # No intersection
            return False

    # Theme prefix filter (case-insensitive prefix match)
    if filter_obj.theme_prefix:
        prefix_lower = filter_obj.theme_prefix.lower()
        if not any(t.name.lower().startswith(prefix_lower) for t in record.themes):
            return False

    # Persons filter (case-insensitive substring match, OR logic)
    if filter_obj.persons:
        filter_persons_lower = [fp.lower() for fp in filter_obj.persons]
        record_persons_lower = [p.name.lower() for p in record.persons]
        if not any(
            fp in rp
            for rp in record_persons_lower
            for fp in filter_persons_lower
        ):
            return False

    # Organizations filter (case-insensitive substring match, OR logic)
    if filter_obj.organizations:
        filter_orgs_lower = [fo.lower() for fo in filter_obj.organizations]
        record_orgs_lower = [o.name.lower() for o in record.organizations]
        if not any(
            fo in ro
            for ro in record_orgs_lower
            for fo in filter_orgs_lower
        ):
            return False

    # Country filter (exact match on FIPS in any location)
    if filter_obj.country:
        if not any(loc.country_code == filter_obj.country for loc in record.locations):
            return False

    # Tone filters (numeric range)
    tone_value = record.tone.tone if record.tone else None
    if filter_obj.min_tone is not None and (tone_value is None or tone_value < filter_obj.min_tone):
        return False
    if filter_obj.max_tone is not None and (tone_value is None or tone_value > filter_obj.max_tone):
        return False

    return True
```

**Update `stream()` to apply filter** (same pattern as Events).

### Phase 3: BigQuery Case-Insensitive Matching

**File: `src/py_gdelt/sources/bigquery.py`**

Use `LOWER()` consistently for all text fields (RE2 doesn't support `(?i)` inline flag reliably):

```diff
--- a/src/py_gdelt/sources/bigquery.py
+++ b/src/py_gdelt/sources/bigquery.py
@@ -374,7 +374,8 @@ def _build_where_clause_for_gkg(...):
     if filter_obj.theme_prefix is not None:
-        conditions.append("REGEXP_CONTAINS(V2Themes, @theme_prefix_pattern)")
+        conditions.append("REGEXP_CONTAINS(LOWER(V2Themes), @theme_prefix_pattern)")
         parameters.append(
             bigquery.ScalarQueryParameter(
                 "theme_prefix_pattern",
                 "STRING",
-                f"(^|;){re.escape(filter_obj.theme_prefix)}",
+                f"(^|;){re.escape(filter_obj.theme_prefix.lower())}",
             ),
         )

@@ -385,14 +386,14 @@ def _build_where_clause_for_gkg(...):
     # Optional: Entity filters (persons, organizations)
     if filter_obj.persons is not None and len(filter_obj.persons) > 0:
-        person_pattern = "|".join(re.escape(p) for p in filter_obj.persons)
-        conditions.append("REGEXP_CONTAINS(V2Persons, @person_pattern)")
+        person_pattern = "|".join(re.escape(p.lower()) for p in filter_obj.persons)
+        conditions.append("REGEXP_CONTAINS(LOWER(V2Persons), @person_pattern)")
         parameters.append(bigquery.ScalarQueryParameter("person_pattern", "STRING", person_pattern))

     if filter_obj.organizations is not None and len(filter_obj.organizations) > 0:
-        org_pattern = "|".join(re.escape(o) for o in filter_obj.organizations)
-        conditions.append("REGEXP_CONTAINS(V2Organizations, @org_pattern)")
+        org_pattern = "|".join(re.escape(o.lower()) for o in filter_obj.organizations)
+        conditions.append("REGEXP_CONTAINS(LOWER(V2Organizations), @org_pattern)")
         parameters.append(bigquery.ScalarQueryParameter("org_pattern", "STRING", org_pattern))
```

### Phase 4: Documentation Updates

**File: `src/py_gdelt/filters.py`**

Update filter docstrings to document behavior and OR logic:

```python
class EventFilter(BaseModel):
    """Filter for Events/Mentions queries.

    All filter fields work with both file downloads and BigQuery:
    - File source: Filters applied client-side after download
    - BigQuery: Filters applied server-side for efficiency

    Country codes (actor1_country, actor2_country, action_country) accept
    both FIPS and ISO3 formats and are normalized to FIPS automatically.

    Event codes are validated against CAMEO codebook.

    Args:
        date_range: Required date range for query
        actor1_country: Filter by Actor1 country (FIPS or ISO3)
        actor2_country: Filter by Actor2 country (FIPS or ISO3)
        event_code: Filter by CAMEO event code
        event_root_code: Filter by CAMEO root event code
        event_base_code: Filter by CAMEO base event code
        min_tone: Minimum average tone threshold
        max_tone: Maximum average tone threshold
        action_country: Filter by action location country (FIPS or ISO3)
        include_translated: Include machine-translated articles (default: True)
    """
```

```python
class GKGFilter(BaseModel):
    """Filter for GKG queries.

    All filter fields work with both file downloads and BigQuery:
    - File source: Filters applied client-side after download
    - BigQuery: Filters applied server-side for efficiency

    Text fields (persons, organizations, theme_prefix) use **case-insensitive
    matching** - "Obama" matches "OBAMA", "obama", "Barack Obama", etc.

    Multi-value filters use **OR logic** - a record matches if ANY value
    in the list is found. For example, `persons=["Obama", "Biden"]` matches
    records containing either "Obama" OR "Biden" (or both).

    Args:
        date_range: Required date range for query
        themes: List of exact GKG theme codes to match (OR logic, case-insensitive)
        theme_prefix: Match themes starting with prefix (case-insensitive)
        persons: Match records containing these person names (OR logic, case-insensitive substring)
        organizations: Match records containing these org names (OR logic, case-insensitive substring)
        country: Filter by country code (FIPS or ISO3, normalized to FIPS)
        min_tone: Minimum tone threshold
        max_tone: Maximum tone threshold
        include_translated: Include machine-translated articles (default: True)
    """
```

Update graph filter docstrings (GQGFilter, GEGFilter, etc.) to document client-side filtering and OR logic for languages.

## Acceptance Criteria

### Functional Requirements

- [ ] EventFilter fields work with file source (actor countries, event codes, tone)
- [ ] GKGFilter fields work with file source (persons, organizations, themes, theme_prefix, country, tone)
- [ ] Text matching is case-insensitive (both file and BigQuery)
- [ ] Multi-value filters use OR logic (documented)
- [ ] All filter docstrings document field behavior

### Non-Functional Requirements

- [ ] No performance regression for BigQuery queries
- [ ] Client-side filtering uses early-return pattern for efficiency
- [ ] Existing tests pass
- [ ] New tests cover client-side filtering

### Quality Gates

- [ ] `make ci` passes (lint + typecheck + tests)
- [ ] Test coverage maintained or improved
- [ ] Docstrings pass pydoclint validation

## Test Plan

### Unit Tests

**File: `tests/unit/endpoints/test_events_filtering.py`**

```python
class TestEventsClientSideFiltering:
    """Test client-side filtering for EventsEndpoint."""

    def test_matches_filter_actor1_country(self):
        """Filter by actor1_country works client-side."""

    def test_matches_filter_actor1_country_none_actor(self):
        """Filter handles records with actor1=None."""

    def test_matches_filter_event_code(self):
        """Filter by event_code works client-side."""

    def test_matches_filter_tone_range(self):
        """Filter by min_tone/max_tone works client-side."""

    def test_matches_filter_all_fields(self):
        """All filter fields applied together."""

    def test_matches_filter_none_values(self):
        """None filter values skip that criterion."""
```

**File: `tests/unit/endpoints/test_gkg_filtering.py`**

```python
class TestGKGClientSideFiltering:
    """Test client-side filtering for GKGEndpoint."""

    def test_matches_filter_themes_exact(self):
        """Themes filter matches exact theme codes (case-insensitive)."""
        # themes=["ENV_CLIMATE"] matches record with theme "env_climate"

    def test_matches_filter_themes_or_logic(self):
        """Themes filter uses OR logic."""
        # themes=["ENV_CLIMATE", "POLITICS"] matches if either present

    def test_matches_filter_persons_case_insensitive(self):
        """Persons filter matches case-insensitively."""
        # persons=["obama"] matches record with "Barack Obama"

    def test_matches_filter_persons_substring(self):
        """Persons filter does substring matching."""
        # persons=["Obama"] matches "Barack Obama" and "Michelle Obama"

    def test_matches_filter_organizations_case_insensitive(self):
        """Organizations filter matches case-insensitively."""

    def test_matches_filter_theme_prefix_case_insensitive(self):
        """Theme prefix filter matches case-insensitively."""
        # theme_prefix="env_" matches "ENV_CLIMATE"

    def test_matches_filter_empty_record_lists(self):
        """Filter handles empty persons/orgs/themes lists."""

    def test_matches_filter_none_values(self):
        """None filter values skip that criterion."""
```

### Integration Tests

**File: `tests/integration/test_filter_consistency.py`**

```python
class TestFilterConsistencyAcrossSources:
    """Verify filters produce same results from file and BigQuery sources."""

    @pytest.mark.integration
    async def test_event_filter_file_vs_bigquery(self):
        """EventFilter produces consistent results from both sources."""

    @pytest.mark.integration
    async def test_gkg_filter_file_vs_bigquery(self):
        """GKGFilter produces consistent results from both sources."""

    @pytest.mark.integration
    async def test_gkg_persons_case_insensitive_both_sources(self):
        """Case-insensitive person matching works on both sources."""
```

## Dependencies & Risks

### Dependencies

- Access to `Event` and `GKGRecord` model fields for filtering
- `EntityMention.name` attribute for accessing entity names

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Client-side filtering slower for large datasets | Medium | Low | Document that BigQuery is more efficient for filtered queries |
| Breaking change if users relied on case-sensitive matching | Low | Low | Document as bugfix (case-sensitive was unintended) |

## References

### Internal References

- Client-side filtering pattern: `src/py_gdelt/endpoints/ngrams.py:231-258`
- Event model: `src/py_gdelt/models/events.py:56` (class `Event`)
- GKGRecord model: `src/py_gdelt/models/gkg.py:62`
- EntityMention model: `src/py_gdelt/models/common.py:78` (has `.name` attribute)
- Country normalization pattern: `src/py_gdelt/lookups/countries.py:197-234`
- BigQuery parameterized queries: `src/py_gdelt/sources/bigquery.py:247-330`

### Review Feedback Incorporated

From code reviews (2026-01-30):
- **Code Simplicity**: Removed Phase 6 VGKG cleanup (redundant `.lower()` is harmless documentation)
- **Architecture**: Added filtering to both `stream()` and `query()` methods
- **Kieran Python**: Fixed model names (`Event` not `EventRecord`), field access patterns
- **Gemini**: Added missing `themes` exact match filter, standardized on `LOWER()` for BigQuery

## Tasks

Run `/workflows:work` with this plan to execute.

| # | Task | Description |
|---|------|-------------|
| 1 | Add client-side filtering to EventsEndpoint | Add `_matches_filter()`, update `stream()` and `query()` |
| 2 | Add client-side filtering to GKGEndpoint | Add `_matches_filter()` with themes, persons, orgs support |
| 3 | Update BigQuery for case-insensitive matching | Use `LOWER()` consistently for all text fields |
| 4 | Update filter docstrings | Document behavior, OR logic, case-insensitivity |
| 5 | Add unit tests | Tests for Events and GKG client-side filtering |
| 6 | Add integration tests | Tests for file vs BigQuery consistency |
| 7 | Run make ci | Verify all checks pass |
