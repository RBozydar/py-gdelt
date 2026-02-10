# Global Knowledge Graph (GKG)

The GKG endpoint provides rich semantic metadata extracted from news articles.

## Overview

GKG records contain:
- Themes (ENV_CLIMATE, ECON_STOCKMARKET, etc.)
- Entities (people, organizations, locations)
- Quotations
- Tone/sentiment
- Source metadata

## Basic Usage

```python
from py_gdelt import GDELTClient
from py_gdelt.filters import DateRange, GKGFilter
from datetime import date

async with GDELTClient() as client:
    gkg_filter = GKGFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        themes=["ENV_CLIMATECHANGE"],
    )

    records = await client.gkg.query(gkg_filter)
```

For details, see [GKG example](../examples/basic.md).

## Analytics (BigQuery)

When BigQuery is configured, analytics methods are available on the GKG endpoint.

### Theme Counting

```python
from py_gdelt import GDELTClient
from py_gdelt.filters import DateRange, GKGFilter
from datetime import date

async with GDELTClient(settings=settings) as client:
    gkg_filter = GKGFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
    )

    # Top 50 themes by frequency
    themes = await client.gkg.aggregate_themes(gkg_filter, top_n=50)
    for row in themes.rows:
        print(f"{row['themes']}: {row['count']}")
```

### Approximate Top-N (High Cardinality)

```python
    from py_gdelt import GKGUnnestField

    # Efficient approximate counting for entities
    top_persons = await client.gkg.approx_top(
        gkg_filter,
        field=GKGUnnestField.PERSONS,
        n=20,
    )
    for row in top_persons.rows:
        print(f"{row['name']}: ~{row['count']}")
```

See the [Analytics API Reference](../api/analytics.md) for full details.
