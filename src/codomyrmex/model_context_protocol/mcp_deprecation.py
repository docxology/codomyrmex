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

import importlib
import logging
import pkgutil
from collections.abc import Iterable, Iterator
from types import ModuleType
from typing import Any

try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


def _mcp_tool_modules() -> Iterator[ModuleType]:
    """Import every ``codomyrmex.*.mcp_tools`` module.

    Modules are found at run time with ``pkgutil``, like the tool listing in
    ``model_context_protocol.mcp_tools``; a module that fails to import is
    logged and skipped so one broken integration does not hide the rest.
    """
    import codomyrmex

    def _on_package_error(name: str) -> None:
        logger.warning("Could not import package %s while scanning MCP tools", name)

    for _, modname, _ in pkgutil.walk_packages(
        codomyrmex.__path__, prefix="codomyrmex.", onerror=_on_package_error
    ):
        if modname.rsplit(".", 1)[-1] != "mcp_tools":
            continue
        try:
            yield importlib.import_module(modname)
        except Exception as e:
            logger.warning(
                "Could not import %s while scanning MCP tools: %s", modname, e
            )


def get_deprecated_tools(
    modules: Iterable[ModuleType] | None = None,
) -> list[dict[str, Any]]:
    """List ``@mcp_tool`` functions whose ``deprecated_in`` is set.

    Args:
        modules: Modules to inspect. Defaults to every ``codomyrmex`` module
            named ``mcp_tools``.

    Returns:
        list of dicts with keys: ``name``, ``module``, ``deprecated_in``,
        ``description``.
    """
    deprecated: list[dict[str, Any]] = []
    seen: set[int] = set()
    for module in _mcp_tool_modules() if modules is None else modules:
        for obj in vars(module).values():
            meta = getattr(obj, "_mcp_tool_meta", None)
            if not callable(obj) or not isinstance(meta, dict) or id(obj) in seen:
                continue
            seen.add(id(obj))
            dep_version = meta.get("deprecated_in")
            if dep_version:
                deprecated.append(
                    {
                        "name": meta.get("name") or obj.__name__,
                        "module": meta.get("module", module.__name__),
                        "deprecated_in": dep_version,
                        "description": meta.get("description", ""),
                    }
                )

    logger.info("Found %d deprecated MCP tools", len(deprecated))
    return deprecated


def get_deprecation_timeline() -> dict[str, list[dict[str, Any]]]:
    """Group deprecated tools by the version they were deprecated in.

    Returns:
        dict mapping version strings to lists of deprecated tool info dicts.
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
        dict with keys: ``total_deprecated``, ``by_version`` (counts),
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
    "get_deprecation_summary",
    "get_deprecation_timeline",
]
