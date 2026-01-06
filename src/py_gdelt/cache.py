"""File-based cache with TTL support for GDELT data files.

This module provides caching functionality for GDELT data with intelligent
TTL (Time To Live) handling:
- Historical files (>30 days old): Cached indefinitely (immutable)
- Recent files: TTL-based (configurable, default 1 hour)
- Master file lists: Short TTL (5 minutes)
"""

import hashlib
import json
import logging
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path


logger = logging.getLogger(__name__)

__all__ = ["Cache"]


class Cache:
    """File-based cache with TTL support for GDELT data files.

    Behavior:
    - Historical files (>30 days old): Cached indefinitely (immutable)
    - Recent files: TTL-based (configurable, default 1 hour)
    - Master file lists: Short TTL (5 minutes)

    The cache stores data files alongside .meta JSON files containing
    expiry timestamps and creation metadata.

    Args:
        cache_dir: Directory for cache storage
        default_ttl: Default TTL in seconds for recent files
        master_list_ttl: TTL in seconds for master file lists
    """

    def __init__(
        self,
        cache_dir: Path,
        default_ttl: int = 3600,  # 1 hour in seconds
        master_list_ttl: int = 300,  # 5 minutes
    ) -> None:
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.master_list_ttl = master_list_ttl

    def get(self, key: str) -> bytes | None:
        """Get cached data if exists and not expired.

        Args:
            key: Cache key (usually URL or filename)

        Returns:
            Cached data as bytes, or None if not found/expired
        """
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_metadata_path(key)

            # Check if both files exist
            if not cache_path.exists() or not meta_path.exists():
                return None

            # Load and validate metadata
            try:
                with meta_path.open() as f:
                    metadata = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Corrupted metadata for key '%s': %s", key, e)
                return None

            # Check expiry
            expires_at = metadata.get("expires_at")
            if expires_at is not None and expires_at != "never":
                try:
                    expiry_time = datetime.fromisoformat(expires_at)
                    if datetime.now(UTC) > expiry_time:
                        logger.debug("Cache entry expired for key '%s'", key)
                        return None
                except (ValueError, TypeError) as e:
                    logger.warning("Invalid expiry time for key '%s': %s", key, e)
                    return None

            # Read and return cached data
            return cache_path.read_bytes()

        except OSError as e:
            logger.warning("Error reading cache for key '%s': %s", key, e)
            return None

    def set(
        self,
        key: str,
        data: bytes,
        file_date: datetime | None = None,
        ttl: int | None = None,
    ) -> None:
        """Store data in cache.

        Args:
            key: Cache key (usually URL or filename)
            data: Raw bytes to cache
            file_date: Date of the GDELT file (if known).
                      Files >30 days old are cached indefinitely.
            ttl: Custom TTL in seconds (overrides default_ttl if provided).
                Use for master file lists or other short-lived cache entries.
        """
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_metadata_path(key)

            # Ensure cache directory exists with secure permissions (owner only)
            cache_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

            # Write data file
            cache_path.write_bytes(data)

            # Determine expiry time
            now = datetime.now(UTC)
            if self._is_historical(file_date):
                # Historical files never expire
                expires_at = "never"
            else:
                # Use custom TTL if provided, otherwise default
                effective_ttl = ttl if ttl is not None else self.default_ttl
                expires_at = (now + timedelta(seconds=effective_ttl)).isoformat()

            # Write metadata
            metadata = {
                "created_at": now.isoformat(),
                "expires_at": expires_at,
                "key": key,
            }

            with meta_path.open("w") as f:
                json.dump(metadata, f, indent=2)

            logger.debug("Cached key '%s' (expires: %s)", key, expires_at)

        except OSError as e:
            logger.error("Failed to cache key '%s': %s", key, e)  # noqa: TRY400
            raise

    def is_valid(self, key: str) -> bool:
        """Check if cache entry exists and is not expired.

        Args:
            key: Cache key to check

        Returns:
            True if entry exists and is valid, False otherwise
        """
        return self.get(key) is not None

    def clear(self, before: datetime | str | None = None) -> int:
        """Clear cache entries.

        Args:
            before: If provided, only clear entries older than this date.
                   Can be datetime or ISO format string.

        Returns:
            Number of entries cleared.
        """
        if not self.cache_dir.exists():
            return 0

        # Parse before parameter if provided
        cutoff_time: datetime | None = None
        if before is not None:
            cutoff_time = datetime.fromisoformat(before) if isinstance(before, str) else before

            # Ensure cutoff_time is timezone-aware
            if cutoff_time.tzinfo is None:
                cutoff_time = cutoff_time.replace(tzinfo=UTC)

        cleared = 0

        try:
            # Find all .meta files
            for meta_path in self.cache_dir.rglob("*.meta"):
                should_delete = False

                if cutoff_time is None:
                    # Clear all
                    should_delete = True
                else:
                    # Check creation time
                    try:
                        with meta_path.open() as f:
                            metadata = json.load(f)

                        created_at = datetime.fromisoformat(metadata["created_at"])

                        if created_at < cutoff_time:
                            should_delete = True

                    except (json.JSONDecodeError, KeyError, ValueError, OSError):
                        # If we can't read metadata, skip (only delete if cutoff_time is None,
                        # which is already handled above)
                        pass

                if should_delete:
                    # Delete both data file and metadata
                    data_path = meta_path.with_suffix("")  # Remove .meta extension

                    try:
                        if data_path.exists():
                            data_path.unlink()
                        meta_path.unlink()
                        cleared += 1
                    except OSError as e:
                        logger.warning("Failed to delete cache entry: %s", e)

        except OSError:
            logger.exception("Error during cache clear")

        logger.info("Cleared %d cache entries", cleared)
        return cleared

    def size(self) -> int:
        """Return total cache size in bytes.

        Returns:
            Total size of all cached files (excluding metadata)
        """
        if not self.cache_dir.exists():
            return 0

        total_size = 0

        try:
            for file_path in self.cache_dir.rglob("*"):
                # Skip metadata files and directories
                if file_path.is_file() and not file_path.name.endswith(".meta"):
                    total_size += file_path.stat().st_size

        except OSError as e:
            logger.warning("Error calculating cache size: %s", e)

        return total_size

    def _is_historical(self, file_date: datetime | None) -> bool:
        """Check if file is historical (>30 days old).

        Args:
            file_date: Date of the file, or None if unknown

        Returns:
            True if file is historical (>30 days old), False otherwise
        """
        if file_date is None:
            return False

        # Ensure file_date is timezone-aware
        if file_date.tzinfo is None:
            file_date = file_date.replace(tzinfo=UTC)

        now = datetime.now(UTC)
        age = now - file_date

        # Must be STRICTLY greater than 30 days (not equal)
        return age > timedelta(days=30)

    def _get_cache_path(self, key: str) -> Path:
        """Get safe cache file path for key.

        Args:
            key: Cache key (URL, filename, or arbitrary string)

        Returns:
            Safe path under cache_dir
        """
        return self._sanitize_cache_key(self.cache_dir, key)

    def _get_metadata_path(self, key: str) -> Path:
        """Get metadata file path for cache entry.

        Args:
            key: Cache key

        Returns:
            Path to .meta file
        """
        cache_path = self._get_cache_path(key)
        return cache_path.with_suffix(cache_path.suffix + ".meta")

    @staticmethod
    def _sanitize_cache_key(base_dir: Path, key: str) -> Path:
        """Generate a safe file path for cache storage.

        Converts potentially unsafe keys (URLs, paths with traversal attempts)
        into safe filesystem paths under base_dir.

        Strategy:
        1. Remove dangerous path components (., .., absolute paths)
        2. Replace unsafe characters with safe ones
        3. Hash long keys to prevent filesystem limits
        4. Ensure result is always under base_dir

        Args:
            base_dir: Base directory for cache storage
            key: Cache key (URL, filename, or arbitrary string)

        Returns:
            Safe path under base_dir
        """
        # Normalize the key
        normalized = key.strip()

        # Remove URL schemes
        normalized = re.sub(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", "", normalized)

        # Replace path separators with underscores
        normalized = normalized.replace("/", "_").replace("\\", "_")

        # Remove or replace dangerous sequences
        normalized = normalized.replace("..", "_")

        # Replace other unsafe characters (keeping alphanumeric, dash, underscore, dot)
        safe_chars = re.sub(r"[^a-zA-Z0-9._-]", "_", normalized)

        # Handle very long filenames (filesystem limit is typically 255 bytes)
        # If too long, use hash of original + truncated safe version
        if len(safe_chars) > 200:
            key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
            safe_chars = f"{safe_chars[:180]}_{key_hash}"

        # Ensure it's not empty
        if not safe_chars or safe_chars in (".", ".."):
            # Use hash of original key
            safe_chars = hashlib.sha256(key.encode()).hexdigest()

        # Build final path
        return base_dir / safe_chars
