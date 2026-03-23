"""MCP tool definitions for the plugin_system module.

Exposes plugin discovery and dependency resolution as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="plugins",
    description="Scan for installed plugins via entry points.",
)
def plugin_scan_entry_points(
    entry_point_group: str = "codomyrmex.plugins",
) -> dict[str, Any]:
    """Discover plugins from Python package entry points.

    Args:
        entry_point_group: Entry point group name to scan.
    """
    try:
        from codomyrmex.plugin_system.discovery import PluginDiscovery

        discovery = PluginDiscovery(entry_point_group=entry_point_group)
        result = discovery.scan_entry_points()
        return {
            "status": "success",
            "plugin_count": len(result.plugins),
            "plugins": [
                {"name": p.name, "module": p.module_path, "state": p.state.value}
                for p in result.plugins
            ],
            "errors": [{"source": s, "error": e} for s, e in result.errors],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="plugins",
    description="Resolve plugin dependencies and produce a load order.",
)
def plugin_resolve_dependencies(
    plugins: list[dict[str, Any]],
) -> dict[str, Any]:
    """Resolve plugin dependencies using topological sort.

    Args:
        plugins: list of dicts with 'name' and optional 'dependencies' list.
    """
    try:
        from codomyrmex.plugin_system.dependency_resolver import (
            DependencyNode,
            DependencyResolver,
        )

        resolver = DependencyResolver()
        for p in plugins:
            resolver.add(
                DependencyNode(
                    name=p["name"],
                    dependencies=p.get("dependencies", []),
                )
            )
        result = resolver.resolve()
        return {
            "status": "success",
            "resolution_status": result.status.value,
            "load_order": result.load_order,
            "missing": result.missing,
            "circular": result.circular,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
