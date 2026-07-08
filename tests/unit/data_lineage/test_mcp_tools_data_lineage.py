"""Tests for data_lineage MCP tools.

Zero-mock policy: all tests exercise real implementations.
"""

from __future__ import annotations


class TestDataLineageTrack:
    """Tests for data_lineage_track tool."""

    def test_track_dataset_returns_success(self):
        from codomyrmex.data_lineage.mcp_tools import data_lineage_track

        result = data_lineage_track(
            event_type="dataset",
            node_id="test_ds_1",
            name="Test Dataset",
            location="/data/test.csv",
        )
        assert result["status"] == "success"
        assert result["node_id"] == "test_ds_1"
        assert result["node_type"] == "dataset"

    def test_track_transformation_returns_success(self):
        from codomyrmex.data_lineage.mcp_tools import data_lineage_track

        result = data_lineage_track(
            event_type="transformation",
            node_id="transform_1",
            name="Clean Data",
            inputs=[],
            outputs=[],
        )
        assert result["status"] == "success"
        assert result["node_id"] == "transform_1"
        assert result["node_type"] == "transformation"

    def test_track_invalid_event_type_returns_error(self):
        from codomyrmex.data_lineage.mcp_tools import data_lineage_track

        result = data_lineage_track(
            event_type="unknown",
            node_id="x",
            name="X",
        )
        assert result["status"] == "error"
        assert "unknown" in result["message"].lower()


class TestDataLineageAnalyzeImpact:
    """Tests for data_lineage_analyze_impact tool."""

    def test_analyze_impact_returns_success(self):
        from codomyrmex.data_lineage.mcp_tools import data_lineage_analyze_impact

        result = data_lineage_analyze_impact(node_id="source_node")
        assert result["status"] == "success"
        assert result["source_node"] == "source_node"
        assert "total_affected" in result
        assert "risk_level" in result

    def test_analyze_impact_zero_affected(self):
        from codomyrmex.data_lineage.mcp_tools import data_lineage_analyze_impact

        result = data_lineage_analyze_impact(node_id="isolated_node")
        assert result["status"] == "success"
        assert result["total_affected"] == 0
        assert result["risk_level"] == "low"


class TestDataLineageValidateGraph:
    """Tests for data_lineage_validate_graph tool."""

    def test_validate_empty_graph(self):
        from codomyrmex.data_lineage.mcp_tools import data_lineage_validate_graph

        result = data_lineage_validate_graph()
        assert result["status"] == "success"
        assert result["node_count"] == 0
        assert result["edge_count"] == 0
        assert result["has_cycles"] is False

    def test_validate_graph_returns_leaf_count(self):
        from codomyrmex.data_lineage.mcp_tools import data_lineage_validate_graph

        result = data_lineage_validate_graph()
        assert result["status"] == "success"
        assert "leaf_node_count" in result
