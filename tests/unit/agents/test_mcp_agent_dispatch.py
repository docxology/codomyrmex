"""Regression tests for the public agent MCP dispatch contract."""

import os

from codomyrmex.agents.mcp_tools import execute_agent, list_agents


def test_unknown_agent_returns_structured_not_found_error():
    result = execute_agent("not-a-real-agent", "hello")
    assert result["status"] == "error"
    assert result["error_code"] == "AGENT_NOT_FOUND"


def test_configured_agent_path_reaches_client_construction():
    """A valid provider must not fail with the old missing-method AttributeError."""
    previous = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        result = execute_agent("claude", "hello")
    finally:
        if previous is not None:
            os.environ["ANTHROPIC_API_KEY"] = previous

    assert result["status"] == "error"
    assert result["error_code"] == "AGENT_EXECUTION_FAILED"
    assert "get_agent_config" not in result.get("message", "")


def test_list_agents_returns_json_safe_descriptors():
    result = list_agents()
    assert result["status"] == "success"
    assert result["count"] == len(result["agents"])
    assert result["agents"]
    assert all(isinstance(agent["name"], str) for agent in result["agents"])
    assert all("probe" not in agent for agent in result["agents"])
