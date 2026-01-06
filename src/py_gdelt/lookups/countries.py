"""
Country code conversions for GDELT data.

This module provides the Countries class for converting between FIPS and ISO
country codes used in GDELT data.
"""

import json
from importlib.resources import files
from typing import Any

from py_gdelt.exceptions import InvalidCodeError
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

    def _load_json(self, filename: str) -> dict[str, dict[str, Any]]:
        """Load JSON data from package resources."""
        data_path = files("py_gdelt.lookups.data").joinpath(filename)
        return json.loads(data_path.read_text())  # type: ignore[no-any-return]

    @property
    def _countries_data(self) -> dict[str, CountryEntry]:
        """Lazy load countries data (FIPS as key)."""
        if self._countries is None:
            raw_data = self._load_json("countries.json")
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

    def __contains__(self, code: str) -> bool:
        """
        Check if country code exists.

        Args:
            code: Country code (FIPS or ISO)

        Returns:
            True if code exists, False otherwise
        """
        return code.upper() in self._countries_data

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
