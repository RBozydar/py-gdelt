"""Base class for tag-based lookups."""

from __future__ import annotations

from abc import ABC, abstractmethod

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.lookups._utils import fuzzy_search, is_fuzzy_available, load_lookup_json
from py_gdelt.lookups.models import TagCountEntry


class BaseTagLookup(ABC):
    """Abstract base class for tag lookups with lazy loading.

    Provides common functionality for tag-based lookup classes including
    case-insensitive search, validation, and suggestion features.
    Subclasses must define _json_filename, _help_url, and _code_type.
    """

    @property
    @abstractmethod
    def _json_filename(self) -> str:
        """JSON data filename for the lookup data.

        Returns:
            Filename of the JSON file containing tag data.
        """

    @property
    @abstractmethod
    def _help_url(self) -> str:
        """Help URL for error messages.

        Returns:
            URL to documentation for this tag type.
        """

    @property
    @abstractmethod
    def _code_type(self) -> str:
        """Code type for InvalidCodeError.

        Returns:
            String identifier for the tag type (e.g., "image_tag").
        """

    def __init__(self) -> None:
        self._data: dict[str, TagCountEntry] | None = None
        self._keys_lower: dict[str, str] | None = None

    @property
    def _tags_data(self) -> dict[str, TagCountEntry]:
        """Lazy load tags data.

        Returns:
            Dictionary mapping tag names to TagCountEntry objects.
        """
        if self._data is None:
            raw: dict[str, int] = load_lookup_json(self._json_filename)
            self._data = {tag: TagCountEntry(tag=tag, count=count) for tag, count in raw.items()}
            self._keys_lower = {tag.lower(): tag for tag in raw}
        return self._data

    def _normalize_key(self, tag: str) -> str | None:
        """Normalize key to match stored format.

        Performs case-insensitive lookup to find the canonical tag name.

        Args:
            tag: Tag name to normalize.

        Returns:
            Canonical tag name if found, None otherwise.
        """
        _ = self._tags_data
        return self._keys_lower.get(tag.lower()) if self._keys_lower else None

    def __len__(self) -> int:
        """Return the number of tags in the lookup.

        Returns:
            Number of tags.
        """
        return len(self._tags_data)

    def __contains__(self, tag: str) -> bool:
        """Check if tag exists.

        Args:
            tag: Tag name to check (case-insensitive).

        Returns:
            True if tag exists, False otherwise.
        """
        return self._normalize_key(tag) is not None

    def __getitem__(self, tag: str) -> TagCountEntry:
        """Get entry by tag.

        Args:
            tag: Tag name (case-insensitive).

        Returns:
            TagCountEntry with tag name and usage count.

        Raises:
            KeyError: If tag is not found.
        """
        key = self._normalize_key(tag)
        if key is None:
            raise KeyError(tag)
        return self._tags_data[key]

    def get(self, tag: str) -> TagCountEntry | None:
        """Get entry or None if not found.

        Args:
            tag: Tag name (case-insensitive).

        Returns:
            TagCountEntry if found, None otherwise.
        """
        key = self._normalize_key(tag)
        return self._tags_data.get(key) if key else None

    def search(
        self,
        query: str,
        limit: int | None = 100,
        *,
        fuzzy: bool | None = None,
        threshold: int = 60,
    ) -> list[str]:
        """Search tags by substring or fuzzy match.

        Supports both substring matching and fuzzy matching (when rapidfuzz is installed).

        Args:
            query: Search query string (case-insensitive).
            limit: Maximum number of results to return. None for unlimited.
            fuzzy: Fuzzy matching mode. None (default) auto-detects: uses fuzzy if
                rapidfuzz is installed, otherwise falls back to substring matching.
                True forces fuzzy matching (raises ImportError if not available).
                False forces substring matching.
            threshold: Minimum score (0-100) for fuzzy matches.

        Returns:
            List of matching tag names.

        Raises:
            ImportError: If fuzzy=True but rapidfuzz is not installed.
        """
        # Determine matching mode
        use_fuzzy = fuzzy if fuzzy is not None else is_fuzzy_available()

        if use_fuzzy and not is_fuzzy_available():
            msg = "Fuzzy matching requires rapidfuzz. Install with: pip install py-gdelt[fuzzy]"
            raise ImportError(msg)

        if use_fuzzy:
            return self._fuzzy_search(query, limit, threshold)
        return self._substring_search(query, limit)

    def _substring_search(self, query: str, limit: int | None) -> list[str]:
        """Perform substring-based search.

        Args:
            query: Search query string.
            limit: Maximum number of results.

        Returns:
            List of matching tag names.
        """
        query_lower = query.lower()
        results = [tag for tag in self._tags_data if query_lower in tag.lower()]
        if limit is not None:
            return results[:limit]
        return results

    def _fuzzy_search(self, query: str, limit: int | None, threshold: int) -> list[str]:
        """Perform fuzzy search using rapidfuzz.

        Args:
            query: Search query string.
            limit: Maximum number of results.
            threshold: Minimum score for fuzzy matches.

        Returns:
            List of matching tag names sorted by score.
        """
        candidates = list(self._tags_data.keys())
        matches = fuzzy_search(
            query,
            candidates,
            threshold=threshold,
            limit=limit,
        )
        return [match for match, _ in matches]

    def suggest(
        self,
        query: str,
        limit: int = 3,
        *,
        fuzzy: bool | None = None,
        threshold: int = 60,
    ) -> list[str]:
        """Suggest similar tags for an invalid query.

        Uses fuzzy matching (when available) or a two-stage matching strategy:
        1. Prefix matches (highest priority)
        2. Contains matches (fallback)

        Args:
            query: The invalid tag to find suggestions for.
            limit: Maximum number of suggestions to return.
            fuzzy: Fuzzy matching mode. None (default) auto-detects: uses fuzzy if
                rapidfuzz is installed, otherwise falls back to substring matching.
                True forces fuzzy matching (raises ImportError if not available).
                False forces substring matching.
            threshold: Minimum score (0-100) for fuzzy matches.

        Returns:
            List of similar valid tags.

        Raises:
            ImportError: If fuzzy=True but rapidfuzz is not installed.
        """
        # Determine matching mode
        use_fuzzy = fuzzy if fuzzy is not None else is_fuzzy_available()

        if use_fuzzy and not is_fuzzy_available():
            msg = "Fuzzy matching requires rapidfuzz. Install with: pip install py-gdelt[fuzzy]"
            raise ImportError(msg)

        if use_fuzzy:
            return self._fuzzy_suggest(query, limit, threshold)
        return self._substring_suggest(query, limit)

    def _substring_suggest(self, query: str, limit: int) -> list[str]:
        """Suggest using substring matching.

        Args:
            query: The query to find suggestions for.
            limit: Maximum number of suggestions.

        Returns:
            List of suggestions.
        """
        query_lower = query.lower()
        suggestions: list[str] = []

        # 1. Prefix matches (highest priority)
        for tag in self._tags_data:
            if tag.lower().startswith(query_lower):
                suggestions.append(tag)
                if len(suggestions) >= limit:
                    return suggestions

        # 2. Contains matches
        for tag in self._tags_data:
            if query_lower in tag.lower() and tag not in suggestions:
                suggestions.append(tag)
                if len(suggestions) >= limit:
                    return suggestions

        return suggestions

    def _fuzzy_suggest(self, query: str, limit: int, threshold: int) -> list[str]:
        """Suggest using fuzzy matching.

        Args:
            query: The query to find suggestions for.
            limit: Maximum number of suggestions.
            threshold: Minimum score for fuzzy matches.

        Returns:
            List of suggestions.
        """
        candidates = list(self._tags_data.keys())
        matches = fuzzy_search(
            query,
            candidates,
            threshold=threshold,
            limit=limit,
        )
        return [match for match, _ in matches]

    def validate(self, tag: str) -> None:
        """Validate tag, raising exception with suggestions if invalid.

        Args:
            tag: Tag name to validate.

        Raises:
            InvalidCodeError: If tag is not valid, with suggestions for similar tags.
        """
        if tag not in self:
            suggestions = self.suggest(tag, limit=3)
            msg = f"Invalid {self._code_type.replace('_', ' ')}: {tag!r}"
            raise InvalidCodeError(
                msg,
                code=tag,
                code_type=self._code_type,
                suggestions=suggestions,
                help_url=self._help_url,
            )
