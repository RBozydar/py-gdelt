"""
CAMEO code lookups for GDELT events.

This module provides the CAMEOCodes class for working with Conflict and Mediation
Event Observations (CAMEO) event codes used throughout GDELT data.
"""

from __future__ import annotations

from typing import Final

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.lookups._utils import fuzzy_search, load_lookup_json, resolve_fuzzy_mode
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

    def search(
        self,
        query: str,
        include_examples: bool = False,
        limit: int | None = None,
        *,
        fuzzy: bool | None = None,
        threshold: int = 60,
    ) -> list[str]:
        """
        Search codes by name/description.

        Supports both substring matching and fuzzy matching (when rapidfuzz is installed).

        Args:
            query: Search query string (case-insensitive).
            include_examples: If True, also search in examples and usage_notes fields.
            limit: Maximum number of results to return. None for unlimited.
            fuzzy: Fuzzy matching mode. None (default) auto-detects: uses fuzzy if
                rapidfuzz is installed, otherwise falls back to substring matching.
                True forces fuzzy matching (raises ImportError if not available).
                False forces substring matching.
            threshold: Minimum score (0-100) for fuzzy matches.

        Returns:
            List of CAMEO codes matching the query.

        Raises:
            ImportError: If fuzzy=True but rapidfuzz is not installed.
        """
        use_fuzzy = resolve_fuzzy_mode(fuzzy)

        # CAMEO-specific: if query is numeric, prioritize exact code prefix matches first
        query_is_numeric = query.isdigit()
        if query_is_numeric:
            prefix_matches = [code for code in self._codes_data if code.startswith(query)]
            if prefix_matches:
                results = sorted(prefix_matches)
                return results[:limit] if limit is not None else results

        if use_fuzzy:
            results = self._fuzzy_search(query, include_examples, threshold)
        else:
            results = self._substring_search(query, include_examples)

        return results[:limit] if limit is not None else results

    def _substring_search(self, query: str, include_examples: bool) -> list[str]:
        """Perform substring-based search.

        Args:
            query: Search query string.
            include_examples: If True, also search in examples and usage_notes.

        Returns:
            List of matching CAMEO codes.
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

    def _fuzzy_search(self, query: str, include_examples: bool, threshold: int) -> list[str]:
        """Perform fuzzy search using rapidfuzz.

        Args:
            query: Search query string.
            include_examples: If True, also search in examples and usage_notes.
            threshold: Minimum score for fuzzy matches.

        Returns:
            List of matching CAMEO codes sorted by score.
        """
        codes = list(self._codes_data.keys())
        texts: list[str] = []
        for entry in self._codes_data.values():
            text_parts = [entry.name, entry.description]
            if include_examples:
                if entry.usage_notes:
                    text_parts.append(entry.usage_notes)
                text_parts.extend(entry.examples)
            texts.append(" ".join(text_parts))

        matches = fuzzy_search(
            query,
            texts,
            threshold=threshold,
        )

        return [codes[idx] for _, _, idx in matches]

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

    def suggest(
        self,
        code: str,
        limit: int = 3,
        *,
        fuzzy: bool | None = None,
        threshold: int = 60,
    ) -> list[str]:
        """Suggest similar CAMEO codes based on input.

        Uses fuzzy matching (when available) to find codes with similar prefixes or names.

        Args:
            code: The invalid code to find suggestions for.
            limit: Maximum number of suggestions to return.
            fuzzy: Fuzzy matching mode. None (default) auto-detects: uses fuzzy if
                rapidfuzz is installed, otherwise falls back to substring matching.
                True forces fuzzy matching (raises ImportError if not available).
                False forces substring matching.
            threshold: Minimum score (0-100) for fuzzy matches.

        Returns:
            List of suggestions in format "code (Name)".

        Raises:
            ImportError: If fuzzy=True but rapidfuzz is not installed.
        """
        use_fuzzy = resolve_fuzzy_mode(fuzzy)

        suggestions: list[str] = []

        # CAMEO-specific: if code is numeric, prioritize exact code prefix matches first
        if code.isdigit():
            for cameo_code, entry in self._codes_data.items():
                if cameo_code.startswith(code):
                    suggestions.append(f"{cameo_code} ({entry.name})")
                    if len(suggestions) >= limit:
                        return suggestions

        if use_fuzzy:
            return self._fuzzy_suggest(code, limit, threshold, suggestions)
        return self._substring_suggest(code, limit, suggestions)

    def _substring_suggest(self, code: str, limit: int, suggestions: list[str]) -> list[str]:
        """Suggest using substring matching.

        Args:
            code: The code to find suggestions for.
            limit: Maximum number of suggestions.
            suggestions: Pre-populated suggestions (e.g., from prefix matching).

        Returns:
            List of suggestions.
        """
        # Strategy 1: Prefix match on code (already done for numeric codes)
        if not code.isdigit():
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

    def _fuzzy_suggest(
        self, code: str, limit: int, threshold: int, suggestions: list[str]
    ) -> list[str]:
        """Suggest using fuzzy matching.

        Args:
            code: The code to find suggestions for.
            limit: Maximum number of suggestions.
            threshold: Minimum score for fuzzy matches.
            suggestions: Pre-populated suggestions (e.g., from prefix matching).

        Returns:
            List of suggestions.
        """
        remaining = limit - len(suggestions)
        if remaining <= 0:
            return suggestions

        # Build candidate list, excluding already-suggested codes
        existing = {s.split()[0] for s in suggestions}  # Extract codes from existing suggestions
        codes: list[str] = []
        texts: list[str] = []

        for cameo_code, entry in self._codes_data.items():
            if cameo_code not in existing:
                codes.append(cameo_code)
                texts.append(f"{cameo_code} {entry.name}")

        if not codes:
            return suggestions

        matches = fuzzy_search(
            code,
            texts,
            threshold=threshold,
            limit=remaining,
        )

        for _, _, idx in matches:
            cameo_code = codes[idx]
            entry = self._codes_data[cameo_code]
            suggestions.append(f"{cameo_code} ({entry.name})")

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
