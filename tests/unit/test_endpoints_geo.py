"""Unit tests for GEO 2.0 API endpoint."""

from __future__ import annotations

import httpx
import pytest
import respx

from py_gdelt.endpoints.geo import GeoEndpoint, GeoPoint, GeoResult
from py_gdelt.filters import GeoFilter


class TestGeoPointModel:
    """Tests for GeoPoint Pydantic model."""

    def test_geo_point_creation(self) -> None:
        """Test GeoPoint model creation."""
        point = GeoPoint(lat=37.8, lon=-122.4, name="SF", count=10)
        assert point.lat == 37.8
        assert point.lon == -122.4
        assert point.count == 10
        assert point.name == "SF"

    def test_geo_point_defaults(self) -> None:
        """Test GeoPoint with default values."""
        point = GeoPoint(lat=0.0, lon=0.0)
        assert point.name is None
        assert point.count == 1
        assert point.url is None

    def test_geo_point_with_url(self) -> None:
        """Test GeoPoint with article URL."""
        point = GeoPoint(
            lat=40.7,
            lon=-74.0,
            name="NYC",
            url="https://example.com/article",
        )
        assert point.url == "https://example.com/article"


class TestGeoResultModel:
    """Tests for GeoResult Pydantic model."""

    def test_geo_result_creation(self) -> None:
        """Test GeoResult model creation."""
        result = GeoResult(
            points=[GeoPoint(lat=0, lon=0)],
            total_count=1,
        )
        assert len(result.points) == 1
        assert result.total_count == 1

    def test_geo_result_empty(self) -> None:
        """Test GeoResult with no points."""
        result = GeoResult(points=[], total_count=0)
        assert result.points == []
        assert result.total_count == 0

    def test_geo_result_multiple_points(self) -> None:
        """Test GeoResult with multiple points."""
        points = [
            GeoPoint(lat=37.8, lon=-122.4, name="SF"),
            GeoPoint(lat=40.7, lon=-74.0, name="NYC"),
        ]
        result = GeoResult(points=points, total_count=2)
        assert len(result.points) == 2
        assert result.points[0].name == "SF"
        assert result.points[1].name == "NYC"


class TestBuildParams:
    """Tests for parameter building."""

    def test_build_params_basic(self) -> None:
        """Test basic parameter building."""
        filter = GeoFilter(query="earthquake")
        endpoint = GeoEndpoint()
        params = endpoint._build_params(filter)

        assert params["query"] == "earthquake"
        assert params["format"] == "json"
        assert "maxpoints" in params
        assert params["maxpoints"] == "250"  # Default

    def test_build_params_with_bbox(self) -> None:
        """Test params with bounding box."""
        filter = GeoFilter(
            query="test",
            bounding_box=(30.0, -120.0, 40.0, -110.0),  # CA region
        )
        endpoint = GeoEndpoint()
        params = endpoint._build_params(filter)

        # BBOX format: lon1,lat1,lon2,lat2
        assert params["BBOX"] == "-120.0,30.0,-110.0,40.0"

    def test_build_params_with_timespan(self) -> None:
        """Test params with timespan."""
        filter = GeoFilter(query="test", timespan="7d")
        endpoint = GeoEndpoint()
        params = endpoint._build_params(filter)

        assert params["timespan"] == "7d"

    def test_build_params_max_results(self) -> None:
        """Test params with custom max_results."""
        filter = GeoFilter(query="test", max_results=50)
        endpoint = GeoEndpoint()
        params = endpoint._build_params(filter)

        assert params["maxpoints"] == "50"

    def test_build_params_all_options(self) -> None:
        """Test params with all options specified."""
        filter = GeoFilter(
            query="climate",
            timespan="30d",
            max_results=100,
            bounding_box=(25.0, -125.0, 50.0, -65.0),  # Continental US
        )
        endpoint = GeoEndpoint()
        params = endpoint._build_params(filter)

        assert params["query"] == "climate"
        assert params["timespan"] == "30d"
        assert params["maxpoints"] == "100"
        assert "BBOX" in params


class TestAPIRequests:
    """Tests for API request handling."""

    @respx.mock
    async def test_search_geojson_response(self) -> None:
        """Test parsing GeoJSON response."""
        respx.get("https://api.gdeltproject.org/api/v2/geo/geo").mock(
            return_value=httpx.Response(
                200,
                json={
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [-122.4, 37.8],
                            },
                            "properties": {"name": "San Francisco", "count": 50},
                        }
                    ],
                    "count": 1,
                },
            )
        )

        async with GeoEndpoint() as geo:
            result = await geo.search("tech")
            assert len(result.points) == 1
            assert result.points[0].name == "San Francisco"
            assert result.points[0].lat == 37.8
            assert result.points[0].lon == -122.4
            assert result.points[0].count == 50
            assert result.total_count == 1

    @respx.mock
    async def test_search_plain_json_response(self) -> None:
        """Test parsing plain JSON response."""
        respx.get("https://api.gdeltproject.org/api/v2/geo/geo").mock(
            return_value=httpx.Response(
                200,
                json={
                    "points": [
                        {"lat": 40.7, "lon": -74.0, "name": "New York", "count": 100}
                    ],
                    "count": 1,
                },
            )
        )

        async with GeoEndpoint() as geo:
            result = await geo.search("finance")
            assert len(result.points) == 1
            assert result.points[0].name == "New York"
            assert result.points[0].lat == 40.7
            assert result.points[0].lon == -74.0
            assert result.points[0].count == 100

    @respx.mock
    async def test_to_geojson(self) -> None:
        """Test raw GeoJSON output."""
        expected_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {"name": "Null Island"},
                }
            ],
        }
        respx.get("https://api.gdeltproject.org/api/v2/geo/geo").mock(
            return_value=httpx.Response(200, json=expected_geojson)
        )

        async with GeoEndpoint() as geo:
            geojson = await geo.to_geojson("test")
            assert geojson["type"] == "FeatureCollection"
            assert len(geojson["features"]) == 1
            assert geojson["features"][0]["properties"]["name"] == "Null Island"

    @respx.mock
    async def test_empty_response(self) -> None:
        """Test handling empty response."""
        respx.get("https://api.gdeltproject.org/api/v2/geo/geo").mock(
            return_value=httpx.Response(200, json={})
        )

        async with GeoEndpoint() as geo:
            result = await geo.search("nonexistent")
            assert result.points == []
            assert result.total_count == 0

    @respx.mock
    async def test_multiple_features(self) -> None:
        """Test response with multiple geographic points."""
        respx.get("https://api.gdeltproject.org/api/v2/geo/geo").mock(
            return_value=httpx.Response(
                200,
                json={
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [-122.4, 37.8],
                            },
                            "properties": {"name": "San Francisco", "count": 30},
                        },
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [-118.2, 34.0],
                            },
                            "properties": {
                                "name": "Los Angeles",
                                "count": 45,
                                "url": "https://example.com/article",
                            },
                        },
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [-87.6, 41.9],
                            },
                            "properties": {"name": "Chicago", "count": 20},
                        },
                    ],
                    "count": 3,
                },
            )
        )

        async with GeoEndpoint() as geo:
            result = await geo.search("technology")
            assert len(result.points) == 3
            assert result.total_count == 3

            # Verify first point
            assert result.points[0].name == "San Francisco"
            assert result.points[0].count == 30

            # Verify second point with URL
            assert result.points[1].name == "Los Angeles"
            assert result.points[1].url == "https://example.com/article"

            # Verify third point
            assert result.points[2].name == "Chicago"

    @respx.mock
    async def test_geojson_without_properties(self) -> None:
        """Test GeoJSON features with minimal properties."""
        respx.get("https://api.gdeltproject.org/api/v2/geo/geo").mock(
            return_value=httpx.Response(
                200,
                json={
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [10.0, 20.0],
                            },
                            "properties": {},
                        }
                    ],
                },
            )
        )

        async with GeoEndpoint() as geo:
            result = await geo.search("test")
            assert len(result.points) == 1
            assert result.points[0].lat == 20.0
            assert result.points[0].lon == 10.0
            assert result.points[0].name is None
            assert result.points[0].count == 1  # Default

    @respx.mock
    async def test_search_with_all_parameters(self) -> None:
        """Test search method with all parameters."""
        respx.get("https://api.gdeltproject.org/api/v2/geo/geo").mock(
            return_value=httpx.Response(200, json={"points": [], "count": 0})
        )

        async with GeoEndpoint() as geo:
            result = await geo.search(
                "earthquake",
                timespan="7d",
                max_points=50,
                bounding_box=(30.0, -120.0, 40.0, -110.0),
            )
            assert result.points == []

    @respx.mock
    async def test_query_with_filter(self) -> None:
        """Test query method with GeoFilter."""
        respx.get("https://api.gdeltproject.org/api/v2/geo/geo").mock(
            return_value=httpx.Response(
                200,
                json={
                    "points": [{"lat": 35.0, "lon": -100.0, "name": "Test"}],
                    "count": 1,
                },
            )
        )

        filter = GeoFilter(query="test", timespan="24h", max_results=100)

        async with GeoEndpoint() as geo:
            result = await geo.query(filter)
            assert len(result.points) == 1
            assert result.points[0].name == "Test"

    @respx.mock
    async def test_max_points_capped(self) -> None:
        """Test that max_points is capped at 250."""
        respx.get("https://api.gdeltproject.org/api/v2/geo/geo").mock(
            return_value=httpx.Response(200, json={})
        )

        async with GeoEndpoint() as geo:
            # Request more than 250
            result = await geo.search("test", max_points=500)

            # Check that the actual request was capped at 250
            request = respx.calls.last.request
            assert request.url.params["maxpoints"] == "250"


class TestURLBuilding:
    """Tests for URL construction."""

    async def test_build_url(self) -> None:
        """Test URL building returns correct base URL."""
        endpoint = GeoEndpoint()
        url = await endpoint._build_url()
        assert url == "https://api.gdeltproject.org/api/v2/geo/geo"

    def test_base_url_class_attribute(self) -> None:
        """Test BASE_URL class attribute."""
        assert GeoEndpoint.BASE_URL == "https://api.gdeltproject.org/api/v2/geo/geo"


class TestContextManager:
    """Tests for async context manager support."""

    @respx.mock
    async def test_context_manager_usage(self) -> None:
        """Test using endpoint as async context manager."""
        respx.get("https://api.gdeltproject.org/api/v2/geo/geo").mock(
            return_value=httpx.Response(200, json={"points": [], "count": 0})
        )

        async with GeoEndpoint() as geo:
            assert geo._client is not None
            result = await geo.search("test")
            assert isinstance(result, GeoResult)

        # Client should be closed after context exit
        # (we can't directly test this, but it's verified by BaseEndpoint tests)
