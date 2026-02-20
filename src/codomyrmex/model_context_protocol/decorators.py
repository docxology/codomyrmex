"""
MCP Tool Decorators.

Provides the @mcp_tool decorator for registering functions as MCP tools
directly within their defining modules. This enables "Module-Native"
MCP exposure without centralized registry files.
"""

import inspect
import functools
from typing import Any, Callable, Dict, Optional, Type, get_type_hints

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def mcp_tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None,
    category: str = "general",
) -> Callable:
    """
    Decorator to mark a function as an MCP tool.
    
    Args:
        name: Tool name (default: function name)
        description: Tool description (default: docstring)
        schema: JSON Schema for arguments (default: auto-generated from type hints)
        category: Tool category for organization
    
    Usage:
        @mcp_tool(category="math")
        def add(a: int, b: int) -> int:
            '''Add two numbers.'''
            return a + b
    """
    def decorator(func: Callable) -> Callable:
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
            "module": func.__module__,
        }
        setattr(func, "_mcp_tool", tool_meta)
        setattr(func, "_mcp_tool_meta", tool_meta)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Copy metadata onto wrapper so scanners find it via dir()
        wrapper._mcp_tool = tool_meta  # type: ignore[attr-defined]
        wrapper._mcp_tool_meta = tool_meta  # type: ignore[attr-defined]
            
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


def _generate_schema_from_signature(func: Callable) -> Dict[str, Any]:
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
            json_type = _map_python_type_to_json(param_type)
            
            prop_schema = {"type": json_type}
            
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
        logger.warning(f"Failed to generate schema for {getattr(func, '__name__', '?')}: {e}")
        return {"type": "object", "properties": {}}  # Fallback


def _map_python_type_to_json(py_type: Type) -> str:
    """Map Python types to JSON Schema types."""
    if py_type == str:
        return "string"
    elif py_type == int:
        return "integer"
    elif py_type == float:
        return "number"
    elif py_type == bool:
        return "boolean"
    elif py_type == list or getattr(py_type, "__origin__", None) == list:
        return "array"
    elif py_type == dict or getattr(py_type, "__origin__", None) == dict:
        return "object"
    else:
        return "string"  # Default fallback
