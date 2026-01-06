# NGrams

Query word and phrase occurrences from GDELT NGrams 3.0.

## Overview

NGrams track word/phrase positions within articles for linguistic analysis.

## Basic Usage

```python
from py_gdelt import GDELTClient
from py_gdelt.filters import DateRange, NGramsFilter
from datetime import date

async with GDELTClient() as client:
    ngrams_filter = NGramsFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        ngram="climate",
        language="en",
    )

    records = await client.ngrams.query(ngrams_filter)
```

For details, see [NGrams example](../examples/basic.md).
