"""Tests for edge_computing MCP tools.

Zero-mock policy: all tests exercise real implementations.
"""

from __future__ import annotations


class TestEdgeComputingClusterHealth:
    """Tests for edge_computing_cluster_health tool."""

    def test_cluster_health_empty_cluster(self):
        from codomyrmex.edge_computing.mcp_tools import edge_computing_cluster_health

        result = edge_computing_cluster_health()
        assert result["status"] == "success"
        assert result["total_nodes"] == 0
        assert result["online"] == 0
        assert result["total_functions"] == 0

    def test_cluster_health_has_required_keys(self):
        from codomyrmex.edge_computing.mcp_tools import edge_computing_cluster_health

        result = edge_computing_cluster_health()
        assert result["status"] == "success"
        for key in (
            "total_nodes",
            "online",
            "draining",
            "total_functions",
            "total_invocations",
        ):
            assert key in result


class TestEdgeComputingListCapabilities:
    """Tests for edge_computing_list_capabilities tool."""

    def test_list_capabilities_returns_statuses(self):
        from codomyrmex.edge_computing.mcp_tools import edge_computing_list_capabilities

        result = edge_computing_list_capabilities()
        assert result["status"] == "success"
        assert "online" in result["node_statuses"]
        assert "offline" in result["node_statuses"]

    def test_list_capabilities_has_strategies(self):
        from codomyrmex.edge_computing.mcp_tools import edge_computing_list_capabilities

        result = edge_computing_list_capabilities()
        assert result["status"] == "success"
        assert len(result["deployment_strategies"]) > 0
        assert len(result["schedule_types"]) > 0


class TestEdgeComputingHealthCheck:
    """Tests for edge_computing_health_check tool."""

    def test_health_check_default_timeout(self):
        from codomyrmex.edge_computing.mcp_tools import edge_computing_health_check

        result = edge_computing_health_check()
        assert result["status"] == "success"
        assert result["timeout_seconds"] == 60.0
        assert result["monitored_nodes"] == 0

    def test_health_check_custom_timeout(self):
        from codomyrmex.edge_computing.mcp_tools import edge_computing_health_check

        result = edge_computing_health_check(heartbeat_timeout_seconds=30.0)
        assert result["status"] == "success"
        assert result["timeout_seconds"] == 30.0

    def test_health_check_has_total_checks(self):
        from codomyrmex.edge_computing.mcp_tools import edge_computing_health_check

        result = edge_computing_health_check()
        assert result["status"] == "success"
        assert "total_checks" in result
        assert result["total_checks"] == 0
