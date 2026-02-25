"""
Tool calling framework for LLMs.

Provides utilities for defining, registering, and executing tools with LLMs.
"""

import inspect
import json
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional, Type, get_type_hints


class ParameterType(Enum):
    """JSON Schema parameter types."""
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    param_type: ParameterType
    description: str
    required: bool = True
    enum: list[str] | None = None
    default: Any | None = None
    items_type: ParameterType | None = None  # For arrays

    def to_json_schema(self) -> dict[str, Any]:
        """Convert to JSON schema format."""
        schema: dict[str, Any] = {
            "type": self.param_type.value,
            "description": self.description,
        }

        if self.enum:
            schema["enum"] = self.enum

        if self.param_type == ParameterType.ARRAY and self.items_type:
            schema["items"] = {"type": self.items_type.value}

        return schema


@dataclass
class ToolResult:
    """Result of tool execution."""
    success: bool
    output: Any
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_string(self) -> str:
        """Convert result to string for LLM consumption."""
        if self.success:
            if isinstance(self.output, (dict, list)):
                return json.dumps(self.output, indent=2)
            return str(self.output)
        return f"Error: {self.error}"


@dataclass
class Tool:
    """A tool that can be called by an LLM."""
    name: str
    description: str
    parameters: list[ToolParameter]
    function: Callable
    category: str | None = None

    def to_openai_format(self) -> dict[str, Any]:
        """Convert to OpenAI function calling format."""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }
        }

    def to_anthropic_format(self) -> dict[str, Any]:
        """Convert to Anthropic tool format."""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }

    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given arguments."""
        try:
            result = self.function(**kwargs)
            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))


class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self.tools: dict[str, Tool] = {}
        self.categories: dict[str, list[str]] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self.tools[tool.name] = tool

        if tool.category:
            if tool.category not in self.categories:
                self.categories[tool.category] = []
            self.categories[tool.category].append(tool.name)

    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self, category: str | None = None) -> list[Tool]:
        """List all tools or tools in a category."""
        if category:
            tool_names = self.categories.get(category, [])
            return [self.tools[name] for name in tool_names]
        return list(self.tools.values())

    def to_openai_format(self, category: str | None = None) -> list[dict]:
        """Get tools in OpenAI format."""
        return [t.to_openai_format() for t in self.list_tools(category)]

    def to_anthropic_format(self, category: str | None = None) -> list[dict]:
        """Get tools in Anthropic format."""
        return [t.to_anthropic_format() for t in self.list_tools(category)]

    def execute(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get(tool_name)
        if not tool:
            return ToolResult(success=False, output=None, error=f"Tool '{tool_name}' not found")
        return tool.execute(**kwargs)


def _python_type_to_param_type(python_type: type) -> ParameterType:
    """Convert Python type to JSON Schema parameter type."""
    type_mapping = {
        str: ParameterType.STRING,
        int: ParameterType.INTEGER,
        float: ParameterType.NUMBER,
        bool: ParameterType.BOOLEAN,
        list: ParameterType.ARRAY,
        dict: ParameterType.OBJECT,
    }
    return type_mapping.get(python_type, ParameterType.STRING)


def tool(
    name: str | None = None,
    description: str | None = None,
    category: str | None = None,
    registry: ToolRegistry | None = None,
):
    """Decorator to create a tool from a function."""
    def decorator(func: Callable) -> Callable:
        """Execute Decorator operations natively."""
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or f"Tool: {tool_name}"

        # Extract parameters from function signature
        sig = inspect.signature(func)
        type_hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}

        parameters = []
        for param_name, param in sig.parameters.items():
            if param_name in ('self', 'cls'):
                continue

            param_type = type_hints.get(param_name, str)
            has_default = param.default != inspect.Parameter.empty

            # Try to get description from docstring
            param_desc = f"Parameter: {param_name}"
            if func.__doc__:
                # Simple docstring parsing
                for line in func.__doc__.split('\n'):
                    if param_name in line and ':' in line:
                        param_desc = line.split(':', 1)[-1].strip()
                        break

            parameters.append(ToolParameter(
                name=param_name,
                param_type=_python_type_to_param_type(param_type),
                description=param_desc,
                required=not has_default,
                default=param.default if has_default else None,
            ))

        tool_obj = Tool(
            name=tool_name,
            description=tool_description,
            parameters=parameters,
            function=func,
            category=category,
        )

        if registry:
            registry.register(tool_obj)

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Execute Wrapper operations natively."""
            return func(*args, **kwargs)

        wrapper._tool = tool_obj
        return wrapper

    return decorator


# Built-in tools
def create_calculator_tool() -> Tool:
    """Create a calculator tool."""
    import ast
    import operator

    _MATH_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def _safe_eval(node: ast.AST) -> float:
        """Recursively evaluate an AST node containing only arithmetic."""
        if isinstance(node, ast.Expression):
            return _safe_eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _MATH_OPS:
            return _MATH_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _MATH_OPS:
            return _MATH_OPS[type(node.op)](_safe_eval(node.operand))
        raise ValueError(f"Unsupported expression: {ast.dump(node)}")

    def calculate(expression: str) -> float:
        """Evaluate a mathematical expression safely using AST parsing."""
        # SECURITY: Uses AST-based evaluator instead of eval() to prevent code injection
        tree = ast.parse(expression, mode="eval")
        return _safe_eval(tree)

    return Tool(
        name="calculator",
        description="Evaluate a mathematical expression. Supports +, -, *, /, and parentheses.",
        parameters=[
            ToolParameter(
                name="expression",
                param_type=ParameterType.STRING,
                description="The mathematical expression to evaluate",
            )
        ],
        function=calculate,
        category="utilities",
    )


def create_datetime_tool() -> Tool:
    """Create a datetime tool."""
    from datetime import datetime

    def get_datetime(format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Get the current date and time."""
        return datetime.now().strftime(format)

    return Tool(
        name="get_datetime",
        description="Get the current date and time in the specified format.",
        parameters=[
            ToolParameter(
                name="format",
                param_type=ParameterType.STRING,
                description="Python strftime format string",
                required=False,
                default="%Y-%m-%d %H:%M:%S",
            )
        ],
        function=get_datetime,
        category="utilities",
    )


# Global registry
DEFAULT_REGISTRY = ToolRegistry()


def register_tool(tool: Tool) -> None:
    """Register a tool in the default registry."""
    DEFAULT_REGISTRY.register(tool)


def get_tool(name: str) -> Tool | None:
    """Get a tool from the default registry."""
    return DEFAULT_REGISTRY.get(name)


__all__ = [
    "ParameterType",
    "ToolParameter",
    "ToolResult",
    "Tool",
    "ToolRegistry",
    "tool",
    "create_calculator_tool",
    "create_datetime_tool",
    "DEFAULT_REGISTRY",
    "register_tool",
    "get_tool",
]
