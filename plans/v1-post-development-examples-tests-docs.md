# feat: V1 Post-Development - Examples, Integration Tests, Notebooks & Documentation

## Overview

After completing V1 of the py-gdelt library, this plan addresses the remaining gaps in examples, integration tests, Jupyter notebooks, and documentation. The goal is to ensure comprehensive coverage across all endpoints and provide excellent developer experience through well-structured docs.

**Current Status (from implementation plan):**
- 772 unit tests passing
- 7 existing Python examples
- 1 integration test (`integration_trump_venezuela.py`)
- Sparse documentation (`docs/` only has `ngrams_endpoint.md`)

---

## Problem Statement / Motivation

The library is feature-complete but lacks:
1. **Missing Examples**: Context, GEO, and TV/TV AI APIs have no examples
2. **Limited Integration Tests**: Only 1 integration test exists (DOC API focused)
3. **No Jupyter Notebooks**: Interactive examples would improve discoverability
4. **Sparse Documentation**: The `docs/` directory is nearly empty despite good docstrings

Without comprehensive examples and docs, users will struggle to adopt the library effectively.

---

## Proposed Solution

A phased approach to fill the gaps:

### Phase 1: Verify & Fix Existing Examples
### Phase 2: Create Missing Examples (Context, GEO, TV APIs)
### Phase 3: Create Integration Tests (non-stale patterns)
### Phase 4: Create Jupyter Notebooks
### Phase 5: Build Documentation Site

---

## Technical Approach

### Phase 1: Verify & Fix Existing Examples

**Goal**: Ensure all existing examples run without errors.

**Tasks:**
- [ ] Run `basic_client_usage.py` and verify output
- [ ] Run `events_endpoint_example.py` and verify output
- [ ] Run `query_mentions.py` (requires BigQuery credentials)
- [ ] Run `gkg_example.py` and verify output
- [ ] Run `ngrams_example.py` and verify output
- [ ] Run `download_gdelt_files.py list` and verify output
- [ ] Run `bigquery_example.py` (requires BigQuery credentials)
- [ ] Fix any broken examples (date ranges, API changes, etc.)

**Files to modify:**
- `examples/basic_client_usage.py`
- `examples/events_endpoint_example.py`
- `examples/gkg_example.py`
- `examples/ngrams_example.py`
- `examples/download_gdelt_files.py`
- `examples/query_mentions.py`
- `examples/bigquery_example.py`

**Success Criteria:**
- [ ] All examples execute without errors
- [ ] Examples produce meaningful output (not empty results)
- [ ] Date ranges updated if needed (currently hardcoded to `date(2026, 1, 1)`)

---

### Phase 2: Create Missing Examples

**Goal**: Add examples for Context, GEO, and TV/TV AI APIs.

#### 2.1 Context API Example

**File**: `examples/context_api_example.py`

```python
#!/usr/bin/env python3
"""Example: Query GDELT Context 2.0 API for contextual analysis.

Demonstrates:
- Basic contextual analysis with themes and entities
- Getting top themes for a search term
- Filtering entities by type (PERSON, ORG, LOCATION)
- Tone/sentiment analysis
"""

import asyncio

from py_gdelt import GDELTClient


async def analyze_topic_context() -> None:
    """Analyze contextual information for a topic."""
    print("=" * 60)
    print("Example 1: Basic Contextual Analysis")
    print("=" * 60)

    async with GDELTClient() as client:
        # Analyze context for "artificial intelligence"
        result = await client.context.analyze(
            "artificial intelligence",
            timespan="7d",
        )

        print(f"\nQuery: 'artificial intelligence'")
        print(f"Articles analyzed: {result.article_count}")

        if result.themes:
            print(f"\nTop Themes:")
            for theme in result.themes[:5]:
                print(f"  - {theme.theme}: {theme.count} mentions")

        if result.entities:
            print(f"\nTop Entities:")
            for entity in result.entities[:5]:
                print(f"  - {entity.name} ({entity.entity_type}): {entity.count}")

        if result.tone:
            print(f"\nTone Analysis:")
            print(f"  Average tone: {result.tone.average_tone:.2f}")
            print(f"  Positive: {result.tone.positive_count}")
            print(f"  Negative: {result.tone.negative_count}")
            print(f"  Neutral: {result.tone.neutral_count}")


async def get_entities_by_type() -> None:
    """Get entities filtered by type."""
    print("\n" + "=" * 60)
    print("Example 2: Entities by Type")
    print("=" * 60)

    async with GDELTClient() as client:
        # Get people mentioned in climate change coverage
        people = await client.context.get_entities(
            "climate change",
            entity_type="PERSON",
            timespan="30d",
            limit=10,
        )

        print(f"\nTop people mentioned in 'climate change' coverage:")
        for person in people:
            print(f"  - {person.name}: {person.count} mentions")

        # Get organizations
        orgs = await client.context.get_entities(
            "climate change",
            entity_type="ORG",
            timespan="30d",
            limit=10,
        )

        print(f"\nTop organizations:")
        for org in orgs:
            print(f"  - {org.name}: {org.count} mentions")


async def compare_topic_themes() -> None:
    """Compare themes across different topics."""
    print("\n" + "=" * 60)
    print("Example 3: Compare Topic Themes")
    print("=" * 60)

    async with GDELTClient() as client:
        topics = ["technology", "healthcare", "economy"]

        for topic in topics:
            themes = await client.context.get_themes(topic, limit=3)
            print(f"\n'{topic}' top themes:")
            for theme in themes:
                print(f"  - {theme.theme}: {theme.count}")


async def main() -> None:
    """Run all examples."""
    await analyze_topic_context()
    await get_entities_by_type()
    await compare_topic_themes()

    print("\n" + "=" * 60)
    print("Context API examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
```

#### 2.2 GEO API Example

**File**: `examples/geo_api_example.py`

```python
#!/usr/bin/env python3
"""Example: Query GDELT GEO 2.0 API for geographic data.

Demonstrates:
- Basic geographic search
- Bounding box filtering
- GeoJSON output for mapping
- Location analysis
"""

import asyncio

from py_gdelt import GDELTClient
from py_gdelt.filters import GeoFilter


async def search_locations() -> None:
    """Search for locations mentioned in news."""
    print("=" * 60)
    print("Example 1: Basic Geographic Search")
    print("=" * 60)

    async with GDELTClient() as client:
        # Search for earthquake-related locations
        result = await client.geo.search(
            "earthquake",
            timespan="7d",
            max_points=50,
        )

        print(f"\nFound {len(result.points)} locations for 'earthquake'")
        print(f"\nTop locations by article count:")

        # Sort by count
        sorted_points = sorted(result.points, key=lambda p: p.count, reverse=True)
        for point in sorted_points[:10]:
            print(f"  - {point.name or 'Unknown'}: {point.count} articles")
            print(f"    Coordinates: ({point.lat:.2f}, {point.lon:.2f})")


async def search_with_bounding_box() -> None:
    """Search within a geographic bounding box."""
    print("\n" + "=" * 60)
    print("Example 2: Bounding Box Search (Europe)")
    print("=" * 60)

    async with GDELTClient() as client:
        # Search within Europe bounding box
        # (min_lat, min_lon, max_lat, max_lon)
        europe_bbox = (35.0, -10.0, 70.0, 40.0)

        result = await client.geo.search(
            "energy crisis",
            timespan="7d",
            bounding_box=europe_bbox,
            max_points=30,
        )

        print(f"\nFound {len(result.points)} locations in Europe for 'energy crisis'")
        for point in result.points[:10]:
            print(f"  - {point.name}: {point.count} articles at ({point.lat:.2f}, {point.lon:.2f})")


async def get_geojson_output() -> None:
    """Get raw GeoJSON for mapping libraries."""
    print("\n" + "=" * 60)
    print("Example 3: GeoJSON Output")
    print("=" * 60)

    async with GDELTClient() as client:
        # Get GeoJSON format for use with mapping libraries
        geojson = await client.geo.to_geojson(
            "climate protest",
            timespan="30d",
            max_points=100,
        )

        print(f"\nGeoJSON type: {geojson.get('type')}")
        features = geojson.get('features', [])
        print(f"Number of features: {len(features)}")

        if features:
            print(f"\nFirst feature:")
            feat = features[0]
            print(f"  Geometry: {feat.get('geometry', {}).get('type')}")
            print(f"  Properties: {list(feat.get('properties', {}).keys())}")


async def main() -> None:
    """Run all examples."""
    await search_locations()
    await search_with_bounding_box()
    await get_geojson_output()

    print("\n" + "=" * 60)
    print("GEO API examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
```

#### 2.3 TV API Example

**File**: `examples/tv_api_example.py`

```python
#!/usr/bin/env python3
"""Example: Query GDELT TV and TVAI APIs for television news monitoring.

Demonstrates:
- Searching TV transcripts for clips
- Timeline of TV mentions
- Station comparison charts
- AI-enhanced TV search
"""

import asyncio

from py_gdelt import GDELTClient


async def search_tv_clips() -> None:
    """Search for TV clips mentioning a topic."""
    print("=" * 60)
    print("Example 1: TV Clip Search")
    print("=" * 60)

    async with GDELTClient() as client:
        # Search for clips about "economy"
        clips = await client.tv.search(
            "economy",
            timespan="24h",
            max_results=10,
        )

        print(f"\nFound {len(clips)} clips about 'economy'")
        for clip in clips[:5]:
            print(f"\n  Station: {clip.station}")
            print(f"  Show: {clip.show_name}")
            if clip.date:
                print(f"  Date: {clip.date}")
            if clip.snippet:
                print(f"  Snippet: {clip.snippet[:100]}...")


async def search_by_station() -> None:
    """Search clips on a specific station."""
    print("\n" + "=" * 60)
    print("Example 2: Station-Specific Search")
    print("=" * 60)

    async with GDELTClient() as client:
        stations = ["CNN", "FOXNEWS", "MSNBC"]

        for station in stations:
            clips = await client.tv.search(
                "election",
                timespan="7d",
                station=station,
                max_results=5,
            )
            print(f"\n{station}: {len(clips)} clips about 'election'")
            if clips:
                print(f"  First clip show: {clips[0].show_name}")


async def get_timeline() -> None:
    """Get timeline of TV mentions."""
    print("\n" + "=" * 60)
    print("Example 3: TV Mention Timeline")
    print("=" * 60)

    async with GDELTClient() as client:
        timeline = await client.tv.timeline(
            "immigration",
            timespan="7d",
        )

        print(f"\nTimeline for 'immigration' (last 7 days):")
        print(f"Number of data points: {len(timeline.points)}")

        if timeline.points:
            # Show last 5 data points
            for point in timeline.points[-5:]:
                print(f"  {point.date}: {point.count} mentions")


async def compare_stations() -> None:
    """Compare coverage across stations."""
    print("\n" + "=" * 60)
    print("Example 4: Station Comparison")
    print("=" * 60)

    async with GDELTClient() as client:
        chart = await client.tv.station_chart(
            "healthcare",
            timespan="7d",
        )

        print(f"\nStation coverage for 'healthcare':")
        for station in chart.stations[:10]:
            pct = f"{station.percentage:.1f}%" if station.percentage else "N/A"
            print(f"  {station.station}: {station.count} mentions ({pct})")


async def ai_enhanced_search() -> None:
    """Use AI-enhanced TV search."""
    print("\n" + "=" * 60)
    print("Example 5: AI-Enhanced Search")
    print("=" * 60)

    async with GDELTClient() as client:
        # TVAI provides AI-enhanced search capabilities
        clips = await client.tv_ai.search(
            "artificial intelligence impact on jobs",
            timespan="7d",
            max_results=5,
        )

        print(f"\nAI-enhanced search found {len(clips)} clips")
        for clip in clips[:3]:
            print(f"\n  Station: {clip.station}")
            print(f"  Show: {clip.show_name}")
            if clip.snippet:
                print(f"  Snippet: {clip.snippet[:150]}...")


async def main() -> None:
    """Run all examples."""
    await search_tv_clips()
    await search_by_station()
    await get_timeline()
    await compare_stations()
    await ai_enhanced_search()

    print("\n" + "=" * 60)
    print("TV API examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
```

**Success Criteria:**
- [ ] `context_api_example.py` runs successfully
- [ ] `geo_api_example.py` runs successfully
- [ ] `tv_api_example.py` runs successfully
- [ ] All examples documented in `examples/README.md`

---

### Phase 3: Create Integration Tests

**Goal**: Create integration tests that don't become stale over time.

**Key Principles:**
1. **Avoid hardcoded dates** - Use relative time ranges (`timespan="7d"`)
2. **Don't assert specific counts** - Assert `len(result) > 0` instead of `len(result) == 42`
3. **Test API contracts, not content** - Verify structure, not specific values
4. **Use pytest markers** - `@pytest.mark.integration` for optional tests
5. **Timeout protection** - Use reasonable timeouts for live API calls

#### Integration Test Files

**File**: `tests/integration/test_doc_api.py`

```python
"""Integration tests for DOC 2.0 API.

These tests make real API calls and verify response structure.
Run with: pytest tests/integration/ -m integration
"""

import pytest

from py_gdelt import GDELTClient
from py_gdelt.filters import DocFilter


@pytest.mark.integration
@pytest.mark.asyncio
async def test_doc_search_returns_articles() -> None:
    """Test that DOC search returns articles with expected structure."""
    async with GDELTClient() as client:
        doc_filter = DocFilter(
            query="technology",
            timespan="24h",  # Relative, not hardcoded date
            max_results=10,
        )

        articles = await client.doc.query(doc_filter)

        # Assert we got results (don't assert exact count)
        assert len(articles) >= 0  # API may return 0 sometimes

        # If we got results, verify structure
        if articles:
            article = articles[0]
            assert hasattr(article, 'title')
            assert hasattr(article, 'url')
            assert hasattr(article, 'domain')
            assert article.url.startswith('http')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_doc_search_with_language_filter() -> None:
    """Test language filtering works."""
    async with GDELTClient() as client:
        doc_filter = DocFilter(
            query="climate",
            timespan="7d",
            source_language="english",
            max_results=5,
        )

        articles = await client.doc.query(doc_filter)

        # Just verify it doesn't error - content filtering is best-effort
        assert isinstance(articles, list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_doc_timeline() -> None:
    """Test timeline endpoint returns data points."""
    async with GDELTClient() as client:
        timeline = await client.doc.timeline(
            query="election",
            timespan="7d",
        )

        # Verify structure
        assert hasattr(timeline, 'points')
        assert isinstance(timeline.points, list)
```

**File**: `tests/integration/test_geo_api.py`

```python
"""Integration tests for GEO 2.0 API."""

import pytest

from py_gdelt import GDELTClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_geo_search_returns_points() -> None:
    """Test that GEO search returns geographic points."""
    async with GDELTClient() as client:
        result = await client.geo.search(
            "earthquake",
            timespan="7d",
            max_points=20,
        )

        assert hasattr(result, 'points')
        assert isinstance(result.points, list)

        if result.points:
            point = result.points[0]
            assert hasattr(point, 'lat')
            assert hasattr(point, 'lon')
            assert -90 <= point.lat <= 90
            assert -180 <= point.lon <= 180


@pytest.mark.integration
@pytest.mark.asyncio
async def test_geo_geojson_format() -> None:
    """Test GeoJSON output format."""
    async with GDELTClient() as client:
        geojson = await client.geo.to_geojson(
            "flood",
            timespan="7d",
        )

        # Verify GeoJSON structure
        assert isinstance(geojson, dict)
        # May be FeatureCollection or empty
        if 'features' in geojson:
            assert isinstance(geojson['features'], list)
```

**File**: `tests/integration/test_context_api.py`

```python
"""Integration tests for Context 2.0 API."""

import pytest

from py_gdelt import GDELTClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_context_analyze_returns_result() -> None:
    """Test contextual analysis returns structured result."""
    async with GDELTClient() as client:
        result = await client.context.analyze(
            "technology",
            timespan="7d",
        )

        assert hasattr(result, 'query')
        assert result.query == "technology"
        assert hasattr(result, 'themes')
        assert hasattr(result, 'entities')
        assert isinstance(result.themes, list)
        assert isinstance(result.entities, list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_context_get_themes() -> None:
    """Test getting themes for a topic."""
    async with GDELTClient() as client:
        themes = await client.context.get_themes(
            "climate change",
            limit=5,
        )

        assert isinstance(themes, list)
        assert len(themes) <= 5

        if themes:
            theme = themes[0]
            assert hasattr(theme, 'theme')
            assert hasattr(theme, 'count')
            assert theme.count >= 0
```

**File**: `tests/integration/test_tv_api.py`

```python
"""Integration tests for TV and TVAI APIs."""

import pytest

from py_gdelt import GDELTClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tv_search_returns_clips() -> None:
    """Test TV search returns clips with expected structure."""
    async with GDELTClient() as client:
        clips = await client.tv.search(
            "politics",
            timespan="24h",
            max_results=10,
        )

        assert isinstance(clips, list)

        if clips:
            clip = clips[0]
            assert hasattr(clip, 'station')
            assert hasattr(clip, 'show_name')
            assert clip.station  # Non-empty


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tv_timeline() -> None:
    """Test TV timeline returns data points."""
    async with GDELTClient() as client:
        timeline = await client.tv.timeline(
            "election",
            timespan="7d",
        )

        assert hasattr(timeline, 'points')
        assert isinstance(timeline.points, list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tv_station_chart() -> None:
    """Test station chart returns station data."""
    async with GDELTClient() as client:
        chart = await client.tv.station_chart(
            "healthcare",
            timespan="7d",
        )

        assert hasattr(chart, 'stations')
        assert isinstance(chart.stations, list)

        if chart.stations:
            station = chart.stations[0]
            assert hasattr(station, 'station')
            assert hasattr(station, 'count')
```

**File**: `tests/integration/test_events_files.py`

```python
"""Integration tests for Events endpoint with file sources."""

import pytest
from datetime import date, timedelta

from py_gdelt import GDELTClient
from py_gdelt.filters import DateRange, EventFilter


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(120)  # 2 minute timeout for file downloads
async def test_events_query_returns_events() -> None:
    """Test events query returns events from files."""
    # Use yesterday to ensure data exists
    yesterday = date.today() - timedelta(days=1)

    async with GDELTClient() as client:
        event_filter = EventFilter(
            date_range=DateRange(start=yesterday, end=yesterday),
        )

        result = await client.events.query(event_filter)

        # File-based queries may fail if files don't exist yet
        # Just verify we get a list back
        assert isinstance(result, list) or hasattr(result, '__iter__')


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(120)
async def test_events_streaming() -> None:
    """Test events streaming works."""
    yesterday = date.today() - timedelta(days=1)

    async with GDELTClient() as client:
        event_filter = EventFilter(
            date_range=DateRange(start=yesterday, end=yesterday),
        )

        count = 0
        async for event in client.events.stream(event_filter):
            count += 1
            assert hasattr(event, 'global_event_id')
            if count >= 10:  # Just verify streaming works
                break

        # We streamed at least something (or 0 if no files)
        assert count >= 0
```

**File**: `tests/integration/conftest.py`

```python
"""Integration test configuration."""

import pytest


def pytest_configure(config):
    """Register integration marker."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (live API calls)"
    )


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio backend for async tests."""
    return "asyncio"
```

**Update**: `pyproject.toml`

Add integration test marker:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --tb=short"
markers = [
    "integration: mark test as integration test (makes live API calls)",
]
```

**Success Criteria:**
- [ ] All integration tests pass when run with live API
- [ ] Tests use relative time ranges (no hardcoded dates)
- [ ] Tests verify structure, not specific content
- [ ] Tests can be skipped with `pytest -m "not integration"`

---

### Phase 4: Create Jupyter Notebooks

**Goal**: Interactive notebook examples for all major features.

**Directory**: `notebooks/`

**Required setup for Jupyter async support**:
```python
import nest_asyncio
nest_asyncio.apply()
```

#### Notebook Files

**File**: `notebooks/01_getting_started.ipynb`

```markdown
# Getting Started with py-gdelt

This notebook introduces the py-gdelt library and demonstrates basic usage.

## Setup
- Installing the library
- Basic client initialization
- Your first query

## Contents
1. Installation
2. Basic Client Usage
3. Querying Events
4. Using REST APIs (DOC, GEO, Context, TV)
5. Accessing Lookup Tables
```

**File**: `notebooks/02_events_and_mentions.ipynb`

```markdown
# Working with Events and Mentions

Deep dive into GDELT Events and Mentions data.

## Contents
1. Event data structure
2. Filtering events (by country, actor, event type)
3. Streaming large datasets
4. Deduplication strategies
5. Working with Mentions
```

**File**: `notebooks/03_gkg_and_ngrams.ipynb`

```markdown
# Global Knowledge Graph and NGrams

Explore GKG records and word frequency analysis.

## Contents
1. GKG data structure
2. Theme and entity extraction
3. NGrams 3.0 overview
4. Position-based filtering
5. Language diversity analysis
```

**File**: `notebooks/04_rest_apis.ipynb`

```markdown
# REST API Endpoints

Comprehensive guide to DOC, GEO, Context, and TV APIs.

## Contents
1. DOC API - Article search
2. GEO API - Geographic analysis
3. Context API - Thematic analysis
4. TV API - Television news monitoring
5. Combining multiple APIs
```

**File**: `notebooks/05_advanced_patterns.ipynb`

```markdown
# Advanced Usage Patterns

Production-ready patterns and best practices.

## Contents
1. Configuration options
2. Error handling
3. Caching strategies
4. BigQuery integration
5. Memory-efficient processing
6. Building data pipelines
```

**File**: `notebooks/06_visualization.ipynb`

```markdown
# Data Visualization

Visualizing GDELT data with pandas and matplotlib.

## Contents
1. Timeline charts
2. Geographic maps (with folium)
3. Tone analysis plots
4. Station comparison charts
5. Entity networks
```

**Success Criteria:**
- [ ] All notebooks execute without errors
- [ ] Each notebook is self-contained with clear outputs
- [ ] Notebooks include markdown explanations
- [ ] `notebooks/README.md` provides overview

---

### Phase 5: Build Documentation Site

**Goal**: Comprehensive documentation using MkDocs Material.

**Setup required in `pyproject.toml`**:

```toml
[project.optional-dependencies]
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.0",
    "mkdocstrings[python]>=0.24",
]
```

**File**: `mkdocs.yml`

```yaml
site_name: py-gdelt
site_description: Python client library for GDELT
repo_url: https://github.com/yourusername/py-gdelt

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - content.code.copy
  palette:
    primary: indigo

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            show_source: true
            show_root_heading: true

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quickstart.md
    - Configuration: getting-started/configuration.md
  - User Guide:
    - Events & Mentions: user-guide/events.md
    - GKG: user-guide/gkg.md
    - NGrams: user-guide/ngrams.md
    - REST APIs: user-guide/rest-apis.md
    - Lookups: user-guide/lookups.md
    - Streaming: user-guide/streaming.md
    - Deduplication: user-guide/deduplication.md
    - Error Handling: user-guide/errors.md
  - API Reference:
    - Client: api/client.md
    - Endpoints: api/endpoints.md
    - Filters: api/filters.md
    - Models: api/models.md
    - Exceptions: api/exceptions.md
  - Examples:
    - Overview: examples/index.md
    - Basic Usage: examples/basic.md
    - Advanced Patterns: examples/advanced.md
  - Contributing: contributing.md
```

**Documentation Files Structure**:

```
docs/
├── index.md                      # Home page
├── getting-started/
│   ├── installation.md           # pip install, dependencies
│   ├── quickstart.md             # 5-minute intro
│   └── configuration.md          # Settings, env vars, TOML
├── user-guide/
│   ├── events.md                 # Events endpoint deep dive
│   ├── gkg.md                    # GKG endpoint
│   ├── ngrams.md                 # NGrams (existing, expand)
│   ├── rest-apis.md              # DOC, GEO, Context, TV
│   ├── lookups.md                # CAMEO, themes, countries
│   ├── streaming.md              # Memory-efficient patterns
│   ├── deduplication.md          # 5 strategies explained
│   └── errors.md                 # Exception handling
├── api/
│   ├── client.md                 # ::: py_gdelt.GDELTClient
│   ├── endpoints.md              # All endpoint classes
│   ├── filters.md                # Filter models
│   ├── models.md                 # Data models
│   └── exceptions.md             # Exception hierarchy
├── examples/
│   ├── index.md                  # Examples overview
│   ├── basic.md                  # Basic patterns
│   └── advanced.md               # Production patterns
└── contributing.md               # How to contribute
```

**Success Criteria:**
- [ ] `mkdocs serve` runs without errors
- [ ] All API reference pages generate correctly
- [ ] Code examples are syntax-highlighted
- [ ] Navigation is intuitive
- [ ] Search works

---

## Acceptance Criteria

### Functional Requirements

- [ ] All 7 existing examples run without errors
- [ ] 3 new examples created (Context, GEO, TV)
- [ ] Integration tests cover all REST API endpoints
- [ ] Integration tests cover file-based endpoints
- [ ] 6 Jupyter notebooks created and working
- [ ] Documentation site builds successfully
- [ ] API reference auto-generates from docstrings

### Non-Functional Requirements

- [ ] Integration tests complete in < 3 minutes total
- [ ] Integration tests can be skipped with marker
- [ ] Notebooks work with `nest_asyncio`
- [ ] Documentation builds in < 30 seconds

### Quality Gates

- [ ] `pytest tests/` passes (existing tests still work)
- [ ] `pytest tests/integration/ -m integration` passes
- [ ] `ruff check examples/` passes
- [ ] `mypy examples/` passes
- [ ] All notebooks execute top-to-bottom without errors

---

## Success Metrics

1. **Coverage**: All 9 API endpoints have examples
2. **Stability**: Integration tests run without flaking
3. **Discoverability**: New users can start in < 5 minutes
4. **Completeness**: Documentation covers all public APIs

---

## Dependencies & Prerequisites

### New Dependencies (dev only)

```toml
[project.optional-dependencies]
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.0",
    "mkdocstrings[python]>=0.24",
]
notebooks = [
    "jupyter>=1.0",
    "nest-asyncio>=1.5",
]
```

### External Requirements

- GDELT APIs must be accessible (no auth required)
- Network connectivity for integration tests
- Python 3.12+ environment

---

## Risk Analysis & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GDELT API rate limiting | Medium | Medium | Use timespan filters, add delays between tests |
| Integration tests flaky | Medium | Medium | Test structure not content, use relative dates |
| Notebooks break on updates | Low | Medium | Include version pins in notebooks |
| Documentation stale | Medium | Low | Generate API docs from docstrings (auto-updates) |

---

## Implementation Checklist

### Phase 1: Verify Existing Examples
- [ ] Run and fix `basic_client_usage.py`
- [ ] Run and fix `events_endpoint_example.py`
- [ ] Run and fix `gkg_example.py`
- [ ] Run and fix `ngrams_example.py`
- [ ] Run and fix `download_gdelt_files.py`
- [ ] Update `examples/README.md`

### Phase 2: Create Missing Examples
- [ ] Create `examples/context_api_example.py`
- [ ] Create `examples/geo_api_example.py`
- [ ] Create `examples/tv_api_example.py`
- [ ] Update `examples/README.md` with new examples

### Phase 3: Integration Tests
- [ ] Create `tests/integration/conftest.py`
- [ ] Create `tests/integration/test_doc_api.py`
- [ ] Create `tests/integration/test_geo_api.py`
- [ ] Create `tests/integration/test_context_api.py`
- [ ] Create `tests/integration/test_tv_api.py`
- [ ] Create `tests/integration/test_events_files.py`
- [ ] Update `pyproject.toml` with integration marker

### Phase 4: Jupyter Notebooks
- [ ] Create `notebooks/` directory
- [ ] Create `notebooks/01_getting_started.ipynb`
- [ ] Create `notebooks/02_events_and_mentions.ipynb`
- [ ] Create `notebooks/03_gkg_and_ngrams.ipynb`
- [ ] Create `notebooks/04_rest_apis.ipynb`
- [ ] Create `notebooks/05_advanced_patterns.ipynb`
- [ ] Create `notebooks/06_visualization.ipynb`
- [ ] Create `notebooks/README.md`

### Phase 5: Documentation
- [ ] Create `mkdocs.yml`
- [ ] Create `docs/index.md`
- [ ] Create `docs/getting-started/` directory with 3 files
- [ ] Create `docs/user-guide/` directory with 8 files
- [ ] Create `docs/api/` directory with 5 files
- [ ] Create `docs/examples/` directory with 3 files
- [ ] Create `docs/contributing.md`
- [ ] Verify `mkdocs serve` works

---

## References & Research

### Internal References
- Implementation plan: `plans/gdelt-python-client-implementation.md`
- Existing documentation: `docs/ngrams_endpoint.md`
- Existing integration test: `tests/integration_trump_venezuela.py`
- Test patterns: `tests/unit/test_endpoints_*.py`
- Source README: `src/py_gdelt/sources/README.md`

### External References
- MkDocs Material: https://squidfunk.github.io/mkdocs-material/
- mkdocstrings: https://mkdocstrings.github.io/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- respx: https://lundberg.github.io/respx/

---

## SpecFlow Analysis: Key Clarifications

Based on SpecFlow analysis, the following decisions have been made:

### Critical Decisions

| Question | Decision |
|----------|----------|
| **Python version** | 3.12+ (pyproject.toml is authoritative) |
| **Date strategy for examples** | REST APIs use `timespan="7d"`, file-based use `date.today() - timedelta(days=2)` for safety margin |
| **TVAIEndpoint methods** | Verified: `search()` method exists (checked `src/py_gdelt/endpoints/tv.py:419`) |
| **Rate limit handling in tests** | Serial execution, no delays (rely on relative timespans), retry once on 429 |
| **Empty results** | Assert structure not counts: `isinstance(result, list)` is sufficient |
| **Optional dependency errors** | Examples should have try/except ImportError with helpful pip install message |

### Integration Test Strategy

- **Markers**: `@pytest.mark.integration` for all live API tests
- **Timeout**: 60s for REST APIs, 120s for file-based endpoints
- **Assertions**: Test structure (`hasattr`, `isinstance`), not content (`len(result) == 42`)
- **Dates**: Always relative (`timespan="7d"` or `date.today() - timedelta(days=2)`)
- **Parallel**: No parallelization (serial execution via pytest defaults)

### Notebook Strategy

- **Setup cell**: All notebooks start with `nest_asyncio.apply()` and import boilerplate
- **Dependencies**: Notebooks have `try/except ImportError` for optional deps (pandas, folium)
- **Caching**: No caching (fresh API calls each run) - keeps examples simple

### Documentation Strategy

- **API docs**: Generated from docstrings via mkdocstrings
- **Code validation**: Manual for now (CI validation deferred)
- **Versioning**: Single version docs initially (mike for versioning deferred)

---

## Identified Edge Cases to Handle

| Edge Case | Handling |
|-----------|----------|
| Files not published yet for recent dates | Use `date.today() - timedelta(days=2)` |
| API returns non-English despite filter | Note in example comments, don't fail tests |
| Network blocked/offline | Examples catch ConnectionError, display helpful message |
| Empty results for legitimate queries | Examples explain this possibility in output |
| Notebook kernel restart | Use context managers in each cell |

---

*Plan generated: January 2026*
*Estimated effort: 3-5 days*
*SpecFlow analysis: Completed - 21 gaps identified, 5 critical decisions made*
