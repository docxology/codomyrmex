# google_workspace — MCP Tool Specification

## Overview

Google Workspace `gws` CLI integration. Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `google_workspace`.

## Tools

| Tool | Summary |
|:-----|:--------|
| `gws_check` | `gws` installed, version, auth flags |
| `gws_run` | Generic `gws` invocation: service, resource, method, optional params/body |
| `gws_schema` | JSON schema for a tool path (e.g. `drive.files.list`) |
| `gws_drive_list_files` | Drive file list with optional query |
| `gws_gmail_list_messages` | Gmail messages list |
| `gws_calendar_list_events` | Calendar events in optional time range |
| `gws_sheets_get_values` | Read spreadsheet range (A1) |
| `gws_tasks_list` | Google Tasks list |
| `gws_mcp_start` | Returns MCP server start command string (does not spawn) |
| `gws_config` | Full CLI config / auth snapshot |

### `gws_run`

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `service` | string | Yes | — | e.g. `drive`, `gmail` |
| `resource` | string | Yes | — | Resource name |
| `method` | string | Yes | — | e.g. `list`, `get` |
| `params` | object | No | `null` | Query params |
| `body` | object | No | `null` | JSON body |
| `page_all` | boolean | No | `false` | Fetch all pages |
| `account` | string | No | `""` | Account override |
| `timeout` | integer | No | `60` | Subprocess timeout (s) |

**Returns:** `status`, `output`, `stderr`, `returncode`.

### `gws_drive_list_files`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `query` | string | `""` | Drive search query |
| `page_size` | integer | `20` | Max files |
| `fields` | string | `files(id,name,...)` | Response fields |
| `account` | string | `""` | Account override |
| `timeout` | integer | `60` | Subprocess timeout |

### `gws_gmail_list_messages`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `query` | string | `""` | Gmail search |
| `max_results` | integer | `20` | Max messages |
| `account` | string | `""` | Account override |
| `timeout` | integer | `60` | Subprocess timeout |

### `gws_calendar_list_events`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `calendar_id` | string | `primary` | Calendar ID |
| `time_min` | string | `""` | RFC3339 lower bound |
| `time_max` | string | `""` | RFC3339 upper bound |
| `max_results` | integer | `20` | Max events |
| `account` | string | `""` | Account override |
| `timeout` | integer | `60` | Subprocess timeout |

### `gws_sheets_get_values`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `spreadsheet_id` | string | Yes | Spreadsheet ID |
| `range_` | string | Yes | A1 range |
| `account` | string | No | Account override |
| `timeout` | integer | No | Default `60` |

### `gws_tasks_list`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `tasklist_id` | string | `@default` | Task list ID |
| `show_completed` | boolean | `false` | Include completed |
| `account` | string | `""` | Account override |
| `timeout` | integer | `60` | Subprocess timeout |

### `gws_mcp_start`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `services` | array[string] | `null` | Enabled services (empty = all) |
| `account` | string | `""` | Account for MCP session |

## Navigation

- **Parent**: [agents](../README.md)
- **Project root**: [README.md](../../../../README.md)
