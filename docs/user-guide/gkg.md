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
