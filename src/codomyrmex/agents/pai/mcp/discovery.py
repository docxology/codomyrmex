"""MCP dynamic tool discovery."""

import importlib
import os
import pkgutil
import threading
import time
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def tool_invalidate_cache(module: str | None = None) -> dict[str, Any]:
    """Invalidate the dynamic tool discovery cache.

    Args:
        module: Optional. If provided, invalidates and rescans only that module.
                If None, clears the entire cache.
    """
    if module:
        if _DISCOVERY_ENGINE is None:
            return {"error": "Discovery engine not initialized"}

        report = _DISCOVERY_ENGINE.scan_module(module)

        global _CACHE_EXPIRY
        _CACHE_EXPIRY = 0.0  # expired in the past → triggers refresh on next access

        return {
            "cleared": False,
            "rescanned_module": module,
            "tools_found": len(report.tools),
            "failed": bool(report.failed_modules),
        }
    invalidate_tool_cache()
    # Rescan happens lazily on next access; no stats available yet.
    return {
        "cleared": True,
        "rescanned_module": None,
        "tools_found": None,
        "failed": False,
    }


_DYNAMIC_TOOLS_CACHE: list[tuple[str, str, Any, dict[str, Any]]] | None = None

_DYNAMIC_TOOLS_CACHE_LOCK = threading.Lock()

_CACHE_EXPIRY: float | None = None  # monotonic timestamp when cache expires

_raw_ttl = os.environ.get("CODOMYRMEX_MCP_CACHE_TTL", "300")
try:
    _parsed_ttl = float(_raw_ttl)
    if not (0 < _parsed_ttl < 86400):
        raise ValueError(f"TTL out of range: {_parsed_ttl}")
    _DEFAULT_CACHE_TTL: float = _parsed_ttl
except ValueError:
    logger.warning("Invalid CODOMYRMEX_MCP_CACHE_TTL %r, using 300s", _raw_ttl)
    _DEFAULT_CACHE_TTL = 300.0

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
                parent = name.rsplit(".", 1)[0]
                parents.add(parent)

        if not parents:
            logger.warning("pkgutil walk found 0 mcp_tools modules; using fallback")
            return list(_FALLBACK_SCAN_TARGETS)

        logger.info("Auto-discovered %d modules with mcp_tools", len(parents))
        return sorted(parents)

    except (ImportError, AttributeError, OSError, RuntimeError) as exc:
        logger.exception("_find_mcp_modules failed (%s); using fallback targets", exc)
        return list(_FALLBACK_SCAN_TARGETS)


def discover_dynamic_tools() -> list[tuple[str, str, Any, dict[str, Any]]]:
    """Scan modules for @mcp_tool definitions using MCPDiscovery engine.

    Uses a TTL-based cache.
    """
    global _DYNAMIC_TOOLS_CACHE, _CACHE_EXPIRY, _DISCOVERY_ENGINE
    now = time.monotonic()
    # Fast path: check cache without holding the lock
    if (
        _DYNAMIC_TOOLS_CACHE is not None
        and _CACHE_EXPIRY is not None
        and now < _CACHE_EXPIRY
    ):
        logger.debug("Discovery cache hit (expires in %.1fs)", _CACHE_EXPIRY - now)
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
        except (ImportError, AttributeError, SyntaxError, TypeError) as e:
            logger.warning("Failed to scan package %s: %s", target, e)

    tools: list[tuple[str, str, Any, dict[str, Any]]] = []

    for tool in _DISCOVERY_ENGINE.list_tools():
        if tool.handler:
            tools.append((tool.name, tool.description, tool.handler, tool.parameters))

    elapsed_ms = (time.monotonic() - t0) * 1000
    logger.info(
        "Dynamic tools discovered: %d in %.0fms",
        len(tools),
        elapsed_ms,
    )

    with _DYNAMIC_TOOLS_CACHE_LOCK:
        # Double-check: another thread may have populated the cache while we scanned
        now2 = time.monotonic()
        if (
            _DYNAMIC_TOOLS_CACHE is not None
            and _CACHE_EXPIRY is not None
            and now2 < _CACHE_EXPIRY
        ):
            return _DYNAMIC_TOOLS_CACHE
        _DYNAMIC_TOOLS_CACHE = tools
        _CACHE_EXPIRY = now2 + _DEFAULT_CACHE_TTL

    return tools


def get_discovery_metrics() -> dict[str, Any] | None:
    """Return discovery engine metrics as a plain dict, or None if not initialized.

    Public accessor so callers (e.g. trust_gateway, server.py) don't need to
    import the private ``_DISCOVERY_ENGINE`` or instantiate a fresh scanner.

    Returns:
        Dict with keys ``total_tools``, ``modules_scanned``, ``cache_hits``,
        ``failed_modules`` (list), ``scan_duration_ms`` (float), and
        ``last_scan_time`` (datetime or None); or None if engine not yet
        initialized.
    """
    if _DISCOVERY_ENGINE is None:
        return None
    try:
        metrics = _DISCOVERY_ENGINE.get_metrics()
        return {
            "total_tools": int(getattr(metrics, "total_tools", 0)),
            "modules_scanned": int(getattr(metrics, "modules_scanned", 0)),
            "cache_hits": int(getattr(metrics, "cache_hits", 0)),
            "failed_modules": list(metrics.failed_modules),
            "scan_duration_ms": float(metrics.scan_duration_ms),
            "last_scan_time": metrics.last_scan_time,
        }
    except AttributeError:
        return None
