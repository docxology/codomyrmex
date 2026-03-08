"""MCP tool definitions for the Network Analysis submodule.

Exposes social graph analysis tools for calculating centrality
and identifying communities.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

# Global state for social graph tools
_GRAPH: Any = None


def _get_graph() -> Any:
    """Return the global SocialGraph instance."""
    global _GRAPH
    if _GRAPH is None:
        from codomyrmex.relations.network_analysis.graph import SocialGraph

        _GRAPH = SocialGraph()
    return _GRAPH


def _reset_graph() -> None:
    """Reset the global SocialGraph (useful for testing)."""
    global _GRAPH
    _GRAPH = None


@mcp_tool(
    category="relations_network_analysis",
    description="Add a relationship edge between two entities in the social graph.",
)
def network_analysis_add_edge(
    source: str,
    target: str,
    weight: float = 1.0,
) -> dict[str, Any]:
    """Record an interaction or relationship edge between two entities.

    Args:
        source: First entity ID.
        target: Second entity ID.
        weight: Interaction strength (default 1.0).

    Returns:
        Confirmation status dict.

    """
    try:
        graph = _get_graph()
        graph.add_edge(source, target, weight=weight)
        return {
            "status": "success",
            "message": f"Edge added between '{source}' and '{target}' with weight {weight}.",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="relations_network_analysis",
    description="Calculate degree centrality for all entities in the graph.",
)
def network_analysis_calculate_centrality() -> dict[str, Any]:
    """Retrieve degree centrality scores across the social network.

    Returns:
        Centrality scores mapped by entity ID.

    """
    try:
        graph = _get_graph()
        centrality = graph.calculate_centrality()
        return {"status": "success", "centrality_scores": centrality}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="relations_network_analysis",
    description="Find communities in the social graph using label propagation.",
)
def network_analysis_find_communities() -> dict[str, Any]:
    """Detect clustered sub-communities within the social graph.

    Returns:
        A list of community sets, where each set is a list of entity IDs.

    """
    try:
        graph = _get_graph()
        communities = graph.find_communities()
        return {
            "status": "success",
            "communities": [list(c) for c in communities],
            "count": len(communities),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
