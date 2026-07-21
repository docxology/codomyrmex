"""PAI bridge for the Secure Cognitive Layer.

Registers MCP tools from identity, wallet, defense, market, and privacy
modules so they are discoverable by the PAI system and external MCP clients.

Usage::

    from codomyrmex.pai_pm.secure_cognitive_bridge import register_secure_cognitive_tools
    register_secure_cognitive_tools()

    # Or query the registry:
    from codomyrmex.pai_pm.secure_cognitive_bridge import SECURE_COGNITIVE_MODULES
    print(f"{len(SECURE_COGNITIVE_MODULES)} secure cognitive modules registered")
"""

from __future__ import annotations

from typing import Any

# Registry of secure cognitive layer modules and their MCP tool modules.
# Each entry maps a module name to its mcp_tools import path.
SECURE_COGNITIVE_MODULES: dict[str, str] = {
    "identity": "codomyrmex.identity.mcp_tools",
    "wallet": "codomyrmex.wallet.mcp_tools",
    "defense": "codomyrmex.defense.mcp_tools",
    "market": "codomyrmex.market.mcp_tools",
    "privacy": "codomyrmex.privacy.mcp_tools",
}


def register_secure_cognitive_tools() -> dict[str, Any]:
    """Import all secure cognitive layer MCP tool modules.

    This triggers ``@mcp_tool`` decorator registration for each module,
    making the tools discoverable by the MCP discovery system.

    Returns:
        dict with keys: status, modules_registered, tool_counts, errors
    """
    results: dict[str, Any] = {
        "status": "success",
        "modules_registered": 0,
        "tool_counts": {},
        "errors": [],
    }

    for module_name, import_path in SECURE_COGNITIVE_MODULES.items():
        try:
            import importlib

            mod = importlib.import_module(import_path)
            # Count @mcp_tool decorated functions
            tool_count = sum(
                1
                for attr_name in dir(mod)
                if not attr_name.startswith("_")
                and hasattr(getattr(mod, attr_name), "_mcp_tool_meta")
            )
            results["tool_counts"][module_name] = tool_count
            results["modules_registered"] += 1
        except Exception as exc:
            results["errors"].append(
                f"Failed to register {module_name}: {exc}"
            )

    if results["errors"] and results["modules_registered"] == 0:
        results["status"] = "error"
    elif results["errors"]:
        results["status"] = "partial"

    return results


def get_secure_cognitive_tool_catalog() -> list[dict[str, str]]:
    """Return a catalog of all secure cognitive layer MCP tools.

    Each entry contains: module, name, description, category.
    """
    catalog: list[dict[str, str]] = []
    for module_name, import_path in SECURE_COGNITIVE_MODULES.items():
        try:
            import importlib

            mod = importlib.import_module(import_path)
            for attr_name in dir(mod):
                if attr_name.startswith("_"):
                    continue
                attr = getattr(mod, attr_name)
                meta = getattr(attr, "_mcp_tool_meta", None)
                if meta:
                    catalog.append({
                        "module": module_name,
                        "name": getattr(attr, "__name__", attr_name),
                        "description": meta.get("description", ""),
                        "category": meta.get("category", module_name),
                    })
        except Exception:
            pass
    return catalog


__all__ = [
    "SECURE_COGNITIVE_MODULES",
    "get_secure_cognitive_tool_catalog",
    "register_secure_cognitive_tools",
]
