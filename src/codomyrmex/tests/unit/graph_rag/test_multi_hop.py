"""Tests for Multi-Hop Graph RAG Retrieval."""

from codomyrmex.graph_rag.graph import KnowledgeGraph
from codomyrmex.graph_rag.models import Entity, EntityType, Relationship, RelationType
from codomyrmex.graph_rag.pipeline import GraphRAGPipeline


class TestMultiHopRetrieval:
    def test_multi_hop_bfs(self):
        """Should retrieve entities at depth 2."""
        graph = KnowledgeGraph()

        # A -> B -> C
        graph.add_entity(Entity(id="A", name="Alpha", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="B", name="Beta", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="C", name="Gamma", entity_type=EntityType.CONCEPT))

        graph.add_relationship(Relationship("A", "B", RelationType.RELATED_TO))
        graph.add_relationship(Relationship("B", "C", RelationType.RELATED_TO))

        pipeline = GraphRAGPipeline(graph=graph)

        # Depth 1 should only get A and B
        context_d1 = pipeline.retrieve(
            "Alpha", include_neighbors=True, max_depth=1, max_entities=10
        )
        eids_d1 = [e.id for e in context_d1.entities]
        assert "A" in eids_d1
        assert "B" in eids_d1
        assert "C" not in eids_d1

        # Depth 2 should get A, B, and C
        context_d2 = pipeline.retrieve(
            "Alpha", include_neighbors=True, max_depth=2, max_entities=10
        )
        eids_d2 = [e.id for e in context_d2.entities]
        assert "A" in eids_d2
        assert "B" in eids_d2
        assert "C" in eids_d2
