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
import asyncio
import logging

from py_gdelt.exceptions import APIError, DataError, RateLimitError

logger = logging.getLogger(__name__)

try:
    result = await client.doc.query(doc_filter)
except RateLimitError as e:
    # Retry-After is parsed from either seconds or an HTTP-date header.
    if e.retry_after is not None:
        await asyncio.sleep(e.retry_after)
except APIError as e:
    # Handle other API errors (network, unavailable, invalid response, etc.)
    logger.error("API error: %s", e)
except DataError as e:
    # Handle data parsing errors
    logger.error("Data error: %s", e)
except Exception as e:
    # Handle unexpected errors
    logger.error("Unexpected error: %s", e)
```

By default, REST endpoint instances fail fast after a `429 Too Many Requests`
response. Further calls through the same endpoint instance raise
`RateLimitError` locally until the parsed `Retry-After` value or configured
fallback circuit expires.

For details, see [API reference](../api/exceptions.md).
