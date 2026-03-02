"""MCP tools for the tool_use module.

Exposes tool registry listing and input validation as auto-discovered
MCP tools. Zero external dependencies beyond the tool_use module itself.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs):
        def decorator(fn):
            fn._mcp_tool_meta = kwargs
            return fn
        return decorator


@mcp_tool(
    category="tool_use",
    description=(
        "List all tools registered in a ToolRegistry instance. "
        "Returns a list of tool entry name strings."
    ),
)
def tool_use_list_tools() -> list[str]:
    """Return a list of registered tool names from a fresh registry.

    Returns:
        List of tool name strings (may be empty if no tools registered).
    """
    from codomyrmex.tool_use import ToolRegistry

    registry = ToolRegistry()
    if hasattr(registry, "list"):
        entries = registry.list()
        if entries and hasattr(entries[0], "name"):
            return [e.name for e in entries]
        return [str(e) for e in entries]
    if hasattr(registry, "tools"):
        return list(registry.tools.keys())
    return []


@mcp_tool(
    category="tool_use",
    description=(
        "Validate input data against a JSON schema dict. "
        "Returns a dict with 'valid' (bool) and 'errors' (list of strings)."
    ),
)
def tool_use_validate_input(schema: dict, data: Any) -> dict:
    """Validate data against a schema.

    Args:
        schema: JSON schema dictionary.
        data: Data to validate.

    Returns:
        Dictionary with 'valid' and 'errors' keys.
    """
    from codomyrmex.tool_use import validate_input

    result = validate_input(data, schema)
    if hasattr(result, "is_valid"):
        return {
            "valid": result.is_valid,
            "errors": getattr(result, "errors", []),
        }
    if isinstance(result, bool):
        return {"valid": result, "errors": []}
    return {"valid": bool(result), "errors": [str(result)]}
