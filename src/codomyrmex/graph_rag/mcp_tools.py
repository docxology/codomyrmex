"""
MCP Tools for Graph RAG

Provides Model Context Protocol tools for accessing knowledge graph features.
"""

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .graph import KnowledgeGraph
from .models import EntityType

# Since KnowledgeGraph is an in-memory instance, we need a way to maintain state
# or assume the tools interact with a global/singleton graph for the sake of the MCP tools.
# For standard MCP tool integrations where there's no stateful manager, we use a global instance.
_global_graph = KnowledgeGraph()


@mcp_tool(
    name="graph_rag_search_entities",
    description="Search the knowledge graph for entities matching a query string.",
    category="graph_rag",
)
def graph_rag_search_entities(
    query: str, entity_type: str | None = None
) -> list[dict[str, Any]]:
    """
    Search the knowledge graph for entities matching a query string.

    Args:
        query: The search query.
        entity_type: Optional filter by EntityType value (e.g. 'concept', 'person').

    Returns:
        A list of matching entity dictionaries.
    """
    et = None
    if entity_type:
        try:
            et = EntityType(entity_type)
        except ValueError:
            pass  # Invalid entity type, ignore filter or handle gracefully

    entities = _global_graph.search_entities(query, entity_type=et)
    return [e.to_dict() for e in entities]


@mcp_tool(
    name="graph_rag_get_stats",
    description="Get statistics about the current knowledge graph.",
    category="graph_rag",
)
def graph_rag_get_stats() -> dict[str, int]:
    """
    Get statistics about the current knowledge graph.

    Returns:
        A dictionary with 'entity_count' and 'relationship_count'.
    """
    return {
        "entity_count": len(_global_graph._entities),
        "relationship_count": len(_global_graph._relationships),
    }


@mcp_tool(
    name="graph_rag_get_neighbors",
    description="Get neighboring entities for a given entity ID.",
    category="graph_rag",
)
def graph_rag_get_neighbors(entity_id: str) -> list[dict[str, Any]]:
    """
    Get neighboring entities for a given entity ID.

    Args:
        entity_id: The ID of the entity.

    Returns:
        A list of neighboring entity dictionaries.
    """
    neighbors = _global_graph.get_neighbors(entity_id)
    return [n.to_dict() for n in neighbors]
