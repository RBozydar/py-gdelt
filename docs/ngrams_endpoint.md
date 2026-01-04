# NGrams Endpoint

The `NGramsEndpoint` provides access to GDELT NGrams 3.0 data, which tracks word and phrase occurrences across global news coverage with contextual information including position, language, and surrounding text.

## Overview

NGrams 3.0 captures individual word and character occurrences from news articles with:
- **Contextual information**: ~7 words before and after each occurrence
- **Position tracking**: Article decile position (0-90, where 0 = first 10% of article)
- **Language identification**: ISO 639-1/2 language codes
- **Segment types**: Space-delimited (1) vs. scriptio continua (2) languages

**Note**: NGrams are file-based only (no BigQuery support).

## Features

- **Async-first API** with sync wrappers for compatibility
- **DataFetcher integration** for orchestrated file downloads with retry logic
- **Client-side filtering** by ngram text, language, and position
- **Streaming support** for memory-efficient processing of large datasets
- **Type-safe models** with Pydantic validation at API boundary

## Quick Start

```python
from datetime import date
from py_gdelt.endpoints import NGramsEndpoint
from py_gdelt.filters import NGramsFilter, DateRange

async with NGramsEndpoint() as endpoint:
    filter_obj = NGramsFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        ngram="climate",
        language="en",
        min_position=0,
        max_position=20,  # Headlines only
    )

    result = await endpoint.query(filter_obj)
    print(f"Found {len(result)} mentions")
```

## Filter Options

The `NGramsFilter` class supports the following filtering options:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date_range` | `DateRange` | Yes | Date range to query (max 365 days) |
| `ngram` | `str` | No | Substring to match in ngram text (case-insensitive) |
| `language` | `str` | No | ISO 639-1/2 language code (exact match) |
| `min_position` | `int` | No | Minimum article decile position (0-90) |
| `max_position` | `int` | No | Maximum article decile position (0-90) |

### Position Values

Position represents the article decile where the ngram appears:
- `0` = First 10% of article (headline area)
- `10` = 10-20% of article
- `20` = 20-30% of article
- ...
- `90` = Last 10% of article (conclusion area)

**Common position ranges:**
- **Headlines**: `min_position=0, max_position=20`
- **Body**: `min_position=30, max_position=70`
- **Conclusions**: `min_position=70, max_position=90`

## Usage Examples

### Basic Query

Collect all results in memory:

```python
from datetime import date
from py_gdelt.endpoints import NGramsEndpoint
from py_gdelt.filters import NGramsFilter, DateRange

async with NGramsEndpoint() as endpoint:
    filter_obj = NGramsFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        language="en",
    )

    result = await endpoint.query(filter_obj)

    for record in result:
        print(f"{record.ngram}: {record.context}")
        print(f"  Position: {record.position}, URL: {record.url}")
```

### Streaming for Large Datasets

Process records one at a time for memory efficiency:

```python
async with NGramsEndpoint() as endpoint:
    filter_obj = NGramsFilter(
        date_range=DateRange(
            start=date(2024, 1, 1),
            end=date(2024, 1, 7)
        ),
        ngram="climate",
        language="en",
    )

    async for record in endpoint.stream(filter_obj):
        if record.is_early_in_article:
            print(f"Headline mention: {record.context}")
```

### Language Analysis

Track language diversity for a term:

```python
language_counts = {}

async with NGramsEndpoint() as endpoint:
    filter_obj = NGramsFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        ngram="peace",
    )

    async for record in endpoint.stream(filter_obj):
        language_counts[record.language] = (
            language_counts.get(record.language, 0) + 1
        )

# Display top languages
for lang, count in sorted(language_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"{lang}: {count} mentions")
```

### Position Distribution Analysis

Understand where in articles a term appears:

```python
early_count = middle_count = late_count = 0

async with NGramsEndpoint() as endpoint:
    filter_obj = NGramsFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        ngram="election",
        language="en",
    )

    async for record in endpoint.stream(filter_obj):
        if record.is_early_in_article:
            early_count += 1
        elif record.is_late_in_article:
            late_count += 1
        else:
            middle_count += 1

print(f"Early: {early_count}, Middle: {middle_count}, Late: {late_count}")
```

### Synchronous Usage

For non-async code:

```python
endpoint = NGramsEndpoint()

filter_obj = NGramsFilter(
    date_range=DateRange(start=date(2024, 1, 1)),
    ngram="technology",
    language="en",
)

# Sync query
result = endpoint.query_sync(filter_obj)
print(f"Found {len(result)} records")

# Sync streaming
for record in endpoint.stream_sync(filter_obj):
    print(record.ngram)

# Clean up
import asyncio
asyncio.run(endpoint.close())
```

## NGramRecord Model

Each record contains:

| Field | Type | Description |
|-------|------|-------------|
| `date` | `datetime` | Publication date/time |
| `ngram` | `str` | The word or character |
| `language` | `str` | ISO 639-1/2 language code |
| `segment_type` | `int` | 1 = space-delimited, 2 = scriptio continua |
| `position` | `int` | Article decile (0-90) |
| `pre_context` | `str` | ~7 words before ngram |
| `post_context` | `str` | ~7 words after ngram |
| `url` | `str` | Source article URL |

### Computed Properties

- `context`: Full context string (pre + ngram + post)
- `is_early_in_article`: True if position <= 20 (first 30%)
- `is_late_in_article`: True if position >= 70 (last 30%)

## Configuration

Configure via `GDELTSettings`:

```python
from pathlib import Path
from py_gdelt.config import GDELTSettings
from py_gdelt.endpoints import NGramsEndpoint

settings = GDELTSettings(
    cache_dir=Path.home() / ".cache" / "gdelt",
    cache_ttl=3600,  # Cache for 1 hour
    max_concurrent_downloads=10,
    max_retries=3,
)

async with NGramsEndpoint(settings=settings) as endpoint:
    # Use configured endpoint
    ...
```

## Error Handling

The endpoint handles errors according to the configured error policy:

```python
from py_gdelt.exceptions import RateLimitError, APIError, DataError

async with NGramsEndpoint() as endpoint:
    try:
        result = await endpoint.query(filter_obj)
    except RateLimitError as e:
        print(f"Rate limited: {e}")
        if e.retry_after:
            print(f"Retry after {e.retry_after} seconds")
    except APIError as e:
        print(f"API error: {e}")
    except DataError as e:
        print(f"Data parsing error: {e}")
```

## Advanced Usage

### Shared Resources

Share FileSource across multiple endpoints:

```python
from py_gdelt.sources import FileSource

async with FileSource() as file_source:
    ngrams1 = NGramsEndpoint(file_source=file_source)
    ngrams2 = NGramsEndpoint(file_source=file_source)

    # Both endpoints share the same HTTP client and cache
    result1 = await ngrams1.query(filter1)
    result2 = await ngrams2.query(filter2)
```

### Custom Filtering

Combine built-in filters with custom logic:

```python
async with NGramsEndpoint() as endpoint:
    filter_obj = NGramsFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        language="en",
    )

    async for record in endpoint.stream(filter_obj):
        # Custom filtering
        if len(record.ngram) > 15:  # Long phrases only
            if "climate" in record.ngram.lower():
                print(f"Long climate phrase: {record.ngram}")
```

## Performance Tips

1. **Use streaming for large datasets** to avoid memory issues
2. **Enable caching** to avoid re-downloading historical files
3. **Limit date ranges** to reduce download volume
4. **Apply specific filters** to reduce client-side processing
5. **Use concurrent downloads** (configure via `max_concurrent_downloads`)

## Limitations

- **No BigQuery support**: NGrams are file-based only
- **Client-side filtering**: Ngram text, language, and position filters applied after download
- **Date range limit**: Maximum 365 days per query
- **Historical data**: NGrams coverage varies by date range

## See Also

- [Filters Documentation](filters.md)
- [Models Documentation](models.md)
- [DataFetcher Documentation](sources.md)
- [GDELT NGrams 3.0 Documentation](https://blog.gdeltproject.org/announcing-gdelt-ngrams-3-0/)
