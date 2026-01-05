"""Integration tests for TV and TVAI APIs."""

import pytest

from py_gdelt import GDELTClient


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_tv_search_returns_clips(gdelt_client: GDELTClient) -> None:
    """Test TV search returns clips with expected structure."""
    clips = await gdelt_client.tv.search(
        "politics",
        timespan="24h",
        max_results=10,
    )

    assert isinstance(clips, list)

    if clips:
        clip = clips[0]
        assert hasattr(clip, "station")
        assert hasattr(clip, "show_name")
        assert clip.station  # Non-empty


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_tv_timeline(gdelt_client: GDELTClient) -> None:
    """Test TV timeline returns data points."""
    timeline = await gdelt_client.tv.timeline(
        "election",
        timespan="7d",
    )

    assert hasattr(timeline, "points")
    assert isinstance(timeline.points, list)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_tv_station_chart(gdelt_client: GDELTClient) -> None:
    """Test station chart returns station data."""
    chart = await gdelt_client.tv.station_chart(
        "healthcare",
        timespan="7d",
    )

    assert hasattr(chart, "stations")
    assert isinstance(chart.stations, list)

    if chart.stations:
        station = chart.stations[0]
        assert hasattr(station, "station")
        assert hasattr(station, "count")


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_tv_search_by_station(gdelt_client: GDELTClient) -> None:
    """Test filtering by specific station."""
    clips = await gdelt_client.tv.search(
        "economy",
        timespan="24h",
        station="CNN",
        max_results=5,
    )

    assert isinstance(clips, list)

    # If we got results, verify they're from CNN
    if clips:
        for clip in clips:
            assert clip.station == "CNN"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_tv_clip_attributes(gdelt_client: GDELTClient) -> None:
    """Test that TV clips have expected attributes."""
    clips = await gdelt_client.tv.search(
        "technology",
        timespan="24h",
        max_results=3,
    )

    if clips:
        clip = clips[0]
        # Required attributes
        assert hasattr(clip, "station")
        assert hasattr(clip, "show_name")
        # Optional attributes
        assert hasattr(clip, "date")
        assert hasattr(clip, "snippet")


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_tvai_search_returns_clips(gdelt_client: GDELTClient) -> None:
    """Test TVAI search returns clips."""
    clips = await gdelt_client.tv_ai.search(
        "artificial intelligence",
        timespan="7d",
        max_results=5,
    )

    assert isinstance(clips, list)

    if clips:
        clip = clips[0]
        assert hasattr(clip, "station")
        assert hasattr(clip, "show_name")


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_tv_max_results_parameter(gdelt_client: GDELTClient) -> None:
    """Test max_results parameter limits results."""
    max_results = 5

    clips = await gdelt_client.tv.search(
        "news",
        timespan="24h",
        max_results=max_results,
    )

    # May return fewer than max_results, but never more
    assert len(clips) <= max_results


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_tv_timeline_data_points(gdelt_client: GDELTClient) -> None:
    """Test timeline data points have expected structure."""
    timeline = await gdelt_client.tv.timeline(
        "climate",
        timespan="7d",
    )

    if timeline.points:
        point = timeline.points[0]
        assert hasattr(point, "date")
        assert hasattr(point, "count")
        assert point.count >= 0
