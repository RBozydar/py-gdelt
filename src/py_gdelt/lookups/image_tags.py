"""Cloud Vision API image tag lookups."""

from __future__ import annotations

from py_gdelt.lookups._base_tag_lookup import BaseTagLookup


__all__ = ["ImageTags"]


class ImageTags(BaseTagLookup):
    """Cloud Vision API image tag lookups with lazy loading.

    Provides methods to look up image tag metadata and validate tags.
    Data is loaded lazily from JSON on first access. Keys are case-insensitive.
    """

    @property
    def _json_filename(self) -> str:
        """JSON data filename for the lookup data.

        Returns:
            Filename of the JSON file containing image tag data.
        """
        return "image_tags.json"

    @property
    def _help_url(self) -> str:
        """Help URL for error messages.

        Returns:
            URL to documentation for image tags.
        """
        return "http://data.gdeltproject.org/api/v2/guides/LOOKUP-IMAGETAGS.TXT"

    @property
    def _code_type(self) -> str:
        """Code type for InvalidCodeError.

        Returns:
            String identifier for the tag type.
        """
        return "image_tag"
