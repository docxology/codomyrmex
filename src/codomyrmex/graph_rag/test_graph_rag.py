"""
Tests for Graph RAG Module
"""

import pytest
from codomyrmex.graph_rag import (
    EntityType,
    RelationType,
    Entity,
    Relationship,
    GraphContext,
    KnowledgeGraph,
    GraphRAGPipeline,
)


class TestEntity:
    """Tests for Entity."""
    
    def test_create(self):
        """Should create entity."""
        e = Entity(id="python", name="Python", entity_type=EntityType.CONCEPT)
        assert e.id == "python"
        assert e.key == "concept:python"
    
    def test_to_dict(self):
        """Should convert to dict."""
        e = Entity(id="test", name="Test", properties={"key": "value"})
        d = e.to_dict()
        assert d["id"] == "test"
        assert d["properties"]["key"] == "value"


class TestRelationship:
    """Tests for Relationship."""
    
    def test_create(self):
        """Should create relationship."""
        r = Relationship(
            source_id="a",
            target_id="b",
            relation_type=RelationType.RELATED_TO,
        )
        assert "a" in r.key
        assert "b" in r.key


class TestKnowledgeGraph:
    """Tests for KnowledgeGraph."""
    
    def test_add_entity(self):
        """Should add entity."""
        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="python", name="Python"))
        
        assert graph.entity_count == 1
        assert graph.get_entity("python").name == "Python"
    
    def test_add_relationship(self):
        """Should add relationship."""
        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="a", name="A"))
        graph.add_entity(Entity(id="b", name="B"))
        graph.add_relationship(Relationship("a", "b", RelationType.RELATED_TO))
        
        assert graph.relationship_count == 1
    
    def test_get_neighbors(self):
        """Should get neighbors."""
        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="a", name="A"))
        graph.add_entity(Entity(id="b", name="B"))
        graph.add_entity(Entity(id="c", name="C"))
        graph.add_relationship(Relationship("a", "b", RelationType.RELATED_TO))
        graph.add_relationship(Relationship("a", "c", RelationType.RELATED_TO))
        
        neighbors = graph.get_neighbors("a", direction="out")
        assert len(neighbors) == 2
    
    def test_find_path(self):
        """Should find path."""
        graph = KnowledgeGraph()
        for name in ["a", "b", "c"]:
            graph.add_entity(Entity(id=name, name=name.upper()))
        graph.add_relationship(Relationship("a", "b", RelationType.RELATED_TO))
        graph.add_relationship(Relationship("b", "c", RelationType.RELATED_TO))
        
        path = graph.find_path("a", "c")
        assert path == ["a", "b", "c"]
    
    def test_search_entities(self):
        """Should search entities."""
        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="py", name="Python Programming"))
        graph.add_entity(Entity(id="java", name="Java Programming"))
        
        results = graph.search_entities("python")
        assert len(results) == 1
        assert results[0].id == "py"
    
    def test_subgraph(self):
        """Should extract subgraph."""
        graph = KnowledgeGraph()
        for name in ["a", "b", "c"]:
            graph.add_entity(Entity(id=name, name=name))
        graph.add_relationship(Relationship("a", "b", RelationType.RELATED_TO))
        
        sg = graph.subgraph(["a"], include_neighbors=True)
        assert sg.entity_count == 2


class TestGraphContext:
    """Tests for GraphContext."""
    
    def test_to_text(self):
        """Should convert to text."""
        ctx = GraphContext(
            query="test",
            entities=[Entity(id="a", name="Test Entity")],
            relationships=[Relationship("a", "b", RelationType.RELATED_TO)],
        )
        text = ctx.to_text()
        assert "Test Entity" in text
        assert "related_to" in text


class TestGraphRAGPipeline:
    """Tests for GraphRAGPipeline."""
    
    def test_retrieve(self):
        """Should retrieve context."""
        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="python", name="Python"))
        graph.add_entity(Entity(id="ml", name="Machine Learning"))
        graph.add_relationship(Relationship("python", "ml", RelationType.RELATED_TO))
        
        pipeline = GraphRAGPipeline(graph=graph)
        context = pipeline.retrieve("Python programming")
        
        assert len(context.entities) >= 1
    
    def test_combine_context(self):
        """Should combine contexts."""
        graph = KnowledgeGraph()
        pipeline = GraphRAGPipeline(graph=graph)
        
        graph_ctx = GraphContext(query="test", entities=[], relationships=[])
        combined = pipeline.combine_context(graph_ctx, "Document text here")
        
        assert "Document Context" in combined


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
