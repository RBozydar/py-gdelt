"""
GKG theme lookups for GDELT Global Knowledge Graph.

This module provides the GKGThemes class for working with themes from
the GDELT Global Knowledge Graph (GKG).
"""

import json
from importlib.resources import files

from py_gdelt.exceptions import InvalidCodeError

__all__ = ["GKGThemes"]


class GKGThemes:
    """
    GKG theme lookups with lazy loading.

    Provides methods to look up GKG theme metadata, search themes,
    and filter by category.

    All data is loaded lazily from JSON files on first access.
    """

    def __init__(self) -> None:
        """Initialize GKGThemes with lazy-loaded data."""
        self._themes: dict[str, dict[str, str]] | None = None

    @property
    def _themes_data(self) -> dict[str, dict[str, str]]:
        """Lazy load GKG themes data."""
        if self._themes is None:
            data_path = files("py_gdelt.lookups.data").joinpath("gkg_themes.json")
            self._themes = json.loads(data_path.read_text())
        return self._themes

    def __getitem__(self, theme: str) -> dict[str, str]:
        """
        Get metadata for GKG theme.

        Args:
            theme: GKG theme code (e.g., "ENV_CLIMATECHANGE")

        Returns:
            Dictionary containing theme metadata (category, description, etc.)

        Raises:
            KeyError: If theme is not found
        """
        return self._themes_data[theme]

    def search(self, query: str) -> list[str]:
        """
        Search for themes by substring (case-insensitive).

        Args:
            query: Search query string

        Returns:
            List of theme codes matching the query
        """
        query_upper = query.upper()
        return [theme for theme in self._themes_data if query_upper in theme.upper()]

    def get_category(self, theme: str) -> str | None:
        """
        Get category for GKG theme.

        Args:
            theme: GKG theme code (e.g., "ENV_CLIMATECHANGE")

        Returns:
            Category name, or None if theme not found
        """
        theme_data = self._themes_data.get(theme)
        if theme_data is None:
            return None
        return theme_data.get("category")

    def list_by_category(self, category: str) -> list[str]:
        """
        List all themes in a specific category (case-sensitive).

        Args:
            category: Category name (e.g., "Environment", "Health")

        Returns:
            List of theme codes in the specified category
        """
        return [
            theme
            for theme, data in self._themes_data.items()
            if data.get("category") == category
        ]

    def validate(self, theme: str) -> None:
        """
        Validate GKG theme, raising exception if invalid.

        Args:
            theme: GKG theme code to validate

        Raises:
            InvalidCodeError: If theme is not valid
        """
        if theme not in self._themes_data:
            msg = f"Invalid GKG theme: {theme!r}"
            raise InvalidCodeError(msg, code=theme, code_type="theme")
