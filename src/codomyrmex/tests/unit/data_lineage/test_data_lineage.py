"""Unit tests for the improved data_lineage module."""
import pytest

from codomyrmex.data_lineage import (
    DataLineage,
    EdgeType,
    ImpactAnalyzer,
    LineageEdge,
    LineageGraph,
    LineageNode,
    LineageTracker,
    NodeType,
)


@pytest.mark.unit
class TestLineageGraph:
    """Test suite for LineageGraph with real execution (zero-mock)."""

    def test_graph_add_node_and_get(self):
        graph = LineageGraph()
        node = LineageNode(id="test_node", name="Test Node", node_type=NodeType.DATASET)
        graph.add_node(node)

        assert graph.get_node("test_node") == node
        assert graph.node_count == 1

    def test_graph_add_edge_validation(self):
        graph = LineageGraph()
        edge = LineageEdge(source_id="A", target_id="B", edge_type=EdgeType.INPUT_TO)

        # Should raise error because nodes A and B don't exist
        with pytest.raises(ValueError, match="Source node 'A' does not exist"):
            graph.add_edge(edge)

        graph.add_node(LineageNode(id="A", name="A", node_type=NodeType.DATASET))
        with pytest.raises(ValueError, match="Target node 'B' does not exist"):
            graph.add_edge(edge)

        graph.add_node(LineageNode(id="B", name="B", node_type=NodeType.TRANSFORMATION))
        graph.add_edge(edge)
        assert graph.edge_count == 1

    def test_graph_traversal_upstream(self):
        graph = LineageGraph()
        graph.add_node(LineageNode(id="A", name="A", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="B", name="B", node_type=NodeType.TRANSFORMATION))
        graph.add_node(LineageNode(id="C", name="C", node_type=NodeType.DATASET))

        graph.add_edge(LineageEdge("A", "B", EdgeType.INPUT_TO))
        graph.add_edge(LineageEdge("B", "C", EdgeType.PRODUCED_BY))

        upstream = graph.get_upstream("C")
        upstream_ids = {n.id for n in upstream}
        assert "A" in upstream_ids
        assert "B" in upstream_ids
        assert len(upstream) == 2

    def test_graph_traversal_downstream(self):
        graph = LineageGraph()
        graph.add_node(LineageNode(id="A", name="A", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="B", name="B", node_type=NodeType.TRANSFORMATION))
        graph.add_node(LineageNode(id="C", name="C", node_type=NodeType.MODEL))

        graph.add_edge(LineageEdge("A", "B", EdgeType.INPUT_TO))
        graph.add_edge(LineageEdge("B", "C", EdgeType.PRODUCED_BY))

        downstream = graph.get_downstream("A")
        downstream_ids = {n.id for n in downstream}
        assert "B" in downstream_ids
        assert "C" in downstream_ids
        assert len(downstream) == 2

    def test_cycle_detection(self):
        graph = LineageGraph()
        graph.add_node(LineageNode(id="A", name="A", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="B", name="B", node_type=NodeType.TRANSFORMATION))
        graph.add_node(LineageNode(id="C", name="C", node_type=NodeType.TRANSFORMATION))

        graph.add_edge(LineageEdge("A", "B", EdgeType.INPUT_TO))
        graph.add_edge(LineageEdge("B", "C", EdgeType.INPUT_TO))
        graph.add_edge(LineageEdge("C", "A", EdgeType.INPUT_TO)) # Cycle A->B->C->A

        cycles = graph.validate_graph()
        assert len(cycles) > 0
        assert "A" in cycles or "B" in cycles or "C" in cycles

    def test_leaf_nodes(self):
        graph = LineageGraph()
        graph.add_node(LineageNode(id="A", name="A", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="B", name="B", node_type=NodeType.TRANSFORMATION))
        graph.add_node(LineageNode(id="C", name="C", node_type=NodeType.MODEL))

        graph.add_edge(LineageEdge("A", "B", EdgeType.INPUT_TO))
        graph.add_edge(LineageEdge("B", "C", EdgeType.PRODUCED_BY))

        leaves = graph.get_leaf_nodes()
        assert len(leaves) == 1
        assert leaves[0].id == "C"

    def test_dot_export(self):
        graph = LineageGraph()
        graph.add_node(LineageNode(id="A", name="Source A", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="B", name="Model B", node_type=NodeType.MODEL))
        graph.add_edge(LineageEdge("A", "B", EdgeType.INPUT_TO))

        dot = graph.export_to_dot()
        assert "digraph G {" in dot
        assert '"A"' in dot
        assert '"B"' in dot
        assert "Source A" in dot
        assert "Model B" in dot
        assert "->" in dot


@pytest.mark.unit
class TestLineageTracker:
    """Test suite for LineageTracker."""

    def test_register_transformation_auto_outputs(self):
        tracker = LineageTracker()
        tracker.register_dataset(id="input_1", name="Input 1")

        # output_1 is not registered yet
        tracker.register_transformation(
            id="job_1",
            name="Job 1",
            inputs=["input_1"],
            outputs=["output_1"]
        )

        assert tracker.graph.get_node("output_1") is not None
        assert tracker.graph.get_node("output_1").node_type == NodeType.DATASET

    def test_get_origin(self):
        tracker = LineageTracker()
        tracker.register_dataset(id="root1", name="Root 1")
        tracker.register_dataset(id="root2", name="Root 2")
        tracker.register_transformation(id="T1", name="T1", inputs=["root1", "root2"], outputs=["mid"])
        tracker.register_transformation(id="T2", name="T2", inputs=["mid"], outputs=["leaf"])

        origins = tracker.get_origin("leaf")
        origin_ids = {n.id for n in origins}
        assert origin_ids == {"root1", "root2"}


@pytest.mark.unit
class TestImpactAnalyzer:
    """Test suite for ImpactAnalyzer."""

    def test_analyze_change_comprehensive(self):
        graph = LineageGraph()
        graph.add_node(LineageNode(id="S1", name="S1", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="T1", name="T1", node_type=NodeType.TRANSFORMATION))
        graph.add_node(LineageNode(id="D1", name="D1", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="M1", name="M1", node_type=NodeType.MODEL))
        graph.add_node(LineageNode(id="DB1", name="DB1", node_type=NodeType.DASHBOARD))

        graph.add_edge(LineageEdge("S1", "T1", EdgeType.INPUT_TO))
        graph.add_edge(LineageEdge("T1", "D1", EdgeType.PRODUCED_BY))
        graph.add_edge(LineageEdge("D1", "M1", EdgeType.INPUT_TO))
        graph.add_edge(LineageEdge("D1", "DB1", EdgeType.USED_BY))

        analyzer = ImpactAnalyzer(graph)
        impact = analyzer.analyze_change("S1")

        assert impact["total_affected"] == 4
        assert "M1" in impact["affected_models"]
        assert "DB1" in impact["affected_dashboards"]
        assert impact["risk_level"] == "high"
        assert impact["impact_paths"]["M1"] == ["S1", "T1", "D1", "M1"]


@pytest.mark.unit
class TestDataLineageOrchestrator:
    """Test suite for the DataLineage orchestrator class."""

    def test_data_lineage_flow(self):
        dl = DataLineage()
        dl.track("dataset", id="raw", name="Raw Data")
        dl.track("transformation", id="clean_job", name="Clean Job", inputs=["raw"], outputs=["clean"])

        impact = dl.analyze("raw")
        assert "clean" in impact["affected_datasets"]
        assert impact["total_affected"] == 2
