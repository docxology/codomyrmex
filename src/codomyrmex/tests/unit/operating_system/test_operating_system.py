"""Tests for the operating_system module.

Zero-mock tests — all data comes from real system queries.

Covers:
- Platform detection
- Provider dispatch
- SystemInfo (real values)
- ProcessInfo (real process listing)
- DiskInfo (real disk usage)
- CommandResult (real command execution)
- Environment variables (real env)
- NetworkInfo (real interfaces)
- Data model serialization (to_dict)
- MCP tools import
"""

import pytest

# ===================================================================
# Platform Detection
# ===================================================================


@pytest.mark.unit
class TestPlatformDetection:
    """Test platform detection returns valid enum."""

    def test_detect_platform_returns_enum(self):
        """Test functionality: detect_platform returns an OSPlatform enum."""
        from codomyrmex.operating_system.base import OSPlatform
        from codomyrmex.operating_system.detector import detect_platform

        result = detect_platform()
        assert isinstance(result, OSPlatform)
        assert result != OSPlatform.UNKNOWN

    def test_detect_platform_matches_system(self):
        """Test functionality: detected platform matches platform.system()."""
        import platform

        from codomyrmex.operating_system.detector import detect_platform

        result = detect_platform()
        system = platform.system().lower()
        expected_map = {"darwin": "macos", "linux": "linux", "windows": "windows"}
        assert result.value == expected_map.get(system, "unknown")


# ===================================================================
# Provider Dispatch
# ===================================================================


@pytest.mark.unit
class TestProviderDispatch:
    """Test provider dispatch returns correct platform provider."""

    def test_get_provider_returns_base_subclass(self):
        """Test functionality: get_provider returns an OSProviderBase subclass."""
        from codomyrmex.operating_system.base import OSProviderBase
        from codomyrmex.operating_system.detector import get_provider

        provider = get_provider()
        assert isinstance(provider, OSProviderBase)

    def test_get_provider_is_cached(self):
        """Test functionality: get_provider returns same instance on repeat call."""
        from codomyrmex.operating_system.detector import get_provider

        p1 = get_provider()
        p2 = get_provider()
        assert p1 is p2

    def test_provider_class_name_matches_platform(self):
        """Test functionality: provider class name matches detected platform."""
        import platform as _platform

        from codomyrmex.operating_system.detector import get_provider

        provider = get_provider()
        system = _platform.system().lower()
        class_name = type(provider).__name__.lower()
        if system == "darwin":
            assert "macos" in class_name or "mac" in class_name
        elif system == "linux":
            assert "linux" in class_name
        elif system == "windows":
            assert "windows" in class_name


# ===================================================================
# System Info (real data)
# ===================================================================


@pytest.mark.unit
class TestSystemInfo:
    """Test real system information retrieval."""

    def test_get_system_info(self):
        """Test functionality: get_system_info returns populated SystemInfo."""
        from codomyrmex.operating_system.detector import get_system_info

        info = get_system_info()
        assert info.hostname != ""
        assert info.cpu_count >= 1
        assert info.architecture != ""
        assert info.kernel_version != ""

    def test_system_info_to_dict(self):
        """Test functionality: SystemInfo.to_dict produces valid dict."""
        from codomyrmex.operating_system.detector import get_system_info

        info = get_system_info()
        d = info.to_dict()
        assert "hostname" in d
        assert "platform" in d
        assert "cpu_count" in d
        assert "memory_total_bytes" in d

    def test_memory_is_positive(self):
        """Test functionality: memory_total_bytes is a positive integer."""
        from codomyrmex.operating_system.detector import get_system_info

        info = get_system_info()
        assert info.memory_total_bytes > 0

    def test_platform_version_populated(self):
        """Test functionality: platform_version is non-empty."""
        from codomyrmex.operating_system.detector import get_system_info

        info = get_system_info()
        assert info.platform_version != ""


# ===================================================================
# Processes (real data)
# ===================================================================


@pytest.mark.unit
class TestProcesses:
    """Test real process listing."""

    def test_list_processes_returns_list(self):
        """Test functionality: list_processes returns a non-empty list."""
        from codomyrmex.operating_system.detector import list_processes

        procs = list_processes(limit=10)
        assert isinstance(procs, list)
        assert len(procs) > 0

    def test_process_has_pid(self):
        """Test functionality: each process has a positive pid."""
        from codomyrmex.operating_system.detector import list_processes

        procs = list_processes(limit=5)
        for p in procs:
            assert p.pid > 0

    def test_process_has_name(self):
        """Test functionality: each process has a non-empty name."""
        from codomyrmex.operating_system.detector import list_processes

        procs = list_processes(limit=5)
        for p in procs:
            assert p.name != ""

    def test_process_to_dict(self):
        """Test functionality: ProcessInfo.to_dict produces valid dict."""
        from codomyrmex.operating_system.detector import list_processes

        procs = list_processes(limit=1)
        if procs:
            d = procs[0].to_dict()
            assert "pid" in d
            assert "name" in d
            assert "status" in d


# ===================================================================
# Disk Usage (real data)
# ===================================================================


@pytest.mark.unit
class TestDiskUsage:
    """Test real disk usage retrieval."""

    def test_get_disk_usage_returns_list(self):
        """Test functionality: get_disk_usage returns a list."""
        from codomyrmex.operating_system.detector import get_disk_usage

        disks = get_disk_usage()
        assert isinstance(disks, list)
        assert len(disks) > 0

    def test_disk_has_mountpoint(self):
        """Test functionality: each disk has a mountpoint."""
        from codomyrmex.operating_system.detector import get_disk_usage

        disks = get_disk_usage()
        for d in disks:
            assert d.mountpoint != ""

    def test_disk_total_positive(self):
        """Test functionality: disk total_bytes is positive."""
        from codomyrmex.operating_system.detector import get_disk_usage

        disks = get_disk_usage()
        for d in disks:
            assert d.total_bytes > 0

    def test_disk_to_dict(self):
        """Test functionality: DiskInfo.to_dict produces valid dict."""
        from codomyrmex.operating_system.detector import get_disk_usage

        disks = get_disk_usage()
        if disks:
            d = disks[0].to_dict()
            assert "device" in d
            assert "total_bytes" in d
            assert "percent_used" in d


# ===================================================================
# Command Execution (real)
# ===================================================================


@pytest.mark.unit
class TestCommandExecution:
    """Test real command execution."""

    def test_execute_echo(self):
        """Test functionality: execute echo command."""
        from codomyrmex.operating_system.detector import execute_command

        result = execute_command("echo hello_os_test")
        assert result.success
        assert "hello_os_test" in result.stdout

    def test_execute_returns_duration(self):
        """Test functionality: execute_command records duration_ms."""
        from codomyrmex.operating_system.detector import execute_command

        result = execute_command("echo fast")
        assert result.duration_ms >= 0

    def test_execute_bad_command(self):
        """Test functionality: non-zero exit code for bad command."""
        from codomyrmex.operating_system.detector import execute_command

        result = execute_command("false")
        assert not result.success

    def test_command_result_to_dict(self):
        """Test functionality: CommandResult.to_dict produces valid dict."""
        from codomyrmex.operating_system.detector import execute_command

        result = execute_command("echo test")
        d = result.to_dict()
        assert "command" in d
        assert "exit_code" in d
        assert "success" in d


# ===================================================================
# Environment Variables (real)
# ===================================================================


@pytest.mark.unit
class TestEnvironmentVariables:
    """Test real environment variable retrieval."""

    def test_get_all_env_vars(self):
        """Test functionality: get_environment_variables returns dict."""
        from codomyrmex.operating_system.detector import get_environment_variables

        env = get_environment_variables()
        assert isinstance(env, dict)
        assert len(env) > 0

    def test_path_in_env(self):
        """Test functionality: PATH variable exists."""
        from codomyrmex.operating_system.detector import get_environment_variables

        env = get_environment_variables()
        assert "PATH" in env

    def test_filter_by_prefix(self):
        """Test functionality: prefix filter works."""
        from codomyrmex.operating_system.detector import get_environment_variables

        env = get_environment_variables(prefix="PATH")
        assert all(k.startswith("PATH") for k in env)


# ===================================================================
# Network Interfaces (real)
# ===================================================================


@pytest.mark.unit
class TestNetworkInterfaces:
    """Test real network interface retrieval."""

    def test_get_network_interfaces_returns_list(self):
        """Test functionality: get_network_interfaces returns list."""
        from codomyrmex.operating_system.detector import get_network_interfaces

        ifaces = get_network_interfaces()
        assert isinstance(ifaces, list)
        assert len(ifaces) > 0

    def test_interface_has_name(self):
        """Test functionality: each interface has a name."""
        from codomyrmex.operating_system.detector import get_network_interfaces

        ifaces = get_network_interfaces()
        for iface in ifaces:
            assert iface.interface != ""

    def test_network_info_to_dict(self):
        """Test functionality: NetworkInfo.to_dict produces valid dict."""
        from codomyrmex.operating_system.detector import get_network_interfaces

        ifaces = get_network_interfaces()
        if ifaces:
            d = ifaces[0].to_dict()
            assert "interface" in d
            assert "is_up" in d


# ===================================================================
# Data Models & ABC
# ===================================================================


@pytest.mark.unit
class TestDataModels:
    """Test data model types and ABC enforcement."""

    def test_os_platform_enum_values(self):
        """Test functionality: OSPlatform enum has expected values."""
        from codomyrmex.operating_system.base import OSPlatform

        assert OSPlatform.MACOS.value == "macos"
        assert OSPlatform.LINUX.value == "linux"
        assert OSPlatform.WINDOWS.value == "windows"
        assert OSPlatform.UNKNOWN.value == "unknown"

    def test_service_status_enum(self):
        """Test functionality: ServiceStatus enum values."""
        from codomyrmex.operating_system.base import ServiceStatus

        assert ServiceStatus.RUNNING.value == "running"
        assert ServiceStatus.STOPPED.value == "stopped"

    def test_process_status_enum(self):
        """Test functionality: ProcessStatus enum values."""
        from codomyrmex.operating_system.base import ProcessStatus

        assert ProcessStatus.RUNNING.value == "running"
        assert ProcessStatus.ZOMBIE.value == "zombie"

    def test_cannot_instantiate_base_directly(self):
        """Test functionality: OSProviderBase cannot be instantiated directly."""
        from codomyrmex.operating_system.base import OSProviderBase

        with pytest.raises(TypeError):
            OSProviderBase()


# ===================================================================
# MCP Tools Import
# ===================================================================


@pytest.mark.unit
class TestMCPTools:
    """Test MCP tools import and callable."""

    def test_import_mcp_tools(self):
        """Test functionality: mcp_tools module imports cleanly."""
        from codomyrmex.operating_system import mcp_tools

        assert hasattr(mcp_tools, "os_system_info")
        assert hasattr(mcp_tools, "os_list_processes")
        assert hasattr(mcp_tools, "os_disk_usage")
        assert hasattr(mcp_tools, "os_network_info")
        assert hasattr(mcp_tools, "os_execute_command")
        assert hasattr(mcp_tools, "os_environment_variables")

    def test_mcp_tools_callable(self):
        """Test functionality: MCP tool functions are callable."""
        from codomyrmex.operating_system import mcp_tools

        assert callable(mcp_tools.os_system_info)
        assert callable(mcp_tools.os_execute_command)


# ===================================================================
# Module-Level Imports
# ===================================================================


@pytest.mark.unit
class TestModuleImports:
    """Test top-level module imports."""

    def test_import_operating_system(self):
        """Test functionality: operating_system module imports."""
        import codomyrmex.operating_system as os_mod

        assert hasattr(os_mod, "detect_platform")
        assert hasattr(os_mod, "get_system_info")
        assert hasattr(os_mod, "OSPlatform")
        assert hasattr(os_mod, "SystemInfo")

    def test_cli_commands(self):
        """Test functionality: cli_commands returns dict."""
        from codomyrmex.operating_system import cli_commands

        cmds = cli_commands()
        assert isinstance(cmds, dict)
        assert "info" in cmds
        assert "platform" in cmds
