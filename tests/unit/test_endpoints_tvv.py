"""Tests for TV Visual (TVV) API endpoint."""

from __future__ import annotations

from datetime import date

import httpx
import pytest
import respx

from py_gdelt.endpoints.tvv import ChannelInfo, TVVEndpoint


# Model Tests


def test_channel_info_creation() -> None:
    """Test ChannelInfo model with minimal fields."""
    channel = ChannelInfo(
        id="CNN",
        label="CNN",
        startDate=20170801,
        endDate=99999999,
    )
    assert channel.id == "CNN"
    assert channel.label == "CNN"
    assert channel.start_date == 20170801
    assert channel.end_date == 99999999
    assert channel.location is None
    assert channel.has_search is None
    assert channel.has_ai_search is None


def test_channel_info_full() -> None:
    """Test ChannelInfo with all fields."""
    channel = ChannelInfo(
        id="MSNBC",
        label="MSNBC News",
        location="United States",
        startDate=20170801,
        endDate=99999999,
        hasSearch=True,
        hasAISearch=True,
    )
    assert channel.id == "MSNBC"
    assert channel.label == "MSNBC News"
    assert channel.location == "United States"
    assert channel.start_date == 20170801
    assert channel.end_date == 99999999
    assert channel.has_search is True
    assert channel.has_ai_search is True


def test_channel_info_is_active() -> None:
    """Test is_active property."""
    active_channel = ChannelInfo(
        id="CNN",
        label="CNN",
        startDate=20170801,
        endDate=99999999,
    )
    assert active_channel.is_active is True

    inactive_channel = ChannelInfo(
        id="OLD",
        label="Old Channel",
        startDate=20170801,
        endDate=20200101,
    )
    assert inactive_channel.is_active is False


def test_channel_info_date_parsing() -> None:
    """Test start_date_parsed property."""
    channel = ChannelInfo(
        id="CNN",
        label="CNN",
        startDate=20170801,
        endDate=99999999,
    )
    assert channel.start_date_parsed == date(2017, 8, 1)


def test_channel_info_date_parsing_invalid() -> None:
    """Test start_date_parsed with invalid date format."""
    channel = ChannelInfo(
        id="BAD",
        label="Bad Date",
        startDate=99999999,  # Invalid date format
        endDate=99999999,
    )
    assert channel.start_date_parsed is None


def test_channel_info_alias_parsing() -> None:
    """Test that field aliases work correctly."""
    # Using aliased names (as would come from API response)
    data = {
        "id": "FOXNEWS",
        "label": "Fox News",
        "location": "United States",
        "startDate": 20170801,
        "endDate": 99999999,
        "hasSearch": True,
        "hasAISearch": False,
    }
    channel = ChannelInfo.model_validate(data)
    assert channel.id == "FOXNEWS"
    assert channel.start_date == 20170801
    assert channel.end_date == 99999999
    assert channel.has_search is True
    assert channel.has_ai_search is False


# URL Building Tests


@pytest.mark.asyncio
async def test_build_url() -> None:
    """Test URL building for TVV endpoint."""
    endpoint = TVVEndpoint()
    url = await endpoint._build_url()
    assert url == "https://api.gdeltproject.org/api/v2/tvv/tvv"


# API Tests


@respx.mock
@pytest.mark.asyncio
async def test_get_inventory() -> None:
    """Test get_inventory method."""
    respx.get("https://api.gdeltproject.org/api/v2/tvv/tvv").mock(
        return_value=httpx.Response(
            200,
            json={
                "channels": [
                    {
                        "id": "CNN",
                        "label": "CNN",
                        "location": "United States",
                        "startDate": 20170801,
                        "endDate": 99999999,
                        "hasSearch": True,
                        "hasAISearch": True,
                    },
                    {
                        "id": "MSNBC",
                        "label": "MSNBC",
                        "location": "United States",
                        "startDate": 20170801,
                        "endDate": 99999999,
                        "hasSearch": True,
                        "hasAISearch": False,
                    },
                ],
            },
        ),
    )

    endpoint = TVVEndpoint()
    async with endpoint:
        channels = await endpoint.get_inventory()
        assert len(channels) == 2
        assert channels[0].id == "CNN"
        assert channels[0].label == "CNN"
        assert channels[0].location == "United States"
        assert channels[0].is_active is True
        assert channels[0].has_search is True
        assert channels[0].has_ai_search is True
        assert channels[1].id == "MSNBC"
        assert channels[1].has_ai_search is False


@respx.mock
@pytest.mark.asyncio
async def test_get_inventory_verifies_params() -> None:
    """Test that get_inventory sends correct parameters."""
    mock_route = respx.get("https://api.gdeltproject.org/api/v2/tvv/tvv").mock(
        return_value=httpx.Response(200, json={"channels": []}),
    )

    endpoint = TVVEndpoint()
    async with endpoint:
        await endpoint.get_inventory()

    assert mock_route.called
    request = mock_route.calls[0].request
    params = dict(request.url.params)
    assert params["mode"] == "chaninv"


@respx.mock
@pytest.mark.asyncio
async def test_empty_inventory() -> None:
    """Test handling empty channel list."""
    respx.get("https://api.gdeltproject.org/api/v2/tvv/tvv").mock(
        return_value=httpx.Response(200, json={"channels": []}),
    )

    endpoint = TVVEndpoint()
    async with endpoint:
        channels = await endpoint.get_inventory()
        assert channels == []


@respx.mock
@pytest.mark.asyncio
async def test_empty_response() -> None:
    """Test handling completely empty response."""
    respx.get("https://api.gdeltproject.org/api/v2/tvv/tvv").mock(
        return_value=httpx.Response(200, json={}),
    )

    endpoint = TVVEndpoint()
    async with endpoint:
        channels = await endpoint.get_inventory()
        assert channels == []


@respx.mock
@pytest.mark.asyncio
async def test_channel_with_missing_optional_fields() -> None:
    """Test handling channels with missing optional fields."""
    respx.get("https://api.gdeltproject.org/api/v2/tvv/tvv").mock(
        return_value=httpx.Response(
            200,
            json={
                "channels": [
                    {
                        "id": "NEWCHAN",
                        "label": "New Channel",
                        "startDate": 20240101,
                        "endDate": 99999999,
                        # Missing: location, hasSearch, hasAISearch
                    },
                ],
            },
        ),
    )

    endpoint = TVVEndpoint()
    async with endpoint:
        channels = await endpoint.get_inventory()
        assert len(channels) == 1
        assert channels[0].id == "NEWCHAN"
        assert channels[0].label == "New Channel"
        assert channels[0].location is None
        assert channels[0].has_search is None
        assert channels[0].has_ai_search is None


# Context Manager Tests


@pytest.mark.asyncio
async def test_context_manager_cleanup() -> None:
    """Test that context manager properly cleans up resources."""
    endpoint = TVVEndpoint()
    async with endpoint:
        assert endpoint._client is not None
        assert endpoint._owns_client is True


@pytest.mark.asyncio
async def test_shared_client() -> None:
    """Test using a shared HTTP client."""
    async with httpx.AsyncClient() as client:
        endpoint = TVVEndpoint(client=client)
        assert endpoint._client is client
        assert endpoint._owns_client is False

        await endpoint.close()
        assert client.is_closed is False
