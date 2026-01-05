"""Integration tests for GEO 2.0 API."""

import pytest

from py_gdelt import GDELTClient


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_geo_search_returns_points(gdelt_client: GDELTClient) -> None:
    """Test that GEO search returns geographic points."""
    result = await gdelt_client.geo.search(
        "earthquake",
        timespan="7d",
        max_points=20,
    )

    assert hasattr(result, "points")
    assert isinstance(result.points, list)

    if result.points:
        point = result.points[0]
        assert hasattr(point, "lat")
        assert hasattr(point, "lon")
        assert -90 <= point.lat <= 90
        assert -180 <= point.lon <= 180


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_geo_geojson_format(gdelt_client: GDELTClient) -> None:
    """Test GeoJSON output format."""
    geojson = await gdelt_client.geo.to_geojson(
        "flood",
        timespan="7d",
    )

    # Verify GeoJSON structure
    assert isinstance(geojson, dict)
    # May be FeatureCollection or empty
    if "features" in geojson:
        assert isinstance(geojson["features"], list)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_geo_bounding_box_filter(gdelt_client: GDELTClient) -> None:
    """Test geographic bounding box filtering."""
    # Europe bounding box
    europe_bbox = (35.0, -10.0, 70.0, 40.0)

    result = await gdelt_client.geo.search(
        "energy",
        timespan="7d",
        bounding_box=europe_bbox,
        max_points=30,
    )

    assert hasattr(result, "points")
    assert isinstance(result.points, list)

    # If we got points, verify they're within bounding box
    if result.points:
        for point in result.points:
            assert europe_bbox[0] <= point.lat <= europe_bbox[2]
            assert europe_bbox[1] <= point.lon <= europe_bbox[3]


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_geo_search_with_max_points(gdelt_client: GDELTClient) -> None:
    """Test max_points parameter."""
    max_points = 10

    result = await gdelt_client.geo.search(
        "climate",
        timespan="24h",
        max_points=max_points,
    )

    # Result may have fewer than max_points, but never more
    assert len(result.points) <= max_points


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_geo_point_attributes(gdelt_client: GDELTClient) -> None:
    """Test that geographic points have expected attributes."""
    result = await gdelt_client.geo.search(
        "protest",
        timespan="7d",
        max_points=5,
    )

    if result.points:
        point = result.points[0]
        # Verify required attributes
        assert hasattr(point, "lat")
        assert hasattr(point, "lon")
        assert hasattr(point, "count")
        # Name may be None for some points
        assert hasattr(point, "name")
        # Count should be positive
        assert point.count > 0
