import pytest

from codomyrmex.graph_rag.mcp_tools import (
    _global_graph,
    graph_rag_get_neighbors,
    graph_rag_get_stats,
    graph_rag_search_entities,
)
from codomyrmex.graph_rag.models import Entity, EntityType, Relationship, RelationType


@pytest.fixture(autouse=True)
def reset_global_graph():
    """Reset the global knowledge graph before each test."""
    _global_graph._entities.clear()
    _global_graph._relationships.clear()
    _global_graph._adjacency.clear()
    _global_graph._reverse_adjacency.clear()


class TestGraphRagMCPTools:
    def test_search_entities_success(self):
        """Test searching for an entity that exists."""
        _global_graph.add_entity(Entity(id="e1", name="Python Language", entity_type=EntityType.CONCEPT))

        results = graph_rag_search_entities(query="python")
        assert len(results) == 1
        assert results[0]["id"] == "e1"
        assert results[0]["name"] == "Python Language"
        assert results[0]["entity_type"] == "concept"

    def test_search_entities_no_match(self):
        """Test searching for an entity that doesn't exist."""
        _global_graph.add_entity(Entity(id="e1", name="Python Language", entity_type=EntityType.CONCEPT))

        results = graph_rag_search_entities(query="java")
        assert len(results) == 0

    def test_search_entities_with_filter(self):
        """Test searching with an entity type filter."""
        _global_graph.add_entity(Entity(id="e1", name="Python", entity_type=EntityType.CONCEPT))
        _global_graph.add_entity(Entity(id="e2", name="Python Software Foundation", entity_type=EntityType.ORGANIZATION))

        # Search with matching filter
        results = graph_rag_search_entities(query="python", entity_type="organization")
        assert len(results) == 1
        assert results[0]["id"] == "e2"

        # Search with invalid filter (should ignore filter or return empty)
        # Assuming the code ignores an invalid filter based on try-except in implementation
        results_invalid = graph_rag_search_entities(query="python", entity_type="invalid_type")
        assert len(results_invalid) == 2

    def test_get_stats(self):
        """Test getting graph stats."""
        assert graph_rag_get_stats() == {"entity_count": 0, "relationship_count": 0}

        _global_graph.add_entity(Entity(id="e1", name="Python", entity_type=EntityType.CONCEPT))
        _global_graph.add_entity(Entity(id="e2", name="Guido", entity_type=EntityType.PERSON))
        _global_graph.add_relationship(Relationship("e2", "e1", RelationType.AUTHORED_BY))

        stats = graph_rag_get_stats()
        assert stats["entity_count"] == 2
        assert stats["relationship_count"] == 1

    def test_get_neighbors_success(self):
        """Test getting neighbors for an existing entity."""
        _global_graph.add_entity(Entity(id="e1", name="Node A"))
        _global_graph.add_entity(Entity(id="e2", name="Node B"))
        _global_graph.add_relationship(Relationship("e1", "e2", RelationType.RELATED_TO))

        neighbors = graph_rag_get_neighbors("e1")
        assert len(neighbors) == 1
        assert neighbors[0]["id"] == "e2"

    def test_get_neighbors_no_match(self):
        """Test getting neighbors for a non-existent entity."""
        neighbors = graph_rag_get_neighbors("invalid_id")
        assert len(neighbors) == 0

    def test_tool_metadata(self):
        """Test that MCP tools have correct metadata."""
        assert hasattr(graph_rag_search_entities, "_mcp_tool_meta")
        assert graph_rag_search_entities._mcp_tool_meta["name"] == "codomyrmex.graph_rag_search_entities"

        assert hasattr(graph_rag_get_stats, "_mcp_tool_meta")
        assert graph_rag_get_stats._mcp_tool_meta["name"] == "codomyrmex.graph_rag_get_stats"

        assert hasattr(graph_rag_get_neighbors, "_mcp_tool_meta")
        assert graph_rag_get_neighbors._mcp_tool_meta["name"] == "codomyrmex.graph_rag_get_neighbors"
