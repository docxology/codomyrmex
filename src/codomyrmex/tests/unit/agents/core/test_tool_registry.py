"""
Unit tests for agents.core.registry — Zero-Mock compliant.

Covers: Tool dataclass, ToolRegistry (register, register_function,
get_tool, list_tools, get_schemas, execute, from_mcp).
"""

import pytest

from codomyrmex.agents.core.registry import Tool, ToolRegistry

# ── Helpers ────────────────────────────────────────────────────────────────


def _add(x: int, y: int) -> int:
    """Add two integers."""
    return x + y


def _greet(name: str) -> str:
    """Return a greeting."""
    return f"hello {name}"


def _typed_all(a: int, b: float, c: bool, d: dict, e: list) -> str:
    return f"{a} {b} {c} {d} {e}"


def _make_tool(name="tool1", description="desc") -> Tool:
    def fn(**kwargs):
        return "ok"

    return Tool(
        name=name,
        func=fn,
        description=description,
        args_schema={"type": "object", "properties": {}},
    )


# ── Tool dataclass ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestTool:
    def test_to_schema_structure(self):
        tool = _make_tool("mytool", "does stuff")
        schema = tool.to_schema()
        assert schema["name"] == "mytool"
        assert schema["description"] == "does stuff"
        assert "parameters" in schema

    def test_return_schema_default_none(self):
        tool = _make_tool()
        assert tool.return_schema is None

    def test_return_schema_explicit(self):
        tool = Tool(
            name="t",
            func=lambda: None,
            description="d",
            args_schema={},
            return_schema={"type": "string"},
        )
        assert tool.return_schema == {"type": "string"}


# ── ToolRegistry — register / get / list ───────────────────────────────────


@pytest.mark.unit
class TestToolRegistryBasic:
    def test_starts_empty(self):
        reg = ToolRegistry()
        assert reg.list_tools() == []

    def test_register_and_get(self):
        reg = ToolRegistry()
        tool = _make_tool("t1")
        reg.register(tool)
        assert reg.get_tool("t1") is tool

    def test_get_missing_returns_none(self):
        reg = ToolRegistry()
        assert reg.get_tool("nonexistent") is None

    def test_list_tools_returns_all(self):
        reg = ToolRegistry()
        reg.register(_make_tool("a"))
        reg.register(_make_tool("b"))
        names = {t.name for t in reg.list_tools()}
        assert names == {"a", "b"}

    def test_overwrite_existing_tool(self):
        reg = ToolRegistry()
        reg.register(_make_tool("t"))
        new_tool = _make_tool("t")
        reg.register(new_tool)
        # Overwrites silently (logs warning) — should still be registered
        assert reg.get_tool("t") is new_tool

    def test_get_schemas_structure(self):
        reg = ToolRegistry()
        reg.register(_make_tool("s1", "schema tool"))
        schemas = reg.get_schemas()
        assert len(schemas) == 1
        assert schemas[0]["name"] == "s1"
        assert schemas[0]["description"] == "schema tool"

    def test_get_schemas_empty(self):
        reg = ToolRegistry()
        assert reg.get_schemas() == []


# ── ToolRegistry — register_function ──────────────────────────────────────


@pytest.mark.unit
class TestToolRegistryRegisterFunction:
    def test_register_plain_function(self):
        reg = ToolRegistry()
        reg.register_function(_add)
        assert reg.get_tool("_add") is not None

    def test_custom_name(self):
        reg = ToolRegistry()
        reg.register_function(_greet, name="greeter")
        assert reg.get_tool("greeter") is not None

    def test_custom_description(self):
        reg = ToolRegistry()
        reg.register_function(_greet, description="my custom desc")
        tool = reg.get_tool("_greet")
        assert tool.description == "my custom desc"

    def test_docstring_becomes_description(self):
        reg = ToolRegistry()
        reg.register_function(_add)
        tool = reg.get_tool("_add")
        assert tool.description == "Add two integers."

    def test_required_params_detected(self):
        reg = ToolRegistry()
        reg.register_function(_add)
        tool = reg.get_tool("_add")
        required = tool.args_schema.get("required", [])
        assert "x" in required
        assert "y" in required

    def test_int_type_annotation_mapped(self):
        reg = ToolRegistry()
        reg.register_function(_add)
        tool = reg.get_tool("_add")
        props = tool.args_schema["properties"]
        assert props["x"]["type"] == "integer"
        assert props["y"]["type"] == "integer"

    def test_all_type_annotations_mapped(self):
        reg = ToolRegistry()
        reg.register_function(_typed_all)
        tool = reg.get_tool("_typed_all")
        props = tool.args_schema["properties"]
        assert props["a"]["type"] == "integer"
        assert props["b"]["type"] == "number"
        assert props["c"]["type"] == "boolean"
        assert props["d"]["type"] == "object"
        assert props["e"]["type"] == "array"

    def test_unannotated_param_defaults_to_string(self):
        def fn(x, y):
            pass

        reg = ToolRegistry()
        reg.register_function(fn)
        tool = reg.get_tool("fn")
        props = tool.args_schema["properties"]
        assert props["x"]["type"] == "string"
        assert props["y"]["type"] == "string"


# ── ToolRegistry — execute ────────────────────────────────────────────────


@pytest.mark.unit
class TestToolRegistryExecute:
    def test_execute_registered_function(self):
        reg = ToolRegistry()
        reg.register_function(_add)
        result = reg.execute("_add", x=3, y=4)
        assert result == 7

    def test_execute_greet(self):
        reg = ToolRegistry()
        reg.register_function(_greet)
        result = reg.execute("_greet", name="world")
        assert result == "hello world"

    def test_execute_missing_tool_raises(self):
        reg = ToolRegistry()
        with pytest.raises(ValueError, match="not found"):
            reg.execute("ghost")

    def test_execute_via_tool_object(self):
        reg = ToolRegistry()
        captured = {}

        def fn(val):
            captured["val"] = val

        tool = Tool(
            name="capture",
            func=fn,
            description="captures",
            args_schema={},
        )
        reg.register(tool)
        reg.execute("capture", val="test123")
        assert captured["val"] == "test123"


# ── ToolRegistry — from_mcp ────────────────────────────────────────────────


@pytest.mark.unit
class TestToolRegistryFromMcp:
    class _FakeMCPTool:
        def __init__(self, name, handler=None):
            self.name = name
            self.description = f"desc for {name}"
            self.handler = handler
            self.input_schema = {"type": "object", "properties": {}}

    class _FakeMCPRegistry:
        def __init__(self, tools):
            self._tools = tools

        def list_tools(self):
            return self._tools

    def test_from_mcp_creates_registry(self):
        mcp_tools = [
            self._FakeMCPTool("tool_a", handler=lambda: "a"),
            self._FakeMCPTool("tool_b", handler=lambda: "b"),
        ]
        mcp_reg = self._FakeMCPRegistry(mcp_tools)
        reg = ToolRegistry.from_mcp(mcp_reg)
        assert reg.get_tool("tool_a") is not None
        assert reg.get_tool("tool_b") is not None

    def test_from_mcp_with_prefix(self):
        mcp_tools = [self._FakeMCPTool("ping", handler=lambda: "pong")]
        mcp_reg = self._FakeMCPRegistry(mcp_tools)
        reg = ToolRegistry.from_mcp(mcp_reg, prefix="mcp.")
        assert reg.get_tool("mcp.ping") is not None

    def test_from_mcp_skips_no_handler(self):
        mcp_tools = [self._FakeMCPTool("nohandler")]  # handler=None
        mcp_reg = self._FakeMCPRegistry(mcp_tools)
        reg = ToolRegistry.from_mcp(mcp_reg)
        assert reg.get_tool("nohandler") is None

    def test_from_mcp_raises_on_missing_list_tools(self):
        with pytest.raises(TypeError, match="list_tools"):
            ToolRegistry.from_mcp(object())

    def test_from_mcp_execute_handler(self):
        mcp_tools = [self._FakeMCPTool("double", handler=lambda x: x * 2)]
        mcp_reg = self._FakeMCPRegistry(mcp_tools)
        reg = ToolRegistry.from_mcp(mcp_reg)
        result = reg.execute("double", x=5)
        assert result == 10
