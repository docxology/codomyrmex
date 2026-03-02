"""Tests for environment_setup MCP tools.

Zero-mock policy: tests use the real environment checking functions.
"""

from __future__ import annotations


def test_import_mcp_tools() -> None:
    """Both MCP tools are importable without errors."""
    from codomyrmex.environment_setup.mcp_tools import env_check, env_list_deps

    assert callable(env_check)
    assert callable(env_list_deps)


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.environment_setup.mcp_tools import env_check, env_list_deps

    for fn in (env_check, env_list_deps):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
        assert fn._mcp_tool_meta.get("category") == "environment_setup"


def test_env_check_returns_dict() -> None:
    """env_check returns a dict with expected boolean keys."""
    from codomyrmex.environment_setup.mcp_tools import env_check

    result = env_check()
    assert isinstance(result, dict)
    assert "python_valid" in result
    assert "uv_available" in result
    assert "uv_environment" in result
    for key in ("python_valid", "uv_available", "uv_environment"):
        assert isinstance(result[key], bool)


def test_env_check_python_valid() -> None:
    """Python version should be valid in the test environment."""
    from codomyrmex.environment_setup.mcp_tools import env_check

    result = env_check()
    assert result["python_valid"] is True


def test_env_list_deps_returns_result() -> None:
    """env_list_deps returns a bool or dict."""
    from codomyrmex.environment_setup.mcp_tools import env_list_deps

    result = env_list_deps()
    assert isinstance(result, (bool, dict))
