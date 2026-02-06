"""Unit tests for data_lineage module."""
import pytest


@pytest.mark.unit
class TestDataLineageImports:
    """Test suite for data_lineage module imports."""

    def test_module_imports(self):
        """Verify module can be imported without errors."""
        from codomyrmex import data_lineage
        assert data_lineage is not None

    def test_public_api_exists(self):
        """Verify expected public API is available."""
        from codomyrmex.data_lineage import __all__
        expected_exports = [
            "NodeType",
            "EdgeType",
            "LineageNode",
            "LineageEdge",
            "DataAsset",
            "LineageGraph",
            "LineageTracker",
            "ImpactAnalyzer",
        ]
        for export in expected_exports:
            assert export in __all__, f"Missing export: {export}"


@pytest.mark.unit
class TestNodeType:
    """Test suite for NodeType enum."""

    def test_node_type_values(self):
        """Verify all node types are available."""
        from codomyrmex.data_lineage import NodeType

        assert NodeType.DATASET.value == "dataset"
        assert NodeType.TRANSFORMATION.value == "transformation"
        assert NodeType.MODEL.value == "model"
        assert NodeType.ARTIFACT.value == "artifact"
        assert NodeType.EXTERNAL.value == "external"


@pytest.mark.unit
class TestEdgeType:
    """Test suite for EdgeType enum."""

    def test_edge_type_values(self):
        """Verify all edge types are available."""
        from codomyrmex.data_lineage import EdgeType

        assert EdgeType.DERIVED_FROM.value == "derived_from"
        assert EdgeType.PRODUCED_BY.value == "produced_by"
        assert EdgeType.USED_BY.value == "used_by"
        assert EdgeType.INPUT_TO.value == "input_to"


@pytest.mark.unit
class TestLineageNode:
    """Test suite for LineageNode dataclass."""

    def test_node_creation(self):
        """Verify LineageNode can be created."""
        from codomyrmex.data_lineage import LineageNode, NodeType

        node = LineageNode(
            id="raw_data",
            name="Raw Customer Data",
            node_type=NodeType.DATASET,
        )

        assert node.id == "raw_data"
        assert node.name == "Raw Customer Data"
        assert node.node_type == NodeType.DATASET
        assert node.version == "1.0"

    def test_node_key_property(self):
        """Verify node key generation."""
        from codomyrmex.data_lineage import LineageNode, NodeType

        node = LineageNode(id="test", name="Test", node_type=NodeType.MODEL)
        assert node.key == "model:test"

    def test_node_to_dict(self):
        """Verify node serialization."""
        from codomyrmex.data_lineage import LineageNode, NodeType

        node = LineageNode(
            id="clean_data",
            name="Clean Data",
            node_type=NodeType.DATASET,
            metadata={"rows": 1000},
        )

        result = node.to_dict()
        assert result["id"] == "clean_data"
        assert result["type"] == "dataset"
        assert result["metadata"]["rows"] == 1000


@pytest.mark.unit
class TestLineageEdge:
    """Test suite for LineageEdge dataclass."""

    def test_edge_creation(self):
        """Verify LineageEdge can be created."""
        from codomyrmex.data_lineage import EdgeType, LineageEdge

        edge = LineageEdge(
            source_id="raw_data",
            target_id="clean_data",
            edge_type=EdgeType.DERIVED_FROM,
        )

        assert edge.source_id == "raw_data"
        assert edge.target_id == "clean_data"
        assert edge.edge_type == EdgeType.DERIVED_FROM

    def test_edge_key_property(self):
        """Verify edge key generation."""
        from codomyrmex.data_lineage import EdgeType, LineageEdge

        edge = LineageEdge(
            source_id="A",
            target_id="B",
            edge_type=EdgeType.INPUT_TO,
        )
        assert edge.key == "A->B:input_to"


@pytest.mark.unit
class TestDataAsset:
    """Test suite for DataAsset dataclass."""

    def test_data_asset_creation(self):
        """Verify DataAsset can be created."""
        from codomyrmex.data_lineage import DataAsset

        asset = DataAsset(
            id="customers",
            name="Customer Table",
            location="s3://bucket/customers.parquet",
            row_count=50000,
        )

        assert asset.id == "customers"
        assert asset.location == "s3://bucket/customers.parquet"
        assert asset.row_count == 50000

    def test_data_asset_compute_checksum(self):
        """Verify checksum computation."""
        from codomyrmex.data_lineage import DataAsset

        asset = DataAsset(id="test", name="Test", location="/tmp/test")
        checksum = asset.compute_checksum(b"test data")

        assert checksum is not None
        assert len(checksum) == 64  # SHA256 hex length


@pytest.mark.unit
class TestLineageGraph:
    """Test suite for LineageGraph."""

    def test_graph_add_node(self):
        """Verify nodes can be added to graph."""
        from codomyrmex.data_lineage import LineageGraph, LineageNode, NodeType

        graph = LineageGraph()
        node = LineageNode(id="data1", name="Data 1", node_type=NodeType.DATASET)

        graph.add_node(node)

        assert graph.node_count == 1
        assert graph.get_node("data1") is not None

    def test_graph_add_edge(self):
        """Verify edges can be added to graph."""
        from codomyrmex.data_lineage import (
            EdgeType,
            LineageEdge,
            LineageGraph,
            LineageNode,
            NodeType,
        )

        graph = LineageGraph()
        graph.add_node(LineageNode(id="A", name="A", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="B", name="B", node_type=NodeType.MODEL))
        graph.add_edge(LineageEdge(
            source_id="A",
            target_id="B",
            edge_type=EdgeType.INPUT_TO,
        ))

        assert graph.edge_count == 1

    def test_graph_get_upstream(self):
        """Verify upstream node retrieval."""
        from codomyrmex.data_lineage import (
            EdgeType,
            LineageEdge,
            LineageGraph,
            LineageNode,
            NodeType,
        )

        graph = LineageGraph()
        graph.add_node(LineageNode(id="raw", name="Raw", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="clean", name="Clean", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="model", name="Model", node_type=NodeType.MODEL))

        graph.add_edge(LineageEdge("raw", "clean", EdgeType.INPUT_TO))
        graph.add_edge(LineageEdge("clean", "model", EdgeType.INPUT_TO))

        upstream = graph.get_upstream("model")
        upstream_ids = [n.id for n in upstream]

        assert "clean" in upstream_ids
        assert "raw" in upstream_ids

    def test_graph_get_downstream(self):
        """Verify downstream node retrieval."""
        from codomyrmex.data_lineage import (
            EdgeType,
            LineageEdge,
            LineageGraph,
            LineageNode,
            NodeType,
        )

        graph = LineageGraph()
        graph.add_node(LineageNode(id="raw", name="Raw", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="clean", name="Clean", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="model", name="Model", node_type=NodeType.MODEL))

        graph.add_edge(LineageEdge("raw", "clean", EdgeType.INPUT_TO))
        graph.add_edge(LineageEdge("clean", "model", EdgeType.INPUT_TO))

        downstream = graph.get_downstream("raw")
        downstream_ids = [n.id for n in downstream]

        assert "clean" in downstream_ids
        assert "model" in downstream_ids

    def test_graph_get_path(self):
        """Verify path finding between nodes."""
        from codomyrmex.data_lineage import (
            EdgeType,
            LineageEdge,
            LineageGraph,
            LineageNode,
            NodeType,
        )

        graph = LineageGraph()
        graph.add_node(LineageNode(id="A", name="A", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="B", name="B", node_type=NodeType.TRANSFORMATION))
        graph.add_node(LineageNode(id="C", name="C", node_type=NodeType.MODEL))

        graph.add_edge(LineageEdge("A", "B", EdgeType.INPUT_TO))
        graph.add_edge(LineageEdge("B", "C", EdgeType.PRODUCED_BY))

        path = graph.get_path("A", "C")

        assert path == ["A", "B", "C"]

    def test_graph_to_dict(self):
        """Verify graph serialization."""
        from codomyrmex.data_lineage import (
            EdgeType,
            LineageEdge,
            LineageGraph,
            LineageNode,
            NodeType,
        )

        graph = LineageGraph()
        graph.add_node(LineageNode(id="test", name="Test", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="other", name="Other", node_type=NodeType.DATASET))
        graph.add_edge(LineageEdge("test", "other", EdgeType.DERIVED_FROM))

        result = graph.to_dict()
        assert "nodes" in result
        assert "edges" in result
        assert len(result["nodes"]) == 2
        assert len(result["edges"]) == 1


@pytest.mark.unit
class TestLineageTracker:
    """Test suite for LineageTracker."""

    def test_tracker_register_dataset(self):
        """Verify dataset registration."""
        from codomyrmex.data_lineage import LineageTracker, NodeType

        tracker = LineageTracker()
        node = tracker.register_dataset(
            id="customers",
            name="Customer Data",
            location="s3://bucket/customers",
        )

        assert node.id == "customers"
        assert node.node_type == NodeType.DATASET
        assert tracker.graph.get_node("customers") is not None

    def test_tracker_register_transformation(self):
        """Verify transformation registration with inputs and outputs."""
        from codomyrmex.data_lineage import LineageTracker, NodeType

        tracker = LineageTracker()
        tracker.register_dataset(id="raw", name="Raw", location="/raw")
        tracker.register_dataset(id="clean", name="Clean", location="/clean")

        transform = tracker.register_transformation(
            id="cleaning",
            name="Data Cleaning",
            inputs=["raw"],
            outputs=["clean"],
        )

        assert transform.node_type == NodeType.TRANSFORMATION
        assert tracker.graph.edge_count >= 2  # Input and output edges


@pytest.mark.unit
class TestImpactAnalyzer:
    """Test suite for ImpactAnalyzer."""

    def test_analyzer_analyze_change(self):
        """Verify impact analysis of changes."""
        from codomyrmex.data_lineage import (
            EdgeType,
            ImpactAnalyzer,
            LineageEdge,
            LineageGraph,
            LineageNode,
            NodeType,
        )

        graph = LineageGraph()
        graph.add_node(LineageNode(id="source", name="Source", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="transform", name="Transform", node_type=NodeType.TRANSFORMATION))
        graph.add_node(LineageNode(id="model", name="Model", node_type=NodeType.MODEL))

        graph.add_edge(LineageEdge("source", "transform", EdgeType.INPUT_TO))
        graph.add_edge(LineageEdge("transform", "model", EdgeType.PRODUCED_BY))

        analyzer = ImpactAnalyzer(graph)
        impact = analyzer.analyze_change("source")

        assert impact["total_affected"] >= 2
        assert "model" in impact["affected_models"]
        assert impact["risk_level"] == "high"
