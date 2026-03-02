"""Graph data structures and algorithms.

This module provides the core graph data structures for network analysis.
"""

import heapq
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from codomyrmex.model_context_protocol.decorators import mcp_tool

T = TypeVar("T")


@dataclass(frozen=True)
class Node(Generic[T]):
    """Represents a node in the graph."""
    id: str
    data: T | None = None

    def __hash__(self):
        """Return the hash value."""
        return hash(self.id)

    def __eq__(self, other):
        """Return True if equal to other."""
        if not isinstance(other, Node):
            return False
        return self.id == other.id


@dataclass(frozen=True)
class Edge:
    """Represents an edge between two nodes."""
    source: Node
    target: Node
    weight: float = 1.0
    data: dict[str, Any] = field(default_factory=dict)


class NetworkGraph(Generic[T]):
    """Represents a network graph."""

    def __init__(self):
        """Initialize an empty graph."""
        self._nodes: dict[str, Node[T]] = {}
        self._adj: dict[str, list[Edge]] = {}

    def add_node(self, node_id: str, data: T | None = None) -> Node[T]:
        """Add a node to the graph.

        Args:
            node_id: Unique identifier for the node.
            data: Optional data associated with the node.

        Returns:
            The created or existing node.
        """
        if node_id not in self._nodes:
            node = Node(id=node_id, data=data)
            self._nodes[node_id] = node
            self._adj[node_id] = []
        return self._nodes[node_id]

    def add_edge(self, source_id: str, target_id: str, weight: float = 1.0, **kwargs) -> Edge:
        """Add an edge between two nodes.

        If nodes do not exist, they are created.

        Args:
            source_id: ID of the source node.
            target_id: ID of the target node.
            weight: Weight of the edge.
            **kwargs: Additional data for the edge.

        Returns:
            The created edge.
        """
        source = self.add_node(source_id)
        target = self.add_node(target_id)

        edge = Edge(source=source, target=target, weight=weight, data=kwargs)
        self._adj[source_id].append(edge)
        return edge

    def get_neighbors(self, node_id: str) -> list[Node[T]]:
        """Get neighbors of a node.

        Args:
            node_id: ID of the node.

        Returns:
            List of neighboring nodes.
        """
        if node_id not in self._adj:
            return []
        return [edge.target for edge in self._adj[node_id]]

    @mcp_tool(name="NetworkGraph.shortest_path", description="Find the shortest path between two nodes using Dijkstra's algorithm")
    def shortest_path(self, start_id: str, end_id: str) -> list[Node[T]] | None:
        """Find the shortest path between two nodes using Dijkstra's algorithm.

        Args:
            start_id: ID of the start node.
            end_id: ID of the end node.

        Returns:
            List of nodes representing the path, or None if no path exists.
        """
        if start_id not in self._nodes or end_id not in self._nodes:
            return None

        # Priority queue: (distance, node_id)
        queue = [(0.0, start_id)]
        distances = {node_id: float('inf') for node_id in self._nodes}
        distances[start_id] = 0.0
        previous = dict.fromkeys(self._nodes)

        while queue:
            current_dist, current_id = heapq.heappop(queue)

            if current_id == end_id:
                break

            if current_dist > distances[current_id]:
                continue

            for edge in self._adj[current_id]:
                neighbor_id = edge.target.id
                new_dist = current_dist + edge.weight

                if new_dist < distances[neighbor_id]:
                    distances[neighbor_id] = new_dist
                    previous[neighbor_id] = current_id
                    heapq.heappush(queue, (new_dist, neighbor_id))

        # Reconstruct path
        path = []
        current = end_id
        while current is not None:
            path.append(self._nodes[current])
            current = previous[current]

        if path[-1].id != start_id:
            return None

        return list(reversed(path))

    @property
    def node_count(self) -> int:
        """Return the number of nodes in the graph."""
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        """Return the number of edges in the graph."""
        return sum(len(edges) for edges in self._adj.values())
