# GDELT Python API Specification

**Version**: 1.0.0-draft  
**Date**: January 2026  
**Python**: 3.11+  
**Status**: Pre-implementation

---

## Table of Contents

1. [Overview & Goals](#1-overview--goals)
2. [Data Sources & Access Matrix](#2-data-sources--access-matrix)
3. [Architecture](#3-architecture)
4. [Client API Reference](#4-client-api-reference)
5. [Data Models](#5-data-models)
6. [Configuration](#6-configuration)
7. [Error Handling](#7-error-handling)
8. [Utilities](#8-utilities)
9. [Technical Constraints & Gotchas](#9-technical-constraints--gotchas)
10. [Design Decisions Log](#10-design-decisions-log)
11. [Future Work](#11-future-work)
12. [Appendices](#appendices)

---

## 1. Overview & Goals

### 1.1 Project Purpose

A comprehensive Python client library for the GDELT (Global Database of Events, Language, and Tone) project, providing unified access to all GDELT data sources with a modern, type-safe API.

### 1.2 Goals

- **Unified Interface**: Single client covering all 6 REST APIs, 3 database tables, and NGrams dataset
- **Version Normalization**: Transparent handling of GDELT v1/v2 differences with normalized output
- **Resilience**: Automatic fallback to BigQuery when APIs fail or rate limit
- **Modern Python**: Async-first, Pydantic models, type hints throughout
- **Streaming**: Generator-based iteration for large datasets with memory efficiency
- **Developer Experience**: Clear errors, progress indicators, comprehensive lookups

### 1.3 Non-Goals (v1)

- CLI interface (library first)
- VGKG (Visual GKG) support
- Visualization helpers
- pandas as required dependency

---

## 2. Data Sources & Access Matrix

### 2.1 Complete Data Source Matrix

| Data Type | API | BigQuery | Raw Files | Time Constraint | Fallback Available |
|-----------|-----|----------|-----------|-----------------|-------------------|
| Articles (fulltext) | DOC 2.0 ✅ | ❌ | ❌ | Rolling 3 months | ❌ No equivalent |
| Article geo heatmaps | GEO 2.0 ✅ | ❌ | ❌ | Rolling 7 days | ❌ No equivalent |
| Sentence-level context | Context 2.0 ✅ | ❌ | ❌ | Rolling 72 hours | ❌ No equivalent |
| TV captions | TV 2.0 ✅ | ❌ | ❌ | July 2009+ (full) | ❌ No equivalent |
| TV visual/AI | TV AI 2.0 ✅ | ❌ | ❌ | 2010+, limited | ❌ No equivalent |
| Events v2 | ❌ | ✅ | ✅ | Feb 2015+ | ✅ Files ↔ BigQuery |
| Events v1 | ❌ | ✅ | ✅ | 1979 - Feb 2015 | ✅ Files ↔ BigQuery |
| Mentions | ❌ | ✅ | ✅ | Feb 2015+ (v2 only) | ✅ Files ↔ BigQuery |
| GKG v2 | ❌ | ✅ | ✅ | Feb 2015+ | ✅ Files ↔ BigQuery |
| GKG v1 | ❌ | ✅ | ✅ | 2013 - Feb 2015 | ✅ Files ↔ BigQuery |
| Web NGrams 3.0 | ❌ | ✅ | ✅ | Jan 2020+ | ✅ Files ↔ BigQuery |

### 2.2 Historical Fulltext Search Strategy

| Need | <3 months | 3mo - 5yr | >5yr |
|------|-----------|-----------|------|
| Fulltext search | DOC API | NGrams 3.0 | ❌ Not available |
| Entity/theme search | GKG | GKG | GKG (v1 to 2013) |
| Event tracking | Events | Events | Events (v1 to 1979) |

### 2.3 API Endpoints Reference

#### DOC 2.0 API
- **Endpoint**: `https://api.gdeltproject.org/api/v2/doc/doc`
- **Purpose**: Full-text article search
- **Time Window**: Rolling 3 months
- **Max Records**: 250
- **Output Modes**: artlist, timelinevol, timelinevolraw, timelinetone, timelinelang, timelinesourcecountry, imagecollage, tonechart

#### GEO 2.0 API
- **Endpoint**: `https://api.gdeltproject.org/api/v2/geo/geo`
- **Purpose**: Geographic visualizations
- **Time Window**: Rolling 7 days
- **Max Points**: 1,000-25,000 (mode dependent)

#### Context 2.0 API
- **Endpoint**: `https://api.gdeltproject.org/api/v2/context/context`
- **Purpose**: Sentence-level search (all terms in same sentence)
- **Time Window**: Rolling 72 hours
- **Max Records**: 200

#### TV 2.0 API
- **Endpoint**: `https://api.gdeltproject.org/api/v2/tv/tv`
- **Purpose**: Television closed caption search
- **Time Window**: July 2009+ (full archive)
- **Max Records**: 3,000

#### TV AI 2.0 API
- **Endpoint**: `https://api.gdeltproject.org/api/v2/tvai/tvai`
- **Purpose**: Visual television search (AI-powered)
- **Time Window**: 2010+ (limited channels)

#### GKG GeoJSON API (v1.0 Legacy)
- **Endpoint**: `https://api.gdeltproject.org/api/v1/gkg_geojson`
- **Purpose**: GeoJSON by GKG theme/person/org
- **Note**: Uses uppercase parameters

### 2.4 BigQuery Tables

| Table | Size | Project |
|-------|------|---------|
| `gdelt-bq.gdeltv2.events` | ~63GB | gdelt-bq |
| `gdelt-bq.gdeltv2.events_partitioned` | ~63GB | gdelt-bq |
| `gdelt-bq.gdeltv2.eventmentions` | ~104GB | gdelt-bq |
| `gdelt-bq.gdeltv2.gkg` | ~3.6TB | gdelt-bq |
| `gdelt-bq.gdeltv2.gkg_partitioned` | ~3.6TB | gdelt-bq |
| `gdelt-bq.gdeltv2.webngrams` | Variable | gdelt-bq |

### 2.5 Raw File Access

**Master File Lists**:
- English: `http://data.gdeltproject.org/gdeltv2/masterfilelist.txt`
- Translated: `http://data.gdeltproject.org/gdeltv2/masterfilelist-translation.txt`
- Last update: `http://data.gdeltproject.org/gdeltv2/lastupdate.txt`

**URL Patterns (v2)**:
```
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.export.CSV.zip
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.mentions.CSV.zip
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.gkg.csv.zip
```

**NGrams 3.0**:
```
http://data.gdeltproject.org/gdeltv3/webngrams/YYYYMMDDHHMMSS.webngrams.json.gz
```

**Update Frequency**: Every 15 minutes (:00, :15, :30, :45)

---

## 3. Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GDELTClient                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐ │
│  │   doc   │ │   geo   │ │ context │ │   tv    │ │   tv_ai   │ │
│  │  (API)  │ │  (API)  │ │  (API)  │ │  (API)  │ │   (API)   │ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └───────────┘ │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐ │
│  │ events  │ │mentions │ │   gkg   │ │ ngrams  │ │  lookups  │ │
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

### 3.2 Multi-Source Endpoints

For Events, Mentions, GKG, and NGrams:

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

### 3.3 Sync/Async Pattern

Async-first internally, sync wrapper for convenience:

```python
class GDELTClient:
    async def events_async(self, ...) -> EventStream:
        # Core implementation
        ...
    
    def events(self, ...) -> EventStream:
        return asyncio.run(self.events_async(...))
```

### 3.4 Streaming Architecture

```python
# Generator-based streaming
def query(self, filter: EventsFilter) -> EventStream:
    for file_url in self._get_file_urls(filter):
        for record in self._parse_file(file_url):
            yield record

# Terminal methods for materialization
class EventStream:
    def __iter__(self): ...
    def to_list(self) -> list[Event]: ...
    def to_dataframe(self) -> pd.DataFrame: ...  # Optional dep
```

---

## 4. Client API Reference

### 4.1 Client Initialization

```python
from gdelt import GDELTClient

# Basic usage
client = GDELTClient()

# Full configuration
client = GDELTClient(
    bigquery_project="my-gcp-project",
    cache_dir="~/.gdelt/cache",
    cache_ttl=3600,
    max_retries=3,
    timeout=30,
    fallback_to_bigquery=True,
    max_concurrent_requests=10,
)

# Context manager (recommended for async)
async with GDELTClient() as client:
    results = await client.events.query_async(filter)

# Sync context manager
with GDELTClient() as client:
    results = client.events.query(filter)
```

### 4.2 Namespaced Endpoints

```python
client.doc          # DOC 2.0 API (articles)
client.geo          # GEO 2.0 API (geographic)
client.context      # Context 2.0 API (sentence-level)
client.tv           # TV 2.0 API (captions)
client.tv_ai        # TV AI 2.0 API (visual)
client.events       # Events table (multi-source)
client.mentions     # Mentions table (multi-source)
client.gkg          # GKG table (multi-source)
client.ngrams       # Web NGrams 3.0 (multi-source)
client.lookups      # Reference data (CAMEO, themes, countries)
```

### 4.3 Filter Objects

#### EventsFilter

```python
from gdelt.filters import EventsFilter

filter = EventsFilter(
    start_date="2024-01-01",           # date, datetime, or str
    end_date="2024-01-31",
    countries=["US", "UK"],            # FIPS codes
    cameo_codes=["14"],                # Protest events
    actor1_country="RUS",
    actor2_country="UKR",
    min_goldstein=-10.0,
    max_goldstein=10.0,
    min_avg_tone=-5.0,
    quad_class=[3, 4],                 # Verbal/Material Conflict
    source_domains=["reuters.com"],
    include_translated=True,           # Include machine-translated
    deduplicate=True,                  # Apply deduplication
    dedupe_strategy="url_date_location",
)

# Reuse with modifications
filter_february = filter.with_dates("2024-02-01", "2024-02-29")
```

#### GKGFilter

```python
from gdelt.filters import GKGFilter

filter = GKGFilter(
    start_date="2024-01-01",
    end_date="2024-01-31",
    themes=["ENV_CLIMATECHANGE", "PROTEST"],
    persons=["Greta Thunberg"],
    organizations=["United Nations"],
    locations=["London"],
    min_tone=-5.0,
    source_domains=["bbc.com"],
    include_translated=True,
)
```

#### DocFilter

```python
from gdelt.filters import DocFilter

# Structured filter
filter = DocFilter(
    query="climate change protests",
    domain="reuters.com",
    source_country="US",
    source_lang="english",
    theme="ENV_CLIMATECHANGE",
    tone_min=-5.0,
    tone_max=5.0,
    timespan="3m",                     # or "7d", "24h", etc.
    mode="artlist",
    max_records=250,
    sort="datedesc",
)

# Raw query for power users
filter = DocFilter(
    raw_query='near10:"climate protests" domain:reuters.com tone<-3',
    mode="artlist",
)
```

#### NGramsFilter

```python
from gdelt.filters import NGramsFilter

filter = NGramsFilter(
    start_date="2024-01-01",
    end_date="2024-01-31",
    ngram="climate",                   # Single word/character
    bigram=("climate", "change"),      # Two-word phrase
    trigram=("United", "Nations", "Human"),
    language="en",
    min_position=0,                    # Article decile (0-90)
    max_position=30,                   # First 30% of articles
)
```

### 4.4 Query Methods

```python
# Events
events = client.events.query(filter)                    # Sync, returns EventStream
events = await client.events.query_async(filter)       # Async

# Explicit source selection
events = client.events.query(filter, source="bigquery")
events = client.events.query(filter, source="files")
events = client.events.query(filter, source="auto")    # Default

# Streaming iteration
for event in client.events.query(filter):
    process(event)

# Materialization
events_list = client.events.query(filter).to_list()
events_df = client.events.query(filter).to_dataframe()  # Requires pandas

# DOC API (API-only, no fallback)
articles = client.doc.search(filter)
timeline = client.doc.timeline(filter, mode="timelinevol")

# GKG
gkg_records = client.gkg.query(filter)

# NGrams
ngrams = client.ngrams.search(filter)
```

### 4.5 Lookups

```python
# CAMEO codes
client.lookups.cameo["14"]           # → "PROTEST"
client.lookups.cameo.get_description("142")  # → "Demonstrate or rally"
client.lookups.cameo.get_goldstein("14")     # → -6.5

# Themes
client.lookups.themes["ENV_CLIMATECHANGE"]   # → Theme info
client.lookups.themes.search("climate")       # → List of matching themes

# Countries (FIPS ↔ ISO conversion)
client.lookups.countries.fips_to_iso("US")   # → "USA"
client.lookups.countries.iso_to_fips("USA")  # → "US"
client.lookups.countries.get_name("US")      # → "United States"

# Validation (used internally, raises InvalidCodeError)
client.lookups.validate_cameo("999")         # Raises InvalidCodeError
client.lookups.validate_theme("INVALID")     # Raises InvalidCodeError
```

---

## 5. Data Models

### 5.1 Core Models

All models use Pydantic v2 for validation and serialization.

#### Location

```python
from pydantic import BaseModel
from typing import Optional

class Location(BaseModel):
    geo_type: int                      # 1=Country, 2=USState, 3=USCity, 4=WorldCity, 5=WorldState
    fullname: str                      # "City, State, Country"
    country_code: str                  # FIPS 2-char
    adm1_code: Optional[str]           # Country + ADM1 (e.g., "USTX")
    adm2_code: Optional[str]           # GAUL ADM2 or US county
    lat: Optional[float]
    lon: Optional[float]
    feature_id: Optional[str]          # GNS/GNIS ID (can be negative)
    
    def as_tuple(self) -> tuple[float, float]:
        """Return (lat, lon) tuple."""
        return (self.lat, self.lon)
    
    def as_wkt(self) -> str:
        """Return WKT POINT string for geopandas compatibility."""
        return f"POINT({self.lon} {self.lat})"
```

#### ToneScores

```python
class ToneScores(BaseModel):
    tone: float                        # -100 to +100 (positive minus negative)
    positive_score: float              # 0-100 (% positive words)
    negative_score: float              # 0-100 (% negative words)
    polarity: float                    # 0-100 (% emotionally charged)
    activity_density: float            # 0-100
    self_group_density: float          # 0-100
    word_count: int
```

#### EntityMention

```python
class EntityMention(BaseModel):
    name: str
    offset: Optional[int] = None       # Character offset, None for v1
```

### 5.2 Event Models

#### Event

```python
class Event(BaseModel):
    # Identifiers
    global_event_id: int
    date: date                         # Event date
    date_added: datetime               # When first recorded (UTC)
    source_url: Optional[str]
    
    # Actors
    actor1: Optional[Actor]
    actor2: Optional[Actor]
    
    # Action
    event_code: str                    # CAMEO code (string, not int!)
    event_base_code: str
    event_root_code: str
    quad_class: int                    # 1-4
    goldstein_scale: float             # -10 to +10
    
    # Metrics
    num_mentions: int
    num_sources: int
    num_articles: int
    avg_tone: float
    is_root_event: bool
    
    # Geography
    actor1_geo: Optional[Location]
    actor2_geo: Optional[Location]
    action_geo: Optional[Location]
    
    # Metadata
    version: int                       # 1 or 2
    is_translated: bool
    original_record_id: Optional[str]  # For translated records
    
class Actor(BaseModel):
    code: Optional[str]
    name: Optional[str]
    country_code: Optional[str]
    known_group_code: Optional[str]
    ethnic_code: Optional[str]
    religion1_code: Optional[str]
    religion2_code: Optional[str]
    type1_code: Optional[str]
    type2_code: Optional[str]
    type3_code: Optional[str]
```

#### Mention

```python
class Mention(BaseModel):
    global_event_id: int
    event_time: datetime
    mention_time: datetime
    mention_type: int                  # 1=WEB, 2=Citation, 3=CORE, etc.
    source_name: str
    identifier: str                    # URL, DOI, or citation
    sentence_id: int
    actor1_char_offset: Optional[int]
    actor2_char_offset: Optional[int]
    action_char_offset: Optional[int]
    in_raw_text: bool
    confidence: int                    # 10-100
    doc_length: int
    doc_tone: float
    translation_info: Optional[str]
```

### 5.3 GKG Models

```python
class GKGRecord(BaseModel):
    # Identifiers
    record_id: str                     # "YYYYMMDDHHMMSS-seq" or "-T" suffix
    date: datetime
    source_url: str
    source_name: str
    source_collection: int             # 1=WEB, 2=Citation, etc.
    
    # Extracted entities (normalized: offset=None for v1)
    themes: list[EntityMention]
    persons: list[EntityMention]
    organizations: list[EntityMention]
    locations: list[Location]
    
    # Tone
    tone: ToneScores
    
    # GCAM emotional dimensions
    gcam: dict[str, float]             # e.g., {"c2.14": 3.2, "c5.1": 0.85}
    
    # V2.1+ fields (empty lists for v1)
    quotations: list[Quotation]
    amounts: list[Amount]
    
    # Metadata
    version: int                       # 1 or 2
    is_translated: bool
    original_record_id: Optional[str]
    translation_info: Optional[str]

class Quotation(BaseModel):
    offset: int
    length: int
    verb: str
    quote: str

class Amount(BaseModel):
    amount: float
    object: str
    offset: int
```

### 5.4 Article Models (DOC API)

```python
class Article(BaseModel):
    url: str
    url_mobile: Optional[str]
    title: str
    seen_date: datetime
    social_image: Optional[str]
    domain: str
    language: str
    source_country: str
    tone: Optional[float]

class Timeline(BaseModel):
    data: list[TimelinePoint]
    mode: str
    
class TimelinePoint(BaseModel):
    date: datetime
    value: float
```

### 5.5 NGram Models

```python
class NGramRecord(BaseModel):
    date: datetime
    ngram: str                         # Word or character
    language: str                      # ISO 639-1/2
    segment_type: int                  # 1=space-delimited, 2=scriptio continua
    position: int                      # Article decile (0-90)
    pre_context: str                   # ~7 words before
    post_context: str                  # ~7 words after
    url: str
```

### 5.6 Result Containers

```python
from typing import TypeVar, Generic, Iterator

T = TypeVar('T')

class ResultStream(Generic[T]):
    """Lazy stream of results with terminal methods."""
    
    def __iter__(self) -> Iterator[T]:
        ...
    
    def to_list(self) -> list[T]:
        ...
    
    def to_dataframe(self) -> "pd.DataFrame":
        """Requires pandas. Raises ImportError if not installed."""
        ...
    
    def to_json(self, path: str) -> None:
        ...
    
    def to_csv(self, path: str) -> None:
        ...

class FetchResult(Generic[T]):
    """Result container with partial failure tracking."""
    data: list[T]
    failed: list[FailedRequest]
    
    @property
    def complete(self) -> bool:
        return len(self.failed) == 0
    
    @property
    def partial(self) -> bool:
        return len(self.failed) > 0 and len(self.data) > 0

class FailedRequest(BaseModel):
    url: str
    error: str
    timestamp: datetime
    retries: int
```

---

## 6. Configuration

### 6.1 Configuration Priority

1. **Constructor arguments** (highest priority)
2. **Environment variables**
3. **Config file** (`~/.gdelt/config.toml`)
4. **Defaults** (lowest priority)

### 6.2 Configuration Options

| Option | Constructor | Env Var | Default | Description |
|--------|-------------|---------|---------|-------------|
| `bigquery_project` | ✓ | `GDELT_BIGQUERY_PROJECT` | None | GCP project for BigQuery |
| `bigquery_credentials` | ✓ | `GDELT_BIGQUERY_CREDENTIALS` | ADC | Path to credentials JSON |
| `cache_dir` | ✓ | `GDELT_CACHE_DIR` | `~/.gdelt/cache` | Local cache directory |
| `cache_ttl` | ✓ | `GDELT_CACHE_TTL` | 3600 | Cache TTL for recent data (seconds) |
| `max_retries` | ✓ | `GDELT_MAX_RETRIES` | 3 | Max retry attempts |
| `timeout` | ✓ | `GDELT_TIMEOUT` | 30 | Request timeout (seconds) |
| `fallback_to_bigquery` | ✓ | `GDELT_FALLBACK_TO_BIGQUERY` | True | Use BQ on API failure |
| `max_concurrent_requests` | ✓ | `GDELT_MAX_CONCURRENT` | 10 | Concurrent file downloads |

### 6.3 Config File Format

```toml
# ~/.gdelt/config.toml

[bigquery]
project = "my-gcp-project"
credentials = "~/.config/gcloud/credentials.json"

[cache]
directory = "~/.gdelt/cache"
ttl = 3600

[requests]
max_retries = 3
timeout = 30
max_concurrent = 10
fallback_to_bigquery = true
```

### 6.4 Implementation

Using `pydantic-settings` for automatic priority handling:

```python
from pydantic_settings import BaseSettings

class GDELTSettings(BaseSettings):
    bigquery_project: str | None = None
    bigquery_credentials: str | None = None
    cache_dir: str = "~/.gdelt/cache"
    cache_ttl: int = 3600
    max_retries: int = 3
    timeout: int = 30
    fallback_to_bigquery: bool = True
    max_concurrent_requests: int = 10
    
    class Config:
        env_prefix = "GDELT_"
        toml_file = "~/.gdelt/config.toml"
```

---

## 7. Error Handling

### 7.1 Exception Hierarchy

```python
class GDELTError(Exception):
    """Base exception for all GDELT errors."""
    pass

class APIError(GDELTError):
    """Errors from GDELT REST APIs."""
    pass

class RateLimitError(APIError):
    """HTTP 429 - rate limited."""
    retry_after: int | None = None

class APIUnavailableError(APIError):
    """API endpoint unavailable (5xx, connection error)."""
    pass

class InvalidQueryError(APIError):
    """Invalid query parameters."""
    pass

class DataError(GDELTError):
    """Errors in data processing."""
    pass

class ParseError(DataError):
    """Failed to parse GDELT data."""
    raw_data: str | None = None

class ValidationError(DataError):
    """Data validation failed."""
    pass

class InvalidCodeError(ValidationError):
    """Invalid CAMEO code, theme, or country code."""
    code: str
    code_type: str  # "cameo", "theme", "country"

class ConfigurationError(GDELTError):
    """Invalid configuration."""
    pass

class BigQueryError(GDELTError):
    """BigQuery-related errors."""
    pass
```

### 7.2 Retry Strategy

Using `tenacity` with exponential backoff:

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((RateLimitError, APIUnavailableError)),
)
async def _fetch_with_retry(self, url: str) -> bytes:
    ...
```

### 7.3 Partial Failure Handling

```python
# Warn on partial failures, continue with available data
result = client.events.query(filter)

if result.partial:
    logger.warning(f"Partial results: {len(result.failed)} requests failed")
    for failure in result.failed:
        logger.warning(f"  {failure.url}: {failure.error}")

# User can still iterate over successful results
for event in result.data:
    process(event)
```

### 7.4 Fallback Behavior

```python
async def _query_with_fallback(self, filter: EventsFilter) -> EventStream:
    try:
        return await self._fetch_files(filter)
    except (RateLimitError, APIUnavailableError) as e:
        if self._config.fallback_to_bigquery and self._bq:
            logger.warning(f"Falling back to BigQuery: {e}")
            return await self._bq.query_events(filter)
        raise
```

---

## 8. Utilities

### 8.1 Deduplication

GDELT captures news reports, not unique events. ~20% redundancy exists.

#### Usage

```python
# Via query parameter (recommended)
events = client.events.query(filter, deduplicate=True)
events = client.events.query(filter, dedupe_strategy="aggressive")

# Via utility function
from gdelt.utils import deduplicate

events = client.events.query(filter)
deduped = deduplicate(events, strategy="url_date_location")
```

#### Strategies

| Strategy | Fields Matched | Reduction |
|----------|---------------|-----------|
| `url_only` | SOURCEURL | Minimal |
| `url_date` | SOURCEURL + SQLDATE | Light |
| `url_date_location` | SOURCEURL + SQLDATE + ActionGeo | Moderate (default) |
| `url_date_location_actors` | Above + Actor1 + Actor2 | Heavy |
| `aggressive` | Above + EventRootCode | Maximum (26-33% of original) |

#### Implementation

```python
def deduplicate(
    events: Iterable[Event],
    strategy: DedupeStrategy = "url_date_location",
) -> Iterator[Event]:
    """
    Deduplicate events using the specified strategy.
    
    Yields unique events based on the strategy's key fields.
    """
    seen: set[tuple] = set()
    key_fn = _get_key_function(strategy)
    
    for event in events:
        key = key_fn(event)
        if key not in seen:
            seen.add(key)
            yield event
```

### 8.2 Lookups

Bundled reference data (~1MB total):

```python
from gdelt.lookups import CAMEOCodes, GKGThemes, Countries

# Bundled with library
client.lookups.cameo      # CAMEO event codes
client.lookups.themes     # GKG theme taxonomy
client.lookups.countries  # FIPS/ISO country codes
client.lookups.goldstein  # Goldstein scale values
```

#### Helper Functions

```python
# CAMEO helpers
client.lookups.cameo.is_conflict("14")      # → True
client.lookups.cameo.is_cooperation("05")   # → True
client.lookups.cameo.get_quad_class("14")   # → 4

# Theme helpers
client.lookups.themes.get_category("ENV_CLIMATECHANGE")  # → "Environment"
client.lookups.themes.list_by_category("Health")         # → List of health themes

# Country helpers
client.lookups.countries.fips_to_iso("IZ")   # → "IRQ" (Iraq)
client.lookups.countries.iso_to_fips("IRQ")  # → "IZ"
```

### 8.3 Caching

```python
# Automatic caching of immutable historical data
# Recent data uses TTL-based caching

# Manual cache control
client.cache.clear()                    # Clear all
client.cache.clear(before="2024-01-01") # Clear old entries
client.cache.size()                     # Current cache size
```

---

## 9. Technical Constraints & Gotchas

### 9.1 Critical File Format Issue

**Files use TAB delimiters despite `.CSV` extension.**

```python
# CORRECT
df = pd.read_csv(file, sep='\t', header=None, encoding='utf-8')

# WRONG - corrupts data
df = pd.read_csv(file)  # Assumes comma delimiter
```

### 9.2 CAMEO Codes Must Be Strings

Leading zeros are significant: `"0251"` ≠ `251`

```python
# CORRECT
event_code: str = "0251"

# WRONG - loses leading zero
event_code: int = 251
```

### 9.3 FIPS Country Codes (Not ISO)

GDELT uses FIPS 10-4 codes: `US`, `UK`, `IZ` (Iraq)

ISO would be: `USA`, `GBR`, `IRQ`

Library provides conversion utilities.

### 9.4 Empty Fields

- Actor fields often empty (single-actor events, unclear actors)
- Don't assume Actor1/Actor2 populated
- FeatureIDs can be negative (signed integers as strings)

### 9.5 Date Handling

- Some records have partial dates: `YYYYMM00`, `YYYY0000`
- Translated records have `-T` suffix in IDs
- All timestamps are UTC

### 9.6 Data Quality

| Issue | Impact |
|-------|--------|
| ~20% redundancy | Use deduplication |
| ~55% actor accuracy | Don't rely on actor fields for precision |
| Geocoding errors | "Aberfeldy" → Australia instead of Scotland |
| Tone never negative | Despite -100 to +100 theoretical range |
| 500 char field truncation | GKG fields may be cut off |

### 9.7 API Constraints

| API | Time Window | Max Records | Notes |
|-----|-------------|-------------|-------|
| DOC 2.0 | 3 months | 250 | No pagination |
| GEO 2.0 | 7 days | 25,000 | Mode-dependent |
| Context 2.0 | 72 hours | 200 | |
| TV 2.0 | Full archive | 3,000 | |

### 9.8 Rate Limiting

- No published limits
- No rate limit headers
- Opaque 429 responses
- Adaptive throttling based on cluster load

### 9.9 BigQuery Cost

```sql
-- DANGEROUS: Scans entire 3.6TB GKG table (~$18)
SELECT * FROM `gdelt-bq.gdeltv2.gkg` LIMIT 100

-- SAFE: Use partitioned table with filter
SELECT * FROM `gdelt-bq.gdeltv2.gkg_partitioned`
WHERE _PARTITIONTIME >= '2024-01-01'
  AND _PARTITIONTIME < '2024-01-02'
LIMIT 100
```

### 9.10 No SLA

GDELT is free/academic. APIs may be unavailable. Some 15-minute files may be missing.

---

## 10. Design Decisions Log

### 10.1 Version Support

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Support GDELT v1? | Yes | Required for pre-2015 historical data |
| V1/V2 API surface | Unified | Normalize v1 → v2 format |
| GKG v2.0 vs v2.1 | v2.1 parsing | Handles both (v2.0 is subset) |
| Missing v1 fields | None/empty list | `offset=None`, `quotations=[]` |

### 10.2 Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Client structure | Single client, namespaced | `client.events`, `client.gkg`, etc. |
| Sync/async | Both, async-first | Async core, sync wrapper via `asyncio.run()` |
| HTTP client | httpx | Supports both sync/async from same codebase |
| Return types | Pydantic models | Validation, serialization, type safety |
| Streaming | Generators + terminal methods | Memory efficiency for large datasets |

### 10.3 Query Interface

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Query style | Filter objects | Serializable, reusable, cleaner types than fluent |
| DOC API raw query | Supported | Power users can use raw GDELT syntax |
| Date input types | date, datetime, str | Developer convenience |
| Timezone | Force UTC | GDELT is all UTC internally |
| Invalid codes | Reject with error | Query would fail anyway |

### 10.4 Data Access

| Decision | Choice | Rationale |
|----------|--------|-----------|
| BigQuery fallback | Yes, for resilience | Fallback on 429s/failures, not just historical |
| Source preference | Files → BigQuery | Files are free; BQ for fallback/large historical |
| Concurrency | Configurable, default 10 | Balance speed vs. rate limits |
| BigQuery auth | ADC + explicit path | Flexibility for different environments |

### 10.5 Output & Dependencies

| Decision | Choice | Rationale |
|----------|--------|-----------|
| pandas integration | Optional (`to_dataframe()`) | Don't force heavy dependency |
| Pydantic version | v2 only | Python 3.11+ means ship modern |
| Progress bars | tqdm (required) | Lightweight, standard |
| Logging | stdlib | Let users configure handlers |
| Lookups | Bundle with library | ~1MB, avoid network calls |

### 10.6 Error Handling

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Retry strategy | tenacity, exponential backoff | Industry standard |
| Partial failures | Warn + return partial | User can still work with available data |
| Circuit breaker | Skip for v1 | Adds complexity, GDELT outages are rare |

### 10.7 Utilities

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Deduplication | Query param + utility | Both entry points |
| Geo output | lat/lon + as_tuple() + as_wkt() | Prep for geopandas without requiring it |
| Translation handling | is_translated flag + filter | Expose metadata, allow filtering |

### 10.8 Deferred Decisions

| Topic | Status | Notes |
|-------|--------|-------|
| Package name | Open | `gdelt` exists but abandoned on PyPI |
| CLI | v2 | Library first |
| VGKG | v2 | Skip for initial release |

---

## 11. Future Work

### 11.1 Version 2 Candidates

- **pandas/geopandas integration**: `.to_geodataframe()` with geometry column
- **CLI interface**: `gdelt events --country US --start 2024-01-01`
- **VGKG support**: Visual GKG image analysis data
- **Visualization helpers**: Timeline plots, geographic maps
- **Pre-built datasets**: Materialized views of common queries

### 11.2 Potential Enhancements

- **Query caching**: Hash-based caching of query results
- **Schema updates**: LLM-assisted codebook parsing for new fields
- **Delta downloads**: Only fetch new data since last query
- **Webhook integration**: Subscribe to real-time updates

---

## Appendices

### A. Dependencies

```toml
[project]
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.25",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "tenacity>=8.0",
    "tqdm>=4.0",
]

[project.optional-dependencies]
bigquery = ["google-cloud-bigquery>=3.0"]
pandas = ["pandas>=2.0"]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "mypy>=1.0",
    "ruff>=0.1",
]
```

### B. File Schemas

#### B.1 Events v2 (61 columns)

```
GLOBALEVENTID, SQLDATE, MonthYear, Year, FractionDate,
Actor1Code, Actor1Name, Actor1CountryCode, Actor1KnownGroupCode,
Actor1EthnicCode, Actor1Religion1Code, Actor1Religion2Code,
Actor1Type1Code, Actor1Type2Code, Actor1Type3Code,
Actor2Code, Actor2Name, Actor2CountryCode, Actor2KnownGroupCode,
Actor2EthnicCode, Actor2Religion1Code, Actor2Religion2Code,
Actor2Type1Code, Actor2Type2Code, Actor2Type3Code,
IsRootEvent, EventCode, EventBaseCode, EventRootCode, QuadClass,
GoldsteinScale, NumMentions, NumSources, NumArticles, AvgTone,
Actor1Geo_Type, Actor1Geo_Fullname, Actor1Geo_CountryCode,
Actor1Geo_ADM1Code, Actor1Geo_ADM2Code, Actor1Geo_Lat, Actor1Geo_Long,
Actor1Geo_FeatureID,
Actor2Geo_Type, Actor2Geo_Fullname, Actor2Geo_CountryCode,
Actor2Geo_ADM1Code, Actor2Geo_ADM2Code, Actor2Geo_Lat, Actor2Geo_Long,
Actor2Geo_FeatureID,
ActionGeo_Type, ActionGeo_Fullname, ActionGeo_CountryCode,
ActionGeo_ADM1Code, ActionGeo_ADM2Code, ActionGeo_Lat, ActionGeo_Long,
ActionGeo_FeatureID,
DATEADDED, SOURCEURL
```

#### B.2 Events v1 (57 columns)

Same as v2 minus: `DATEADDED` is date-only, some minor field differences.

#### B.3 GKG v2.1 (27 columns)

```
GKGRECORDID, V2.1DATE, V2SOURCECOLLECTIONIDENTIFIER, V2SOURCECOMMONNAME,
V2DOCUMENTIDENTIFIER, V1COUNTS, V2.1COUNTS, V1THEMES, V2ENHANCEDTHEMES,
V1LOCATIONS, V2ENHANCEDLOCATIONS, V1PERSONS, V2ENHANCEDPERSONS,
V1ORGANIZATIONS, V2ENHANCEDORGANIZATIONS, V1.5TONE, V2.1DATES,
V2GCAM, V2.1SHARINGIMAGE, V2.1RELATEDIMAGES, V2.1SOCIALIMAGEEMBEDS,
V2.1SOCIALVIDEOEMBEDS, V2.1QUOTATIONS, V2.1ALLNAMES, V2.1AMOUNTS,
V2.1TRANSLATIONINFO, V2EXTRASXML
```

#### B.4 NGrams 3.0 (JSON fields)

```json
{
  "date": "2024-01-15T10:30:00Z",
  "ngram": "climate",
  "lang": "en",
  "type": 1,
  "pos": 20,
  "pre": "scientists warn about",
  "post": "change impacts on",
  "url": "https://example.com/article"
}
```

### C. Reference URLs

| Resource | URL |
|----------|-----|
| GDELT Project | https://www.gdeltproject.org |
| GDELT Blog | https://blog.gdeltproject.org |
| Event Codebook v2.0 | http://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf |
| GKG Codebook | http://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook-V2.1.pdf |
| CAMEO Codes | http://gdeltproject.org/data/lookups/CAMEO.eventcodes.txt |
| Country Codes | http://data.gdeltproject.org/api/v2/guides/LOOKUP-COUNTRIES.TXT |
| GKG Themes | http://data.gdeltproject.org/api/v2/guides/LOOKUP-GKGTHEMES.TXT |
| BigQuery Console | https://console.cloud.google.com/bigquery?project=gdelt-bq |

---

*Document generated: January 2026*  
*Specification version: 1.0.0-draft*
