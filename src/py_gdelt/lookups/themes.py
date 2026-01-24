"""
GKG theme lookups for GDELT Global Knowledge Graph.

This module provides the GKGThemes class for working with themes from
the GDELT Global Knowledge Graph (GKG).
"""

from __future__ import annotations

import logging
import re

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.lookups._utils import load_lookup_json
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

    def search(self, query: str) -> list[str]:
        """
        Search themes by description (substring match).

        Args:
            query: Search query string

        Returns:
            List of theme codes matching the query
        """
        query_lower = query.lower()
        return [
            theme
            for theme, entry in self._themes_data.items()
            if query_lower in entry.description.lower()
        ]

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

    def suggest(self, theme: str, limit: int = 3) -> list[str]:
        """Suggest similar GKG themes based on input.

        Uses fuzzy matching to find themes with similar prefixes or descriptions.

        Args:
            theme: The invalid theme to find suggestions for.
            limit: Maximum number of suggestions to return.

        Returns:
            List of suggestions in format "THEME (category)".
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
