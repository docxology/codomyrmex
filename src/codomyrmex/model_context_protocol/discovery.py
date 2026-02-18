"""MCP tool and server auto-discovery and registration.

Provides mechanisms for discovering available MCP servers,
tools, and resources at runtime via introspection.  Supports
error-isolated scanning, incremental refresh, and runtime metrics.
"""

from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

logger = logging.getLogger(__name__)


# =====================================================================
# Data models
# =====================================================================


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


@dataclass
class FailedModule:
    """Record of a module that failed to import during scanning."""

    module: str
    error: str
    error_type: str


@dataclass
class DiscoveryReport:
    """Result of a package scan with error isolation.

    Contains the list of discovered tools alongside any modules
    that failed to import, plus timing information.
    """

    tools: list[DiscoveredTool] = field(default_factory=list)
    failed_modules: list[FailedModule] = field(default_factory=list)
    scan_duration_ms: float = 0.0
    modules_scanned: int = 0


@dataclass
class DiscoveryMetrics:
    """Runtime metrics for the discovery engine."""

    total_tools: int = 0
    scan_duration_ms: float = 0.0
    failed_modules: list[str] = field(default_factory=list)
    modules_scanned: int = 0
    cache_hits: int = 0
    last_scan_time: datetime | None = None


# =====================================================================
# Discovery engine
# =====================================================================


class MCPDiscovery:
    """Auto-discovery engine for MCP tools and servers.

    Scans Python packages for MCP-compatible tools and servers,
    building a registry of available capabilities.  Supports
    error-isolated scanning (broken modules don't kill the scan),
    incremental single-module refresh, and runtime metrics.
    """

    TOOL_MARKER = "_mcp_tool"
    SERVER_MARKER = "_mcp_server"

    def __init__(self) -> None:
        self._tools: dict[str, DiscoveredTool] = {}
        self._servers: dict[str, DiscoveredServer] = {}
        # Metrics tracking
        self._cache_hits: int = 0
        self._last_scan_time: datetime | None = None
        self._last_scan_duration_ms: float = 0.0
        self._last_modules_scanned: int = 0
        self._last_failed_modules: list[str] = []

    # ── Full package scan (error-isolated) ───────────────────────

    def scan_package(self, package_name: str) -> DiscoveryReport:
        """Scan a Python package for MCP tools with error isolation.

        Each sub-module is imported inside its own ``try/except`` block
        so that a broken module never kills the full scan.  The returned
        :class:`DiscoveryReport` lists both the discovered tools *and*
        any modules that failed to load.
        """
        report = DiscoveryReport()
        t0 = time.monotonic()

        try:
            package = importlib.import_module(package_name)
        except (ImportError, SyntaxError, Exception) as exc:
            report.failed_modules.append(FailedModule(
                module=package_name,
                error=str(exc),
                error_type=type(exc).__name__,
            ))
            report.scan_duration_ms = (time.monotonic() - t0) * 1000
            logger.warning("Cannot import package %s: %s", package_name, exc)
            return report

        if not hasattr(package, "__path__"):
            # Single module, not a package
            report.modules_scanned = 1
            tools = self._scan_module(package)
            report.tools.extend(tools)
            for tool in tools:
                self._tools[tool.name] = tool
            report.scan_duration_ms = (time.monotonic() - t0) * 1000
            self._update_metrics(report)
            return report

        for _importer, modname, _ispkg in pkgutil.walk_packages(
            package.__path__, prefix=package_name + "."
        ):
            report.modules_scanned += 1
            try:
                module = importlib.import_module(modname)
                tools = self._scan_module(module)
                report.tools.extend(tools)
            except (ImportError, SyntaxError, RecursionError) as exc:
                report.failed_modules.append(FailedModule(
                    module=modname,
                    error=str(exc),
                    error_type=type(exc).__name__,
                ))
                logger.warning("Error scanning %s: %s", modname, exc)
            except Exception as exc:
                report.failed_modules.append(FailedModule(
                    module=modname,
                    error=str(exc),
                    error_type=type(exc).__name__,
                ))
                logger.warning("Unexpected error scanning %s: %s", modname, exc)

        for tool in report.tools:
            self._tools[tool.name] = tool

        report.scan_duration_ms = (time.monotonic() - t0) * 1000
        self._update_metrics(report)
        return report

    # ── Incremental single-module scan ───────────────────────────

    def scan_module(self, module_name: str) -> DiscoveryReport:
        """Scan a single module for MCP tools (incremental refresh).

        Imports the named module, scans it for ``@mcp_tool`` markers,
        and merges discovered tools into the existing registry without
        clearing other tools.

        Args:
            module_name: Fully-qualified module name
                         (e.g. ``"codomyrmex.search.mcp_tools"``).

        Returns:
            A :class:`DiscoveryReport` for this single module.
        """
        report = DiscoveryReport()
        t0 = time.monotonic()

        try:
            module = importlib.import_module(module_name)
            report.modules_scanned = 1
            tools = self._scan_module(module)
            report.tools.extend(tools)
            for tool in tools:
                self._tools[tool.name] = tool
        except (ImportError, SyntaxError, RecursionError, Exception) as exc:
            report.failed_modules.append(FailedModule(
                module=module_name,
                error=str(exc),
                error_type=type(exc).__name__,
            ))
            logger.warning("Error scanning module %s: %s", module_name, exc)

        report.scan_duration_ms = (time.monotonic() - t0) * 1000
        return report

    # ── Private helpers ──────────────────────────────────────────

    def _scan_module(self, module: Any) -> list[DiscoveredTool]:
        """Scan a single already-imported module for MCP tool markers."""
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

    def _update_metrics(self, report: DiscoveryReport) -> None:
        """Update internal metrics after a scan."""
        self._last_scan_time = datetime.now(timezone.utc)
        self._last_scan_duration_ms = report.scan_duration_ms
        self._last_modules_scanned = report.modules_scanned
        self._last_failed_modules = [f.module for f in report.failed_modules]

    # ── Registry accessors ───────────────────────────────────────

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

    def record_cache_hit(self) -> None:
        """Increment cache-hit counter (called by bridge cache logic)."""
        self._cache_hits += 1

    # ── Metrics ──────────────────────────────────────────────────

    def get_metrics(self) -> DiscoveryMetrics:
        """Return current discovery metrics."""
        return DiscoveryMetrics(
            total_tools=len(self._tools),
            scan_duration_ms=self._last_scan_duration_ms,
            failed_modules=list(self._last_failed_modules),
            modules_scanned=self._last_modules_scanned,
            cache_hits=self._cache_hits,
            last_scan_time=self._last_scan_time,
        )


# =====================================================================
# Decorator
# =====================================================================


def mcp_tool(
    name: str | None = None,
    description: str = "",
    tags: list[str] | None = None,
) -> Callable:
    """Decorator to mark a function as an MCP tool."""

    def decorator(func: Callable) -> Callable:
        setattr(func, MCPDiscovery.TOOL_MARKER, {
            "name": name or func.__name__,
            "description": description or inspect.getdoc(func) or "",
            "tags": tags or [],
        })
        return func

    return decorator
