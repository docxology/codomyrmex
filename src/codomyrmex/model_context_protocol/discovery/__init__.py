"""MCP tool and server auto-discovery and registration.

Provides mechanisms for discovering available MCP servers,
tools, and resources at runtime via introspection.  Supports
error-isolated scanning, incremental refresh, and runtime metrics.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import pkgutil
import threading
import time
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.tool_tagging import manifest_tags

if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger(__name__)


def _synchronized(method: Any) -> Any:
    """Serialize access to a discovery engine while preserving its API."""

    def wrapper(self: MCPDiscovery, *args: Any, **kwargs: Any) -> Any:
        with self._lock:
            return method(self, *args, **kwargs)

    wrapper.__name__ = getattr(method, "__name__", "synchronized")
    wrapper.__doc__ = getattr(method, "__doc__", None)
    return wrapper


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
            schema["description"] = (
                str(schema["description"])
                + f" (UNAVAILABLE: {self.unavailable_reason})"
            )
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
        self._lock = threading.RLock()
        self._registry: dict[str, DiscoveredTool] = {}
        self._module_tools: dict[str, set[str]] = {}
        self._failed_modules: list[FailedModule] = []
        self._metrics = DiscoveryMetrics()

    # ── Full package scan (error-isolated) ───────────────────────

    @_synchronized
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
        scanned_module_names: set[str] = set()

        # Import the root package first
        try:
            root_pkg = importlib.import_module(package_name)
        except ImportError as e:
            logger.error("Failed to import root package %s: %s", package_name, e)
            return DiscoveryReport(
                failed_modules=[FailedModule(package_name, str(e), type(e).__name__)]
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
            scanned_module_names.add(name)
            try:
                # Import module in isolation
                module = importlib.import_module(name)
                # Scan correctly imported module
                module_tools = self._scan_module(module)
                discovered_tools.extend(module_tools)
                self._replace_module_tools(name, module_tools)

            except Exception as e:
                # Isolate failure
                logger.debug("Failed to scan module %s: %s", name, e)
                failed_modules.append(FailedModule(name, str(e), type(e).__name__))
                self._failed_modules.append(
                    FailedModule(name, str(e), type(e).__name__)
                )
                self._remove_module_tools(name)

        # A full package refresh must also remove modules that disappeared
        # from the package walk; otherwise removed tools remain callable.
        package_prefix = f"{package_name}."
        for module_name in tuple(self._module_tools):
            if module_name == package_name or module_name.startswith(package_prefix):
                if module_name not in scanned_module_names:
                    self._remove_module_tools(module_name)

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

    @_synchronized
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

            self._replace_module_tools(module_name, tools)

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
            self._remove_module_tools(module_name)
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

    def _remove_module_tools(self, module_name: str) -> None:
        """Remove the tools last owned by *module_name* from the registry."""
        names = self._module_tools.pop(module_name, set())
        for name in names:
            current = self._registry.get(name)
            if current is not None and current.module_path == module_name:
                self._registry.pop(name, None)

    def _replace_module_tools(
        self, module_name: str, tools: list[DiscoveredTool]
    ) -> None:
        """Atomically replace one module's discovered tool contribution."""
        self._remove_module_tools(module_name)
        owned_names: set[str] = set()
        for tool in tools:
            # Deterministic last-writer ownership prevents a stale owner from
            # deleting a replacement during a later module refresh.
            for names in self._module_tools.values():
                if tool.name in names:
                    names.discard(tool.name)
            self._registry[tool.name] = tool
            owned_names.add(tool.name)
        if owned_names:
            self._module_tools[module_name] = owned_names

    # ── Private helpers ──────────────────────────────────────────

    def _scan_module(self, module: Any) -> list[DiscoveredTool]:
        """Scan a single already-imported module for MCP tool markers."""
        tools = []

        def _add_if_tool(name: str, obj: Any) -> None:
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

                cat = str(meta.get("category", "general"))
                tag_list = manifest_tags(
                    category=cat,
                    explicit=meta.get("tags"),
                )
                tool = DiscoveredTool(
                    name=meta["name"] or name,
                    description=meta["description"] or (obj.__doc__ or "").strip(),
                    module_path=module.__name__,
                    callable_name=name,
                    parameters=meta.get("schema", meta.get("parameters", {})),
                    tags=tag_list,
                    version=meta.get("version", "1.0"),
                    requires=meta.get("requires", []),
                    available=available,
                    unavailable_reason=unavailable_reason,
                    handler=obj,
                )
                tools.append(tool)

        for name, obj in inspect.getmembers(module):
            _add_if_tool(name, obj)
            if (
                inspect.isclass(obj)
                and getattr(obj, "__module__", None) == module.__name__
            ):
                for method_name, method_obj in inspect.getmembers(obj):
                    _add_if_tool(method_name, method_obj)

        return tools

    def _update_metrics(self, report: DiscoveryReport) -> None:
        """Update internal metrics after a scan."""
        self._metrics.total_tools = len(self._registry)
        self._metrics.scan_duration_ms = report.scan_duration_ms
        self._metrics.modules_scanned = report.modules_scanned
        self._metrics.last_scan_time = datetime.now(UTC)
        self._metrics.failed_modules = [m.module for m in self._failed_modules]

    # ── Registry accessors ───────────────────────────────────────

    @_synchronized
    def register_tool(self, tool: DiscoveredTool) -> None:
        """Manually register a tool."""
        self._registry[tool.name] = tool

    @_synchronized
    def get_tool(self, name: str) -> DiscoveredTool | None:
        tool = self._registry.get(name)
        return deepcopy(tool) if tool is not None else None

    @_synchronized
    def list_tools(self, tag: str | None = None) -> list[DiscoveredTool]:
        """list all discovered tools, optionally filtered by tag."""
        tools = (
            (tool for tool in self._registry.values() if tag in tool.tags)
            if tag
            else self._registry.values()
        )
        return [
            deepcopy(tool)
            for tool in sorted(tools, key=lambda tool: (tool.name, tool.module_path))
        ]

    @property
    def tool_count(self) -> int:
        with self._lock:
            return len(self._registry)

    @_synchronized
    def record_cache_hit(self) -> None:
        """Increment cache-hit counter (called by bridge cache logic)."""
        self._metrics.cache_hits += 1

    # ── Metrics ──────────────────────────────────────────────────

    @_synchronized
    def get_metrics(self) -> DiscoveryMetrics:
        """Return a defensive copy of current discovery metrics."""
        return deepcopy(self._metrics)


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
        tags: list of tags for classification.
        version: Semantic version string.
        requires: list of importable package names required by this tool.
                  If any are missing, the tool will be registered as unavailable.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator."""
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
        except Exception as _exc:
            params = {}

        func._mcp_tool_meta = {
            "name": name,
            "description": description,
            "tags": tags or [],
            "parameters": params,
            "version": version,
            "requires": requires or [],
        }
        return func

    return decorator
