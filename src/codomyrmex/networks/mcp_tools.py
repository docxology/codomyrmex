"""MCP tool definitions for the networks module.

Exposes network graph management capabilities as MCP tools.
"""

from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.networks.core import Network

logger = get_logger(__name__)

# Registry to hold networks by name for MCP tool interactions
_networks: dict[str, Network] = {}


@mcp_tool(
    name="network_get_neighbors",
    category="networks",
    description="Query the neighbors of a node in a network. Returns all node IDs connected to the specified node via inbound or outbound edges.",
)
def network_get_neighbors(network_name: str, node_id: str) -> dict[str, Any]:
    """Query the neighbors of a node in a network.

    Args:
        network_name: Name of the network to query.
        node_id: ID of the node whose neighbors to retrieve.

    Returns:
        Dictionary with status, node_id, neighbors array, and count, or error.
    """
    if network_name not in _networks:
        return {"error": f"Network '{network_name}' not found."}

    net = _networks[network_name]

    if not net.has_node(node_id):
        return {"error": f"Node '{node_id}' not found in network '{network_name}'."}

    neighbors = net.get_neighbors(node_id)
    return {
        "status": "success",
        "node_id": node_id,
        "neighbors": neighbors,
        "count": len(neighbors),
    }


@mcp_tool(
    name="network_add_node",
    category="networks",
    description="Add a node to an existing network. Enables agents to dynamically construct graph topologies.",
)
def network_add_node(
    network_name: str,
    node_id: str,
    data: Any = None,
    attributes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Add a node to a network.

    Args:
        network_name: Name of the target network.
        node_id: Unique identifier for the new node.
        data: Optional payload data for the node.
        attributes: Optional arbitrary key-value attributes.

    Returns:
        Dictionary with status (success, duplicate, error), node_id, and message.
    """
    if not network_name:
        return {"error": "network_name must be a non-empty string."}
    if not node_id:
        return {"error": "node_id must be a non-empty string."}

    attrs = attributes or {}

    # The SPEC says "Returns error if no network with network_name is registered."
    # But for a tool building networks dynamically, if it doesn't exist, we might want to auto-create
    # Wait, the spec strictly says: Returns error if no network with `network_name` is registered.
    if network_name not in _networks:
        return {"error": f"Network '{network_name}' not found."}

    net = _networks[network_name]

    if net.has_node(node_id):
        return {
            "status": "duplicate",
            "node_id": node_id,
            "message": f"Node '{node_id}' already exists in network '{network_name}'",
        }

    net.add_node(node_id, data=data, **attrs)

    return {
        "status": "success",
        "node_id": node_id,
        "message": f"Node '{node_id}' added",
    }


@mcp_tool(
    name="network_add_edge",
    category="networks",
    description="Add a directed, weighted edge between two existing nodes in a network.",
)
def network_add_edge(
    network_name: str,
    source: str,
    target: str,
    weight: float = 1.0,
    attributes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Add a directed, weighted edge between two existing nodes in a network.

    Args:
        network_name: Name of the target network.
        source: Source node ID.
        target: Target node ID.
        weight: Edge weight (default: 1.0).
        attributes: Optional arbitrary key-value attributes.

    Returns:
        Dictionary with status, source, target, and weight, or error.
    """
    if not network_name:
        return {"error": "network_name must be a non-empty string."}
    if not source:
        return {"error": "source must be a non-empty string."}
    if not target:
        return {"error": "target must be a non-empty string."}

    attrs = attributes or {}

    if network_name not in _networks:
        return {"error": f"Network '{network_name}' not found."}

    net = _networks[network_name]

    if not net.has_node(source):
        return {
            "error": f"Source node '{source}' not found in network '{network_name}'."
        }
    if not net.has_node(target):
        return {
            "error": f"Target node '{target}' not found in network '{network_name}'."
        }

    net.add_edge(source, target, weight=weight, **attrs)

    return {"status": "success", "source": source, "target": target, "weight": weight}


def _reset_networks_registry() -> None:
    """Reset the global networks registry (primarily for testing)."""
    global _networks
    _networks.clear()


def _register_network(network: Network) -> None:
    """Register a network in the global registry."""
    _networks[network.name] = network
