# Exceptions API

Exception hierarchy for error handling.

## Base Exceptions

::: py_gdelt.exceptions.GDELTError
    options:
      show_root_heading: true
      heading_level: 3

## Specific Exceptions

::: py_gdelt.exceptions.APIError
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.exceptions.DataError
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.exceptions.SecurityError
    options:
      show_root_heading: true
      heading_level: 3

::: py_gdelt.exceptions.ConfigurationError
    options:
      show_root_heading: true
      heading_level: 3

## Usage

```python
from py_gdelt.exceptions import APIError, DataError

try:
    result = await client.doc.query(doc_filter)
except APIError as e:
    # Handle API errors (rate limiting, network, etc.)
    logger.error(f"API error: {e}")
except DataError as e:
    # Handle data parsing errors
    logger.error(f"Data error: {e}")
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
```
