"""GCAM (Global Content Analysis Measures) codebook lookups."""

from __future__ import annotations

from typing import Any

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.lookups._utils import fuzzy_search, load_lookup_json, resolve_fuzzy_mode
from py_gdelt.lookups.models import GCAMEntry


__all__ = ["GCAMLookup"]

_HELP_URL = "http://data.gdeltproject.org/documentation/GCAM-MASTER-CODEBOOK.TXT"


class GCAMLookup:
    """GCAM codebook lookups with lazy loading.

    Provides methods to look up GCAM dimension metadata from the Global Content
    Analysis Measures codebook. Data is loaded lazily from JSON on first access.
    Keys are case-insensitive.
    """

    def __init__(self) -> None:
        self._data: dict[str, GCAMEntry] | None = None
        self._keys_lower: dict[str, str] | None = None
        self._fuzzy_search_cache: tuple[list[str], list[str]] | None = None
        self._fuzzy_suggest_cache: tuple[list[str], list[str]] | None = None

    @property
    def _gcam_data(self) -> dict[str, GCAMEntry]:
        """Lazy load GCAM data from JSON.

        Returns:
            Dictionary mapping variable codes to GCAMEntry objects.
        """
        if self._data is None:
            raw: dict[str, Any] = load_lookup_json("gcam_codebook.json")
            self._data = {var: GCAMEntry(variable=var, **entry) for var, entry in raw.items()}
            self._keys_lower = {var.lower(): var for var in raw}
        return self._data

    def _normalize_key(self, variable: str) -> str | None:
        """Normalize key to match stored format (case-insensitive).

        Args:
            variable: Variable code to normalize.

        Returns:
            Canonical variable code if found, None otherwise.
        """
        _ = self._gcam_data
        return self._keys_lower.get(variable.lower()) if self._keys_lower else None

    def __len__(self) -> int:
        """Return the number of GCAM variables in the lookup.

        Returns:
            Number of GCAM variables.
        """
        return len(self._gcam_data)

    def __contains__(self, key: str) -> bool:
        """Check if GCAM variable exists (case-insensitive).

        Args:
            key: GCAM variable code to check

        Returns:
            True if variable exists, False otherwise
        """
        return self._normalize_key(key) is not None

    def __getitem__(self, key: str) -> GCAMEntry:
        """Get full entry for GCAM variable (case-insensitive).

        Args:
            key: GCAM variable code (e.g., "c2.14", "C2.14")

        Returns:
            Full GCAM entry with metadata

        Raises:
            KeyError: If variable is not found
        """
        canonical_key = self._normalize_key(key)
        if canonical_key is None:
            msg = f"GCAM variable not found: {key!r}"
            raise KeyError(msg)
        return self._gcam_data[canonical_key]

    def get(self, variable: str) -> GCAMEntry | None:
        """Get entry for GCAM variable, or None if not found.

        Args:
            variable: GCAM variable code (case-insensitive).

        Returns:
            GCAMEntry, or None if variable not found.
        """
        key = self._normalize_key(variable)
        return self._gcam_data.get(key) if key else None

    def search(
        self,
        query: str,
        limit: int | None = None,
        *,
        fuzzy: bool | None = None,
        threshold: int = 60,
    ) -> list[str]:
        """Search variables by dictionary name or dimension name.

        Supports both substring matching and fuzzy matching (when rapidfuzz is installed).

        Args:
            query: Search query string.
            limit: Maximum number of results to return. None for unlimited.
            fuzzy: Fuzzy matching mode. None (default) auto-detects: uses fuzzy if
                rapidfuzz is installed, otherwise falls back to substring matching.
                True forces fuzzy matching (raises ImportError if not available).
                False forces substring matching.
            threshold: Minimum score (0-100) for fuzzy matches.

        Returns:
            List of GCAM variable codes matching the query.

        Raises:
            ImportError: If fuzzy=True but rapidfuzz is not installed.
        """
        use_fuzzy = resolve_fuzzy_mode(fuzzy)
        if use_fuzzy:
            return self._fuzzy_search(query, limit, threshold)
        return self._substring_search(query, limit)

    def _substring_search(self, query: str, limit: int | None) -> list[str]:
        """Perform substring-based search.

        Args:
            query: Search query string.
            limit: Maximum number of results.

        Returns:
            List of matching variable codes.
        """
        query_lower = query.lower()
        results = [
            var
            for var, entry in self._gcam_data.items()
            if query_lower in entry.dictionary_name.lower()
            or query_lower in entry.dimension_name.lower()
        ]
        if limit is not None:
            return results[:limit]
        return results

    @property
    def _fuzzy_search_candidates(self) -> tuple[list[str], list[str]]:
        """Lazily cache candidate lists for fuzzy search."""
        if self._fuzzy_search_cache is None:
            codes = list(self._gcam_data.keys())
            texts = [
                f"{entry.dictionary_name} {entry.dimension_name}"
                for entry in self._gcam_data.values()
            ]
            self._fuzzy_search_cache = (codes, texts)
        return self._fuzzy_search_cache

    @property
    def _fuzzy_suggest_candidates(self) -> tuple[list[str], list[str]]:
        """Lazily cache candidate lists for fuzzy suggest."""
        if self._fuzzy_suggest_cache is None:
            codes = list(self._gcam_data.keys())
            texts = [
                f"{var} {entry.dictionary_name} {entry.dimension_name}"
                for var, entry in self._gcam_data.items()
            ]
            self._fuzzy_suggest_cache = (codes, texts)
        return self._fuzzy_suggest_cache

    def _fuzzy_search(self, query: str, limit: int | None, threshold: int) -> list[str]:
        """Perform fuzzy search using rapidfuzz.

        Args:
            query: Search query string.
            limit: Maximum number of results.
            threshold: Minimum score for fuzzy matches.

        Returns:
            List of matching variable codes sorted by score.
        """
        codes, texts = self._fuzzy_search_candidates
        matches = fuzzy_search(query, texts, threshold=threshold, limit=limit)
        return [codes[idx] for _, _, idx in matches]

    def suggest(
        self,
        code: str,
        limit: int = 3,
        *,
        fuzzy: bool | None = None,
        threshold: int = 60,
    ) -> list[str]:
        """Suggest similar GCAM variables based on input.

        Uses fuzzy matching (when available) or prefix matching to find variables
        with similar codes.

        Args:
            code: The code to find suggestions for.
            limit: Maximum number of suggestions to return.
            fuzzy: Fuzzy matching mode. None (default) auto-detects: uses fuzzy if
                rapidfuzz is installed, otherwise falls back to prefix matching.
                True forces fuzzy matching (raises ImportError if not available).
                False forces prefix matching.
            threshold: Minimum score (0-100) for fuzzy matches.

        Returns:
            List of GCAM variable codes.

        Raises:
            ImportError: If fuzzy=True but rapidfuzz is not installed.
        """
        use_fuzzy = resolve_fuzzy_mode(fuzzy)
        if use_fuzzy:
            return self._fuzzy_suggest(code, limit, threshold)
        return self._prefix_suggest(code, limit)

    def _prefix_suggest(self, code: str, limit: int) -> list[str]:
        """Suggest using prefix matching.

        Args:
            code: The code to find suggestions for.
            limit: Maximum number of suggestions.

        Returns:
            List of suggestions.
        """
        code_lower = code.lower()
        suggestions: list[str] = []

        # Strategy: Prefix match (e.g., "c2.1" suggests "c2.1", "c2.10", "c2.11", ...)
        for var in sorted(self._gcam_data.keys()):
            if var.lower().startswith(code_lower):
                suggestions.append(var)
                if len(suggestions) >= limit:
                    break

        return suggestions

    def _fuzzy_suggest(self, code: str, limit: int, threshold: int) -> list[str]:
        """Suggest using fuzzy matching.

        Args:
            code: The code to find suggestions for.
            limit: Maximum number of suggestions.
            threshold: Minimum score for fuzzy matches.

        Returns:
            List of suggestions.
        """
        codes, texts = self._fuzzy_suggest_candidates
        matches = fuzzy_search(code, texts, threshold=threshold, limit=limit)
        return [codes[idx] for _, _, idx in matches]

    def validate(self, code: str) -> None:
        """Validate GCAM variable code, raising exception if invalid.

        Args:
            code: GCAM variable code to validate

        Raises:
            InvalidCodeError: If code is not valid
        """
        if code not in self:
            suggestions = self.suggest(code)
            msg = f"Invalid GCAM variable: {code!r}"
            raise InvalidCodeError(
                msg,
                code=code,
                code_type="gcam",
                suggestions=suggestions,
                help_url=_HELP_URL,
            )

    def get_dictionary(self, prefix: str) -> dict[str, GCAMEntry]:
        """Get all entries for a dictionary by prefix.

        Returns all variables starting with the prefix followed by a dot
        (e.g., "c2" returns all "c2.*" entries).

        Args:
            prefix: Dictionary prefix (e.g., "c2", "v42")

        Returns:
            Dictionary mapping variable codes to GCAMEntry objects
        """
        prefix_lower = prefix.lower()
        search_prefix = f"{prefix_lower}."
        return {
            var: entry
            for var, entry in self._gcam_data.items()
            if var.lower().startswith(search_prefix)
        }

    def list_dictionaries(self) -> list[str]:
        """List unique dictionary prefixes.

        Extracts the prefix before the dot from all variable codes
        (e.g., ["c1", "c2", "v42"]).

        Returns:
            Sorted list of unique dictionary prefixes
        """
        prefixes = set()
        for var in self._gcam_data:
            if "." in var:
                prefixes.add(var.split(".")[0])
        return sorted(prefixes)

    def list_dictionary_names(self) -> list[str]:
        """List unique human-readable dictionary names.

        Returns:
            Sorted list of unique dictionary names
        """
        names = {entry.dictionary_name for entry in self._gcam_data.values()}
        return sorted(names)

    def by_language(self, language: str) -> dict[str, GCAMEntry]:
        """Get all entries for a specific language.

        Args:
            language: Language code (e.g., "eng", "spa")

        Returns:
            Dictionary mapping variable codes to GCAMEntry objects for that language
        """
        lang_lower = language.lower()
        return {
            var: entry
            for var, entry in self._gcam_data.items()
            if entry.language.lower() == lang_lower
        }
