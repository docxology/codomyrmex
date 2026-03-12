# Mission Control - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Mission Control Python client (`MissionControlClient`) wraps the upstream builderz-labs/mission-control REST API. All communication uses stdlib `urllib.request` — zero external HTTP dependencies.

## Authentication

Two authentication modes are supported:

| Mode | Header | Configuration |
| :--- | :--- | :--- |
| **API Key** | `x-api-key: <key>` | `mc_api_key` / `MC_API_KEY` env var |
| **Session Cookie** | `Cookie: mc-session=<token>` | Obtained via `login()` method |

## Client API

### Configuration

```python
from codomyrmex.agents.mission_control import MissionControlClient, MissionControlConfig

# Default configuration
client = MissionControlClient()

# Custom configuration via dict
client = MissionControlClient(config={
    "base_url": "http://mc.local:3000",
    "api_key": "your-api-key",
    "timeout": 30,
})

# Custom configuration via dataclass
config = MissionControlConfig(
    base_url="http://mc.local:3000",
    api_key="your-api-key",
)
client = MissionControlClient(config=config)
```

### Methods

#### Authentication

| Method | Signature | Returns | Description |
| :--- | :--- | :--- | :--- |
| `login()` | `() -> dict` | Login response | Authenticate and store session cookie |

#### Status

| Method | Signature | Returns | Description |
| :--- | :--- | :--- | :--- |
| `is_running()` | `() -> bool` | Boolean | Check if dashboard is reachable |
| `status()` | `() -> dict` | `{running, user/error}` | Get running status and user info |

#### Agent Management

| Method | Signature | Returns | Description |
| :--- | :--- | :--- | :--- |
| `list_agents()` | `() -> list[dict]` | Agent list | List all registered agents |
| `register_agent(name, model, **kwargs)` | `(str, str) -> dict` | Created agent | Register a new agent |

#### Task Management

| Method | Signature | Returns | Description |
| :--- | :--- | :--- | :--- |
| `list_tasks(status, assigned_to, priority)` | `(**) -> list[dict]` | Task list | List tasks with filters |
| `get_task(task_id)` | `(str) -> dict` | Task details | Get a task by ID |
| `create_task(title, description, priority, assigned_to, **kwargs)` | `(str, **) -> dict` | Created task | Create a new task |
| `update_task(task_id, **kwargs)` | `(str, **) -> dict` | Updated task | Update an existing task |
| `delete_task(task_id)` | `(str) -> dict` | Deletion result | Delete a task by ID |

#### Comments

| Method | Signature | Returns | Description |
| :--- | :--- | :--- | :--- |
| `list_comments(task_id)` | `(str) -> list[dict]` | Comment list | List comments on a task |
| `add_comment(task_id, content, author)` | `(str, str, str) -> dict` | Created comment | Add a comment to a task |

#### Server Lifecycle

| Method | Signature | Returns | Description |
| :--- | :--- | :--- | :--- |
| `start_server()` | `() -> dict` | `{status, pid}` | Start the dashboard dev server |
| `stop_server()` | `() -> dict` | `{status, pid}` | Stop the running server |

## Error Handling

All client methods raise `MissionControlError` on failure. The error message includes:
- HTTP status code and reason (for HTTP errors)
- The HTTP method and path (for debugging)
- The response body (when available)

```python
from codomyrmex.agents.mission_control import MissionControlClient, MissionControlError

client = MissionControlClient()
try:
    agents = client.list_agents()
except MissionControlError as e:
    print(f"Failed: {e}")
```

## Configuration Reference

| Key | Default | Env Var | Description |
| :--- | :--- | :--- | :--- |
| `base_url` | `http://localhost:3000` | — | Dashboard URL |
| `api_key` | `""` | `MC_API_KEY` | API key auth |
| `auth_user` | `admin` | — | Login username |
| `auth_pass` | `""` | `MC_AUTH_PASS` | Login password |
| `app_path` | `<module>/app` | — | Git submodule path |
| `timeout` | `30` | — | HTTP timeout (seconds) |
