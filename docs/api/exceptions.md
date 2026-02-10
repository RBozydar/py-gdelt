# Exceptions API

Exception hierarchy for error handling.

## Exception Hierarchy

```
GDELTError (base)
├── APIError
│   ├── RateLimitError
│   ├── APIUnavailableError
│   └── InvalidQueryError
├── DataError
│   ├── ParseError
│   └── ValidationError
│       └── InvalidCodeError
├── ConfigurationError
├── BigQueryError
│   └── BudgetExceededError
└── SecurityError
```

## Base Exception

::: py_gdelt.exceptions.GDELTError
    options:
      show_root_heading: true
      heading_level: 3

## API Exceptions

::: py_gdelt.exceptions.APIError
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.exceptions.RateLimitError
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.exceptions.APIUnavailableError
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.exceptions.InvalidQueryError
    options:
      show_root_heading: true
      heading_level: 3

## Data Exceptions

::: py_gdelt.exceptions.DataError
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.exceptions.ParseError
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.exceptions.ValidationError
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.exceptions.InvalidCodeError
    options:
      show_root_heading: true
      heading_level: 3

## Other Exceptions

::: py_gdelt.exceptions.ConfigurationError
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.exceptions.BigQueryError
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.exceptions.BudgetExceededError
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.exceptions.SecurityError
    options:
      show_root_heading: true
      heading_level: 3

## Usage

```python
import asyncio
import logging

from py_gdelt.exceptions import APIError, RateLimitError, DataError

logger = logging.getLogger(__name__)

try:
    result = await client.doc.query(doc_filter)
except RateLimitError as e:
    # Handle rate limiting with retry info
    if e.retry_after:
        await asyncio.sleep(e.retry_after)
except APIError as e:
    # Handle other API errors (network, unavailable, etc.)
    logger.error(f"API error: {e}")
except DataError as e:
    # Handle data parsing errors
    logger.error(f"Data error: {e}")
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
```
