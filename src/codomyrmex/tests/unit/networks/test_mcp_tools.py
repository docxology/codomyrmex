"""Strictly zero-mock unit tests for networks MCP tools.

Verifies that the MCP tools correctly interact with the networks core logic
without utilizing mocking frameworks.
"""

from collections.abc import Generator

import pytest

from codomyrmex.networks.core import Network
from codomyrmex.networks.mcp_tools import (
    _register_network,
    _reset_networks_registry,
    network_add_edge,
    network_add_node,
    network_get_neighbors,
)


@pytest.fixture(autouse=True)
def reset_registry() -> Generator[None, None, None]:
    """Ensure the networks registry is empty before and after each test."""
    _reset_networks_registry()
    yield
    _reset_networks_registry()


@pytest.fixture
def sample_network() -> Network:
    """Provide a sample network populated with nodes and edges."""
    net = Network(name="test_net")
    net.add_node("n1", data="val1")
    net.add_node("n2", data="val2")
    net.add_edge("n1", "n2", weight=1.5)
    _register_network(net)
    return net


def test_network_add_node_success() -> None:
    """Test adding a node successfully."""
    net = Network(name="my_net")
    _register_network(net)

    result = network_add_node(
        network_name="my_net", node_id="n1", data="my_data", attributes={"color": "red"}
    )

    assert result["status"] == "success"
    assert result["node_id"] == "n1"
    assert "added" in result["message"]

    # Verify actual network state
    assert net.has_node("n1")
    assert net.nodes["n1"].data == "my_data"
    assert net.nodes["n1"].attributes == {"color": "red"}


def test_network_add_node_duplicate(sample_network: Network) -> None:
    """Test adding a node that already exists."""
    result = network_add_node(network_name=sample_network.name, node_id="n1")

    assert result["status"] == "duplicate"
    assert result["node_id"] == "n1"
    assert "already exists" in result["message"]


def test_network_add_node_network_not_found() -> None:
    """Test adding a node to a non-existent network."""
    result = network_add_node(network_name="missing_net", node_id="n1")

    assert "error" in result
    assert "not found" in result["error"]


def test_network_add_edge_success(sample_network: Network) -> None:
    """Test adding an edge successfully."""
    sample_network.add_node("n3")

    result = network_add_edge(
        network_name=sample_network.name,
        source="n1",
        target="n3",
        weight=2.0,
        attributes={"type": "depends"},
    )

    assert result["status"] == "success"
    assert result["source"] == "n1"
    assert result["target"] == "n3"
    assert result["weight"] == 2.0

    # Verify actual network state
    assert sample_network.has_edge("n1", "n3")
    edges = sample_network._adj["n1"]
    edge = next(e for e in edges if e.target == "n3")
    assert edge.weight == 2.0
    assert edge.attributes == {"type": "depends"}


def test_network_add_edge_missing_nodes(sample_network: Network) -> None:
    """Test adding an edge where source or target nodes do not exist."""
    # Source missing
    result_src = network_add_edge(
        network_name=sample_network.name, source="missing_src", target="n2"
    )
    assert "error" in result_src
    assert "Source node 'missing_src' not found" in result_src["error"]

    # Target missing
    result_tgt = network_add_edge(
        network_name=sample_network.name, source="n1", target="missing_tgt"
    )
    assert "error" in result_tgt
    assert "Target node 'missing_tgt' not found" in result_tgt["error"]


def test_network_get_neighbors_success(sample_network: Network) -> None:
    """Test retrieving neighbors for a node."""
    result = network_get_neighbors(network_name=sample_network.name, node_id="n1")

    assert result["status"] == "success"
    assert result["node_id"] == "n1"
    assert "n2" in result["neighbors"]
    assert result["count"] == 1


def test_network_get_neighbors_missing_node(sample_network: Network) -> None:
    """Test retrieving neighbors for a non-existent node."""
    result = network_get_neighbors(
        network_name=sample_network.name, node_id="missing_node"
    )

    assert "error" in result
    assert "Node 'missing_node' not found" in result["error"]


def test_network_get_neighbors_network_not_found() -> None:
    """Test retrieving neighbors from a non-existent network."""
    result = network_get_neighbors(network_name="missing_net", node_id="n1")

    assert "error" in result
    assert "not found" in result["error"]
