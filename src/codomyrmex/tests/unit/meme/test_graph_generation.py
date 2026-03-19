"""Tests for scale-free graph generation in rhizome network module.

Validates that build_graph with SCALE_FREE topology produces graphs with
correct structural properties: proper node/edge counts, no isolated nodes,
power-law-like degree distributions, and acceptable performance.
"""

from __future__ import annotations

import time

import pytest

from codomyrmex.meme.rhizome.models import NetworkTopology
from codomyrmex.meme.rhizome.network import build_graph, calculate_centrality

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _degree_list(graph):
    """Return sorted list of node degrees (descending)."""
    return sorted((len(n.connections) for n in graph.nodes.values()), reverse=True)


def _max_degree(graph):
    return max(len(n.connections) for n in graph.nodes.values())


def _is_connected(graph) -> bool:
    """Simple BFS check – returns True if the whole graph is one component."""
    if not graph.nodes:
        return True
    start = next(iter(graph.nodes))
    visited: set[str] = set()
    stack = [start]
    while stack:
        nid = stack.pop()
        if nid in visited:
            continue
        visited.add(nid)
        stack.extend(graph.nodes[nid].connections - visited)
    return len(visited) == len(graph.nodes)


# ---------------------------------------------------------------------------
# 1. Correct node & edge counts
# ---------------------------------------------------------------------------


class TestNodeEdgeCounts:
    """build_graph(SCALE_FREE) must create exactly the requested number of nodes
    and at least one edge per newly-added node (after the initial clique)."""

    @pytest.mark.parametrize("num_nodes", [10, 100, 500])
    def test_node_count(self, num_nodes):
        g = build_graph(num_nodes, NetworkTopology.SCALE_FREE)
        assert len(g.nodes) == num_nodes

    @pytest.mark.parametrize("num_nodes", [10, 100, 500])
    def test_edge_count_positive(self, num_nodes):
        """Every generated graph must have at least num_nodes-1 edges."""
        g = build_graph(num_nodes, NetworkTopology.SCALE_FREE)
        # A connected graph on N nodes needs >= N-1 edges
        assert len(g.edges) >= num_nodes - 1

    @pytest.mark.parametrize("num_nodes", [10, 100, 500])
    def test_edge_count_not_complete(self, num_nodes):
        """Scale-free should be sparser than a fully-connected graph."""
        g = build_graph(num_nodes, NetworkTopology.SCALE_FREE)
        max_possible = num_nodes * (num_nodes - 1) // 2
        assert len(g.edges) < max_possible


# ---------------------------------------------------------------------------
# 2. No isolated nodes
# ---------------------------------------------------------------------------


class TestNoIsolatedNodes:
    """Every node must have at least one connection."""

    @pytest.mark.parametrize("num_nodes", [10, 100, 500])
    def test_all_nodes_connected(self, num_nodes):
        g = build_graph(num_nodes, NetworkTopology.SCALE_FREE)
        isolated = [nid for nid, node in g.nodes.items() if len(node.connections) == 0]
        assert isolated == [], f"Isolated nodes found: {isolated}"


# ---------------------------------------------------------------------------
# 3. Power-law-like degree distribution (hub existence)
# ---------------------------------------------------------------------------


class TestPowerLawProperties:
    """Scale-free networks should exhibit a skewed degree distribution:
    a few high-degree hubs and many low-degree nodes."""

    @pytest.mark.parametrize("num_nodes", [100, 500])
    def test_hub_exists(self, num_nodes):
        """At least one node should have degree >= 2x the average."""
        g = build_graph(num_nodes, NetworkTopology.SCALE_FREE)
        degrees = _degree_list(g)
        avg_degree = sum(degrees) / len(degrees)
        assert degrees[0] >= 2 * avg_degree, (
            f"Max degree {degrees[0]} not hub-like vs avg {avg_degree:.1f}"
        )

    @pytest.mark.parametrize("num_nodes", [100, 500])
    def test_degree_variance_high(self, num_nodes):
        """Variance in degree should be substantial (not uniform)."""
        g = build_graph(num_nodes, NetworkTopology.SCALE_FREE)
        degrees = _degree_list(g)
        mean_d = sum(degrees) / len(degrees)
        variance = sum((d - mean_d) ** 2 for d in degrees) / len(degrees)
        # For a power-law network variance should be at least ~mean
        assert variance >= mean_d * 0.5, f"Variance {variance:.1f} too low vs mean {mean_d:.1f}"

    @pytest.mark.parametrize("num_nodes", [100, 500])
    def test_most_nodes_low_degree(self, num_nodes):
        """>50% of nodes should have degree <= 2*mean (long tail property)."""
        g = build_graph(num_nodes, NetworkTopology.SCALE_FREE)
        degrees = _degree_list(g)
        mean_d = sum(degrees) / len(degrees)
        low_count = sum(1 for d in degrees if d <= 2 * mean_d)
        assert low_count > 0.5 * len(degrees), (
            f"Only {low_count}/{len(degrees)} nodes have degree <= 2*mean"
        )


# ---------------------------------------------------------------------------
# 4. Multi-scale tests (10, 100, 500 nodes)
# ---------------------------------------------------------------------------


class TestMultiScale:
    """Verify graphs are well-formed across a range of sizes."""

    @pytest.mark.parametrize("num_nodes", [10, 100, 500])
    def test_graph_validity(self, num_nodes):
        g = build_graph(num_nodes, NetworkTopology.SCALE_FREE)
        # Structural sanity
        assert len(g.nodes) == num_nodes
        assert len(g.edges) > 0
        # Edge endpoints must reference real nodes
        for edge in g.edges:
            assert edge.source in g.nodes
            assert edge.target in g.nodes
        # Topology tag preserved
        assert g.topology == NetworkTopology.SCALE_FREE


# ---------------------------------------------------------------------------
# 5. Connectivity
# ---------------------------------------------------------------------------


class TestConnectivity:
    """Graph should be connected (single component)."""

    @pytest.mark.parametrize("num_nodes", [10, 100, 500])
    def test_is_connected(self, num_nodes):
        g = build_graph(num_nodes, NetworkTopology.SCALE_FREE)
        assert _is_connected(g), "Graph is not fully connected"

    @pytest.mark.parametrize("num_nodes", [10, 100, 500])
    def test_centrality_returns_all_nodes(self, num_nodes):
        """calculate_centrality should return a value for every node."""
        g = build_graph(num_nodes, NetworkTopology.SCALE_FREE)
        cent = calculate_centrality(g)
        assert set(cent.keys()) == set(g.nodes.keys())
        for v in cent.values():
            assert 0.0 <= v <= 1.0


# ---------------------------------------------------------------------------
# 6. Performance benchmark
# ---------------------------------------------------------------------------


class TestPerformance:
    """Scale-free generation must be efficient."""

    def test_1000_nodes_under_5_seconds(self):
        """build_graph with 1000 SCALE_FREE nodes must finish in < 5 s."""
        start = time.perf_counter()
        g = build_graph(1000, NetworkTopology.SCALE_FREE)
        elapsed = time.perf_counter() - start

        assert len(g.nodes) == 1000
        assert elapsed < 5.0, f"Generation took {elapsed:.2f}s (limit 5s)"

    def test_500_nodes_fast(self):
        """500-node graph should be sub-second."""
        start = time.perf_counter()
        g = build_graph(500, NetworkTopology.SCALE_FREE)
        elapsed = time.perf_counter() - start

        assert len(g.nodes) == 500
        assert elapsed < 1.0, f"Generation took {elapsed:.2f}s (limit 1s)"
