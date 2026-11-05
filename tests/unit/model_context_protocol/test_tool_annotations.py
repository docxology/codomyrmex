"""MCP behavior hints survive registration and discovery without authorizing tools."""

import asyncio
from types import ModuleType

import pytest

from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.model_context_protocol.discovery import MCPDiscovery
from codomyrmex.model_context_protocol.schemas.mcp_schemas import (
    MCPRegistrationError,
    MCPToolRegistry,
)
from codomyrmex.model_context_protocol.tool_annotations import (
    normalize_tool_annotations,
)
from codomyrmex.model_context_protocol.transport.server import MCPServer

DEFAULTS = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": False,
    "openWorldHint": True,
}
READ_ONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}


def test_defaults_are_explicit_and_independent_copies() -> None:
    first = normalize_tool_annotations()
    first["readOnlyHint"] = True
    assert normalize_tool_annotations() == DEFAULTS


@pytest.mark.parametrize("hint", list(DEFAULTS))
@pytest.mark.parametrize("value", ["false", 0, 1, [], None])
def test_behavior_hints_require_real_booleans(hint: str, value: object) -> None:
    with pytest.raises(ValueError, match="must be a boolean"):
        normalize_tool_annotations({hint: value})


@pytest.mark.parametrize(
    "annotations",
    [[], "readOnlyHint", {"readonlyHint": True}, {"title": False}],
)
def test_invalid_annotation_shapes_fail_explicitly(annotations: object) -> None:
    with pytest.raises(ValueError):
        normalize_tool_annotations(annotations)


def test_partial_hints_fill_only_omitted_fields() -> None:
    assert normalize_tool_annotations({"openWorldHint": False, "title": "Lookup"}) == {
        **DEFAULTS,
        "openWorldHint": False,
        "title": "Lookup",
    }


def test_decorator_discovery_and_server_retain_declared_hints() -> None:
    declared = dict(READ_ONLY)

    @mcp_tool(annotations=declared)
    def lookup(value: str) -> str:
        return value

    declared["openWorldHint"] = True
    module = ModuleType("annotation_test_module")
    module.lookup = lookup
    discovered = MCPDiscovery()._scan_module(module)
    assert len(discovered) == 1
    tool = discovered[0]
    schema = tool.to_mcp_schema()
    assert schema["annotations"] == READ_ONLY
    schema["annotations"]["readOnlyHint"] = False
    assert tool.to_mcp_schema()["annotations"] == READ_ONLY

    server = MCPServer()
    server.register_tool(tool.name, tool.to_mcp_schema(), lookup)
    listed = asyncio.run(server._list_tools({}))["tools"]
    assert listed[0]["annotations"] == READ_ONLY
    assert lookup("legitimate") == "legitimate"
    # Behavior hints must not rewrite the separate PAI destructive marker.
    assert lookup._mcp_tool_meta["destructive"] is None


def test_unannotated_decorator_and_manual_registration_are_conservative() -> None:
    @mcp_tool(name="read_safe_sounding_name", destructive=False)
    def read_safe_sounding_name() -> str:
        return "ok"

    registry = MCPToolRegistry()
    schema = {"name": "read_safe_sounding_name", "inputSchema": {"type": "object"}}
    registry.register("read_safe_sounding_name", schema, read_safe_sounding_name)
    assert registry.get("read_safe_sounding_name")["schema"]["annotations"] == DEFAULTS
    assert "annotations" not in schema
    # A repeat using the original schema remains idempotent after normalization.
    registry.register("read_safe_sounding_name", schema, read_safe_sounding_name)


def test_registry_hints_are_copied_and_explicit_schema_takes_precedence() -> None:
    @mcp_tool(annotations=READ_ONLY)
    def lookup() -> str:
        return "ok"

    schema = {"annotations": {"openWorldHint": False}}
    registry = MCPToolRegistry()
    registry.register("lookup", schema, lookup)
    schema["annotations"]["readOnlyHint"] = True
    exposed = registry.get("lookup")
    assert exposed["schema"]["annotations"] == {**DEFAULTS, "openWorldHint": False}
    exposed["schema"]["annotations"]["destructiveHint"] = False
    assert registry.get("lookup")["schema"]["annotations"]["destructiveHint"] is True


def test_registry_rejects_invalid_hints_before_registration() -> None:
    registry = MCPToolRegistry()
    with pytest.raises(MCPRegistrationError, match="must be a boolean"):
        registry.register("unsafe", {"annotations": {"readOnlyHint": "false"}})
    assert registry.list_tools() == []


def test_server_decorator_accepts_explicit_hints() -> None:
    server = MCPServer()

    @server.tool(annotations=READ_ONLY)
    def lookup() -> str:
        return "ok"

    assert asyncio.run(server._list_tools({}))["tools"][0]["annotations"] == READ_ONLY


def test_pai_registry_preserves_hints_before_trust_wrapping() -> None:
    from codomyrmex.agents.pai.mcp.server import _ToolRegistry

    @mcp_tool(annotations=READ_ONLY, destructive=True)
    def lookup() -> str:
        return "ok"

    registry = _ToolRegistry()
    registry.register(tool_name="lookup", schema={"name": "lookup"}, handler=lookup)
    assert registry.get("lookup")["schema"]["annotations"] == READ_ONLY
    assert lookup._mcp_tool_meta["destructive"] is True


def test_http_discovery_preserves_hints() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    server = MCPServer()
    server.register_tool(
        "lookup", {"name": "lookup"}, lambda: "ok", annotations=READ_ONLY
    )
    with TestClient(server._create_http_app()) as client:
        response = client.get("/tools")
        assert response.status_code == 200
        assert response.json()["tools"][0]["annotations"] == READ_ONLY
