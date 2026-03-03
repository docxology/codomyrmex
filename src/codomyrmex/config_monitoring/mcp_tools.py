"""MCP tools for configuration monitoring."""

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .config_monitor import ConfigurationMonitor


@mcp_tool(category="config_monitoring")
def config_monitoring_detect_changes(
    config_paths: list[str], workspace_dir: str | None = None
) -> list[dict[str, Any]]:
    """Detect changes in configuration files.

    Args:
        config_paths: List of configuration file paths to monitor.
        workspace_dir: Optional workspace directory.

    Returns:
        List of configuration changes detected.

    """
    monitor = ConfigurationMonitor(workspace_dir)
    # Type cast needed because detect_config_changes expects list[str | Path]
    changes = monitor.detect_config_changes(list(config_paths))
    return [
        {
            "change_id": c.change_id,
            "config_path": c.config_path,
            "change_type": c.change_type,
            "timestamp": c.timestamp.isoformat(),
            "previous_hash": c.previous_hash,
            "current_hash": c.current_hash,
        }
        for c in changes
    ]


@mcp_tool(category="config_monitoring")
def config_monitoring_create_snapshot(
    environment: str, config_dir: str, workspace_dir: str | None = None
) -> dict[str, Any]:
    """Create a configuration snapshot.

    Args:
        environment: Environment name.
        config_dir: Directory containing configuration files.
        workspace_dir: Optional workspace directory.

    Returns:
        The created configuration snapshot.

    """
    monitor = ConfigurationMonitor(workspace_dir)
    snapshot = monitor.create_snapshot(environment, config_dir)
    return {
        "snapshot_id": snapshot.snapshot_id,
        "timestamp": snapshot.timestamp.isoformat(),
        "environment": snapshot.environment,
        "total_files": snapshot.total_files,
    }


@mcp_tool(category="config_monitoring")
def config_monitoring_detect_drift(
    snapshot_id: str, config_dir: str, workspace_dir: str | None = None
) -> dict[str, Any]:
    """Detect drift between a snapshot and the current configuration directory.

    Args:
        snapshot_id: ID of the snapshot to compare against.
        config_dir: Current configuration directory to compare.
        workspace_dir: Optional workspace directory.

    Returns:
        Drift analysis report.

    """
    monitor = ConfigurationMonitor(workspace_dir)
    return monitor.detect_drift(snapshot_id, config_dir)


@mcp_tool(category="config_monitoring")
def config_monitoring_audit(
    environment: str, config_dir: str, workspace_dir: str | None = None
) -> dict[str, Any]:
    """Perform a compliance audit on configuration files.

    Args:
        environment: Environment name.
        config_dir: Directory to audit.
        workspace_dir: Optional workspace directory.

    Returns:
        Audit results including compliance status and issues found.

    """
    monitor = ConfigurationMonitor(workspace_dir)
    audit = monitor.audit_configuration(environment, config_dir)
    return {
        "audit_id": audit.audit_id,
        "timestamp": audit.timestamp.isoformat(),
        "environment": audit.environment,
        "compliance_status": audit.compliance_status,
        "issues_found": audit.issues_found,
        "recommendations": audit.recommendations,
    }
