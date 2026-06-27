# Streaming Large Datasets

Memory-efficient data processing with streaming.

## Why Stream?

Loading large datasets into memory can exhaust resources. Streaming processes data incrementally:

- **Memory Efficient**: Process millions of records without loading all at once
- **Faster Start**: Begin processing immediately without waiting for complete download
- **Scalable**: Handle datasets of any size
- **Interruptible**: Stop early if you find what you need

## Basic Streaming

```
from py_gdelt import GDELTClient
from py_gdelt.filters import DateRange, EventFilter
from datetime import date, timedelta

async with GDELTClient() as client:
    event_filter = EventFilter(
        date_range=DateRange(
            start=date(2024, 1, 1),
            end=date(2024, 1, 7),
        ),
    )

    # Stream instead of query()
    async for event in client.events.stream(event_filter):
        process(event)  # Process one at a time
```

## Filtering While Streaming

Apply additional filters during streaming:

```
us_protest_count = 0

async for event in client.events.stream(event_filter):
    # Filter in-stream
    if event.event_code == "14":  # Protest
        if hasattr(event, 'actor1') and event.actor1:
            if hasattr(event.actor1, 'country_code') and event.actor1.country_code == 'US':
                us_protest_count += 1
```

## Early Exit

Stop processing when you have enough data:

```
count = 0
async for event in client.events.stream(event_filter):
    count += 1
    if count >= 1000:
        break  # Stop after 1000 events
```

## Batching

Process in batches for efficiency:

```
batch_size = 100
batch = []

async for event in client.events.stream(event_filter):
    batch.append(event)

    if len(batch) >= batch_size:
        process_batch(batch)
        batch = []

# Process remaining
if batch:
    process_batch(batch)
```

## GKG Streaming

Stream GKG records similarly:

```
from py_gdelt.filters import GKGFilter

gkg_filter = GKGFilter(
    date_range=DateRange(start=date(2024, 1, 1)),
    themes=["ENV_CLIMATECHANGE"],
)

async for record in client.gkg.stream(gkg_filter):
    # Process GKG record
    for theme in record.themes:
        print(theme.name)
```

## NGrams Streaming

Stream word/phrase occurrences:

```
from py_gdelt.filters import NGramsFilter

ngrams_filter = NGramsFilter(
    date_range=DateRange(start=date(2024, 1, 1)),
    ngram="climate",
    language="en",
)

async for ngram in client.ngrams.stream(ngrams_filter):
    print(f"{ngram.context}")
```

## Memory Monitoring

Track memory usage during streaming:

```
import psutil
import os

process = psutil.Process(os.getpid())

count = 0
async for event in client.events.stream(event_filter):
    count += 1

    if count % 10000 == 0:
        mem_mb = process.memory_info().rss / 1024 / 1024
        print(f"Processed {count} events, Memory: {mem_mb:.2f} MB")
```

## Error Handling

Handle errors gracefully during streaming:

```
from py_gdelt.exceptions import DataError

try:
    async for event in client.events.stream(event_filter):
        try:
            process(event)
        except Exception as e:
            # Log and continue
            logger.error(f"Error processing event: {e}")
            continue
except DataError as e:
    logger.error(f"Data stream error: {e}")
```

## Comparison: Query vs Stream

```
# query() - Loads all into memory
result = await client.events.query(event_filter)
for event in result:
    process(event)
# Memory: ~500MB for 100k events

# stream() - Process incrementally
async for event in client.events.stream(event_filter):
    process(event)
# Memory: ~50MB constant
```

## Best Practices

- Use `stream()` for >1000 records
- Use `query()` for \<1000 records (simpler)
- Batch processing for efficiency
- Handle errors per-record, not per-stream
- Monitor memory in production
- Use early exit to save resources
- Apply filters early to reduce data volume
