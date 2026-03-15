# Paperclip — PAI Bridge

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## PAI Integration

The Paperclip module bridges the Personal AI Infrastructure with the Paperclip zero-human company orchestration platform. It enables PAI agents to:

1. **Manage companies** — Create, list, and inspect autonomous AI companies.
2. **Coordinate agents** — Register agents, trigger heartbeats, and monitor activity.
3. **Track work** — Create issues, list tickets, and review approval queues.
4. **Monitor health** — Run diagnostics and enforce budgets.

## Architecture

```text
PAI Dashboard (:8787)
    └── Paperclip MCP Tools
            ├── PaperclipClient (CLI → paperclipai binary)
            │     └── heartbeat run, doctor, onboard, configure
            └── PaperclipAPIClient (HTTP → localhost:3100)
                  └── companies, agents, issues, approvals, dashboard
```

## MCP Tools Available

- `paperclip_execute` — Heartbeat run
- `paperclip_list_companies` — List companies
- `paperclip_create_issue` — Create ticket
- `paperclip_trigger_heartbeat` — Trigger heartbeat via API
- `paperclip_doctor` — Health diagnostics

## Configuration

| Key | Default | Description |
| :--- | :--- | :--- |
| `paperclip_command` | `paperclipai` | CLI binary name |
| `paperclip_timeout` | `120` | CLI timeout (seconds) |
| `paperclip_api_base` | `http://localhost:3100` | Server URL |
| `paperclip_agent_id` | — | Default agent ID |
| `paperclip_config_path` | — | Path to Paperclip config |

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md)
- **README**: [README.md](README.md)
