# Deduplication

GDELT data often contains duplicates. Use deduplication strategies to clean data.

## Strategies

- `URL_ONLY` - Deduplicate by source URL
- `URL_DATE` - By URL and date
- `URL_DATE_LOCATION` - By URL, date, and location
- `ACTOR_PAIR` - By actor pair
- `FULL` - By all fields

## Usage

```
from py_gdelt.utils.dedup import DedupeStrategy

result = await client.events.query(
    event_filter,
    deduplicate=True,
    dedupe_strategy=DedupeStrategy.URL_DATE_LOCATION,
)
```

For details, see [Events guide](https://rbozydar.github.io/py-gdelt/user-guide/events/index.md).
