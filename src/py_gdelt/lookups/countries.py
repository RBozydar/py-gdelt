"""
Country code conversions for GDELT data.

This module provides the Countries class for converting between FIPS and ISO
country codes used in GDELT data.
"""

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.lookups._utils import load_lookup_json
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
                entry.iso3: fips for fips, entry in self._countries_data.items()
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
        # Check FIPS codes (keys in _countries_data)
        if code_upper in self._countries_data:
            return True
        # Check ISO3 codes (reverse mapping)
        return code_upper in self._iso_to_fips_mapping

    def __getitem__(self, code: str) -> CountryEntry:
        """
        Get full entry for country code.

        Args:
            code: Country code (FIPS)

        Returns:
            Full country entry with metadata

        Raises:
            KeyError: If code is not found
        """
        return self._countries_data[code.upper()]

    def get(self, code: str) -> CountryEntry | None:
        """
        Get entry for country code, or None if not found.

        Args:
            code: Country code (FIPS)

        Returns:
            Country entry, or None if code not found
        """
        return self._countries_data.get(code.upper())

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

    def suggest(self, code: str, limit: int = 3) -> list[str]:
        """
        Suggest similar country codes based on input.

        Uses fuzzy matching to find codes with similar prefixes or names.

        Args:
            code: The invalid code to find suggestions for
            limit: Maximum number of suggestions to return

        Returns:
            List of suggestions in format "FIPS (Name)"
        """
        code_upper = code.upper()
        suggestions = []

        # Strategy 1: Exact prefix match on FIPS or ISO3 (highest priority)
        for fips, entry in self._countries_data.items():
            if fips.startswith(code_upper) or entry.iso3.startswith(code_upper):
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
            if code_upper in fips or code_upper in entry.iso3:
                suggestions.append(f"{fips} ({entry.name})")
                if len(suggestions) >= limit:
                    return suggestions

        return suggestions

    def search(self, query: str, limit: int = 10) -> list[str]:
        """
        Search for countries by code or name.

        Searches FIPS codes, ISO codes, and country names (case-insensitive).
        Results are ordered by relevance: exact code match, code prefix match,
        name prefix match, then contains match.

        Args:
            query: Search term (can match code or name).
            limit: Maximum number of results to return.

        Returns:
            List of matching FIPS codes.
        """
        query_upper = query.upper()
        matches: list[str] = []
        seen: set[str] = set()

        # Strategy 1: Exact FIPS or ISO3 match
        for fips, entry in self._countries_data.items():
            if query_upper in (fips, entry.iso3) and fips not in seen:
                matches.append(fips)
                seen.add(fips)
                if len(matches) >= limit:
                    return matches

        # Strategy 2: FIPS or ISO3 prefix match
        for fips, entry in self._countries_data.items():
            if (
                fips.startswith(query_upper) or entry.iso3.startswith(query_upper)
            ) and fips not in seen:
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
