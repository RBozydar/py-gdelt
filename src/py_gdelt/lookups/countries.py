"""
Country code conversions for GDELT data.

This module provides the Countries class for converting between FIPS and ISO
country codes used in GDELT data.
"""

from __future__ import annotations

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.lookups._utils import fuzzy_search, load_lookup_json, resolve_fuzzy_mode
from py_gdelt.lookups.models import CountryEntry


__all__ = ["Countries"]


class Countries:
    """
    FIPS/ISO country code conversions.

    Provides methods to convert between FIPS 10-4 codes (used in GDELT v1)
    and ISO 3166-1 alpha-3 codes (used in GDELT v2).

    All data is loaded lazily from JSON files on first access.
    """

    def __init__(self) -> None:
        self._countries: dict[str, CountryEntry] | None = None
        self._iso_to_fips_map: dict[str, str] | None = None

    @property
    def _countries_data(self) -> dict[str, CountryEntry]:
        """Lazy load countries data (FIPS as key)."""
        if self._countries is None:
            raw_data = load_lookup_json("countries.json")
            self._countries = {code: CountryEntry(**data) for code, data in raw_data.items()}
        return self._countries

    @property
    def _iso_to_fips_mapping(self) -> dict[str, str]:
        """Lazy build reverse mapping from ISO3 to FIPS."""
        if self._iso_to_fips_map is None:
            self._iso_to_fips_map = {
                entry.iso3: fips
                for fips, entry in self._countries_data.items()
                if entry.iso3 is not None
            }
        return self._iso_to_fips_map

    def __len__(self) -> int:
        """Return the number of countries in the lookup.

        Returns:
            Number of countries.
        """
        return len(self._countries_data)

    def __contains__(self, code: str) -> bool:
        """
        Check if country code exists.

        Args:
            code: Country code (FIPS or ISO3)

        Returns:
            True if code exists, False otherwise
        """
        code_upper = code.upper()
        return code_upper in self._countries_data or code_upper in self._iso_to_fips_mapping

    def __getitem__(self, code: str) -> CountryEntry:
        """
        Get full entry for country code.

        Args:
            code: Country code (FIPS or ISO3)

        Returns:
            Full country entry with metadata

        Raises:
            KeyError: If code is not found
        """
        code_upper = code.upper()
        # Try FIPS first
        if code_upper in self._countries_data:
            return self._countries_data[code_upper]
        # Try ISO3 via reverse mapping
        fips = self._iso_to_fips_mapping.get(code_upper)
        if fips is not None:
            return self._countries_data[fips]
        raise KeyError(code)

    def get(self, code: str) -> CountryEntry | None:
        """
        Get entry for country code, or None if not found.

        Args:
            code: Country code (FIPS or ISO3)

        Returns:
            Country entry, or None if code not found
        """
        code_upper = code.upper()
        # Try FIPS first
        entry = self._countries_data.get(code_upper)
        if entry is not None:
            return entry
        # Try ISO3 via reverse mapping
        fips = self._iso_to_fips_mapping.get(code_upper)
        if fips is not None:
            return self._countries_data.get(fips)
        return None

    def fips_to_iso3(self, fips: str) -> str | None:
        """
        Convert FIPS code to ISO 3166-1 alpha-3.

        Args:
            fips: FIPS 10-4 country code (e.g., "US", "UK")

        Returns:
            ISO 3166-1 alpha-3 code (e.g., "USA", "GBR"), or None if not found
        """
        entry = self._countries_data.get(fips.upper())
        return entry.iso3 if entry else None

    def fips_to_iso2(self, fips: str) -> str | None:
        """
        Convert FIPS code to ISO 3166-1 alpha-2.

        Args:
            fips: FIPS 10-4 country code (e.g., "US", "UK")

        Returns:
            ISO 3166-1 alpha-2 code (e.g., "US", "GB"), or None if not found
        """
        entry = self._countries_data.get(fips.upper())
        return entry.iso2 if entry else None

    def iso_to_fips(self, iso: str) -> str | None:
        """
        Convert ISO code to FIPS code.

        Args:
            iso: ISO 3166-1 alpha-3 country code (e.g., "USA", "GBR")

        Returns:
            FIPS 10-4 code (e.g., "US", "UK"), or None if not found
        """
        return self._iso_to_fips_mapping.get(iso)

    def get_name(self, code: str) -> str | None:
        """
        Get country name from either FIPS or ISO code.

        Args:
            code: FIPS or ISO country code

        Returns:
            Country name, or None if code not found
        """
        # Try FIPS first
        entry = self._countries_data.get(code.upper())
        if entry is not None:
            return entry.name

        # Try ISO3
        fips = self._iso_to_fips_mapping.get(code.upper())
        if fips is not None:
            entry = self._countries_data.get(fips)
            if entry is not None:
                return entry.name

        return None

    def validate(self, code: str) -> None:
        """
        Validate country code (FIPS or ISO), raising exception if invalid.

        Args:
            code: Country code to validate (FIPS or ISO)

        Raises:
            InvalidCodeError: If code is not valid
        """
        # Check if it's a valid FIPS code
        if code in self._countries_data:
            return

        # Check if it's a valid ISO code
        if code in self._iso_to_fips_mapping:
            return

        msg = f"Invalid country code: {code!r}"
        raise InvalidCodeError(msg, code=code, code_type="country")

    def normalize(self, code: str) -> str:
        """
        Normalize country code to FIPS format.

        Accepts both FIPS (2-char) and ISO3 (3-char) codes and returns
        the FIPS code for GDELT API compatibility.

        Args:
            code: Country code (FIPS or ISO3)

        Returns:
            FIPS code (2 characters) for GDELT API compatibility

        Raises:
            InvalidCodeError: If code is not valid
        """
        code_upper = code.upper()

        # Already FIPS and valid
        if code_upper in self._countries_data:
            return code_upper

        # Try ISO3 conversion
        if len(code_upper) == 3:
            fips = self._iso_to_fips_mapping.get(code_upper)
            if fips:
                return fips

        # Build helpful error with suggestions
        suggestions = self.suggest(code_upper)
        msg = f"Invalid country code: {code!r}"
        raise InvalidCodeError(
            msg,
            code=code,
            code_type="country",
            suggestions=suggestions,
            help_url="http://data.gdeltproject.org/api/v2/guides/LOOKUP-COUNTRIES.TXT",
        )

    def suggest(
        self,
        code: str,
        limit: int = 3,
        *,
        fuzzy: bool | None = None,
        threshold: int = 60,
    ) -> list[str]:
        """
        Suggest similar country codes based on input.

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
            List of suggestions in format "FIPS (Name)".

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
        code_upper = code.upper()
        suggestions: list[str] = []

        # Strategy 1: Exact prefix match on FIPS or ISO3 (highest priority)
        for fips, entry in self._countries_data.items():
            iso3_match = entry.iso3 is not None and entry.iso3.startswith(code_upper)
            if fips.startswith(code_upper) or iso3_match:
                suggestions.append(f"{fips} ({entry.name})")
                if len(suggestions) >= limit:
                    return suggestions

        # Strategy 2: Contains match in country name
        for fips, entry in self._countries_data.items():
            if code_upper in entry.name.upper():
                suggestions.append(f"{fips} ({entry.name})")
                if len(suggestions) >= limit:
                    return suggestions

        # Strategy 3: Partial match (code is substring of FIPS/ISO3)
        for fips, entry in self._countries_data.items():
            iso3_match = entry.iso3 is not None and code_upper in entry.iso3
            if code_upper in fips or iso3_match:
                suggestions.append(f"{fips} ({entry.name})")
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
        fips_codes = list(self._countries_data.keys())
        texts = [
            f"{fips} {entry.iso3 or ''} {entry.name}"
            for fips, entry in self._countries_data.items()
        ]

        matches = fuzzy_search(
            code,
            texts,
            threshold=threshold,
            limit=limit,
        )

        suggestions: list[str] = []
        for _, _, idx in matches:
            fips = fips_codes[idx]
            entry = self._countries_data[fips]
            suggestions.append(f"{fips} ({entry.name})")

        return suggestions

    def search(
        self,
        query: str,
        limit: int = 10,
        *,
        fuzzy: bool | None = None,
        threshold: int = 60,
    ) -> list[str]:
        """
        Search for countries by code or name.

        Searches FIPS codes, ISO codes, and country names (case-insensitive).
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
            List of matching FIPS codes.

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
            List of matching FIPS codes.
        """
        query_upper = query.upper()
        matches: list[str] = []
        seen: set[str] = set()

        # Strategy 1: Exact FIPS or ISO3 match
        for fips, entry in self._countries_data.items():
            codes = {fips, entry.iso3} if entry.iso3 else {fips}
            if query_upper in codes and fips not in seen:
                matches.append(fips)
                seen.add(fips)
                if len(matches) >= limit:
                    return matches

        # Strategy 2: FIPS or ISO3 prefix match
        for fips, entry in self._countries_data.items():
            iso3_match = entry.iso3 is not None and entry.iso3.startswith(query_upper)
            if (fips.startswith(query_upper) or iso3_match) and fips not in seen:
                matches.append(fips)
                seen.add(fips)
                if len(matches) >= limit:
                    return matches

        # Strategy 3: Name prefix match
        query_lower = query.lower()
        for fips, entry in self._countries_data.items():
            if entry.name.lower().startswith(query_lower) and fips not in seen:
                matches.append(fips)
                seen.add(fips)
                if len(matches) >= limit:
                    return matches

        # Strategy 4: Contains match in name
        for fips, entry in self._countries_data.items():
            if query_lower in entry.name.lower() and fips not in seen:
                matches.append(fips)
                seen.add(fips)
                if len(matches) >= limit:
                    return matches

        return matches

    def _fuzzy_search(self, query: str, limit: int, threshold: int) -> list[str]:
        """Perform fuzzy search using rapidfuzz.

        Args:
            query: Search query string.
            limit: Maximum number of results.
            threshold: Minimum score for fuzzy matches.

        Returns:
            List of matching FIPS codes sorted by score.
        """
        fips_codes = list(self._countries_data.keys())
        texts = [
            f"{fips} {entry.iso3 or ''} {entry.name}"
            for fips, entry in self._countries_data.items()
        ]

        matches = fuzzy_search(query, texts, threshold=threshold, limit=limit)

        return [fips_codes[idx] for _, _, idx in matches]
