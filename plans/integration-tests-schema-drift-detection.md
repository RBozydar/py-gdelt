# Integration Tests: Schema Drift Detection & Mapping Validation

**Type:** Enhancement
**Priority:** High
**Created:** 2025-01-07
**Revised:** 2025-01-07 (simplified based on review feedback)

## Overview

Add integration tests to detect schema drift (GDELT adding fields without notice) and validate lookup table coverage (CAMEO codes, countries, themes).

### Problem

GDELT adds fields without notice. Our parsers should warn when this happens so we can update models.

### Goals

1. Detect when GDELT adds/removes fields
2. Verify lookup tables cover codes in live data
3. Warn but don't fail (forward compatibility)
4. Run weekly in CI

---

## Implementation

### Phase 1: Write the Tests

**File: `tests/integration/test_schema_drift.py`**

```python
"""Schema drift detection for GDELT APIs and file sources."""
from __future__ import annotations

import warnings
from typing import Any

import pytest

from py_gdelt import GDELTClient
from py_gdelt.lookups import CAMEOCodes, Countries, GKGThemes
from py_gdelt.models.articles import Article
from py_gdelt.models.events import Event, Mention
from py_gdelt.models.gkg import GKGRecord
from py_gdelt.parsers.events import EventsParser


class SchemaDriftWarning(UserWarning):
    """Warning raised when schema drift is detected."""

    pass


class UnknownCodeWarning(UserWarning):
    """Warning raised when unknown lookup codes are found."""

    pass


# --- Schema Drift Detection ---


def get_drift(raw_data: dict[str, Any], model: type) -> set[str]:
    """Return fields in raw data but not in model."""
    return set(raw_data.keys()) - set(model.model_fields.keys())


@pytest.mark.integration
@pytest.mark.timeout(60)
async def test_doc_api_schema_drift(gdelt_client: GDELTClient) -> None:
    """Detect schema drift in DOC API responses."""
    results = await gdelt_client.doc.search(query="test", timespan="24h", max_records=10)
    if not results:
        pytest.skip("No data from DOC API")

    # Get raw dict representation
    raw = results[0].model_dump()
    new_fields = get_drift(raw, Article)

    if new_fields:
        warnings.warn(
            f"DOC API schema drift: new fields {sorted(new_fields)}",
            SchemaDriftWarning,
            stacklevel=2,
        )


@pytest.mark.integration
@pytest.mark.timeout(120)
async def test_events_file_schema_drift(gdelt_client: GDELTClient) -> None:
    """Detect schema drift in Events file downloads."""
    async for event in gdelt_client.events.stream(limit=100):
        raw = event.model_dump()
        new_fields = get_drift(raw, Event)

        if new_fields:
            warnings.warn(
                f"Events schema drift: new fields {sorted(new_fields)}",
                SchemaDriftWarning,
                stacklevel=2,
            )
        break  # Only need to check first batch


@pytest.mark.integration
@pytest.mark.timeout(120)
async def test_gkg_file_schema_drift(gdelt_client: GDELTClient) -> None:
    """Detect schema drift in GKG file downloads."""
    async for record in gdelt_client.gkg.stream(limit=100):
        raw = record.model_dump()
        new_fields = get_drift(raw, GKGRecord)

        if new_fields:
            warnings.warn(
                f"GKG schema drift: new fields {sorted(new_fields)}",
                SchemaDriftWarning,
                stacklevel=2,
            )
        break


# --- Lookup Table Validation ---


@pytest.mark.integration
@pytest.mark.timeout(120)
async def test_cameo_codes_coverage(gdelt_client: GDELTClient) -> None:
    """Check if CAMEO codes in live data are in our lookup."""
    cameo = CAMEOCodes()
    unknown_codes: set[str] = set()

    async for event in gdelt_client.events.stream(limit=500):
        if event.event_code and event.event_code not in cameo:
            unknown_codes.add(event.event_code)

    if unknown_codes:
        warnings.warn(
            f"Unknown CAMEO codes in live data: {sorted(unknown_codes)}. "
            "Consider updating cameo_codes.json",
            UnknownCodeWarning,
            stacklevel=2,
        )


@pytest.mark.integration
@pytest.mark.timeout(120)
async def test_country_codes_coverage(gdelt_client: GDELTClient) -> None:
    """Check if country codes in live data are in our lookup."""
    countries = Countries()
    unknown_codes: set[str] = set()

    async for event in gdelt_client.events.stream(limit=500):
        for code in [event.actor1.country_code, event.actor2.country_code] if event.actor1 or event.actor2 else []:
            if code and code not in countries:
                unknown_codes.add(code)

    if unknown_codes:
        warnings.warn(
            f"Unknown country codes in live data: {sorted(unknown_codes)}. "
            "Consider updating countries.json",
            UnknownCodeWarning,
            stacklevel=2,
        )


@pytest.mark.integration
@pytest.mark.timeout(120)
async def test_gkg_themes_coverage(gdelt_client: GDELTClient) -> None:
    """Check if GKG themes in live data are in our lookup."""
    themes = GKGThemes()
    unknown_themes: set[str] = set()

    async for record in gdelt_client.gkg.stream(limit=200):
        for theme in record.themes or []:
            if theme and theme not in themes:
                unknown_themes.add(theme)

    # Only warn if significant number of unknown themes
    if len(unknown_themes) > 10:
        warnings.warn(
            f"Many unknown GKG themes ({len(unknown_themes)}): {sorted(list(unknown_themes)[:10])}... "
            "Consider updating gkg_themes.json",
            UnknownCodeWarning,
            stacklevel=2,
        )
```

**Tasks:**

- [ ] Create `tests/integration/test_schema_drift.py`
- [ ] Add `schema_drift` marker to `pyproject.toml`
- [ ] Run tests locally to verify they work

### Phase 2: CI Integration

**File: `.github/workflows/schema-drift.yml`**

```yaml
name: Schema Drift Detection

on:
  schedule:
    - cron: '0 8 * * 1'  # Weekly on Monday at 8 AM UTC
  workflow_dispatch:

jobs:
  schema-drift:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install uv
          uv sync --all-extras

      - name: Run schema drift tests
        id: tests
        run: |
          uv run pytest tests/integration/test_schema_drift.py -v 2>&1 | tee output.txt
        continue-on-error: true

      - name: Check for drift warnings
        id: check
        run: |
          if grep -q "SchemaDriftWarning\|UnknownCodeWarning" output.txt; then
            echo "drift_detected=true" >> $GITHUB_OUTPUT
          fi

      - name: Find existing drift issue
        if: steps.check.outputs.drift_detected == 'true'
        id: find_issue
        uses: actions/github-script@v7
        with:
          script: |
            const issues = await github.rest.issues.listForRepo({
              owner: context.repo.owner,
              repo: context.repo.repo,
              labels: 'schema-drift',
              state: 'open'
            });
            if (issues.data.length > 0) {
              core.setOutput('issue_number', issues.data[0].number);
            }

      - name: Update or create issue
        if: steps.check.outputs.drift_detected == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const output = fs.readFileSync('output.txt', 'utf8');
            const issueNumber = '${{ steps.find_issue.outputs.issue_number }}';
            const body = `## Schema Drift Detected - ${new Date().toISOString().split('T')[0]}

            \`\`\`
            ${output.substring(0, 60000)}
            \`\`\`

            ### Action Required
            1. Review the warnings above
            2. Update models/lookups if needed
            3. Close this issue when resolved

            ---
            *Auto-generated by schema drift workflow*`;

            if (issueNumber) {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: parseInt(issueNumber),
                body: body
              });
            } else {
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: '[Schema Drift] Changes detected',
                body: body,
                labels: ['schema-drift', 'needs-review']
              });
            }
```

**Tasks:**

- [ ] Create `.github/workflows/schema-drift.yml`
- [ ] Add `schema-drift` and `needs-review` labels to repository
- [ ] Test workflow with `workflow_dispatch`

---

## Acceptance Criteria

- [ ] Schema drift tests run for DOC API, Events, and GKG
- [ ] Lookup validation covers CAMEO codes, countries, and GKG themes
- [ ] Tests emit warnings (not failures) when drift is detected
- [ ] Weekly CI job runs and creates/updates GitHub issue on drift
- [ ] All tests pass `make ci`

---

## What We're NOT Doing (YAGNI)

Based on reviewer feedback, these were removed from scope:

1. **Baseline JSON files** - Pydantic models are the baseline
2. **Historical drift tracking** - Git history serves this purpose
3. **CLI commands for baseline updates** - Not needed
4. **Separate test classes** - Simple functions are sufficient
5. **DriftReport abstraction** - Inline set operations work fine
6. **Type drift detection** - Added as future enhancement if needed

---

## Future Enhancements (Not in Scope)

1. **Type drift detection** - Use dynamic strict models to catch type changes
2. **Statistical validation** - Pandera for distribution drift
3. **Nested field detection** - Deep comparison for complex objects
4. **Parser column validation** - Compare against `EventsParser.V2_COLUMNS`

---

## References

- `src/py_gdelt/models/events.py` - Event model
- `src/py_gdelt/lookups/cameo.py` - CAMEO codes lookup
- `tests/integration/conftest.py` - Existing `gdelt_client` fixture
