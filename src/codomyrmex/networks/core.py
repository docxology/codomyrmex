"""Network module for Codomyrmex.

This module provides the core graph structure for representing and
manipulating networks in the system, including graph algorithms for
traversal, analysis, and serialization.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class Node(Generic[T]):
    """A node in the network."""

    id: str
    data: T
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    """An edge between two nodes."""

    source: str
    target: str
    weight: float = 1.0
    attributes: dict[str, Any] = field(default_factory=dict)


class Network:
    """Core undirected network/graph structure with analysis algorithms.

    Supports weighted edges, node/edge attributes, BFS/DFS traversal,
    connected component detection, degree centrality, and serialization.

    Example::

        net = Network("social")
        net.add_node("alice", data={"role": "admin"})
        net.add_node("bob")
        net.add_edge("alice", "bob", weight=0.9)
        assert net.has_path("alice", "bob")
    """

    def __init__(self, name: str = "default_network") -> None:
        """Initialize the network."""
        self.name = name
        self.nodes: dict[str, Node[Any]] = {}
        self.edges: list[Edge] = []
        self._adj: dict[str, list[Edge]] = {}
        logger.info("Network initialized: %s", self.name)

    # ── Node operations ─────────────────────────────────────────────

    def add_node(self, node_id: str, data: Any = None, **attributes: Any) -> Node[Any]:
        """Add a node to the network. Returns the node (existing or new)."""
        if node_id in self.nodes:
            return self.nodes[node_id]
        node = Node(id=node_id, data=data, attributes=attributes)
        self.nodes[node_id] = node
        self._adj[node_id] = []
        return node

    def remove_node(self, node_id: str) -> None:
        """Remove a node and all its edges."""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist")
        del self.nodes[node_id]
        # Remove edges involving this node
        self.edges = [e for e in self.edges if e.source != node_id and e.target != node_id]
        del self._adj[node_id]
        for nid in self._adj:
            self._adj[nid] = [e for e in self._adj[nid] if e.target != node_id and e.source != node_id]

    def has_node(self, node_id: str) -> bool:
        return node_id in self.nodes

    # ── Edge operations ─────────────────────────────────────────────

    def add_edge(
        self, source: str, target: str, weight: float = 1.0, **attributes: Any
    ) -> Edge:
        """Add an undirected edge between two existing nodes.

        Args:
            source: Source node ID.
            target: Target node ID.
            weight: Edge weight (default 1.0).

        Returns:
            The created Edge.

        Raises:
            ValueError: If either node does not exist.
        """
        if source not in self.nodes:
            raise ValueError(f"Source node {source} does not exist")
        if target not in self.nodes:
            raise ValueError(f"Target node {target} does not exist")

        edge = Edge(source=source, target=target, weight=weight, attributes=attributes)
        self.edges.append(edge)
        self._adj[source].append(edge)
        # Undirected: store reverse reference
        reverse = Edge(source=target, target=source, weight=weight, attributes=attributes)
        self._adj[target].append(reverse)
        return edge

    def has_edge(self, source: str, target: str) -> bool:
        """Check if an edge exists between two nodes (in either direction)."""
        return any(
            (e.source == source and e.target == target)
            or (e.source == target and e.target == source)
            for e in self.edges
        )

    # ── Neighborhood ────────────────────────────────────────────────

    def get_neighbors(self, node_id: str) -> list[str]:
        """Get neighbor IDs of a node.

        Raises:
            ValueError: If the node does not exist.
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist")
        return [e.target for e in self._adj.get(node_id, [])]

    def degree(self, node_id: str) -> int:
        """Return the degree (number of edges) of a node."""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist")
        return len(self._adj.get(node_id, []))

    # ── Traversal ───────────────────────────────────────────────────

    def bfs(self, start_id: str) -> list[str]:
        """Breadth-first traversal from a starting node.

        Returns:
            List of node IDs in BFS visit order.
        """
        if start_id not in self.nodes:
            raise ValueError(f"Node {start_id} does not exist")
        visited: set[str] = set()
        queue: deque[str] = deque([start_id])
        order: list[str] = []
        while queue:
            node_id = queue.popleft()
            if node_id in visited:
                continue
            visited.add(node_id)
            order.append(node_id)
            for neighbor in self.get_neighbors(node_id):
                if neighbor not in visited:
                    queue.append(neighbor)
        return order

    def dfs(self, start_id: str) -> list[str]:
        """Depth-first traversal from a starting node.

        Returns:
            List of node IDs in DFS visit order.
        """
        if start_id not in self.nodes:
            raise ValueError(f"Node {start_id} does not exist")
        visited: set[str] = set()
        stack: list[str] = [start_id]
        order: list[str] = []
        while stack:
            node_id = stack.pop()
            if node_id in visited:
                continue
            visited.add(node_id)
            order.append(node_id)
            for neighbor in reversed(self.get_neighbors(node_id)):
                if neighbor not in visited:
                    stack.append(neighbor)
        return order

    def has_path(self, source: str, target: str) -> bool:
        """Check if a path exists between two nodes."""
        return target in self.bfs(source)

    # ── Connected Components ────────────────────────────────────────

    def connected_components(self) -> list[set[str]]:
        """Find all connected components in the network.

        Returns:
            List of sets, each containing the node IDs of one component.
        """
        visited: set[str] = set()
        components: list[set[str]] = []
        for node_id in self.nodes:
            if node_id not in visited:
                component = set(self.bfs(node_id))
                visited.update(component)
                components.append(component)
        return components

    def is_connected(self) -> bool:
        """Return True if the entire network is connected."""
        if not self.nodes:
            return True
        return len(self.bfs(next(iter(self.nodes)))) == len(self.nodes)

    # ── Centrality ──────────────────────────────────────────────────

    def degree_centrality(self) -> dict[str, float]:
        """Compute normalized degree centrality for all nodes.

        Returns:
            Dict mapping node_id to centrality score in [0, 1].
        """
        n = len(self.nodes)
        if n <= 1:
            return dict.fromkeys(self.nodes, 0.0)
        return {nid: self.degree(nid) / (n - 1) for nid in self.nodes}

    # ── Properties ──────────────────────────────────────────────────

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def density(self) -> float:
        """Edge density of the network (0 to 1)."""
        n = len(self.nodes)
        if n < 2:
            return 0.0
        max_edges = n * (n - 1) / 2
        return len(self.edges) / max_edges

    # ── Serialization ───────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Serialize the network to a JSON-compatible dict."""
        return {
            "name": self.name,
            "nodes": [
                {"id": n.id, "data": n.data, "attributes": n.attributes}
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "weight": e.weight,
                    "attributes": e.attributes,
                }
                for e in self.edges
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Network:
        """Reconstruct a Network from a serialized dict."""
        net = cls(name=data.get("name", "default_network"))
        for nd in data.get("nodes", []):
            net.add_node(nd["id"], data=nd.get("data"), **nd.get("attributes", {}))
        for ed in data.get("edges", []):
            net.add_edge(ed["source"], ed["target"], weight=ed.get("weight", 1.0), **ed.get("attributes", {}))
        return net

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Network(name='{self.name}', nodes={self.node_count}, edges={self.edge_count})"
