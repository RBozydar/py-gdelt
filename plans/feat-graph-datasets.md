# Feature Plan: GDELT Graph Datasets

**Created:** 2025-01-20
**Updated:** 2025-01-20 (Post-review revision)
**Priority:** Medium (high future value)
**Effort:** Medium (simplified architecture)
**Target:** v1.1 (fetch only)

---

## Overview

Implement support for 9 GDELT Graph Datasets with type-safe fetch and parse APIs. These datasets are inherently graph-structured and will unlock significant value when combined with graph database integration in v2.0.

**Scope for v1.1:** Fetch and parse only. Export APIs (Neo4j, pandas, geopandas) deferred to v2.0.

---

## Datasets Summary

| Dataset | Full Name | Format | Update | BigQuery Table | v1.1 Status |
|---------|-----------|--------|--------|----------------|-------------|
| **GQG** | Global Quotation Graph | JSON-NL | 15 min | `gdeltv2.gqg` | Implement |
| **GEG** | Global Entity Graph | JSON-NL | 15 min | `gdeltv2.geg_gcnlapi` | Implement |
| **GFG** | Global Frontpage Graph | Tab-CSV | Hourly | `gdeltv2.gfg_partitioned` | Implement |
| **GGG** | Global Geographic Graph | JSON-NL | 15 min | `gdeltv2.ggg` | Implement |
| **GDG** | Global Difference Graph | Unknown | Daily | `gdeltv2.gdg_partitioned` | Defer |
| **GEMG** | Global Embedded Metadata Graph | JSON-NL | 15 min | `gdeltv2.gemg` | Implement |
| **GRG** | Global Relationship Graph | Unknown | 15 min | `gdeltv2.grg_vcn` | Defer |
| **VGEG** | Visual Global Entity Graph | Unknown | Daily | `gdeltv2.vgegv2_iatv` | Defer |
| **GAL** | Article List | JSON-NL | 15 min | Unknown | Implement |

**Note:** GDG, GRG, VGEG have unknown file formats - defer to v1.2 pending format documentation.

**Important:** Update frequencies need verification against live GDELT endpoints before implementation.

---

## Architecture Design

### Simplified Architecture (Post-Review)

Based on reviewer feedback, the architecture has been simplified:

1. **No parser classes** - Use module-level functions (stateless, simpler)
2. **No `_Raw*` for JSON-NL** - Parse directly to Pydantic (JSON is already structured)
3. **Keep `_Raw*` only for GFG** - TSV parsing benefits from intermediate dataclass
4. **Per-dataset filters** - Follow existing `EventFilter`/`GKGFilter` pattern
5. **Per-dataset endpoint methods** - Preserve type safety, no union return types
6. **Extend existing `DataFetcher`** - Don't create new fetcher class
7. **Defer sync wrappers** - Async-first for v1.1

### Data Flow

```
JSON-NL Datasets (GQG, GEG, GGG, GEMG, GAL):
  HTTP Response → Decompress → parse_gqg() → GQGRecord (Pydantic) → User

TSV Dataset (GFG):
  HTTP Response → Decompress → parse_gfg() → _RawGFGRecord → GFGRecord.from_raw() → User
```

### URL Patterns

Base URL: `http://data.gdeltproject.org/gdeltv3/`

| Dataset | Pattern | Example |
|---------|---------|---------|
| GQG | `gqg/YYYYMMDDHHMM00.gqg.json.gz` | `gqg/20250120103000.gqg.json.gz` |
| GEG | `geg/YYYYMMDDHHMM00.geg.json.gz` | `geg/20250120103000.geg.json.gz` |
| GFG | `gfg/YYYYMMDDHH0000.gfg.csv.gz` | `gfg/20250120100000.gfg.csv.gz` |
| GGG | `ggg/YYYYMMDDHHMM00.ggg.json.gz` | `ggg/20250120103000.ggg.json.gz` |
| GEMG | `gemg/YYYYMMDDHHMM00.gemg.json.gz` | `gemg/20250120103000.gemg.json.gz` |
| GAL | `gal/YYYYMMDDHHMM00.gal.json.gz` | `gal/20250120103000.gal.json.gz` |

**Note:** URL patterns assume 15-min intervals. Must verify against live endpoints.

---

## Schema Evolution Handling

All Pydantic models will use `extra="ignore"` with warnings to handle GDELT schema changes gracefully:

```python
# src/py_gdelt/models/graphs.py

import logging
import warnings
from pydantic import BaseModel, ConfigDict, model_validator

logger = logging.getLogger(__name__)

# Track seen unknown fields to avoid warning spam
_warned_fields: set[tuple[str, str]] = set()


class SchemaEvolutionMixin:
    """Mixin that warns about unknown fields from GDELT schema changes."""

    @model_validator(mode="before")
    @classmethod
    def warn_unknown_fields(cls, data: dict) -> dict:
        if not isinstance(data, dict):
            return data

        model_fields = set(cls.model_fields.keys())
        # Include aliases
        for field_info in cls.model_fields.values():
            if field_info.alias:
                model_fields.add(field_info.alias)

        unknown = set(data.keys()) - model_fields
        for field in unknown:
            key = (cls.__name__, field)
            if key not in _warned_fields:
                _warned_fields.add(key)
                warnings.warn(
                    f"GDELT schema change detected: {cls.__name__} has new field '{field}'. "
                    f"Consider updating py-gdelt. Field will be ignored.",
                    UserWarning,
                    stacklevel=4,
                )
                logger.warning(
                    "Unknown field '%s' in %s - GDELT may have updated their schema",
                    field,
                    cls.__name__,
                )
        return data


class GQGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Quotation Graph record."""

    model_config = ConfigDict(extra="ignore")

    # ... fields
```

---

## Data Models

### Internal Dataclass (GFG Only)

```python
# src/py_gdelt/models/_internal.py

@dataclass(slots=True)
class _RawGFGRecord:
    """Global Frontpage Graph raw record (TSV parsing)."""
    date: str
    from_frontpage_url: str
    link_url: str
    link_text: str
    page_position: str
    lang: str
```

### Public Pydantic Models

```python
# src/py_gdelt/models/graphs.py

from __future__ import annotations

from datetime import UTC, datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Quote(BaseModel):
    """Quoted statement from GQG."""

    model_config = ConfigDict(extra="ignore")

    pre: str
    quote: str
    post: str


class GQGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Quotation Graph record.

    Contains extracted quoted statements with pre/post context
    for speaker identification.
    """

    model_config = ConfigDict(extra="ignore")

    date: datetime
    url: str
    lang: str
    quotes: list[Quote] = Field(default_factory=list)

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: str | datetime) -> datetime:
        if isinstance(v, datetime):
            return v
        # Handle ISO format from JSON
        if "T" in str(v):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        # Handle GDELT format YYYYMMDDHHMMSS
        return datetime.strptime(v, "%Y%m%d%H%M%S").replace(tzinfo=UTC)


class Entity(BaseModel):
    """Named entity from GEG."""

    model_config = ConfigDict(extra="ignore")

    name: str
    entity_type: str = Field(alias="type")
    salience: float | None = None
    wikipedia_url: str | None = None
    knowledge_graph_mid: str | None = Field(default=None, alias="mid")


class GEGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Entity Graph record.

    Contains named entities extracted via Google Cloud NLP API
    with salience scores.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    date: datetime
    url: str
    lang: str
    entities: list[Entity] = Field(default_factory=list)

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: str | datetime) -> datetime:
        if isinstance(v, datetime):
            return v
        if "T" in str(v):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return datetime.strptime(v, "%Y%m%d%H%M%S").replace(tzinfo=UTC)


class GFGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Frontpage Graph record.

    Contains hourly scans of news homepage links showing
    editorial priorities and prominence.
    """

    model_config = ConfigDict(extra="ignore")

    date: datetime
    from_frontpage_url: str
    link_url: str
    link_text: str
    page_position: int
    lang: str

    @classmethod
    def from_raw(cls, raw: _RawGFGRecord) -> Self:
        """Convert from raw TSV record."""
        return cls(
            date=datetime.strptime(raw.date, "%Y%m%d%H%M%S").replace(tzinfo=UTC),
            from_frontpage_url=raw.from_frontpage_url,
            link_url=raw.link_url,
            link_text=raw.link_text,
            page_position=int(raw.page_position) if raw.page_position else 0,
            lang=raw.lang,
        )


class GGGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Geographic Graph record.

    Contains location mentions with coordinates and context snippets.
    """

    model_config = ConfigDict(extra="ignore")

    date: datetime
    url: str
    location_name: str
    lat: float
    lon: float
    context: str

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: str | datetime) -> datetime:
        if isinstance(v, datetime):
            return v
        if "T" in str(v):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return datetime.strptime(v, "%Y%m%d%H%M%S").replace(tzinfo=UTC)


class MetaTag(BaseModel):
    """HTML meta tag from GEMG."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    key: str
    tag_type: str = Field(alias="type")
    value: str


class GEMGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Embedded Metadata Graph record.

    Contains HTML META tags and JSON-LD blocks extracted from articles.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    date: datetime
    url: str
    title: str | None = None
    lang: str
    metatags: list[MetaTag] = Field(default_factory=list)
    jsonld: list[str] = Field(default_factory=list)

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: str | datetime) -> datetime:
        if isinstance(v, datetime):
            return v
        if "T" in str(v):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return datetime.strptime(v, "%Y%m%d%H%M%S").replace(tzinfo=UTC)


class GALRecord(SchemaEvolutionMixin, BaseModel):
    """Article List record.

    Contains minimal article metadata without full GKG overhead.
    """

    model_config = ConfigDict(extra="ignore")

    date: datetime
    url: str
    title: str | None = None
    image: str | None = None
    description: str | None = None
    author: str | None = None
    lang: str

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: str | datetime) -> datetime:
        if isinstance(v, datetime):
            return v
        if "T" in str(v):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return datetime.strptime(v, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
```

---

## Filter Design

### Per-Dataset Filters (Following Existing Pattern)

```python
# src/py_gdelt/filters.py

class GQGFilter(BaseModel):
    """Filter for Global Quotation Graph queries."""

    date_range: DateRange
    languages: list[str] | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.date_range.days > 7:
            raise ValueError("GQG max date range: 7 days")
        return self


class GEGFilter(BaseModel):
    """Filter for Global Entity Graph queries."""

    date_range: DateRange
    languages: list[str] | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.date_range.days > 7:
            raise ValueError("GEG max date range: 7 days")
        return self


class GFGFilter(BaseModel):
    """Filter for Global Frontpage Graph queries."""

    date_range: DateRange
    languages: list[str] | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.date_range.days > 30:
            raise ValueError("GFG max date range: 30 days")
        return self


class GGGFilter(BaseModel):
    """Filter for Global Geographic Graph queries."""

    date_range: DateRange
    languages: list[str] | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.date_range.days > 7:
            raise ValueError("GGG max date range: 7 days")
        return self


class GEMGFilter(BaseModel):
    """Filter for Global Embedded Metadata Graph queries."""

    date_range: DateRange
    languages: list[str] | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.date_range.days > 7:
            raise ValueError("GEMG max date range: 7 days")
        return self


class GALFilter(BaseModel):
    """Filter for Article List queries."""

    date_range: DateRange
    languages: list[str] | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.date_range.days > 7:
            raise ValueError("GAL max date range: 7 days")
        return self
```

---

## Parser Design

### Module-Level Functions (No Classes)

```python
# src/py_gdelt/parsers/graphs.py

from __future__ import annotations

import csv
import gzip
import io
import json
import logging
from collections.abc import Iterator

from py_gdelt.models._internal import _RawGFGRecord
from py_gdelt.models.graphs import (
    GALRecord,
    GEGRecord,
    GEMGRecord,
    GFGRecord,
    GGGRecord,
    GQGRecord,
)

logger = logging.getLogger(__name__)


def _decompress_if_needed(data: bytes) -> bytes:
    """Decompress gzip data if compressed."""
    if data[:2] == b"\x1f\x8b":  # gzip magic number
        return gzip.decompress(data)
    return data


def _parse_jsonl(data: bytes, model_cls: type[T]) -> Iterator[T]:
    """Parse JSON-NL data directly to Pydantic models.

    Args:
        data: Raw bytes (potentially gzipped).
        model_cls: Pydantic model class to parse into.

    Yields:
        Validated Pydantic model instances.

    Note:
        Malformed lines are logged and skipped for data recovery.
    """
    decompressed = _decompress_if_needed(data)
    text = decompressed.decode("utf-8", errors="replace")

    for line_num, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue

        try:
            obj = json.loads(line)
            yield model_cls.model_validate(obj)
        except json.JSONDecodeError as e:
            logger.warning("Malformed JSON at line %d: %s", line_num, e)
            continue
        except Exception as e:
            logger.warning("Failed to parse line %d: %s", line_num, e)
            continue


def parse_gqg(data: bytes) -> Iterator[GQGRecord]:
    """Parse Global Quotation Graph JSON-NL data.

    Args:
        data: Raw bytes (potentially gzipped).

    Yields:
        GQGRecord: Validated quotation records.
    """
    yield from _parse_jsonl(data, GQGRecord)


def parse_geg(data: bytes) -> Iterator[GEGRecord]:
    """Parse Global Entity Graph JSON-NL data.

    Args:
        data: Raw bytes (potentially gzipped).

    Yields:
        GEGRecord: Validated entity records.
    """
    yield from _parse_jsonl(data, GEGRecord)


def parse_ggg(data: bytes) -> Iterator[GGGRecord]:
    """Parse Global Geographic Graph JSON-NL data.

    Args:
        data: Raw bytes (potentially gzipped).

    Yields:
        GGGRecord: Validated geographic records.
    """
    yield from _parse_jsonl(data, GGGRecord)


def parse_gemg(data: bytes) -> Iterator[GEMGRecord]:
    """Parse Global Embedded Metadata Graph JSON-NL data.

    Args:
        data: Raw bytes (potentially gzipped).

    Yields:
        GEMGRecord: Validated metadata records.
    """
    yield from _parse_jsonl(data, GEMGRecord)


def parse_gal(data: bytes) -> Iterator[GALRecord]:
    """Parse Article List JSON-NL data.

    Args:
        data: Raw bytes (potentially gzipped).

    Yields:
        GALRecord: Validated article records.
    """
    yield from _parse_jsonl(data, GALRecord)


def parse_gfg(data: bytes) -> Iterator[GFGRecord]:
    """Parse Global Frontpage Graph tab-delimited CSV data.

    Args:
        data: Raw bytes (potentially gzipped).

    Yields:
        GFGRecord: Validated frontpage records.
    """
    decompressed = _decompress_if_needed(data)
    text = decompressed.decode("utf-8", errors="replace")

    reader = csv.reader(io.StringIO(text), delimiter="\t")

    for line_num, row in enumerate(reader, start=1):
        if not row or not row[0].strip():
            continue

        if len(row) < 6:
            logger.warning("Incomplete row at line %d: expected 6 columns, got %d", line_num, len(row))
            continue

        try:
            raw = _RawGFGRecord(
                date=row[0],
                from_frontpage_url=row[1],
                link_url=row[2],
                link_text=row[3],
                page_position=row[4],
                lang=row[5],
            )
            yield GFGRecord.from_raw(raw)
        except Exception as e:
            logger.warning("Failed to parse line %d: %s", line_num, e)
            continue
```

---

## Endpoint Design

### Type-Safe Per-Dataset Methods

```python
# src/py_gdelt/endpoints/graphs.py

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Literal

from py_gdelt.filters import (
    GALFilter,
    GEGFilter,
    GEMGFilter,
    GFGFilter,
    GGGFilter,
    GQGFilter,
)
from py_gdelt.models.common import FetchResult
from py_gdelt.models.graphs import (
    GALRecord,
    GEGRecord,
    GEMGRecord,
    GFGRecord,
    GGGRecord,
    GQGRecord,
)
from py_gdelt.parsers import graphs as graph_parsers

if TYPE_CHECKING:
    from py_gdelt.sources.fetcher import DataFetcher

logger = logging.getLogger(__name__)


class GraphEndpoint:
    """Endpoint for GDELT Graph datasets.

    Provides type-safe access to all graph datasets with per-dataset
    query methods that preserve return types.

    Args:
        fetcher: DataFetcher instance for file/BigQuery access.

    Example:
        async with GDELTClient() as client:
            # Type-safe: returns FetchResult[GQGRecord]
            result = await client.graphs.query_gqg(
                GQGFilter(date_range=DateRange(start=date(2025, 1, 20)))
            )
            for record in result.records:
                print(record.quotes)  # IDE knows this is list[Quote]
    """

    def __init__(self, fetcher: DataFetcher) -> None:
        self._fetcher = fetcher

    # --- GQG (Global Quotation Graph) ---

    async def query_gqg(
        self,
        filter_obj: GQGFilter,
        *,
        error_policy: Literal["raise", "warn", "skip"] = "warn",
    ) -> FetchResult[GQGRecord]:
        """Query Global Quotation Graph records.

        Args:
            filter_obj: Filter specifying date range and optional language filter.
            error_policy: How to handle errors ('raise', 'warn', 'skip').

        Returns:
            FetchResult containing GQGRecord instances.
        """
        records: list[GQGRecord] = []
        async for record in self.stream_gqg(filter_obj, error_policy=error_policy):
            records.append(record)
        return FetchResult(records=records)

    async def stream_gqg(
        self,
        filter_obj: GQGFilter,
        *,
        error_policy: Literal["raise", "warn", "skip"] = "warn",
    ) -> AsyncIterator[GQGRecord]:
        """Stream Global Quotation Graph records.

        Args:
            filter_obj: Filter specifying date range and optional language filter.
            error_policy: How to handle errors ('raise', 'warn', 'skip').

        Yields:
            GQGRecord: Individual quotation records.
        """
        async for url, data in self._fetcher.fetch_graph_files("gqg", filter_obj.date_range):
            try:
                for record in graph_parsers.parse_gqg(data):
                    if filter_obj.languages and record.lang not in filter_obj.languages:
                        continue
                    yield record
            except Exception as e:
                if error_policy == "raise":
                    raise
                elif error_policy == "warn":
                    logger.warning("Error parsing %s: %s", url, e)

    # --- GEG (Global Entity Graph) ---

    async def query_geg(
        self,
        filter_obj: GEGFilter,
        *,
        error_policy: Literal["raise", "warn", "skip"] = "warn",
    ) -> FetchResult[GEGRecord]:
        """Query Global Entity Graph records."""
        records: list[GEGRecord] = []
        async for record in self.stream_geg(filter_obj, error_policy=error_policy):
            records.append(record)
        return FetchResult(records=records)

    async def stream_geg(
        self,
        filter_obj: GEGFilter,
        *,
        error_policy: Literal["raise", "warn", "skip"] = "warn",
    ) -> AsyncIterator[GEGRecord]:
        """Stream Global Entity Graph records."""
        async for url, data in self._fetcher.fetch_graph_files("geg", filter_obj.date_range):
            try:
                for record in graph_parsers.parse_geg(data):
                    if filter_obj.languages and record.lang not in filter_obj.languages:
                        continue
                    yield record
            except Exception as e:
                if error_policy == "raise":
                    raise
                elif error_policy == "warn":
                    logger.warning("Error parsing %s: %s", url, e)

    # --- GFG (Global Frontpage Graph) ---

    async def query_gfg(
        self,
        filter_obj: GFGFilter,
        *,
        error_policy: Literal["raise", "warn", "skip"] = "warn",
    ) -> FetchResult[GFGRecord]:
        """Query Global Frontpage Graph records."""
        records: list[GFGRecord] = []
        async for record in self.stream_gfg(filter_obj, error_policy=error_policy):
            records.append(record)
        return FetchResult(records=records)

    async def stream_gfg(
        self,
        filter_obj: GFGFilter,
        *,
        error_policy: Literal["raise", "warn", "skip"] = "warn",
    ) -> AsyncIterator[GFGRecord]:
        """Stream Global Frontpage Graph records."""
        async for url, data in self._fetcher.fetch_graph_files("gfg", filter_obj.date_range):
            try:
                for record in graph_parsers.parse_gfg(data):
                    if filter_obj.languages and record.lang not in filter_obj.languages:
                        continue
                    yield record
            except Exception as e:
                if error_policy == "raise":
                    raise
                elif error_policy == "warn":
                    logger.warning("Error parsing %s: %s", url, e)

    # --- GGG (Global Geographic Graph) ---

    async def query_ggg(
        self,
        filter_obj: GGGFilter,
        *,
        error_policy: Literal["raise", "warn", "skip"] = "warn",
    ) -> FetchResult[GGGRecord]:
        """Query Global Geographic Graph records."""
        records: list[GGGRecord] = []
        async for record in self.stream_ggg(filter_obj, error_policy=error_policy):
            records.append(record)
        return FetchResult(records=records)

    async def stream_ggg(
        self,
        filter_obj: GGGFilter,
        *,
        error_policy: Literal["raise", "warn", "skip"] = "warn",
    ) -> AsyncIterator[GGGRecord]:
        """Stream Global Geographic Graph records."""
        async for url, data in self._fetcher.fetch_graph_files("ggg", filter_obj.date_range):
            try:
                for record in graph_parsers.parse_ggg(data):
                    if filter_obj.languages and record.lang not in filter_obj.languages:
                        continue
                    yield record
            except Exception as e:
                if error_policy == "raise":
                    raise
                elif error_policy == "warn":
                    logger.warning("Error parsing %s: %s", url, e)

    # --- GEMG (Global Embedded Metadata Graph) ---

    async def query_gemg(
        self,
        filter_obj: GEMGFilter,
        *,
        error_policy: Literal["raise", "warn", "skip"] = "warn",
    ) -> FetchResult[GEMGRecord]:
        """Query Global Embedded Metadata Graph records."""
        records: list[GEMGRecord] = []
        async for record in self.stream_gemg(filter_obj, error_policy=error_policy):
            records.append(record)
        return FetchResult(records=records)

    async def stream_gemg(
        self,
        filter_obj: GEMGFilter,
        *,
        error_policy: Literal["raise", "warn", "skip"] = "warn",
    ) -> AsyncIterator[GEMGRecord]:
        """Stream Global Embedded Metadata Graph records."""
        async for url, data in self._fetcher.fetch_graph_files("gemg", filter_obj.date_range):
            try:
                for record in graph_parsers.parse_gemg(data):
                    if filter_obj.languages and record.lang not in filter_obj.languages:
                        continue
                    yield record
            except Exception as e:
                if error_policy == "raise":
                    raise
                elif error_policy == "warn":
                    logger.warning("Error parsing %s: %s", url, e)

    # --- GAL (Article List) ---

    async def query_gal(
        self,
        filter_obj: GALFilter,
        *,
        error_policy: Literal["raise", "warn", "skip"] = "warn",
    ) -> FetchResult[GALRecord]:
        """Query Article List records."""
        records: list[GALRecord] = []
        async for record in self.stream_gal(filter_obj, error_policy=error_policy):
            records.append(record)
        return FetchResult(records=records)

    async def stream_gal(
        self,
        filter_obj: GALFilter,
        *,
        error_policy: Literal["raise", "warn", "skip"] = "warn",
    ) -> AsyncIterator[GALRecord]:
        """Stream Article List records."""
        async for url, data in self._fetcher.fetch_graph_files("gal", filter_obj.date_range):
            try:
                for record in graph_parsers.parse_gal(data):
                    if filter_obj.languages and record.lang not in filter_obj.languages:
                        continue
                    yield record
            except Exception as e:
                if error_policy == "raise":
                    raise
                elif error_policy == "warn":
                    logger.warning("Error parsing %s: %s", url, e)
```

---

## Implementation Plan

### Phase 1: URL Verification (Pre-Implementation)

Before writing any code, verify URL patterns against live GDELT endpoints:

**File:** `scripts/verify_graph_urls.py` (not part of package)

- [ ] Verify GQG URL pattern with HTTP HEAD request
- [ ] Verify GEG URL pattern with HTTP HEAD request
- [ ] Verify GFG URL pattern with HTTP HEAD request
- [ ] Verify GGG URL pattern with HTTP HEAD request
- [ ] Verify GEMG URL pattern with HTTP HEAD request
- [ ] Verify GAL URL pattern with HTTP HEAD request
- [ ] Document actual update frequencies
- [ ] Update plan with correct URL patterns

### Phase 2: Models

#### 2.1 Add Internal Dataclass (GFG Only)

**File:** `src/py_gdelt/models/_internal.py`

- [ ] Add `_RawGFGRecord` dataclass

#### 2.2 Create Pydantic Models

**File:** `src/py_gdelt/models/graphs.py`

- [ ] Create `SchemaEvolutionMixin` with unknown field warnings
- [ ] Create `Quote` model (nested in GQG)
- [ ] Create `GQGRecord` model with `extra="ignore"`
- [ ] Create `Entity` model (nested in GEG)
- [ ] Create `GEGRecord` model with `extra="ignore"`
- [ ] Create `GFGRecord` model with `from_raw()` and `extra="ignore"`
- [ ] Create `GGGRecord` model with `extra="ignore"`
- [ ] Create `MetaTag` model (nested in GEMG)
- [ ] Create `GEMGRecord` model with `extra="ignore"`
- [ ] Create `GALRecord` model with `extra="ignore"`

### Phase 3: Filters

**File:** `src/py_gdelt/filters.py`

- [ ] Add `GQGFilter` with 7-day max
- [ ] Add `GEGFilter` with 7-day max
- [ ] Add `GFGFilter` with 30-day max
- [ ] Add `GGGFilter` with 7-day max
- [ ] Add `GEMGFilter` with 7-day max
- [ ] Add `GALFilter` with 7-day max

### Phase 4: Parsers

**File:** `src/py_gdelt/parsers/graphs.py`

- [ ] Implement `_decompress_if_needed()` helper
- [ ] Implement `_parse_jsonl()` generic helper
- [ ] Implement `parse_gqg()` function
- [ ] Implement `parse_geg()` function
- [ ] Implement `parse_gfg()` function (TSV)
- [ ] Implement `parse_ggg()` function
- [ ] Implement `parse_gemg()` function
- [ ] Implement `parse_gal()` function

### Phase 5: Data Fetcher Extension

**File:** `src/py_gdelt/sources/fetcher.py`

- [ ] Add `fetch_graph_files()` method to existing `DataFetcher`
- [ ] Implement URL generation for each graph type
- [ ] Handle different time resolutions (15-min, hourly)

**File:** `src/py_gdelt/sources/files.py`

- [ ] Add graph file URL generation to `FileSource`
- [ ] Add `GraphFileType` literal or extend `FileType`

### Phase 6: Endpoint

**File:** `src/py_gdelt/endpoints/graphs.py`

- [ ] Create `GraphEndpoint` class
- [ ] Implement `query_gqg()` and `stream_gqg()`
- [ ] Implement `query_geg()` and `stream_geg()`
- [ ] Implement `query_gfg()` and `stream_gfg()`
- [ ] Implement `query_ggg()` and `stream_ggg()`
- [ ] Implement `query_gemg()` and `stream_gemg()`
- [ ] Implement `query_gal()` and `stream_gal()`

**File:** `src/py_gdelt/client.py`

- [ ] Add `graphs` property returning `GraphEndpoint` instance

### Phase 7: Testing

#### 7.1 Unit Tests

**File:** `tests/unit/test_graphs.py`

- [ ] Test `SchemaEvolutionMixin` warns on unknown fields
- [ ] Test `parse_gqg()` with valid JSON-NL
- [ ] Test `parse_gqg()` with malformed line (should skip)
- [ ] Test `parse_geg()` with valid data
- [ ] Test `parse_gfg()` with valid TSV
- [ ] Test `parse_ggg()` with valid data
- [ ] Test `parse_gemg()` with valid data
- [ ] Test `parse_gal()` with valid data
- [ ] Test parsers with empty input
- [ ] Test parsers with unicode content
- [ ] Test `GFGRecord.from_raw()` conversion
- [ ] Test filter date range validation
- [ ] Test `GraphEndpoint` methods with mocked fetcher

#### 7.2 Weekly Integration Tests (Schema Evolution)

**File:** `tests/weekly/test_graph_schema_evolution.py`

```python
"""Weekly integration tests to detect GDELT schema changes.

These tests fetch live data from GDELT and verify our models can parse it.
Run weekly via CI to detect schema changes early.
"""

import pytest
from datetime import date, timedelta

from py_gdelt import GDELTClient
from py_gdelt.filters import GQGFilter, GEGFilter, GFGFilter, GGGFilter, GEMGFilter, GALFilter
from py_gdelt.models.common import DateRange


@pytest.mark.weekly
@pytest.mark.integration
class TestGraphSchemaEvolution:
    """Weekly tests to detect GDELT schema changes."""

    @pytest.fixture
    def recent_date_range(self) -> DateRange:
        """Return a date range for yesterday (likely to have data)."""
        yesterday = date.today() - timedelta(days=1)
        return DateRange(start=yesterday, end=yesterday)

    async def test_gqg_schema_unchanged(self, recent_date_range: DateRange) -> None:
        """Verify GQG schema hasn't changed."""
        async with GDELTClient() as client:
            with pytest.warns(None) as warnings:
                result = await client.graphs.query_gqg(
                    GQGFilter(date_range=recent_date_range)
                )

            # Check for schema change warnings
            schema_warnings = [w for w in warnings if "schema change" in str(w.message).lower()]
            if schema_warnings:
                pytest.fail(
                    f"GQG schema has changed! New fields detected: {schema_warnings}. "
                    "Update GQGRecord model to include new fields."
                )

            assert len(result.records) > 0, "No GQG records returned - check GDELT availability"

    async def test_geg_schema_unchanged(self, recent_date_range: DateRange) -> None:
        """Verify GEG schema hasn't changed."""
        async with GDELTClient() as client:
            with pytest.warns(None) as warnings:
                result = await client.graphs.query_geg(
                    GEGFilter(date_range=recent_date_range)
                )

            schema_warnings = [w for w in warnings if "schema change" in str(w.message).lower()]
            if schema_warnings:
                pytest.fail(
                    f"GEG schema has changed! New fields detected: {schema_warnings}. "
                    "Update GEGRecord model to include new fields."
                )

            assert len(result.records) > 0

    async def test_gfg_schema_unchanged(self, recent_date_range: DateRange) -> None:
        """Verify GFG schema hasn't changed."""
        async with GDELTClient() as client:
            with pytest.warns(None) as warnings:
                result = await client.graphs.query_gfg(
                    GFGFilter(date_range=recent_date_range)
                )

            schema_warnings = [w for w in warnings if "schema change" in str(w.message).lower()]
            if schema_warnings:
                pytest.fail(f"GFG schema has changed! {schema_warnings}")

            assert len(result.records) > 0

    async def test_ggg_schema_unchanged(self, recent_date_range: DateRange) -> None:
        """Verify GGG schema hasn't changed."""
        async with GDELTClient() as client:
            with pytest.warns(None) as warnings:
                result = await client.graphs.query_ggg(
                    GGGFilter(date_range=recent_date_range)
                )

            schema_warnings = [w for w in warnings if "schema change" in str(w.message).lower()]
            if schema_warnings:
                pytest.fail(f"GGG schema has changed! {schema_warnings}")

            assert len(result.records) > 0

    async def test_gemg_schema_unchanged(self, recent_date_range: DateRange) -> None:
        """Verify GEMG schema hasn't changed."""
        async with GDELTClient() as client:
            with pytest.warns(None) as warnings:
                result = await client.graphs.query_gemg(
                    GEMGFilter(date_range=recent_date_range)
                )

            schema_warnings = [w for w in warnings if "schema change" in str(w.message).lower()]
            if schema_warnings:
                pytest.fail(f"GEMG schema has changed! {schema_warnings}")

            assert len(result.records) > 0

    async def test_gal_schema_unchanged(self, recent_date_range: DateRange) -> None:
        """Verify GAL schema hasn't changed."""
        async with GDELTClient() as client:
            with pytest.warns(None) as warnings:
                result = await client.graphs.query_gal(
                    GALFilter(date_range=recent_date_range)
                )

            schema_warnings = [w for w in warnings if "schema change" in str(w.message).lower()]
            if schema_warnings:
                pytest.fail(f"GAL schema has changed! {schema_warnings}")

            assert len(result.records) > 0
```

**File:** `.github/workflows/weekly-integration.yml` (or update existing)

```yaml
name: Weekly Integration Tests

on:
  schedule:
    # Run every Monday at 6 AM UTC
    - cron: '0 6 * * 1'
  workflow_dispatch:  # Allow manual trigger

jobs:
  schema-evolution:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --all-extras
      - name: Run weekly integration tests
        run: uv run pytest tests/weekly/ -m "weekly and integration" -v
        env:
          GDELT_INTEGRATION_TESTS: "1"
      - name: Notify on schema change
        if: failure()
        # Add Slack/email notification here
        run: echo "GDELT schema change detected! Check test output."
```

### Phase 8: Package Exports

- [ ] `src/py_gdelt/models/__init__.py` - Export graph models
- [ ] `src/py_gdelt/parsers/__init__.py` - Export graph parser functions
- [ ] `src/py_gdelt/endpoints/__init__.py` - Export GraphEndpoint
- [ ] `src/py_gdelt/filters.py` - Already has exports, add new filters
- [ ] `src/py_gdelt/__init__.py` - Export from main package

---

## Files to Create

| File | Purpose |
|------|---------|
| `src/py_gdelt/models/graphs.py` | Pydantic models with schema evolution handling |
| `src/py_gdelt/parsers/graphs.py` | Module-level parser functions |
| `src/py_gdelt/endpoints/graphs.py` | GraphEndpoint with per-dataset methods |
| `tests/unit/test_graphs.py` | Unit tests (consolidated) |
| `tests/weekly/test_graph_schema_evolution.py` | Weekly integration tests |
| `scripts/verify_graph_urls.py` | Pre-implementation URL verification |

## Files to Modify

| File | Changes |
|------|---------|
| `src/py_gdelt/models/_internal.py` | Add `_RawGFGRecord` only |
| `src/py_gdelt/filters.py` | Add 6 per-dataset filter classes |
| `src/py_gdelt/sources/files.py` | Add graph file URL generation |
| `src/py_gdelt/sources/fetcher.py` | Add `fetch_graph_files()` method |
| `src/py_gdelt/client.py` | Add `graphs` property |
| `src/py_gdelt/models/__init__.py` | Export graph models |
| `src/py_gdelt/parsers/__init__.py` | Export parser functions |
| `src/py_gdelt/endpoints/__init__.py` | Export GraphEndpoint |
| `.github/workflows/weekly-integration.yml` | Add schema evolution tests |

---

## Design Decisions (Post-Review)

| Decision | Rationale |
|----------|-----------|
| Module-level parser functions | Parsers are stateless; classes add unnecessary ceremony |
| Skip `_Raw*` for JSON-NL | JSON is already structured; Pydantic validates directly |
| Keep `_Raw*` for GFG (TSV) | TSV parsing benefits from intermediate staging |
| Per-dataset filters | Follows existing pattern; simpler than discriminated union |
| Per-dataset endpoint methods | Preserves type safety; IDE autocomplete works |
| Extend existing `DataFetcher` | Reuses battle-tested code; no parallel hierarchy |
| Defer sync wrappers | Async-first for v1.1; sync can wait for v1.2 |
| `extra="ignore"` + warnings | Graceful degradation with user notification |
| Weekly integration tests | Early detection of GDELT schema changes |

---

## Acceptance Criteria

### Functional Requirements

- [ ] Users can query/stream GQG records with type safety
- [ ] Users can query/stream GEG records with type safety
- [ ] Users can query/stream GFG records with type safety
- [ ] Users can query/stream GGG records with type safety
- [ ] Users can query/stream GEMG records with type safety
- [ ] Users can query/stream GAL records with type safety
- [ ] Users receive warnings when GDELT adds new fields
- [ ] Users can filter by language (client-side)

### Non-Functional Requirements

- [ ] Memory usage stays bounded during streaming
- [ ] Date range limits prevent accidental DoS
- [ ] Malformed lines are logged and skipped
- [ ] Schema changes don't crash parsing (graceful degradation)
- [ ] All code passes `make ci`

### Quality Gates

- [ ] 100% test coverage on new code
- [ ] All models have Google-style docstrings
- [ ] No new ruff/mypy warnings
- [ ] Weekly integration tests pass
- [ ] URL patterns verified against live GDELT

---

## References

### Internal References

- `src/py_gdelt/endpoints/gkg.py:1` - Reference endpoint pattern
- `src/py_gdelt/models/_internal.py:1` - Internal dataclass pattern (for GFG)
- `src/py_gdelt/parsers/gkg.py:1` - Parser pattern reference
- `src/py_gdelt/sources/files.py:1` - FileSource URL patterns
- `src/py_gdelt/sources/fetcher.py:1` - DataFetcher to extend
- `src/py_gdelt/filters.py:1` - Per-dataset filter pattern

### External References

- [GDELT Graph Datasets](https://blog.gdeltproject.org/) - Official GDELT blog
- [Pydantic v2 extra="ignore"](https://docs.pydantic.dev/latest/concepts/models/#extra-fields)
- [Pydantic v2 model_validator](https://docs.pydantic.dev/latest/concepts/validators/#model-validators)
