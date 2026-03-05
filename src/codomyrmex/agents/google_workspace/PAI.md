# PAI.md — agents/google_workspace

## PAI Integration

### Module Role
Subprocess wrapper for Google Workspace CLI — gives PAI agents access to all 40+ Google Workspace services without Python SDK deps.

### MCP Tools

| Tool | Category | Description |
|------|----------|-------------|
| `gws_check` | google_workspace | Check installation and auth |
| `gws_run` | google_workspace | Run any gws command |
| `gws_schema` | google_workspace | Fetch tool schema |
| `gws_drive_list_files` | google_workspace | List Drive files |
| `gws_gmail_list_messages` | google_workspace | List Gmail messages |
| `gws_calendar_list_events` | google_workspace | List Calendar events |
| `gws_sheets_get_values` | google_workspace | Read Sheets values |
| `gws_tasks_list` | google_workspace | List Tasks |
| `gws_mcp_start` | google_workspace | Get MCP server start command |
| `gws_config` | google_workspace | Full configuration status |

### Phase -> Tool Mapping

| Phase | Tools |
|-------|-------|
| OBSERVE | `gws_check`, `gws_drive_list_files`, `gws_gmail_list_messages`, `gws_calendar_list_events` |
| THINK | `gws_schema` |
| PLAN | `gws_config` |
| BUILD | `gws_run` (read ops), `gws_sheets_get_values`, `gws_tasks_list` |
| EXECUTE | `gws_run` (write ops — requires `/codomyrmexTrust`) |
| VERIFY | `gws_schema`, `gws_check` |
| LEARN | `gws_config` |

### Auto-Discovery
This module is auto-discovered by PAI via `@mcp_tool` decorators in `mcp_tools.py`. No manual registration needed.

### Prerequisites
- `gws` binary in PATH: `npm install -g @googleworkspace/cli`
- Auth configured: `gws auth setup && gws auth login --account <email>`
