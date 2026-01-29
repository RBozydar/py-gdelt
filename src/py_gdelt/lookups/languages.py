"""Language code lookups for GDELT DOC/GEO APIs."""

from __future__ import annotations

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.lookups._utils import fuzzy_search, load_lookup_json, resolve_fuzzy_mode
from py_gdelt.lookups.models import LanguageEntry


__all__ = ["Languages"]

_HELP_URL = "http://data.gdeltproject.org/api/v2/guides/LOOKUP-LANGUAGES.TXT"


class Languages:
    """Language code lookups with lazy loading and case-insensitive keys.

    Provides methods to look up supported language codes for GDELT DOC/GEO APIs.
    Language codes follow ISO 639-3 standard (3-character codes).
    All data is loaded lazily from JSON on first access. Keys are case-insensitive.
    """

    def __init__(self) -> None:
        self._data: dict[str, LanguageEntry] | None = None
        self._keys_lower: dict[str, str] | None = None

    @property
    def _languages_data(self) -> dict[str, LanguageEntry]:
        """Lazy load languages data from JSON.

        Returns:
            Dictionary mapping language codes to LanguageEntry instances.
        """
        if self._data is None:
            raw: dict[str, str] = load_lookup_json("languages.json")
            self._data = {code: LanguageEntry(code=code, name=name) for code, name in raw.items()}
            self._keys_lower = {code.lower(): code for code in raw}
        return self._data

    def _normalize_key(self, code: str) -> str | None:
        """Normalize key to match stored format (case-insensitive).

        Args:
            code: Language code to normalize.

        Returns:
            Canonical code if found, None otherwise.
        """
        _ = self._languages_data
        return self._keys_lower.get(code.lower()) if self._keys_lower else None

    def __len__(self) -> int:
        """Return the number of languages in the lookup.

        Returns:
            Number of languages.
        """
        return len(self._languages_data)

    def __contains__(self, code: str) -> bool:
        """Check if language code exists.

        Args:
            code: Language code (case-insensitive).

        Returns:
            True if code exists, False otherwise.
        """
        normalized = self._normalize_key(code)
        return normalized is not None

    def __getitem__(self, code: str) -> LanguageEntry:
        """Get full entry for language code.

        Args:
            code: Language code (case-insensitive).

        Returns:
            Language entry with code and name.

        Raises:
            KeyError: If code is not found.
        """
        normalized = self._normalize_key(code)
        if normalized is None:
            raise KeyError(code)
        return self._languages_data[normalized]

    def get(self, code: str) -> LanguageEntry | None:
        """Get entry for language code, or None if not found.

        Args:
            code: Language code (case-insensitive).

        Returns:
            Language entry, or None if code not found.
        """
        normalized = self._normalize_key(code)
        if normalized is None:
            return None
        return self._languages_data.get(normalized)

    def search(
        self,
        query: str,
        limit: int = 10,
        *,
        fuzzy: bool | None = None,
        threshold: int = 60,
    ) -> list[str]:
        """Search for languages by code or name.

        Searches both language codes and names (case-insensitive).
        Results are ordered by relevance: exact code match, code prefix match,
        name prefix match, then contains match.

        Args:
            query: Search term (can match code or name).
            limit: Maximum number of results to return.
            fuzzy: Fuzzy matching mode. None (default) auto-detects: uses fuzzy if
                rapidfuzz is installed, otherwise falls back to substring matching.
                True forces fuzzy matching (raises ImportError if not available).
                False forces substring matching.
            threshold: Minimum score (0-100) for fuzzy matches.

        Returns:
            List of matching language codes (no duplicates).

        Raises:
            ImportError: If fuzzy=True but rapidfuzz is not installed.
        """
        use_fuzzy = resolve_fuzzy_mode(fuzzy)
        if use_fuzzy:
            return self._fuzzy_search(query, limit, threshold)
        return self._substring_search(query, limit)

    def _substring_search(self, query: str, limit: int) -> list[str]:
        """Perform substring-based search.

        Args:
            query: Search query string.
            limit: Maximum number of results.

        Returns:
            List of matching language codes.
        """
        query_lower = query.lower()

        # Score matches: exact > prefix > contains
        scored: list[tuple[int, str]] = []

        for code, entry in self._languages_data.items():
            code_lower = code.lower()
            name_lower = entry.name.lower()

            # Exact match on code (highest priority)
            if code_lower == query_lower:
                scored.append((0, code))
            # Code prefix match
            elif code_lower.startswith(query_lower):
                scored.append((1, code))
            # Name prefix match
            elif name_lower.startswith(query_lower):
                scored.append((2, code))
            # Contains match in name
            elif query_lower in name_lower:
                scored.append((3, code))
            # Contains match in code
            elif query_lower in code_lower:
                scored.append((4, code))

        # Sort by score (priority) and return codes
        scored.sort(key=lambda x: x[0])
        return [code for _, code in scored[:limit]]

    def _fuzzy_search(self, query: str, limit: int, threshold: int) -> list[str]:
        """Perform fuzzy search using rapidfuzz.

        Args:
            query: Search query string.
            limit: Maximum number of results.
            threshold: Minimum score for fuzzy matches.

        Returns:
            List of matching language codes sorted by score.
        """
        codes = list(self._languages_data.keys())
        texts = [f"{code} {entry.name}" for code, entry in self._languages_data.items()]

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
        """Suggest similar language codes based on input.

        Uses fuzzy matching (when available) to find codes with similar prefixes
        or names. Returns codes in format "code (Name)".

        Args:
            code: The invalid code to find suggestions for.
            limit: Maximum number of suggestions to return.
            fuzzy: Fuzzy matching mode. None (default) auto-detects: uses fuzzy if
                rapidfuzz is installed, otherwise falls back to substring matching.
                True forces fuzzy matching (raises ImportError if not available).
                False forces substring matching.
            threshold: Minimum score (0-100) for fuzzy matches.

        Returns:
            List of suggestions in format "code (Name)" (no duplicates).

        Raises:
            ImportError: If fuzzy=True but rapidfuzz is not installed.
        """
        use_fuzzy = resolve_fuzzy_mode(fuzzy)
        if use_fuzzy:
            return self._fuzzy_suggest(code, limit, threshold)
        return self._substring_suggest(code, limit)

    def _substring_suggest(self, code: str, limit: int) -> list[str]:
        """Suggest using substring matching.

        Args:
            code: The code to find suggestions for.
            limit: Maximum number of suggestions.

        Returns:
            List of suggestions.
        """
        code_lower = code.lower()
        suggestions: list[str] = []
        seen: set[str] = set()

        # Strategy 1: Exact prefix match on code (highest priority)
        for lang_code, entry in self._languages_data.items():
            if lang_code.lower().startswith(code_lower) and lang_code not in seen:
                suggestions.append(f"{lang_code} ({entry.name})")
                seen.add(lang_code)
                if len(suggestions) >= limit:
                    return suggestions

        # Strategy 2: Contains match in language name
        for lang_code, entry in self._languages_data.items():
            if code_lower in entry.name.lower() and lang_code not in seen:
                suggestions.append(f"{lang_code} ({entry.name})")
                seen.add(lang_code)
                if len(suggestions) >= limit:
                    return suggestions

        # Strategy 3: Partial match (code is substring of language code)
        for lang_code, entry in self._languages_data.items():
            if code_lower in lang_code.lower() and lang_code not in seen:
                suggestions.append(f"{lang_code} ({entry.name})")
                seen.add(lang_code)
                if len(suggestions) >= limit:
                    return suggestions

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
        codes = list(self._languages_data.keys())
        texts = [f"{c} {entry.name}" for c, entry in self._languages_data.items()]

        matches = fuzzy_search(code, texts, threshold=threshold, limit=limit)

        suggestions: list[str] = []
        for _, _, idx in matches:
            lang_code = codes[idx]
            entry = self._languages_data[lang_code]
            suggestions.append(f"{lang_code} ({entry.name})")

        return suggestions

    def validate(self, code: str) -> None:
        """Validate language code, raising exception if invalid.

        Args:
            code: Language code to validate (case-insensitive).

        Raises:
            InvalidCodeError: If code is not valid, with helpful suggestions.
        """
        if code in self:
            return

        suggestions = self.suggest(code)
        msg = f"Invalid language code: {code!r}"
        raise InvalidCodeError(
            msg,
            code=code,
            code_type="language",
            suggestions=suggestions,
            help_url=_HELP_URL,
        )
