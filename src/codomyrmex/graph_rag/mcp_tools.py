"""MCP tool definitions for the graph_rag module.

Exposes knowledge graph operations as MCP tools for agent consumption.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_graph():
    """Lazy import of KnowledgeGraph."""
    from codomyrmex.graph_rag.graph import KnowledgeGraph

    return KnowledgeGraph


def _get_models():
    """Lazy import of graph_rag models."""
    from codomyrmex.graph_rag import models

    return models


@mcp_tool(
    category="graph_rag",
    description="list available entity types and relation types in the knowledge graph.",
)
def graph_rag_list_types() -> dict[str, Any]:
    """list all supported entity and relation types.

    Returns:
        dict with keys: status, entity_types, relation_types
    """
    try:
        models = _get_models()
        return {
            "status": "success",
            "entity_types": [et.value for et in models.EntityType],
            "relation_types": [rt.value for rt in models.RelationType],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="graph_rag",
    description=(
        "Add entities and relationships to a knowledge graph, then return "
        "graph statistics. Operates on a fresh in-memory graph."
    ),
)
def graph_rag_build_graph(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a knowledge graph from entities and relationships.

    Args:
        entities: list of entity dicts with keys 'id', 'name', and optional
                  'entity_type' (person, organization, location, concept, event,
                  document, custom). Defaults to 'concept'.
        relationships: Optional list of relationship dicts with keys 'source_id',
                       'target_id', 'relation_type'. Defaults to 'related_to'.

    Returns:
        dict with keys: status, entity_count, relationship_count, entities
    """
    try:
        graph_cls = _get_graph()
        models = _get_models()
        graph = graph_cls()

        for ent in entities:
            et = models.EntityType(ent.get("entity_type", "concept"))
            entity = models.Entity(
                id=ent["id"],
                name=ent["name"],
                entity_type=et,
                properties=ent.get("properties", {}),
            )
            graph.add_entity(entity)

        if relationships:
            for rel in relationships:
                rt = models.RelationType(rel.get("relation_type", "related_to"))
                relationship = models.Relationship(
                    source_id=rel["source_id"],
                    target_id=rel["target_id"],
                    relation_type=rt,
                    weight=rel.get("weight", 1.0),
                )
                graph.add_relationship(relationship)

        entity_list = [
            graph.get_entity(eid).to_dict()
            for eid in [e["id"] for e in entities]
            if graph.get_entity(eid)
        ]

        return {
            "status": "success",
            "entity_count": graph.entity_count,
            "relationship_count": graph.relationship_count,
            "entities": entity_list,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="graph_rag",
    description=(
        "Search entities in a knowledge graph by name. "
        "Builds a graph from provided entities, then searches."
    ),
)
def graph_rag_search_entities(
    entities: list[dict[str, Any]],
    query: str,
    entity_type: str = "",
    limit: int = 10,
) -> dict[str, Any]:
    """Search entities in a knowledge graph by name.

    Args:
        entities: list of entity dicts to populate the graph (keys: id, name,
                  entity_type).
        query: Search query string matched against entity names.
        entity_type: Optional entity type filter.
        limit: Maximum results to return (default 10).

    Returns:
        dict with keys: status, query, match_count, matches
    """
    try:
        graph_cls = _get_graph()
        models = _get_models()
        graph = graph_cls()

        for ent in entities:
            et = models.EntityType(ent.get("entity_type", "concept"))
            entity = models.Entity(
                id=ent["id"],
                name=ent["name"],
                entity_type=et,
            )
            graph.add_entity(entity)

        et_filter = models.EntityType(entity_type) if entity_type else None
        results = graph.search_entities(query, entity_type=et_filter, limit=limit)

        matches = [e.to_dict() for e in results]

        return {
            "status": "success",
            "query": query,
            "match_count": len(matches),
            "matches": matches,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
