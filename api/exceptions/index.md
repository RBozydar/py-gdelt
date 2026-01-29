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
└── SecurityError
```

## Base Exception

### `GDELTError`

Bases: `Exception`

Base exception for all GDELT client errors.

All custom exceptions in this library inherit from this class, allowing consumers to catch all library-specific errors with a single handler.

Source code in `src/py_gdelt/exceptions.py`

```
class GDELTError(Exception):
    """
    Base exception for all GDELT client errors.

    All custom exceptions in this library inherit from this class,
    allowing consumers to catch all library-specific errors with a single handler.
    """
```

## API Exceptions

### `APIError`

Bases: `GDELTError`

Base exception for all API-related errors.

Raised when errors occur during communication with GDELT REST APIs.

Source code in `src/py_gdelt/exceptions.py`

```
class APIError(GDELTError):
    """
    Base exception for all API-related errors.

    Raised when errors occur during communication with GDELT REST APIs.
    """
```

### `RateLimitError`

Bases: `APIError`

Raised when API rate limits are exceeded.

Parameters:

| Name          | Type  | Description       | Default                                                                                    |
| ------------- | ----- | ----------------- | ------------------------------------------------------------------------------------------ |
| `message`     | `str` | Error description | *required*                                                                                 |
| `retry_after` | \`int | None\`            | Optional number of seconds to wait before retrying. None if the retry duration is unknown. |

Source code in `src/py_gdelt/exceptions.py`

```
class RateLimitError(APIError):
    """
    Raised when API rate limits are exceeded.

    Args:
        message: Error description
        retry_after: Optional number of seconds to wait before retrying.
                    None if the retry duration is unknown.
    """

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after

    def __str__(self) -> str:
        """Return string representation including retry information."""
        base_message = super().__str__()
        if self.retry_after is not None:
            return f"{base_message} (retry after {self.retry_after} seconds)"
        return base_message
```

#### `__str__()`

Return string representation including retry information.

Source code in `src/py_gdelt/exceptions.py`

```
def __str__(self) -> str:
    """Return string representation including retry information."""
    base_message = super().__str__()
    if self.retry_after is not None:
        return f"{base_message} (retry after {self.retry_after} seconds)"
    return base_message
```

### `APIUnavailableError`

Bases: `APIError`

Raised when a GDELT API is temporarily unavailable.

This typically indicates server-side issues or maintenance windows. Consider falling back to BigQuery when this occurs.

Source code in `src/py_gdelt/exceptions.py`

```
class APIUnavailableError(APIError):
    """
    Raised when a GDELT API is temporarily unavailable.

    This typically indicates server-side issues or maintenance windows.
    Consider falling back to BigQuery when this occurs.
    """
```

### `InvalidQueryError`

Bases: `APIError`

Raised when API request parameters are invalid.

This indicates a client-side error in query construction or parameters.

Source code in `src/py_gdelt/exceptions.py`

```
class InvalidQueryError(APIError):
    """
    Raised when API request parameters are invalid.

    This indicates a client-side error in query construction or parameters.
    """
```

## Data Exceptions

### `DataError`

Bases: `GDELTError`

Base exception for data processing and validation errors.

Raised when errors occur during data parsing, transformation, or validation.

Source code in `src/py_gdelt/exceptions.py`

```
class DataError(GDELTError):
    """
    Base exception for data processing and validation errors.

    Raised when errors occur during data parsing, transformation, or validation.
    """
```

### `ParseError`

Bases: `DataError`, `ValueError`

Raised when data parsing fails.

Parameters:

| Name       | Type  | Description       | Default                                                         |
| ---------- | ----- | ----------------- | --------------------------------------------------------------- |
| `message`  | `str` | Error description | *required*                                                      |
| `raw_data` | \`str | None\`            | Optional raw data that failed to parse, for debugging purposes. |

Source code in `src/py_gdelt/exceptions.py`

```
class ParseError(DataError, ValueError):
    """
    Raised when data parsing fails.

    Args:
        message: Error description
        raw_data: Optional raw data that failed to parse, for debugging purposes.
    """

    def __init__(self, message: str, raw_data: str | None = None) -> None:
        super().__init__(message)
        self.raw_data = raw_data

    def __str__(self) -> str:
        """Return string representation with truncated raw data if available."""
        base_message = super().__str__()
        if self.raw_data is not None:
            # Truncate raw data to first 100 characters for readability
            truncated = self.raw_data[:100]
            if len(self.raw_data) > 100:
                truncated += "..."
            return f"{base_message} (raw data: {truncated!r})"
        return base_message
```

#### `__str__()`

Return string representation with truncated raw data if available.

Source code in `src/py_gdelt/exceptions.py`

```
def __str__(self) -> str:
    """Return string representation with truncated raw data if available."""
    base_message = super().__str__()
    if self.raw_data is not None:
        # Truncate raw data to first 100 characters for readability
        truncated = self.raw_data[:100]
        if len(self.raw_data) > 100:
            truncated += "..."
        return f"{base_message} (raw data: {truncated!r})"
    return base_message
```

### `ValidationError`

Bases: `DataError`

Raised when data validation fails.

This includes Pydantic validation errors and custom validation logic.

Source code in `src/py_gdelt/exceptions.py`

```
class ValidationError(DataError):
    """
    Raised when data validation fails.

    This includes Pydantic validation errors and custom validation logic.
    """
```

### `InvalidCodeError`

Bases: `ValidationError`

Raised when an invalid GDELT code is encountered.

Parameters:

| Name          | Type        | Description                                              | Default                                 |
| ------------- | ----------- | -------------------------------------------------------- | --------------------------------------- |
| `message`     | `str`       | Error description                                        | *required*                              |
| `code`        | `str`       | The invalid code value                                   | *required*                              |
| `code_type`   | `str`       | Type of code (e.g., "cameo", "theme", "country", "fips") | *required*                              |
| `suggestions` | \`list[str] | None\`                                                   | Optional list of suggested valid codes  |
| `help_url`    | \`str       | None\`                                                   | Optional URL to reference documentation |

Source code in `src/py_gdelt/exceptions.py`

```
class InvalidCodeError(ValidationError):
    """
    Raised when an invalid GDELT code is encountered.

    Args:
        message: Error description
        code: The invalid code value
        code_type: Type of code (e.g., "cameo", "theme", "country", "fips")
        suggestions: Optional list of suggested valid codes
        help_url: Optional URL to reference documentation
    """

    def __init__(
        self,
        message: str,
        code: str,
        code_type: str,
        suggestions: list[str] | None = None,
        help_url: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.code_type = code_type
        self.suggestions = suggestions or []
        self.help_url = help_url

    def __str__(self) -> str:
        """Return string representation including code details and guidance."""
        base_message = super().__str__()

        # Always include code and code_type in the base representation (backward compatibility)
        lines = [f"{base_message} (code={self.code!r}, type={self.code_type!r})"]

        # Add country-specific help
        if self.code_type == "country":
            lines.extend(
                [
                    "",
                    "Accepted formats:",
                    "  - FIPS (2 chars): US, UK, IR, FR, GM, CH, RS",
                    "  - ISO3 (3 chars): USA, GBR, IRN, FRA, DEU, CHN, RUS",
                ]
            )

        # Add suggestions if available
        if self.suggestions:
            lines.extend(["", f"Did you mean: {', '.join(self.suggestions)}?"])

        # Add reference URL if available
        if self.help_url:
            lines.extend(["", f"Reference: {self.help_url}"])

        return "\n".join(lines)
```

#### `__str__()`

Return string representation including code details and guidance.

Source code in `src/py_gdelt/exceptions.py`

```
def __str__(self) -> str:
    """Return string representation including code details and guidance."""
    base_message = super().__str__()

    # Always include code and code_type in the base representation (backward compatibility)
    lines = [f"{base_message} (code={self.code!r}, type={self.code_type!r})"]

    # Add country-specific help
    if self.code_type == "country":
        lines.extend(
            [
                "",
                "Accepted formats:",
                "  - FIPS (2 chars): US, UK, IR, FR, GM, CH, RS",
                "  - ISO3 (3 chars): USA, GBR, IRN, FRA, DEU, CHN, RUS",
            ]
        )

    # Add suggestions if available
    if self.suggestions:
        lines.extend(["", f"Did you mean: {', '.join(self.suggestions)}?"])

    # Add reference URL if available
    if self.help_url:
        lines.extend(["", f"Reference: {self.help_url}"])

    return "\n".join(lines)
```

## Other Exceptions

### `ConfigurationError`

Bases: `GDELTError`

Raised when client configuration is invalid or incomplete.

This includes missing credentials, invalid settings, or misconfiguration.

Source code in `src/py_gdelt/exceptions.py`

```
class ConfigurationError(GDELTError):
    """
    Raised when client configuration is invalid or incomplete.

    This includes missing credentials, invalid settings, or misconfiguration.
    """
```

### `BigQueryError`

Bases: `GDELTError`

Raised when BigQuery operations fail.

This includes query execution errors, authentication failures, and quota/billing issues.

Source code in `src/py_gdelt/exceptions.py`

```
class BigQueryError(GDELTError):
    """
    Raised when BigQuery operations fail.

    This includes query execution errors, authentication failures,
    and quota/billing issues.
    """
```

### `SecurityError`

Bases: `GDELTError`

Raised when a security check fails.

This includes URL validation failures, path traversal detection, zip bomb detection, and other security-related issues.

Source code in `src/py_gdelt/exceptions.py`

```
class SecurityError(GDELTError):
    """
    Raised when a security check fails.

    This includes URL validation failures, path traversal detection,
    zip bomb detection, and other security-related issues.
    """
```

## Usage

```
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
