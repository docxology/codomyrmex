"""Tests for MCP tool discovery across all modules.

Verifies that @mcp_tool decorated functions are discoverable
and that the auto-discovery mechanism finds them.
"""

import importlib
import pkgutil

import pytest


@pytest.mark.unit
class TestMCPToolDiscovery:
    """Verify that mcp_tools submodules are discoverable across the codebase."""

    EXPECTED_MCP_MODULES = [
        "codomyrmex.git_operations.mcp_tools",
        "codomyrmex.containerization.mcp_tools",
        "codomyrmex.coding.mcp_tools",
        "codomyrmex.search.mcp_tools",
        "codomyrmex.formal_verification.mcp_tools",
        "codomyrmex.email.mcp_tools",
    ]

    def test_all_mcp_modules_importable(self):
        """Every expected mcp_tools module should be importable."""
        for mod_name in self.EXPECTED_MCP_MODULES:
            mod = importlib.import_module(mod_name)
            assert mod is not None, f"Failed to import {mod_name}"

    def test_each_module_has_tools(self):
        """Each mcp_tools module should have at least one @mcp_tool function."""
        for mod_name in self.EXPECTED_MCP_MODULES:
            mod = importlib.import_module(mod_name)
            tools = [
                name
                for name in dir(mod)
                if callable(getattr(mod, name))
                and hasattr(getattr(mod, name), "_mcp_tool_meta")
            ]
            assert len(tools) > 0, f"{mod_name} has no @mcp_tool decorated functions"

    def test_tool_count_by_module(self):
        """Verify minimum expected tool counts per module."""
        expected_min = {
            "codomyrmex.git_operations.mcp_tools": 12,
            "codomyrmex.containerization.mcp_tools": 4,
            "codomyrmex.coding.mcp_tools": 5,
            "codomyrmex.search.mcp_tools": 3,
            "codomyrmex.formal_verification.mcp_tools": 6,
            "codomyrmex.email.mcp_tools": 8,
        }
        for mod_name, min_count in expected_min.items():
            mod = importlib.import_module(mod_name)
            tools = [
                name
                for name in dir(mod)
                if callable(getattr(mod, name))
                and hasattr(getattr(mod, name), "_mcp_tool_meta")
            ]
            assert len(tools) >= min_count, (
                f"{mod_name}: expected >={min_count} tools, found {len(tools)}: {tools}"
            )

    def test_no_duplicate_tool_names(self):
        """Tool names must be unique across all modules."""
        seen: dict[str, str] = {}
        for mod_name in self.EXPECTED_MCP_MODULES:
            mod = importlib.import_module(mod_name)
            for name in dir(mod):
                obj = getattr(mod, name)
                if callable(obj) and hasattr(obj, "_mcp_tool_meta"):
                    if name in seen:
                        pytest.fail(
                            f"Duplicate tool name '{name}' in {mod_name} "
                            f"and {seen[name]}"
                        )
                    seen[name] = mod_name

    def test_all_tools_have_description(self):
        """Every @mcp_tool should have a non-empty description."""
        for mod_name in self.EXPECTED_MCP_MODULES:
            mod = importlib.import_module(mod_name)
            for name in dir(mod):
                obj = getattr(mod, name)
                if callable(obj) and hasattr(obj, "_mcp_tool_meta"):
                    meta = obj._mcp_tool_meta
                    assert "description" in meta, f"{mod_name}.{name} missing description"
                    assert len(meta["description"]) > 10, (
                        f"{mod_name}.{name} description too short"
                    )

    def test_all_tools_have_category(self):
        """Every @mcp_tool should have a category."""
        for mod_name in self.EXPECTED_MCP_MODULES:
            mod = importlib.import_module(mod_name)
            for name in dir(mod):
                obj = getattr(mod, name)
                if callable(obj) and hasattr(obj, "_mcp_tool_meta"):
                    meta = obj._mcp_tool_meta
                    assert "category" in meta, f"{mod_name}.{name} missing category"

    def test_total_tool_count(self):
        """Total discoverable MCP tools should be at least 30."""
        total = 0
        for mod_name in self.EXPECTED_MCP_MODULES:
            mod = importlib.import_module(mod_name)
            total += sum(
                1
                for name in dir(mod)
                if callable(getattr(mod, name))
                and hasattr(getattr(mod, name), "_mcp_tool_meta")
            )
        assert total >= 30, f"Expected ≥30 MCP tools, found {total}"
