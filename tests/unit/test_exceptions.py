"""
Unit tests for py_gdelt.exceptions module.

Tests verify exception hierarchy, initialization, attributes, and string representations.
"""

import pytest

from py_gdelt.exceptions import (
    APIError,
    APIUnavailableError,
    BigQueryError,
    ConfigurationError,
    DataError,
    GDELTError,
    InvalidCodeError,
    InvalidQueryError,
    ParseError,
    RateLimitError,
    SecurityError,
    ValidationError,
)


class TestGDELTError:
    """Tests for base GDELTError exception."""

    def test_inheritance(self):
        """GDELTError should inherit from Exception."""
        assert issubclass(GDELTError, Exception)

    def test_basic_initialization(self):
        """GDELTError should accept a message."""
        error = GDELTError("Something went wrong")
        assert str(error) == "Something went wrong"

    def test_raise_and_catch(self):
        """GDELTError should be raiseable and catchable."""
        msg = "Test error"
        with pytest.raises(GDELTError, match="Test error"):
            raise GDELTError(msg)


class TestAPIError:
    """Tests for APIError and its subclasses."""

    def test_inheritance(self):
        """APIError should inherit from GDELTError."""
        assert issubclass(APIError, GDELTError)

    def test_basic_initialization(self):
        """APIError should accept a message."""
        error = APIError("API failed")
        assert str(error) == "API failed"

    def test_catch_as_base_class(self):
        """APIError should be catchable as GDELTError."""
        msg = "API error"
        with pytest.raises(GDELTError):
            raise APIError(msg)


class TestRateLimitError:
    """Tests for RateLimitError with retry_after attribute."""

    def test_inheritance(self):
        """RateLimitError should inherit from APIError."""
        assert issubclass(RateLimitError, APIError)

    def test_initialization_with_retry_after(self):
        """RateLimitError should accept and store retry_after."""
        error = RateLimitError("Rate limited", retry_after=60)
        assert error.retry_after == 60
        assert "Rate limited" in str(error)
        assert "60" in str(error)

    def test_initialization_without_retry_after(self):
        """RateLimitError should allow None for retry_after."""
        error = RateLimitError("Rate limited", retry_after=None)
        assert error.retry_after is None
        assert "Rate limited" in str(error)

    def test_default_retry_after(self):
        """RateLimitError should default retry_after to None."""
        error = RateLimitError("Rate limited")
        assert error.retry_after is None

    def test_string_representation_with_retry(self):
        """String representation should include retry_after when present."""
        error = RateLimitError("Too many requests", retry_after=120)
        error_str = str(error)
        assert "Too many requests" in error_str
        assert "120" in error_str
        assert "retry" in error_str.lower()

    def test_string_representation_without_retry(self):
        """String representation should work without retry_after."""
        error = RateLimitError("Too many requests", retry_after=None)
        error_str = str(error)
        assert "Too many requests" in error_str


class TestAPIUnavailableError:
    """Tests for APIUnavailableError."""

    def test_inheritance(self):
        """APIUnavailableError should inherit from APIError."""
        assert issubclass(APIUnavailableError, APIError)

    def test_basic_initialization(self):
        """APIUnavailableError should accept a message."""
        error = APIUnavailableError("Service down")
        assert str(error) == "Service down"


class TestInvalidQueryError:
    """Tests for InvalidQueryError."""

    def test_inheritance(self):
        """InvalidQueryError should inherit from APIError."""
        assert issubclass(InvalidQueryError, APIError)

    def test_basic_initialization(self):
        """InvalidQueryError should accept a message."""
        error = InvalidQueryError("Invalid parameters")
        assert str(error) == "Invalid parameters"


class TestDataError:
    """Tests for DataError and its subclasses."""

    def test_inheritance(self):
        """DataError should inherit from GDELTError."""
        assert issubclass(DataError, GDELTError)

    def test_basic_initialization(self):
        """DataError should accept a message."""
        error = DataError("Data corrupted")
        assert str(error) == "Data corrupted"


class TestParseError:
    """Tests for ParseError with raw_data attribute."""

    def test_inheritance(self):
        """ParseError should inherit from DataError and ValueError."""
        assert issubclass(ParseError, DataError)
        assert issubclass(ParseError, ValueError)

    def test_initialization_with_raw_data(self):
        """ParseError should accept and store raw_data."""
        raw = '{"invalid": json}'
        error = ParseError("Failed to parse JSON", raw_data=raw)
        assert error.raw_data == raw
        assert "Failed to parse JSON" in str(error)

    def test_initialization_without_raw_data(self):
        """ParseError should allow None for raw_data."""
        error = ParseError("Parse failed", raw_data=None)
        assert error.raw_data is None

    def test_default_raw_data(self):
        """ParseError should default raw_data to None."""
        error = ParseError("Parse failed")
        assert error.raw_data is None

    def test_string_representation_with_raw_data(self):
        """String representation should include truncated raw_data when present."""
        raw = "x" * 200
        error = ParseError("Parse failed", raw_data=raw)
        error_str = str(error)
        assert "Parse failed" in error_str
        # Should be truncated
        assert len(error_str) < len(raw) + 100

    def test_string_representation_without_raw_data(self):
        """String representation should work without raw_data."""
        error = ParseError("Parse failed", raw_data=None)
        error_str = str(error)
        assert error_str == "Parse failed"

    def test_raw_data_truncation(self):
        """Raw data should be truncated in string representation."""
        raw = "a" * 500
        error = ParseError("Parse failed", raw_data=raw)
        error_str = str(error)
        # Should contain truncation indicator
        assert "..." in error_str or len(error_str) < 500


class TestValidationError:
    """Tests for ValidationError."""

    def test_inheritance(self):
        """ValidationError should inherit from DataError."""
        assert issubclass(ValidationError, DataError)

    def test_basic_initialization(self):
        """ValidationError should accept a message."""
        error = ValidationError("Invalid field")
        assert str(error) == "Invalid field"


class TestInvalidCodeError:
    """Tests for InvalidCodeError with code and code_type attributes."""

    def test_inheritance(self):
        """InvalidCodeError should inherit from ValidationError."""
        assert issubclass(InvalidCodeError, ValidationError)

    def test_initialization_with_all_attributes(self):
        """InvalidCodeError should accept and store code and code_type."""
        error = InvalidCodeError("Invalid code", code="XX", code_type="cameo")
        assert error.code == "XX"
        assert error.code_type == "cameo"
        assert "Invalid code" in str(error)
        assert "XX" in str(error)
        assert "cameo" in str(error)

    def test_string_representation(self):
        """String representation should include code and code_type."""
        error = InvalidCodeError(
            "Code not found in lookup",
            code="ZZZ",
            code_type="theme",
        )
        error_str = str(error)
        assert "Code not found in lookup" in error_str
        assert "ZZZ" in error_str
        assert "theme" in error_str

    def test_different_code_types(self):
        """InvalidCodeError should work with different code types."""
        code_types = ["cameo", "theme", "country", "fips"]
        for code_type in code_types:
            error = InvalidCodeError(
                "Invalid",
                code="TEST",
                code_type=code_type,
            )
            assert error.code_type == code_type
            assert code_type in str(error)


class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_inheritance(self):
        """ConfigurationError should inherit from GDELTError."""
        assert issubclass(ConfigurationError, GDELTError)

    def test_basic_initialization(self):
        """ConfigurationError should accept a message."""
        error = ConfigurationError("Missing API key")
        assert str(error) == "Missing API key"


class TestBigQueryError:
    """Tests for BigQueryError."""

    def test_inheritance(self):
        """BigQueryError should inherit from GDELTError."""
        assert issubclass(BigQueryError, GDELTError)

    def test_basic_initialization(self):
        """BigQueryError should accept a message."""
        error = BigQueryError("Query execution failed")
        assert str(error) == "Query execution failed"


class TestSecurityError:
    """Tests for SecurityError."""

    def test_inheritance(self):
        """SecurityError should inherit from GDELTError."""
        assert issubclass(SecurityError, GDELTError)

    def test_basic_initialization(self):
        """SecurityError should accept a message."""
        error = SecurityError("Path traversal detected")
        assert str(error) == "Path traversal detected"


class TestExceptionHierarchy:
    """Tests for overall exception hierarchy relationships."""

    def test_all_inherit_from_gdelt_error(self):
        """All custom exceptions should inherit from GDELTError."""
        all_exceptions = [
            APIError,
            RateLimitError,
            APIUnavailableError,
            InvalidQueryError,
            DataError,
            ParseError,
            ValidationError,
            InvalidCodeError,
            ConfigurationError,
            BigQueryError,
            SecurityError,
        ]
        for exc_class in all_exceptions:
            assert issubclass(exc_class, GDELTError)

    def test_api_error_hierarchy(self):
        """Verify API error hierarchy."""
        assert issubclass(RateLimitError, APIError)
        assert issubclass(APIUnavailableError, APIError)
        assert issubclass(InvalidQueryError, APIError)

    def test_data_error_hierarchy(self):
        """Verify data error hierarchy."""
        assert issubclass(ParseError, DataError)
        assert issubclass(ValidationError, DataError)
        assert issubclass(InvalidCodeError, ValidationError)

    def test_catch_patterns(self):
        """Test common exception catching patterns."""
        msg = "Test"
        # Catch all GDELT errors
        with pytest.raises(GDELTError):
            raise InvalidCodeError(msg, code="X", code_type="test")

        # Catch all API errors
        with pytest.raises(APIError):
            raise RateLimitError(msg, retry_after=60)

        # Catch all data errors
        with pytest.raises(DataError):
            raise ParseError(msg, raw_data="bad data")

        # Catch validation errors
        with pytest.raises(ValidationError):
            raise InvalidCodeError(msg, code="X", code_type="test")


class TestExceptionExports:
    """Tests for module exports."""

    def test_all_exceptions_exported(self):
        """All exception classes should be in __all__."""
        from py_gdelt import exceptions

        expected_exports = {
            "GDELTError",
            "APIError",
            "RateLimitError",
            "APIUnavailableError",
            "InvalidQueryError",
            "DataError",
            "ParseError",
            "ValidationError",
            "InvalidCodeError",
            "ConfigurationError",
            "BigQueryError",
            "SecurityError",
        }
        assert hasattr(exceptions, "__all__")
        assert set(exceptions.__all__) == expected_exports

    def test_all_exports_importable(self):
        """All exports should be importable."""
        from py_gdelt.exceptions import __all__

        for name in __all__:
            assert name in globals() or name in dir()
