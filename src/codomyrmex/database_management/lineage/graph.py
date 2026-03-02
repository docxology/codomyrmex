"""
Data Lineage Graph

Graph data structure for tracking data lineage relationships.
"""

import threading
from typing import Any

from .models import LineageEdge, LineageNode


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
            """dfs ."""
            if depth > max_depth or current_id in visited:
                return
            visited.add(current_id)
            for edge in self._edges:
                if edge.target_id == current_id:
                    source_node = self.get_node(edge.source_id)
                    if source_node and source_node.id not in visited:
                        result.append(source_node)
                        dfs(source_node.id, depth + 1)

        dfs(node_id, 0)
        return result

    def get_downstream(self, node_id: str, max_depth: int = 10) -> list[LineageNode]:
        """Get all downstream nodes (descendants)."""
        visited: set[str] = set()
        result = []

        def dfs(current_id: str, depth: int):
            """dfs ."""
            if depth > max_depth or current_id in visited:
                return
            visited.add(current_id)
            for edge in self._edges:
                if edge.source_id == current_id:
                    target_node = self.get_node(edge.target_id)
                    if target_node and target_node.id not in visited:
                        result.append(target_node)
                        dfs(target_node.id, depth + 1)

        dfs(node_id, 0)
        return result

    def get_path(self, source_id: str, target_id: str) -> list[str]:
        """Find path between two nodes."""
        visited: set[str] = set()

        def dfs(current: str, path: list[str]) -> list[str] | None:
            """dfs ."""
            if current == target_id:
                return path + [current]
            if current in visited:
                return None
            visited.add(current)
            for edge in self._edges:
                if edge.source_id == current:
                    result = dfs(edge.target_id, path + [current])
                    if result:
                        return result
            return None

        return dfs(source_id, []) or []

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
