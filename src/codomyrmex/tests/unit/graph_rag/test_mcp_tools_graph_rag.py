"""Tests for graph_rag MCP tools.

Zero-mock tests validating the graph_rag MCP tool wrappers.
"""

from __future__ import annotations

SAMPLE_ENTITIES = [
    {"id": "python", "name": "Python", "entity_type": "concept"},
    {"id": "ai", "name": "Artificial Intelligence", "entity_type": "concept"},
    {"id": "anthropic", "name": "Anthropic", "entity_type": "organization"},
]

SAMPLE_RELATIONSHIPS = [
    {
        "source_id": "python",
        "target_id": "ai",
        "relation_type": "related_to",
    },
    {
        "source_id": "anthropic",
        "target_id": "ai",
        "relation_type": "related_to",
    },
]


class TestGraphRagListTypes:
    """Tests for graph_rag_list_types tool."""

    def test_returns_success_status(self):
        from codomyrmex.graph_rag.mcp_tools import graph_rag_list_types

        result = graph_rag_list_types()
        assert result["status"] == "success"

    def test_contains_entity_types(self):
        from codomyrmex.graph_rag.mcp_tools import graph_rag_list_types

        result = graph_rag_list_types()
        assert "entity_types" in result
        assert "person" in result["entity_types"]
        assert "concept" in result["entity_types"]
        assert "organization" in result["entity_types"]

    def test_contains_relation_types(self):
        from codomyrmex.graph_rag.mcp_tools import graph_rag_list_types

        result = graph_rag_list_types()
        assert "relation_types" in result
        assert "related_to" in result["relation_types"]
        assert "is_a" in result["relation_types"]


class TestGraphRagBuildGraph:
    """Tests for graph_rag_build_graph tool."""

    def test_build_graph_entities_only(self):
        from codomyrmex.graph_rag.mcp_tools import graph_rag_build_graph

        result = graph_rag_build_graph(entities=SAMPLE_ENTITIES)
        assert result["status"] == "success"
        assert result["entity_count"] == 3
        assert result["relationship_count"] == 0

    def test_build_graph_with_relationships(self):
        from codomyrmex.graph_rag.mcp_tools import graph_rag_build_graph

        result = graph_rag_build_graph(
            entities=SAMPLE_ENTITIES,
            relationships=SAMPLE_RELATIONSHIPS,
        )
        assert result["status"] == "success"
        assert result["entity_count"] == 3
        assert result["relationship_count"] == 2

    def test_build_graph_returns_entity_dicts(self):
        from codomyrmex.graph_rag.mcp_tools import graph_rag_build_graph

        result = graph_rag_build_graph(
            entities=[{"id": "test", "name": "Test Entity"}],
        )
        assert result["status"] == "success"
        assert len(result["entities"]) == 1
        assert result["entities"][0]["id"] == "test"
        assert result["entities"][0]["name"] == "Test Entity"

    def test_build_graph_invalid_entity_type_returns_error(self):
        from codomyrmex.graph_rag.mcp_tools import graph_rag_build_graph

        result = graph_rag_build_graph(
            entities=[{"id": "bad", "name": "Bad", "entity_type": "nonexistent"}],
        )
        assert result["status"] == "error"


class TestGraphRagSearchEntities:
    """Tests for graph_rag_search_entities tool."""

    def test_search_finds_matching_entity(self):
        from codomyrmex.graph_rag.mcp_tools import graph_rag_search_entities

        result = graph_rag_search_entities(
            entities=SAMPLE_ENTITIES,
            query="Python",
        )
        assert result["status"] == "success"
        assert result["match_count"] >= 1
        ids = [m["id"] for m in result["matches"]]
        assert "python" in ids

    def test_search_no_results(self):
        from codomyrmex.graph_rag.mcp_tools import graph_rag_search_entities

        result = graph_rag_search_entities(
            entities=SAMPLE_ENTITIES,
            query="xyznonexistent",
        )
        assert result["status"] == "success"
        assert result["match_count"] == 0

    def test_search_with_entity_type_filter(self):
        from codomyrmex.graph_rag.mcp_tools import graph_rag_search_entities

        result = graph_rag_search_entities(
            entities=SAMPLE_ENTITIES,
            query="Anthropic",
            entity_type="organization",
        )
        assert result["status"] == "success"
        assert result["match_count"] == 1
        assert result["matches"][0]["entity_type"] == "organization"

    def test_search_echoes_query(self):
        from codomyrmex.graph_rag.mcp_tools import graph_rag_search_entities

        result = graph_rag_search_entities(
            entities=SAMPLE_ENTITIES,
            query="Intelligence",
        )
        assert result["query"] == "Intelligence"
