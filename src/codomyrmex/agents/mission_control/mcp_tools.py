"""MCP tool definitions for the Mission Control agent module.

Exposes Mission Control dashboard operations as MCP tools for use by
Claude, swarm orchestrators, and other Codomyrmex agents.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_client(**kwargs: Any) -> Any:
    """Lazy-instantiate MissionControlClient with optional overrides.

    Args:
        **kwargs: Override keys for MissionControlConfig.
    """
    from codomyrmex.agents.mission_control.mission_control_client import (
        MissionControlClient,
        MissionControlConfig,
    )

    config_kwargs: dict[str, Any] = {}
    if "base_url" in kwargs:
        config_kwargs["base_url"] = kwargs["base_url"]
    if "api_key" in kwargs:
        config_kwargs["api_key"] = kwargs["api_key"]
    if "timeout" in kwargs:
        config_kwargs["timeout"] = kwargs["timeout"]

    config = MissionControlConfig(**config_kwargs)
    return MissionControlClient(config=config)


@mcp_tool(
    category="mission_control",
    description=(
        "Check if the Mission Control dashboard is running and reachable. "
        "Returns running status and current user info."
    ),
)
def mission_control_status(
    base_url: str = "http://localhost:3000",
    api_key: str = "",
) -> dict[str, Any]:
    """Check Mission Control dashboard status.

    Args:
        base_url: Dashboard URL (default ``http://localhost:3000``).
        api_key: Optional API key for authentication.

    Returns:
        dict with keys: status, running, user/error info
    """
    try:
        client = _get_client(base_url=base_url, api_key=api_key)
        info = client.status()
        return {"status": "success", **info}
    except Exception as exc:
        return {"status": "error", "running": False, "message": str(exc)}


@mcp_tool(
    category="mission_control",
    description="list all agents registered in Mission Control.",
)
def mission_control_list_agents(
    base_url: str = "http://localhost:3000",
    api_key: str = "",
) -> dict[str, Any]:
    """list registered Mission Control agents.

    Args:
        base_url: Dashboard URL.
        api_key: Optional API key.

    Returns:
        dict with keys: status, agents (list), count
    """
    try:
        client = _get_client(base_url=base_url, api_key=api_key)
        agents = client.list_agents()
        return {"status": "success", "agents": agents, "count": len(agents)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="mission_control",
    description=(
        "list tasks on the Mission Control Kanban board. "
        "Optionally filter by status, assignee, or priority."
    ),
)
def mission_control_list_tasks(
    base_url: str = "http://localhost:3000",
    api_key: str = "",
    task_status: str | None = None,
    assigned_to: str | None = None,
    priority: str | None = None,
) -> dict[str, Any]:
    """list Mission Control tasks.

    Args:
        base_url: Dashboard URL.
        api_key: Optional API key.
        task_status: Filter by status (inbox, assigned, in_progress,
            review, quality_review, done).
        assigned_to: Filter by assignee.
        priority: Filter by priority (low, medium, high, critical).

    Returns:
        dict with keys: status, tasks (list), count
    """
    try:
        client = _get_client(base_url=base_url, api_key=api_key)
        tasks = client.list_tasks(
            status=task_status,
            assigned_to=assigned_to,
            priority=priority,
        )
        return {"status": "success", "tasks": tasks, "count": len(tasks)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="mission_control",
    description="Create a new task on the Mission Control Kanban board.",
)
def mission_control_create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    assigned_to: str | None = None,
    base_url: str = "http://localhost:3000",
    api_key: str = "",
) -> dict[str, Any]:
    """Create a Mission Control task.

    Args:
        title: Task title.
        description: Task description.
        priority: Priority level (low, medium, high, critical).
        assigned_to: Agent ID to assign the task to.
        base_url: Dashboard URL.
        api_key: Optional API key.

    Returns:
        dict with keys: status, task (created task dict)
    """
    try:
        client = _get_client(base_url=base_url, api_key=api_key)
        task = client.create_task(
            title=title,
            description=description,
            priority=priority,
            assigned_to=assigned_to,
        )
        return {"status": "success", "task": task}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="mission_control",
    description="Get details of a specific task by its ID.",
)
def mission_control_get_task(
    task_id: str,
    base_url: str = "http://localhost:3000",
    api_key: str = "",
) -> dict[str, Any]:
    """Get Mission Control task details.

    Args:
        task_id: Task identifier.
        base_url: Dashboard URL.
        api_key: Optional API key.

    Returns:
        dict with keys: status, task (detail dict)
    """
    try:
        client = _get_client(base_url=base_url, api_key=api_key)
        task = client.get_task(task_id)
        return {"status": "success", "task": task}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="mission_control",
    description=(
        "Start the Mission Control dashboard dev server. "
        "Requires Node.js 22 and pnpm in the app/ submodule directory."
    ),
)
def mission_control_start(
    app_path: str = "",
) -> dict[str, Any]:
    """Start the Mission Control dashboard server.

    Args:
        app_path: Path to the mission-control app directory.
            Defaults to the ``app/`` subdirectory of this module.

    Returns:
        dict with keys: status, pid
    """
    try:
        from codomyrmex.agents.mission_control.mission_control_client import (
            MissionControlClient,
            MissionControlConfig,
        )

        config_kwargs: dict[str, Any] = {}
        if app_path:
            config_kwargs["app_path"] = app_path

        client = MissionControlClient(config=MissionControlConfig(**config_kwargs))
        result = client.start_server()
        return {"status": "success", **result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
