"""MCP tool definitions for the logistics module.

Exposes task queue management and scheduling as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_queue():
    """Lazy import of Queue to avoid circular deps."""
    from codomyrmex.logistics.task import Queue

    return Queue


def _get_job():
    """Lazy import of Job."""
    from codomyrmex.logistics.task import Job

    return Job


def _get_schedule_manager():
    """Lazy import of ScheduleManager."""
    from codomyrmex.logistics.schedule import ScheduleManager

    return ScheduleManager


@mcp_tool(
    category="logistics",
    description="Get queue statistics including pending, running, and completed job counts.",
)
def logistics_queue_stats(backend: str = "in_memory") -> dict[str, Any]:
    """Return statistics for a logistics task queue.

    Args:
        backend: Queue backend to use (default: in_memory).

    Returns:
        dict with keys: status, backend, stats
    """
    try:
        queue_cls = _get_queue()
        queue = queue_cls(backend=backend)
        stats = queue.get_stats()
        return {"status": "success", "backend": backend, "stats": stats}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="logistics",
    description="List all currently scheduled task IDs in the schedule manager.",
)
def logistics_list_scheduled() -> dict[str, Any]:
    """List scheduled task IDs from the ScheduleManager.

    Returns:
        dict with keys: status, task_ids, count
    """
    try:
        mgr_cls = _get_schedule_manager()
        mgr = mgr_cls()
        task_ids = mgr.list_tasks()
        return {"status": "success", "task_ids": task_ids, "count": len(task_ids)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="logistics",
    description="Get logistics module version and available component names.",
)
def logistics_status() -> dict[str, Any]:
    """Return the logistics module version and available components.

    Returns:
        dict with keys: status, version, components
    """
    try:
        import codomyrmex.logistics as lg

        components = [
            name
            for name in lg.__all__
            if not name.startswith("_") and name != "cli_commands"
        ]
        return {
            "status": "success",
            "version": getattr(lg, "__version__", "unknown"),
            "components": components,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
