# Error Handling

Proper error handling for robust applications.

## Exception Hierarchy

- `GDELTError` - Base exception
  - `APIError` - API-related errors
  - `DataError` - Data parsing errors
  - `SecurityError` - Security violations
  - `ConfigurationError` - Configuration issues

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

For details, see [API reference](../api/exceptions.md).
