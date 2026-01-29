# Advanced Patterns

Production-ready patterns for py-gdelt.

## Custom Configuration

```
from pathlib import Path
from py_gdelt import GDELTClient, GDELTSettings

settings = GDELTSettings(
    timeout=60,
    max_retries=5,
    cache_dir=Path("/custom/cache"),
    fallback_to_bigquery=True,
)

async with GDELTClient(settings=settings) as client:
    ...
```

## Error Handling

```
from py_gdelt.exceptions import APIError, DataError

try:
    result = await client.doc.query(doc_filter)
except APIError as e:
    logger.error(f"API error: {e}")
except DataError as e:
    logger.error(f"Data error: {e}")
```

## Streaming Large Datasets

```
async for event in client.events.stream(event_filter):
    process(event)  # Memory-efficient
```

See `notebooks/02_advanced_patterns.ipynb` for detailed examples.
