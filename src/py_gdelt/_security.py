"""Security utilities for GDELT client.

This module provides security checks for file operations, URL validation,
and decompression safety to prevent common attack vectors.
"""

import logging
from pathlib import Path
from urllib.parse import urlparse

from py_gdelt.exceptions import SecurityError


logger = logging.getLogger(__name__)

# Allowed GDELT hosts for URL validation
ALLOWED_HOSTS: frozenset[str] = frozenset({"api.gdeltproject.org", "data.gdeltproject.org"})

# Decompression safety limits
MAX_DECOMPRESSED_SIZE: int = 500 * 1024 * 1024  # 500MB
MAX_COMPRESSION_RATIO: int = 100

# Re-export SecurityError for backward compatibility
__all__ = ["SecurityError", "check_decompression_safety", "safe_cache_path", "validate_url"]


def safe_cache_path(cache_dir: Path, filename: str) -> Path:
    """Sanitize filename and ensure it stays within cache directory.

    This function prevents path traversal attacks by validating that the
    resolved path stays within the cache directory bounds. It checks for
    common attack patterns including parent directory references, absolute
    paths, null bytes, and Windows path separators.

    Args:
        cache_dir: The base cache directory
        filename: The filename to validate and join

    Returns:
        A Path object within the cache directory

    Raises:
        SecurityError: If path traversal is detected or filename is unsafe
    """
    # Check for null bytes (filesystem injection)
    if "\x00" in filename:
        logger.error("Null byte detected in filename: %s", repr(filename))
        raise SecurityError("Path traversal detected: null byte in filename")

    # Check for Windows path separators (even on Unix systems)
    if "\\" in filename:
        logger.error("Windows path separator detected: %s", filename)
        raise SecurityError("Path traversal detected: invalid path separator")

    # Create candidate path
    candidate = cache_dir / filename

    # Resolve both paths to handle symlinks and relative components
    resolved_cache = cache_dir.resolve()
    try:
        resolved_candidate = candidate.resolve()
    except (OSError, RuntimeError) as e:
        logger.error("Failed to resolve path %s: %s", candidate, e)
        raise SecurityError(f"Path traversal detected: {e}") from e

    # Verify the resolved path is within cache directory
    try:
        resolved_candidate.relative_to(resolved_cache)
    except ValueError as e:
        logger.error("Path traversal attempt: %s escapes %s", resolved_candidate, resolved_cache)
        raise SecurityError("Path traversal detected: path escapes cache directory") from e

    return candidate


def validate_url(url: str) -> str:
    """Validate URL is HTTPS and from allowed hosts.

    This function ensures that URLs are from trusted GDELT domains and use
    secure HTTPS connections. It prevents credential leakage and domain
    spoofing attacks.

    Args:
        url: The URL to validate

    Returns:
        The validated URL string

    Raises:
        SecurityError: If URL is invalid, not HTTPS, or not from allowed host
    """
    if not url:
        logger.error("Empty URL provided")
        raise SecurityError("Invalid URL: empty string")

    try:
        parsed = urlparse(url)
    except Exception as e:
        logger.error("Failed to parse URL %s: %s", url, e)
        raise SecurityError(f"Invalid URL: {e}") from e

    # Verify scheme is HTTPS
    if parsed.scheme != "https":
        logger.error("Non-HTTPS URL rejected: %s", url)
        raise SecurityError("URL must use HTTPS protocol")

    # Verify no credentials in URL
    if parsed.username or parsed.password:
        logger.error("URL contains credentials: %s", parsed.hostname)
        raise SecurityError("URL must not contain credentials")

    # Verify hostname is in allowed list
    if not parsed.hostname:
        logger.error("URL missing hostname: %s", url)
        raise SecurityError("Invalid URL: missing hostname")

    if parsed.hostname not in ALLOWED_HOSTS:
        logger.error("Disallowed host: %s (allowed: %s)", parsed.hostname, ALLOWED_HOSTS)
        raise SecurityError(
            f"Host '{parsed.hostname}' is not an allowed GDELT host. "
            f"Allowed hosts: {', '.join(sorted(ALLOWED_HOSTS))}",
        )

    return url


def check_decompression_safety(compressed_size: int, decompressed_size: int) -> None:
    """Check if decompression is safe (not a zip bomb).

    This function prevents zip bomb attacks by validating that the compression
    ratio and decompressed size are within safe limits. Zip bombs are malicious
    archives that expand to extremely large sizes.

    Args:
        compressed_size: Size of compressed data in bytes
        decompressed_size: Expected size of decompressed data in bytes

    Raises:
        SecurityError: If size exceeds limits or ratio is suspicious
    """
    # Validate inputs are positive
    if compressed_size <= 0:
        logger.error("Invalid compressed size: %d", compressed_size)
        raise SecurityError(f"Invalid compressed size: {compressed_size}")

    if decompressed_size < 0:
        logger.error("Invalid decompressed size: %d", decompressed_size)
        raise SecurityError(f"Invalid decompressed size: {decompressed_size}")

    # Check absolute size limit
    if decompressed_size > MAX_DECOMPRESSED_SIZE:
        logger.error(
            "Decompressed size %d exceeds limit %d",
            decompressed_size,
            MAX_DECOMPRESSED_SIZE,
        )
        raise SecurityError(
            f"Decompressed size {decompressed_size} bytes "
            f"exceeds maximum allowed size {MAX_DECOMPRESSED_SIZE} bytes "
            f"({MAX_DECOMPRESSED_SIZE // (1024 * 1024)}MB)",
        )

    # Check compression ratio (potential zip bomb)
    ratio = decompressed_size / compressed_size
    if ratio > MAX_COMPRESSION_RATIO:
        logger.error(
            "Suspicious compression ratio: %.1fx (compressed: %d, decompressed: %d)",
            ratio,
            compressed_size,
            decompressed_size,
        )
        raise SecurityError(
            f"Suspicious compression ratio: {ratio:.1f}x "
            f"(max allowed: {MAX_COMPRESSION_RATIO}x). "
            f"Possible zip bomb attack.",
        )
