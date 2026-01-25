"""Tests for LowerThird (Chyron) API endpoint."""

from __future__ import annotations

from datetime import UTC, datetime

import httpx
import pytest
import respx
from pydantic import ValidationError

from py_gdelt.endpoints.lowerthird import (
    LowerThirdClip,
    LowerThirdEndpoint,
)
from py_gdelt.endpoints.tv import TVStationChart, TVTimeline
from py_gdelt.filters import LowerThirdFilter
from py_gdelt.utils.dates import try_parse_gdelt_datetime


# Model Tests


def test_lowerthird_clip_creation() -> None:
    """Test LowerThirdClip model with minimal fields."""
    clip = LowerThirdClip(
        station="CNN",
        chyron_text="BREAKING NEWS",
    )
    assert clip.station == "CNN"
    assert clip.chyron_text == "BREAKING NEWS"
    assert clip.show_name is None
    assert clip.date is None
    assert clip.preview_url is None
    assert clip.clip_url is None


def test_lowerthird_clip_full() -> None:
    """Test LowerThirdClip with all fields."""
    clip = LowerThirdClip(
        station="MSNBC",
        show_name="Morning Joe",
        date=datetime(2024, 1, 15, 9, 30, 0, tzinfo=UTC),
        preview_url="https://example.com/thumb.jpg",
        clip_url="https://example.com/clip",
        chyron_text="STOCK MARKET UPDATE",
    )
    assert clip.station == "MSNBC"
    assert clip.show_name == "Morning Joe"
    assert clip.date == datetime(2024, 1, 15, 9, 30, 0, tzinfo=UTC)
    assert clip.preview_url == "https://example.com/thumb.jpg"
    assert clip.clip_url == "https://example.com/clip"
    assert clip.chyron_text == "STOCK MARKET UPDATE"


# Filter Tests


def test_lowerthird_filter_basic() -> None:
    """Test basic LowerThirdFilter creation."""
    f = LowerThirdFilter(query="breaking news")
    assert f.query == "breaking news"
    assert f.timespan is None
    assert f.start_datetime is None
    assert f.end_datetime is None
    assert f.mode == "ClipGallery"
    assert f.max_results == 250
    assert f.sort is None


def test_lowerthird_filter_with_timespan() -> None:
    """Test LowerThirdFilter with timespan."""
    f = LowerThirdFilter(query="test", timespan="24h")
    assert f.timespan == "24h"
    assert f.start_datetime is None
    assert f.end_datetime is None


def test_lowerthird_filter_with_datetime_range() -> None:
    """Test LowerThirdFilter with datetime range."""
    f = LowerThirdFilter(
        query="test",
        start_datetime=datetime(2024, 1, 1, 0, 0, 0),
        end_datetime=datetime(2024, 1, 2, 0, 0, 0),
    )
    assert f.timespan is None
    assert f.start_datetime == datetime(2024, 1, 1, 0, 0, 0)
    assert f.end_datetime == datetime(2024, 1, 2, 0, 0, 0)


def test_lowerthird_filter_mutual_exclusion() -> None:
    """Test that timespan and datetime range are mutually exclusive."""
    with pytest.raises(
        ValidationError,
        match="Cannot specify both timespan and datetime range",
    ):
        LowerThirdFilter(
            query="test",
            timespan="24h",
            start_datetime=datetime(2024, 1, 1),
        )


def test_lowerthird_filter_max_results_bounds() -> None:
    """Test max_results validation (1-3000)."""
    # Too low
    with pytest.raises(ValidationError):
        LowerThirdFilter(query="test", max_results=0)

    # Too high
    with pytest.raises(ValidationError):
        LowerThirdFilter(query="test", max_results=3001)

    # Valid boundaries
    f_min = LowerThirdFilter(query="test", max_results=1)
    assert f_min.max_results == 1

    f_max = LowerThirdFilter(query="test", max_results=3000)
    assert f_max.max_results == 3000


def test_lowerthird_filter_mode_validation() -> None:
    """Test that mode accepts only valid values."""
    f1 = LowerThirdFilter(query="test", mode="ClipGallery")
    assert f1.mode == "ClipGallery"

    f2 = LowerThirdFilter(query="test", mode="TimelineVol")
    assert f2.mode == "TimelineVol"

    f3 = LowerThirdFilter(query="test", mode="StationChart")
    assert f3.mode == "StationChart"

    with pytest.raises(ValidationError):
        LowerThirdFilter(query="test", mode="invalid")  # type: ignore[arg-type]


def test_lowerthird_filter_sort_validation() -> None:
    """Test sort parameter validation."""
    f1 = LowerThirdFilter(query="test", sort="DateDesc")
    assert f1.sort == "DateDesc"

    f2 = LowerThirdFilter(query="test", sort="DateAsc")
    assert f2.sort == "DateAsc"

    with pytest.raises(ValidationError):
        LowerThirdFilter(query="test", sort="invalid")  # type: ignore[arg-type]


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
    query_filter = LowerThirdFilter(query="breaking news")
    endpoint = LowerThirdEndpoint()
    params = endpoint._build_params(query_filter)

    assert params["query"] == "breaking news"
    assert params["format"] == "json"
    assert params["mode"] == "ClipGallery"
    assert params["maxrecords"] == "250"
    assert "timespan" not in params
    assert "STARTDATETIME" not in params
    assert "sort" not in params


def test_build_params_with_timespan() -> None:
    """Test params with timespan."""
    query_filter = LowerThirdFilter(query="test", timespan="7d")
    endpoint = LowerThirdEndpoint()
    params = endpoint._build_params(query_filter)

    assert params["timespan"] == "7d"
    assert "STARTDATETIME" not in params


def test_build_params_with_datetime_range() -> None:
    """Test params with datetime range."""
    query_filter = LowerThirdFilter(
        query="test",
        start_datetime=datetime(2024, 1, 1, 12, 0, 0),
        end_datetime=datetime(2024, 1, 2, 12, 0, 0),
    )
    endpoint = LowerThirdEndpoint()
    params = endpoint._build_params(query_filter)

    assert params["STARTDATETIME"] == "20240101120000"
    assert params["ENDDATETIME"] == "20240102120000"
    assert "timespan" not in params


def test_build_params_with_sort() -> None:
    """Test params with sort parameter."""
    query_filter = LowerThirdFilter(query="test", sort="DateDesc")
    endpoint = LowerThirdEndpoint()
    params = endpoint._build_params(query_filter)

    assert params["sort"] == "DateDesc"


def test_build_params_with_max_results() -> None:
    """Test params with custom max_results."""
    query_filter = LowerThirdFilter(query="test", max_results=500)
    endpoint = LowerThirdEndpoint()
    params = endpoint._build_params(query_filter)

    assert params["maxrecords"] == "500"


# URL Building Tests


@pytest.mark.asyncio
async def test_build_url() -> None:
    """Test URL building for LowerThird endpoint."""
    endpoint = LowerThirdEndpoint()
    url = await endpoint._build_url()
    assert url == "https://api.gdeltproject.org/api/v2/lowerthird/lowerthird"


# API Tests


@respx.mock
@pytest.mark.asyncio
async def test_search_clips() -> None:
    """Test search method."""
    respx.get("https://api.gdeltproject.org/api/v2/lowerthird/lowerthird").mock(
        return_value=httpx.Response(
            200,
            json={
                "clips": [
                    {
                        "station": "CNN",
                        "show": "Anderson Cooper 360",
                        "snippet": "BREAKING: Major news event",
                        "date": "20240115200000",
                        "url": "https://example.com/clip",
                        "preview": "https://example.com/thumb.jpg",
                    },
                ],
            },
        ),
    )

    endpoint = LowerThirdEndpoint()
    async with endpoint:
        clips = await endpoint.search("breaking")
        assert len(clips) == 1
        assert clips[0].station == "CNN"
        assert clips[0].show_name == "Anderson Cooper 360"
        assert clips[0].chyron_text == "BREAKING: Major news event"
        assert clips[0].date == datetime(2024, 1, 15, 20, 0, 0, tzinfo=UTC)
        assert clips[0].clip_url == "https://example.com/clip"
        assert clips[0].preview_url == "https://example.com/thumb.jpg"


@respx.mock
@pytest.mark.asyncio
async def test_search_with_parameters() -> None:
    """Test search with all parameters."""
    mock_route = respx.get("https://api.gdeltproject.org/api/v2/lowerthird/lowerthird").mock(
        return_value=httpx.Response(200, json={"clips": []}),
    )

    endpoint = LowerThirdEndpoint()
    async with endpoint:
        await endpoint.search(
            "breaking news",
            timespan="24h",
            max_results=100,
            sort="DateDesc",
        )

    assert mock_route.called
    request = mock_route.calls[0].request
    params = dict(request.url.params)
    assert params["query"] == "breaking news"
    assert params["timespan"] == "24h"
    assert params["maxrecords"] == "100"
    assert params["sort"] == "DateDesc"
    assert params["mode"] == "ClipGallery"


@respx.mock
@pytest.mark.asyncio
async def test_query_clips() -> None:
    """Test query_clips method with filter."""
    respx.get("https://api.gdeltproject.org/api/v2/lowerthird/lowerthird").mock(
        return_value=httpx.Response(
            200,
            json={
                "clips": [
                    {
                        "station": "FOXNEWS",
                        "snippet": "LIVE: Press conference",
                    },
                ],
            },
        ),
    )

    query_filter = LowerThirdFilter(query="press conference", max_results=50)
    endpoint = LowerThirdEndpoint()
    async with endpoint:
        clips = await endpoint.query_clips(query_filter)
        assert len(clips) == 1
        assert clips[0].station == "FOXNEWS"
        assert clips[0].chyron_text == "LIVE: Press conference"


@respx.mock
@pytest.mark.asyncio
async def test_timeline() -> None:
    """Test timeline method."""
    respx.get("https://api.gdeltproject.org/api/v2/lowerthird/lowerthird").mock(
        return_value=httpx.Response(
            200,
            json={
                "timeline": [
                    {"date": "2024-01-01", "series": "CNN", "value": 100},
                    {"date": "2024-01-02", "series": "MSNBC", "value": 75},
                ],
            },
        ),
    )

    endpoint = LowerThirdEndpoint()
    async with endpoint:
        timeline = await endpoint.timeline("test")
        assert isinstance(timeline, TVTimeline)
        assert len(timeline.points) == 2
        assert timeline.points[0].date == "2024-01-01"
        assert timeline.points[0].station == "CNN"
        assert timeline.points[0].count == 100
        assert timeline.points[1].date == "2024-01-02"
        assert timeline.points[1].station == "MSNBC"
        assert timeline.points[1].count == 75


@respx.mock
@pytest.mark.asyncio
async def test_station_chart() -> None:
    """Test station_chart method."""
    respx.get("https://api.gdeltproject.org/api/v2/lowerthird/lowerthird").mock(
        return_value=httpx.Response(
            200,
            json={
                "stationchart": [
                    {"station": "CNN", "value": 150, "share": 50.0},
                    {"station": "MSNBC", "value": 100, "share": 33.3},
                    {"station": "FOXNEWS", "value": 50, "share": 16.7},
                ],
            },
        ),
    )

    endpoint = LowerThirdEndpoint()
    async with endpoint:
        chart = await endpoint.station_chart("test")
        assert isinstance(chart, TVStationChart)
        assert len(chart.stations) == 3
        assert chart.stations[0].station == "CNN"
        assert chart.stations[0].count == 150
        assert chart.stations[0].percentage == 50.0
        assert chart.stations[1].station == "MSNBC"
        assert chart.stations[2].station == "FOXNEWS"


@respx.mock
@pytest.mark.asyncio
async def test_empty_results() -> None:
    """Test handling empty response."""
    respx.get("https://api.gdeltproject.org/api/v2/lowerthird/lowerthird").mock(
        return_value=httpx.Response(200, json={}),
    )

    endpoint = LowerThirdEndpoint()
    async with endpoint:
        clips = await endpoint.search("nonexistent")
        assert clips == []


@respx.mock
@pytest.mark.asyncio
async def test_empty_clips_array() -> None:
    """Test handling empty clips array."""
    respx.get("https://api.gdeltproject.org/api/v2/lowerthird/lowerthird").mock(
        return_value=httpx.Response(200, json={"clips": []}),
    )

    endpoint = LowerThirdEndpoint()
    async with endpoint:
        clips = await endpoint.search("test")
        assert clips == []


@respx.mock
@pytest.mark.asyncio
async def test_empty_timeline() -> None:
    """Test handling empty timeline."""
    respx.get("https://api.gdeltproject.org/api/v2/lowerthird/lowerthird").mock(
        return_value=httpx.Response(200, json={"timeline": []}),
    )

    endpoint = LowerThirdEndpoint()
    async with endpoint:
        timeline = await endpoint.timeline("test")
        assert timeline.points == []


@respx.mock
@pytest.mark.asyncio
async def test_empty_station_chart() -> None:
    """Test handling empty station chart."""
    respx.get("https://api.gdeltproject.org/api/v2/lowerthird/lowerthird").mock(
        return_value=httpx.Response(200, json={"stationchart": []}),
    )

    endpoint = LowerThirdEndpoint()
    async with endpoint:
        chart = await endpoint.station_chart("test")
        assert chart.stations == []


@respx.mock
@pytest.mark.asyncio
async def test_clip_with_missing_fields() -> None:
    """Test handling clips with missing optional fields."""
    respx.get("https://api.gdeltproject.org/api/v2/lowerthird/lowerthird").mock(
        return_value=httpx.Response(
            200,
            json={
                "clips": [
                    {
                        "station": "CNN",
                        # Missing: show, url, preview, date, snippet
                    },
                ],
            },
        ),
    )

    endpoint = LowerThirdEndpoint()
    async with endpoint:
        clips = await endpoint.search("test")
        assert len(clips) == 1
        assert clips[0].station == "CNN"
        assert clips[0].show_name is None
        assert clips[0].clip_url is None
        assert clips[0].preview_url is None
        assert clips[0].date is None
        assert clips[0].chyron_text is None


# Context Manager Tests


@pytest.mark.asyncio
async def test_context_manager_cleanup() -> None:
    """Test that context manager properly cleans up resources."""
    endpoint = LowerThirdEndpoint()
    async with endpoint:
        assert endpoint._client is not None
        assert endpoint._owns_client is True


@pytest.mark.asyncio
async def test_shared_client() -> None:
    """Test using a shared HTTP client."""
    async with httpx.AsyncClient() as client:
        endpoint = LowerThirdEndpoint(client=client)
        assert endpoint._client is client
        assert endpoint._owns_client is False

        await endpoint.close()
        assert client.is_closed is False
