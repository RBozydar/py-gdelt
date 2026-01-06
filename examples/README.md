# py-gdelt Examples

This directory contains example code demonstrating how to use the py-gdelt library.

## Available Examples

### Core Client Examples

- **`basic_client_usage.py`** - Comprehensive GDELTClient usage including:
  - Basic client initialization
  - Querying events data
  - Using REST API endpoints (DOC)
  - Accessing lookup tables (CAMEO, countries)
  - Custom configuration (programmatic and TOML file)
  - Streaming large datasets
  - Synchronous usage patterns

### File-Based Endpoints

- **`events_endpoint_example.py`** - EventsEndpoint examples:
  - Basic event queries with filtering
  - Streaming for memory efficiency
  - Deduplication strategies
  - Advanced filtering (actor countries, tone)
  - Synchronous wrappers

- **`gkg_example.py`** - Global Knowledge Graph (GKG) examples:
  - Querying GKG records by themes
  - Filtering by tone, organizations, locations
  - Streaming large result sets
  - Extracting quotations, entities
  - Both async and sync patterns

- **`download_gdelt_files.py`** - FileSource usage for downloading raw data:
  - Downloading recent events files
  - Fetching specific files by URL
  - Listing available files from master list
  - Custom concurrency controls

### NGrams Examples

- **`ngrams_example.py`** - NGrams 3.0 endpoint examples:
  - Querying word/phrase occurrences
  - Language filtering
  - Position-based filtering (headlines vs body)
  - Analyzing language diversity
  - Position distribution analysis

### BigQuery Examples

- **`query_mentions.py`** - BigQuery integration (requires credentials):
  - Querying MENTIONS table
  - Complex filtering and aggregations
  - Working with large datasets via BigQuery

- **`bigquery_example.py`** - General BigQuery usage (requires credentials):
  - Direct BigQuery queries
  - Using BigQuery as fallback source

### REST API Examples

- **`context_api_example.py`** - Context 2.0 API examples:
  - Contextual analysis (themes, entities, tone)
  - Filtering entities by type (PERSON, ORG, LOCATION)
  - Comparing topics
  - Sentiment analysis

- **`geo_api_example.py`** - GEO 2.0 API examples:
  - Geographic search
  - Bounding box filtering
  - GeoJSON output for mapping
  - Location analysis

- **`tv_api_example.py`** - TV and TVAI API examples:
  - Searching TV transcripts
  - Timeline of TV mentions
  - Station comparison charts
  - AI-enhanced TV search

## Running Examples

All examples are standalone scripts that can be run directly:

```bash
# File-based endpoints
python examples/basic_client_usage.py
python examples/events_endpoint_example.py
python examples/gkg_example.py
python examples/ngrams_example.py

# Download examples
python examples/download_gdelt_files.py list

# REST API examples
python examples/context_api_example.py
python examples/geo_api_example.py
python examples/tv_api_example.py

# BigQuery (requires credentials)
python examples/query_mentions.py
python examples/bigquery_example.py
```

## Quick Start

Basic usage pattern with GDELTClient:

```python
from datetime import date, timedelta
from py_gdelt import GDELTClient
from py_gdelt.filters import DateRange, EventFilter

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

## BigQuery Setup

For BigQuery examples, you need to:

1. Install BigQuery dependencies: `pip install py-gdelt[bigquery]`
2. Set up Google Cloud credentials:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
   ```
3. Or use the `gcp_project_id` setting in GDELTSettings

See [BigQuery documentation](https://cloud.google.com/bigquery/docs/authentication) for more details.
