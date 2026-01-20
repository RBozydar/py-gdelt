"""Tests for GKG GeoJSON API endpoint (v1.0 Legacy)."""

from __future__ import annotations

import httpx
import pytest
import respx
from pydantic import ValidationError

from py_gdelt.endpoints.gkg_geojson import (
    GKGGeoJSONEndpoint,
    GKGGeoJSONFeature,
    GKGGeoJSONResult,
)
from py_gdelt.filters import GKGGeoJSONFilter


# Model Tests


def test_gkg_geojson_feature_creation() -> None:
    """Test GKGGeoJSONFeature model creation."""
    feature = GKGGeoJSONFeature(
        geometry={"type": "Point", "coordinates": [-74.006, 40.7128]},
        properties={"name": "New York", "count": 50},
    )
    assert feature.type == "Feature"
    assert feature.geometry["type"] == "Point"
    assert feature.geometry["coordinates"] == [-74.006, 40.7128]
    assert feature.properties["name"] == "New York"
    assert feature.properties["count"] == 50


def test_gkg_geojson_feature_coordinates_property() -> None:
    """Test coordinates property for Point geometry."""
    feature = GKGGeoJSONFeature(
        geometry={"type": "Point", "coordinates": [-74.006, 40.7128]},
        properties={},
    )
    coords = feature.coordinates
    assert coords is not None
    assert coords == (-74.006, 40.7128)


def test_gkg_geojson_feature_coordinates_non_point() -> None:
    """Test coordinates property returns None for non-Point geometry."""
    feature = GKGGeoJSONFeature(
        geometry={
            "type": "Polygon",
            "coordinates": [[[-74.0, 40.7], [-74.1, 40.8], [-74.0, 40.8], [-74.0, 40.7]]],
        },
        properties={},
    )
    assert feature.coordinates is None


def test_gkg_geojson_feature_coordinates_missing() -> None:
    """Test coordinates property with missing coordinates."""
    feature = GKGGeoJSONFeature(
        geometry={"type": "Point"},  # Missing coordinates
        properties={},
    )
    assert feature.coordinates is None


def test_gkg_geojson_feature_coordinates_incomplete() -> None:
    """Test coordinates property with incomplete coordinates."""
    feature = GKGGeoJSONFeature(
        geometry={"type": "Point", "coordinates": [-74.0]},  # Only one value
        properties={},
    )
    assert feature.coordinates is None


def test_gkg_geojson_result_creation() -> None:
    """Test GKGGeoJSONResult model creation."""
    result = GKGGeoJSONResult(
        features=[
            GKGGeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-74.006, 40.7128]},
                properties={"name": "NYC"},
            ),
            GKGGeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-118.2437, 34.0522]},
                properties={"name": "LA"},
            ),
        ],
    )
    assert result.type == "FeatureCollection"
    assert len(result.features) == 2
    assert result.features[0].properties["name"] == "NYC"
    assert result.features[1].properties["name"] == "LA"


def test_gkg_geojson_result_empty() -> None:
    """Test GKGGeoJSONResult with empty features."""
    result = GKGGeoJSONResult(features=[])
    assert result.type == "FeatureCollection"
    assert result.features == []


# Filter Tests


def test_gkg_geojson_filter_basic() -> None:
    """Test basic GKGGeoJSONFilter creation."""
    f = GKGGeoJSONFilter(query="TERROR")
    assert f.query == "TERROR"
    assert f.timespan == 60  # default


def test_gkg_geojson_filter_with_timespan() -> None:
    """Test GKGGeoJSONFilter with custom timespan."""
    f = GKGGeoJSONFilter(query="CLIMATE", timespan=120)
    assert f.query == "CLIMATE"
    assert f.timespan == 120


def test_gkg_geojson_filter_timespan_bounds() -> None:
    """Test timespan validation (1-1440)."""
    # Too low
    with pytest.raises(ValidationError):
        GKGGeoJSONFilter(query="test", timespan=0)

    # Too high
    with pytest.raises(ValidationError):
        GKGGeoJSONFilter(query="test", timespan=1441)

    # Valid boundaries
    f_min = GKGGeoJSONFilter(query="test", timespan=1)
    assert f_min.timespan == 1

    f_max = GKGGeoJSONFilter(query="test", timespan=1440)
    assert f_max.timespan == 1440


# Parameter Building Tests


def test_build_params_basic() -> None:
    """Test basic parameter building with UPPERCASE names."""
    query_filter = GKGGeoJSONFilter(query="TERROR")
    endpoint = GKGGeoJSONEndpoint()
    params = endpoint._build_params(query_filter)

    # v1.0 API uses UPPERCASE parameter names
    assert params["QUERY"] == "TERROR"
    assert params["TIMESPAN"] == "60"


def test_build_params_custom_timespan() -> None:
    """Test parameter building with custom timespan."""
    query_filter = GKGGeoJSONFilter(query="CLIMATE", timespan=120)
    endpoint = GKGGeoJSONEndpoint()
    params = endpoint._build_params(query_filter)

    assert params["QUERY"] == "CLIMATE"
    assert params["TIMESPAN"] == "120"


# URL Building Tests


@pytest.mark.asyncio
async def test_build_url() -> None:
    """Test URL building for GKG GeoJSON endpoint."""
    endpoint = GKGGeoJSONEndpoint()
    url = await endpoint._build_url()
    # Note: v1.0 API uses api/v1 path
    assert url == "https://api.gdeltproject.org/api/v1/gkg_geojson"


# API Tests


@respx.mock
@pytest.mark.asyncio
async def test_search() -> None:
    """Test search method."""
    respx.get("https://api.gdeltproject.org/api/v1/gkg_geojson").mock(
        return_value=httpx.Response(
            200,
            json={
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [-74.006, 40.7128]},
                        "properties": {"name": "New York", "count": 50},
                    },
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [-0.1276, 51.5074]},
                        "properties": {"name": "London", "count": 30},
                    },
                ],
            },
        ),
    )

    endpoint = GKGGeoJSONEndpoint()
    async with endpoint:
        result = await endpoint.search("TERROR")
        assert isinstance(result, GKGGeoJSONResult)
        assert result.type == "FeatureCollection"
        assert len(result.features) == 2
        assert result.features[0].properties["name"] == "New York"
        assert result.features[0].coordinates == (-74.006, 40.7128)
        assert result.features[1].properties["name"] == "London"


@respx.mock
@pytest.mark.asyncio
async def test_search_verifies_params() -> None:
    """Test that search sends correct UPPERCASE parameters."""
    mock_route = respx.get("https://api.gdeltproject.org/api/v1/gkg_geojson").mock(
        return_value=httpx.Response(
            200,
            json={"type": "FeatureCollection", "features": []},
        ),
    )

    endpoint = GKGGeoJSONEndpoint()
    async with endpoint:
        await endpoint.search("CLIMATE", timespan=120)

    assert mock_route.called
    request = mock_route.calls[0].request
    params = dict(request.url.params)
    # Verify UPPERCASE parameter names for v1.0 API
    assert params["QUERY"] == "CLIMATE"
    assert params["TIMESPAN"] == "120"


@respx.mock
@pytest.mark.asyncio
async def test_query_with_filter() -> None:
    """Test query method with filter object."""
    respx.get("https://api.gdeltproject.org/api/v1/gkg_geojson").mock(
        return_value=httpx.Response(
            200,
            json={
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [139.6917, 35.6895]},
                        "properties": {"name": "Tokyo"},
                    },
                ],
            },
        ),
    )

    query_filter = GKGGeoJSONFilter(query="EARTHQUAKE", timespan=60)
    endpoint = GKGGeoJSONEndpoint()
    async with endpoint:
        result = await endpoint.query(query_filter)
        assert len(result.features) == 1
        assert result.features[0].properties["name"] == "Tokyo"


@respx.mock
@pytest.mark.asyncio
async def test_to_raw_geojson() -> None:
    """Test to_raw_geojson method returns raw dict."""
    geojson_response = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [2.3522, 48.8566]},
                "properties": {"name": "Paris", "extra_field": "value"},
            },
        ],
    }
    respx.get("https://api.gdeltproject.org/api/v1/gkg_geojson").mock(
        return_value=httpx.Response(200, json=geojson_response),
    )

    endpoint = GKGGeoJSONEndpoint()
    async with endpoint:
        result = await endpoint.to_raw_geojson("PROTEST")
        # Result should be a raw dict, not a Pydantic model
        assert isinstance(result, dict)
        assert result["type"] == "FeatureCollection"
        assert len(result["features"]) == 1
        assert result["features"][0]["properties"]["extra_field"] == "value"


@respx.mock
@pytest.mark.asyncio
async def test_empty_features() -> None:
    """Test handling empty features array."""
    respx.get("https://api.gdeltproject.org/api/v1/gkg_geojson").mock(
        return_value=httpx.Response(
            200,
            json={"type": "FeatureCollection", "features": []},
        ),
    )

    endpoint = GKGGeoJSONEndpoint()
    async with endpoint:
        result = await endpoint.search("NONEXISTENT")
        assert result.type == "FeatureCollection"
        assert result.features == []


@respx.mock
@pytest.mark.asyncio
async def test_feature_with_extra_properties() -> None:
    """Test handling features with extra properties (ConfigDict extra='allow')."""
    respx.get("https://api.gdeltproject.org/api/v1/gkg_geojson").mock(
        return_value=httpx.Response(
            200,
            json={
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [0, 0]},
                        "properties": {"name": "Test"},
                        "id": "feature-123",  # Extra field not in model
                        "custom_field": "custom_value",  # Another extra field
                    },
                ],
            },
        ),
    )

    endpoint = GKGGeoJSONEndpoint()
    async with endpoint:
        result = await endpoint.search("TEST")
        assert len(result.features) == 1
        # The model should accept extra fields without error


# Context Manager Tests


@pytest.mark.asyncio
async def test_context_manager_cleanup() -> None:
    """Test that context manager properly cleans up resources."""
    endpoint = GKGGeoJSONEndpoint()
    async with endpoint:
        assert endpoint._client is not None
        assert endpoint._owns_client is True


@pytest.mark.asyncio
async def test_shared_client() -> None:
    """Test using a shared HTTP client."""
    async with httpx.AsyncClient() as client:
        endpoint = GKGGeoJSONEndpoint(client=client)
        assert endpoint._client is client
        assert endpoint._owns_client is False

        await endpoint.close()
        assert client.is_closed is False
