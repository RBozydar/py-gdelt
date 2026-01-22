"""
Lookup tables for GDELT codes and identifiers.

This module provides unified access to all GDELT lookup tables including
CAMEO codes, GKG themes, country code conversions, GCAM dimensions,
image tags, and language codes.
"""

from functools import cached_property

from py_gdelt.lookups.cameo import CAMEOCodes
from py_gdelt.lookups.countries import Countries
from py_gdelt.lookups.gcam import GCAMLookup
from py_gdelt.lookups.image_tags import ImageTags
from py_gdelt.lookups.image_web_tags import ImageWebTags
from py_gdelt.lookups.languages import Languages
from py_gdelt.lookups.themes import GKGThemes


__all__ = [
    "CAMEOCodes",
    "Countries",
    "GCAMLookup",
    "GKGThemes",
    "ImageTags",
    "ImageWebTags",
    "Languages",
    "Lookups",
]


class Lookups:
    """
    Aggregates all lookup classes with lazy loading.

    Provides unified access to CAMEO codes, GKG themes, country code
    conversions, GCAM dimensions, image tags, and language codes.
    All lookup tables are loaded lazily on first access.

    Example:
        >>> lookups = Lookups()
        >>> lookups.cameo["01"].name
        'MAKE PUBLIC STATEMENT'
        >>> lookups.themes.get_category("ENV_CLIMATECHANGE")
        'Environment'
        >>> lookups.countries.fips_to_iso3("US")
        'USA'
        >>> lookups.languages.get_name("eng")
        'English'
        >>> lookups.image_tags.validate("TAG_PERSON")
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

    @cached_property
    def gcam(self) -> GCAMLookup:
        """
        Get GCAM codebook lookup instance.

        Returns:
            GCAMLookup instance for GCAM dimension lookups
        """
        return GCAMLookup()

    @cached_property
    def image_tags(self) -> ImageTags:
        """
        Get image tags lookup instance.

        Returns:
            ImageTags instance for Cloud Vision API tag lookups
        """
        return ImageTags()

    @cached_property
    def image_web_tags(self) -> ImageWebTags:
        """
        Get image web tags lookup instance.

        Returns:
            ImageWebTags instance for crowdsourced web tag lookups
        """
        return ImageWebTags()

    @cached_property
    def languages(self) -> Languages:
        """
        Get languages lookup instance.

        Returns:
            Languages instance for language code lookups
        """
        return Languages()

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
