"""Integration tests for Gateway Tool Sandboxing (D2)."""

import pytest

from codomyrmex.agents.hermes.gateway.sandbox import (
    GatewayToolSandbox,
    SandboxViolation,
)


def mock_executor(name: str, args: dict) -> str:
    """Simulates a function that actually runs the tool."""
    # In a true zero-mock gateway, this would be `tool_registry.execute_tool(...)`.
    # For testing the sandbox isolation natively, we just return success if it gets here.
    return f"Executed {name} successfully"


def test_sandbox_blocks_unauthenticated_destruction() -> None:
    """Ensure an untrusted session cannot trigger run_command."""
    sandbox = GatewayToolSandbox(is_authenticated=False)

    # 1. Safe tool should pass
    safe_result = sandbox.wrap_execution(
        "search_web", {"query": "hello"}, mock_executor
    )
    assert safe_result == "Executed search_web successfully"

    # 2. Hostile tool should raise SandboxViolation
    with pytest.raises(SandboxViolation) as exc_info:
        sandbox.wrap_execution("run_command", {"command": "rm -rf /"}, mock_executor)

    assert "restricted" in str(exc_info.value).lower()


def test_sandbox_allows_authenticated_destruction() -> None:
    """Ensure an explicitly trusted (owner) session can trigger run_command."""
    sandbox = GatewayToolSandbox(is_authenticated=True)

    # Both pass
    sandbox.wrap_execution("search_web", {"query": "hello"}, mock_executor)

    dangerous_result = sandbox.wrap_execution(
        "run_command", {"command": "ls -la"}, mock_executor
    )
    assert dangerous_result == "Executed run_command successfully"
