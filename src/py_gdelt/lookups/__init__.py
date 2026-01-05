"""
Lookup tables for GDELT codes and identifiers.

This module provides unified access to all GDELT lookup tables including
CAMEO codes, GKG themes, and country code conversions.
"""

from functools import cached_property

from py_gdelt.lookups.cameo import CAMEOCodes
from py_gdelt.lookups.countries import Countries
from py_gdelt.lookups.themes import GKGThemes


__all__ = [
    "CAMEOCodes",
    "Countries",
    "GKGThemes",
    "Lookups",
]


class Lookups:
    """
    Aggregates all lookup classes with lazy loading.

    Provides unified access to CAMEO codes, GKG themes, and country code
    conversions. All lookup tables are loaded lazily on first access.

    Example:
        >>> lookups = Lookups()
        >>> lookups.cameo["01"].name
        'MAKE PUBLIC STATEMENT'
        >>> lookups.themes.get_category("ENV_CLIMATECHANGE")
        'Environment'
        >>> lookups.countries.fips_to_iso3("US")
        'USA'
    """

    @cached_property
    def cameo(self) -> CAMEOCodes:
        """
        Get CAMEO codes lookup instance.

        Returns:
            CAMEOCodes instance for event code lookups
        """
        return CAMEOCodes()

    @cached_property
    def themes(self) -> GKGThemes:
        """
        Get GKG themes lookup instance.

        Returns:
            GKGThemes instance for theme lookups
        """
        return GKGThemes()

    @cached_property
    def countries(self) -> Countries:
        """
        Get country codes lookup instance.

        Returns:
            Countries instance for FIPS/ISO code conversions
        """
        return Countries()

    def validate_cameo(self, code: str) -> None:
        """
        Validate CAMEO code.

        Args:
            code: CAMEO code to validate

        Raises:
            InvalidCodeError: If code is not valid
        """
        self.cameo.validate(code)

    def validate_theme(self, theme: str) -> None:
        """
        Validate GKG theme.

        Args:
            theme: GKG theme code to validate

        Raises:
            InvalidCodeError: If theme is not valid
        """
        self.themes.validate(theme)

    def validate_country(self, code: str) -> None:
        """
        Validate country code (FIPS or ISO).

        Args:
            code: Country code to validate

        Raises:
            InvalidCodeError: If code is not valid
        """
        self.countries.validate(code)
