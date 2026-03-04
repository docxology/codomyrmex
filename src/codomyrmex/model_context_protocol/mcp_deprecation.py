"""MCP Deprecation Timeline — surface ``deprecated_in`` metadata from @mcp_tool.

Provides programmatic access to the deprecation timeline for MCP tools,
enabling dashboard UIs and CLI commands to display which tools are
deprecated and when they will be removed.

Example::

    >>> from codomyrmex.model_context_protocol.mcp_deprecation import (
    ...     get_deprecated_tools,
    ...     get_deprecation_timeline,
    ... )
    >>> deprecated = get_deprecated_tools()
    >>> for tool in deprecated:
    ...     print(f"{tool['name']} deprecated in v{tool['deprecated_in']}")
    >>> timeline = get_deprecation_timeline()
    >>> for version, tools in timeline.items():
    ...     print(f"v{version}: {len(tools)} tools deprecated")
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


def get_deprecated_tools() -> list[dict[str, Any]]:
    """Scan the MCP tool registry for tools with ``deprecated_in`` set.

    Returns:
        List of dicts with keys: ``name``, ``module``, ``deprecated_in``,
        ``description``.
    """
    deprecated: list[dict[str, Any]] = []

    try:
        from codomyrmex.model_context_protocol import get_all_tools
        tools = get_all_tools()
    except ImportError:
        logger.warning("MCP get_all_tools not available")
        return deprecated

    for tool in tools:
        meta = getattr(tool, "metadata", {}) or {}
        dep_version = meta.get("deprecated_in")
        if dep_version:
            deprecated.append({
                "name": getattr(tool, "name", str(tool)),
                "module": getattr(tool, "module", "unknown"),
                "deprecated_in": dep_version,
                "description": getattr(tool, "description", ""),
            })

    logger.info("Found %d deprecated MCP tools", len(deprecated))
    return deprecated


def get_deprecation_timeline() -> dict[str, list[dict[str, Any]]]:
    """Group deprecated tools by the version they were deprecated in.

    Returns:
        Dict mapping version strings to lists of deprecated tool info dicts.
        Sorted by version (ascending).
    """
    deprecated = get_deprecated_tools()
    timeline: dict[str, list[dict[str, Any]]] = {}

    for tool in deprecated:
        version = tool["deprecated_in"]
        timeline.setdefault(version, []).append(tool)

    # Sort by version
    return dict(sorted(timeline.items()))


def get_deprecation_summary() -> dict[str, Any]:
    """Get a high-level summary of the deprecation status.

    Returns:
        Dict with keys: ``total_deprecated``, ``by_version`` (counts),
        ``tools`` (full list).
    """
    deprecated = get_deprecated_tools()
    by_version: dict[str, int] = {}
    for tool in deprecated:
        v = tool["deprecated_in"]
        by_version[v] = by_version.get(v, 0) + 1

    return {
        "total_deprecated": len(deprecated),
        "by_version": dict(sorted(by_version.items())),
        "tools": deprecated,
    }


__all__ = [
    "get_deprecated_tools",
    "get_deprecation_timeline",
    "get_deprecation_summary",
]
