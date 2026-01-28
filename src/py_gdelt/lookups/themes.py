"""
GKG theme lookups for GDELT Global Knowledge Graph.

This module provides the GKGThemes class for working with themes from
the GDELT Global Knowledge Graph (GKG).
"""

from __future__ import annotations

import logging
import re

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.lookups._utils import fuzzy_search, is_fuzzy_available, load_lookup_json
from py_gdelt.lookups.models import GKGThemeEntry


logger = logging.getLogger(__name__)


__all__ = ["GKGThemes"]


# GKG theme pattern: uppercase letters, numbers, underscores (e.g., ENV_CLIMATECHANGE, WB_2263_POLITICAL_STABILITY)
_THEME_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")


class GKGThemes:
    """
    GKG theme lookups with lazy loading.

    Provides methods to look up GKG theme metadata, search themes,
    and filter by category.

    All data is loaded lazily from JSON files on first access.
    """

    def __init__(self) -> None:
        self._themes: dict[str, GKGThemeEntry] | None = None

    @property
    def _themes_data(self) -> dict[str, GKGThemeEntry]:
        """Lazy load GKG themes data."""
        if self._themes is None:
            raw_data = load_lookup_json("gkg_themes.json")
            self._themes = {theme: GKGThemeEntry(**data) for theme, data in raw_data.items()}
        return self._themes

    def __contains__(self, theme: str) -> bool:
        """
        Check if theme exists (case-insensitive).

        Args:
            theme: GKG theme code to check

        Returns:
            True if theme exists, False otherwise
        """
        return theme.upper() in self._themes_data

    def __getitem__(self, theme: str) -> GKGThemeEntry:
        """
        Get full entry for theme (case-insensitive).

        Args:
            theme: GKG theme code (e.g., "ENV_CLIMATECHANGE")

        Returns:
            Full GKG theme entry with metadata

        Raises:
            KeyError: If theme is not found
        """
        theme_upper = theme.upper()
        if theme_upper not in self._themes_data:
            raise KeyError(theme)
        return self._themes_data[theme_upper]

    def __len__(self) -> int:
        """Return the number of themes in the lookup.

        Returns:
            Number of themes.
        """
        return len(self._themes_data)

    def get(self, theme: str) -> GKGThemeEntry | None:
        """
        Get entry for theme, or None if not found (case-insensitive).

        Args:
            theme: GKG theme code (e.g., "ENV_CLIMATECHANGE")

        Returns:
            GKG theme entry, or None if theme not found
        """
        return self._themes_data.get(theme.upper())

    def search(
        self,
        query: str,
        *,
        fuzzy: bool | None = None,
        threshold: int = 60,
    ) -> list[str]:
        """
        Search themes by description.

        Supports both substring matching and fuzzy matching (when rapidfuzz is installed).

        Args:
            query: Search query string.
            fuzzy: Fuzzy matching mode. None (default) auto-detects: uses fuzzy if
                rapidfuzz is installed, otherwise falls back to substring matching.
                True forces fuzzy matching (raises ImportError if not available).
                False forces substring matching.
            threshold: Minimum score (0-100) for fuzzy matches.

        Returns:
            List of theme codes matching the query.

        Raises:
            ImportError: If fuzzy=True but rapidfuzz is not installed.
        """
        # Determine matching mode
        use_fuzzy = fuzzy if fuzzy is not None else is_fuzzy_available()

        if use_fuzzy and not is_fuzzy_available():
            msg = "Fuzzy matching requires rapidfuzz. Install with: pip install py-gdelt[fuzzy]"
            raise ImportError(msg)

        if use_fuzzy:
            return self._fuzzy_search(query, threshold)
        return self._substring_search(query)

    def _substring_search(self, query: str) -> list[str]:
        """Perform substring-based search.

        Args:
            query: Search query string.

        Returns:
            List of matching theme codes.
        """
        query_lower = query.lower()
        return [
            theme
            for theme, entry in self._themes_data.items()
            if query_lower in entry.description.lower()
        ]

    def _fuzzy_search(self, query: str, threshold: int) -> list[str]:
        """Perform fuzzy search using rapidfuzz.

        Args:
            query: Search query string.
            threshold: Minimum score for fuzzy matches.

        Returns:
            List of matching theme codes sorted by score.
        """
        # Build candidate list with descriptions
        candidates: dict[str, str] = {}
        for theme, entry in self._themes_data.items():
            candidates[theme] = entry.description

        matches = fuzzy_search(
            query,
            list(candidates.values()),
            threshold=threshold,
        )

        # Map back to theme codes
        desc_to_theme = {desc: theme for theme, desc in candidates.items()}
        return [desc_to_theme[match] for match, _ in matches]

    def get_category(self, theme: str) -> str | None:
        """
        Get category for GKG theme.

        Args:
            theme: GKG theme code (e.g., "ENV_CLIMATECHANGE")

        Returns:
            Category name, or None if theme not found
        """
        entry = self._themes_data.get(theme)
        return entry.category if entry else None

    def list_by_category(self, category: str) -> list[str]:
        """
        List all themes in a specific category (case-sensitive).

        Args:
            category: Category name (e.g., "Environment", "Health")

        Returns:
            List of theme codes in the specified category
        """
        return [theme for theme, entry in self._themes_data.items() if entry.category == category]

    def suggest(
        self,
        theme: str,
        limit: int = 3,
        *,
        fuzzy: bool | None = None,
        threshold: int = 60,
    ) -> list[str]:
        """Suggest similar GKG themes based on input.

        Uses fuzzy matching (when available) to find themes with similar prefixes
        or descriptions.

        Args:
            theme: The invalid theme to find suggestions for.
            limit: Maximum number of suggestions to return.
            fuzzy: Fuzzy matching mode. None (default) auto-detects: uses fuzzy if
                rapidfuzz is installed, otherwise falls back to substring matching.
                True forces fuzzy matching (raises ImportError if not available).
                False forces substring matching.
            threshold: Minimum score (0-100) for fuzzy matches.

        Returns:
            List of suggestions in format "THEME (category)".

        Raises:
            ImportError: If fuzzy=True but rapidfuzz is not installed.
        """
        # Determine matching mode
        use_fuzzy = fuzzy if fuzzy is not None else is_fuzzy_available()

        if use_fuzzy and not is_fuzzy_available():
            msg = "Fuzzy matching requires rapidfuzz. Install with: pip install py-gdelt[fuzzy]"
            raise ImportError(msg)

        if use_fuzzy:
            return self._fuzzy_suggest(theme, limit, threshold)
        return self._substring_suggest(theme, limit)

    def _substring_suggest(self, theme: str, limit: int) -> list[str]:
        """Suggest using substring matching.

        Args:
            theme: The theme to find suggestions for.
            limit: Maximum number of suggestions.

        Returns:
            List of suggestions.
        """
        theme_upper = theme.upper()
        suggestions: list[str] = []

        # Strategy 1: Prefix match on theme code
        for theme_code, entry in self._themes_data.items():
            if theme_code.startswith(theme_upper):
                suggestions.append(f"{theme_code} ({entry.category})")
                if len(suggestions) >= limit:
                    return suggestions

        # Strategy 2: Contains match in description
        theme_lower = theme.lower()
        for theme_code, entry in self._themes_data.items():
            if (
                theme_lower in entry.description.lower()
                and f"{theme_code} ({entry.category})" not in suggestions
            ):
                suggestions.append(f"{theme_code} ({entry.category})")
                if len(suggestions) >= limit:
                    return suggestions

        return suggestions

    def _fuzzy_suggest(self, theme: str, limit: int, threshold: int) -> list[str]:
        """Suggest using fuzzy matching.

        Args:
            theme: The theme to find suggestions for.
            limit: Maximum number of suggestions.
            threshold: Minimum score for fuzzy matches.

        Returns:
            List of suggestions.
        """
        # Build candidate list with searchable text
        candidates: dict[str, str] = {}
        for theme_code, entry in self._themes_data.items():
            candidates[theme_code] = f"{theme_code} {entry.description}"

        matches = fuzzy_search(
            theme,
            list(candidates.values()),
            threshold=threshold,
            limit=limit,
        )

        # Map back to formatted suggestions
        text_to_theme = {text: code for code, text in candidates.items()}
        suggestions: list[str] = []
        for match, _ in matches:
            theme_code = text_to_theme[match]
            entry = self._themes_data[theme_code]
            suggestions.append(f"{theme_code} ({entry.category})")

        return suggestions

    def validate(self, theme: str) -> None:
        """Validate GKG theme (relaxed mode - accepts well-formed patterns).

        Known themes are always valid. Unknown themes are accepted if they
        match the expected pattern (uppercase with underscores). This relaxed
        validation accommodates GDELT's 59,000+ themes without requiring a
        complete theme list.

        Args:
            theme: GKG theme code to validate.

        Raises:
            InvalidCodeError: If theme format is invalid, with helpful suggestions.
        """
        theme_upper = theme.upper()

        # Known theme - always valid
        if theme_upper in self._themes_data:
            return

        # Unknown but well-formed pattern - accept with debug log
        if _THEME_PATTERN.match(theme_upper):
            logger.debug("Unknown GKG theme (accepting): %s", theme_upper)
            return

        # Invalid format
        suggestions = self.suggest(theme, limit=3)
        msg = f"Invalid GKG theme format: {theme!r}. Expected uppercase with underscores (e.g., ENV_CLIMATE)"
        raise InvalidCodeError(msg, code=theme, code_type="theme", suggestions=suggestions)
