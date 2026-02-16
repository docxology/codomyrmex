"""
Graph RAG

Knowledge graph-enhanced retrieval-augmented generation.
"""

from .models import (
    EntityType,
    RelationType,
    Entity,
    Relationship,
    GraphContext,
)

from .graph import KnowledgeGraph

from .pipeline import GraphRAGPipeline

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the graph_rag module."""

    def _stats():
        """Show knowledge graph stats."""
        graph = KnowledgeGraph()
        print("Graph RAG Statistics")
        print(f"  Entity Types: {[et.value for et in EntityType]}")
        print(f"  Relation Types: {[rt.value for rt in RelationType]}")
        print(f"  Entities: {len(graph.entities)}")
        print(f"  Relationships: {len(graph.relationships)}")

    def _query(query: str = ""):
        """Query the knowledge graph with --query arg."""
        if not query:
            print("Usage: graph_rag query --query <search_term>")
            return
        graph = KnowledgeGraph()
        results = graph.search(query)
        if not results:
            print(f"No results found for: {query}")
        for entity in results:
            print(f"  [{entity.entity_type.value}] {entity.name}")

    return {
        "stats": _stats,
        "query": _query,
    }


__all__ = [
    # Models
    "EntityType",
    "RelationType",
    "Entity",
    "Relationship",
    "GraphContext",
    # Graph
    "KnowledgeGraph",
    # Pipeline
    "GraphRAGPipeline",
    # CLI
    "cli_commands",
]
