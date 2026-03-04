"""Tests for networks MCP tools.

Zero-mock tests that exercise the real networks MCP tool implementations.
"""

from __future__ import annotations


class TestNetworksAnalyze:
    """Tests for networks_analyze MCP tool."""

    def test_returns_success_for_simple_graph(self):
        from codomyrmex.networks.mcp_tools import networks_analyze

        result = networks_analyze(
            nodes=["a", "b", "c"],
            edges=[["a", "b"], ["b", "c"]],
        )
        assert result["status"] == "success"
        assert result["node_count"] == 3
        assert result["edge_count"] == 2

    def test_density_calculation(self):
        from codomyrmex.networks.mcp_tools import networks_analyze

        result = networks_analyze(
            nodes=["a", "b", "c"],
            edges=[["a", "b"], ["b", "c"], ["a", "c"]],
        )
        assert result["status"] == "success"
        assert result["density"] == 1.0  # Complete graph K3

    def test_connected_components(self):
        from codomyrmex.networks.mcp_tools import networks_analyze

        result = networks_analyze(
            nodes=["a", "b", "c", "d"],
            edges=[["a", "b"]],
        )
        assert result["status"] == "success"
        assert result["num_components"] == 3
        assert result["is_connected"] is False

    def test_degree_centrality_returned(self):
        from codomyrmex.networks.mcp_tools import networks_analyze

        result = networks_analyze(
            nodes=["a", "b"],
            edges=[["a", "b"]],
        )
        assert result["status"] == "success"
        assert "degree_centrality" in result
        assert result["degree_centrality"]["a"] == 1.0
        assert result["degree_centrality"]["b"] == 1.0

    def test_empty_graph(self):
        from codomyrmex.networks.mcp_tools import networks_analyze

        result = networks_analyze(nodes=[], edges=[])
        assert result["status"] == "success"
        assert result["node_count"] == 0
        assert result["edge_count"] == 0


class TestNetworksHasPath:
    """Tests for networks_has_path MCP tool."""

    def test_path_exists(self):
        from codomyrmex.networks.mcp_tools import networks_has_path

        result = networks_has_path(
            nodes=["a", "b", "c"],
            edges=[["a", "b"], ["b", "c"]],
            source="a",
            target="c",
        )
        assert result["status"] == "success"
        assert result["has_path"] is True

    def test_no_path(self):
        from codomyrmex.networks.mcp_tools import networks_has_path

        result = networks_has_path(
            nodes=["a", "b", "c"],
            edges=[["a", "b"]],
            source="a",
            target="c",
        )
        assert result["status"] == "success"
        assert result["has_path"] is False

    def test_missing_source_target_returns_error(self):
        from codomyrmex.networks.mcp_tools import networks_has_path

        result = networks_has_path(nodes=["a"], edges=[], source="", target="a")
        assert result["status"] == "error"


class TestNetworksToDict:
    """Tests for networks_to_dict MCP tool."""

    def test_serializes_network(self):
        from codomyrmex.networks.mcp_tools import networks_to_dict

        result = networks_to_dict(
            name="test_net",
            nodes=["x", "y"],
            edges=[["x", "y"]],
        )
        assert result["status"] == "success"
        assert result["network"]["name"] == "test_net"
        assert len(result["network"]["nodes"]) == 2
        assert len(result["network"]["edges"]) == 1

    def test_empty_network(self):
        from codomyrmex.networks.mcp_tools import networks_to_dict

        result = networks_to_dict(name="empty")
        assert result["status"] == "success"
        assert result["network"]["name"] == "empty"
        assert len(result["network"]["nodes"]) == 0
