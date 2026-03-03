"""Unit tests for the CLI module's MCP tools.

Follows the zero-mock policy by using real CLI components
for `cli_list_commands` and `cli_run_command`.
"""

import json

import pytest

from codomyrmex.cli.mcp_tools import cli_list_commands, cli_run_command


@pytest.mark.unit
def test_cli_list_commands_success():
    """Test that cli_list_commands successfully returns available commands."""
    result = cli_list_commands()

    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert "command_count" in result
    assert "commands" in result

    assert isinstance(result["commands"], list)
    assert len(result["commands"]) > 0

    # Verify that some known commands exist
    command_names = [cmd["name"] for cmd in result["commands"]]
    assert "check" in command_names
    assert "doctor" in command_names
    assert "info" in command_names

    # Verify the structure of a command entry
    first_cmd = result["commands"][0]
    assert "name" in first_cmd
    assert "description" in first_cmd


@pytest.mark.unit
def test_cli_run_command_success():
    """Test that cli_run_command successfully executes a known simple command."""
    # We run 'info' which prints info but might not explicitly return True.
    result = cli_run_command(command="info")

    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert result["command"] == "info"
    # the info handler doesn't seem to return True, it just completes and returns None
    assert result["result"] is None


@pytest.mark.unit
def test_cli_run_command_with_args():
    """Test that cli_run_command successfully parses and passes JSON args."""
    # The 'check' command takes no args, but let's see if we can run it with empty args
    # For a command that takes args, we can use 'run' or 'demo'
    # 'test' takes module_name
    args_json = json.dumps({"module_name": "cli"})

    # We can't actually run a full test here because it takes a long time or timeouts
    # Instead, we try a simple command that fails cleanly if we provide invalid args

    # doctor takes flags like 'pai'
    args_json = json.dumps({"pai": True, "workflows": False})
    result = cli_run_command(command="doctor", args=args_json)

    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert result["command"] == "doctor"
    # doctor returns exit code 0 on success
    assert result["result"] == 0


@pytest.mark.unit
def test_cli_run_command_unknown_command():
    """Test that cli_run_command handles an unknown command."""
    result = cli_run_command(command="non_existent_command_123")

    assert isinstance(result, dict)
    assert result["status"] == "error"
    assert "Unknown CLI command: non_existent_command_123" in result["message"]


@pytest.mark.unit
def test_cli_run_command_invalid_json_args():
    """Test that cli_run_command handles malformed JSON args."""
    result = cli_run_command(command="info", args="invalid_json_string")

    assert isinstance(result, dict)
    assert result["status"] == "error"
    assert "args must be a JSON object" in result.get("message", "") or "Expecting value" in result.get("message", "")


@pytest.mark.unit
def test_cli_run_command_non_dict_json_args():
    """Test that cli_run_command handles JSON args that do not parse into a dict."""
    result = cli_run_command(command="info", args='["a", "list"]')

    assert isinstance(result, dict)
    assert result["status"] == "error"
    assert "args must be a JSON object (dict)" in result["message"]
