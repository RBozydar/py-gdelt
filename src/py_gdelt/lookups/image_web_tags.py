"""Crowdsourced image web tag lookups."""

from __future__ import annotations

from py_gdelt.lookups._base_tag_lookup import BaseTagLookup


__all__ = ["ImageWebTags"]


class ImageWebTags(BaseTagLookup):
    """Crowdsourced image web tag lookups with lazy loading.

    Provides methods to look up image web tag metadata from reverse Google Images search.
    Data is loaded lazily from JSON on first access. Keys are case-insensitive.
    """

    @property
    def _json_filename(self) -> str:
        """JSON data filename for the lookup data.

        Returns:
            Filename of the JSON file containing image web tag data.
        """
        return "image_web_tags.json"

    @property
    def _help_url(self) -> str:
        """Help URL for error messages.

        Returns:
            URL to documentation for image web tags.
        """
        return "http://data.gdeltproject.org/api/v2/guides/LOOKUP-IMAGEWEBTAGS.TXT"

    @property
    def _code_type(self) -> str:
        """Code type for InvalidCodeError.

        Returns:
            String identifier for the tag type.
        """
        return "image_web_tag"
