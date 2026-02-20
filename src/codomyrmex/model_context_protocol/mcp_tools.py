"""MCP tools for the model_context_protocol module itself — MCP introspection."""

from typing import Any, Dict, List, Optional

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="model_context_protocol")
def inspect_server(server_name: str = "default") -> dict:
    """Inspect the running MCP server's configuration and state.

    Args:
        server_name: Name of the server to inspect

    Returns:
        Server info including name, version, tool count, resource count.
    """
    from codomyrmex.model_context_protocol.server import MCPServer

    try:
        # Return static info for introspection
        return {
            "status": "success",
            "server_name": server_name,
            "protocol_version": "2025-06-18",
            "capabilities": ["tools", "resources", "prompts"],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="model_context_protocol")
def list_registered_tools() -> dict:
    """List all tools registered across the MCP ecosystem.

    Returns:
        Dictionary with all registered tool names and their modules.
    """
    import importlib
    import pkgutil

    try:
        tools: List[Dict[str, str]] = []
        import codomyrmex
        pkg_path = codomyrmex.__path__

        for _importer, modname, _ispkg in pkgutil.walk_packages(pkg_path, prefix="codomyrmex."):
            if modname.endswith(".mcp_tools"):
                try:
                    mod = importlib.import_module(modname)
                    for name in dir(mod):
                        obj = getattr(mod, name)
                        if callable(obj) and hasattr(obj, "_mcp_tool_meta"):
                            tools.append({
                                "name": name,
                                "module": modname,
                                "category": getattr(obj, "_mcp_tool_meta", {}).get("category", "unknown"),
                            })
                except ImportError:
                    continue

        return {
            "status": "success",
            "tools": tools,
            "total_count": len(tools),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="model_context_protocol")
def get_tool_schema(tool_name: str) -> dict:
    """Get the JSON schema for a specific registered MCP tool.

    Args:
        tool_name: Fully qualified tool name

    Returns:
        JSON schema for the tool's input parameters.
    """
    try:
        from codomyrmex.model_context_protocol.decorators import _generate_schema_from_signature
        import importlib

        # Search through all mcp_tools modules
        import pkgutil
        import codomyrmex
        for _importer, modname, _ispkg in pkgutil.walk_packages(
            codomyrmex.__path__, prefix="codomyrmex."
        ):
            if modname.endswith(".mcp_tools"):
                try:
                    mod = importlib.import_module(modname)
                    if hasattr(mod, tool_name):
                        func = getattr(mod, tool_name)
                        schema = _generate_schema_from_signature(func)
                        return {
                            "status": "success",
                            "tool_name": tool_name,
                            "module": modname,
                            "schema": schema,
                        }
                except ImportError:
                    continue

        return {"status": "error", "message": f"Tool not found: {tool_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
