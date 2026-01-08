# Architecture

This page describes the high-level architecture of gdelt-py and how it manages multiple data sources.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GDELTClient                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐ │
│  │   doc   │ │   geo   │ │ context │ │   tv    │ │   tv_ai   │ │
│  │  (API)  │ │  (API)  │ │  (API)  │ │  (API)  │ │   (API)   │ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └───────────┘ │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐ │
│  │ events  │ │ mentions│ │   gkg   │ │ ngrams  │ │  lookups  │ │
│  │(Multi)  │ │ (Multi) │ │ (Multi) │ │ (Multi) │ │ (Bundled) │ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  REST APIs    │    │   BigQuery    │    │  Raw Files    │
│  (Real-time)  │    │  (Fallback/   │    │   (HTTP)      │
│               │    │   Historical) │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
```

### Endpoint Types

The library provides two categories of endpoints:

**API-Only Endpoints** (top row):

- `doc` - Article fulltext search (DOC 2.0 API)
- `geo` - Geographic visualizations (GEO 2.0 API)
- `context` - Sentence-level search (Context 2.0 API)
- `tv` - Television caption search (TV 2.0 API)
- `tv_ai` - Visual TV search (TV AI 2.0 API)

These endpoints only access GDELT REST APIs and have no fallback options.

**Multi-Source Endpoints** (bottom row):

- `events` - Event records (Files + BigQuery)
- `mentions` - Article mentions of events (Files + BigQuery)
- `gkg` - Global Knowledge Graph records (Files + BigQuery)
- `ngrams` - Web NGrams 3.0 (Files + BigQuery)
- `lookups` - Reference data (bundled with library)

These endpoints can switch between raw files and BigQuery for resilience. See [Data Sources](getting-started/data-sources.md) for detailed information about each data source and access method.

## Multi-Source Endpoints

For Events, Mentions, GKG, and NGrams, the library implements intelligent source selection:

```
┌─────────────────────────────────────────┐
│            EventsEndpoint               │
├─────────────────────────────────────────┤
│  query(filter, source="auto")           │
│                                         │
│  source="auto" logic:                   │
│  1. Try raw files (free, fast)          │
│  2. On failure/429 → BigQuery fallback  │
│  3. Large historical → prefer BigQuery  │
└─────────────────────────────────────────┘
```

### Source Selection

```python
# Auto mode (default) - intelligent source selection
events = await client.events.query(filter)

# Explicit file source
events = await client.events.query(filter, source="files")

# Explicit BigQuery source
events = await client.events.query(filter, source="bigquery")
```

### Fallback Behavior

When `source="auto"` (default):

1. **Primary**: Raw files are tried first (free, no authentication required)
2. **Fallback**: On rate limiting (HTTP 429) or errors, automatically switches to BigQuery
3. **Large queries**: For historical queries spanning many days, BigQuery may be preferred

### Configuration

Control fallback behavior via settings:

```python
from py_gdelt import GDELTClient, GDELTSettings

settings = GDELTSettings(
    fallback_to_bigquery=True,  # Enable automatic fallback
    bigquery_project="my-gcp-project",  # Required for BigQuery
)

async with GDELTClient(settings=settings) as client:
    # Will fallback to BigQuery if files fail
    events = await client.events.query(filter)
```

## Data Flow

### Query Execution

1. User creates a filter object (e.g., `EventFilter`)
2. User calls endpoint method (e.g., `client.events.query(filter)`)
3. Endpoint determines optimal source based on:
   - User preference (`source` parameter)
   - Query time range
   - Previous failures/rate limits
4. Source adapter fetches and parses data
5. Results are returned as Pydantic models

### Streaming

For large result sets, use streaming to process records without loading everything into memory:

```python
async with GDELTClient() as client:
    async for event in client.events.stream(filter):
        process(event)  # Memory efficient
```
