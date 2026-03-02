"""Tests for feature_flags MCP tools.

Zero-mock policy: tests use the real FlagDefinition + FlagEvaluator via the
MCP tool functions.  The module-level _flags dict is reset between tests.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def reset_flags():
    """Clear the module-level flag registry before and after each test."""
    import codomyrmex.feature_flags.mcp_tools as _mod
    _mod._flags.clear()
    yield
    _mod._flags.clear()


def test_import_mcp_tools() -> None:
    """All three MCP tools are importable without errors."""
    from codomyrmex.feature_flags.mcp_tools import (
        flag_create,
        flag_is_enabled,
        flag_list,
    )
    assert callable(flag_create)
    assert callable(flag_is_enabled)
    assert callable(flag_list)


def test_flag_list_empty() -> None:
    """flag_list returns empty list when no flags are registered."""
    from codomyrmex.feature_flags.mcp_tools import flag_list

    assert flag_list() == []


def test_flag_create_returns_dict() -> None:
    """flag_create returns a dict with key, enabled, and percentage."""
    from codomyrmex.feature_flags.mcp_tools import flag_create

    result = flag_create("my_feature", enabled=True, percentage=100.0)
    assert result["key"] == "my_feature"
    assert result["enabled"] is True
    assert result["percentage"] == 100.0


def test_flag_create_adds_to_list() -> None:
    """Creating a flag makes it appear in flag_list."""
    from codomyrmex.feature_flags.mcp_tools import flag_create, flag_list

    flag_create("feat_a")
    flag_create("feat_b")
    names = [f["key"] for f in flag_list()]
    assert "feat_a" in names
    assert "feat_b" in names


def test_flag_is_enabled_for_enabled_flag() -> None:
    """flag_is_enabled returns True for a fully-enabled flag."""
    from codomyrmex.feature_flags.mcp_tools import flag_create, flag_is_enabled

    flag_create("always_on", enabled=True, percentage=100.0)
    assert flag_is_enabled("always_on") is True


def test_flag_is_enabled_for_disabled_flag() -> None:
    """flag_is_enabled returns False when the global kill-switch is off."""
    from codomyrmex.feature_flags.mcp_tools import flag_create, flag_is_enabled

    flag_create("always_off", enabled=False)
    assert flag_is_enabled("always_off") is False


def test_flag_is_enabled_unknown_flag() -> None:
    """flag_is_enabled returns False for an unknown flag key."""
    from codomyrmex.feature_flags.mcp_tools import flag_is_enabled

    assert flag_is_enabled("nonexistent_flag_xyzzy") is False


def test_flag_is_enabled_zero_percent() -> None:
    """flag_is_enabled returns False for a 0% rollout."""
    from codomyrmex.feature_flags.mcp_tools import flag_create, flag_is_enabled

    flag_create("zero_rollout", enabled=True, percentage=0.0)
    # With 0% rollout, all users should be excluded
    assert flag_is_enabled("zero_rollout", user_id="any_user") is False


def test_flag_create_overwrites_existing() -> None:
    """Creating a flag with the same key updates the existing flag."""
    from codomyrmex.feature_flags.mcp_tools import flag_create, flag_is_enabled

    flag_create("toggle", enabled=True)
    assert flag_is_enabled("toggle") is True
    flag_create("toggle", enabled=False)
    assert flag_is_enabled("toggle") is False


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.feature_flags.mcp_tools import (
        flag_create,
        flag_is_enabled,
        flag_list,
    )
    for fn in (flag_create, flag_is_enabled, flag_list):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
