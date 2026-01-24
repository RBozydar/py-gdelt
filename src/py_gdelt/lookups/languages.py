"""Language code lookups for GDELT DOC/GEO APIs."""

from __future__ import annotations

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.lookups._utils import load_lookup_json
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

    def search(self, query: str, limit: int = 10) -> list[str]:
        """Search for languages by code or name.

        Searches both language codes and names (case-insensitive).
        Results are ordered by relevance: exact code match, code prefix match,
        name prefix match, then contains match.

        Args:
            query: Search term (can match code or name).
            limit: Maximum number of results to return.

        Returns:
            List of matching language codes (no duplicates).
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

    def suggest(self, code: str, limit: int = 3) -> list[str]:
        """Suggest similar language codes based on input.

        Uses fuzzy matching to find codes with similar prefixes or names.
        Returns codes in format "code (Name)".

        Args:
            code: The invalid code to find suggestions for.
            limit: Maximum number of suggestions to return.

        Returns:
            List of suggestions in format "code (Name)" (no duplicates).
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
