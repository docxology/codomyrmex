"""Strictly zero-mock tests for relations MCP tools.

Tests cover crm, network_analysis, uor, and social_media mcp tools.
"""

from __future__ import annotations

import pytest

# crm
from codomyrmex.relations.crm.mcp_tools import (
    _reset_manager,
    crm_add_contact,
    crm_add_interaction,
    crm_search_contacts,
)

# network_analysis
from codomyrmex.relations.network_analysis.mcp_tools import (
    _reset_graph,
    network_analysis_add_edge,
    network_analysis_calculate_centrality,
    network_analysis_find_communities,
)

# social_media
from codomyrmex.relations.social_media.mcp_tools import (
    social_media_analyze_sentiment,
)

# uor
from codomyrmex.relations.uor.mcp_tools import (
    _reset_uor_graph,
    uor_add_entity,
    uor_find_path,
)


@pytest.fixture(autouse=True)
def _reset_state():
    """Reset global state before and after each test."""
    _reset_manager()
    _reset_graph()
    _reset_uor_graph()
    yield
    _reset_manager()
    _reset_graph()
    _reset_uor_graph()


def test_crm_tools():
    """Test CRM MCP tools with real ContactManager."""
    # 1. Add contact
    res_add = crm_add_contact("Alice Example", "alice@example.com", ["vip"])
    assert res_add["status"] == "ok"
    contact_id = res_add["contact"]["id"]
    assert res_add["contact"]["name"] == "Alice Example"

    # 2. Search contact
    res_search = crm_search_contacts("alice")
    assert res_search["status"] == "ok"
    assert res_search["count"] == 1
    assert res_search["results"][0]["id"] == contact_id

    # 3. Add interaction
    res_int = crm_add_interaction(contact_id, "email", "Sent a welcome email")
    assert res_int["status"] == "ok"
    assert res_int["interaction"]["type"] == "email"

    # 4. Add interaction to non-existent contact
    res_err = crm_add_interaction("invalid-id", "email", "Test")
    assert res_err["status"] == "error"


def test_network_analysis_tools():
    """Test Network Analysis MCP tools with real SocialGraph."""
    # 1. Add edges
    res_edge1 = network_analysis_add_edge("Alice", "Bob", weight=2.0)
    assert res_edge1["status"] == "ok"

    res_edge2 = network_analysis_add_edge("Bob", "Charlie", weight=1.0)
    assert res_edge2["status"] == "ok"

    # 2. Centrality
    res_cent = network_analysis_calculate_centrality()
    assert res_cent["status"] == "ok"
    scores = res_cent["centrality_scores"]
    assert scores["Bob"] > scores["Alice"]
    assert scores["Bob"] > scores["Charlie"]

    # 3. Communities
    res_comm = network_analysis_find_communities()
    assert res_comm["status"] == "ok"
    assert res_comm["count"] > 0
    assert "Bob" in [node for c in res_comm["communities"] for node in c]


def test_uor_tools():
    """Test UOR MCP tools with real UORGraph."""
    # 1. Add entities
    res_a = uor_add_entity("Entity A", "test", {"value": 1})
    assert res_a["status"] == "ok"
    id_a = res_a["entity"]["id"]

    res_b = uor_add_entity("Entity B", "test", {"value": 2})
    assert res_b["status"] == "ok"
    id_b = res_b["entity"]["id"]

    # 2. Find path (no path exists yet)
    res_path_empty = uor_find_path(id_a, id_b)
    assert res_path_empty["status"] == "ok"
    assert res_path_empty.get("message") == "No path found."

    # NOTE: uor_add_relationship tool would connect them, but we haven't implemented it.
    # The requirement is just zero-mock testing what we have.


def test_social_media_tools():
    """Test social media mock MCP tool."""
    res_pos = social_media_analyze_sentiment("I love this!")
    assert res_pos["status"] == "ok"
    assert res_pos["label"] == "positive"

    res_neg = social_media_analyze_sentiment("This is bad.")
    assert res_neg["status"] == "ok"
    assert res_neg["label"] == "negative"

    res_neu = social_media_analyze_sentiment("Just regular text.")
    assert res_neu["status"] == "ok"
    assert res_neu["label"] == "neutral"
