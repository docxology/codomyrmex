# AGENTS.md — cloud/google_workspace

## Agent Consumption Guide

### When to Use This Module

Use `cloud/google_workspace` when you need typed Python SDK access to Google Workspace APIs with service account authentication.

### Available SDK Tools (via cloud/mcp_tools.py)

| Tool | Operation |
|------|-----------|
| `gws_sdk_drive_list_files` | List Drive files |
| `gws_sdk_gmail_list_messages` | List Gmail messages |
| `gws_sdk_calendar_list_events` | List Calendar events |
| `gws_sdk_sheets_get_values` | Read Sheets values |

### Prerequisites
- SDK installed: `uv sync --extra google_workspace`
- Service account key: `GWS_SERVICE_ACCOUNT_FILE=/path/to/sa.json`

### Error Handling
- Missing creds -> `GoogleWorkspaceAuthError` (explicit, not silent)
- API errors -> `GoogleWorkspaceAPIError(status_code, reason)`
- Quota exceeded -> `GoogleWorkspaceQuotaError`
- Not found -> `GoogleWorkspaceNotFoundError`
