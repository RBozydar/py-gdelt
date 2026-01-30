"""
Exception hierarchy for the GDELT Python client library.

This module defines a comprehensive exception hierarchy for all error conditions
that can occur when interacting with GDELT APIs, data sources, and BigQuery.

Exception Hierarchy:
    GDELTError (base)
    ├── APIError
    │   ├── RateLimitError (with retry_after: int | None)
    │   ├── APIUnavailableError
    │   └── InvalidQueryError
    ├── DataError
    │   ├── ParseError (with raw_data: str | None)
    │   └── ValidationError
    │       └── InvalidCodeError (with code: str, code_type: str)
    ├── ConfigurationError
    ├── BigQueryError
    └── SecurityError
"""

__all__ = [
    "APIError",
    "APIUnavailableError",
    "BigQueryError",
    "ConfigurationError",
    "DataError",
    "GDELTError",
    "InvalidCodeError",
    "InvalidQueryError",
    "ParseError",
    "RateLimitError",
    "SecurityError",
    "ValidationError",
]


class GDELTError(Exception):
    """
    Base exception for all GDELT client errors.

    All custom exceptions in this library inherit from this class,
    allowing consumers to catch all library-specific errors with a single handler.
    """


class APIError(GDELTError):
    """
    Base exception for all API-related errors.

    Raised when errors occur during communication with GDELT REST APIs.
    """


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


class APIUnavailableError(APIError):
    """
    Raised when a GDELT API is temporarily unavailable.

    This typically indicates server-side issues or maintenance windows.
    Consider falling back to BigQuery when this occurs.
    """


class InvalidQueryError(APIError):
    """
    Raised when API request parameters are invalid.

    This indicates a client-side error in query construction or parameters.

    Args:
        message: The original error message from GDELT API.
        hint: Optional hint with guidance on how to fix the query.
    """

    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message)
        self.hint = hint

    def __str__(self) -> str:
        """Return string representation with hint if available."""
        base_message = super().__str__()
        if self.hint:
            return f"{base_message}\n\nHint: {self.hint}"
        return base_message


# Query error patterns and their hints for GDELT DOC API
_QUERY_ERROR_HINTS: dict[str, str] = {
    "parentheses may only be used around or'd statements": (
        "Parentheses can ONLY wrap OR groups like '(A OR B)'. "
        "Remove parentheses from single terms or phrases.\n"
        "  Wrong: '(climate change) AND policy'\n"
        "  Right: '\"climate change\" AND policy'\n"
        "  Right: '(climate OR weather) AND policy'"
    ),
    "illegal character": (
        "Special characters (dashes, dots, etc.) require quotes.\n"
        "  Wrong: 'US-EU relations' or 'F-16 fighter'\n"
        "  Right: '\"US-EU\" relations' or '\"F-16\" fighter'"
    ),
    "query must contain at least one non-stopword": (
        "Your query contains only common words (the, a, is, etc.). Add more specific search terms."
    ),
    "query is too long": ("Simplify your query by removing terms or using fewer OR groups."),
}


def _enhance_query_error(raw_message: str) -> tuple[str, str | None]:
    """Enhance GDELT API error messages with actionable hints.

    Args:
        raw_message: The raw error message from GDELT API.

    Returns:
        Tuple of (message, hint) where hint may be None if no pattern matched.
    """
    message_lower = raw_message.lower()
    for pattern, hint in _QUERY_ERROR_HINTS.items():
        if pattern in message_lower:
            return raw_message, hint
    return raw_message, None


def _is_query_error(raw_message: str) -> bool:
    """Check if an error message indicates a query syntax error.

    Args:
        raw_message: The raw error message from GDELT API.

    Returns:
        True if this appears to be a query syntax error.
    """
    message_lower = raw_message.lower()
    query_error_indicators = [
        "parentheses",
        "illegal character",
        "query must contain",
        "query is too",
        "keyword",
        "search term",
    ]
    return any(indicator in message_lower for indicator in query_error_indicators)


class DataError(GDELTError):
    """
    Base exception for data processing and validation errors.

    Raised when errors occur during data parsing, transformation, or validation.
    """


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


class ValidationError(DataError):
    """
    Raised when data validation fails.

    This includes Pydantic validation errors and custom validation logic.
    """


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


class ConfigurationError(GDELTError):
    """
    Raised when client configuration is invalid or incomplete.

    This includes missing credentials, invalid settings, or misconfiguration.
    """


class BigQueryError(GDELTError):
    """
    Raised when BigQuery operations fail.

    This includes query execution errors, authentication failures,
    and quota/billing issues.
    """


class SecurityError(GDELTError):
    """
    Raised when a security check fails.

    This includes URL validation failures, path traversal detection,
    zip bomb detection, and other security-related issues.
    """
