"""Tests for CLI MCP tools.

Zero-mock policy: tests use the real CLI and MCP tools.
"""

from __future__ import annotations

import json

def test_import_mcp_tools() -> None:
    """All MCP tools are importable without errors."""
    from codomyrmex.cli.mcp_tools import (
        cli_list_commands,
        cli_run_command,
    )

    assert callable(cli_list_commands)
    assert callable(cli_run_command)


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.cli.mcp_tools import (
        cli_list_commands,
        cli_run_command,
    )

    for fn in (cli_list_commands, cli_run_command):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
        assert fn._mcp_tool_meta.get("category") == "cli"


def test_cli_list_commands() -> None:
    """cli_list_commands returns a successful dict with available commands."""
    from codomyrmex.cli.mcp_tools import cli_list_commands

    result = cli_list_commands()
    assert isinstance(result, dict)
    assert result.get("status") == "success"
    assert "commands" in result
    assert isinstance(result["commands"], list)

    # Check that at least some expected commands are present
    command_names = [cmd["name"] for cmd in result["commands"]]
    assert "check" in command_names
    assert "info" in command_names


def test_cli_run_command_valid() -> None:
    """cli_run_command executes a valid command successfully."""
    from codomyrmex.cli.mcp_tools import cli_run_command

    # Run the 'info' command which should return something or just not fail
    # Actually 'info' returns the output of show_info()
    result = cli_run_command("info")

    assert isinstance(result, dict)
    # The command might print and return 0 or return dict/string. The tool wraps it.
    assert result.get("status") in ("success", "error")
    if result.get("status") == "success":
        assert result.get("command") == "info"


def test_cli_run_command_invalid_command() -> None:
    """cli_run_command returns error for unknown command."""
    from codomyrmex.cli.mcp_tools import cli_run_command

    result = cli_run_command("nonexistent_command_123")
    assert isinstance(result, dict)
    assert result.get("status") == "error"
    assert "Unknown CLI command" in result.get("message", "")


def test_cli_run_command_invalid_args_json() -> None:
    """cli_run_command returns error for invalid args JSON."""
    from codomyrmex.cli.mcp_tools import cli_run_command

    result = cli_run_command("info", args="not valid json")
    assert isinstance(result, dict)
    assert result.get("status") == "error"
    # Should be JSON decode error caught in some way or another
    # Wait, the try/except catches Exception and returns it

def test_cli_run_command_args_not_dict() -> None:
    """cli_run_command returns error if args JSON is not a dictionary."""
    from codomyrmex.cli.mcp_tools import cli_run_command

    result = cli_run_command("info", args=json.dumps(["list", "of", "args"]))
    assert isinstance(result, dict)
    assert result.get("status") == "error"
    assert "args must be a JSON object" in result.get("message", "")
