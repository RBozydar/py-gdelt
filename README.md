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
```

## Data Sources Covered

### File-Based Endpoints
- **Events** - Structured event data (who, what, when, where)
- **Mentions** - Article mentions of events
- **GKG** - Global Knowledge Graph (themes, entities, quotations)
- **NGrams** - Word and phrase occurrences in articles

### REST APIs
- **DOC 2.0** - Article search and discovery
- **GEO 2.0** - Geographic analysis and mapping
- **Context 2.0** - Contextual analysis (themes, entities, sentiment)
- **TV** - Television news transcript search
- **TVAI** - AI-enhanced TV transcript search

### Lookup Tables
- **CAMEO** - Event classification codes
- **Themes** - GDELT theme taxonomy
- **Countries** - Country code conversions (FIPS, ISO2, ISO3)
- **Ethnic/Religious Groups** - Group classifications

## Data Source Matrix

| Data Type | API | BigQuery | Raw Files | Time Constraint | Fallback |
|-----------|-----|----------|-----------|-----------------|----------|
| Articles (fulltext) | DOC 2.0 | - | - | Rolling 3 months | No |
| Article geo heatmaps | GEO 2.0 | - | - | Rolling 7 days | No |
| Sentence-level context | Context 2.0 | - | - | Rolling 72 hours | No |
| TV captions | TV 2.0 | - | - | July 2009+ | No |
| Events v2 | - | Yes | Yes | Feb 2015+ | Yes |
| Events v1 | - | Yes | Yes | 1979 - Feb 2015 | Yes |
| Mentions | - | Yes | Yes | Feb 2015+ | Yes |
| GKG v2 | - | Yes | Yes | Feb 2015+ | Yes |
| GKG v1 | - | Yes | Yes | 2013 - Feb 2015 | Yes |
| Web NGrams 3.0 | - | Yes | Yes | Jan 2020+ | Yes |

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
