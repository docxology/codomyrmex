"""Tests for graph_rag/agent_bridge.py."""

from __future__ import annotations

from codomyrmex.graph_rag.agent_bridge import (
    GraphRetriever,
    LinkedEntity,
)
from codomyrmex.graph_rag.graph import KnowledgeGraph
from codomyrmex.graph_rag.models import (
    Entity,
    EntityType,
    GraphContext,
    Relationship,
    RelationType,
)


def _make_test_graph() -> KnowledgeGraph:
    """Construct a small test knowledge graph."""
    g = KnowledgeGraph()
    g.add_entity(Entity(id="python", name="Python", entity_type=EntityType.CONCEPT))
    g.add_entity(Entity(id="ml", name="Machine Learning", entity_type=EntityType.CONCEPT))
    g.add_entity(Entity(id="pytorch", name="PyTorch", entity_type=EntityType.CONCEPT))
    g.add_entity(Entity(id="numpy", name="NumPy", entity_type=EntityType.CONCEPT))
    g.add_entity(Entity(id="guido", name="Guido van Rossum", entity_type=EntityType.PERSON))

    g.add_relationship(Relationship(
        source_id="python", target_id="ml", relation_type=RelationType.RELATED_TO
    ))
    g.add_relationship(Relationship(
        source_id="pytorch", target_id="ml", relation_type=RelationType.PART_OF
    ))
    g.add_relationship(Relationship(
        source_id="numpy", target_id="python", relation_type=RelationType.PART_OF
    ))
    g.add_relationship(Relationship(
        source_id="guido", target_id="python", relation_type=RelationType.AUTHORED_BY
    ))
    return g


class TestLinkedEntity:
    """Test suite for LinkedEntity."""
    def test_create(self) -> None:
        """Test functionality: create."""
        e = Entity(id="x", name="X")
        le = LinkedEntity(entity=e, matched_term="x")
        assert le.score == 1.0
        assert le.matched_term == "x"


class TestGraphRetriever:
    """Test suite for GraphRetriever."""
    def test_retrieve_basic(self) -> None:
        """Test functionality: retrieve basic."""
        g = _make_test_graph()
        r = GraphRetriever(g)
        ctx = r.retrieve("Python")
        assert isinstance(ctx, GraphContext)
        assert len(ctx.entities) >= 1
        names = [e.name for e in ctx.entities]
        assert "Python" in names

    def test_retrieve_returns_neighbors(self) -> None:
        """Test functionality: retrieve returns neighbors."""
        g = _make_test_graph()
        r = GraphRetriever(g, expand_neighbors=True)
        ctx = r.retrieve("Python")
        names = [e.name for e in ctx.entities]
        # Should include neighbors like ML, NumPy, Guido
        assert len(names) >= 2

    def test_retrieve_without_neighbors(self) -> None:
        """Test functionality: retrieve without neighbors."""
        g = _make_test_graph()
        r = GraphRetriever(g, expand_neighbors=False)
        ctx = r.retrieve("Python")
        # Without expansion, should be minimal
        assert len(ctx.entities) >= 1

    def test_retrieve_no_match(self) -> None:
        """Test functionality: retrieve no match."""
        g = _make_test_graph()
        r = GraphRetriever(g)
        ctx = r.retrieve("Quantum Computing")
        assert len(ctx.entities) == 0
        assert ctx.confidence == 0.0

    def test_retrieve_with_type_filter(self) -> None:
        """Test functionality: retrieve with type filter."""
        g = _make_test_graph()
        r = GraphRetriever(g)
        ctx = r.retrieve("Python", entity_type=EntityType.PERSON)
        # Should not match "Python" (CONCEPT) but might not match anything
        names = [e.name for e in ctx.entities]
        # Guido has "Python" substring? No. So empty.
        assert all(e.entity_type == EntityType.PERSON for e in ctx.entities)

    def test_confidence_positive(self) -> None:
        """Test functionality: confidence positive."""
        g = _make_test_graph()
        r = GraphRetriever(g)
        ctx = r.retrieve("Python machine learning")
        assert ctx.confidence > 0

    def test_relationships_populated(self) -> None:
        """Test functionality: relationships populated."""
        g = _make_test_graph()
        r = GraphRetriever(g, expand_neighbors=True)
        ctx = r.retrieve("Python")
        assert len(ctx.relationships) >= 1

    def test_limit_respected(self) -> None:
        """Test functionality: limit respected."""
        g = _make_test_graph()
        r = GraphRetriever(g, max_entities=2)
        ctx = r.retrieve("Python machine learning PyTorch")
        assert len(ctx.entities) <= 2

    def test_extract_terms(self) -> None:
        """Test functionality: extract terms."""
        terms = GraphRetriever._extract_terms("How do I use Python for machine learning?")
        assert "python" in terms
        assert "machine" in terms
        assert "learning" in terms
        # Should also have bigrams
        assert "machine learning" in terms
