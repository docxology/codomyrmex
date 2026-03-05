# AGENTS.md — agents/google_workspace

## Agent Consumption Guide

### When to Use This Module

Use `agents/google_workspace` when you need to interact with Google Workspace services (Drive, Gmail, Calendar, Sheets, Tasks, etc.) without installing the Google Python SDK.

### Key Tools

| Tool | When to Use |
|------|-------------|
| `gws_check` | Verify installation and auth before other operations |
| `gws_run` | General-purpose command for any gws operation |
| `gws_drive_list_files` | Browse or search Drive files |
| `gws_gmail_list_messages` | Search inbox, find emails |
| `gws_calendar_list_events` | Read calendar events in a date range |
| `gws_sheets_get_values` | Read spreadsheet data |
| `gws_tasks_list` | List tasks from Google Tasks |
| `gws_schema` | Inspect available parameters for any gws command |
| `gws_config` | Check current configuration status |

### Trust Requirements

- Read operations (`list`, `get`): VERIFIED trust level
- Write operations (`create`, `update`, `delete`): TRUSTED trust level (run `/codomyrmexTrust`)

### Error Handling

All tools return `{"status": "error", "message": "..."}` on failure. Always check `result["status"]` before using results.
