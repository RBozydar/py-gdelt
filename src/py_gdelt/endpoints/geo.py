"""GEO 2.0 API endpoint for geographic article data.

This module provides the GeoEndpoint class for querying GDELT's GEO 2.0 API,
which returns geographic locations mentioned in news articles matching a query.

The endpoint supports:
- Full-text search across news articles
- Time-based filtering
- Geographic bounding box constraints
- GeoJSON and plain JSON output formats

Example:
    async with GeoEndpoint() as geo:
        result = await geo.search("earthquake", max_points=100)
        for point in result.points:
            print(f"{point.name}: {point.count} articles at ({point.lat}, {point.lon})")
"""

from __future__ import annotations

from typing import Any, cast

from pydantic import BaseModel

from py_gdelt.endpoints.base import BaseEndpoint
from py_gdelt.filters import GeoFilter


__all__ = ["GeoEndpoint", "GeoPoint", "GeoResult"]


class GeoPoint(BaseModel):
    """Geographic point from GEO API.

    Represents a location mentioned in news articles with article count.

    Attributes:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        name: Location name if available
        count: Number of articles mentioning this location
        url: Representative article URL if available
    """

    lat: float
    lon: float
    name: str | None = None
    count: int = 1
    url: str | None = None


class GeoResult(BaseModel):
    """Result container for GEO API responses.

    Attributes:
        points: List of geographic points with article counts
        total_count: Total number of points in result
    """

    points: list[GeoPoint]
    total_count: int = 0


class GeoEndpoint(BaseEndpoint):
    """GEO 2.0 API endpoint for geographic article data.

    Returns locations mentioned in news articles matching a query.
    Supports time-based filtering and geographic bounds.

    Example:
        async with GeoEndpoint() as geo:
            result = await geo.search("earthquake", max_points=100)
            for point in result.points:
                print(f"{point.name}: {point.count} articles")

    Attributes:
        BASE_URL: GEO API base URL
    """

    BASE_URL = "https://api.gdeltproject.org/api/v2/geo/geo"

    async def _build_url(self, **kwargs: Any) -> str:
        """Build GEO API URL.

        The GEO API uses a fixed base URL with query parameters.

        Args:
            **kwargs: Unused, kept for BaseEndpoint compatibility

        Returns:
            Base URL for GEO API
        """
        return self.BASE_URL

    def _build_params(self, query_filter: GeoFilter) -> dict[str, str]:
        """Build query parameters from GeoFilter.

        Args:
            query_filter: GeoFilter with query parameters

        Returns:
            Dict of URL query parameters
        """
        params: dict[str, str] = {
            "query": query_filter.query,
            "format": "GeoJSON",  # GDELT GEO API requires exact case
            "maxpoints": str(query_filter.max_results),
        }

        if query_filter.timespan:
            params["timespan"] = query_filter.timespan

        # Add bounding box if provided (format: lon1,lat1,lon2,lat2)
        if query_filter.bounding_box:
            min_lat, min_lon, max_lat, max_lon = query_filter.bounding_box
            params["BBOX"] = f"{min_lon},{min_lat},{max_lon},{max_lat}"

        return params

    async def search(
        self,
        query: str,
        *,
        timespan: str | None = None,
        max_points: int = 250,
        bounding_box: tuple[float, float, float, float] | None = None,
    ) -> GeoResult:
        """Search for geographic locations in news.

        Args:
            query: Search query (full text search)
            timespan: Time range (e.g., "24h", "7d", "1m")
            max_points: Maximum points to return (1-250)
            bounding_box: Optional (min_lat, min_lon, max_lat, max_lon)

        Returns:
            GeoResult with list of GeoPoints

        Example:
            async with GeoEndpoint() as geo:
                result = await geo.search(
                    "earthquake",
                    timespan="7d",
                    max_points=50
                )
                print(f"Found {len(result.points)} locations")
        """
        query_filter = GeoFilter(
            query=query,
            timespan=timespan,
            max_results=min(max_points, 250),  # Cap at filter max
            bounding_box=bounding_box,
        )
        return await self.query(query_filter)

    async def query(self, query_filter: GeoFilter) -> GeoResult:
        """Query the GEO API with a filter.

        Args:
            query_filter: GeoFilter with query parameters

        Returns:
            GeoResult containing geographic points

        Raises:
            APIError: On request failure
            RateLimitError: On rate limit
            APIUnavailableError: On server error
        """
        params = self._build_params(query_filter)
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        # Parse GeoJSON features or raw points
        points: list[GeoPoint] = []

        if "features" in data:
            # GeoJSON format
            for feature in data["features"]:
                coords = feature.get("geometry", {}).get("coordinates", [])
                props = feature.get("properties", {})
                if len(coords) >= 2:
                    points.append(
                        GeoPoint(
                            lon=coords[0],
                            lat=coords[1],
                            name=props.get("name"),
                            count=props.get("count", 1),
                            url=props.get("url"),
                        ),
                    )
        elif "points" in data:
            # Plain JSON format
            points.extend([GeoPoint.model_validate(item) for item in data["points"]])

        return GeoResult(
            points=points,
            total_count=data.get("count", len(points)),
        )

    async def to_geojson(
        self,
        query: str,
        *,
        timespan: str | None = None,
        max_points: int = 250,
    ) -> dict[str, Any]:
        """Get raw GeoJSON response.

        Useful for direct use with mapping libraries (Leaflet, Folium, etc).

        Args:
            query: Search query
            timespan: Time range (e.g., "24h", "7d")
            max_points: Maximum points (1-250)

        Returns:
            Raw GeoJSON dict (FeatureCollection)

        Example:
            async with GeoEndpoint() as geo:
                geojson = await geo.to_geojson("climate change", timespan="30d")
                # Pass directly to mapping library
                folium.GeoJson(geojson).add_to(map)
        """
        query_filter = GeoFilter(
            query=query,
            timespan=timespan,
            max_results=min(max_points, 250),
        )

        params = self._build_params(query_filter)
        params["format"] = "geojson"
        url = await self._build_url()

        result = await self._get_json(url, params=params)
        return cast("dict[str, Any]", result)
