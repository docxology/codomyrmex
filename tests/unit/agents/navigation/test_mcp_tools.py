"""MCP-level tests for navigation without live provider activity."""

from codomyrmex.agents.navigation.mcp_tools import (
    agent_operability_status,
    get_agent_capability,
    list_agent_capabilities,
    search_agent_capabilities,
)


def test_list_navigation_capabilities():
    result = list_agent_capabilities(kind="agent", limit=3)
    assert result["status"] == "success"
    assert result["count"] == 3
    assert all(item["kind"] == "agent" for item in result["capabilities"])


def test_search_navigation_capabilities():
    result = search_agent_capabilities("claude", kind="agent", limit=3)
    assert result["status"] == "success"
    assert result["capabilities"][0]["id"] == "agent:claude"


def test_get_navigation_capability_not_found_is_structured():
    result = get_agent_capability("agent:not-real")
    assert result["status"] == "error"
    assert result["error_code"] == "CAPABILITY_NOT_FOUND"


def test_navigation_rejects_malformed_inputs_structurally():
    assert list_agent_capabilities(limit="3")["error_code"] == "INVALID_INPUT"
    assert list_agent_capabilities(kind="unknown")["error_code"] == "INVALID_KIND"
    assert (
        list_agent_capabilities(include_unavailable="yes")["error_code"]
        == "INVALID_INPUT"
    )
    assert search_agent_capabilities("!!!")["error_code"] == "INVALID_QUERY"
    assert (
        get_agent_capability("agent:claude", kind="unknown")["error_code"]
        == "INVALID_KIND"
    )
    assert get_agent_capability(None)["error_code"] == "INVALID_CAPABILITY_ID"
    assert (
        agent_operability_status(include_tools="yes")["error_code"] == "INVALID_INPUT"
    )


def test_operability_status_is_explicitly_probe_free():
    result = agent_operability_status()
    assert result["status"] in {"success", "degraded"}
    assert result["probe_policy"] == "no live probes performed"
    assert result["implementation_present_agents"] > 0
    assert result["dispatchability_verified"] is False
    assert result["verified_dispatchable_agents"] == 0
    assert "unverified" in result["dispatchability_note"]
    assert result["declared_agents"] >= result["implementation_present_agents"]
