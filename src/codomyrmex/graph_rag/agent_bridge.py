"""Agent bridge for Graph-RAG knowledge retrieval.

Bridges the ``KnowledgeGraph`` to the agent reasoning loop by
providing query-based entity retrieval with entity linking and
context generation for LLM consumption.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.graph_rag.graph import KnowledgeGraph
from codomyrmex.graph_rag.models import (
    Entity,
    EntityType,
    GraphContext,
    Relationship,
    RelationType,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class LinkedEntity:
    """An entity linked from a query term.

    Attributes:
        entity: The matched graph entity.
        matched_term: The query term that matched.
        score: Matching confidence (0–1).
    """

    entity: Entity
    matched_term: str
    score: float = 1.0


class GraphRetriever:
    """Retrieves relevant entities and context from a KnowledgeGraph.

    Provides entity linking from natural-language queries to graph
    nodes, with context expansion via neighbor traversal.

    Usage::

        graph = KnowledgeGraph()
        # ... populate graph ...
        retriever = GraphRetriever(graph)
        context = retriever.retrieve("Python machine learning")
        print(context.to_text())
    """

    def __init__(
        self,
        graph: KnowledgeGraph,
        max_entities: int = 10,
        expand_neighbors: bool = True,
        max_depth: int = 2,
    ) -> None:
        """Initialize the retriever.

        Args:
            graph: The knowledge graph to query.
            max_entities: Maximum entities to return per query.
            expand_neighbors: Whether to include neighbor entities.
            max_depth: Maximum traversal depth for neighbor expansion.
        """
        self._graph = graph
        self._max_entities = max_entities
        self._expand_neighbors = expand_neighbors
        self._max_depth = max_depth

    def retrieve(
        self,
        query: str,
        entity_type: EntityType | None = None,
        k: int | None = None,
    ) -> GraphContext:
        """Retrieve relevant graph context for a query.

        Performs entity linking by splitting the query into terms,
        searching for matches in the graph, and expanding with
        neighbor entities.

        Args:
            query: Natural-language query.
            entity_type: Optional filter by entity type.
            k: Override max entities for this call.

        Returns:
            ``GraphContext`` with matched entities and relationships.
        """
        limit = k or self._max_entities

        logger.info(
            "GraphRetriever: querying",
            extra={"query": query[:100], "limit": limit},
        )

        # Phase 1: Entity linking — split query into terms and search
        linked = self._link_entities(query, entity_type, limit)

        # Phase 2: Expand with neighbors
        all_entities: dict[str, Entity] = {}
        all_relationships: list[Relationship] = []

        for le in linked:
            all_entities[le.entity.id] = le.entity

            if self._expand_neighbors:
                neighbors = self._graph.get_neighbors(le.entity.id)
                for n in neighbors[:3]:  # Limit neighbor expansion
                    all_entities[n.id] = n

                rels = self._graph.get_relationships(le.entity.id)
                all_relationships.extend(rels)

        # Phase 3: Find inter-entity paths
        entity_ids = list(all_entities.keys())
        paths: list[list[str]] = []
        if len(entity_ids) >= 2:
            for i in range(min(len(entity_ids) - 1, 3)):
                path = self._graph.find_path(
                    entity_ids[i], entity_ids[i + 1], self._max_depth
                )
                if path:
                    paths.append(path)

        # Compute confidence based on match quality
        confidence = (
            sum(le.score for le in linked) / len(linked)
            if linked else 0.0
        )

        context = GraphContext(
            query=query,
            entities=list(all_entities.values())[:limit],
            relationships=all_relationships,
            paths=paths,
            confidence=min(confidence, 1.0),
        )

        logger.info(
            "GraphRetriever: retrieved",
            extra={
                "entities": len(context.entities),
                "relationships": len(context.relationships),
                "confidence": round(context.confidence, 3),
            },
        )

        return context

    def _link_entities(
        self,
        query: str,
        entity_type: EntityType | None,
        limit: int,
    ) -> list[LinkedEntity]:
        """Link query terms to graph entities."""
        terms = self._extract_terms(query)
        linked: list[LinkedEntity] = []
        seen: set[str] = set()

        for term in terms:
            matches = self._graph.search_entities(
                term, entity_type=entity_type, limit=limit
            )
            for entity in matches:
                if entity.id not in seen:
                    seen.add(entity.id)
                    # Score: exact match > partial match
                    score = (
                        1.0 if term.lower() == entity.name.lower()
                        else 0.5 + 0.5 * (len(term) / max(len(entity.name), 1))
                    )
                    linked.append(LinkedEntity(
                        entity=entity,
                        matched_term=term,
                        score=min(score, 1.0),
                    ))

            if len(linked) >= limit:
                break

        # Sort by score descending
        linked.sort(key=lambda le: le.score, reverse=True)
        return linked[:limit]

    @staticmethod
    def _extract_terms(query: str) -> list[str]:
        """Extract search terms from a query.

        Splits on whitespace, filters short/stop words, returns
        individual terms plus any 2-gram phrases.
        """
        stop_words = {"the", "a", "an", "is", "are", "was", "were",
                      "in", "on", "at", "to", "for", "of", "and", "or",
                      "but", "not", "with", "from", "by", "as", "it",
                      "this", "that", "how", "what", "do", "i"}
        words = [w.strip(".,!?;:\"'()[]{}") for w in query.lower().split()]
        terms = [w for w in words if len(w) > 2 and w not in stop_words]

        # Add bigrams for better matching
        bigrams = [f"{terms[i]} {terms[i+1]}" for i in range(len(terms) - 1)]

        return terms + bigrams


__all__ = [
    "GraphRetriever",
    "LinkedEntity",
]
