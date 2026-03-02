"""MCP tool and server auto-discovery and registration.

Provides mechanisms for discovering available MCP servers,
tools, and resources at runtime via introspection.  Supports
error-isolated scanning, incremental refresh, and runtime metrics.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import logging
import pkgutil
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any

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
    version: str = "1.0"
    requires: list[str] = field(default_factory=list)
    available: bool = True
    unavailable_reason: str | None = None
    handler: Callable[..., Any] | None = None

    def to_mcp_schema(self) -> dict[str, Any]:
        """Convert to MCP tool schema format."""
        schema = {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.parameters,
            "tags": self.tags,
            "x-codomyrmex": {
                "module": self.module_path,
                "callable": self.callable_name,
                "version": self.version,
                "available": self.available,
            },
        }
        if not self.available:
            schema["description"] = str(schema["description"]) + f" (UNAVAILABLE: {self.unavailable_reason})"
        return schema


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
    error-isolated scanning, incremental refresh, and runtime metrics.
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._registry: dict[str, DiscoveredTool] = {}
        self._failed_modules: list[FailedModule] = []
        self._metrics = DiscoveryMetrics()

    # ── Full package scan (error-isolated) ───────────────────────

    def scan_package(self, package_name: str) -> DiscoveryReport:
        """Scan a Python package for MCP tools with error isolation.

        Each sub-module is imported inside its own ``try/except`` block
        so that a broken module never kills the full scan.  The returned
        :class:`DiscoveryReport` lists both the discovered tools *and*
        any modules that failed to load.
        """
        start_time = time.perf_counter()
        discovered_tools: list[DiscoveredTool] = []
        failed_modules: list[FailedModule] = []
        modules_scanned = 0

        # Import the root package first
        try:
            root_pkg = importlib.import_module(package_name)
        except ImportError as e:
            logger.error(f"Failed to import root package {package_name}: {e}")
            return DiscoveryReport(
                failed_modules=[
                    FailedModule(package_name, str(e), type(e).__name__)
                ]
            )

        # Walk through all submodules
        path = getattr(root_pkg, "__path__", [])
        if not path:
            # Single module, just scan it
            report = self.scan_module(package_name)
            self._update_metrics(report)
            return report

        for _, name, _ in pkgutil.walk_packages(path, prefix=f"{package_name}."):
            modules_scanned += 1
            try:
                # Import module in isolation
                module = importlib.import_module(name)
                # Scan correctly imported module
                module_tools = self._scan_module(module)
                discovered_tools.extend(module_tools)
                # Update main registry incrementally
                for tool in module_tools:
                    self._registry[tool.name] = tool

            except Exception as e:
                # Isolate failure
                logger.debug(f"Failed to scan module {name}: {e}")
                failed_modules.append(
                    FailedModule(name, str(e), type(e).__name__)
                )
                self._failed_modules.append(
                    FailedModule(name, str(e), type(e).__name__)
                )

        duration = (time.perf_counter() - start_time) * 1000.0
        report = DiscoveryReport(
            tools=discovered_tools,
            failed_modules=failed_modules,
            scan_duration_ms=duration,
            modules_scanned=modules_scanned,
        )
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
        start_time = time.perf_counter()
        try:
            module = importlib.import_module(module_name)
            tools = self._scan_module(module)

            # Update registry
            for tool in tools:
                self._registry[tool.name] = tool

            duration = (time.perf_counter() - start_time) * 1000.0
            report = DiscoveryReport(
                tools=tools,
                scan_duration_ms=duration,
                modules_scanned=1,
            )
            self._update_metrics(report)
            return report

        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000.0
            fail = FailedModule(module_name, str(e), type(e).__name__)
            self._failed_modules.append(fail)
            # Update metrics even on failure
            self._metrics.scan_duration_ms += duration
            self._metrics.failed_modules.append(module_name)

            return DiscoveryReport(
                failed_modules=[fail],
                scan_duration_ms=duration,
                modules_scanned=1,
            )

    # ── Private helpers ──────────────────────────────────────────

    def _scan_module(self, module: Any) -> list[DiscoveredTool]:
        """Scan a single already-imported module for MCP tool markers."""
        tools = []

        def _add_if_tool(name: str, obj: Any) -> None:
            """add If Tool ."""
            if hasattr(obj, "_mcp_tool_meta"):
                meta = obj._mcp_tool_meta

                # Check requirements
                available = True
                unavailable_reason = None
                if meta.get("requires"):
                    missing = []
                    for req in meta["requires"]:
                        if not importlib.util.find_spec(req):
                            missing.append(req)

                    if missing:
                        available = False
                        unavailable_reason = (
                            f"Missing dependencies: {', '.join(missing)}. "
                            f"Install via 'uv add {' '.join(missing)}'"
                        )

                tool = DiscoveredTool(
                    name=meta["name"] or name,
                    description=meta["description"] or (obj.__doc__ or "").strip(),
                    module_path=module.__name__,
                    callable_name=name,
                    parameters=meta.get("parameters", {}),
                    tags=meta.get("tags", []),
                    version=meta.get("version", "1.0"),
                    requires=meta.get("requires", []),
                    available=available,
                    unavailable_reason=unavailable_reason,
                    handler=obj,
                )
                tools.append(tool)

        for name, obj in inspect.getmembers(module):
            _add_if_tool(name, obj)
            if inspect.isclass(obj) and getattr(obj, "__module__", None) == module.__name__:
                for method_name, method_obj in inspect.getmembers(obj):
                    _add_if_tool(method_name, method_obj)

        return tools

    def _update_metrics(self, report: DiscoveryReport) -> None:
        """Update internal metrics after a scan."""
        self._metrics.total_tools = len(self._registry)
        self._metrics.scan_duration_ms = report.scan_duration_ms
        self._metrics.modules_scanned = report.modules_scanned
        self._metrics.last_scan_time = datetime.now(timezone.utc)
        self._metrics.failed_modules = [m.module for m in self._failed_modules]

    # ── Registry accessors ───────────────────────────────────────

    def register_tool(self, tool: DiscoveredTool) -> None:
        """Manually register a tool."""
        self._registry[tool.name] = tool

    def get_tool(self, name: str) -> DiscoveredTool | None:
        """get Tool ."""
        return self._registry.get(name)

    def list_tools(self, tag: str | None = None) -> list[DiscoveredTool]:
        """List all discovered tools, optionally filtered by tag."""
        if tag:
            return [t for t in self._registry.values() if tag in t.tags]
        return list(self._registry.values())

    @property
    def tool_count(self) -> int:
        """tool Count ."""
        return len(self._registry)

    def record_cache_hit(self) -> None:
        """Increment cache-hit counter (called by bridge cache logic)."""
        self._metrics.cache_hits += 1

    # ── Metrics ──────────────────────────────────────────────────

    def get_metrics(self) -> DiscoveryMetrics:
        """Return current discovery metrics."""
        return self._metrics


# =====================================================================
# Decorator
# =====================================================================


def mcp_tool(
    name: str | None = None,
    description: str = "",
    tags: list[str] | None = None,
    version: str = "1.0",
    requires: list[str] | None = None,
) -> Callable[..., Any]:
    """Decorator to mark a function as an MCP tool.

    Args:
        name: Override the tool name (default: function name).
        description: Tool description (default: docstring).
        tags: List of tags for classification.
        version: Semantic version string.
        requires: List of importable package names required by this tool.
                  If any are missing, the tool will be registered as unavailable.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """decorator ."""
        # Extract parameters using pydantic or typed-dict generation logic if needed
        # For now, we rely on the bridge to inspect signatures at runtime
        # but here we just mark it.
        # Ideally we should generate the JSON schema here to avoid repeated inspection.

        # We assume parameters will be extracted/validated by the bridge/server logic
        # Here we just store metadata.
        # But wait, DiscoveredTool needs parameters.
        # Let's extract them here.

        from codomyrmex.model_context_protocol.quality.validation import (
            # We might not want to couple tightly here if validation module is heavy
            # But validation.py is lightweight.
            _generate_schema_from_func,
        )

        try:
            params = _generate_schema_from_func(func)
        except Exception:
            params = {}

        func._mcp_tool_meta = {"name": name, "description": description, "tags": tags or [], "parameters": params, "version": version, "requires": requires or []}
        return func
    return decorator


