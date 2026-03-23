"""MCP tools for the operating_system module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="operating_system")
def os_system_info() -> dict:
    """Retrieve system information for the current platform.

    Returns:
        Dictionary with hostname, platform, architecture, CPU count,
        memory, kernel version, and uptime.
    """
    try:
        from codomyrmex.operating_system.detector import get_system_info

        info = get_system_info()
        return {"status": "success", **info.to_dict()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="operating_system")
def os_list_processes(limit: int = 50) -> dict:
    """list running processes on the current platform.

    Args:
        limit: Maximum number of processes to return (default 50).

    Returns:
        Dictionary with a list of process information dictionaries.
    """
    try:
        from codomyrmex.operating_system.detector import list_processes

        processes = list_processes(limit=limit)
        return {
            "status": "success",
            "count": len(processes),
            "processes": [p.to_dict() for p in processes],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="operating_system")
def os_disk_usage() -> dict:
    """Return disk usage for all mounted filesystems.

    Returns:
        Dictionary with a list of disk usage entries.
    """
    try:
        from codomyrmex.operating_system.detector import get_disk_usage

        disks = get_disk_usage()
        return {
            "status": "success",
            "count": len(disks),
            "disks": [d.to_dict() for d in disks],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="operating_system")
def os_network_info() -> dict:
    """Return network interface information.

    Returns:
        Dictionary with a list of network interface entries.
    """
    try:
        from codomyrmex.operating_system.detector import get_network_interfaces

        interfaces = get_network_interfaces()
        return {
            "status": "success",
            "count": len(interfaces),
            "interfaces": [n.to_dict() for n in interfaces],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="operating_system")
def os_execute_command(command: str, timeout: float = 30.0) -> dict:
    """Execute a shell command on the current platform.

    Args:
        command: The shell command to execute.
        timeout: Timeout in seconds (default 30).

    Returns:
        Dictionary with command output, exit code, and timing.
    """
    try:
        from codomyrmex.operating_system.detector import execute_command

        result = execute_command(command, timeout=timeout)
        return {"status": "success", **result.to_dict()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="operating_system")
def os_environment_variables(prefix: str = "") -> dict:
    """Return current environment variables.

    Args:
        prefix: Optional prefix to filter variables.

    Returns:
        Dictionary with matching environment variables.
    """
    try:
        from codomyrmex.operating_system.detector import get_environment_variables

        env_vars = get_environment_variables(prefix=prefix)
        return {
            "status": "success",
            "count": len(env_vars),
            "variables": env_vars,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
