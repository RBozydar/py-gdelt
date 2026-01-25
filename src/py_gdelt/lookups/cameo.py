"""
CAMEO code lookups for GDELT events.

This module provides the CAMEOCodes class for working with Conflict and Mediation
Event Observations (CAMEO) event codes used throughout GDELT data.
"""

from __future__ import annotations

from typing import Final

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.lookups._utils import load_lookup_json
from py_gdelt.lookups.models import CAMEOCodeEntry, GoldsteinEntry


__all__ = ["CAMEOCodes"]

# CAMEO code ranges
_COOPERATION_START: Final[int] = 1
_COOPERATION_END: Final[int] = 8
_CONFLICT_START: Final[int] = 14
_CONFLICT_END: Final[int] = 20

# Quad class boundaries
_VERBAL_COOPERATION_END: Final[int] = 5
_MATERIAL_COOPERATION_END: Final[int] = 8
_VERBAL_CONFLICT_END: Final[int] = 13
_MATERIAL_CONFLICT_END: Final[int] = 20


class CAMEOCodes:
    """
    CAMEO event code lookups with lazy loading.

    Provides methods to look up CAMEO code descriptions, Goldstein scale values,
    and classify codes as cooperation/conflict or by quad class.

    All data is loaded lazily from JSON files on first access.
    """

    def __init__(self) -> None:
        self._codes: dict[str, CAMEOCodeEntry] | None = None
        self._goldstein: dict[str, GoldsteinEntry] | None = None

    @property
    def _codes_data(self) -> dict[str, CAMEOCodeEntry]:
        """Lazy load CAMEO codes data."""
        if self._codes is None:
            raw_data = load_lookup_json("cameo_codes.json")
            self._codes = {code: CAMEOCodeEntry(**data) for code, data in raw_data.items()}
        return self._codes

    @property
    def _goldstein_data(self) -> dict[str, GoldsteinEntry]:
        """Lazy load Goldstein scale data."""
        if self._goldstein is None:
            raw_data = load_lookup_json("cameo_goldstein.json")
            self._goldstein = {code: GoldsteinEntry(**data) for code, data in raw_data.items()}
        return self._goldstein

    def __contains__(self, code: str) -> bool:
        """
        Check if code exists.

        Args:
            code: CAMEO code to check

        Returns:
            True if code exists, False otherwise
        """
        return code in self._codes_data

    def __getitem__(self, code: str) -> CAMEOCodeEntry:
        """
        Get full entry for CAMEO code.

        Args:
            code: CAMEO code (e.g., "01", "141", "20")

        Returns:
            Full CAMEO code entry with metadata

        Raises:
            KeyError: If code is not found
        """
        return self._codes_data[code]

    def get(self, code: str) -> CAMEOCodeEntry | None:
        """
        Get entry for CAMEO code, or None if not found.

        Args:
            code: CAMEO code (e.g., "01", "141", "20")

        Returns:
            CAMEO code entry, or None if code not found
        """
        return self._codes_data.get(code)

    def get_goldstein(self, code: str) -> GoldsteinEntry | None:
        """
        Get Goldstein entry for CAMEO code.

        The Goldstein scale ranges from -10 (most conflictual) to +10 (most cooperative).

        Args:
            code: CAMEO code (e.g., "01", "141", "20")

        Returns:
            Goldstein entry with value and description, or None if code not found
        """
        return self._goldstein_data.get(code)

    def get_goldstein_category(self, score: float) -> str:
        """
        Categorize a Goldstein scale score into conflict/cooperation buckets.

        Categories:
        - highly_conflictual: -10 to -5
        - moderately_conflictual: -5 to -2
        - mildly_conflictual: -2 to 0
        - cooperative: 0 to +10

        Args:
            score: Goldstein scale value from -10 to +10

        Returns:
            Category name string
        """
        if score < -5:
            return "highly_conflictual"
        if score < -2:
            return "moderately_conflictual"
        if score < 0:
            return "mildly_conflictual"
        return "cooperative"

    def search(self, query: str, include_examples: bool = False) -> list[str]:
        """
        Search codes by name/description (substring match).

        Args:
            query: Search query string (case-insensitive).
            include_examples: If True, also search in examples and usage_notes fields.

        Returns:
            List of CAMEO codes matching the query.
        """
        query_lower = query.lower()
        results: list[str] = []
        for code, entry in self._codes_data.items():
            if query_lower in entry.name.lower() or query_lower in entry.description.lower():
                results.append(code)
                continue
            if include_examples:
                if entry.usage_notes and query_lower in entry.usage_notes.lower():
                    results.append(code)
                    continue
                if any(query_lower in example.lower() for example in entry.examples):
                    results.append(code)
        return results

    def is_conflict(self, code: str) -> bool:
        """
        Check if CAMEO code represents conflict (codes 14-20).

        Args:
            code: CAMEO code (e.g., "01", "141", "20")

        Returns:
            True if code is in conflict range (14-20), False otherwise
        """
        root_code = int(code[:2])
        return _CONFLICT_START <= root_code <= _CONFLICT_END

    def is_cooperation(self, code: str) -> bool:
        """
        Check if CAMEO code represents cooperation (codes 01-08).

        Args:
            code: CAMEO code (e.g., "01", "141", "20")

        Returns:
            True if code is in cooperation range (01-08), False otherwise
        """
        root_code = int(code[:2])
        return _COOPERATION_START <= root_code <= _COOPERATION_END

    def get_quad_class(self, code: str) -> int | None:
        """
        Get quad class (1-4) for CAMEO code.

        Quad classes:
        - 1: Verbal cooperation (01-05)
        - 2: Material cooperation (06-08)
        - 3: Verbal conflict (09-13)
        - 4: Material conflict (14-20)

        Args:
            code: CAMEO code (e.g., "01", "141", "20")

        Returns:
            Quad class (1-4), or None if code is invalid or not found
        """
        if code not in self._codes_data:
            return None

        root_code = int(code[:2])

        if _COOPERATION_START <= root_code <= _VERBAL_COOPERATION_END:
            return 1
        if root_code <= _MATERIAL_COOPERATION_END:
            return 2
        if root_code <= _VERBAL_CONFLICT_END:
            return 3
        if root_code <= _MATERIAL_CONFLICT_END:
            return 4

        return None

    def suggest(self, code: str, limit: int = 3) -> list[str]:
        """Suggest similar CAMEO codes based on input.

        Uses fuzzy matching to find codes with similar prefixes or names.

        Args:
            code: The invalid code to find suggestions for.
            limit: Maximum number of suggestions to return.

        Returns:
            List of suggestions in format "code (Name)".
        """
        suggestions: list[str] = []

        # Strategy 1: Prefix match on code
        for cameo_code, entry in self._codes_data.items():
            if cameo_code.startswith(code):
                suggestions.append(f"{cameo_code} ({entry.name})")
                if len(suggestions) >= limit:
                    return suggestions

        # Strategy 2: Contains match in name
        code_lower = code.lower()
        for cameo_code, entry in self._codes_data.items():
            if (
                code_lower in entry.name.lower()
                and f"{cameo_code} ({entry.name})" not in suggestions
            ):
                suggestions.append(f"{cameo_code} ({entry.name})")
                if len(suggestions) >= limit:
                    return suggestions

        return suggestions

    def validate(self, code: str) -> None:
        """Validate CAMEO code, raising exception if invalid.

        Args:
            code: CAMEO code to validate.

        Raises:
            InvalidCodeError: If code is not valid, with helpful suggestions.
        """
        if code not in self._codes_data:
            suggestions = self.suggest(code, limit=3)
            msg = f"Invalid CAMEO code: {code!r}"
            raise InvalidCodeError(
                msg,
                code=code,
                code_type="cameo",
                suggestions=suggestions,
            )

    def codes_with_examples(self) -> list[str]:
        """Return all CAMEO codes that have example scenarios.

        Returns:
            List of CAMEO codes with non-empty examples.
        """
        return [code for code, entry in self._codes_data.items() if entry.examples]

    def codes_with_usage_notes(self) -> list[str]:
        """Return all CAMEO codes that have usage notes.

        Returns:
            List of CAMEO codes with non-None usage_notes.
        """
        return [code for code, entry in self._codes_data.items() if entry.usage_notes]
