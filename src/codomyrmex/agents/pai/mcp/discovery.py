"""MCP dynamic tool discovery."""

import importlib
import os
import pkgutil
import threading
import time
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

def _tool_invalidate_cache(module: str | None = None) -> dict[str, Any]:
    """Invalidate the dynamic tool discovery cache.

    Args:
        module: Optional. If provided, invalidates and rescans only that module.
                If None, clears the entire cache.
    """
    if module:
        # We call scan_module from discovery engine
        if _DISCOVERY_ENGINE is None:
             return {"error": "Discovery engine not initialized"}

        report = _DISCOVERY_ENGINE.scan_module(module)

        # Force a cache refresh next time get_tool_registry is called
        global _CACHE_TIMESTAMP
        _CACHE_TIMESTAMP = 0.0

        return {
             "cleared": False, # We didn't clear everything
             "rescanned_module": module,
             "tools_found": len(report.tools),
             "failed": bool(report.failed_modules)
        }
    else:
        invalidate_tool_cache()
        return {"cleared": True, "rescan_duration_ms": 0.0, "new_tool_count": 0} # stats avail on next call

_DYNAMIC_TOOLS_CACHE: list[tuple[str, str, Any, dict[str, Any]]] | None = None

_DYNAMIC_TOOLS_CACHE_LOCK = threading.Lock()

_CACHE_EXPIRY: float | None = None  # monotonic timestamp when cache expires

_DEFAULT_CACHE_TTL: float = float(os.environ.get("CODOMYRMEX_MCP_CACHE_TTL", "300"))

_DISCOVERY_ENGINE: Any | None = None

def invalidate_tool_cache() -> None:
    """Clear the dynamic tool discovery cache and its TTL."""
    global _DYNAMIC_TOOLS_CACHE, _CACHE_EXPIRY
    with _DYNAMIC_TOOLS_CACHE_LOCK:
        _DYNAMIC_TOOLS_CACHE = None
        _CACHE_EXPIRY = None
    logger.info("Dynamic tool cache invalidated")

_FALLBACK_SCAN_TARGETS = [
    "codomyrmex.data_visualization",
    "codomyrmex.llm",
    "codomyrmex.agentic_memory",
    "codomyrmex.security",
    "codomyrmex.git_operations",
    "codomyrmex.coding",
    "codomyrmex.documentation",
    "codomyrmex.email",
]

def _find_mcp_modules() -> list[str]:
    """Auto-discover all codomyrmex sub-packages that contain an ``mcp_tools`` module.

    Uses :func:`pkgutil.walk_packages` to walk the ``codomyrmex`` package tree,
    filtering for modules whose name ends with ``.mcp_tools``.  Returns the
    *parent* package name for each match (e.g. ``codomyrmex.security``).

    Falls back to :data:`_FALLBACK_SCAN_TARGETS` if the walk fails entirely.
    """
    try:
        root = importlib.import_module("codomyrmex")
        root_path = getattr(root, "__path__", None)
        if not root_path:
            return list(_FALLBACK_SCAN_TARGETS)

        parents: set[str] = set()
        for _importer, name, _ispkg in pkgutil.walk_packages(
            root_path, prefix="codomyrmex."
        ):
            if name.endswith(".mcp_tools"):
                # e.g. "codomyrmex.security.mcp_tools" -> "codomyrmex.security"
                parent = name.rsplit(".", 1)[0]
                parents.add(parent)

        if not parents:
            logger.warning("pkgutil walk found 0 mcp_tools modules; using fallback")
            return list(_FALLBACK_SCAN_TARGETS)

        logger.info("Auto-discovered %d modules with mcp_tools", len(parents))
        return sorted(parents)

    except Exception as exc:
        import traceback
        traceback.print_exc()
        logger.warning("_find_mcp_modules failed (%s); using fallback targets", exc)
        return list(_FALLBACK_SCAN_TARGETS)

def _discover_dynamic_tools() -> list[tuple[str, str, Any, dict[str, Any]]]:
    """Scan modules for @mcp_tool definitions using MCPDiscovery engine.

    Uses a TTL-based cache.
    """
    global _DYNAMIC_TOOLS_CACHE, _CACHE_EXPIRY, _DISCOVERY_ENGINE
    now = time.monotonic()
    with _DYNAMIC_TOOLS_CACHE_LOCK:
        if _DYNAMIC_TOOLS_CACHE is not None and _CACHE_EXPIRY is not None and now < _CACHE_EXPIRY:
            logger.debug("Discovery cache hit (expires in %.1fs)", _CACHE_EXPIRY - now)
            # Record cache hit if engine available
            if _DISCOVERY_ENGINE:
                 _DISCOVERY_ENGINE.record_cache_hit()
            return _DYNAMIC_TOOLS_CACHE

    if _DISCOVERY_ENGINE is None:
        from codomyrmex.model_context_protocol.discovery import MCPDiscovery
        _DISCOVERY_ENGINE = MCPDiscovery()

    t0 = time.monotonic()

    scan_targets = _find_mcp_modules()

    for target in scan_targets:
        try:
             _DISCOVERY_ENGINE.scan_package(target)
        except Exception as e:
             logger.warning(f"Failed to scan package {target}: {e}")

    tools: list[tuple[str, str, Any, dict[str, Any]]] = []

    for tool in _DISCOVERY_ENGINE.list_tools():
        if tool.handler:
            tools.append((tool.name, tool.description, tool.handler, tool.parameters))

    elapsed_ms = (time.monotonic() - t0) * 1000
    logger.info(
        "Dynamic tools discovered: %d in %.0fms",
        len(tools), elapsed_ms,
    )

    with _DYNAMIC_TOOLS_CACHE_LOCK:
        _DYNAMIC_TOOLS_CACHE = tools
        _CACHE_EXPIRY = time.monotonic() + _DEFAULT_CACHE_TTL

    return tools

