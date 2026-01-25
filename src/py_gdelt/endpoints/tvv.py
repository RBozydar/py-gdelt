"""TV Visual (TVV) API endpoint for channel inventory metadata.

This module provides the TVVEndpoint for accessing TV Visual Explorer
channel inventory information. The API returns metadata about available
TV channels including their IDs, locations, coverage dates, and search
capability flags.

Example:
    Get all available channels:

        async with TVVEndpoint() as tvv:
            channels = await tvv.get_inventory()
            for ch in channels:
                print(f"{ch.id}: {ch.label} ({ch.location})")

    Filter to active channels with search capability:

        async with TVVEndpoint() as tvv:
            channels = await tvv.get_inventory()
            active = [ch for ch in channels if ch.is_active and ch.has_search]
            print(f"Found {len(active)} active searchable channels")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from py_gdelt.endpoints.base import BaseEndpoint
from py_gdelt.utils.dates import parse_gdelt_date


__all__ = [
    "ChannelInfo",
    "TVVEndpoint",
]


class ChannelInfo(BaseModel):
    """Information about a TV channel in the GDELT Visual Explorer.

    Attributes:
        id: Channel identifier (e.g., "CNN", "MSNBC").
        label: Human-readable display name.
        location: Geographic location (e.g., "United States").
        start_date: Coverage start date (YYYYMMDD integer format).
        end_date: Coverage end date (99999999 means ongoing).
        has_search: Whether channel is available in TV Explorer.
        has_ai_search: Whether channel is available in TV AI Explorer.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    label: str
    location: str | None = None
    start_date: int = Field(alias="startDate")
    end_date: int = Field(alias="endDate")
    has_search: bool | None = Field(default=None, alias="hasSearch")
    has_ai_search: bool | None = Field(default=None, alias="hasAISearch")

    @property
    def is_active(self) -> bool:
        """Whether the channel is currently active (end_date is 99999999)."""
        return self.end_date == 99999999

    @property
    def start_date_parsed(self) -> date | None:
        """Parse start_date integer to date object.

        Returns:
            Date object, or None if parsing fails (e.g., invalid dates like 99999999).
        """
        try:
            return parse_gdelt_date(str(self.start_date))
        except ValueError:
            return None


class TVVEndpoint(BaseEndpoint):
    """Endpoint for TV Visual Explorer channel inventory.

    Provides metadata about available TV channels including their IDs,
    locations, coverage dates, and search capability flags.

    Attributes:
        BASE_URL: API endpoint URL.

    Example:
        async with TVVEndpoint() as tvv:
            channels = await tvv.get_inventory()
            active = [ch for ch in channels if ch.is_active]
            print(f"Found {len(active)} active channels")
    """

    BASE_URL: str = "https://api.gdeltproject.org/api/v2/tvv/tvv"

    async def _build_url(self, **kwargs: Any) -> str:
        """Build the request URL.

        Args:
            **kwargs: Unused, required by BaseEndpoint interface.

        Returns:
            The base TVV API URL.
        """
        return self.BASE_URL

    async def get_inventory(self) -> list[ChannelInfo]:
        """Get the complete channel inventory.

        Returns:
            List of ChannelInfo objects for all available channels.

        Raises:
            APIError: If the API request fails.
            RateLimitError: If rate limit is exceeded.
            APIUnavailableError: If the API is temporarily unavailable.

        Example:
            channels = await tvv.get_inventory()
            for ch in channels:
                if ch.is_active and ch.has_search:
                    print(f"{ch.id}: {ch.label}")
        """
        url = await self._build_url()
        data = await self._get_json(url, params={"mode": "chaninv"})

        return [ChannelInfo.model_validate(item) for item in data.get("channels", [])]
