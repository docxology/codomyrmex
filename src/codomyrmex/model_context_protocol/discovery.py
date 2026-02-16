"""MCP tool and server auto-discovery and registration.

Provides mechanisms for discovering available MCP servers,
tools, and resources at runtime via introspection.
"""

from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class DiscoveredTool:
    """A tool discovered via introspection."""
    name: str
    description: str
    module_path: str
    callable_name: str
    parameters: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def to_mcp_schema(self) -> dict[str, Any]:
        """Convert to MCP tool schema format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.parameters,
            },
        }


@dataclass
class DiscoveredServer:
    """An MCP server discovered via introspection."""
    name: str
    module_path: str
    tools: list[DiscoveredTool] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)


class MCPDiscovery:
    """Auto-discovery engine for MCP tools and servers.

    Scans Python packages for MCP-compatible tools and servers,
    building a registry of available capabilities.
    """

    TOOL_MARKER = "_mcp_tool"
    SERVER_MARKER = "_mcp_server"

    def __init__(self) -> None:
        self._tools: dict[str, DiscoveredTool] = {}
        self._servers: dict[str, DiscoveredServer] = {}

    def scan_package(self, package_name: str) -> list[DiscoveredTool]:
        """Scan a Python package for MCP tools."""
        discovered: list[DiscoveredTool] = []
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            logger.warning("Cannot import package: %s", package_name)
            return discovered

        if not hasattr(package, "__path__"):
            # Single module, not a package
            discovered.extend(self._scan_module(package))
            return discovered

        for importer, modname, ispkg in pkgutil.walk_packages(
            package.__path__, prefix=package_name + "."
        ):
            try:
                module = importlib.import_module(modname)
                discovered.extend(self._scan_module(module))
            except Exception as e:
                logger.debug("Skipping %s: %s", modname, e)

        for tool in discovered:
            self._tools[tool.name] = tool
        return discovered

    def _scan_module(self, module: Any) -> list[DiscoveredTool]:
        """Scan a single module for MCP tool markers."""
        tools: list[DiscoveredTool] = []
        for name, obj in inspect.getmembers(module):
            if hasattr(obj, self.TOOL_MARKER):
                tool_info = getattr(obj, self.TOOL_MARKER)
                sig = inspect.signature(obj)
                params = {}
                for pname, param in sig.parameters.items():
                    if pname in ("self", "cls"):
                        continue
                    ptype = "string"
                    if param.annotation != inspect.Parameter.empty:
                        ptype = getattr(param.annotation, "__name__", "string")
                    params[pname] = {"type": ptype}

                tools.append(DiscoveredTool(
                    name=tool_info.get("name", name),
                    description=tool_info.get("description", inspect.getdoc(obj) or ""),
                    module_path=module.__name__,
                    callable_name=name,
                    parameters=params,
                    tags=tool_info.get("tags", []),
                ))
        return tools

    def register_tool(self, tool: DiscoveredTool) -> None:
        """Manually register a tool."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> DiscoveredTool | None:
        return self._tools.get(name)

    def list_tools(self, tag: str | None = None) -> list[DiscoveredTool]:
        """List all discovered tools, optionally filtered by tag."""
        tools = list(self._tools.values())
        if tag:
            tools = [t for t in tools if tag in t.tags]
        return tools

    @property
    def tool_count(self) -> int:
        return len(self._tools)


def mcp_tool(name: str | None = None, description: str = "",
             tags: list[str] | None = None) -> Callable:
    """Decorator to mark a function as an MCP tool."""
    def decorator(func: Callable) -> Callable:
        setattr(func, MCPDiscovery.TOOL_MARKER, {
            "name": name or func.__name__,
            "description": description or inspect.getdoc(func) or "",
            "tags": tags or [],
        })
        return func
    return decorator
