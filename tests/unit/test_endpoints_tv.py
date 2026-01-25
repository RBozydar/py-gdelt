"""Tests for TV and TVAI API endpoints."""

from datetime import UTC, datetime

import httpx
import pytest
import respx

from py_gdelt.endpoints.tv import (
    TVAIEndpoint,
    TVClip,
    TVEndpoint,
    TVStationChart,
    TVStationData,
    TVTimeline,
    TVTimelinePoint,
)
from py_gdelt.filters import TVFilter
from py_gdelt.utils.dates import try_parse_gdelt_datetime


# Model Tests


def test_tv_clip_creation() -> None:
    """Test TVClip model."""
    clip = TVClip(
        station="CNN",
        show_name="Anderson Cooper 360",
        snippet="Breaking news...",
    )
    assert clip.station == "CNN"
    assert clip.show_name == "Anderson Cooper 360"
    assert clip.snippet == "Breaking news..."
    assert clip.clip_url is None
    assert clip.preview_url is None
    assert clip.date is None
    assert clip.duration_seconds is None


def test_tv_clip_full() -> None:
    """Test TVClip with all fields."""
    clip = TVClip(
        station="MSNBC",
        show_name="Rachel Maddow Show",
        clip_url="https://example.com/clip",
        preview_url="https://example.com/thumb.jpg",
        date=datetime(2024, 1, 15, 20, 0, 0),
        duration_seconds=180,
        snippet="In today's news...",
    )
    assert clip.station == "MSNBC"
    assert clip.show_name == "Rachel Maddow Show"
    assert clip.clip_url == "https://example.com/clip"
    assert clip.preview_url == "https://example.com/thumb.jpg"
    assert clip.date == datetime(2024, 1, 15, 20, 0, 0)
    assert clip.duration_seconds == 180
    assert clip.snippet == "In today's news..."


def test_tv_timeline_point() -> None:
    """Test TVTimelinePoint model."""
    point = TVTimelinePoint(date="2024-01-01", station="CNN", count=50)
    assert point.date == "2024-01-01"
    assert point.station == "CNN"
    assert point.count == 50


def test_tv_timeline_point_no_station() -> None:
    """Test TVTimelinePoint without station."""
    point = TVTimelinePoint(date="2024-01-01", count=100)
    assert point.date == "2024-01-01"
    assert point.station is None
    assert point.count == 100


def test_tv_timeline() -> None:
    """Test TVTimeline model."""
    timeline = TVTimeline(
        points=[
            TVTimelinePoint(date="2024-01-01", count=50),
            TVTimelinePoint(date="2024-01-02", count=75),
        ],
    )
    assert len(timeline.points) == 2
    assert timeline.points[0].count == 50
    assert timeline.points[1].count == 75


def test_tv_station_data() -> None:
    """Test TVStationData model."""
    data = TVStationData(station="CNN", count=100, percentage=33.3)
    assert data.station == "CNN"
    assert data.count == 100
    assert data.percentage == 33.3


def test_tv_station_data_no_percentage() -> None:
    """Test TVStationData without percentage."""
    data = TVStationData(station="FOX", count=50)
    assert data.station == "FOX"
    assert data.count == 50
    assert data.percentage is None


def test_tv_station_chart() -> None:
    """Test TVStationChart model."""
    chart = TVStationChart(
        stations=[
            TVStationData(station="CNN", count=100, percentage=50.0),
            TVStationData(station="FOX", count=100, percentage=50.0),
        ],
    )
    assert len(chart.stations) == 2
    assert chart.stations[0].station == "CNN"
    assert chart.stations[1].station == "FOX"


# Date Parsing Tests


def test_try_parse_gdelt_datetime_gdelt_format() -> None:
    """Test parsing GDELT date format."""
    result = try_parse_gdelt_datetime("20240115120000")
    assert result == datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)


def test_try_parse_gdelt_datetime_iso_format() -> None:
    """Test parsing ISO date format."""
    result = try_parse_gdelt_datetime("2024-01-15T12:00:00")
    assert result is not None
    assert result == datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)


def test_try_parse_gdelt_datetime_none() -> None:
    """Test parsing None returns None."""
    assert try_parse_gdelt_datetime(None) is None


def test_try_parse_gdelt_datetime_empty_string() -> None:
    """Test parsing empty string returns None."""
    assert try_parse_gdelt_datetime("") is None


def test_try_parse_gdelt_datetime_invalid() -> None:
    """Test parsing invalid date returns None."""
    assert try_parse_gdelt_datetime("invalid") is None
    assert try_parse_gdelt_datetime("2024") is None


# Parameter Building Tests


def test_build_params_basic() -> None:
    """Test basic parameter building."""
    filter = TVFilter(query="election")
    endpoint = TVEndpoint()
    params = endpoint._build_params(filter)

    assert params["query"] == "election"
    assert params["format"] == "json"
    assert params["mode"] == "ClipGallery"
    assert params["maxrecords"] == "250"


def test_build_params_with_station() -> None:
    """Test params with station filter.

    Station is now embedded in the query string, not as a separate parameter.
    """
    filter = TVFilter(query="test", station="CNN")
    endpoint = TVEndpoint()
    params = endpoint._build_params(filter)

    # Station is embedded in query, not as separate param
    assert "station:CNN" in params["query"]
    assert params["query"] == "test station:CNN"


def test_build_params_with_market() -> None:
    """Test params with market filter.

    Market is now embedded in the query string, not as a separate parameter.
    """
    filter = TVFilter(query="test", market="National")
    endpoint = TVEndpoint()
    params = endpoint._build_params(filter)

    # Market is embedded in query, not as separate param
    assert "market:National" in params["query"]


def test_build_params_with_timespan() -> None:
    """Test params with timespan.

    Timespan is now converted to explicit STARTDATETIME/ENDDATETIME.
    """
    filter = TVFilter(query="test", timespan="7d")
    endpoint = TVEndpoint()
    params = endpoint._build_params(filter)

    # Timespan is now converted to explicit datetime range
    assert "STARTDATETIME" in params
    assert "ENDDATETIME" in params
    assert "timespan" not in params


def test_build_params_with_datetime() -> None:
    """Test params with datetime range."""
    filter = TVFilter(
        query="test",
        start_datetime=datetime(2024, 1, 1, 0, 0, 0),
        end_datetime=datetime(2024, 1, 2, 0, 0, 0),
    )
    endpoint = TVEndpoint()
    params = endpoint._build_params(filter)

    assert params["STARTDATETIME"] == "20240101000000"
    assert params["ENDDATETIME"] == "20240102000000"


def test_build_params_start_datetime_only() -> None:
    """Test params with only start datetime."""
    filter = TVFilter(
        query="test",
        start_datetime=datetime(2024, 1, 1, 12, 30, 45),
    )
    endpoint = TVEndpoint()
    params = endpoint._build_params(filter)

    assert params["STARTDATETIME"] == "20240101123045"
    assert "ENDDATETIME" not in params


def test_build_params_max_results() -> None:
    """Test params with custom max_results."""
    filter = TVFilter(query="test", max_results=100)
    endpoint = TVEndpoint()
    params = endpoint._build_params(filter)

    assert params["maxrecords"] == "100"


def test_build_params_timeline_mode() -> None:
    """Test params with timeline mode."""
    filter = TVFilter(query="test", mode="TimelineVol")
    endpoint = TVEndpoint()
    params = endpoint._build_params(filter)

    assert params["mode"] == "TimelineVol"


def test_build_params_stationchart_mode() -> None:
    """Test params with stationchart mode."""
    filter = TVFilter(query="test", mode="StationChart")
    endpoint = TVEndpoint()
    params = endpoint._build_params(filter)

    assert params["mode"] == "StationChart"


# URL Building Tests


@pytest.mark.asyncio
async def test_build_url() -> None:
    """Test URL building for TV endpoint."""
    endpoint = TVEndpoint()
    url = await endpoint._build_url()
    assert url == "https://api.gdeltproject.org/api/v2/tv/tv"


@pytest.mark.asyncio
async def test_build_url_tvai() -> None:
    """Test URL building for TVAI endpoint."""
    endpoint = TVAIEndpoint()
    url = await endpoint._build_url()
    assert url == "https://api.gdeltproject.org/api/v2/tvai/tvai"


# API Tests - TVEndpoint


@respx.mock
@pytest.mark.asyncio
async def test_search_clips() -> None:
    """Test search method."""
    respx.get("https://api.gdeltproject.org/api/v2/tv/tv").mock(
        return_value=httpx.Response(
            200,
            json={
                "clips": [
                    {
                        "station": "CNN",
                        "show": "News",
                        "snippet": "Test clip",
                        "date": "20240101120000",
                    },
                ],
            },
        ),
    )

    endpoint = TVEndpoint()
    async with endpoint:
        clips = await endpoint.search("test")
        assert len(clips) == 1
        assert clips[0].station == "CNN"
        assert clips[0].show_name == "News"
        assert clips[0].snippet == "Test clip"
        assert clips[0].date == datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)


@respx.mock
@pytest.mark.asyncio
async def test_search_with_parameters() -> None:
    """Test search with all parameters.

    Station and market are now embedded in query, timespan is converted to datetime range.
    """
    mock_route = respx.get("https://api.gdeltproject.org/api/v2/tv/tv").mock(
        return_value=httpx.Response(200, json={"clips": []}),
    )

    endpoint = TVEndpoint()
    async with endpoint:
        await endpoint.search(
            "climate change",
            station="CNN",
            market="National",
            timespan="7d",
            max_results=100,
        )

    # Verify the request parameters
    assert mock_route.called
    request = mock_route.calls[0].request
    params = dict(request.url.params)
    # Station and market are now embedded in query string
    assert "climate change" in params["query"]
    assert "station:CNN" in params["query"]
    assert "market:National" in params["query"]
    # Timespan is now converted to explicit datetime range
    assert "STARTDATETIME" in params
    assert "ENDDATETIME" in params
    assert params["maxrecords"] == "100"
    assert params["mode"] == "ClipGallery"


@respx.mock
@pytest.mark.asyncio
async def test_query_clips() -> None:
    """Test query_clips method with filter."""
    respx.get("https://api.gdeltproject.org/api/v2/tv/tv").mock(
        return_value=httpx.Response(
            200,
            json={
                "clips": [
                    {
                        "station": "MSNBC",
                        "show": "Morning Joe",
                        "url": "https://example.com/clip",
                        "preview": "https://example.com/thumb.jpg",
                        "duration": 120,
                        "snippet": "Breaking news story",
                    },
                ],
            },
        ),
    )

    filter = TVFilter(query="breaking", station="MSNBC")
    endpoint = TVEndpoint()
    async with endpoint:
        clips = await endpoint.query_clips(filter)
        assert len(clips) == 1
        assert clips[0].station == "MSNBC"
        assert clips[0].show_name == "Morning Joe"
        assert clips[0].clip_url == "https://example.com/clip"
        assert clips[0].preview_url == "https://example.com/thumb.jpg"
        assert clips[0].duration_seconds == 120


@respx.mock
@pytest.mark.asyncio
async def test_timeline() -> None:
    """Test timeline method."""
    respx.get("https://api.gdeltproject.org/api/v2/tv/tv").mock(
        return_value=httpx.Response(
            200,
            json={
                "timeline": [
                    {"date": "2024-01-01", "count": 100},
                    {"date": "2024-01-02", "count": 150},
                ],
            },
        ),
    )

    endpoint = TVEndpoint()
    async with endpoint:
        timeline = await endpoint.timeline("test")
        assert len(timeline.points) == 2
        assert timeline.points[0].date == "2024-01-01"
        assert timeline.points[0].count == 100
        assert timeline.points[1].date == "2024-01-02"
        assert timeline.points[1].count == 150


@respx.mock
@pytest.mark.asyncio
async def test_timeline_with_station() -> None:
    """Test timeline with station breakdown."""
    respx.get("https://api.gdeltproject.org/api/v2/tv/tv").mock(
        return_value=httpx.Response(
            200,
            json={
                "timeline": [
                    {"date": "2024-01-01", "station": "CNN", "count": 50},
                    {"date": "2024-01-01", "station": "FOX", "count": 75},
                ],
            },
        ),
    )

    endpoint = TVEndpoint()
    async with endpoint:
        timeline = await endpoint.timeline("test", station="CNN")
        assert len(timeline.points) == 2
        assert timeline.points[0].station == "CNN"
        assert timeline.points[1].station == "FOX"


@respx.mock
@pytest.mark.asyncio
async def test_station_chart() -> None:
    """Test station_chart method."""
    respx.get("https://api.gdeltproject.org/api/v2/tv/tv").mock(
        return_value=httpx.Response(
            200,
            json={
                "stations": [
                    {"station": "CNN", "count": 100},
                    {"station": "MSNBC", "count": 50},
                ],
            },
        ),
    )

    endpoint = TVEndpoint()
    async with endpoint:
        chart = await endpoint.station_chart("test")
        assert len(chart.stations) == 2
        # CNN should have ~66.7%, MSNBC ~33.3%
        assert chart.stations[0].station == "CNN"
        assert chart.stations[0].count == 100
        assert chart.stations[0].percentage is not None
        assert abs(chart.stations[0].percentage - 66.67) < 1

        assert chart.stations[1].station == "MSNBC"
        assert chart.stations[1].count == 50
        assert chart.stations[1].percentage is not None
        assert abs(chart.stations[1].percentage - 33.33) < 1


@respx.mock
@pytest.mark.asyncio
async def test_station_chart_zero_total() -> None:
    """Test station_chart with zero total (edge case)."""
    respx.get("https://api.gdeltproject.org/api/v2/tv/tv").mock(
        return_value=httpx.Response(
            200,
            json={
                "stations": [
                    {"station": "CNN", "count": 0},
                ],
            },
        ),
    )

    endpoint = TVEndpoint()
    async with endpoint:
        chart = await endpoint.station_chart("nonexistent")
        assert len(chart.stations) == 1
        assert chart.stations[0].percentage is None


@respx.mock
@pytest.mark.asyncio
async def test_empty_response() -> None:
    """Test handling empty response."""
    respx.get("https://api.gdeltproject.org/api/v2/tv/tv").mock(
        return_value=httpx.Response(200, json={}),
    )

    endpoint = TVEndpoint()
    async with endpoint:
        clips = await endpoint.search("nonexistent")
        assert clips == []


@respx.mock
@pytest.mark.asyncio
async def test_empty_clips_array() -> None:
    """Test handling empty clips array."""
    respx.get("https://api.gdeltproject.org/api/v2/tv/tv").mock(
        return_value=httpx.Response(200, json={"clips": []}),
    )

    endpoint = TVEndpoint()
    async with endpoint:
        clips = await endpoint.search("test")
        assert clips == []


@respx.mock
@pytest.mark.asyncio
async def test_empty_timeline() -> None:
    """Test handling empty timeline."""
    respx.get("https://api.gdeltproject.org/api/v2/tv/tv").mock(
        return_value=httpx.Response(200, json={"timeline": []}),
    )

    endpoint = TVEndpoint()
    async with endpoint:
        timeline = await endpoint.timeline("test")
        assert timeline.points == []


@respx.mock
@pytest.mark.asyncio
async def test_empty_stations() -> None:
    """Test handling empty stations."""
    respx.get("https://api.gdeltproject.org/api/v2/tv/tv").mock(
        return_value=httpx.Response(200, json={"stations": []}),
    )

    endpoint = TVEndpoint()
    async with endpoint:
        chart = await endpoint.station_chart("test")
        assert chart.stations == []


# API Tests - TVAIEndpoint


@respx.mock
@pytest.mark.asyncio
async def test_tvai_search() -> None:
    """Test TVAI endpoint search."""
    respx.get("https://api.gdeltproject.org/api/v2/tvai/tvai").mock(
        return_value=httpx.Response(
            200,
            json={"clips": [{"station": "FOX", "snippet": "AI clip"}]},
        ),
    )

    endpoint = TVAIEndpoint()
    async with endpoint:
        clips = await endpoint.search("test")
        assert len(clips) == 1
        assert clips[0].station == "FOX"
        assert clips[0].snippet == "AI clip"


@respx.mock
@pytest.mark.asyncio
async def test_tvai_search_with_parameters() -> None:
    """Test TVAI search with all parameters.

    Station is now embedded in query, timespan is converted to datetime range.
    """
    mock_route = respx.get("https://api.gdeltproject.org/api/v2/tvai/tvai").mock(
        return_value=httpx.Response(200, json={"clips": []}),
    )

    endpoint = TVAIEndpoint()
    async with endpoint:
        await endpoint.search(
            "artificial intelligence",
            station="CNN",
            timespan="30d",
            max_results=50,
        )

    # Verify the request parameters
    assert mock_route.called
    request = mock_route.calls[0].request
    params = dict(request.url.params)
    # Station is now embedded in query string
    assert "artificial intelligence" in params["query"]
    assert "station:CNN" in params["query"]
    # Timespan is now converted to explicit datetime range
    assert "STARTDATETIME" in params
    assert "ENDDATETIME" in params
    assert params["maxrecords"] == "50"
    assert params["mode"] == "ClipGallery"


@respx.mock
@pytest.mark.asyncio
async def test_tvai_empty_response() -> None:
    """Test TVAI handling empty response."""
    respx.get("https://api.gdeltproject.org/api/v2/tvai/tvai").mock(
        return_value=httpx.Response(200, json={}),
    )

    endpoint = TVAIEndpoint()
    async with endpoint:
        clips = await endpoint.search("nonexistent")
        assert clips == []


# Context Manager Tests


@pytest.mark.asyncio
async def test_context_manager_cleanup() -> None:
    """Test that context manager properly cleans up resources."""
    endpoint = TVEndpoint()
    async with endpoint:
        assert endpoint._client is not None
        assert endpoint._owns_client is True

    # Client should be closed after exiting context
    # We can't directly test if it's closed, but we can verify it ran


@pytest.mark.asyncio
async def test_shared_client() -> None:
    """Test using a shared HTTP client."""
    async with httpx.AsyncClient() as client:
        endpoint = TVEndpoint(client=client)
        assert endpoint._client is client
        assert endpoint._owns_client is False

        # Should not close shared client
        await endpoint.close()
        # Client should still be usable
        assert client.is_closed is False


# Integration-style Tests


@respx.mock
@pytest.mark.asyncio
async def test_multiple_queries_same_endpoint() -> None:
    """Test making multiple queries with the same endpoint instance."""
    respx.get("https://api.gdeltproject.org/api/v2/tv/tv").mock(
        return_value=httpx.Response(200, json={"clips": []}),
    )

    endpoint = TVEndpoint()
    async with endpoint:
        clips1 = await endpoint.search("query1")
        clips2 = await endpoint.search("query2")
        timeline = await endpoint.timeline("query3")
        chart = await endpoint.station_chart("query4")

        assert clips1 == []
        assert clips2 == []
        assert timeline.points == []
        assert chart.stations == []


@respx.mock
@pytest.mark.asyncio
async def test_clip_with_missing_fields() -> None:
    """Test handling clips with missing optional fields."""
    respx.get("https://api.gdeltproject.org/api/v2/tv/tv").mock(
        return_value=httpx.Response(
            200,
            json={
                "clips": [
                    {
                        "station": "CNN",
                        # Missing: show, url, preview, date, duration, snippet
                    },
                ],
            },
        ),
    )

    endpoint = TVEndpoint()
    async with endpoint:
        clips = await endpoint.search("test")
        assert len(clips) == 1
        assert clips[0].station == "CNN"
        assert clips[0].show_name is None
        assert clips[0].clip_url is None
        assert clips[0].preview_url is None
        assert clips[0].date is None
        assert clips[0].duration_seconds is None
        assert clips[0].snippet is None
