"""MCP tool definitions for the config_monitoring module.

Exposes configuration change detection, drift analysis, and monitoring summaries.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_monitor():
    """Lazy import of ConfigurationMonitor to avoid circular deps."""
    from codomyrmex.config_monitoring.config_monitor import ConfigurationMonitor

    return ConfigurationMonitor


@mcp_tool(
    category="config_monitoring",
    description="Detect changes in configuration files by comparing current hashes to stored baselines.",
)
def config_monitoring_detect_changes(
    config_paths: list[str],
    workspace_dir: str | None = None,
) -> dict[str, Any]:
    """Detect configuration file changes by hashing and comparing to stored baselines.

    Args:
        config_paths: list of file paths to check for changes.
        workspace_dir: Optional workspace directory for storing monitoring state.

    Returns:
        dict with status, changes detected, and per-file change details.
    """
    try:
        Monitor = _get_monitor()
        monitor = Monitor(workspace_dir=workspace_dir)
        changes = monitor.detect_config_changes(config_paths)

        change_list = [
            {
                "change_id": c.change_id,
                "config_path": c.config_path,
                "change_type": c.change_type,
                "timestamp": c.timestamp.isoformat(),
            }
            for c in changes
        ]

        return {
            "status": "success",
            "paths_checked": len(config_paths),
            "changes_detected": len(changes),
            "changes": change_list,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="config_monitoring",
    description="Get a summary of the configuration monitoring state including snapshots, changes, and audits.",
)
def config_monitoring_summary(
    workspace_dir: str | None = None,
) -> dict[str, Any]:
    """Return a summary of current configuration monitoring state.

    Args:
        workspace_dir: Optional workspace directory for monitoring data.

    Returns:
        dict with status and monitoring summary (snapshots, changes, audits counts).
    """
    try:
        Monitor = _get_monitor()
        monitor = Monitor(workspace_dir=workspace_dir)
        summary = monitor.get_monitoring_summary()

        return {
            "status": "success",
            "summary": summary,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="config_monitoring",
    description="Calculate the SHA-256 hash of a configuration file for change detection.",
)
def config_monitoring_hash_file(
    file_path: str,
) -> dict[str, Any]:
    """Calculate the SHA-256 hash of a file.

    Args:
        file_path: Path to the file to hash.

    Returns:
        dict with status, file_path, and sha256 hash.
    """
    try:
        Monitor = _get_monitor()
        monitor = Monitor()
        file_hash = monitor.calculate_file_hash(file_path)

        if not file_hash:
            return {
                "status": "error",
                "message": f"File not found or not a regular file: {file_path}",
            }

        return {
            "status": "success",
            "file_path": file_path,
            "sha256": file_hash,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
