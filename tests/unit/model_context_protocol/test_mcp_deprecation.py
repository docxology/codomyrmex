"""Deprecation reporting reads ``deprecated_in`` from @mcp_tool metadata."""

from __future__ import annotations

import types

import pytest

from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.model_context_protocol.mcp_deprecation import (
    get_deprecated_tools,
    get_deprecation_summary,
    get_deprecation_timeline,
)


def _module_with_tools() -> types.ModuleType:
    module = types.ModuleType("fake_mcp_tools_module")

    @mcp_tool(category="demo", deprecated_in="1.2")
    def old_tool() -> dict:
        """Old tool."""
        return {}

    @mcp_tool(category="demo")
    def current_tool() -> dict:
        """Current tool."""
        return {}

    module.old_tool = old_tool
    module.alias = old_tool  # the same function exported twice counts once
    module.current_tool = current_tool
    module.not_a_tool = len
    return module


@pytest.mark.unit
def test_reports_only_deprecated_tools() -> None:
    tools = get_deprecated_tools([_module_with_tools()])

    assert len(tools) == 1
    assert tools[0]["deprecated_in"] == "1.2"
    assert tools[0]["description"] == "Old tool."
    assert tools[0]["name"].endswith("old_tool")


@pytest.mark.unit
def test_default_scan_covers_codomyrmex_tools() -> None:
    # No shipped tool is deprecated today; the scan must still run cleanly.
    tools = get_deprecated_tools()
    assert isinstance(tools, list)
    assert all(t["deprecated_in"] for t in tools)


@pytest.mark.unit
def test_timeline_and_summary_group_by_version() -> None:
    assert isinstance(get_deprecation_timeline(), dict)
    summary = get_deprecation_summary()
    assert summary["total_deprecated"] == len(summary["tools"])
