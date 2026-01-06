"""
GKG theme lookups for GDELT Global Knowledge Graph.

This module provides the GKGThemes class for working with themes from
the GDELT Global Knowledge Graph (GKG).
"""

import json
from importlib.resources import files
from typing import Any

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.lookups.models import GKGThemeEntry


__all__ = ["GKGThemes"]


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
