# PAI.md — cloud/google_workspace

## PAI Integration

### Module Role
SDK-based Google Workspace clients for typed, strongly-authenticated API access.

### MCP Tools (via cloud/mcp_tools.py)

| Tool | Category | Description |
|------|----------|-------------|
| `gws_sdk_drive_list_files` | google_workspace | List Drive files via SDK |
| `gws_sdk_gmail_list_messages` | google_workspace | List Gmail messages via SDK |
| `gws_sdk_calendar_list_events` | google_workspace | List Calendar events via SDK |
| `gws_sdk_sheets_get_values` | google_workspace | Read Sheets values via SDK |

### Phase -> Tool Mapping

| Phase | Tools |
|-------|-------|
| OBSERVE | `gws_sdk_drive_list_files`, `gws_sdk_gmail_list_messages`, `gws_sdk_calendar_list_events` |
| THINK | (use agents/google_workspace gws_schema instead) |
| PLAN | (use agents/google_workspace gws_config instead) |
| BUILD | `gws_sdk_sheets_get_values` |
| EXECUTE | SDK clients directly via Python |
| VERIFY | `gws_sdk_drive_list_files` (confirm file created) |
| LEARN | (no dedicated tool) |

### Auto-Discovery
SDK tools are in `cloud/mcp_tools.py` which is auto-discovered. The `cloud/google_workspace/` subpackage itself does NOT have its own `mcp_tools.py` — tools are surfaced through the parent `cloud` module's `mcp_tools.py`.

### Prerequisites
- SDK: `uv sync --extra google_workspace`
- Service account: `GWS_SERVICE_ACCOUNT_FILE=/path/to/sa.json`
