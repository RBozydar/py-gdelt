"""GDELT REST API endpoints.

This package contains implementations for all GDELT REST API endpoints.
All endpoint classes inherit from BaseEndpoint and provide type-safe,
async interfaces to GDELT data sources.
"""

from py_gdelt.endpoints.base import BaseEndpoint
from py_gdelt.endpoints.context import (
    ContextEndpoint,
    ContextEntity,
    ContextResult,
    ContextTheme,
    ContextTone,
)
from py_gdelt.endpoints.doc import DocEndpoint
from py_gdelt.endpoints.events import EventsEndpoint
from py_gdelt.endpoints.geo import GeoEndpoint, GeoPoint, GeoResult
from py_gdelt.endpoints.gkg import GKGEndpoint
from py_gdelt.endpoints.mentions import MentionsEndpoint
from py_gdelt.endpoints.ngrams import NGramsEndpoint
from py_gdelt.endpoints.tv import (
    TVAIEndpoint,
    TVClip,
    TVEndpoint,
    TVStationChart,
    TVStationData,
    TVTimeline,
    TVTimelinePoint,
)


__all__ = [
    "BaseEndpoint",
    "ContextEndpoint",
    "ContextEntity",
    "ContextResult",
    "ContextTheme",
    "ContextTone",
    "DocEndpoint",
    "EventsEndpoint",
    "GKGEndpoint",
    "GeoEndpoint",
    "GeoPoint",
    "GeoResult",
    "MentionsEndpoint",
    "NGramsEndpoint",
    "TVAIEndpoint",
    "TVClip",
    "TVEndpoint",
    "TVStationChart",
    "TVStationData",
    "TVTimeline",
    "TVTimelinePoint",
]
