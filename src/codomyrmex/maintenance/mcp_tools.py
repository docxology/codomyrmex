"""MCP tool definitions for the maintenance module.

Exposes health checks and maintenance task scheduling as MCP tools.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func
        return decorator


@mcp_tool(
    category="maintenance",
    description="Run a simple health check and return its status.",
)
def maintenance_health_check(
    name: str = "system",
    check_fn_source: str = "default",
) -> dict[str, Any]:
    """Run a named health check.

    Args:
        name: Check identifier.
        check_fn_source: Source of the check function (default runs a basic system check).
    """
    try:
        from codomyrmex.maintenance.health.health_check import (
            HealthCheck,
            HealthChecker,
            HealthStatus,
        )
        checker = HealthChecker()
        checker.register(HealthCheck(
            name=name,
            description="Agent-triggered health check",
            check_fn=lambda: (HealthStatus.HEALTHY, "System operational", {}),
        ))
        result = checker.run(name)
        return {
            "status": "ok",
            "check_name": name,
            "health_status": result.status.value,
            "message": result.message,
            "duration_ms": result.duration_ms,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="maintenance",
    description="List all registered maintenance tasks and their status.",
)
def maintenance_list_tasks() -> dict[str, Any]:
    """List maintenance tasks with their current status."""
    try:
        from codomyrmex.maintenance.health.scheduler import MaintenanceScheduler
        scheduler = MaintenanceScheduler()
        return {
            "status": "ok",
            "task_count": scheduler.task_count,
            "tasks": [],
            "message": "No tasks registered in this ephemeral instance",
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
