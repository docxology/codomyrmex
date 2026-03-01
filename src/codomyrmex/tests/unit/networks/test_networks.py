"""Unit tests for the networks module: Network (core.py) and NetworkGraph (graph.py).

Tests cover:
- Node/Edge dataclass construction (both core and graph variants)
- Network: add/remove nodes, add edges, has_node, has_edge
- Network: get_neighbors, degree
- Network: BFS, DFS, has_path
- Network: connected_components, is_connected
- Network: degree_centrality
- Network: density, node_count, edge_count properties
- Network: to_dict / from_dict serialization round-trip
- Network: repr
- Network: error handling (ValueError for missing nodes)
- NetworkGraph: add_node, add_edge, get_neighbors, shortest_path
- NetworkGraph: node_count, edge_count
"""


import pytest

from codomyrmex.networks.core import Edge as CoreEdge
from codomyrmex.networks.core import Network, Node as CoreNode
from codomyrmex.networks.graph import Edge as GraphEdge
from codomyrmex.networks.graph import NetworkGraph, Node as GraphNode


# ---------------------------------------------------------------------------
# core.py -- Node and Edge dataclasses
# ---------------------------------------------------------------------------

class TestCoreNodeEdge:
    """Node and Edge dataclasses from core.py."""

    @pytest.mark.unit
    def test_node_creation(self) -> None:
        node = CoreNode(id="a", data={"key": "val"})
        assert node.id == "a"
        assert node.data == {"key": "val"}
        assert node.attributes == {}

    @pytest.mark.unit
    def test_node_with_attributes(self) -> None:
        node = CoreNode(id="b", data=None, attributes={"color": "red"})
        assert node.attributes["color"] == "red"

    @pytest.mark.unit
    def test_edge_defaults(self) -> None:
        edge = CoreEdge(source="a", target="b")
        assert edge.weight == 1.0
        assert edge.attributes == {}

    @pytest.mark.unit
    def test_edge_custom_weight(self) -> None:
        edge = CoreEdge(source="x", target="y", weight=0.5, attributes={"label": "friend"})
        assert edge.weight == 0.5
        assert edge.attributes["label"] == "friend"


# ---------------------------------------------------------------------------
# core.py -- Network class: node operations
# ---------------------------------------------------------------------------

class TestNetworkNodeOps:
    """Network.add_node, remove_node, has_node."""

    @pytest.mark.unit
    def test_add_node_returns_node(self) -> None:
        net = Network("test")
        node = net.add_node("a", data="hello")
        assert node.id == "a"
        assert node.data == "hello"
        assert net.has_node("a")

    @pytest.mark.unit
    def test_add_duplicate_returns_existing(self) -> None:
        net = Network("test")
        n1 = net.add_node("a", data="first")
        n2 = net.add_node("a", data="second")
        assert n1 is n2
        assert n1.data == "first"  # original data preserved
        assert net.node_count == 1

    @pytest.mark.unit
    def test_remove_node(self) -> None:
        net = Network("test")
        net.add_node("a")
        net.add_node("b")
        net.add_edge("a", "b")
        net.remove_node("a")
        assert not net.has_node("a")
        assert net.edge_count == 0

    @pytest.mark.unit
    def test_remove_nonexistent_node_raises(self) -> None:
        net = Network("test")
        with pytest.raises(ValueError, match="does not exist"):
            net.remove_node("ghost")

    @pytest.mark.unit
    def test_has_node_false_for_missing(self) -> None:
        net = Network("test")
        assert not net.has_node("nope")


# ---------------------------------------------------------------------------
# core.py -- Network class: edge operations
# ---------------------------------------------------------------------------

class TestNetworkEdgeOps:
    """Network.add_edge, has_edge."""

    @pytest.mark.unit
    def test_add_edge(self) -> None:
        net = Network("test")
        net.add_node("a")
        net.add_node("b")
        edge = net.add_edge("a", "b", weight=2.0)
        assert edge.source == "a"
        assert edge.target == "b"
        assert edge.weight == 2.0
        assert net.edge_count == 1

    @pytest.mark.unit
    def test_has_edge_both_directions(self) -> None:
        net = Network("test")
        net.add_node("a")
        net.add_node("b")
        net.add_edge("a", "b")
        assert net.has_edge("a", "b")
        assert net.has_edge("b", "a")  # undirected

    @pytest.mark.unit
    def test_has_edge_false(self) -> None:
        net = Network("test")
        net.add_node("a")
        net.add_node("b")
        assert not net.has_edge("a", "b")

    @pytest.mark.unit
    def test_add_edge_missing_source_raises(self) -> None:
        net = Network("test")
        net.add_node("b")
        with pytest.raises(ValueError, match="Source node"):
            net.add_edge("missing", "b")

    @pytest.mark.unit
    def test_add_edge_missing_target_raises(self) -> None:
        net = Network("test")
        net.add_node("a")
        with pytest.raises(ValueError, match="Target node"):
            net.add_edge("a", "missing")


# ---------------------------------------------------------------------------
# core.py -- Network class: neighborhood
# ---------------------------------------------------------------------------

class TestNetworkNeighborhood:
    """get_neighbors, degree."""

    @pytest.mark.unit
    def test_get_neighbors(self) -> None:
        net = Network("test")
        net.add_node("a")
        net.add_node("b")
        net.add_node("c")
        net.add_edge("a", "b")
        net.add_edge("a", "c")
        neighbors = net.get_neighbors("a")
        assert set(neighbors) == {"b", "c"}

    @pytest.mark.unit
    def test_get_neighbors_missing_raises(self) -> None:
        net = Network("test")
        with pytest.raises(ValueError):
            net.get_neighbors("ghost")

    @pytest.mark.unit
    def test_degree(self) -> None:
        net = Network("test")
        net.add_node("a")
        net.add_node("b")
        net.add_node("c")
        net.add_edge("a", "b")
        net.add_edge("a", "c")
        assert net.degree("a") == 2
        assert net.degree("b") == 1

    @pytest.mark.unit
    def test_degree_missing_raises(self) -> None:
        net = Network("test")
        with pytest.raises(ValueError):
            net.degree("ghost")


# ---------------------------------------------------------------------------
# core.py -- Network class: traversal
# ---------------------------------------------------------------------------

class TestNetworkTraversal:
    """BFS, DFS, has_path."""

    @pytest.mark.unit
    def test_bfs_linear(self) -> None:
        net = Network("test")
        for n in ("a", "b", "c"):
            net.add_node(n)
        net.add_edge("a", "b")
        net.add_edge("b", "c")
        order = net.bfs("a")
        assert order == ["a", "b", "c"]

    @pytest.mark.unit
    def test_bfs_missing_start_raises(self) -> None:
        net = Network("test")
        with pytest.raises(ValueError):
            net.bfs("ghost")

    @pytest.mark.unit
    def test_dfs_linear(self) -> None:
        net = Network("test")
        for n in ("a", "b", "c"):
            net.add_node(n)
        net.add_edge("a", "b")
        net.add_edge("b", "c")
        order = net.dfs("a")
        assert order == ["a", "b", "c"]

    @pytest.mark.unit
    def test_dfs_missing_start_raises(self) -> None:
        net = Network("test")
        with pytest.raises(ValueError):
            net.dfs("ghost")

    @pytest.mark.unit
    def test_has_path_connected(self) -> None:
        net = Network("test")
        for n in ("a", "b", "c"):
            net.add_node(n)
        net.add_edge("a", "b")
        net.add_edge("b", "c")
        assert net.has_path("a", "c")

    @pytest.mark.unit
    def test_has_path_disconnected(self) -> None:
        net = Network("test")
        net.add_node("a")
        net.add_node("z")
        assert not net.has_path("a", "z")

    @pytest.mark.unit
    def test_bfs_visits_all_reachable(self) -> None:
        """BFS from hub node visits all connected nodes in a star topology."""
        net = Network("star")
        net.add_node("hub")
        for i in range(5):
            nid = f"leaf_{i}"
            net.add_node(nid)
            net.add_edge("hub", nid)
        visited = net.bfs("hub")
        assert len(visited) == 6
        assert visited[0] == "hub"


# ---------------------------------------------------------------------------
# core.py -- Network class: components and connectivity
# ---------------------------------------------------------------------------

class TestNetworkComponents:
    """connected_components, is_connected."""

    @pytest.mark.unit
    def test_single_component(self) -> None:
        net = Network("test")
        for n in ("a", "b", "c"):
            net.add_node(n)
        net.add_edge("a", "b")
        net.add_edge("b", "c")
        components = net.connected_components()
        assert len(components) == 1
        assert components[0] == {"a", "b", "c"}

    @pytest.mark.unit
    def test_two_components(self) -> None:
        net = Network("test")
        for n in ("a", "b", "x", "y"):
            net.add_node(n)
        net.add_edge("a", "b")
        net.add_edge("x", "y")
        components = net.connected_components()
        assert len(components) == 2

    @pytest.mark.unit
    def test_is_connected_true(self) -> None:
        net = Network("test")
        for n in ("a", "b"):
            net.add_node(n)
        net.add_edge("a", "b")
        assert net.is_connected()

    @pytest.mark.unit
    def test_is_connected_false(self) -> None:
        net = Network("test")
        net.add_node("a")
        net.add_node("b")
        assert not net.is_connected()

    @pytest.mark.unit
    def test_empty_network_is_connected(self) -> None:
        net = Network("empty")
        assert net.is_connected()


# ---------------------------------------------------------------------------
# core.py -- Network class: centrality
# ---------------------------------------------------------------------------

class TestNetworkCentrality:
    """degree_centrality."""

    @pytest.mark.unit
    def test_degree_centrality_single_node(self) -> None:
        net = Network("test")
        net.add_node("a")
        cent = net.degree_centrality()
        assert cent["a"] == 0.0

    @pytest.mark.unit
    def test_degree_centrality_star(self) -> None:
        net = Network("star")
        net.add_node("hub")
        for i in range(4):
            nid = f"leaf_{i}"
            net.add_node(nid)
            net.add_edge("hub", nid)
        cent = net.degree_centrality()
        # hub has degree 4 out of 4 possible (n-1=4), so centrality = 1.0
        assert cent["hub"] == 1.0
        for i in range(4):
            assert cent[f"leaf_{i}"] == 1 / 4  # degree 1 / (n-1=4)


# ---------------------------------------------------------------------------
# core.py -- Network class: properties
# ---------------------------------------------------------------------------

class TestNetworkProperties:
    """node_count, edge_count, density."""

    @pytest.mark.unit
    def test_node_count(self) -> None:
        net = Network("test")
        assert net.node_count == 0
        net.add_node("a")
        net.add_node("b")
        assert net.node_count == 2

    @pytest.mark.unit
    def test_edge_count(self) -> None:
        net = Network("test")
        net.add_node("a")
        net.add_node("b")
        net.add_edge("a", "b")
        assert net.edge_count == 1

    @pytest.mark.unit
    def test_density_empty(self) -> None:
        net = Network("test")
        assert net.density == 0.0

    @pytest.mark.unit
    def test_density_complete_triangle(self) -> None:
        net = Network("triangle")
        for n in ("a", "b", "c"):
            net.add_node(n)
        net.add_edge("a", "b")
        net.add_edge("b", "c")
        net.add_edge("a", "c")
        # 3 edges / max_edges(3 nodes) = 3 / 3 = 1.0
        assert net.density == 1.0

    @pytest.mark.unit
    def test_density_single_node(self) -> None:
        net = Network("test")
        net.add_node("a")
        assert net.density == 0.0


# ---------------------------------------------------------------------------
# core.py -- Network class: serialization
# ---------------------------------------------------------------------------

class TestNetworkSerialization:
    """to_dict / from_dict round-trip."""

    @pytest.mark.unit
    def test_to_dict_structure(self) -> None:
        net = Network("mynet")
        net.add_node("a", data="hello")
        net.add_node("b")
        net.add_edge("a", "b", weight=3.0)
        d = net.to_dict()
        assert d["name"] == "mynet"
        assert len(d["nodes"]) == 2
        assert len(d["edges"]) == 1
        assert d["edges"][0]["weight"] == 3.0

    @pytest.mark.unit
    def test_round_trip(self) -> None:
        net = Network("roundtrip")
        net.add_node("x", data=42)
        net.add_node("y", data=99)
        net.add_edge("x", "y", weight=2.5)
        d = net.to_dict()

        restored = Network.from_dict(d)
        assert restored.name == "roundtrip"
        assert restored.node_count == 2
        assert restored.edge_count == 1
        assert restored.has_edge("x", "y")
        assert restored.nodes["x"].data == 42

    @pytest.mark.unit
    def test_from_dict_missing_name_uses_default(self) -> None:
        data = {"nodes": [{"id": "a"}], "edges": []}
        net = Network.from_dict(data)
        assert net.name == "default_network"

    @pytest.mark.unit
    def test_repr(self) -> None:
        net = Network("demo")
        net.add_node("a")
        net.add_node("b")
        net.add_edge("a", "b")
        r = repr(net)
        assert "demo" in r
        assert "nodes=2" in r
        assert "edges=1" in r


# ---------------------------------------------------------------------------
# graph.py -- GraphNode and GraphEdge dataclasses
# ---------------------------------------------------------------------------

class TestGraphNodeEdge:
    """Frozen Node and Edge from graph.py."""

    @pytest.mark.unit
    def test_graph_node_hash_by_id(self) -> None:
        n1 = GraphNode(id="a", data="one")
        n2 = GraphNode(id="a", data="two")
        assert hash(n1) == hash(n2)
        assert n1 == n2

    @pytest.mark.unit
    def test_graph_node_not_equal_different_id(self) -> None:
        n1 = GraphNode(id="a")
        n2 = GraphNode(id="b")
        assert n1 != n2

    @pytest.mark.unit
    def test_graph_node_not_equal_non_node(self) -> None:
        n = GraphNode(id="a")
        assert n != "a"

    @pytest.mark.unit
    def test_graph_edge_defaults(self) -> None:
        src = GraphNode(id="a")
        tgt = GraphNode(id="b")
        edge = GraphEdge(source=src, target=tgt)
        assert edge.weight == 1.0
        assert edge.data == {}


# ---------------------------------------------------------------------------
# graph.py -- NetworkGraph class
# ---------------------------------------------------------------------------

class TestNetworkGraph:
    """NetworkGraph: add_node, add_edge, get_neighbors, shortest_path, counts."""

    @pytest.mark.unit
    def test_add_node(self) -> None:
        g = NetworkGraph()
        node = g.add_node("a", data="val")
        assert node.id == "a"
        assert node.data == "val"
        assert g.node_count == 1

    @pytest.mark.unit
    def test_add_node_idempotent(self) -> None:
        g = NetworkGraph()
        n1 = g.add_node("a", data="first")
        n2 = g.add_node("a", data="second")
        assert n1 is n2
        assert g.node_count == 1

    @pytest.mark.unit
    def test_add_edge_auto_creates_nodes(self) -> None:
        g = NetworkGraph()
        edge = g.add_edge("a", "b", weight=2.0)
        assert g.node_count == 2
        assert edge.weight == 2.0

    @pytest.mark.unit
    def test_get_neighbors(self) -> None:
        g = NetworkGraph()
        g.add_edge("a", "b")
        g.add_edge("a", "c")
        neighbors = g.get_neighbors("a")
        assert len(neighbors) == 2
        neighbor_ids = {n.id for n in neighbors}
        assert neighbor_ids == {"b", "c"}

    @pytest.mark.unit
    def test_get_neighbors_missing_node(self) -> None:
        g = NetworkGraph()
        assert g.get_neighbors("ghost") == []

    @pytest.mark.unit
    def test_shortest_path_direct(self) -> None:
        g = NetworkGraph()
        g.add_edge("a", "b", weight=1.0)
        path = g.shortest_path("a", "b")
        assert path is not None
        assert [n.id for n in path] == ["a", "b"]

    @pytest.mark.unit
    def test_shortest_path_chooses_lighter(self) -> None:
        """Shortest path prefers lower total weight."""
        g = NetworkGraph()
        g.add_edge("a", "b", weight=1.0)
        g.add_edge("b", "c", weight=1.0)
        g.add_edge("a", "c", weight=10.0)
        path = g.shortest_path("a", "c")
        assert path is not None
        assert [n.id for n in path] == ["a", "b", "c"]

    @pytest.mark.unit
    def test_shortest_path_no_path(self) -> None:
        g = NetworkGraph()
        g.add_node("a")
        g.add_node("b")
        path = g.shortest_path("a", "b")
        assert path is None

    @pytest.mark.unit
    def test_shortest_path_nonexistent_nodes(self) -> None:
        g = NetworkGraph()
        assert g.shortest_path("x", "y") is None

    @pytest.mark.unit
    def test_edge_count(self) -> None:
        g = NetworkGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        assert g.edge_count == 2

    @pytest.mark.unit
    def test_edge_with_extra_data(self) -> None:
        g = NetworkGraph()
        edge = g.add_edge("a", "b", weight=1.5, label="friend", since=2020)
        assert edge.data["label"] == "friend"
        assert edge.data["since"] == 2020


# ---------------------------------------------------------------------------
# Integration: Network + package __init__
# ---------------------------------------------------------------------------

class TestPackageInit:
    """The networks package __init__ re-exports core classes."""

    @pytest.mark.unit
    def test_init_exports_network(self) -> None:
        from codomyrmex.networks import Network as N

        assert N is Network

    @pytest.mark.unit
    def test_init_exports_node_edge(self) -> None:
        from codomyrmex.networks import Edge, Node

        assert Node is CoreNode
        assert Edge is CoreEdge
