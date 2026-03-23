"""MCP tool definitions for the networks module.

Exposes graph/network creation, analysis, and serialization as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_network():
    """Lazy import of Network class."""
    from codomyrmex.networks.core import Network

    return Network


@mcp_tool(
    category="networks",
    description=(
        "Analyze a network graph: compute node count, edge count, density, "
        "connected components, and degree centrality."
    ),
)
def networks_analyze(
    nodes: list[str],
    edges: list[list[str]],
) -> dict[str, Any]:
    """Build a network from nodes/edges and return analysis metrics.

    Args:
        nodes: list of node IDs.
        edges: list of [source, target] pairs.

    Returns:
        dict with keys: status, node_count, edge_count, density,
        num_components, is_connected, degree_centrality
    """
    try:
        Network = _get_network()
        net = Network("analysis")
        for nid in nodes:
            net.add_node(nid)
        for edge in edges:
            if len(edge) >= 2:
                net.add_edge(edge[0], edge[1])
        components = net.connected_components()
        return {
            "status": "success",
            "node_count": net.node_count,
            "edge_count": net.edge_count,
            "density": net.density,
            "num_components": len(components),
            "is_connected": net.is_connected(),
            "degree_centrality": net.degree_centrality(),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="networks",
    description="Check if a path exists between two nodes in a network graph.",
)
def networks_has_path(
    nodes: list[str],
    edges: list[list[str]],
    source: str = "",
    target: str = "",
) -> dict[str, Any]:
    """Check reachability between two nodes.

    Args:
        nodes: list of node IDs.
        edges: list of [source, target] pairs.
        source: Source node ID.
        target: Target node ID.

    Returns:
        dict with keys: status, has_path, source, target
    """
    if not source or not target:
        return {"status": "error", "message": "source and target are required"}
    try:
        Network = _get_network()
        net = Network("pathcheck")
        for nid in nodes:
            net.add_node(nid)
        for edge in edges:
            if len(edge) >= 2:
                net.add_edge(edge[0], edge[1])
        return {
            "status": "success",
            "has_path": net.has_path(source, target),
            "source": source,
            "target": target,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="networks",
    description="Serialize a network to a JSON-compatible dictionary.",
)
def networks_to_dict(
    name: str = "default",
    nodes: list[str] | None = None,
    edges: list[list[str]] | None = None,
) -> dict[str, Any]:
    """Build a network and return its serialized form.

    Args:
        name: Network name.
        nodes: list of node IDs (default: empty).
        edges: list of [source, target] pairs (default: empty).

    Returns:
        dict with keys: status, network (serialized dict)
    """
    try:
        Network = _get_network()
        net = Network(name)
        for nid in nodes or []:
            net.add_node(nid)
        for edge in edges or []:
            if len(edge) >= 2:
                net.add_edge(edge[0], edge[1])
        return {"status": "success", "network": net.to_dict()}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
