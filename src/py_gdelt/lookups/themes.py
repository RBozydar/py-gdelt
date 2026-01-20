"""
GKG theme lookups for GDELT Global Knowledge Graph.

This module provides the GKGThemes class for working with themes from
the GDELT Global Knowledge Graph (GKG).
"""

import json
import logging
import re
from importlib.resources import files
from typing import Any

from py_gdelt.exceptions import InvalidCodeError
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

    def _load_json(self, filename: str) -> dict[str, dict[str, Any]]:
        """Load JSON data from package resources."""
        data_path = files("py_gdelt.lookups.data").joinpath(filename)
        return json.loads(data_path.read_text())  # type: ignore[no-any-return]

    @property
    def _themes_data(self) -> dict[str, GKGThemeEntry]:
        """Lazy load GKG themes data."""
        if self._themes is None:
            raw_data = self._load_json("gkg_themes.json")
            self._themes = {theme: GKGThemeEntry(**data) for theme, data in raw_data.items()}
        return self._themes

    def __contains__(self, theme: str) -> bool:
        """
        Check if theme exists.

        Args:
            theme: GKG theme code to check

        Returns:
            True if theme exists, False otherwise
        """
        return theme in self._themes_data

    def __getitem__(self, theme: str) -> GKGThemeEntry:
        """
        Get full entry for theme.

        Args:
            theme: GKG theme code (e.g., "ENV_CLIMATECHANGE")

        Returns:
            Full GKG theme entry with metadata

        Raises:
            KeyError: If theme is not found
        """
        return self._themes_data[theme]

    def get(self, theme: str) -> GKGThemeEntry | None:
        """
        Get entry for theme, or None if not found.

        Args:
            theme: GKG theme code (e.g., "ENV_CLIMATECHANGE")

        Returns:
            GKG theme entry, or None if theme not found
        """
        return self._themes_data.get(theme)

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

    def validate(self, theme: str) -> None:
        """Validate GKG theme (relaxed mode - accepts well-formed patterns).

        Known themes are always valid. Unknown themes are accepted if they
        match the expected pattern (uppercase with underscores). This relaxed
        validation accommodates GDELT's 59,000+ themes without requiring a
        complete theme list.

        Args:
            theme: GKG theme code to validate

        Raises:
            InvalidCodeError: If theme format is invalid
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
        msg = f"Invalid GKG theme format: {theme!r}. Expected uppercase with underscores (e.g., ENV_CLIMATE)"
        raise InvalidCodeError(msg, code=theme, code_type="theme")
