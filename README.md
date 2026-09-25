# gdelt-py

[![CI](https://github.com/RBozydar/py-gdelt/workflows/CI/badge.svg)](https://github.com/RBozydar/py-gdelt/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/gdelt-py.svg)](https://badge.fury.io/py/gdelt-py)
[![Python Versions](https://img.shields.io/pypi/pyversions/gdelt-py.svg)](https://pypi.org/project/gdelt-py/)
[![License](https://img.shields.io/github/license/RBozydar/py-gdelt.svg)](https://github.com/RBozydar/py-gdelt/blob/main/LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

A comprehensive Python client library for the [GDELT](https://www.gdeltproject.org/) (Global Database of Events, Language, and Tone) project.

## Features

- **Unified Interface**: Single client covering all 6 REST APIs, 3 database tables, and NGrams dataset
- **Version Normalization**: Transparent handling of GDELT v1/v2 differences with normalized output
- **Resilience**: Automatic fallback to BigQuery when APIs fail or rate limit
- **Modern Python**: 3.11+, Async-first, Pydantic models, type hints throughout
- **Streaming**: Generator-based iteration for large datasets with memory efficiency
- **Developer Experience**: Clear errors, progress indicators, comprehensive lookups

## Installation

```bash
# Basic installation
pip install gdelt-py

# With BigQuery support
pip install gdelt-py[bigquery]

# With all optional dependencies
pip install gdelt-py[bigquery,pandas]
```

## Quick Start

```python
from py_gdelt import GDELTClient
from py_gdelt.filters import DateRange, EventFilter
from datetime import date, timedelta

async with GDELTClient() as client:
    # Query recent events
    yesterday = date.today() - timedelta(days=1)
    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
        actor1_country="USA",
    )

    result = await client.events.query(event_filter)
    print(f"Found {len(result)} events")

    # Query Visual GKG (image analysis)
    from py_gdelt.filters import VGKGFilter

    vgkg_filter = VGKGFilter(
        date_range=DateRange(start=yesterday),
        domain="cnn.com",
    )
    images = await client.vgkg.query(vgkg_filter)

    # Query TV NGrams (word frequencies from TV)
    from py_gdelt.filters import BroadcastNGramsFilter

    tv_filter = BroadcastNGramsFilter(
        date_range=DateRange(start=yesterday),
        station="CNN",
        ngram_size=1,
    )
    ngrams = await client.tv_ngrams.query(tv_filter)

    # Query Graph Datasets (quotes, entities, frontpage links)
    from py_gdelt.filters import GQGFilter, GEGFilter

    gqg_filter = GQGFilter(date_range=DateRange(start=yesterday))
    quotes = await client.graphs.query_gqg(gqg_filter)

    geg_filter = GEGFilter(date_range=DateRange(start=yesterday))
    async for entity in client.graphs.stream_geg(geg_filter):
        print(f"{entity.name}: {entity.entity_type}")
```

## Data Sources Covered

### File-Based Endpoints
- **Events** - Structured event data (who did what to whom, when, where)
- **Mentions** - Article mentions of events over time
- **GKG** - Global Knowledge Graph (themes, entities, tone, quotations)
- **NGrams** - Word and phrase occurrences in articles (Jan 2020+)
- **VGKG** - Visual GKG (image annotations via Cloud Vision API)
- **TV-GKG** - Television GKG (closed caption analysis from TV broadcasts)
- **TV NGrams** - Word frequencies from TV closed captions
- **Radio NGrams** - Word frequencies from radio transcripts
- **Graph Datasets** - GQG, GEG, GFG, GGG, GEMG, GAL (see below)

### REST APIs
- **DOC 2.0** - Full-text article search and discovery
- **GEO 2.0** - Geographic analysis and mapping
- **Context 2.0** - Sentence-level contextual search
- **TV 2.0** - Television news closed caption search
- **TV AI 2.0** - AI-enhanced visual TV search (labels, OCR, faces)
- **LowerThird** 🏗️ - TV chyron/lower-third text search
- **TVV** 🏗️ - TV Visual channel inventory
- **GKG GeoJSON v1** 🏗️ - Legacy geographic GKG API

### Graph Datasets
- **GQG** - Global Quotation Graph (extracted quotes with context)
- **GEG** - Global Entity Graph (NER via Cloud NLP API)
- **GFG** - Global Frontpage Graph (homepage link tracking)
- **GGG** - Global Geographic Graph (location co-mentions)
- **GDG** 🏗️ - Global Difference Graph (article change detection)
- **GEMG** - Global Embedded Metadata Graph (meta tags, JSON-LD)
- **GRG** 🏗️ - Global Relationship Graph (subject-verb-object triples)
- **GAL** - Article List (lightweight article metadata)

### Lookup Tables
- **CAMEO** - Event classification codes and Goldstein scale
- **Themes** - GKG theme taxonomy
- **Countries** - Country code conversions (FIPS ↔ ISO)
- **Ethnic/Religious Groups** - Group classification codes
- **GCAM** 🏗️ - 2,300+ emotional/thematic dimensions
- **Image Tags** 🏗️ - Cloud Vision labels for DOC API
- **Languages** 🏗️ - Supported language codes

## Data Source Matrix

| Data Type | API | BigQuery | Raw Files | Time Range | Fallback |
|-----------|:---:|:--------:|:---------:|------------|:--------:|
| **Articles (fulltext)** | DOC 2.0 | - | - | Rolling 3 months | - |
| **Article geography** | GEO 2.0 | - | - | Rolling 7 days | - |
| **Sentence context** | Context 2.0 | - | - | Rolling 72 hours | - |
| **TV captions** | TV 2.0 | - | - | Jul 2009+ | - |
| **TV visual/AI** | TV AI 2.0 | - | - | Jul 2010+ | - |
| **TV chyrons** 🏗️ | LowerThird | - | - | Aug 2017+ | - |
| **Events v2** | - | ✓ | ✓ | Feb 2015+ | ✓ |
| **Events v1** | - | ✓ | ✓ | 1979 - Feb 2015 | ✓ |
| **Mentions** | - | ✓ | ✓ | Feb 2015+ | ✓ |
| **GKG v2** | - | ✓ | ✓ | Feb 2015+ | ✓ |
| **GKG v1** | - | ✓ | ✓ | Apr 2013 - Feb 2015 | ✓ |
| **Web NGrams** | - | ✓ | ✓ | Jan 2020+ | ✓ |
| **VGKG** | - | ✓ | ✓ | Dec 2015+ | ✓ |
| **TV-GKG** | - | ✓ | ✓ | Jul 2009+ | ✓ |
| **TV NGrams** | - | - | ✓ | Jul 2009+ | - |
| **Radio NGrams** | - | - | ✓ | 2017+ | - |
| **GQG** | - | - | ✓ | Jan 2020+ | - |
| **GEG** | - | - | ✓ | Jul 2016+ | - |
| **GFG** | - | - | ✓ | Mar 2018+ | - |
| **GGG** | - | - | ✓ | Jan 2020+ | - |
| **GEMG** | - | - | ✓ | Jan 2020+ | - |
| **GAL** | - | - | ✓ | Jan 2020+ | - |

> 🏗️ = Work in progress - coming in future releases

## Key Concepts

### Async-First Design

All I/O operations are async by default for optimal performance:

```python
async with GDELTClient() as client:
    articles = await client.doc.query(doc_filter)
```

Synchronous wrappers are available for compatibility:

```python
with GDELTClient() as client:
    articles = client.doc.query_sync(doc_filter)
```

### Streaming for Efficiency

Process large datasets without loading everything into memory:

```python
async with GDELTClient() as client:
    async for event in client.events.stream(event_filter):
        process(event)  # Memory-efficient
```

### Type Safety

Pydantic models throughout with full type hints:

```python
event: Event = result[0]
assert event.goldstein_scale  # Type-checked
```

### Configuration

Flexible configuration via environment variables, TOML files, or programmatic settings:

```python
settings = GDELTSettings(
    timeout=60,
    max_retries=5,
    cache_dir=Path("/custom/cache"),
)

async with GDELTClient(settings=settings) as client:
    ...
```

## Documentation

Full documentation available at: https://rbozydar.github.io/py-gdelt/

## Contributing

Contributions are welcome! See [Contributing Guide](https://github.com/RBozydar/py-gdelt/blob/main/CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [GitHub Repository](https://github.com/RBozydar/py-gdelt)
- [PyPI Package](https://pypi.org/project/gdelt-py/)
- [Documentation](https://rbozydar.github.io/py-gdelt/)
- [GDELT Project](https://www.gdeltproject.org/)
