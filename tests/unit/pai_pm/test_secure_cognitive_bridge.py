"""Tests for the PAI secure cognitive bridge."""

from __future__ import annotations

from codomyrmex.pai_pm.secure_cognitive_bridge import (
    SECURE_COGNITIVE_MODULES,
    get_secure_cognitive_tool_catalog,
    register_secure_cognitive_tools,
)


def test_secure_cognitive_modules_registry() -> None:
    """The registry covers all 5 secure cognitive layer modules."""
    assert set(SECURE_COGNITIVE_MODULES.keys()) == {
        "identity",
        "wallet",
        "defense",
        "market",
        "privacy",
    }


def test_register_secure_cognitive_tools() -> None:
    """Registration succeeds for all modules and returns tool counts."""
    result = register_secure_cognitive_tools()
    assert result["status"] == "success"
    assert result["modules_registered"] == 5
    assert len(result["errors"]) == 0
    # Each module should have at least 1 tool
    for module_name, count in result["tool_counts"].items():
        assert count >= 1, f"{module_name} has no MCP tools"


def test_secure_cognitive_tool_catalog() -> None:
    """The catalog contains tools from all 5 modules."""
    catalog = get_secure_cognitive_tool_catalog()
    assert len(catalog) >= 15  # 3 tools × 5 modules

    modules_in_catalog = {t["module"] for t in catalog}
    assert modules_in_catalog == {
        "identity",
        "wallet",
        "defense",
        "market",
        "privacy",
    }

    # Each entry should have required fields
    for entry in catalog:
        assert "module" in entry
        assert "name" in entry
        assert "description" in entry
        assert "category" in entry
