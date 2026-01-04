"""
Country code conversions for GDELT data.

This module provides the Countries class for converting between FIPS and ISO
country codes used in GDELT data.
"""

import json
from importlib.resources import files

from py_gdelt.exceptions import InvalidCodeError

__all__ = ["Countries"]


class Countries:
    """
    FIPS/ISO country code conversions.

    Provides methods to convert between FIPS 10-4 codes (used in GDELT v1)
    and ISO 3166-1 alpha-3 codes (used in GDELT v2).

    All data is loaded lazily from JSON files on first access.
    """

    def __init__(self) -> None:
        """Initialize Countries with lazy-loaded data."""
        self._countries: dict[str, dict[str, str]] | None = None
        self._iso_to_fips_map: dict[str, str] | None = None

    @property
    def _countries_data(self) -> dict[str, dict[str, str]]:
        """Lazy load countries data (FIPS as key)."""
        if self._countries is None:
            data_path = files("py_gdelt.lookups.data").joinpath("countries.json")
            self._countries = json.loads(data_path.read_text())
        return self._countries

    @property
    def _iso_to_fips_mapping(self) -> dict[str, str]:
        """Lazy build reverse mapping from ISO to FIPS."""
        if self._iso_to_fips_map is None:
            self._iso_to_fips_map = {
                data["iso"]: fips for fips, data in self._countries_data.items()
            }
        return self._iso_to_fips_map

    def fips_to_iso(self, fips: str) -> str | None:
        """
        Convert FIPS code to ISO code.

        Args:
            fips: FIPS 10-4 country code (e.g., "US", "UK")

        Returns:
            ISO 3166-1 alpha-3 code (e.g., "USA", "GBR"), or None if not found
        """
        country_data = self._countries_data.get(fips)
        if country_data is None:
            return None
        return country_data.get("iso")

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
        country_data = self._countries_data.get(code)
        if country_data is not None:
            return country_data.get("name")

        # Try ISO
        fips = self._iso_to_fips_mapping.get(code)
        if fips is not None:
            country_data = self._countries_data.get(fips)
            if country_data is not None:
                return country_data.get("name")

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
