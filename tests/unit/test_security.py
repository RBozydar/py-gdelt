"""Unit tests for security utilities."""

import logging
from pathlib import Path

import pytest

from py_gdelt._security import (
    ALLOWED_HOSTS,
    MAX_COMPRESSION_RATIO,
    MAX_DECOMPRESSED_SIZE,
    SecurityError,
    check_decompression_safety,
    safe_cache_path,
    validate_url,
)


logger = logging.getLogger(__name__)


class TestSecurityError:
    """Test SecurityError exception."""

    def test_security_error_is_exception(self) -> None:
        """SecurityError should be a subclass of Exception."""
        assert issubclass(SecurityError, Exception)

    def test_security_error_message(self) -> None:
        """SecurityError should accept and preserve message."""
        error = SecurityError("Test security violation")
        assert str(error) == "Test security violation"


class TestSafeCachePath:
    """Test safe_cache_path function."""

    def test_valid_simple_filename(self, tmp_path: Path) -> None:
        """Should accept simple valid filename."""
        result = safe_cache_path(tmp_path, "data.csv")
        assert result == tmp_path / "data.csv"
        assert result.parent == tmp_path

    def test_valid_filename_with_extension(self, tmp_path: Path) -> None:
        """Should accept filename with multiple extensions."""
        result = safe_cache_path(tmp_path, "export.2024.csv.zip")
        assert result == tmp_path / "export.2024.csv.zip"
        assert result.parent == tmp_path

    def test_valid_filename_with_underscores(self, tmp_path: Path) -> None:
        """Should accept filename with underscores."""
        result = safe_cache_path(tmp_path, "gdelt_events_export.csv")
        assert result == tmp_path / "gdelt_events_export.csv"

    def test_valid_filename_with_hyphens(self, tmp_path: Path) -> None:
        """Should accept filename with hyphens."""
        result = safe_cache_path(tmp_path, "2024-01-01-export.csv")
        assert result == tmp_path / "2024-01-01-export.csv"

    def test_parent_directory_traversal(self, tmp_path: Path) -> None:
        """Should reject path traversal with parent directory reference."""
        with pytest.raises(SecurityError, match="Path traversal detected"):
            safe_cache_path(tmp_path, "../etc/passwd")

    def test_current_directory_traversal(self, tmp_path: Path) -> None:
        """Should reject path traversal with current directory reference."""
        with pytest.raises(SecurityError, match="Path traversal detected"):
            safe_cache_path(tmp_path, "./../../etc/passwd")

    def test_absolute_path_attempt(self, tmp_path: Path) -> None:
        """Should reject absolute path attempts."""
        with pytest.raises(SecurityError, match="Path traversal detected"):
            safe_cache_path(tmp_path, "/etc/passwd")

    def test_mixed_traversal_attempt(self, tmp_path: Path) -> None:
        """Should reject mixed traversal attempts."""
        with pytest.raises(SecurityError, match="Path traversal detected"):
            safe_cache_path(tmp_path, "foo/../../../bar")

    def test_hidden_file_is_allowed(self, tmp_path: Path) -> None:
        """Should allow hidden files (starting with dot)."""
        result = safe_cache_path(tmp_path, ".hidden_cache")
        assert result == tmp_path / ".hidden_cache"
        assert result.parent == tmp_path

    def test_windows_path_separator(self, tmp_path: Path) -> None:
        """Should reject Windows-style path separators."""
        with pytest.raises(SecurityError, match="Path traversal detected"):
            safe_cache_path(tmp_path, "..\\windows\\system32")

    def test_null_byte_injection(self, tmp_path: Path) -> None:
        """Should reject null byte injection attempts."""
        with pytest.raises(SecurityError, match="Path traversal detected"):
            safe_cache_path(tmp_path, "file.txt\x00.exe")

    def test_result_is_within_cache_dir(self, tmp_path: Path) -> None:
        """Resolved path should always be within cache directory."""
        result = safe_cache_path(tmp_path, "subdir/file.txt")
        # Result should be relative to cache_dir and not escape it
        assert result.resolve().is_relative_to(tmp_path.resolve())

    def test_symlink_traversal_attempt(self, tmp_path: Path) -> None:
        """Should prevent symlink-based traversal attempts."""
        # This tests the filename itself contains traversal, not actual symlinks
        with pytest.raises(SecurityError, match="Path traversal detected"):
            safe_cache_path(tmp_path, "link/../../../etc")


class TestValidateUrl:
    """Test validate_url function."""

    def test_valid_gdelt_api_url(self) -> None:
        """Should accept valid GDELT API URL."""
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        result = validate_url(url)
        assert result == url

    def test_valid_gdelt_data_url(self) -> None:
        """Should accept valid GDELT data URL."""
        url = "https://data.gdeltproject.org/events/20240101.export.CSV.zip"
        result = validate_url(url)
        assert result == url

    def test_http_url_rejected(self) -> None:
        """Should reject HTTP (non-HTTPS) URLs."""
        with pytest.raises(SecurityError, match="URL must use HTTPS"):
            validate_url("http://api.gdeltproject.org/api/v2/doc/doc")

    def test_invalid_host_rejected(self) -> None:
        """Should reject URLs from non-allowed hosts."""
        with pytest.raises(SecurityError, match="not an allowed GDELT host"):
            validate_url("https://evil.example.com/api/v2/doc/doc")

    def test_subdomain_attack_rejected(self) -> None:
        """Should reject subdomain-based attacks."""
        with pytest.raises(SecurityError, match="not an allowed GDELT host"):
            validate_url("https://api.gdeltproject.org.evil.com/data")

    def test_missing_scheme(self) -> None:
        """Should reject URLs without scheme."""
        with pytest.raises(SecurityError, match="URL must use HTTPS"):
            validate_url("api.gdeltproject.org/api/v2/doc/doc")

    def test_empty_url(self) -> None:
        """Should reject empty URLs."""
        with pytest.raises(SecurityError, match="Invalid URL"):
            validate_url("")

    def test_malformed_url(self) -> None:
        """Should reject malformed URLs."""
        with pytest.raises(SecurityError, match="Invalid URL"):
            validate_url("https://[invalid")

    def test_url_without_hostname(self) -> None:
        """Should reject URLs without hostname."""
        with pytest.raises(SecurityError, match="Invalid URL: missing hostname"):
            validate_url("https:///path/to/resource")

    def test_url_with_credentials_rejected(self) -> None:
        """Should reject URLs containing credentials."""
        with pytest.raises(SecurityError, match="URL must not contain credentials"):
            validate_url("https://user:pass@api.gdeltproject.org/api")

    def test_url_with_username_only_rejected(self) -> None:
        """Should reject URLs with username but no password."""
        with pytest.raises(SecurityError, match="URL must not contain credentials"):
            validate_url("https://user@api.gdeltproject.org/api")

    def test_allowed_hosts_is_frozen(self) -> None:
        """ALLOWED_HOSTS should be immutable frozenset."""
        assert isinstance(ALLOWED_HOSTS, frozenset)
        assert "api.gdeltproject.org" in ALLOWED_HOSTS
        assert "data.gdeltproject.org" in ALLOWED_HOSTS


class TestCheckDecompressionSafety:
    """Test check_decompression_safety function."""

    def test_normal_compression_accepted(self) -> None:
        """Should accept normal compression ratios."""
        # 10MB compressed -> 50MB decompressed (5x ratio)
        check_decompression_safety(10 * 1024 * 1024, 50 * 1024 * 1024)

    def test_maximum_allowed_size(self) -> None:
        """Should accept maximum allowed decompressed size."""
        # Exactly at the limit
        check_decompression_safety(100 * 1024 * 1024, MAX_DECOMPRESSED_SIZE)

    def test_exceeds_maximum_size(self) -> None:
        """Should reject decompressed size exceeding limit."""
        # 501MB exceeds 500MB limit
        with pytest.raises(SecurityError, match="exceeds maximum allowed size"):
            check_decompression_safety(10 * 1024 * 1024, 501 * 1024 * 1024)

    def test_suspicious_compression_ratio(self) -> None:
        """Should reject suspicious compression ratios (zip bombs)."""
        # 1MB compressed -> 200MB decompressed (200x ratio, exceeds 100x limit)
        with pytest.raises(SecurityError, match="Suspicious compression ratio"):
            check_decompression_safety(1 * 1024 * 1024, 200 * 1024 * 1024)

    def test_extreme_zip_bomb(self) -> None:
        """Should reject extreme zip bomb attempts."""
        # 1KB compressed -> 100MB decompressed (100,000x ratio)
        with pytest.raises(SecurityError, match="Suspicious compression ratio"):
            check_decompression_safety(1024, 100 * 1024 * 1024)

    def test_maximum_allowed_ratio(self) -> None:
        """Should accept maximum allowed compression ratio."""
        # Exactly at 100x ratio
        compressed = 5 * 1024 * 1024  # 5MB
        decompressed = compressed * MAX_COMPRESSION_RATIO  # 500MB (100x)
        check_decompression_safety(compressed, decompressed)

    def test_zero_compressed_size(self) -> None:
        """Should handle zero compressed size gracefully."""
        # Zero compressed size would cause division by zero
        with pytest.raises(SecurityError, match="Invalid compressed size"):
            check_decompression_safety(0, 1000)

    def test_negative_sizes_rejected(self) -> None:
        """Should reject negative sizes."""
        with pytest.raises(SecurityError, match="Invalid"):
            check_decompression_safety(-100, 1000)

        with pytest.raises(SecurityError, match="Invalid"):
            check_decompression_safety(100, -1000)

    def test_very_small_file(self) -> None:
        """Should accept very small files."""
        # 1KB compressed -> 10KB decompressed (10x ratio)
        check_decompression_safety(1024, 10 * 1024)

    def test_constants_defined(self) -> None:
        """Security constants should be defined correctly."""
        assert MAX_DECOMPRESSED_SIZE == 500 * 1024 * 1024
        assert MAX_COMPRESSION_RATIO == 100


class TestSecurityIntegration:
    """Integration tests for security utilities."""

    def test_multiple_security_checks(self, tmp_path: Path) -> None:
        """Should handle multiple security checks in sequence."""
        # Valid path check
        cache_path = safe_cache_path(tmp_path, "data.csv")
        assert cache_path.parent == tmp_path

        # Valid URL check
        url = validate_url("https://api.gdeltproject.org/api/v2/doc/doc")
        assert url.startswith("https://")

        # Valid decompression check
        check_decompression_safety(10 * 1024 * 1024, 50 * 1024 * 1024)

    def test_all_security_checks_fail_independently(self, tmp_path: Path) -> None:
        """Each security check should fail independently."""
        # Path traversal should fail
        with pytest.raises(SecurityError, match="Path traversal"):
            safe_cache_path(tmp_path, "../../../etc/passwd")

        # Invalid URL should fail
        with pytest.raises(SecurityError, match="not an allowed GDELT host"):
            validate_url("https://evil.com/data")

        # Zip bomb should fail (1MB compressed -> 200MB decompressed = 200x ratio)
        with pytest.raises(SecurityError, match="Suspicious compression ratio"):
            check_decompression_safety(1 * 1024 * 1024, 200 * 1024 * 1024)
