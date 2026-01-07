# gdelt-py

A comprehensive Python client library for the [GDELT](https://www.gdeltproject.org/) (Global Database of Events, Language, and Tone) project.

## Features

- **Unified Interface**: Single client covering all 6 REST APIs, 3 database tables, and NGrams dataset
- **Version Normalization**: Transparent handling of GDELT v1/v2 differences with normalized output
- **Resilience**: Automatic fallback to BigQuery when APIs fail or rate limit
- **Modern Python**: 3.11+, Async-first, Pydantic models, type hints throughout
- **Streaming**: Generator-based iteration for large datasets with memory efficiency
- **Developer Experience**: Clear errors, progress indicators, comprehensive lookups

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

## Installation

```bash
# Basic installation
pip install gdelt-py

# With BigQuery support
pip install gdelt-py[bigquery]

# With all optional dependencies
pip install gdelt-py[bigquery,pandas]
```

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

## Project Structure

```
py-gdelt/
├── src/py_gdelt/
│   ├── client.py           # Main GDELTClient
│   ├── endpoints/          # All endpoint implementations
│   ├── filters/            # Query filter models
│   ├── models/             # Data models (Event, GKG, etc.)
│   ├── sources/            # Data sources (files, BigQuery)
│   ├── lookups/            # Lookup tables
│   └── utils/              # Utilities (deduplication, etc.)
├── tests/                  # Unit and integration tests
├── examples/               # Usage examples
├── notebooks/              # Jupyter notebooks
└── docs/                   # Documentation
```

## Documentation Structure
- **[Getting Started](getting-started/installation.md)** - Installation and quick start
- **[User Guide](user-guide/events.md)** - Deep dives into each feature
- **[API Reference](api/client.md)** - Complete API documentation
- **[Examples](examples/index.md)** - Practical usage examples

## Contributing

Contributions are welcome! See [Contributing Guide](contributing.md) for details.

## License

MIT License - see LICENSE file for details.

## Links

- [GitHub Repository](https://github.com/rbwasilewski/py-gdelt)
- [GDELT Project](https://www.gdeltproject.org/)
- [GDELT Documentation](https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/)
