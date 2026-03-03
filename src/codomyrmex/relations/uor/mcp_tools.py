"""MCP tool definitions for the Universal Object Reference (UOR) submodule.

Exposes entity creation and relationship pathfinding tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

_UOR_GRAPH: Any = None


def _get_uor_graph() -> Any:
    """Return the global UORGraph instance."""
    global _UOR_GRAPH
    if _UOR_GRAPH is None:
        from codomyrmex.relations.uor.graph import UORGraph

        _UOR_GRAPH = UORGraph(quantum=0)
    return _UOR_GRAPH


def _reset_uor_graph() -> None:
    """Reset the global UORGraph (useful for testing)."""
    global _UOR_GRAPH
    _UOR_GRAPH = None


@mcp_tool(
    category="relations_uor",
    description="Add or retrieve a UOR entity using its type and attributes.",
)
def uor_add_entity(
    name: str,
    entity_type: str,
    attributes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create and return a universal object reference entity.

    Args:
        name: Human-readable entity name.
        entity_type: Category (e.g., 'agent', 'document').
        attributes: Dictionary of properties.

    Returns:
        The registered UOREntity serialized as a dict.

    """
    try:
        graph = _get_uor_graph()
        entity = graph.add_entity(
            name=name,
            entity_type=entity_type,
            attributes=attributes or {},
        )
        return {"status": "ok", "entity": entity.to_dict()}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="relations_uor",
    description="Find the shortest relationship path between two entities in the UOR graph.",
)
def uor_find_path(
    source_id: str,
    target_id: str,
) -> dict[str, Any]:
    """Find the shortest BFS path between two entities.

    Args:
        source_id: Starting entity ID.
        target_id: Destination entity ID.

    Returns:
        A list of entity IDs defining the path.

    """
    try:
        graph = _get_uor_graph()
        path = graph.find_path(source_id, target_id)
        if not path:
            return {"status": "ok", "message": "No path found."}
        return {"status": "ok", "path": path}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
