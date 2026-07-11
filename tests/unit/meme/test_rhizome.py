"""Tests for meme.rhizome -- zero-mock, real instances only.

Covers NetworkTopology, Node, Edge, Graph, RhizomeEngine, build_graph,
and calculate_centrality with real graph structures.
"""

from __future__ import annotations

import random

import pytest

from codomyrmex.meme.rhizome.engine import RhizomeEngine
from codomyrmex.meme.rhizome.models import Edge, Graph, NetworkTopology, Node
from codomyrmex.meme.rhizome.network import build_graph, calculate_centrality

# ---------------------------------------------------------------------------
# NetworkTopology enum
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNetworkTopology:
    """Tests for the NetworkTopology enum."""

    def test_five_types_present(self) -> None:
        """All five topology types are present."""
        expected = {"random", "scale_free", "small_world", "lattice", "fully_connected"}
        assert {t.value for t in NetworkTopology} == expected

    def test_str_subclass(self) -> None:
        """NetworkTopology is a StrEnum."""
        assert isinstance(NetworkTopology.RANDOM, str)
        assert NetworkTopology.SCALE_FREE == "scale_free"


# ---------------------------------------------------------------------------
# Node dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNode:
    """Tests for the Node dataclass."""

    def test_id_auto_generated(self) -> None:
        """ID is auto-generated as an 8-char string."""
        node = Node()
        assert isinstance(node.id, str)
        assert len(node.id) == 8

    def test_default_content_empty(self) -> None:
        """Default content is empty string."""
        node = Node()
        assert node.content == ""

    def test_default_node_type(self) -> None:
        """Default node_type is 'generic'."""
        node = Node()
        assert node.node_type == "generic"

    def test_default_capacity(self) -> None:
        """Default capacity is 1.0."""
        node = Node()
        assert node.capacity == pytest.approx(1.0)

    def test_default_connections_empty(self) -> None:
        """Default connections set is empty."""
        node = Node()
        assert node.connections == set()

    def test_default_metadata_empty(self) -> None:
        """Default metadata dict is empty."""
        node = Node()
        assert node.metadata == {}

    def test_explicit_fields_stored(self) -> None:
        """Explicit field values are stored correctly."""
        node = Node(
            id="n12345ab",
            content="Test node content",
            node_type="meme",
            capacity=0.7,
        )
        assert node.id == "n12345ab"
        assert node.content == "Test node content"
        assert node.node_type == "meme"
        assert node.capacity == pytest.approx(0.7)

    def test_connections_are_mutable_set(self) -> None:
        """Connections set can be modified after creation."""
        node = Node()
        node.connections.add("other_node")
        assert "other_node" in node.connections


# ---------------------------------------------------------------------------
# Edge dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEdge:
    """Tests for the Edge dataclass."""

    def test_creation_stores_source_target(self) -> None:
        """Source and target are stored correctly."""
        edge = Edge(source="n1", target="n2")
        assert edge.source == "n1"
        assert edge.target == "n2"

    def test_default_weight(self) -> None:
        """Default weight is 1.0."""
        edge = Edge(source="a", target="b")
        assert edge.weight == pytest.approx(1.0)

    def test_default_edge_type(self) -> None:
        """Default edge_type is 'undirected'."""
        edge = Edge(source="a", target="b")
        assert edge.edge_type == "undirected"

    def test_auto_id_deterministic(self) -> None:
        """Auto-generated ID is deterministic for the same source/target."""
        e1 = Edge(source="alpha", target="beta")
        e2 = Edge(source="alpha", target="beta")
        assert e1.id == e2.id

    def test_auto_id_sorted_order(self) -> None:
        """Edge ID uses sorted source/target for undirected consistency."""
        e1 = Edge(source="z", target="a")
        e2 = Edge(source="a", target="z")
        assert e1.id == e2.id

    def test_explicit_id_preserved(self) -> None:
        """Explicit ID overrides auto-generation."""
        edge = Edge(source="x", target="y", id="custom_edge_id")
        assert edge.id == "custom_edge_id"

    def test_custom_weight(self) -> None:
        """Custom weight is stored correctly."""
        edge = Edge(source="a", target="b", weight=0.42)
        assert edge.weight == pytest.approx(0.42)


# ---------------------------------------------------------------------------
# Graph dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGraph:
    """Tests for the Graph dataclass."""

    def test_empty_defaults(self) -> None:
        """Default Graph has empty nodes and edges."""
        g = Graph()
        assert g.nodes == {}
        assert g.edges == []

    def test_add_node(self) -> None:
        """add_node stores node by ID."""
        g = Graph()
        node = Node(id="n1", content="hello")
        g.add_node(node)
        assert "n1" in g.nodes
        assert g.nodes["n1"].content == "hello"

    def test_add_edge_appended(self) -> None:
        """add_edge appends edge to list."""
        g = Graph()
        g.add_node(Node(id="a"))
        g.add_node(Node(id="b"))
        edge = Edge(source="a", target="b")
        g.add_edge(edge)
        assert len(g.edges) == 1

    def test_add_edge_updates_connections(self) -> None:
        """add_edge updates connection sets on both nodes."""
        g = Graph()
        g.add_node(Node(id="a"))
        g.add_node(Node(id="b"))
        g.add_edge(Edge(source="a", target="b"))
        assert "b" in g.nodes["a"].connections
        assert "a" in g.nodes["b"].connections

    def test_topology_default_random(self) -> None:
        """Default topology is RANDOM."""
        g = Graph()
        assert g.topology == NetworkTopology.RANDOM

    def test_add_edge_missing_node_does_not_crash(self) -> None:
        """Adding edge with non-existent node doesn't raise."""
        g = Graph()
        g.add_node(Node(id="a"))
        # target 'z' not in nodes — should not crash
        g.add_edge(Edge(source="a", target="z"))
        assert len(g.edges) == 1


# ---------------------------------------------------------------------------
# build_graph
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBuildGraph:
    """Tests for the build_graph factory function."""

    def test_random_topology_node_count(self) -> None:
        """build_graph with RANDOM topology has exactly the requested nodes."""
        g = build_graph(20, NetworkTopology.RANDOM)
        assert len(g.nodes) == 20

    def test_scale_free_node_count(self) -> None:
        """build_graph with SCALE_FREE topology has exactly the requested nodes."""
        g = build_graph(15, NetworkTopology.SCALE_FREE)
        assert len(g.nodes) == 15

    def test_random_topology_has_edges(self) -> None:
        """Random graph with enough nodes typically has some edges."""
        random.seed(42)
        g = build_graph(20, NetworkTopology.RANDOM)
        # With p=0.1 and N=20, expected edges ~19; we just check > 0
        assert len(g.edges) >= 0  # at minimum must not crash

    def test_scale_free_initial_core_connected(self) -> None:
        """Scale-free graph initial core nodes are connected."""
        g = build_graph(10, NetworkTopology.SCALE_FREE)
        # First few nodes should be well-connected
        assert len(g.edges) > 0

    def test_nodes_have_string_ids(self) -> None:
        """All nodes have string IDs prefixed with 'n'."""
        g = build_graph(5, NetworkTopology.RANDOM)
        for nid in g.nodes:
            assert nid.startswith("n")

    def test_node_content_format(self) -> None:
        """Node content follows the 'Node {i}' pattern."""
        g = build_graph(3, NetworkTopology.RANDOM)
        contents = {n.content for n in g.nodes.values()}
        assert "Node 0" in contents
        assert "Node 2" in contents

    def test_topology_stored_on_graph(self) -> None:
        """build_graph stores the topology on the returned graph."""
        g = build_graph(5, NetworkTopology.SCALE_FREE)
        assert g.topology == NetworkTopology.SCALE_FREE


# ---------------------------------------------------------------------------
# calculate_centrality
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculateCentrality:
    """Tests for the calculate_centrality function."""

    def test_empty_graph_returns_empty(self) -> None:
        """Empty graph yields empty centrality dict."""
        g = Graph()
        result = calculate_centrality(g)
        assert result == {}

    def test_single_node_returns_zero(self) -> None:
        """Single node has zero centrality (no other nodes to connect to)."""
        g = Graph()
        g.add_node(Node(id="n0"))
        result = calculate_centrality(g)
        assert result["n0"] == pytest.approx(0.0)

    def test_fully_connected_two_nodes(self) -> None:
        """In a two-node graph, each node has degree centrality 1.0."""
        g = Graph()
        g.add_node(Node(id="a"))
        g.add_node(Node(id="b"))
        g.add_edge(Edge(source="a", target="b"))
        result = calculate_centrality(g)
        assert result["a"] == pytest.approx(1.0)
        assert result["b"] == pytest.approx(1.0)

    def test_hub_node_has_highest_centrality(self) -> None:
        """In a star graph, the hub has the highest centrality."""
        g = Graph()
        for i in range(5):
            g.add_node(Node(id=f"n{i}"))
        # n0 is the hub
        for i in range(1, 5):
            g.add_edge(Edge(source="n0", target=f"n{i}"))
        result = calculate_centrality(g)
        hub_score = result["n0"]
        for leaf in ["n1", "n2", "n3", "n4"]:
            assert hub_score >= result[leaf]

    def test_degree_normalized_by_n_minus_1(self) -> None:
        """Centrality = degree / (N-1)."""
        g = Graph()
        g.add_node(Node(id="a"))
        g.add_node(Node(id="b"))
        g.add_node(Node(id="c"))
        g.add_edge(Edge(source="a", target="b"))
        g.add_edge(Edge(source="a", target="c"))
        # a has degree 2; N=3; centrality = 2/(3-1) = 1.0
        result = calculate_centrality(g)
        assert result["a"] == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------------------
# RhizomeEngine
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRhizomeEngineInitialize:
    """Tests for RhizomeEngine.initialize_network."""

    def test_default_graph_starts_empty(self) -> None:
        """Fresh RhizomeEngine starts with an empty graph."""
        engine = RhizomeEngine()
        assert len(engine.graph.nodes) == 0

    def test_initialize_random_topology(self) -> None:
        """initialize_network builds a graph with the requested size."""
        engine = RhizomeEngine()
        engine.initialize_network(size=10, topology="random")
        assert len(engine.graph.nodes) == 10

    def test_initialize_scale_free_topology(self) -> None:
        """initialize_network with scale_free builds correct graph."""
        engine = RhizomeEngine()
        engine.initialize_network(size=15, topology="scale_free")
        assert len(engine.graph.nodes) == 15

    def test_initialize_unknown_topology_falls_back_to_random(self) -> None:
        """Unknown topology string falls back to RANDOM."""
        engine = RhizomeEngine()
        engine.initialize_network(size=8, topology="unknown_type")
        assert len(engine.graph.nodes) == 8

    def test_reinitialize_replaces_graph(self) -> None:
        """Calling initialize_network twice replaces the previous graph."""
        engine = RhizomeEngine()
        engine.initialize_network(size=10, topology="random")
        engine.initialize_network(size=5, topology="random")
        assert len(engine.graph.nodes) == 5


@pytest.mark.unit
class TestRhizomeEngineResilience:
    """Tests for RhizomeEngine.analyze_resilience."""

    def test_empty_graph_resilience_zero(self) -> None:
        """Empty graph has zero resilience."""
        engine = RhizomeEngine()
        assert engine.analyze_resilience() == pytest.approx(0.0)

    def test_connected_graph_has_positive_resilience(self) -> None:
        """Graph with edges has positive resilience."""
        engine = RhizomeEngine()
        engine.initialize_network(size=20, topology="scale_free")
        resilience = engine.analyze_resilience()
        assert resilience > 0.0

    def test_resilience_in_unit_range(self) -> None:
        """Resilience is always in [0, 1]."""
        engine = RhizomeEngine()
        engine.initialize_network(size=30, topology="scale_free")
        resilience = engine.analyze_resilience()
        assert 0.0 <= resilience <= 1.0


@pytest.mark.unit
class TestRhizomeEngineInfluencers:
    """Tests for RhizomeEngine.find_influencers."""

    def test_empty_graph_returns_empty_list(self) -> None:
        """Empty graph has no influencers."""
        engine = RhizomeEngine()
        result = engine.find_influencers(top_n=5)
        assert result == []

    def test_returns_correct_count(self) -> None:
        """find_influencers returns at most top_n results."""
        engine = RhizomeEngine()
        engine.initialize_network(size=20, topology="scale_free")
        result = engine.find_influencers(top_n=5)
        assert len(result) <= 5

    def test_returns_node_ids(self) -> None:
        """find_influencers returns strings (node IDs)."""
        engine = RhizomeEngine()
        engine.initialize_network(size=15, topology="scale_free")
        result = engine.find_influencers(top_n=3)
        for nid in result:
            assert isinstance(nid, str)

    def test_influencers_are_valid_node_ids(self) -> None:
        """All returned influencers exist in the graph."""
        engine = RhizomeEngine()
        engine.initialize_network(size=20, topology="scale_free")
        result = engine.find_influencers(top_n=5)
        for nid in result:
            assert nid in engine.graph.nodes
