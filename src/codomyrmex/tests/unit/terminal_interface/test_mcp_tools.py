"""Tests for terminal_interface MCP tools.

Zero-mock policy: tests use the real terminal_interface MCP tool functions.
"""

from __future__ import annotations


def test_import_mcp_tools() -> None:
    """The new MCP tools are importable without errors."""
    from codomyrmex.terminal_interface.mcp_tools import (
        terminal_get_history,
        terminal_list_shells,
        terminal_run_command,
    )

    assert callable(terminal_list_shells)
    assert callable(terminal_get_history)
    assert callable(terminal_run_command)


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.terminal_interface.mcp_tools import (
        terminal_get_history,
        terminal_list_shells,
        terminal_run_command,
    )

    for fn in (terminal_list_shells, terminal_get_history, terminal_run_command):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
        assert fn._mcp_tool_meta.get("category") == "terminal_interface"


def test_terminal_list_shells() -> None:
    """terminal_list_shells returns expected shell types."""
    from codomyrmex.terminal_interface.mcp_tools import terminal_list_shells

    result = terminal_list_shells()
    assert result.get("status") == "success"
    assert "shells" in result
    assert "interactive" in result["shells"]
    assert "standard" in result["shells"]
    assert "headless" in result["shells"]


def test_terminal_get_history() -> None:
    """terminal_get_history returns expected recent command history."""
    from codomyrmex.terminal_interface.mcp_tools import terminal_get_history

    result = terminal_get_history()
    assert result.get("status") == "success"
    assert "history" in result
    assert isinstance(result["history"], list)

    result_with_limit = terminal_get_history(limit=5)
    assert result_with_limit.get("status") == "success"
    assert len(result_with_limit["history"]) <= 5


def test_terminal_run_command_success() -> None:
    """terminal_run_command can run a safe command and capture output."""
    from codomyrmex.terminal_interface.mcp_tools import terminal_run_command

    result = terminal_run_command("echo 'hello world'")
    assert result.get("status") == "success"
    assert result.get("returncode") == 0
    assert "hello world" in result.get("stdout", "")


def test_terminal_run_command_error() -> None:
    """terminal_run_command handles error codes properly."""
    from codomyrmex.terminal_interface.mcp_tools import terminal_run_command

    result = terminal_run_command("ls /non/existent/path/for/test/xyz")
    assert result.get("status") == "success"  # The subprocess execution succeeded
    assert result.get("returncode") != 0
    assert "No such file or directory" in result.get("stderr", "") or "not found" in result.get("stderr", "")
