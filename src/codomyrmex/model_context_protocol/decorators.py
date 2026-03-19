"""
MCP Tool Decorators.

Provides the @mcp_tool decorator for registering functions as MCP tools
directly within their defining modules. This enables "Module-Native"
MCP exposure without centralized registry files.
"""

import functools
import inspect
import types
from collections.abc import Callable
from typing import Any, Union, get_args, get_origin, get_type_hints

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def mcp_tool(
    name: str | None = None,
    description: str | None = None,
    schema: dict[str, Any] | None = None,
    category: str = "general",
    tags: list[str] | None = None,
    version: str | None = None,
    deprecated_in: str | None = None,
) -> Callable[..., Any]:
    """
    Decorator to mark a function as an MCP tool.

    Args:
        name: Tool name (default: function name)
        description: Tool description (default: docstring)
        schema: JSON Schema for arguments (default: auto-generated from type hints)
        category: Tool category for organization
        tags: Optional tags for discovery / PAI manifest indexing (e.g. ``skills``).
        version: Tool version string (e.g., "1.0", "2.0"). Defaults to "1.0".
        deprecated_in: Version in which this tool was deprecated (e.g., "1.5").
                       If set, calling the tool emits a DeprecationWarning.

    Usage:
        @mcp_tool(category="math", version="2.0")
        def add(a: int, b: int) -> int:
            '''Add two numbers.'''
            return a + b
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Get metadata
        base_name = name or func.__name__
        if not base_name.startswith("codomyrmex."):
            tool_name = f"codomyrmex.{base_name}"
        else:
            tool_name = base_name

        tool_desc = description or (func.__doc__ or "").strip()

        # Auto-generate schema if not provided
        tool_schema = schema or _generate_schema_from_signature(func)

        # Attach metadata to the function object
        # This allows scanners to find it without importing everything at once
        tool_meta = {
            "name": tool_name,
            "description": tool_desc,
            "schema": tool_schema,
            "category": category,
            "tags": list(tags or []),
            "module": func.__module__,
            "version": version or "1.0",
            "deprecated_in": deprecated_in,
        }
        func._mcp_tool_meta = tool_meta
        func._mcp_tool = tool_meta

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if deprecated_in:
                import warnings

                warnings.warn(
                    f"MCP tool {tool_name!r} deprecated since v{deprecated_in}.",
                    DeprecationWarning,
                    stacklevel=2,
                )
            return func(*args, **kwargs)

        # Copy metadata onto wrapper so scanners find it via dir()
        wrapper._mcp_tool_meta = tool_meta
        wrapper._mcp_tool = tool_meta

        return wrapper

    return decorator


def _safe_default(value: Any) -> Any:
    """Convert a Python default value to a JSON-safe representation."""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_safe_default(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _safe_default(v) for k, v in value.items()}
    # Enum members → use their value
    import enum

    if isinstance(value, enum.Enum):
        return value.value
    # Skip callables (factory defaults like list, dict)
    if callable(value):
        return None
    # Fallback: stringify
    return str(value)


def _generate_schema_from_signature(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate JSON Schema from function signature and type hints."""
    try:
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            # Handle **kwargs and *args gracefully
            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue

            # Determine type
            param_type = type_hints.get(param_name, Any)
            prop_schema = _annotation_to_json_schema(param_type)

            # Default value? (JSON-safe conversion)
            if param.default is not inspect.Parameter.empty:
                safe_val = _safe_default(param.default)
                if safe_val is not None:
                    prop_schema["default"] = safe_val
            else:
                required.append(param_name)

            properties[param_name] = prop_schema

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }
    except Exception as e:
        logger.warning(
            "Failed to generate schema for %s: %s", getattr(func, "__name__", "?"), e
        )
        return {"type": "object", "properties": {}}  # Fallback


def _is_union(tp: Any) -> bool:
    origin = get_origin(tp)
    return origin is Union or origin is types.UnionType


def _annotation_to_json_schema(annotation: Any) -> dict[str, Any]:
    """Map a typing annotation to a JSON Schema fragment (object with type/anyOf/items)."""
    if annotation is Any:
        return {"type": "string"}

    if _is_union(annotation):
        parts: list[dict[str, Any]] = []
        for arg in get_args(annotation):
            if arg is type(None):
                parts.append({"type": "null"})
            else:
                sub = _annotation_to_json_schema(arg)
                if sub:
                    parts.append(sub)
        if not parts:
            return {"type": "string"}
        if len(parts) == 1:
            return parts[0]
        return {"anyOf": parts}

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is list or annotation is list:
        inner = args[0] if args else Any
        inner_schema = (
            _annotation_to_json_schema(inner)
            if inner is not Any
            else {"type": "string"}
        )
        return {"type": "array", "items": inner_schema}

    if origin is dict or annotation is dict:
        return {"type": "object"}

    if annotation is str:
        return {"type": "string"}
    if annotation is int:
        return {"type": "integer"}
    if annotation is float:
        return {"type": "number"}
    if annotation is bool:
        return {"type": "boolean"}
    if annotation is type(None):
        return {"type": "null"}

    # Legacy single-string fallback (bytes, custom classes, etc.)
    return {"type": _map_python_type_to_json_string(annotation)}


def _map_python_type_to_json_string(py_type: type[Any]) -> str:
    """Map Python types to a single JSON Schema type string (non-union)."""
    if py_type is str:
        return "string"
    if py_type is int:
        return "integer"
    if py_type is float:
        return "number"
    if py_type is bool:
        return "boolean"
    if py_type is list or getattr(py_type, "__origin__", None) is list:
        return "array"
    if py_type is dict or getattr(py_type, "__origin__", None) is dict:
        return "object"
    return "string"


def _map_python_type_to_json(py_type: type[Any]) -> str:
    """Map Python types to JSON Schema types (tests and simple callers)."""
    return _map_python_type_to_json_string(py_type)
