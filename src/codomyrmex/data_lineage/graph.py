"""
Data Lineage Graph

Graph data structure for tracking data lineage relationships.
"""

import threading
from typing import Any

from .models import LineageEdge, LineageNode, NodeType


class LineageGraph:
    """
    Graph of data lineage relationships.

    Usage:
        graph = LineageGraph()
        graph.add_node(LineageNode(id="raw_data", name="Raw Data", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="model", name="ML Model", node_type=NodeType.MODEL))
        graph.add_edge(LineageEdge("raw_data", "model", EdgeType.INPUT_TO))
        upstream = graph.get_upstream("model")
    """

    def __init__(self):
        self._nodes: dict[str, LineageNode] = {}
        self._edges: list[LineageEdge] = []
        self._lock = threading.Lock()

    def add_node(self, node: LineageNode) -> None:
        """Add a node to the graph."""
        with self._lock:
            self._nodes[node.id] = node

    def get_node(self, node_id: str) -> LineageNode | None:
        """Get a node by ID."""
        return self._nodes.get(node_id)

    def add_edge(self, edge: LineageEdge) -> None:
        """Add an edge to the graph."""
        if edge.source_id not in self._nodes:
            raise ValueError(f"Source node '{edge.source_id}' does not exist in graph.")
        if edge.target_id not in self._nodes:
            raise ValueError(f"Target node '{edge.target_id}' does not exist in graph.")
        with self._lock:
            self._edges.append(edge)

    def get_edges(
        self,
        source_id: str | None = None,
        target_id: str | None = None,
    ) -> list[LineageEdge]:
        """Get edges matching criteria."""
        results = []
        for edge in self._edges:
            if source_id and edge.source_id != source_id:
                continue
            if target_id and edge.target_id != target_id:
                continue
            results.append(edge)
        return results

    def get_upstream(self, node_id: str, max_depth: int = 10) -> list[LineageNode]:
        """Get all upstream nodes (ancestors)."""
        visited: set[str] = set()
        result = []

        def dfs(current_id: str, depth: int):
            """Dfs."""
            if depth > max_depth or current_id in visited:
                return
            visited.add(current_id)
            for edge in self._edges:
                if edge.target_id == current_id:
                    source_node = self.get_node(edge.source_id)
                    if source_node:
                        if source_node.id not in visited:
                            result.append(source_node)
                        dfs(source_node.id, depth + 1)

        dfs(node_id, 0)
        return result

    def get_downstream(self, node_id: str, max_depth: int = 10) -> list[LineageNode]:
        """Get all downstream nodes (descendants)."""
        visited: set[str] = set()
        result = []

        def dfs(current_id: str, depth: int):
            """Dfs."""
            if depth > max_depth or current_id in visited:
                return
            visited.add(current_id)
            for edge in self._edges:
                if edge.source_id == current_id:
                    target_node = self.get_node(edge.target_id)
                    if target_node:
                        if target_node.id not in visited:
                            result.append(target_node)
                        dfs(target_node.id, depth + 1)

        dfs(node_id, 0)
        return result

    def get_path(self, source_id: str, target_id: str) -> list[str]:
        """Find path between two nodes."""
        visited: set[str] = set()

        def dfs(current: str, path: list[str]) -> list[str] | None:
            """Dfs."""
            if current == target_id:
                return [*path, current]
            if current in visited:
                return None
            visited.add(current)
            for edge in self._edges:
                if edge.source_id == current:
                    result = dfs(edge.target_id, [*path, current])
                    if result:
                        return result
            return None

        return dfs(source_id, []) or []

    def validate_graph(self) -> list[str]:
        """Check for cycles in the graph. Returns list of nodes in cycles."""
        cycles = []
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for edge in self.get_edges(source_id=node_id):
                neighbor = edge.target_id
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in self._nodes:
            if node_id not in visited and has_cycle(node_id):
                cycles.append(node_id)

        return cycles

    def get_leaf_nodes(self) -> list[LineageNode]:
        """Get nodes with no downstream edges."""
        source_ids = {edge.source_id for edge in self._edges}
        return [
            node for node_id, node in self._nodes.items() if node_id not in source_ids
        ]

    def export_to_dot(self) -> str:
        """Export graph to DOT format for visualization."""
        dot = ["digraph G {"]
        dot.append("  node [shape=box];")

        # Add nodes
        for node_id, node in self._nodes.items():
            color = "lightblue"
            if node.node_type == NodeType.TRANSFORMATION:
                color = "lightgrey"
            elif node.node_type == NodeType.MODEL:
                color = "lightgreen"
            dot.append(
                f'  "{node_id}" [label="{node.name}\\n({node.node_type.value})", style=filled, fillcolor={color}];'
            )

        # Add edges
        for edge in self._edges:
            dot.append(
                f'  "{edge.source_id}" -> "{edge.target_id}" [label="{edge.edge_type.value}"];'
            )

        dot.append("}")
        return "\n".join(dot)

    @property
    def node_count(self) -> int:
        """Get number of nodes."""
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        """Get number of edges."""
        return len(self._edges)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges],
        }
