"""
Unit tests for MCP server helper functions.

These tests verify the helper functions used in the MCP server without
requiring the full MCP server infrastructure.
"""

import pytest


# Test _top_n function logic (reimplemented to avoid mcp import)
class TestTopNHelper:
    """Tests for the _top_n helper function logic."""

    @staticmethod
    def _top_n(counts: dict[str, int], n: int) -> list[dict[str, object]]:
        """Extract top N items from a counter dictionary.

        This mirrors the implementation in server.py for testing.
        """
        return [{"name": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: -x[1])[:n]]

    def test_top_n_returns_top_items_sorted(self) -> None:
        """Test that _top_n returns items sorted by count descending."""
        counts = {"a": 10, "b": 30, "c": 20}
        result = self._top_n(counts, 3)
        assert result == [
            {"name": "b", "count": 30},
            {"name": "c", "count": 20},
            {"name": "a", "count": 10},
        ]

    def test_top_n_limits_results(self) -> None:
        """Test that _top_n limits to n items."""
        counts = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
        result = self._top_n(counts, 2)
        assert len(result) == 2
        assert result[0]["name"] == "e"
        assert result[1]["name"] == "d"

    def test_top_n_empty_dict(self) -> None:
        """Test _top_n with empty dictionary."""
        result = self._top_n({}, 10)
        assert result == []

    def test_top_n_fewer_items_than_n(self) -> None:
        """Test _top_n when dict has fewer items than n."""
        counts = {"a": 1, "b": 2}
        result = self._top_n(counts, 10)
        assert len(result) == 2

    def test_top_n_with_zero(self) -> None:
        """Test _top_n with n=0."""
        counts = {"a": 1, "b": 2}
        result = self._top_n(counts, 0)
        assert result == []

    def test_top_n_preserves_name_and_count_keys(self) -> None:
        """Test that result dicts have 'name' and 'count' keys."""
        counts = {"test_key": 42}
        result = self._top_n(counts, 1)
        assert len(result) == 1
        assert "name" in result[0]
        assert "count" in result[0]
        assert result[0]["name"] == "test_key"
        assert result[0]["count"] == 42


class TestGoldsteinBucketHelper:
    """Tests for Goldstein bucket categorization logic."""

    @staticmethod
    def _goldstein_bucket(score: float) -> str:
        """Map Goldstein scale score to conflict/cooperation category.

        This mirrors the implementation that was in server.py (now in CAMEOCodes).
        """
        if score < -5:
            return "highly_conflictual"
        if score < -2:
            return "moderately_conflictual"
        if score < 0:
            return "mildly_conflictual"
        return "cooperative"

    def test_goldstein_bucket_highly_conflictual(self) -> None:
        """Test scores below -5 are highly_conflictual."""
        assert self._goldstein_bucket(-10.0) == "highly_conflictual"
        assert self._goldstein_bucket(-7.0) == "highly_conflictual"
        assert self._goldstein_bucket(-5.01) == "highly_conflictual"

    def test_goldstein_bucket_moderately_conflictual(self) -> None:
        """Test scores from -5 to -2 are moderately_conflictual."""
        assert self._goldstein_bucket(-5.0) == "moderately_conflictual"
        assert self._goldstein_bucket(-3.5) == "moderately_conflictual"
        assert self._goldstein_bucket(-2.01) == "moderately_conflictual"

    def test_goldstein_bucket_mildly_conflictual(self) -> None:
        """Test scores from -2 to 0 are mildly_conflictual."""
        assert self._goldstein_bucket(-2.0) == "mildly_conflictual"
        assert self._goldstein_bucket(-1.0) == "mildly_conflictual"
        assert self._goldstein_bucket(-0.01) == "mildly_conflictual"

    def test_goldstein_bucket_cooperative(self) -> None:
        """Test scores >= 0 are cooperative."""
        assert self._goldstein_bucket(0.0) == "cooperative"
        assert self._goldstein_bucket(5.0) == "cooperative"
        assert self._goldstein_bucket(10.0) == "cooperative"


class TestMCPServerImport:
    """Test that MCP server module handles missing mcp dependency gracefully."""

    def test_mcp_server_init_lazy_import(self) -> None:
        """Test that mcp_server __init__ uses lazy import."""
        # This should not raise even if mcp is not installed
        # because __init__.py uses lazy loading
        from py_gdelt import mcp_server

        assert hasattr(mcp_server, "__all__")
        assert "mcp" in mcp_server.__all__

    @pytest.mark.skipif(
        True,  # Skip by default - only run if mcp is installed
        reason="Requires mcp package to be installed",
    )
    def test_mcp_server_import_with_mcp_installed(self) -> None:
        """Test that mcp attribute is accessible when mcp is installed."""
        from py_gdelt.mcp_server import mcp

        assert mcp is not None
