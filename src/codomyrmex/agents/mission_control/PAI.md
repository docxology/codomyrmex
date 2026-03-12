# PAI Access Matrix - Mission Control Agent

Provides AI agent orchestration dashboard integration via the builderz-labs/mission-control REST API. Manages agent fleets, task boards, cost tracking, and real-time monitoring.

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|:---|:---|:---|:---|
| **Engineer** | Full | `mission_control_status`, `mission_control_list_agents`, `mission_control_list_tasks`, `mission_control_create_task`, `mission_control_get_task`, `mission_control_start` | TRUSTED |
| **Architect** | Read + Config | `mission_control_status`, `mission_control_list_agents`, `mission_control_list_tasks` | OBSERVED |
| **QATester** | Tests | `mission_control_status`, `mission_control_list_tasks`, `mission_control_get_task` | OBSERVED |
| **Researcher** | Read-only | `mission_control_status`, `mission_control_list_agents` | OBSERVED |

## Configuration

| Key | Default | Description |
|:---|:---|:---|
| `mc_base_url` | `http://localhost:3000` | Dashboard base URL |
| `mc_api_key` | `""` | API key for authentication |
| `mc_auth_user` | `admin` | Login username |
| `mc_timeout` | `30` | HTTP timeout (s) |

## Use Cases

- Fleet-wide agent status monitoring and lifecycle management.
- Kanban task orchestration with priority and assignment tracking.
- Token usage and cost analysis across multiple models.
- Real-time session inspection and log aggregation.
- Claude Code session and team task bridge integration.
