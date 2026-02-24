"""
Data Lineage Tracker

High-level lineage tracking and impact analysis.
"""

from typing import Any

from .graph import LineageGraph
from .models import EdgeType, LineageEdge, LineageNode, NodeType


class LineageTracker:
    """
    Tracks data lineage through transformations.

    Usage:
        tracker = LineageTracker()
        tracker.register_dataset("raw_data", "Raw Data", location="/data/raw.csv")
        tracker.register_transformation(
            "transform_1", "Clean Data",
            inputs=["raw_data"], outputs=["clean_data"],
        )
    """

    def __init__(self, graph: LineageGraph | None = None):
        """Execute   Init   operations natively."""
        self.graph = graph or LineageGraph()
        self._current_transform: str | None = None

    def register_dataset(
        self,
        id: str,
        name: str,
        location: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> LineageNode:
        """Register a dataset."""
        node = LineageNode(
            id=id,
            name=name,
            node_type=NodeType.DATASET,
            metadata={"location": location, **(metadata or {})},
        )
        self.graph.add_node(node)
        return node

    def register_transformation(
        self,
        id: str,
        name: str,
        inputs: list[str],
        outputs: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> LineageNode:
        """Register a transformation with inputs and outputs."""
        transform_node = LineageNode(
            id=id,
            name=name,
            node_type=NodeType.TRANSFORMATION,
            metadata=metadata or {},
        )
        self.graph.add_node(transform_node)

        for input_id in inputs:
            self.graph.add_edge(LineageEdge(
                source_id=input_id,
                target_id=id,
                edge_type=EdgeType.INPUT_TO,
            ))

        for output_id in outputs:
            self.graph.add_edge(LineageEdge(
                source_id=id,
                target_id=output_id,
                edge_type=EdgeType.PRODUCED_BY,
            ))

        return transform_node

    def get_origin(self, node_id: str) -> list[LineageNode]:
        """Get the original source data for a node."""
        upstream = self.graph.get_upstream(node_id)
        return [n for n in upstream if n.node_type == NodeType.DATASET and not self.graph.get_upstream(n.id)]

    def get_impact(self, node_id: str) -> list[LineageNode]:
        """Get all nodes affected by changes to this node."""
        return self.graph.get_downstream(node_id)


class ImpactAnalyzer:
    """
    Analyzes impact of data changes.

    Usage:
        analyzer = ImpactAnalyzer(tracker.graph)
        impact = analyzer.analyze_change("raw_data")
        print(f"Affects {impact['total_affected']} nodes")
    """

    def __init__(self, graph: LineageGraph):
        """Execute   Init   operations natively."""
        self.graph = graph

    def analyze_change(self, node_id: str) -> dict[str, Any]:
        """Analyze impact of changing a node."""
        downstream = self.graph.get_downstream(node_id)

        affected_datasets = [n for n in downstream if n.node_type == NodeType.DATASET]
        affected_models = [n for n in downstream if n.node_type == NodeType.MODEL]
        affected_transforms = [n for n in downstream if n.node_type == NodeType.TRANSFORMATION]

        return {
            "source_node": node_id,
            "total_affected": len(downstream),
            "affected_datasets": [n.id for n in affected_datasets],
            "affected_models": [n.id for n in affected_models],
            "affected_transformations": [n.id for n in affected_transforms],
            "risk_level": "high" if affected_models else "medium" if affected_datasets else "low",
        }
