"""GDELT MCP Server for geopolitical research agents.

This module provides a FastMCP server exposing GDELT data through specialized tools
for AI agents conducting geopolitical analysis, conflict monitoring, and news research.

All tools use streaming aggregation with O(1) memory consumption.
"""

from typing import Any


__all__ = ["mcp"]


# Lazy import to avoid requiring mcp dependency for library users
def __getattr__(name: str) -> Any:
    """Lazy import of MCP server components."""
    if name == "mcp":
        from py_gdelt.mcp_server.server import mcp  # noqa: PLC0415

        return mcp
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
