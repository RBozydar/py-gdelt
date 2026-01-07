# Documentation Enhancement Plan

## Summary

Three tasks:
1. Add llms.txt plugin to MkDocs Material docs (both llms.txt and llms-full.txt)
2. Fix missing API documentation coverage (export Event/Mention/Actor + document all exceptions)
3. Ensure documentation is LLM-readable (llms.txt plugin handles this)

---

## Task 1: Add llms.txt Plugin

### Files to Modify
- `pyproject.toml` - Add `mkdocs-llmstxt` to docs dependencies
- `mkdocs.yml` - Configure the llmstxt plugin

### Implementation

**pyproject.toml** - Add to `[project.optional-dependencies]` docs section:
```toml
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.0",
    "mkdocstrings[python]>=0.24",
    "mkdocs-llmstxt",  # NEW
]
```

**mkdocs.yml** - Add plugin configuration:
```yaml
plugins:
  - search
  - llmstxt:
      markdown_description: |
        gdelt-py is a Python client library for GDELT (Global Database of Events, Language, and Tone).
        It provides unified access to all 6 REST APIs, 3 database tables (Events, Mentions, GKG),
        and NGrams dataset with modern async-first design, Pydantic models, and streaming support.
      sections:
        Getting Started:
          - getting-started/installation.md
          - getting-started/quickstart.md
          - getting-started/configuration.md
        User Guide:
          - user-guide/events.md
          - user-guide/gkg.md
          - user-guide/ngrams.md
          - user-guide/rest-apis.md
          - user-guide/lookups.md
          - user-guide/streaming.md
          - user-guide/deduplication.md
          - user-guide/errors.md
        API Reference:
          - api/client.md
          - api/endpoints.md
          - api/filters.md
          - api/models.md
          - api/exceptions.md
        Examples:
          - examples/basic.md
          - examples/advanced.md
      full_output: llms-full.txt
  - mkdocstrings:
      # ... existing config
```

---

## Task 2: Fix Missing API Documentation

### Critical Gaps Found

**models/__init__.py** - Event, Mention, Actor NOT exported:
- `Event`, `Mention`, `Actor` defined in `events.py` but not imported into `__init__.py`
- These are core models that users need

**docs/api/models.md** - Missing models:
- `Event` - Core event model
- `Mention` - Event mention model
- `Actor` - Actor model for events

**docs/api/exceptions.md** - Missing 7 of 12 exceptions:
- `RateLimitError`
- `APIUnavailableError`
- `InvalidQueryError`
- `ParseError`
- `ValidationError`
- `InvalidCodeError`
- `BigQueryError`

### Files to Modify

1. **src/py_gdelt/models/__init__.py** - Add missing exports:
```python
from py_gdelt.models.events import Actor, Event, Mention
# Add to __all__: "Actor", "Event", "Mention"
```

2. **docs/api/models.md** - Add sections for Event, Mention, Actor:
```markdown
## Event Models

::: py_gdelt.models.Event
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.models.Mention
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.models.Actor
    options:
      show_root_heading: true
      heading_level: 3
```

3. **docs/api/exceptions.md** - Add all missing exceptions:
```markdown
::: py_gdelt.exceptions.RateLimitError
::: py_gdelt.exceptions.APIUnavailableError
::: py_gdelt.exceptions.InvalidQueryError
::: py_gdelt.exceptions.ParseError
::: py_gdelt.exceptions.ValidationError
::: py_gdelt.exceptions.InvalidCodeError
::: py_gdelt.exceptions.BigQueryError
```

---

## Task 3: LLM Readability Assessment

### Current State
Documentation is already fairly LLM-friendly:
- Clear structure with Getting Started → User Guide → API Reference
- Code examples with async/sync patterns
- Google-style docstrings rendered via mkdocstrings
- No excessive verbosity

### Recommendation
The llms.txt + llms-full.txt files will serve as the LLM-optimized version:
- `llms.txt` - Condensed overview with links
- `llms-full.txt` - Full documentation in markdown

No separate LLM-specific documentation version needed - the llms.txt plugin handles this.

---

## Execution Order

1. Fix `src/py_gdelt/models/__init__.py` - Export Event, Mention, Actor
2. Update `docs/api/models.md` - Add Event/Mention/Actor sections
3. Update `docs/api/exceptions.md` - Add all exception docs
4. Update `pyproject.toml` - Add mkdocs-llmstxt dependency
5. Update `mkdocs.yml` - Configure llmstxt plugin
6. Run `make ci` to verify no regressions
7. Build docs locally to verify llms.txt generation
