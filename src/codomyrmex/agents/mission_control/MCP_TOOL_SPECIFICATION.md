# Mission Control - MCP Tool Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Mission Control module exposes 6 Model Context Protocol (MCP) tools in the `mission_control` category. These tools allow Claude, swarm orchestrators, and sibling agents to interact with the Mission Control dashboard programmatically.

All tools return a `dict[str, Any]` with at minimum a `status` key (`"success"` or `"error"`). On error, a `message` key contains the error description.

## Tools

### `mission_control_status`

Check if the Mission Control dashboard is running and reachable.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `base_url` | `str` | `http://localhost:3000` | Dashboard URL |
| `api_key` | `str` | `""` | API key for authentication |

**Returns**: `{status, running: bool, user?: dict, error?: str}`

---

### `mission_control_list_agents`

List all agents registered in Mission Control.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `base_url` | `str` | `http://localhost:3000` | Dashboard URL |
| `api_key` | `str` | `""` | API key |

**Returns**: `{status, agents: list[dict], count: int}`

---

### `mission_control_list_tasks`

List tasks on the Kanban board with optional filters.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `base_url` | `str` | `http://localhost:3000` | Dashboard URL |
| `api_key` | `str` | `""` | API key |
| `task_status` | `str \| None` | `None` | Filter: inbox, assigned, in_progress, review, quality_review, done |
| `assigned_to` | `str \| None` | `None` | Filter by assignee agent ID |
| `priority` | `str \| None` | `None` | Filter: low, medium, high, critical |

**Returns**: `{status, tasks: list[dict], count: int}`

---

### `mission_control_create_task`

Create a new task on the Kanban board.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `title` | `str` | *required* | Task title |
| `description` | `str` | `""` | Task description |
| `priority` | `str` | `"medium"` | Priority: low, medium, high, critical |
| `assigned_to` | `str \| None` | `None` | Agent ID to assign |
| `base_url` | `str` | `http://localhost:3000` | Dashboard URL |
| `api_key` | `str` | `""` | API key |

**Returns**: `{status, task: dict}`

---

### `mission_control_get_task`

Get details of a specific task by its ID.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `task_id` | `str` | *required* | Task identifier |
| `base_url` | `str` | `http://localhost:3000` | Dashboard URL |
| `api_key` | `str` | `""` | API key |

**Returns**: `{status, task: dict}`

---

### `mission_control_start`

Start the Mission Control dashboard dev server.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `app_path` | `str` | `<module>/app` | Path to the mission-control app directory |

**Returns**: `{status, pid?: int}`

## Usage Example

```python
from codomyrmex.agents.mission_control.mcp_tools import (
    mission_control_status,
    mission_control_list_tasks,
    mission_control_create_task,
)

# Check if dashboard is running
status = mission_control_status()
if status["running"]:
    # List open tasks
    tasks = mission_control_list_tasks(task_status="in_progress")
    print(f"{tasks['count']} tasks in progress")

    # Create a new task
    result = mission_control_create_task(
        title="Deploy v2.0",
        description="Ship the new release",
        priority="high",
    )
    print(f"Created task: {result['task']}")
```

## Error Handling

All tools catch exceptions and return `{status: "error", message: str}` instead of raising. This makes them safe for use in swarm orchestration contexts where unhandled exceptions would break the agent loop.
