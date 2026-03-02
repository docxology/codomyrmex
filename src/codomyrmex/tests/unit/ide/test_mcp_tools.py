"""Unit tests for IDE MCP tools."""

import pytest

from codomyrmex.ide.mcp_tools import (
    ide_execute_command,
    ide_get_status,
    ide_list_integrations,
)


@pytest.mark.unit
def test_ide_list_integrations():
    """Test ide_list_integrations returns correct integrations."""
    result = ide_list_integrations()
    assert result["status"] == "success"
    assert "integrations" in result
    assert set(result["integrations"]) == {"antigravity", "cursor", "vscode"}


@pytest.mark.unit
def test_ide_get_status_valid_integration():
    """Test ide_get_status with a valid integration."""
    result = ide_get_status("antigravity")
    assert result["status"] == "success"
    assert result["integration"] == "antigravity"
    assert "connection_status" in result
    # We expect connecting or error if no real IDE is found,
    # but the tool logic itself shouldn't raise unhandled exceptions
    assert result["connection_status"] in ("connecting", "connected", "error", "disconnected")


@pytest.mark.unit
def test_ide_get_status_invalid_integration():
    """Test ide_get_status handles invalid integration names gracefully."""
    result = ide_get_status("invalid_ide")
    assert result["status"] == "error"
    assert "Unknown IDE integration: invalid_ide" in result["message"]


@pytest.mark.unit
def test_ide_execute_command_valid_integration():
    """Test ide_execute_command with a valid integration and simple command."""
    # Using 'antigravity' with a command that would fail safely if IDE not fully up
    result = ide_execute_command("antigravity", "some_nonexistent_command")
    assert result["status"] == "success"
    assert result["integration"] == "antigravity"
    assert "result" in result

    # execute_command_safe should catch the error and return success=False in the IDECommandResult
    command_result = result["result"]
    assert "success" in command_result
    # The actual success value will likely be False due to it being a dummy command/no IDE running
    # but the MCP tool itself should return status="success" because it didn't crash


@pytest.mark.unit
def test_ide_execute_command_invalid_integration():
    """Test ide_execute_command handles invalid integration names gracefully."""
    result = ide_execute_command("invalid_ide", "test")
    assert result["status"] == "error"
    assert "Unknown IDE integration: invalid_ide" in result["message"]
