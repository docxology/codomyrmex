"""
Graph RAG Pipeline

RAG pipeline enhanced with knowledge graph context.
"""

from collections.abc import Callable

from .graph import KnowledgeGraph
from .models import GraphContext


class GraphRAGPipeline:
    """
    RAG pipeline enhanced with knowledge graph context.

    Usage:
        pipeline = GraphRAGPipeline(
            graph=knowledge_graph,
            embedding_fn=embed_function,
        )

        # Query with graph context
        context = pipeline.retrieve("Who is the CEO of Anthropic?")

        # Use context for generation
        print(context.to_text())
    """

    def __init__(
        self,
        graph: KnowledgeGraph,
        embedding_fn: Callable[[list[str]], list[list[float]]] | None = None,
    ):
        """Initialize this instance."""
        self.graph = graph
        self.embedding_fn = embedding_fn

    def extract_entities(self, query: str) -> list[str]:
        """Extract entity IDs mentioned in query (simple word matching)."""
        query_words = set(query.lower().split())
        matches = []

        for entity in self.graph._entities.values():
            name_words = set(entity.name.lower().split())
            if name_words & query_words:
                matches.append(entity.id)

        return matches

    def retrieve(
        self,
        query: str,
        max_entities: int = 10,
        include_neighbors: bool = True,
        max_depth: int = 2,
    ) -> GraphContext:
        """
        Retrieve graph context for a query.

        Args:
            query: Search query
            max_entities: Maximum entities to include
            include_neighbors: Whether to include related entities
            max_depth: Max depth for neighbor expansion

        Returns:
            GraphContext with entities and relationships
        """
        # Find matching entities
        entity_ids = self.extract_entities(query)

        # Also do text search
        for entity in self.graph.search_entities(query, limit=5):
            if entity.id not in entity_ids:
                entity_ids.append(entity.id)

        # Expand to neighbors
        all_entity_ids = set(entity_ids[:max_entities])
        if include_neighbors:
            for eid in list(all_entity_ids):
                for neighbor in self.graph.get_neighbors(eid):
                    all_entity_ids.add(neighbor.id)
                    if len(all_entity_ids) >= max_entities:
                        break

        # Get entities
        entities = [
            self.graph.get_entity(eid)
            for eid in all_entity_ids
            if self.graph.get_entity(eid)
        ]

        # Get relationships between these entities
        relationships = []
        for r in self.graph._relationships:
            if r.source_id in all_entity_ids and r.target_id in all_entity_ids:
                relationships.append(r)

        return GraphContext(
            query=query,
            entities=entities,
            relationships=relationships,
        )

    def combine_context(
        self,
        graph_context: GraphContext,
        text_context: str,
    ) -> str:
        """Combine graph and text context for LLM."""
        return f"""{graph_context.to_text()}

Document Context:
{text_context}"""
