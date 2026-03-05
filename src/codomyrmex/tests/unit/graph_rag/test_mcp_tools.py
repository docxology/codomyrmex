import pytest

from codomyrmex.graph_rag.mcp_tools import (
    graph_rag_build_graph,
    graph_rag_list_types,
    graph_rag_search_entities,
)


class TestGraphRagMCPTools:
    def test_list_types(self):
        """Test listing graph types via MCP."""
        result = graph_rag_list_types()
        assert result["status"] == "success"
        assert "concept" in result["entity_types"]
        assert "related_to" in result["relation_types"]

    def test_build_graph(self):
        """Test building a graph via MCP."""
        entities = [
            {"id": "e1", "name": "Python", "entity_type": "concept"},
            {"id": "e2", "name": "Guido", "entity_type": "person"},
        ]
        relationships = [
            {"source_id": "e2", "target_id": "e1", "relation_type": "authored_by"}
        ]

        result = graph_rag_build_graph(entities=entities, relationships=relationships)
        assert result["status"] == "success"
        assert result["entity_count"] == 2
        assert result["relationship_count"] == 1
        assert len(result["entities"]) == 2

    def test_search_entities(self):
        """Test searching for entities via MCP."""
        entities = [
            {"id": "e1", "name": "Python Language", "entity_type": "concept"},
            {"id": "e2", "name": "Java Language", "entity_type": "concept"},
        ]

        result = graph_rag_search_entities(entities=entities, query="python")
        assert result["status"] == "success"
        assert result["match_count"] == 1
        assert result["matches"][0]["id"] == "e1"

    def test_search_with_filter(self):
        """Test searching with entity type filter."""
        entities = [
            {"id": "e1", "name": "Python Language", "entity_type": "concept"},
            {"id": "e2", "name": "Python Software Foundation", "entity_type": "organization"},
        ]

        # Matches the organization only
        result = graph_rag_search_entities(entities=entities, query="python", entity_type="organization")
        assert result["status"] == "success"
        assert result["match_count"] == 1
        assert result["matches"][0]["id"] == "e2"

    def test_tool_metadata(self):
        """Test that MCP tools have correct metadata."""
        assert hasattr(graph_rag_list_types, "_mcp_tool_meta")
        assert graph_rag_list_types._mcp_tool_meta["name"] == "codomyrmex.graph_rag_list_types"

        assert hasattr(graph_rag_build_graph, "_mcp_tool_meta")
        assert graph_rag_build_graph._mcp_tool_meta["name"] == "codomyrmex.graph_rag_build_graph"

        assert hasattr(graph_rag_search_entities, "_mcp_tool_meta")
        assert graph_rag_search_entities._mcp_tool_meta["name"] == "codomyrmex.graph_rag_search_entities"
