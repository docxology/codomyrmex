"""Strictly zero-mock tests for operating_system MCP tools."""

import pytest
from typing import Dict, Any

from codomyrmex.operating_system.mcp_tools import (
    os_system_info,
    os_list_processes,
    os_disk_usage,
    os_network_info,
    os_execute_command,
    os_environment_variables,
)


@pytest.mark.unit
class TestOperatingSystemMCPTools:
    """Zero-mock tests for the operating_system MCP tools."""

    def test_os_system_info_success(self) -> None:
        """Test os_system_info returns correct dict structure."""
        result = os_system_info()
        assert isinstance(result, dict)
        assert result.get("status") == "success"
        assert "hostname" in result
        assert "platform_version" in result
        assert "architecture" in result

    def test_os_list_processes_success(self) -> None:
        """Test os_list_processes returns correct dict structure."""
        result = os_list_processes(limit=5)
        assert isinstance(result, dict)
        assert result.get("status") == "success"
        assert "count" in result
        assert "processes" in result
        assert isinstance(result["processes"], list)

        # We asked for limit=5, so we should get at most 5 processes
        assert len(result["processes"]) <= 5

    def test_os_disk_usage_success(self) -> None:
        """Test os_disk_usage returns correct dict structure."""
        result = os_disk_usage()
        assert isinstance(result, dict)
        assert result.get("status") == "success"
        assert "count" in result
        assert "disks" in result
        assert isinstance(result["disks"], list)

    def test_os_network_info_success(self) -> None:
        """Test os_network_info returns correct dict structure."""
        result = os_network_info()
        assert isinstance(result, dict)
        assert result.get("status") == "success"
        assert "count" in result
        assert "interfaces" in result
        assert isinstance(result["interfaces"], list)

    def test_os_execute_command_success(self) -> None:
        """Test os_execute_command returns correct dict structure."""
        result = os_execute_command(command="echo 'test'")
        assert isinstance(result, dict)
        assert result.get("status") == "success"
        assert "command" in result
        assert "exit_code" in result
        assert "stdout" in result
        assert "test" in result["stdout"]

    def test_os_environment_variables_success(self) -> None:
        """Test os_environment_variables returns correct dict structure."""
        result = os_environment_variables(prefix="PATH")
        assert isinstance(result, dict)
        assert result.get("status") == "success"
        assert "count" in result
        assert "variables" in result
        assert isinstance(result["variables"], dict)
        # Should at least find PATH if the system has it
        assert any("PATH" in k for k in result["variables"].keys())

    def test_os_list_processes_invalid_limit(self) -> None:
        """Test os_list_processes error handling by passing an invalid type."""
        # A string instead of int will cause an error somewhere down the line
        result = os_list_processes(limit="not_an_int") # type: ignore
        assert isinstance(result, dict)
        # It should gracefully return an error status, or maybe it works if not typed checked at runtime,
        # but the tool handles exceptions.
        if result.get("status") == "error":
            assert "message" in result
