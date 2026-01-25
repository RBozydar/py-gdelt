"""GKG GeoJSON API endpoint (v1.0 Legacy).

This module provides the GKGGeoJSONEndpoint for querying geographic mentions
of themes, persons, and organizations from the GDELT Global Knowledge Graph.
Returns GeoJSON FeatureCollection output suitable for mapping applications.

Note:
    This is a v1.0 API that uses UPPERCASE parameter names (QUERY, TIMESPAN).
    The maximum timespan is 1440 minutes (24 hours).

Example:
    Search for geographic mentions of a theme:

        async with GKGGeoJSONEndpoint() as gkg:
            result = await gkg.search("TERROR", timespan=60)
            for feature in result.features:
                if coords := feature.coordinates:
                    print(f"Location: {coords}")

    Get raw GeoJSON for mapping libraries:

        async with GKGGeoJSONEndpoint() as gkg:
            geojson = await gkg.to_geojson("CLIMATE", timespan=120)
            # Pass directly to folium, geopandas, etc.
"""

from __future__ import annotations

from typing import Any, Literal, cast

from pydantic import BaseModel, ConfigDict

from py_gdelt.endpoints.base import BaseEndpoint
from py_gdelt.filters import GKGGeoJSONFilter


__all__ = [
    "GKGGeoJSONEndpoint",
    "GKGGeoJSONFeature",
    "GKGGeoJSONResult",
]


class GKGGeoJSONFeature(BaseModel):
    """A single GeoJSON feature from the GKG API.

    Attributes:
        type: GeoJSON type (always "Feature").
        geometry: GeoJSON geometry object with type and coordinates.
        properties: Feature properties (varies by query type).
    """

    model_config = ConfigDict(extra="allow")

    type: Literal["Feature"] = "Feature"
    geometry: dict[str, Any]
    properties: dict[str, Any]

    @property
    def coordinates(self) -> tuple[float, float] | None:
        """Extract coordinates as (longitude, latitude) if Point geometry.

        Note:
            GeoJSON uses [lon, lat] order, which this property preserves.

        Returns:
            Tuple of (longitude, latitude) or None if not a Point.
        """
        if self.geometry.get("type") == "Point":
            coords = self.geometry.get("coordinates")
            if isinstance(coords, list) and len(coords) >= 2:
                return (coords[0], coords[1])
        return None


class GKGGeoJSONResult(BaseModel):
    """GeoJSON FeatureCollection from GKG API.

    Attributes:
        type: GeoJSON type (always "FeatureCollection").
        features: List of GeoJSON features.
    """

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GKGGeoJSONFeature]


class GKGGeoJSONEndpoint(BaseEndpoint):
    """Endpoint for GKG GeoJSON API (v1.0 Legacy).

    Provides GeoJSON output for GKG themes, persons, and organizations
    within a rolling 24-hour window.

    Note:
        This is a v1.0 API that uses UPPERCASE parameter names (QUERY, TIMESPAN).
        Maximum timespan is 1440 minutes (24 hours).

    Attributes:
        BASE_URL: API endpoint URL.

    Example:
        async with GKGGeoJSONEndpoint() as gkg:
            result = await gkg.search("TERROR", timespan=60)
            for feature in result.features:
                if coords := feature.coordinates:
                    print(f"Location: {coords}")
    """

    BASE_URL: str = "https://api.gdeltproject.org/api/v1/gkg_geojson"

    async def _build_url(self, **kwargs: Any) -> str:
        """Build the request URL.

        Args:
            **kwargs: Unused, required by BaseEndpoint interface.

        Returns:
            The base GKG GeoJSON API URL.
        """
        return self.BASE_URL

    def _build_params(self, query_filter: GKGGeoJSONFilter) -> dict[str, str]:
        """Build query parameters with v1.0 UPPERCASE naming.

        Args:
            query_filter: Validated filter object.

        Returns:
            Dictionary with UPPERCASE parameter names for v1.0 API.
        """
        return {
            "QUERY": query_filter.query,
            "TIMESPAN": str(query_filter.timespan),
        }

    async def search(
        self,
        query: str,
        *,
        timespan: int = 60,
    ) -> GKGGeoJSONResult:
        """Search for geographic mentions of a theme/person/organization.

        Args:
            query: Theme (e.g., "TERROR"), person, or organization to search.
            timespan: Minutes of data to include (1-1440, default 60).

        Returns:
            GeoJSON FeatureCollection with matching locations.

        Raises:
            ValueError: If timespan exceeds 1440 minutes.
            APIError: If the API request fails.
            RateLimitError: If rate limit is exceeded.
            APIUnavailableError: If the API is temporarily unavailable.

        Example:
            result = await gkg.search("CLIMATE", timespan=120)
            print(f"Found {len(result.features)} locations")
        """
        query_filter = GKGGeoJSONFilter(query=query, timespan=timespan)
        return await self.query(query_filter)

    async def query(self, query_filter: GKGGeoJSONFilter) -> GKGGeoJSONResult:
        """Query using a filter object.

        Args:
            query_filter: Filter with query and timespan parameters.

        Returns:
            GeoJSON FeatureCollection result.

        Raises:
            APIError: If the API request fails.
            RateLimitError: If rate limit is exceeded.
            APIUnavailableError: If the API is temporarily unavailable.
        """
        url = await self._build_url()
        params = self._build_params(query_filter)
        data = await self._get_json(url, params=params)
        return GKGGeoJSONResult.model_validate(data)

    async def to_geojson(
        self,
        query: str,
        *,
        timespan: int = 60,
    ) -> dict[str, Any]:
        """Get raw GeoJSON dict without Pydantic parsing.

        Useful for passing directly to mapping libraries that expect
        GeoJSON dictionaries.

        Args:
            query: Theme, person, or organization to search.
            timespan: Minutes of data to include (1-1440).

        Returns:
            Raw GeoJSON dictionary.

        Raises:
            APIError: If the API request fails.
            RateLimitError: If rate limit is exceeded.
            APIUnavailableError: If the API is temporarily unavailable.
        """
        query_filter = GKGGeoJSONFilter(query=query, timespan=timespan)
        url = await self._build_url()
        params = self._build_params(query_filter)
        return cast("dict[str, Any]", await self._get_json(url, params=params))
