"""Parsers for GDELT data files.

This module provides parsers for converting raw GDELT data files into internal
dataclasses for further processing.

Available parsers:
- EventsParser: Parse GDELT Events v1 and v2 files (TAB-delimited)
- MentionsParser: Parse GDELT Mentions v2 files (TAB-delimited)
- GKGParser: Parse GDELT GKG (Global Knowledge Graph) v1 and v2.1 files (TAB-delimited)
- NGramsParser: Parse GDELT NGrams 3.0 files (newline-delimited JSON)
"""

from py_gdelt.parsers.events import EventsParser
from py_gdelt.parsers.gkg import GKGParser
from py_gdelt.parsers.mentions import MentionsParser
from py_gdelt.parsers.ngrams import NGramsParser


__all__ = [
    "EventsParser",
    "GKGParser",
    "MentionsParser",
    "NGramsParser",
]
