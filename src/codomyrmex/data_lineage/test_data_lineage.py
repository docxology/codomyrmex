"""
Tests for Data Lineage Module
"""

import pytest
from codomyrmex.data_lineage import (
    NodeType,
    EdgeType,
    LineageNode,
    LineageEdge,
    DataAsset,
    LineageGraph,
    LineageTracker,
    ImpactAnalyzer,
)


class TestLineageNode:
    """Tests for LineageNode."""
    
    def test_create(self):
        """Should create node."""
        node = LineageNode(id="n1", name="Test", node_type=NodeType.DATASET)
        assert node.id == "n1"
        assert node.key == "dataset:n1"
    
    def test_to_dict(self):
        """Should convert to dict."""
        node = LineageNode(id="n1", name="Test", node_type=NodeType.MODEL)
        d = node.to_dict()
        assert d["type"] == "model"


class TestLineageEdge:
    """Tests for LineageEdge."""
    
    def test_create(self):
        """Should create edge."""
        edge = LineageEdge("a", "b", EdgeType.DERIVED_FROM)
        assert "a->b" in edge.key


class TestDataAsset:
    """Tests for DataAsset."""
    
    def test_compute_checksum(self):
        """Should compute checksum."""
        asset = DataAsset(id="d1", name="Test", location="/data")
        checksum = asset.compute_checksum(b"test data")
        
        assert len(checksum) == 64
        assert asset.checksum == checksum


class TestLineageGraph:
    """Tests for LineageGraph."""
    
    def test_add_node(self):
        """Should add node."""
        graph = LineageGraph()
        graph.add_node(LineageNode(id="n1", name="Test", node_type=NodeType.DATASET))
        
        assert graph.node_count == 1
    
    def test_add_edge(self):
        """Should add edge."""
        graph = LineageGraph()
        graph.add_node(LineageNode(id="a", name="A", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="b", name="B", node_type=NodeType.DATASET))
        graph.add_edge(LineageEdge("a", "b", EdgeType.DERIVED_FROM))
        
        assert graph.edge_count == 1
    
    def test_get_upstream(self):
        """Should get upstream nodes."""
        graph = LineageGraph()
        graph.add_node(LineageNode(id="raw", name="Raw", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="clean", name="Clean", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="final", name="Final", node_type=NodeType.DATASET))
        graph.add_edge(LineageEdge("raw", "clean", EdgeType.DERIVED_FROM))
        graph.add_edge(LineageEdge("clean", "final", EdgeType.DERIVED_FROM))
        
        upstream = graph.get_upstream("final")
        
        assert len(upstream) == 2
    
    def test_get_downstream(self):
        """Should get downstream nodes."""
        graph = LineageGraph()
        graph.add_node(LineageNode(id="source", name="Source", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="derived1", name="D1", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="derived2", name="D2", node_type=NodeType.DATASET))
        graph.add_edge(LineageEdge("source", "derived1", EdgeType.DERIVED_FROM))
        graph.add_edge(LineageEdge("source", "derived2", EdgeType.DERIVED_FROM))
        
        downstream = graph.get_downstream("source")
        
        assert len(downstream) == 2
    
    def test_get_path(self):
        """Should find path."""
        graph = LineageGraph()
        graph.add_node(LineageNode(id="a", name="A", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="b", name="B", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="c", name="C", node_type=NodeType.DATASET))
        graph.add_edge(LineageEdge("a", "b", EdgeType.DERIVED_FROM))
        graph.add_edge(LineageEdge("b", "c", EdgeType.DERIVED_FROM))
        
        path = graph.get_path("a", "c")
        
        assert path == ["a", "b", "c"]


class TestLineageTracker:
    """Tests for LineageTracker."""
    
    def test_register_dataset(self):
        """Should register dataset."""
        tracker = LineageTracker()
        node = tracker.register_dataset("d1", "Dataset 1", "/data/d1")
        
        assert node.node_type == NodeType.DATASET
        assert tracker.graph.node_count == 1
    
    def test_register_transformation(self):
        """Should register transformation."""
        tracker = LineageTracker()
        tracker.register_dataset("input", "Input", "/data/input")
        tracker.register_dataset("output", "Output", "/data/output")
        
        node = tracker.register_transformation(
            id="transform",
            name="Clean Data",
            inputs=["input"],
            outputs=["output"],
        )
        
        assert node.node_type == NodeType.TRANSFORMATION
        assert tracker.graph.edge_count == 2
    
    def test_get_origin(self):
        """Should get origin datasets."""
        tracker = LineageTracker()
        tracker.register_dataset("raw", "Raw", "")
        tracker.register_dataset("clean", "Clean", "")
        tracker.register_transformation("t1", "Transform", ["raw"], ["clean"])
        
        origins = tracker.get_origin("clean")
        
        assert len(origins) == 1
        assert origins[0].id == "raw"
    
    def test_get_impact(self):
        """Should get impacted nodes."""
        tracker = LineageTracker()
        tracker.register_dataset("source", "Source", "")
        tracker.register_dataset("output", "Output", "")
        tracker.register_transformation("t1", "Transform", ["source"], ["output"])
        
        impact = tracker.get_impact("source")
        
        assert len(impact) == 2  # transform + output


class TestImpactAnalyzer:
    """Tests for ImpactAnalyzer."""
    
    def test_analyze_change(self):
        """Should analyze impact."""
        graph = LineageGraph()
        graph.add_node(LineageNode(id="data", name="Data", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="model", name="Model", node_type=NodeType.MODEL))
        graph.add_edge(LineageEdge("data", "model", EdgeType.INPUT_TO))
        
        analyzer = ImpactAnalyzer(graph)
        impact = analyzer.analyze_change("data")
        
        assert impact["total_affected"] == 1
        assert "model" in impact["affected_models"]
        assert impact["risk_level"] == "high"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
