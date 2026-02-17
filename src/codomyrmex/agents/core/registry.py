
"""Tool Registry for Agents.

This module provides a registry for tools that can be used by agents.
Tools are functions or methods that are exposed to the LLM.
"""

import inspect
from dataclasses import dataclass
from typing import Any
from collections.abc import Callable

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

@dataclass
class Tool:
    """Represents a tool available to an agent."""
    name: str
    func: Callable
    description: str
    args_schema: dict[str, Any]
    return_schema: dict[str, Any] | None = None

    def to_schema(self) -> dict[str, Any]:
        """Convert tool to JSON schema format (e.g. for OpenAI functions)."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.args_schema
        }

class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self.logger = get_logger(self.__class__.__name__)

    def register(self, tool: Tool):
        """Register a tool instance."""
        if tool.name in self._tools:
            self.logger.warning(f"Overwriting tool '{tool.name}'")
        self._tools[tool.name] = tool
        self.logger.debug(f"Registered tool: {tool.name}")

    def register_function(self, func: Callable, name: str | None = None, description: str | None = None):
        """Register a python function as a tool."""
        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or "No description provided."

        # Simple schema extraction (can be enhanced with Pydantic)
        sig = inspect.signature(func)
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }

        for param_name, param in sig.parameters.items():
            param_type = "string" # Default
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == dict:
                    param_type = "object"
                elif param.annotation == list:
                    param_type = "array"

            parameters["properties"][param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }

            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)

        tool = Tool(
            name=tool_name,
            func=func,
            description=tool_desc,
            args_schema=parameters
        )
        self.register(tool)

    def get_tool(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    def get_schemas(self) -> list[dict[str, Any]]:
        """Get all tool schemas."""
        return [tool.to_schema() for tool in self._tools.values()]

    def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")

        return tool.func(**kwargs)

    @classmethod
    def from_mcp(cls, mcp_registry: Any, *, prefix: str = "") -> "ToolRegistry":
        """Create a ToolRegistry from an MCP tool registry.

        Bridges ``model_context_protocol.MCPToolRegistry`` (or any object
        with a ``list_tools()`` method returning objects with ``name``,
        ``description``, ``input_schema``, and ``handler`` attributes) into
        the agent-level ToolRegistry.

        Args:
            mcp_registry: An MCP-style tool registry instance.
            prefix: Optional prefix for tool names (e.g. ``"mcp."``)

        Returns:
            A new ``ToolRegistry`` populated with bridged tools.

        Raises:
            TypeError: If *mcp_registry* doesn't expose ``list_tools()``.
        """
        if not hasattr(mcp_registry, "list_tools"):
            raise TypeError(
                f"Expected an MCP registry with list_tools(), got {type(mcp_registry).__name__}"
            )

        registry = cls()
        for mcp_tool in mcp_registry.list_tools():
            name = f"{prefix}{mcp_tool.name}" if prefix else mcp_tool.name
            description = getattr(mcp_tool, "description", "MCP tool")
            handler = getattr(mcp_tool, "handler", None)
            input_schema = getattr(mcp_tool, "input_schema", {"type": "object", "properties": {}})

            if handler is None:
                registry.logger.warning(f"MCP tool '{name}' has no handler, skipping")
                continue

            tool = Tool(
                name=name,
                func=handler,
                description=description,
                args_schema=input_schema,
            )
            registry.register(tool)

        registry.logger.info(f"Bridged {len(registry._tools)} tools from MCP registry")
        return registry
