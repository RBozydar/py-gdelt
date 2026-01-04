# feat: Convert GDELT Documentation to Lookup Tables

## Overview

Populate the 4 lookup JSON files with complete GDELT reference data, including descriptions/text for future semantic search capabilities.

**Hard Requirement**: All lookup entries MUST include description/text fields to enable future semantic search.

**Breaking Changes**: Acceptable - nothing released yet. Will document changes for implementation.

---

## Files to Update

### 1. `cameo_codes.json`
- **Source**: `gdelt_docs/cameo_docs/chapter_2_verb_codebook.md` (has descriptions, usage notes, examples)
- **Currently**: ~30 codes
- **Need**: ~300 codes (all 01-20 root codes + subcodes)
- **New Format**:
```json
{
  "01": {
    "name": "MAKE PUBLIC STATEMENT",
    "description": "All public statements not otherwise specified.",
    "quad_class": 1,
    "root": true
  },
  "010": {
    "name": "Make statement, not specified below",
    "description": "All public statements expressed verbally or in action not otherwise specified.",
    "usage_notes": "This residual category is not coded except when distinctions among 011 to 017 cannot be made.",
    "examples": ["U.S. military chief General Colin Powell said on Wednesday NATO would need to remain strong."],
    "parent": "01",
    "quad_class": 1
  }
}
```

### 2. `cameo_goldstein.json`
- **Source**: CAMEO crosswalk files + verb codebook
- **Currently**: ~30 values
- **Need**: ~300 values (matching all CAMEO codes)
- **New Format**:
```json
{
  "01": {
    "value": 0.0,
    "description": "Neutral statements"
  },
  "141": {
    "value": -6.5,
    "description": "Demonstrations and protests"
  }
}
```

### 3. `countries.json`
- **Source**: FIPS 10-4 to ISO 3166 mapping
- **Currently**: ~10 countries
- **Need**: ~250 countries
- **New Format**:
```json
{
  "US": {
    "iso3": "USA",
    "iso2": "US",
    "name": "United States",
    "full_name": "United States of America",
    "region": "North America"
  },
  "IZ": {
    "iso3": "IRQ",
    "iso2": "IQ",
    "name": "Iraq",
    "full_name": "Republic of Iraq",
    "region": "Middle East"
  }
}
```

### 4. `gkg_themes.json`
- **Source**: `gdelt_docs/gkg_cookbook.md` + GDELT Master Themes
- **Currently**: ~10 themes
- **Need**: ~300 themes
- **Format** (keep current, just add more):
```json
{
  "ENV_CLIMATECHANGE": {
    "category": "Environment",
    "description": "Climate change, global warming, greenhouse gases"
  },
  "HEALTH_PANDEMIC": {
    "category": "Health",
    "description": "Pandemic diseases and epidemic outbreaks"
  }
}
```

---

## Approach

**Simple, not scripted**: Parse the markdown manually or with minimal tooling. These are ~300 codes total - straightforward data entry, not a software project.

1. Open source markdown file
2. Extract codes, names, descriptions into JSON
3. Validate structure
4. Commit

**One extraction script is fine** if it speeds things up, but don't over-engineer. The script should be disposable after use.

---

## Breaking Changes & Migration Guide

The following changes affect existing code. Use this guide to update your code.

---

### `CAMEOCodes` class changes

#### 1. `__getitem__` returns Pydantic model instead of string

```python
# BEFORE
cameo = CAMEOCodes()
name = cameo["01"]  # Returns: "MAKE PUBLIC STATEMENT"

# AFTER
cameo = CAMEOCodes()
entry = cameo["01"]  # Returns: CAMEOCodeEntry model
name = entry.name    # "MAKE PUBLIC STATEMENT"
# Also available: entry.description, entry.quad_class, entry.parent, entry.root
```

#### 2. `get_goldstein()` returns Pydantic model instead of float

```python
# BEFORE
cameo = CAMEOCodes()
score = cameo.get_goldstein("141")  # Returns: -6.5

# AFTER
cameo = CAMEOCodes()
entry = cameo.get_goldstein("141")  # Returns: GoldsteinEntry model
score = entry.value                  # -6.5
desc = entry.description             # "Demonstrate or rally, not specified below"
```

#### 3. `get_description()` removed - use `get()` instead

```python
# BEFORE
desc = cameo.get_description("01")

# AFTER
entry = cameo.get("01")
desc = entry.description if entry else None
# Or simply: cameo["01"].description (raises KeyError if not found)
```

#### 4. New methods added

```python
# Check if code exists
if "01" in cameo:
    ...

# Safe get (returns None if not found)
entry = cameo.get("999")  # None

# Search by name/description
codes = cameo.search("protest")  # ["141", "1411", "1412", ...]
```

---

### `Countries` class changes

#### 1. `fips_to_iso()` renamed to `fips_to_iso3()`

```python
# BEFORE
countries = Countries()
iso = countries.fips_to_iso("US")  # "USA"

# AFTER
countries = Countries()
iso3 = countries.fips_to_iso3("US")  # "USA"
iso2 = countries.fips_to_iso2("US")  # "US"
```

#### 2. New methods added

```python
# Check if code exists
if "US" in countries:
    ...

# Get full entry
entry = countries["US"]  # Returns: CountryEntry model
# entry.iso3 = "USA", entry.iso2 = "US", entry.name = "United States"
# entry.full_name = "United States of America", entry.region = "North America"

# Safe get
entry = countries.get("XX")  # None
```

---

### `GKGThemes` class changes

#### 1. `__getitem__` returns Pydantic model instead of dict

```python
# BEFORE
themes = GKGThemes()
data = themes["TAX_FNCACT"]  # Returns: {"category": "...", "description": "..."}

# AFTER
themes = GKGThemes()
entry = themes["TAX_FNCACT"]  # Returns: GKGThemeEntry model
category = entry.category
description = entry.description
```

#### 2. New methods added

```python
# Check if theme exists
if "TAX_FNCACT" in themes:
    ...

# Safe get
entry = themes.get("UNKNOWN")  # None

# Search now searches description field too
themes.search("climate")  # Searches both theme names and descriptions
```

---

### JSON Structure Changes (for direct file readers)

#### `countries.json`
```python
# BEFORE
{"US": {"iso": "USA", "name": "United States"}}

# AFTER
{"US": {"iso3": "USA", "iso2": "US", "name": "United States",
        "full_name": "United States of America", "region": "North America"}}
```

#### `cameo_codes.json`
```python
# BEFORE
{"01": "MAKE PUBLIC STATEMENT"}

# AFTER
{"01": {"name": "MAKE PUBLIC STATEMENT", "description": "...",
        "quad_class": 1, "root": true}}
```

#### `cameo_goldstein.json`
```python
# BEFORE
{"01": 0.0}

# AFTER
{"01": {"value": 0.0, "description": "MAKE PUBLIC STATEMENT"}}
```

---

## Pydantic Models

Add Pydantic models for type safety and validation:

```python
from pydantic import BaseModel

class CAMEOCodeEntry(BaseModel):
    name: str
    description: str
    usage_notes: str | None = None
    examples: list[str] = []
    parent: str | None = None
    quad_class: int
    root: bool = False

class GoldsteinEntry(BaseModel):
    value: float
    description: str

class CountryEntry(BaseModel):
    iso3: str
    iso2: str
    name: str
    full_name: str | None = None
    region: str

class GKGThemeEntry(BaseModel):
    category: str
    description: str
```

---

## Python Class Updates Needed

### CAMEOCodes (`src/py_gdelt/lookups/cameo.py`)

Store parsed Pydantic models, add accessors:

```python
def __init__(self) -> None:
    # Parse JSON into Pydantic models on load
    self._codes: dict[str, CAMEOCodeEntry] = {
        code: CAMEOCodeEntry(**data)
        for code, data in self._load_json("cameo_codes.json").items()
    }
    self._goldstein: dict[str, GoldsteinEntry] = {
        code: GoldsteinEntry(**data)
        for code, data in self._load_json("cameo_goldstein.json").items()
    }

def __contains__(self, code: str) -> bool:
    """Check if code exists."""
    return code in self._codes

def __getitem__(self, code: str) -> CAMEOCodeEntry:
    """Get full entry for CAMEO code."""
    return self._codes[code]

def get(self, code: str) -> CAMEOCodeEntry | None:
    """Get entry for CAMEO code, or None if not found."""
    return self._codes.get(code)

def get_goldstein(self, code: str) -> GoldsteinEntry | None:
    """Get Goldstein entry for CAMEO code."""
    return self._goldstein.get(code)

def search(self, query: str) -> list[str]:
    """Search codes by name/description (substring match)."""
    query_lower = query.lower()
    return [
        code for code, entry in self._codes.items()
        if query_lower in entry.name.lower()
        or query_lower in entry.description.lower()
    ]
```

### Countries (`src/py_gdelt/lookups/countries.py`)

```python
def __init__(self) -> None:
    self._countries: dict[str, CountryEntry] = {
        code: CountryEntry(**data)
        for code, data in self._load_json("countries.json").items()
    }

def __contains__(self, code: str) -> bool:
    """Check if country code exists."""
    return code.upper() in self._countries

def __getitem__(self, code: str) -> CountryEntry:
    """Get full entry for country code."""
    return self._countries[code.upper()]

def get(self, code: str) -> CountryEntry | None:
    """Get entry for country code, or None if not found."""
    return self._countries.get(code.upper())

def fips_to_iso3(self, fips: str) -> str | None:
    """Convert FIPS code to ISO 3166-1 alpha-3."""
    entry = self._countries.get(fips.upper())
    return entry.iso3 if entry else None

def fips_to_iso2(self, fips: str) -> str | None:
    """Convert FIPS code to ISO 3166-1 alpha-2."""
    entry = self._countries.get(fips.upper())
    return entry.iso2 if entry else None
```

### GKGThemes (`src/py_gdelt/lookups/themes.py`)

```python
def __init__(self) -> None:
    self._themes: dict[str, GKGThemeEntry] = {
        code: GKGThemeEntry(**data)
        for code, data in self._load_json("gkg_themes.json").items()
    }

def __contains__(self, theme: str) -> bool:
    """Check if theme exists."""
    return theme in self._themes

def __getitem__(self, theme: str) -> GKGThemeEntry:
    """Get full entry for theme."""
    return self._themes[theme]

def get(self, theme: str) -> GKGThemeEntry | None:
    """Get entry for theme, or None if not found."""
    return self._themes.get(theme)

def search(self, query: str) -> list[str]:
    """Search themes by description (substring match)."""
    query_lower = query.lower()
    return [
        theme for theme, entry in self._themes.items()
        if query_lower in entry.description.lower()
    ]
```

---

## Acceptance Criteria

- [ ] All 20 CAMEO root codes (01-20) present with descriptions
- [ ] All CAMEO subcodes (3-4 digit) present with descriptions
- [ ] All Goldstein values present with descriptions
- [ ] All ~250 countries present with full names and regions
- [ ] All ~300 GKG themes present with descriptions
- [ ] Pydantic models defined for all entry types
- [ ] Python accessor classes updated for new structure
- [ ] Existing tests updated and passing
- [ ] `search()` method works for substring matching
- [ ] `__contains__` method added for Pythonic `in` checks

---

## Implementation Checklist

### Data Population
- [ ] Populate `cameo_codes.json` from verb codebook (chapter 2)
- [ ] Populate `cameo_goldstein.json` with values and descriptions
- [ ] Populate `countries.json` with all FIPS codes
- [ ] Populate `gkg_themes.json` with all themes

### Code Updates
- [ ] Add Pydantic models (`CAMEOCodeEntry`, `GoldsteinEntry`, `CountryEntry`, `GKGThemeEntry`)
- [ ] Update `CAMEOCodes` class to parse JSON into Pydantic models
- [ ] Update `Countries` class with `fips_to_iso3()`, `fips_to_iso2()` methods
- [ ] Update `GKGThemes` class to parse JSON into Pydantic models
- [ ] Add `search()` method to `CAMEOCodes` and `GKGThemes`
- [ ] Add `__contains__` and `get()` methods to all lookup classes
- [ ] Update tests for new structure

### Validation
- [ ] Every CAMEO code has a description
- [ ] Every Goldstein entry has a value and description
- [ ] Every country has iso3, name, region
- [ ] Every theme has category and description
- [ ] All tests pass

---

## Code Quality Guidelines

1. **Use Pydantic models** for JSON structures - provides validation, type safety, and IDE support
2. **Parse JSON to models on load** - validate data once at startup, access typed attributes thereafter
3. **Keep search simple** - substring matching is sufficient for ~300 entries
4. **No backward compatibility** - clean API without legacy aliases

---

## References

### Documentation Sources
- `gdelt_docs/cameo_docs/chapter_2_verb_codebook.md` - CAMEO codes with full descriptions
- `gdelt_docs/cameo_docs/chapter_6_cameo_event_codes.md` - Condensed code list
- `gdelt_docs/gkg_cookbook.md` - GKG themes
- FIPS 10-4 to ISO mapping tables

### External (use HTTPS)
- https://gdeltproject.org/data/lookups/ - CAMEO crosswalk files
- https://data.gdeltproject.org/documentation/ - Codebooks

---

*Plan simplified: January 2026*
*Based on reviewer feedback - kept semantic search requirement, Pydantic models, no backward compat*
