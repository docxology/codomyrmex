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
        from codomyrmex.operating_system.base import OSPlatform
        from codomyrmex.operating_system.detector import detect_platform
        result = detect_platform()
        assert isinstance(result, OSPlatform)
        assert result != OSPlatform.UNKNOWN

    def test_detect_platform_matches_system(self):
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
        from codomyrmex.operating_system.base import OSProviderBase
        from codomyrmex.operating_system.detector import get_provider
        provider = get_provider()
        assert isinstance(provider, OSProviderBase)

    def test_get_provider_is_cached(self):
        from codomyrmex.operating_system.detector import get_provider
        p1 = get_provider()
        p2 = get_provider()
        assert p1 is p2

    def test_provider_class_name_matches_platform(self):
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
        from codomyrmex.operating_system.detector import get_system_info
        info = get_system_info()
        assert info.hostname != ""
        assert info.cpu_count >= 1
        assert info.architecture != ""
        assert info.kernel_version != ""

    def test_system_info_to_dict(self):
        from codomyrmex.operating_system.detector import get_system_info
        info = get_system_info()
        d = info.to_dict()
        assert "hostname" in d
        assert "platform" in d
        assert "cpu_count" in d
        assert "memory_total_bytes" in d

    def test_memory_is_positive(self):
        from codomyrmex.operating_system.detector import get_system_info
        info = get_system_info()
        assert info.memory_total_bytes > 0

    def test_platform_version_populated(self):
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
        from codomyrmex.operating_system.detector import list_processes
        procs = list_processes(limit=10)
        assert isinstance(procs, list)
        assert len(procs) > 0

    def test_process_has_pid(self):
        from codomyrmex.operating_system.detector import list_processes
        procs = list_processes(limit=5)
        for p in procs:
            assert p.pid > 0

    def test_process_has_name(self):
        from codomyrmex.operating_system.detector import list_processes
        procs = list_processes(limit=5)
        for p in procs:
            assert p.name != ""

    def test_process_to_dict(self):
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
        from codomyrmex.operating_system.detector import get_disk_usage
        disks = get_disk_usage()
        assert isinstance(disks, list)
        assert len(disks) > 0

    def test_disk_has_mountpoint(self):
        from codomyrmex.operating_system.detector import get_disk_usage
        disks = get_disk_usage()
        for d in disks:
            assert d.mountpoint != ""

    def test_disk_total_positive(self):
        from codomyrmex.operating_system.detector import get_disk_usage
        disks = get_disk_usage()
        for d in disks:
            assert d.total_bytes > 0

    def test_disk_to_dict(self):
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
        from codomyrmex.operating_system.detector import execute_command
        result = execute_command("echo hello_os_test")
        assert result.success
        assert "hello_os_test" in result.stdout

    def test_execute_returns_duration(self):
        from codomyrmex.operating_system.detector import execute_command
        result = execute_command("echo fast")
        assert result.duration_ms >= 0

    def test_execute_bad_command(self):
        from codomyrmex.operating_system.detector import execute_command
        result = execute_command("false")
        assert not result.success

    def test_command_result_to_dict(self):
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
        from codomyrmex.operating_system.detector import get_environment_variables
        env = get_environment_variables()
        assert isinstance(env, dict)
        assert len(env) > 0

    def test_path_in_env(self):
        from codomyrmex.operating_system.detector import get_environment_variables
        env = get_environment_variables()
        assert "PATH" in env

    def test_filter_by_prefix(self):
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
        from codomyrmex.operating_system.detector import get_network_interfaces
        ifaces = get_network_interfaces()
        assert isinstance(ifaces, list)
        assert len(ifaces) > 0

    def test_interface_has_name(self):
        from codomyrmex.operating_system.detector import get_network_interfaces
        ifaces = get_network_interfaces()
        for iface in ifaces:
            assert iface.interface != ""

    def test_network_info_to_dict(self):
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
        from codomyrmex.operating_system.base import OSPlatform
        assert OSPlatform.MACOS.value == "macos"
        assert OSPlatform.LINUX.value == "linux"
        assert OSPlatform.WINDOWS.value == "windows"
        assert OSPlatform.UNKNOWN.value == "unknown"

    def test_service_status_enum(self):
        from codomyrmex.operating_system.base import ServiceStatus
        assert ServiceStatus.RUNNING.value == "running"
        assert ServiceStatus.STOPPED.value == "stopped"

    def test_process_status_enum(self):
        from codomyrmex.operating_system.base import ProcessStatus
        assert ProcessStatus.RUNNING.value == "running"
        assert ProcessStatus.ZOMBIE.value == "zombie"

    def test_cannot_instantiate_base_directly(self):
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
        from codomyrmex.operating_system import mcp_tools
        assert hasattr(mcp_tools, "os_system_info")
        assert hasattr(mcp_tools, "os_list_processes")
        assert hasattr(mcp_tools, "os_disk_usage")
        assert hasattr(mcp_tools, "os_network_info")
        assert hasattr(mcp_tools, "os_execute_command")
        assert hasattr(mcp_tools, "os_environment_variables")

    def test_mcp_tools_callable(self):
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
        import codomyrmex.operating_system as os_mod
        assert hasattr(os_mod, "detect_platform")
        assert hasattr(os_mod, "get_system_info")
        assert hasattr(os_mod, "OSPlatform")
        assert hasattr(os_mod, "SystemInfo")

    def test_cli_commands(self):
        from codomyrmex.operating_system import cli_commands
        cmds = cli_commands()
        assert isinstance(cmds, dict)
        assert "info" in cmds
        assert "platform" in cmds
