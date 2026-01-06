# MentionsEndpoint Quick Reference

## Installation

```bash
# Install with BigQuery support (required for mentions)
pip install py-gdelt[bigquery]
```

## Basic Usage

```python
from datetime import date
from py_gdelt.endpoints.mentions import MentionsEndpoint
from py_gdelt.filters import DateRange, EventFilter
from py_gdelt.sources import FileSource, BigQuerySource

# Setup
async with FileSource() as file_source:
    bq_source = BigQuerySource()
    endpoint = MentionsEndpoint(
        file_source=file_source,
        bigquery_source=bq_source,
    )

    # Create filter
    filter_obj = EventFilter(
        date_range=DateRange(
            start=date(2024, 1, 1),
            end=date(2024, 1, 7),
        )
    )

    # Query mentions
    result = await endpoint.query(
        global_event_id="123456789",
        filter_obj=filter_obj,
    )

    print(f"Found {len(result)} mentions")
```

## API Reference

### Constructor

```python
MentionsEndpoint(
    file_source: FileSource,
    bigquery_source: BigQuerySource | None = None,
    *,
    settings: GDELTSettings | None = None,
    fallback_enabled: bool = True,
    error_policy: ErrorPolicy = "warn",
)
```

### query() - Batch Query

```python
async def query(
    global_event_id: str,
    filter_obj: EventFilter,
    *,
    use_bigquery: bool = True,
) -> FetchResult[Mention]
```

Returns all mentions as `FetchResult[Mention]`.

### stream() - Streaming Query

```python
async def stream(
    global_event_id: str,
    filter_obj: EventFilter,
    *,
    use_bigquery: bool = True,
) -> AsyncIterator[Mention]
```

Yields mentions one at a time (memory-efficient).

### query_sync() - Synchronous Batch

```python
def query_sync(
    global_event_id: str,
    filter_obj: EventFilter,
    *,
    use_bigquery: bool = True,
) -> FetchResult[Mention]
```

Synchronous wrapper for `query()`.

### stream_sync() - Synchronous Stream

```python
def stream_sync(
    global_event_id: str,
    filter_obj: EventFilter,
    *,
    use_bigquery: bool = True,
) -> Iterator[Mention]
```

Synchronous wrapper for `stream()`.

## Mention Model

```python
class Mention(BaseModel):
    global_event_id: int
    event_time: datetime
    mention_time: datetime
    mention_type: int
    source_name: str
    identifier: str  # URL, DOI, or citation
    sentence_id: int
    actor1_char_offset: int | None
    actor2_char_offset: int | None
    action_char_offset: int | None
    in_raw_text: bool
    confidence: int  # 10-100
    doc_length: int
    doc_tone: float
    translation_info: str | None
```

## Common Patterns

### Filter by Confidence

```python
async for mention in endpoint.stream(event_id, filter_obj):
    if mention.confidence >= 80:
        print(f"High confidence: {mention.source_name}")
```

### Count by Source

```python
sources = {}
async for mention in endpoint.stream(event_id, filter_obj):
    sources[mention.source_name] = sources.get(mention.source_name, 0) + 1

for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
    print(f"{source}: {count}")
```

### Analyze Tone Distribution

```python
tones = []
async for mention in endpoint.stream(event_id, filter_obj):
    tones.append(mention.doc_tone)

avg_tone = sum(tones) / len(tones)
print(f"Average tone: {avg_tone:.2f}")
```

## Error Handling

```python
from py_gdelt.exceptions import ConfigurationError, RateLimitError

try:
    result = await endpoint.query(event_id, filter_obj)
except ConfigurationError as e:
    print(f"BigQuery not configured: {e}")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
```

## Configuration

### Error Policy

```python
endpoint = MentionsEndpoint(
    file_source=file_source,
    bigquery_source=bq_source,
    error_policy="raise",  # or "warn", "skip"
)
```

### Disable Fallback

```python
endpoint = MentionsEndpoint(
    file_source=file_source,
    bigquery_source=bq_source,
    fallback_enabled=False,
)
```

## Notes

- **BigQuery Required**: Mentions queries typically need BigQuery as files don't support event-specific filtering
- **Memory Efficiency**: Use `stream()` for large result sets to avoid loading everything into memory
- **Date Range**: Keep date ranges reasonable (< 1 year) for better query performance
- **Global Event ID**: Must be a valid event ID from GDELT Events data

## See Also

- [Full Implementation Documentation](MENTIONS_ENDPOINT_IMPLEMENTATION.md)
- [Examples](../examples/query_mentions.py)
- [Tests](../tests/test_endpoints_mentions.py)
