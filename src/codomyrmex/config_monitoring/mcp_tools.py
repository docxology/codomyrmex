"""MCP Tools for configuration monitoring."""

from typing import Any

from codomyrmex.config_monitoring.config_monitor import ConfigurationMonitor
from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool()
def config_monitoring_detect_changes(
    config_paths: list[str], workspace_dir: str | None = None
) -> list[dict[str, Any]]:
    """Detect changes in specified configuration files against known hashes.

    Args:
        config_paths: List of file paths to check for changes.
        workspace_dir: Optional workspace directory to persist data.

    Returns:
        List of dictionaries containing detected configuration changes.
    """
    monitor = ConfigurationMonitor(workspace_dir=workspace_dir)
    changes = monitor.detect_config_changes(config_paths)
    return [
        {
            "change_id": c.change_id,
            "config_path": c.config_path,
            "change_type": c.change_type,
            "timestamp": c.timestamp.isoformat(),
            "previous_hash": c.previous_hash,
            "current_hash": c.current_hash,
            "changes": c.changes,
            "source": c.source,
        }
        for c in changes
    ]


@mcp_tool()
def config_monitoring_create_snapshot(
    environment: str, config_dir: str, workspace_dir: str | None = None
) -> dict[str, Any]:
    """Create a point-in-time snapshot of configuration files for drift detection.

    Args:
        environment: The environment name (e.g., 'production').
        config_dir: Directory containing configuration files.
        workspace_dir: Optional workspace directory to persist data.

    Returns:
        Dictionary containing details of the created snapshot.
    """
    monitor = ConfigurationMonitor(workspace_dir=workspace_dir)
    snapshot = monitor.create_snapshot(environment=environment, config_dir=config_dir)
    return {
        "snapshot_id": snapshot.snapshot_id,
        "timestamp": snapshot.timestamp.isoformat(),
        "environment": snapshot.environment,
        "total_files": snapshot.total_files,
        "config_hashes": snapshot.config_hashes,
    }


@mcp_tool()
def config_monitoring_detect_drift(
    snapshot_id: str, config_dir: str, workspace_dir: str | None = None
) -> dict[str, Any]:
    """Compare a configuration directory against a saved snapshot to detect drift.

    Args:
        snapshot_id: ID of the snapshot to compare against.
        config_dir: Current directory containing configuration files.
        workspace_dir: Optional workspace directory containing snapshot data.

    Returns:
        Dictionary containing detected drift (added, removed, modified files).
    """
    monitor = ConfigurationMonitor(workspace_dir=workspace_dir)
    return monitor.detect_drift(snapshot_id=snapshot_id, config_dir=config_dir)


@mcp_tool()
def config_monitoring_audit_configuration(
    environment: str, config_dir: str, workspace_dir: str | None = None
) -> dict[str, Any]:
    """Audit configuration files against compliance rules and security checks.

    Args:
        environment: The environment name (e.g., 'production').
        config_dir: Directory containing configuration files to audit.
        workspace_dir: Optional workspace directory to persist audit results.

    Returns:
        Dictionary containing compliance status, issues found, and recommendations.
    """
    monitor = ConfigurationMonitor(workspace_dir=workspace_dir)
    audit = monitor.audit_configuration(environment=environment, config_dir=config_dir)
    return {
        "audit_id": audit.audit_id,
        "timestamp": audit.timestamp.isoformat(),
        "environment": audit.environment,
        "compliance_status": audit.compliance_status,
        "issues_found": audit.issues_found,
        "recommendations": audit.recommendations,
        "audit_scope": audit.audit_scope,
    }
