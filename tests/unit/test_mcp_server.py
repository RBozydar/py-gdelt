"""
Unit tests for MCP server helper functions.

These tests verify the helper functions used in the MCP server.
"""

import pytest


# Check if mcp is available
try:
    import mcp  # noqa: F401

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestTopNHelper:
    """Tests for the _top_n helper function from server.py."""

    def test_top_n_returns_top_items_sorted(self) -> None:
        """Test that _top_n returns items sorted by count descending."""
        from py_gdelt.mcp_server.server import _top_n

        counts = {"a": 10, "b": 30, "c": 20}
        result = _top_n(counts, 3)
        assert result == [
            {"name": "b", "count": 30},
            {"name": "c", "count": 20},
            {"name": "a", "count": 10},
        ]

    def test_top_n_limits_results(self) -> None:
        """Test that _top_n limits to n items."""
        from py_gdelt.mcp_server.server import _top_n

        counts = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
        result = _top_n(counts, 2)
        assert len(result) == 2
        assert result[0]["name"] == "e"
        assert result[1]["name"] == "d"

    def test_top_n_empty_dict(self) -> None:
        """Test _top_n with empty dictionary."""
        from py_gdelt.mcp_server.server import _top_n

        result = _top_n({}, 10)
        assert result == []

    def test_top_n_fewer_items_than_n(self) -> None:
        """Test _top_n when dict has fewer items than n."""
        from py_gdelt.mcp_server.server import _top_n

        counts = {"a": 1, "b": 2}
        result = _top_n(counts, 10)
        assert len(result) == 2

    def test_top_n_with_zero(self) -> None:
        """Test _top_n with n=0."""
        from py_gdelt.mcp_server.server import _top_n

        counts = {"a": 1, "b": 2}
        result = _top_n(counts, 0)
        assert result == []

    def test_top_n_preserves_name_and_count_keys(self) -> None:
        """Test that result dicts have 'name' and 'count' keys."""
        from py_gdelt.mcp_server.server import _top_n

        counts = {"test_key": 42}
        result = _top_n(counts, 1)
        assert len(result) == 1
        assert "name" in result[0]
        assert "count" in result[0]
        assert result[0]["name"] == "test_key"
        assert result[0]["count"] == 42


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestMCPServerFunctions:
    """Tests for MCP server utility functions."""

    def test_get_cameo_codes_returns_singleton(self) -> None:
        """Test that get_cameo_codes returns a CAMEOCodes instance."""
        from py_gdelt.mcp_server.server import get_cameo_codes

        cameo = get_cameo_codes()
        assert cameo is not None
        # Should return same instance on second call
        cameo2 = get_cameo_codes()
        assert cameo is cameo2

    def test_cameo_codes_has_goldstein_category(self) -> None:
        """Test that CAMEOCodes has get_goldstein_category method."""
        from py_gdelt.mcp_server.server import get_cameo_codes

        cameo = get_cameo_codes()
        assert hasattr(cameo, "get_goldstein_category")
        assert cameo.get_goldstein_category(-7.0) == "highly_conflictual"
        assert cameo.get_goldstein_category(-3.0) == "moderately_conflictual"
        assert cameo.get_goldstein_category(-1.0) == "mildly_conflictual"
        assert cameo.get_goldstein_category(5.0) == "cooperative"


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestMCPServerImport:
    """Test MCP server module imports."""

    def test_mcp_server_init_exports(self) -> None:
        """Test that mcp_server __init__ has correct exports."""
        from py_gdelt import mcp_server

        assert hasattr(mcp_server, "__all__")
        assert "mcp" in mcp_server.__all__

    def test_mcp_server_import_mcp(self) -> None:
        """Test that mcp FastMCP instance is accessible."""
        from py_gdelt.mcp_server import mcp

        assert mcp is not None
        assert mcp.name == "GDELT Research Server"

    def test_server_has_tools(self) -> None:
        """Test that server module has tool functions defined."""
        from py_gdelt.mcp_server import server

        # Check that tool functions exist
        assert hasattr(server, "gdelt_events")
        assert hasattr(server, "gdelt_gkg")
        assert hasattr(server, "gdelt_actors")
        assert hasattr(server, "gdelt_trends")
        assert hasattr(server, "gdelt_doc")
        assert hasattr(server, "gdelt_cameo_lookup")
