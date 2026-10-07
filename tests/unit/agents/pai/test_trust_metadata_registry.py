"""Trust classification entries must name tools that are actually registered.

Regression: ``EXPLICIT_SAFE_TOOLS`` listed ``codomyrmex.tool_list_modules`` /
``codomyrmex.tool_module_info`` (the Python function names), but the tools are
registered as ``codomyrmex.list_modules`` / ``codomyrmex.module_info``. The
fail-closed default therefore treated the read-only module listing as
destructive, so ``verify_all_safe()`` could never make it callable and
``call_tool("codomyrmex.list_modules")`` required full TRUSTED status.
"""

from __future__ import annotations

import pytest

from codomyrmex.agents.pai.mcp.trust_metadata import (
    EXPLICIT_DESTRUCTIVE_TOOLS,
    EXPLICIT_SAFE_TOOLS,
    is_destructive_tool,
)
from codomyrmex.agents.pai.mcp_bridge import get_tool_registry


@pytest.fixture(scope="module")
def registered_tools() -> set[str]:
    return set(get_tool_registry().list_tools())


@pytest.mark.unit
def test_every_explicit_safe_tool_is_registered(registered_tools: set[str]) -> None:
    assert registered_tools >= EXPLICIT_SAFE_TOOLS, sorted(
        EXPLICIT_SAFE_TOOLS - registered_tools
    )


@pytest.mark.unit
def test_every_explicit_destructive_tool_is_registered(
    registered_tools: set[str],
) -> None:
    assert registered_tools >= EXPLICIT_DESTRUCTIVE_TOOLS, sorted(
        EXPLICIT_DESTRUCTIVE_TOOLS - registered_tools
    )


@pytest.mark.unit
def test_safe_and_destructive_sets_are_disjoint() -> None:
    assert not (EXPLICIT_SAFE_TOOLS & EXPLICIT_DESTRUCTIVE_TOOLS)


@pytest.mark.unit
@pytest.mark.parametrize("name", ["codomyrmex.list_modules", "codomyrmex.module_info"])
def test_read_only_module_introspection_is_safe(name: str) -> None:
    assert is_destructive_tool(name) is False


@pytest.mark.unit
@pytest.mark.parametrize(
    "name",
    [
        "codomyrmex.write_file",
        "codomyrmex.run_command",
        "codomyrmex.tool_list_modules",  # not a registered name: fail closed
        "codomyrmex.some_new_dynamic_tool",
        None,
    ],
)
def test_unlisted_or_mutating_tools_fail_closed(name) -> None:
    assert is_destructive_tool(name) is True


@pytest.mark.unit
def test_verify_all_safe_makes_list_modules_callable(tmp_path) -> None:
    from codomyrmex.agents.pai import trust_gateway

    registry = trust_gateway._registry
    registry.configure_ledger_path(tmp_path / "ledger.json", load_existing=False)
    assert "codomyrmex.list_modules" in registry.verify_all_safe()
    result = trust_gateway.trusted_call_tool("codomyrmex.list_modules")
    assert "modules" in result
