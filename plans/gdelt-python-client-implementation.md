# feat: Implement GDELT Python Client Library v1.0

## Overview

Build a comprehensive Python client library for the GDELT (Global Database of Events, Language, and Tone) project. The library provides unified access to all 6 REST APIs, 3 database tables (via BigQuery/files), and NGrams dataset with modern Python patterns, type safety, and streaming support.

**Target**: Python 3.12+, async-first with sync wrappers for convenience

---

## Problem Statement

GDELT provides invaluable global event data but accessing it requires:
- Understanding 6 different REST APIs with varying query syntaxes
- Parsing TAB-delimited files (despite .CSV extension)
- Handling v1/v2 format differences (1979-2015 vs 2015+)
- Managing BigQuery for historical queries (cost-aware)
- Dealing with rate limits and missing files
- Converting FIPS country codes, CAMEO event codes, etc.

Existing Python libraries (gdelt, gdeltPyR) are abandoned and lack modern patterns.

---

## Proposed Solution

A single `GDELTClient` with namespaced endpoints providing:
- **Unified Interface**: `client.doc`, `client.events`, `client.gkg`, etc.
- **Automatic Fallback**: Files → BigQuery when rate limited
- **Streaming**: Memory-efficient async generators for large datasets
- **Validation**: Bundled lookups reject invalid codes immediately
- **Type Safety**: Dataclasses internally, Pydantic at API boundaries

---

## Technical Approach

### Architecture

```
src/py_gdelt/
├── __init__.py              # Public exports with __all__, py.typed marker
├── client.py                # GDELTClient class with endpoint namespaces
├── config.py                # GDELTSettings (pydantic-settings)
├── exceptions.py            # Exception hierarchy (9 classes per spec)
│
├── filters.py               # All filter Pydantic models (consolidated, validated)
│
├── models/                  # Data models
│   ├── __init__.py          # Public Pydantic models (API boundary)
│   ├── _internal.py         # Internal dataclasses (slots=True for performance)
│   ├── common.py            # Location, ToneScores, EntityMention, FetchResult
│   ├── events.py            # Event, Actor, Mention
│   ├── gkg.py               # GKGRecord, Quotation, Amount
│   ├── articles.py          # Article, Timeline, TimelinePoint
│   └── ngrams.py            # NGramRecord
│
├── endpoints/               # API endpoint handlers (separate for readability)
│   ├── __init__.py
│   ├── base.py              # BaseEndpoint with shared HTTP logic
│   ├── doc.py               # DocEndpoint (DOC 2.0 API)
│   ├── geo.py               # GeoEndpoint (GEO 2.0 API)
│   ├── context.py           # ContextEndpoint (Context 2.0 API)
│   ├── tv.py                # TVEndpoint, TVAIEndpoint
│   ├── events.py            # EventsEndpoint (multi-source)
│   ├── mentions.py          # MentionsEndpoint (multi-source)
│   ├── gkg.py               # GKGEndpoint (multi-source)
│   └── ngrams.py            # NGramsEndpoint (multi-source)
│
├── sources/                 # Data source handlers (clean separation)
│   ├── __init__.py
│   ├── fetcher.py           # DataFetcher - source selection + fallback
│   ├── files.py             # FileSource - download, extract, parse
│   ├── bigquery.py          # BigQuerySource - parameterized queries
│   └── api.py               # APISource - REST API calls
│
├── parsers/                 # File format parsers (consolidated by type)
│   ├── __init__.py          # Parser registry
│   ├── events.py            # Events parser (v1/v2 with version detection)
│   ├── mentions.py          # Mentions parser
│   ├── gkg.py               # GKG parser (v1/v2 with version detection)
│   └── ngrams.py            # NGrams JSON parser
│
├── lookups/                 # Bundled reference data
│   ├── __init__.py          # Lazy-loaded lookup access
│   ├── cameo.py             # CAMEOCodes (dict-based)
│   ├── themes.py            # GKGThemes (dict-based)
│   ├── countries.py         # Countries (FIPS↔ISO)
│   └── data/                # JSON lookup files (~1MB total)
│       ├── cameo_codes.json
│       ├── cameo_goldstein.json
│       ├── gkg_themes.json
│       └── countries.json
│
├── _security.py             # Path sanitization, URL validation, limits
│
├── cache.py                 # Cache management (TTL-based + immutable)
│
└── utils/                   # Utilities
    ├── __init__.py
    ├── dates.py             # Date parsing, UTC enforcement
    ├── dedup.py             # Deduplication (5 strategies)
    └── streaming.py         # ResultStream[T] with terminal methods
```

### Key Design Principles

1. **Filters**: Consolidated to `filters.py` with Pydantic models for immediate validation on construction
2. **Parsers**: Merged v1/v2 into single files with version detection
3. **Models**: Dataclasses internally (`_internal.py` with `slots=True`), Pydantic at API boundaries
4. **Streaming**: Simple async generators (prefetching deferred to v1.1 after profiling)
5. **Exceptions**: Granular hierarchy (9 classes) for actionable error handling
6. **Sync/Async**: Async-first with `_sync()` wrappers for convenience
7. **Deduplication**: 5 strategies from minimal to aggressive, with sensible default
8. **Lookups**: Rich helper methods (is_conflict, get_goldstein, search, etc.)
9. **Caching**: TTL-based for recent data, indefinite for historical (immutable)

### Data Model Details

#### Location Helpers
```python
class Location(BaseModel):
    lat: float | None
    lon: float | None
    # ... other fields

    def as_tuple(self) -> tuple[float, float]:
        """Return (lat, lon) tuple."""
        return (self.lat, self.lon)

    def as_wkt(self) -> str:
        """Return WKT POINT string for geopandas compatibility."""
        return f"POINT({self.lon} {self.lat})"
```

#### Translated Record Linking
```python
class Event(BaseModel):
    # ... other fields
    is_translated: bool
    original_record_id: str | None  # Links translated record to original
```

#### Internal Dataclasses (Performance)
```python
from dataclasses import dataclass

@dataclass(slots=True)  # Python 3.10+ - faster attribute access, less memory
class _RawEvent:
    """Internal representation during parsing - no validation overhead."""
    global_event_id: str
    sql_date: str  # Still string, validated when converting to Pydantic
    actor1_code: str | None
    actor2_code: str | None
    # ... other fields

    def to_event(self) -> Event:
        """Convert to public Pydantic model at API boundary."""
        return Event.model_validate(self.__dict__)
```

#### FetchResult (Partial Failure Tracking)
```python
@dataclass
class FetchResult(Generic[T]):
    """Result container with partial failure tracking."""
    data: list[T]
    failed: list[FailedRequest] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        return len(self.failed) == 0

    @property
    def partial(self) -> bool:
        return len(self.failed) > 0 and len(self.data) > 0

# Usage
result = client.events.query(filter)
if result.partial:
    logger.warning(f"Partial results: {len(result.failed)} requests failed")
    for failure in result.failed:
        logger.warning(f"  {failure.url}: {failure.error}")
# User can still iterate over successful results
for event in result.data:
    ...
```

#### ResultStream vs FetchResult: When to Use Each

| Use Case | Return Type | Why |
|----------|-------------|-----|
| **Streaming large datasets** | `AsyncIterator[T]` | Memory efficient, process as you go |
| **Batch with failure tracking** | `FetchResult[T]` | Know what failed, retry partial |
| **Terminal methods** | `ResultStream[T]` | Wraps iterator with `.to_list()`, `.to_dataframe()` |

```python
# Streaming (memory efficient)
async for event in client.events.stream(filter):
    process(event)

# Batch with failure tracking
result: FetchResult[Event] = await client.events.query(filter)
if not result.complete:
    handle_failures(result.failed)

# ResultStream wraps streaming with terminal methods
stream = client.events.query(filter)
df = await stream.to_dataframe()  # Materializes
```

### Security Architecture

Security is a first-class concern. The `_security.py` module provides:

#### SQL Injection Prevention
```python
# All BigQuery queries MUST use parameterized queries
from google.cloud import bigquery

query = """
    SELECT * FROM `gdelt-bq.gdeltv2.events_partitioned`
    WHERE Actor1CountryCode = @country
    AND _PARTITIONTIME >= @start_date
"""
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("country", "STRING", country_code),
        bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date),
    ]
)
```

#### Path Traversal Prevention
```python
def safe_cache_path(cache_dir: Path, filename: str) -> Path:
    """Sanitize filename and ensure it stays within cache directory."""
    safe_name = re.sub(r"[/\\]", "_", filename).replace("..", "__")
    cache_path = (cache_dir / safe_name).resolve()
    if not str(cache_path).startswith(str(cache_dir.resolve())):
        raise SecurityError(f"Path traversal detected: {filename}")
    return cache_path
```

#### Decompression Limits
```python
MAX_DECOMPRESSED_SIZE = 500 * 1024 * 1024  # 500MB
MAX_COMPRESSION_RATIO = 100  # Reject suspicious ratios (zip bombs)
```

#### Input Validation
- All filter inputs validated against bundled lookups before use
- CAMEO codes, country codes, themes checked against allowlists
- Date ranges capped to prevent runaway queries

#### HTTPS Enforcement
```python
ALLOWED_HOSTS = {"api.gdeltproject.org", "data.gdeltproject.org"}
# All connections must use HTTPS with certificate verification
```

#### Rate Limit Respect (Client-Side)

As a client library, we don't implement server-side rate limiting. Instead, we **respect** GDELT's rate limits:

```python
# Configurable concurrency (default: sensible limits)
MAX_CONCURRENT_DOWNLOADS = 10  # Don't overwhelm file server
MAX_CONCURRENT_API_REQUESTS = 5  # Respect API rate limits

# Exponential backoff on 429 responses
@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
)
async def _make_request(self, url: str) -> Response:
    ...

# Honor Retry-After header when provided
if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", 60))
    raise RateLimitError(retry_after=retry_after)
```

**Note**: GDELT's rate limits are undocumented and vary. We use conservative defaults and automatic fallback to BigQuery when rate limited.

---

### Utilities

#### Deduplication Strategies

GDELT captures news reports, not unique events. ~20% redundancy exists. Provide multiple strategies:

```python
from enum import StrEnum

class DedupeStrategy(StrEnum):
    """Deduplication strategies - use StrEnum for type safety."""
    URL_ONLY = "url_only"
    URL_DATE = "url_date"
    URL_DATE_LOCATION = "url_date_location"  # Default
    URL_DATE_LOCATION_ACTORS = "url_date_location_actors"
    AGGRESSIVE = "aggressive"

# Via query parameter (recommended)
events = client.events.query(filter, deduplicate=True)  # Uses default
events = client.events.query(filter, dedupe_strategy=DedupeStrategy.AGGRESSIVE)

# Via utility function
from gdelt.utils import deduplicate
deduped = deduplicate(events, strategy=DedupeStrategy.URL_DATE_LOCATION)
```

| Strategy | Fields Matched | Reduction |
|----------|---------------|-----------|
| `URL_ONLY` | SOURCEURL | Minimal |
| `URL_DATE` | SOURCEURL + SQLDATE | Light |
| `URL_DATE_LOCATION` | SOURCEURL + SQLDATE + ActionGeo | Moderate (**default**) |
| `URL_DATE_LOCATION_ACTORS` | Above + Actor1 + Actor2 | Heavy |
| `AGGRESSIVE` | Above + EventRootCode | Maximum (26-33% of original) |

#### Lookup Helper Methods

```python
# CAMEO helpers
client.lookups.cameo["14"]                    # → "PROTEST"
client.lookups.cameo.get_description("142")   # → "Demonstrate or rally"
client.lookups.cameo.get_goldstein("14")      # → -6.5
client.lookups.cameo.is_conflict("14")        # → True
client.lookups.cameo.is_cooperation("05")     # → True
client.lookups.cameo.get_quad_class("14")     # → 4

# Theme helpers
client.lookups.themes["ENV_CLIMATECHANGE"]             # → Theme info
client.lookups.themes.search("climate")                 # → List of matching themes
client.lookups.themes.get_category("ENV_CLIMATECHANGE") # → "Environment"
client.lookups.themes.list_by_category("Health")        # → List of health themes

# Country helpers (FIPS ↔ ISO)
client.lookups.countries.fips_to_iso("US")    # → "USA"
client.lookups.countries.iso_to_fips("USA")   # → "US"
client.lookups.countries.get_name("US")       # → "United States"
client.lookups.countries.fips_to_iso("IZ")    # → "IRQ" (Iraq uses IZ in FIPS)

# Validation (used internally, raises InvalidCodeError)
client.lookups.validate_cameo("999")          # Raises InvalidCodeError
client.lookups.validate_theme("INVALID")      # Raises InvalidCodeError
```

#### Cache Management

```python
# Automatic caching of immutable historical data
# Recent data uses TTL-based caching (default: 1 hour)

# Manual cache control
client.cache.clear()                     # Clear all
client.cache.clear(before="2024-01-01")  # Clear old entries
client.cache.size()                      # Current cache size in bytes
```

**Cache behavior:**
- Historical files (>30 days old): Cached indefinitely (immutable)
- Recent files: TTL-based (configurable, default 1 hour)
- Master file lists: Short TTL (5 minutes)

---

### Parallelization Strategy

Use `@agent-python-coder` subagents to parallelize independent work streams. Each stream can be assigned to a separate agent.

#### Phase 1: Core Infrastructure (7 parallel streams)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ SEQUENTIAL: Project setup (ruff, mypy, pyproject.toml)                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Agent 1         │     │ Agent 2         │     │ Agent 3         │
│ config.py       │     │ exceptions.py   │     │ _security.py    │
│ (GDELTSettings) │     │ (9 classes)     │     │ (path, URL)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
          │                         │                         │
          ▼                         ▼                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Agent 4         │     │ Agent 5         │     │ Agent 6         │
│ lookups/        │     │ cache.py        │     │ utils/dedup.py  │
│ (CAMEO, themes) │     │ (TTL + immut)   │     │ (5 strategies)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Agent 7: models/common.py (Location, ToneScores, FetchResult)           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ SEQUENTIAL: filters.py (depends on lookups for validation)              │
│             utils/streaming.py (depends on models)                      │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Phase 2: REST API Endpoints (4 parallel streams after base)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ SEQUENTIAL: BaseEndpoint (shared HTTP client, retry logic)              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
     ┌──────────────┬───────────────┼───────────────┬──────────────┐
     ▼              ▼               ▼               ▼              ▼
┌─────────┐  ┌─────────┐    ┌─────────────┐  ┌─────────┐  ┌──────────────┐
│ Agent 1 │  │ Agent 2 │    │   Agent 3   │  │ Agent 4 │  │   Agent 5    │
│ doc.py  │  │ geo.py  │    │ context.py  │  │  tv.py  │  │ articles.py  │
│ (DOC)   │  │ (GEO)   │    │ (Context)   │  │(TV+TVAI)│  │  (models)    │
└─────────┘  └─────────┘    └─────────────┘  └─────────┘  └──────────────┘
```

#### Phase 3: File Parsers & Sources (5 parallel streams)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ SEQUENTIAL: models/_internal.py (shared dataclasses for all parsers)    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
     ┌──────────────┬───────────────┼───────────────┬──────────────┐
     ▼              ▼               ▼               ▼              ▼
┌─────────┐  ┌───────────┐  ┌─────────────┐  ┌───────────┐  ┌──────────┐
│ Agent 1 │  │  Agent 2  │  │   Agent 3   │  │  Agent 4  │  │ Agent 5  │
│events.py│  │mentions.py│  │   gkg.py    │  │ ngrams.py │  │ files.py │
│(v1/v2)  │  │           │  │(v1/v2+XML) │  │  (JSON)   │  │(FileSource)│
└─────────┘  └───────────┘  └─────────────┘  └───────────┘  └──────────┘
```

#### Phase 4: BigQuery Integration (sequential)

Single agent - `bigquery.py` is cohesive unit with parameterized queries, credential handling, streaming.

#### Phase 5: Multi-Source Endpoints (4 parallel streams after fetcher)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ SEQUENTIAL: DataFetcher (source selection, fallback logic)              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
     ┌──────────────┬───────────────┼───────────────┬──────────────┐
     ▼              ▼               ▼               ▼              │
┌─────────┐  ┌───────────┐  ┌─────────────┐  ┌───────────┐        │
│ Agent 1 │  │  Agent 2  │  │   Agent 3   │  │  Agent 4  │        │
│events.py│  │mentions.py│  │   gkg.py    │  │ ngrams.py │        │
│         │  │           │  │             │  │           │        │
└─────────┘  └───────────┘  └─────────────┘  └───────────┘        │
     │              │               │               │              │
     └──────────────┴───────────────┴───────────────┴──────────────┘
                                    │
                                    ▼
                            (all 4 parallel)
```

#### Phase 6: Integration (sequential)

Single agent - `client.py` wires everything together, requires all prior phases.

#### Summary: Parallelization Opportunities

| Phase | Sequential Tasks | Parallel Streams | Max Agents |
|-------|------------------|------------------|------------|
| 1 | Project setup, filters.py, streaming.py | config, exceptions, security, lookups, cache, dedup, models | **7** |
| 2 | BaseEndpoint | doc, geo, context, tv, articles | **5** |
| 3 | _internal.py | events, mentions, gkg, ngrams, files | **5** |
| 4 | - | (single unit) | **1** |
| 5 | DataFetcher | events, mentions, gkg, ngrams | **4** |
| 6 | - | (single unit) | **1** |

**Total potential parallel agents**: 23 (but constrained by phase dependencies)
**Recommended approach**: Run each phase with max parallelism, then move to next phase.

---

### Implementation Phases

#### Phase 1: Core Infrastructure (Foundation)

**Tasks:**
1. Configure project tooling (ruff, mypy strict, pytest-asyncio)
2. Implement `GDELTSettings` with pydantic-settings (env vars + TOML config file)
3. Build exception hierarchy (9 classes per spec):
   - `GDELTError` (base)
   - `APIError` → `RateLimitError`, `APIUnavailableError`, `InvalidQueryError`
   - `DataError` → `ParseError`, `ValidationError` → `InvalidCodeError`
   - `ConfigurationError`
   - `BigQueryError`
4. Create base HTTP client with retry logic (tenacity)
5. Implement security module (`_security.py`)
6. Build `ResultStream[T]` with terminal methods (simple async generator)
7. Bundle lookup data (CAMEO, themes, countries) with lazy loading
8. Create consolidated filter Pydantic models (`filters.py`)

**Key Files:**
- `src/py_gdelt/config.py`
- `src/py_gdelt/exceptions.py`
- `src/py_gdelt/_security.py`
- `src/py_gdelt/filters.py`
- `src/py_gdelt/cache.py`
- `src/py_gdelt/utils/streaming.py`
- `src/py_gdelt/utils/dedup.py`
- `src/py_gdelt/lookups/`

**Success Criteria:**
- [ ] `GDELTSettings` loads from env vars (GDELT_ prefix) AND optional TOML file
- [ ] Config constructor accepts `config_path: Path | None` for TOML loading
- [ ] Exceptions have proper `__init__` with context attributes (9 classes)
- [ ] RateLimitError includes `retry_after` attribute when available
- [ ] Security utilities handle path sanitization, URL validation
- [ ] ResultStream supports async iteration, `.to_list()`, `.to_dataframe()`
- [ ] Filter models validate CAMEO/country codes on construction
- [ ] Lookups lazy-load via `@cached_property` and validate codes
- [ ] Lookup helpers: `is_conflict()`, `get_goldstein()`, `search()`, `fips_to_iso()`, etc.
- [ ] Cache module with TTL-based + immutable caching strategies
- [ ] Deduplication utility with 5 strategies (default: `url_date_location`)
- [ ] Location model with `as_tuple()` and `as_wkt()` for geopandas prep
- [ ] Event/GKG models include `original_record_id` for translated record linking
- [ ] FetchResult with partial failure tracking (`complete`, `partial`, `failed`)
- [ ] `py.typed` marker file exists
- [ ] All modules have `__all__` exports

#### Phase 2: REST API Endpoints

**Tasks:**
1. Implement `BaseEndpoint` with httpx async client (HTTPS only)
2. Build `DocEndpoint` (DOC 2.0 API) with all output modes
3. Build `GeoEndpoint` (GEO 2.0 API)
4. Build `ContextEndpoint` (Context 2.0 API)
5. Build `TVEndpoint` and `TVAIEndpoint`
6. Implement Pydantic models for API responses (boundary models)
7. Add URL validation against allowed hosts

**Key Files:**
- `src/py_gdelt/endpoints/base.py`
- `src/py_gdelt/endpoints/doc.py`
- `src/py_gdelt/endpoints/geo.py`
- `src/py_gdelt/endpoints/context.py`
- `src/py_gdelt/endpoints/tv.py`
- `src/py_gdelt/models/articles.py`

**Success Criteria:**
- [ ] DOC API returns Article/Timeline Pydantic models
- [ ] All APIs handle rate limits with exponential backoff retry
- [ ] All HTTP connections use HTTPS with cert verification
- [ ] URL parameters properly encoded (no injection)
- [ ] Async methods named `query()`, sync wrappers named `query_sync()`
- [ ] Sync wrappers use `asyncio.run()` internally

#### Phase 3: File Parsers & Sources

**Tasks:**
1. Implement Events parser with version detection (v1: 57 cols, v2: 61 cols)
2. Implement Mentions parser
3. Implement GKG parser with version detection (v1/v2.1, complex delimiters)
4. Build `FileSource` with secure ZIP extraction (size limits, ratio checks)
5. Implement master file list fetching (short TTL cache)
6. Add `defusedxml` for GKG XML parsing
7. Implement internal dataclasses for parsed records

**Key Files:**
- `src/py_gdelt/parsers/events.py` (consolidated v1/v2)
- `src/py_gdelt/parsers/mentions.py`
- `src/py_gdelt/parsers/gkg.py` (consolidated v1/v2)
- `src/py_gdelt/sources/files.py`
- `src/py_gdelt/models/_internal.py`

**Success Criteria:**
- [ ] All parsers handle TAB delimiters correctly
- [ ] CAMEO codes preserved as strings (leading zeros)
- [ ] Version detected from column count, normalization applied
- [ ] Translated records detected (`is_translated=True`)
- [ ] GKG GCAM scores parsed into dict
- [ ] XML parsed with defusedxml (entity expansion protection)
- [ ] ZIP extraction enforces size and ratio limits
- [ ] Line/field length limits prevent memory exhaustion

#### Phase 4: BigQuery Integration

**Tasks:**
1. Build `BigQuerySource` with **parameterized queries only**
2. Implement cost-aware query construction (partitioned tables required)
3. Add credential validation (ADC preferred, explicit path as fallback)
4. Build BigQuery result streaming with async wrapper
5. Create query builder with column allowlist validation

**Key Files:**
- `src/py_gdelt/sources/bigquery.py`

**Success Criteria:**
- [ ] **ALL queries use parameterized queries** (no string formatting)
- [ ] Only `_partitioned` tables used with mandatory date filters
- [ ] Column names validated against explicit allowlist
- [ ] Credentials validated on first use, never logged
- [ ] Results stream via `run_in_executor` (BigQuery client is sync)
- [ ] Credential file paths validated (no traversal)

#### Phase 5: Multi-Source Endpoints & Fallback

**Tasks:**
1. Build `DataFetcher` with source selection logic:
   - Files are **always primary** (free, no credentials needed)
   - BigQuery is **fallback only** (on 429/error, if credentials configured)
2. Implement automatic fallback (files → BigQuery on 429/error)
3. Build `EventsEndpoint` using DataFetcher
4. Build `MentionsEndpoint`
5. Build `GKGEndpoint`
6. Build `NGramsEndpoint`
7. Implement configurable error policy with sensible default
8. Add logging for fallback events (structured logging)

**Key Files:**
- `src/py_gdelt/sources/fetcher.py`
- `src/py_gdelt/endpoints/events.py`
- `src/py_gdelt/endpoints/mentions.py`
- `src/py_gdelt/endpoints/gkg.py`
- `src/py_gdelt/endpoints/ngrams.py`

**Success Criteria:**
- [ ] Source selection: files first (primary), BigQuery only as fallback
- [ ] Fallback triggers on 429 or connection errors (only if BQ credentials configured)
- [ ] Fallback logged at WARNING level (not silent)
- [ ] Default error policy: warn and continue
- [ ] Internal dataclasses converted to Pydantic at yield boundary

#### Phase 6: Main Client & Integration

**Tasks:**
1. Build `GDELTClient` with endpoint namespaces
2. Implement async context manager (`__aenter__`/`__aexit__`)
3. Wire up HTTP client with ownership tracking
4. Comprehensive integration tests (with VCR/cassettes)
5. Documentation and examples
6. Security-focused code review

**Key Files:**
- `src/py_gdelt/client.py`
- `src/py_gdelt/__init__.py`
- `tests/integration/`
- `README.md`

**Success Criteria:**
- [ ] `async with GDELTClient() as client:` works
- [ ] All endpoints accessible via namespace (`client.events`, etc.)
- [ ] Client owns HTTP lifecycle (closes on exit)
- [ ] Integration tests use recorded responses (VCR pattern)
- [ ] README includes security best practices section

---

## Alternative Approaches Considered

### 1. Sync/Async Strategy

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Async-first + sync wrappers** | Works for most users, simple | Jupyter needs `nest_asyncio` | **Selected** |
| `unasync` codegen | Best Jupyter support | Build complexity | Deferred to v2 |
| Async-only | Fastest to ship | Excludes scripts/REPL users | Rejected |

**Rationale**: Provide both async and sync APIs. Async is primary (`async def query()`). Sync wrappers use `asyncio.run()` for simple scripts and CLI usage. Jupyter users must install `nest_asyncio` or use async directly. Document this clearly. v2 may add `unasync` codegen for true sync without the asyncio overhead.

**Sync wrapper pattern:**

⚠️ **Note**: `asyncio.run()` per-call is problematic (creates new event loop, breaks in Jupyter/FastAPI). Use `anyio` for robust sync/async duality:

```python
# Add anyio to dependencies (thin asyncio wrapper, same as httpx uses)
import anyio

class GDELTClient:
    """Async-first client with sync convenience methods."""

    async def query(self, filters: EventFilter) -> AsyncIterator[Event]:
        """Primary async API - use this in async contexts."""
        ...

    def query_sync(self, filters: EventFilter) -> list[Event]:
        """Sync wrapper using anyio - works in nested event loops."""
        return anyio.from_thread.run_sync(
            lambda: anyio.run(self._collect_async, filters)
        )
```

Alternative: Separate `GDELTClientSync` class with background thread + persistent event loop for connection reuse.

### 2. HTTP Client Lifecycle

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Global singleton | Max connection reuse | Lifecycle complexity | Rejected |
| **Instance-owned with DI** | Clean lifecycle, testable | No cross-client sharing | **Selected** |

**Rationale**: Accept optional `httpx.AsyncClient` in constructor for testing, create internally if not provided. Track ownership to know when to close.

### 3. Fallback Logic Location

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| In endpoint classes | Simple | Hard to reuse/test | Rejected |
| **DataFetcher pattern** | Centralized, testable | Extra abstraction | **Selected** |

**Rationale**: All multi-source endpoints need the same fallback logic. Centralizing in `DataFetcher` avoids duplication and enables unit testing without mocking entire endpoints.

**DataFetcher with Dependency Injection:**
```python
class DataFetcher:
    """Orchestrates source selection and fallback."""

    def __init__(
        self,
        file_source: FileSource,
        bigquery_source: BigQuerySource | None = None,
        *,
        fallback_enabled: bool = True,
    ) -> None:
        self._file = file_source
        self._bq = bigquery_source
        self._fallback = fallback_enabled and bigquery_source is not None

    async def fetch(
        self,
        filter: EventFilter,
        parser: Parser[T],
    ) -> AsyncIterator[T]:
        try:
            async for record in self._file.fetch(filter, parser):
                yield record
        except RateLimitError as e:
            if self._fallback:
                logger.warning(f"Rate limited, falling back to BigQuery: {e}")
                async for record in self._bq.fetch(filter, parser):
                    yield record
            else:
                raise
```

**Parser Protocol:**
```python
from typing import Protocol, TypeVar

T = TypeVar("T")

class Parser(Protocol[T]):
    """Interface for file format parsers."""

    def parse(self, raw: bytes) -> Iterator[T]:
        """Parse raw bytes into records."""
        ...

    def detect_version(self, header: bytes) -> int:
        """Detect format version from header (1 or 2)."""
        ...
```

### 4. Streaming Strategy

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Simple async generator** | Low memory, simple, correct | Network idle during processing | **Selected** |
| Queue-based prefetch | Downloads next while processing current | Cancellation complexity, harder to reason about | Deferred to v1.1 |

**Rationale**: Start with simple async generators. They're easier to reason about, test, and debug. Profile real-world usage in v1.0, then add prefetching in v1.1 if benchmarks show meaningful improvement. Premature optimization is the root of all evil.

---

## Acceptance Criteria

### Functional Requirements

- [ ] All 6 REST APIs accessible (DOC, GEO, Context, TV, TV AI, GKG GeoJSON)
- [ ] Events, Mentions, GKG queryable from files AND BigQuery
- [ ] NGrams 3.0 queryable from files AND BigQuery
- [ ] Filters validate against bundled lookups
- [ ] Invalid CAMEO/theme/country codes rejected immediately
- [ ] v1 data (pre-2015) normalized to v2 format
- [ ] Translated records identified via `is_translated` flag
- [ ] Deduplication available via filter parameter or utility
- [ ] FIPS↔ISO country code conversion available

### Non-Functional Requirements

- [ ] Memory stays constant during streaming (generator-based)
- [ ] Concurrent file downloads (default 10)
- [ ] Retry with exponential backoff on failures
- [ ] Configurable error policy (`on_error='raise'|'warn'|'skip'`)
- [ ] Progress bars for long operations
- [ ] Type hints throughout (mypy strict mode passes)
- [ ] Test coverage >80%

### Quality Gates

**Code Quality:**
- [ ] `ruff check` passes with no errors
- [ ] `mypy --strict` passes
- [ ] `pytest` passes with >80% coverage
- [ ] All public APIs documented with docstrings
- [ ] Modern type hints used (`str | None` not `Optional[str]`)

**Security Gates:**
- [ ] All BigQuery queries use parameterized queries (code review verified)
- [ ] All user inputs validated against allowlists before use
- [ ] Path traversal tests pass for cache operations
- [ ] HTTPS enforced for all HTTP connections (no `http://`)
- [ ] XML parsing uses `defusedxml`
- [ ] Decompression size limits implemented and tested
- [ ] No credentials logged or stored in plaintext
- [ ] `pip-audit` or `safety` check passes with no high/critical vulnerabilities
- [ ] Security-focused code review completed before release

---

## Success Metrics

1. **Correctness**: All GDELT file formats parse without data corruption
2. **Reliability**: Fallback triggers correctly on rate limits (when BQ configured)
3. **Performance**: Streaming maintains constant memory regardless of result size
4. **Usability**: New users can query events in <10 lines of code
5. **Maintainability**: Adding new GDELT API requires <100 lines

---

## Dependencies & Prerequisites

### Required Dependencies (already in pyproject.toml)
- `httpx>=0.28.1` - Async HTTP client
- `pydantic>=2.12.5` - Data validation (API boundaries)
- `pydantic-settings>=2.12.0` - Configuration
- `tenacity>=9.1.2` - Retry logic
- `tqdm>=4.67.1` - Progress bars
- `defusedxml>=0.7.1` - Secure XML parsing (GKG V2EXTRASXML)
- `anyio>=4.0` - **NEW: Robust sync/async wrapper** (handles nested event loops)

### Optional Dependencies
- `google-cloud-bigquery>=3.0` - BigQuery support
- `pandas>=2.0` - DataFrame export

### Development Dependencies (add to pyproject.toml)
- `pytest>=7.0`, `pytest-asyncio>=0.21`, `pytest-cov>=4.0`
- `mypy>=1.0`, `ruff>=0.1`
- `pip-audit` - Vulnerability scanning
- `respx>=0.20` - HTTP mocking for tests

### External Requirements
- GDELT APIs must be accessible (no auth required)
- BigQuery requires GCP project + credentials (optional)

---

## Risk Analysis & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GDELT API changes | Low | High | Version-pin endpoints, add response validation |
| Rate limiting unpredictable | Medium | Medium | Adaptive throttling, BigQuery fallback |
| BigQuery costs surprise users | Medium | High | Document clearly, consider dry-run mode |
| GKG delimiter edge cases | Medium | Medium | Comprehensive parser tests with real data |
| Jupyter async issues | Low | Medium | Sync wrappers work outside Jupyter; document `nest_asyncio` for Jupyter |

---

## Future Considerations (v2+)

1. **True sync API** via `unasync` codegen (avoid asyncio overhead for sync users)
2. **CLI interface**: `gdelt events --country US --start 2024-01-01`
3. **GeoPandas integration**: `.to_geodataframe()` with geometry column
4. **Query cost estimation**: Estimate BigQuery bytes scanned before execution
5. **VGKG support**: Visual GKG image analysis data
6. **Visualization helpers**: Timeline plots, geographic maps
7. **Pre-built datasets**: Materialized views of common queries
8. **Webhook integration**: Subscribe to real-time GDELT updates

---

## Documentation Plan

1. **README.md**: Quick start, installation, basic examples
2. **API Reference**: Auto-generated from docstrings (mkdocs/sphinx)
3. **User Guide**: Common patterns, filter examples, streaming best practices
4. **Migration Guide**: From gdelt/gdeltPyR libraries
5. **Contributing Guide**: Development setup, testing, PR process

---

## References & Research

### Internal References
- API Specification: `plans/api_spec_v1.md`
- Events Codebook: `gdelt_docs/gdelt_event_cookbook.md`
- GKG Codebook: `gdelt_docs/gkg_cookbook.md`
- Project Config: `pyproject.toml`

### External References
- GDELT Project: https://www.gdeltproject.org
- Event Codebook v2.0: http://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf
- GKG Codebook v2.1: http://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook-V2.1.pdf
- CAMEO Manual: http://gdeltproject.org/data/documentation/CAMEO.Manual.1.1b3.pdf
- GCAM Codebook: http://data.gdeltproject.org/documentation/GCAM-MASTERCODEBOOK.xlsx

### Framework Documentation
- httpx: https://www.python-httpx.org/
- Pydantic v2: https://docs.pydantic.dev/
- pydantic-settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- tenacity: https://tenacity.readthedocs.io/
- tqdm: https://tqdm.github.io/

---

## Key Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Sync/Async | Async-first + sync wrappers (anyio) | Scripts get sync; anyio handles nested loops |
| HTTP Client | Owned with optional DI | Testability + clean lifecycle |
| Source Selection | Files primary, BQ fallback | Files are free; BQ only when configured and files fail |
| Fallback Logic | DataFetcher with DI | Centralized, testable, accepts sources via constructor |
| Parser Interface | Protocol[T] | Extensible, type-safe, enables new formats |
| Streaming | Simple async generators | Deferred prefetching to v1.1 after profiling |
| Lookups | Lazy `@cached_property` | No startup penalty |
| Error Policy | Configurable, default `warn` | Sensible default, user can override |
| Validation | On filter creation (Pydantic) | Immediate feedback on typos, built-in validation |
| Models | Dataclasses (slots=True) internal, Pydantic at boundary | Performance + type safety |
| Filters | Consolidated Pydantic models | Validation on construction, simpler than 8 files |
| Exceptions | Granular hierarchy | RateLimitError vs APIError enables targeted retry logic |
| Config | Env vars + TOML file | Flexible for both scripts and project configs |
| Parsers | Version detection in single file | Less duplication than v1/v2 split |
| Deduplication | StrEnum with 5 strategies | Type-safe, IDE autocomplete, default `URL_DATE_LOCATION` |
| Caching | TTL-based recent + indefinite historical | Historical data is immutable; recent changes often |
| Geo output | `Location.as_tuple()` + `as_wkt()` | Prep for geopandas without requiring it |
| Partial failures | FetchResult with `partial`, `failed` | User can still work with available data |
| Translation linking | `original_record_id` on Event/GKG | Track which translated records map to originals |
| Security | First-class concern | Parameterized queries, path sanitization, defusedxml |

---

## Implementation Checklist

### Phase 1: Core Infrastructure
- [x] Configure ruff + mypy strict in pyproject.toml
- [x] Add `defusedxml` to dependencies
- [x] Implement `GDELTSettings` class (env vars + TOML config file)
- [x] Build exception hierarchy (9 classes per spec)
- [x] Create `_security.py` module
- [x] Create consolidated `filters.py` with Pydantic models
- [x] Build `ResultStream[T]` and `FetchResult[T]` in models
- [x] Build cache module with TTL-based + immutable strategies
- [x] Build deduplication utility with 5 strategies
- [x] Bundle lookup data (CAMEO, themes, countries)
- [x] Implement lazy-loaded lookups with helper methods
- [x] Build common models (Location with `as_tuple()`/`as_wkt()`, ToneScores)
- [x] Add `py.typed` marker and `__all__` exports

### Phase 2: REST API Endpoints
- [x] Build `BaseEndpoint` with httpx (HTTPS only)
- [x] Implement `DocEndpoint` (async + sync wrappers)
- [x] Implement `GeoEndpoint` (async + sync wrappers)
- [x] Implement `ContextEndpoint` (async + sync wrappers)
- [x] Implement `TVEndpoint` and `TVAIEndpoint` (async + sync wrappers)
- [x] Create Pydantic models for API responses
- [x] Add URL validation against allowed hosts

### Phase 3: File Parsers & Sources
- [x] Build Events parser (v1/v2 with version detection)
- [x] Build Mentions parser
- [x] Build GKG parser (v1/v2 with version detection, defusedxml)
- [x] Build NGrams JSON parser
- [x] Implement `FileSource` with secure ZIP extraction
- [x] Add decompression size/ratio limits
- [x] Add line/field length limits
- [x] Create internal dataclasses (`models/_internal.py`)
- [x] Include `original_record_id` parsing for translated records

### Phase 4: BigQuery Integration
- [x] Build `BigQuerySource`
- [x] Implement parameterized queries (NO string formatting)
- [x] Add column allowlist validation
- [x] Add credential path validation
- [x] Build result streaming via `run_in_executor`

### Phase 5: Multi-Source Endpoints
- [x] Build `DataFetcher` (files primary, BQ fallback only when configured)
- [x] Implement fallback logic (files → BigQuery on 429/error)
- [x] Build `EventsEndpoint` with dedup support
- [x] Build `MentionsEndpoint`
- [x] Build `GKGEndpoint`
- [x] Build `NGramsEndpoint`
- [x] Implement configurable error policy
- [x] Add structured logging for fallback events

### Phase 6: Integration
- [x] Build `GDELTClient` with async context manager
- [x] Wire endpoint namespaces
- [x] Write integration tests (with respx mocking)
- [x] Write README with security best practices
- [x] Run `pip-audit` security scan (no vulnerabilities found)
- [x] Security-focused code review

### Phase 7: Real life integration tests
There's code in examples folder but date ranges are off - update them to Jan 1st 2026 as starting point.
- [x] Fix stream_files() TaskGroup bug (see plans/potential_memory_issue.md)
- [x] Memory test verified - sliding window bounds memory to ~12MB for 50MB+ data
- [x] Apply breaking changes from lookup refactoring (see plans/convert-gdelt-docs-to-lookups.md)
- [x] Update examples for new lookup API (fips_to_iso3, entry.name, etc.)
- [x] All 772 tests pass
- [x] Lookup API verified working
- [x] Real-life integration test: Trump+Venezuela query via DOC API (tests/integration_trump_venezuela.py)

**SPIKE COMPLETE:** Memory analysis identified 1 real bug in `stream_files()`.
See `plans/potential_memory_issue_v3.md` for final fix (sliding window with asyncio.wait).

#### Coverage Matrix

| Endpoint | Unit Tests | Example | Integration |
|----------|------------|---------|-------------|
| DOC | ✅ | ✅ basic_client_usage.py | ✅ integration_trump_venezuela.py |
| Events | ✅ | ✅ events_endpoint_example.py | - |
| Mentions | ✅ | ✅ query_mentions.py | - |
| GKG | ✅ | ✅ gkg_example.py | - |
| NGrams | ✅ | ✅ ngrams_example.py | - |
| Context | ✅ | ❌ MISSING | - |
| GEO | ✅ | ❌ MISSING | - |
| TV/TV AI | ✅ | ❌ MISSING | - |
| FileSource | ✅ | ✅ download_gdelt_files.py | - |
| BigQuery | ✅ | ✅ bigquery_example.py | - |

**Status:** All endpoints have unit tests. 3 endpoints missing examples (Context, GEO, TV).

---

*Plan generated: January 2026*
*Specification version: 1.0.0-draft*
