"""Social graph analysis and metrics.

Implements an undirected weighted graph with community detection
(label propagation), centrality measures, and shortest-path search.
"""

from __future__ import annotations

import random
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any


class SocialGraph:
    """Undirected weighted graph representing a social network.

    Nodes represent people or entities; edges represent relationships
    with optional weights (default 1.0).

    Attributes:
        nodes: Mapping of node ID to attribute dict.
        edges: Adjacency list mapping node ID to {neighbor: weight}.
    """

    def __init__(self) -> None:
        """Initialize an empty social graph."""
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: dict[str, dict[str, float]] = defaultdict(dict)

    def add_node(self, id: str, attributes: dict[str, Any] | None = None) -> None:
        """Add a node (person/entity) to the graph.

        If the node already exists its attributes are updated.

        Args:
            id: Unique node identifier.
            attributes: Optional key-value metadata.
        """
        if id in self._nodes:
            if attributes:
                self._nodes[id].update(attributes)
        else:
            self._nodes[id] = attributes or {}
            # Ensure adjacency entry exists
            if id not in self._edges:
                self._edges[id] = {}

    def add_edge(self, source: str, target: str, weight: float = 1.0) -> None:
        """Add an undirected edge between two nodes.

        Both nodes are created automatically if they don't exist.

        Args:
            source: First node ID.
            target: Second node ID.
            weight: Edge weight (default 1.0).
        """
        if source not in self._nodes:
            self.add_node(source)
        if target not in self._nodes:
            self.add_node(target)
        self._edges[source][target] = weight
        self._edges[target][source] = weight

    def find_communities(self) -> list[set[str]]:
        """Detect communities using label propagation.

        Each node starts with its own label.  In each iteration, every
        node adopts the most common label among its neighbors.  The
        process repeats until labels stabilize (or a max iteration
        count is reached).

        Returns:
            List of sets, each set containing node IDs in a community.
        """
        labels: dict[str, str] = {n: n for n in self._nodes}
        max_iterations = 50

        for _ in range(max_iterations):
            changed = False
            node_list = list(self._nodes.keys())
            random.shuffle(node_list)

            for node in node_list:
                neighbors = self._edges.get(node, {})
                if not neighbors:
                    continue

                # Count neighbor labels weighted by edge weight
                label_weights: dict[str, float] = defaultdict(float)
                for neighbor, weight in neighbors.items():
                    label_weights[labels[neighbor]] += weight

                best_label = max(label_weights, key=lambda lb: label_weights[lb])
                if labels[node] != best_label:
                    labels[node] = best_label
                    changed = True

            if not changed:
                break

        # Group nodes by label
        communities: dict[str, set[str]] = defaultdict(set)
        for node, label in labels.items():
            communities[label].add(node)

        return list(communities.values())

    def calculate_centrality(self) -> dict[str, float]:
        """Compute degree centrality for every node.

        Degree centrality is the fraction of other nodes each node is
        connected to: degree(v) / (N - 1).

        Returns:
            Mapping of node ID to centrality score in [0, 1].
        """
        n = len(self._nodes)
        if n <= 1:
            return {nid: 0.0 for nid in self._nodes}

        return {
            nid: len(self._edges.get(nid, {})) / (n - 1)
            for nid in self._nodes
        }

    def shortest_path(self, source: str, target: str) -> list[str]:
        """Find the shortest (fewest hops) path between two nodes via BFS.

        Args:
            source: Starting node ID.
            target: Destination node ID.

        Returns:
            Ordered list of node IDs from source to target inclusive.
            Empty list if no path exists or nodes are missing.
        """
        if source not in self._nodes or target not in self._nodes:
            return []

        if source == target:
            return [source]

        visited: set[str] = {source}
        queue: deque[list[str]] = deque([[source]])

        while queue:
            path = queue.popleft()
            current = path[-1]

            for neighbor in self._edges.get(current, {}):
                if neighbor == target:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return []  # No path found

    def get_influence_score(self, node_id: str) -> float:
        """Compute an influence score for a node.

        Influence is defined as the weighted sum of edges incident to
        the node, normalized by the total edge weight in the graph.

        Args:
            node_id: The node to score.

        Returns:
            Influence score in [0, 1], or 0.0 if the node is absent.
        """
        if node_id not in self._nodes:
            return 0.0

        node_weight = sum(self._edges.get(node_id, {}).values())
        total_weight = sum(
            w for neighbors in self._edges.values() for w in neighbors.values()
        )
        # Each undirected edge is counted twice in total_weight
        if total_weight == 0:
            return 0.0
        return node_weight / (total_weight / 2)

    def neighbors(self, node_id: str) -> dict[str, float]:
        """Return the neighbors and edge weights for a node."""
        return dict(self._edges.get(node_id, {}))

    @property
    def node_count(self) -> int:
        """Number of nodes in the graph."""
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        """Number of undirected edges (each pair counted once)."""
        total = sum(len(adj) for adj in self._edges.values())
        return total // 2

    @property
    def nodes(self) -> dict[str, dict[str, Any]]:
        """Read-only copy of node data."""
        return dict(self._nodes)


class GraphMetrics:
    """Static utility class for computing aggregate graph metrics."""

    @staticmethod
    def density(graph: SocialGraph) -> float:
        """Compute graph density: ratio of actual to possible edges.

        For an undirected graph with N nodes, max edges = N*(N-1)/2.

        Args:
            graph: The SocialGraph to analyze.

        Returns:
            Density value in [0, 1].
        """
        n = graph.node_count
        if n <= 1:
            return 0.0
        max_edges = n * (n - 1) / 2
        return graph.edge_count / max_edges

    @staticmethod
    def clustering_coefficient(graph: SocialGraph) -> float:
        """Compute the average local clustering coefficient.

        For each node, the local clustering coefficient is the fraction
        of pairs of its neighbors that are themselves connected.  The
        graph-level coefficient is the mean over all nodes.

        Args:
            graph: The SocialGraph to analyze.

        Returns:
            Average clustering coefficient in [0, 1].
        """
        coefficients: list[float] = []

        for node_id in graph.nodes:
            neighbor_ids = list(graph.neighbors(node_id).keys())
            k = len(neighbor_ids)
            if k < 2:
                coefficients.append(0.0)
                continue

            # Count edges among neighbors
            triangles = 0
            for i in range(k):
                for j in range(i + 1, k):
                    ni = neighbor_ids[i]
                    nj = neighbor_ids[j]
                    if nj in graph.neighbors(ni):
                        triangles += 1

            possible = k * (k - 1) / 2
            coefficients.append(triangles / possible)

        if not coefficients:
            return 0.0
        return sum(coefficients) / len(coefficients)

    @staticmethod
    def degree_distribution(graph: SocialGraph) -> dict[int, int]:
        """Compute the degree distribution of the graph.

        Returns:
            Mapping of degree value to the count of nodes with that degree.
        """
        distribution: dict[int, int] = defaultdict(int)
        for node_id in graph.nodes:
            degree = len(graph.neighbors(node_id))
            distribution[degree] += 1
        return dict(sorted(distribution.items()))
