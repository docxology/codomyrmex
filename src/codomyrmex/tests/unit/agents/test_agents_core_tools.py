
import pytest
from codomyrmex.agents.core import Tool, ToolRegistry

class TestToolRegistry:
    """Test tool registration and execution."""

    def test_register_tool(self):
        """Test registering a Tool instance."""
        registry = ToolRegistry()
        tool = Tool(
            name="test_tool",
            func=lambda x: x * 2,
            description="Double a number",
            args_schema={"type": "object", "properties": {"x": {"type": "integer"}}},
        )
        registry.register(tool)
        assert registry.get_tool("test_tool") is not None

    def test_register_function(self):
        """Test registering a function as a tool."""
        registry = ToolRegistry()

        def multiply(a: int, b: int) -> int:
            """Multiply two numbers."""
            return a * b

        registry.register_function(multiply)
        tool = registry.get_tool("multiply")
        assert tool is not None
        assert tool.description == "Multiply two numbers."

    def test_tool_execution(self, tool_registry):
        """Test executing a registered tool."""
        result = tool_registry.execute("add_numbers", a=3, b=5)
        assert result == 8

    def test_tool_execution_string_result(self, tool_registry):
        """Test executing a tool with string result."""
        result = tool_registry.execute("greet", name="World")
        assert result == "Hello, World!"

    def test_tool_not_found_raises(self, tool_registry):
        """Test executing non-existent tool raises ValueError."""
        with pytest.raises(ValueError, match="Tool 'nonexistent' not found"):
            tool_registry.execute("nonexistent")

    def test_list_tools(self, tool_registry):
        """Test listing all registered tools."""
        tools = tool_registry.list_tools()
        assert len(tools) == 2
        names = [t.name for t in tools]
        assert "add_numbers" in names
        assert "greet" in names

    def test_get_schemas(self, tool_registry):
        """Test getting all tool schemas."""
        schemas = tool_registry.get_schemas()
        assert len(schemas) == 2
        schema_names = [s["name"] for s in schemas]
        assert "add_numbers" in schema_names

    def test_tool_schema_structure(self, tool_registry):
        """Test tool schema has correct structure."""
        tool = tool_registry.get_tool("add_numbers")
        schema = tool.to_schema()
        assert "name" in schema
        assert "description" in schema
        assert "parameters" in schema

    def test_register_overwrites_existing(self):
        """Test registering tool with same name overwrites."""
        registry = ToolRegistry()
        registry.register_function(lambda: 1, name="dup")
        registry.register_function(lambda: 2, name="dup")
        result = registry.execute("dup")
        assert result == 2
