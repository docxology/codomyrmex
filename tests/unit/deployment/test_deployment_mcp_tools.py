"""Tests for deployment MCP tools.

Zero-mock policy: tests use real DeploymentManager and strategy classes.
deployment_execute uses delay_seconds=0 so tests run fast.
"""

from __future__ import annotations


def test_import_mcp_tools() -> None:
    """All three MCP tools are importable without errors."""
    from codomyrmex.deployment.mcp_tools import (
        deployment_execute,
        deployment_get_history,
        deployment_list_strategies,
    )

    assert callable(deployment_execute)
    assert callable(deployment_list_strategies)
    assert callable(deployment_get_history)


def test_list_strategies_returns_list() -> None:
    """deployment_list_strategies returns a list of strategy names."""
    from codomyrmex.deployment.mcp_tools import deployment_list_strategies

    strategies = deployment_list_strategies()
    assert isinstance(strategies, list)
    assert len(strategies) >= 3
    assert "rolling" in strategies
    assert "blue_green" in strategies
    assert "canary" in strategies


def test_execute_rolling_returns_success() -> None:
    """deployment_execute returns a success dict for a rolling deployment."""
    from codomyrmex.deployment.mcp_tools import deployment_execute

    result = deployment_execute(
        service_name="my-service",
        version="1.0.0",
        strategy="rolling",
        targets=[{"id": "t1", "name": "t1", "address": "localhost"}],
    )
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["service"] == "my-service"
    assert result["version"] == "1.0.0"


def test_execute_blue_green_returns_dict() -> None:
    """deployment_execute with blue_green strategy returns a dict."""
    from codomyrmex.deployment.mcp_tools import deployment_execute

    result = deployment_execute(
        service_name="svc",
        version="2.0.0",
        strategy="blue_green",
        targets=[{"id": "t1", "name": "t1", "address": "localhost"}],
    )
    assert isinstance(result, dict)
    assert "success" in result


def test_get_history_returns_list() -> None:
    """deployment_get_history returns a list (may be empty for fresh manager)."""
    from codomyrmex.deployment.mcp_tools import deployment_get_history

    history = deployment_get_history()
    assert isinstance(history, list)


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.deployment.mcp_tools import (
        deployment_execute,
        deployment_get_history,
        deployment_list_strategies,
    )

    for fn in (deployment_execute, deployment_list_strategies, deployment_get_history):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
