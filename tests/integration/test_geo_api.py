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

    if not result.points:
        pytest.skip("No points returned - API may be temporarily unavailable")

    point = result.points[0]
    assert hasattr(point, "lat"), "Point should have lat"
    assert hasattr(point, "lon"), "Point should have lon"
    assert -90 <= point.lat <= 90, f"Latitude {point.lat} out of range"
    assert -180 <= point.lon <= 180, f"Longitude {point.lon} out of range"


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

    if "features" not in geojson or not geojson["features"]:
        pytest.skip("No GeoJSON features returned")

    assert isinstance(geojson["features"], list)
    assert len(geojson["features"]) > 0, "Expected at least one feature"


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

    if not result.points:
        pytest.skip("No points returned for bounding box test")

    # Verify points are within bounding box
    for point in result.points:
        assert europe_bbox[0] <= point.lat <= europe_bbox[2], f"Latitude {point.lat} outside bbox"
        assert europe_bbox[1] <= point.lon <= europe_bbox[3], f"Longitude {point.lon} outside bbox"


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

    if not result.points:
        pytest.skip("No points returned for attribute test")

    point = result.points[0]
    # Verify required attributes
    assert hasattr(point, "lat"), "Point should have lat"
    assert hasattr(point, "lon"), "Point should have lon"
    assert hasattr(point, "count"), "Point should have count"
    # Name may be None for some points
    assert hasattr(point, "name"), "Point should have name attribute"
    # Count should be positive
    assert point.count > 0, f"Expected positive count, got {point.count}"
