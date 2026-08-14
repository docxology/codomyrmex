"""Regression tests for MCP registry result and async-handler boundaries."""

import asyncio

from codomyrmex.model_context_protocol.schemas.mcp_schemas import (
    MCPToolCall,
    MCPToolRegistry,
)


def test_async_handler_is_awaited_in_sync_registry_execution() -> None:
    registry = MCPToolRegistry()

    async def handler(value: int) -> dict[str, int]:
        await asyncio.sleep(0)
        return {"value": value}

    registry.register(
        "async_tool",
        {"type": "object", "properties": {"value": {"type": "integer"}}},
        handler,
    )

    result = registry.execute(
        MCPToolCall(tool_name="async_tool", arguments={"value": 7})
    )

    assert result.status == "success"
    assert result.data == {"result": {"value": 7}}


def test_partial_and_success_with_error_are_not_false_successes() -> None:
    registry = MCPToolRegistry()

    def partial() -> dict[str, str]:
        return {"status": "partial", "message": "incomplete"}

    registry.register("partial_tool", {"type": "object"}, partial)
    partial_result = registry.execute(
        MCPToolCall(tool_name="partial_tool", arguments={})
    )
    assert partial_result.status == "failure"
    assert partial_result.error is not None

    def success_with_error() -> dict[str, object]:
        return {"status": "success", "error": "side effect failed"}

    registry.register("error_tool", {"type": "object"}, success_with_error)
    error_result = registry.execute(MCPToolCall(tool_name="error_tool", arguments={}))
    assert error_result.status == "failure"
    assert error_result.error is not None

    def ok_with_error() -> dict[str, object]:
        return {"status": "ok", "error": "postcondition failed"}

    registry.register("ok_error_tool", {"type": "object"}, ok_with_error)
    ok_error_result = registry.execute(
        MCPToolCall(tool_name="ok_error_tool", arguments={})
    )
    assert ok_error_result.status == "failure"
    assert ok_error_result.error is not None
