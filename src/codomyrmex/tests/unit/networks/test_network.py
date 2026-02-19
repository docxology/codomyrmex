"""Unit tests for the networks module."""

import pytest
from codomyrmex.networks.graph import NetworkGraph, Node, Edge


def test_graph_add_node():
    """Test standard node addition."""
    graph = NetworkGraph[str]()
    node = graph.add_node("A", data="Value A")

    assert node.id == "A"
    assert node.data == "Value A"
    assert graph.node_count == 1
    assert "A" in graph._nodes


def test_graph_add_edge():
    """Test standard edge addition."""
    graph = NetworkGraph[str]()
    edge = graph.add_edge("A", "B", weight=2.5, type="directed")

    assert edge.source.id == "A"
    assert edge.target.id == "B"
    assert edge.weight == 2.5
    assert edge.data["type"] == "directed"
    assert graph.edge_count == 1
    
    # Check neighbors
    neighbors = graph.get_neighbors("A")
    assert len(neighbors) == 1
    assert neighbors[0].id == "B"


def test_shortest_path():
    """Test Dijkstra's shortest path."""
    graph = NetworkGraph[str]()
    # A -> B -> C
    # |         ^
    # v         |
    # D -> E ---+
    
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "C", weight=1.0)
    graph.add_edge("A", "D", weight=1.0)
    graph.add_edge("D", "E", weight=1.0)
    graph.add_edge("E", "C", weight=1.0) # Path A->D->E->C is length 3.0, A->B->C is 2.0

    path = graph.shortest_path("A", "C")
    assert path is not None
    assert len(path) == 3
    assert [n.id for n in path] == ["A", "B", "C"]


def test_shortest_path_no_path():
    """Test shortest path when no path exists."""
    graph = NetworkGraph[str]()
    graph.add_node("A")
    graph.add_node("B")

    path = graph.shortest_path("A", "B")
    assert path is None
