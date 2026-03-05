# agents/google_workspace

Subprocess wrapper around the `gws` (Google Workspace CLI) tool for programmatic access to 40+ Google Workspace services.

## Overview

This module wraps the [`gws` CLI](https://github.com/googleworkspace/gws-cli) via subprocess, following the same pattern as the `aider` module. No Google Python SDK required — only the `gws` binary in PATH.

## Installation

```bash
# Install gws CLI
npm install -g @googleworkspace/cli

# Configure authentication
gws auth setup
gws auth login --account your@workspace.com
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_WORKSPACE_CLI_TOKEN` | OAuth2 bearer token |
| `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` | Path to credentials JSON |
| `GOOGLE_WORKSPACE_CLI_ACCOUNT` | Default account for all calls |
| `GWS_TIMEOUT` | Subprocess timeout in seconds (default: 60) |
| `GWS_PAGE_ALL` | Auto-paginate responses (set to "1" or "true") |

## Quick Start

```python
from codomyrmex.agents.google_workspace import GoogleWorkspaceRunner, HAS_GWS

if HAS_GWS:
    runner = GoogleWorkspaceRunner()
    result = runner.run("drive", "files", "list", params={"pageSize": 10})
    print(result["stdout"])
```

## MCP Tools

10 tools exposed via `@mcp_tool`: `gws_check`, `gws_run`, `gws_schema`, `gws_drive_list_files`, `gws_gmail_list_messages`, `gws_calendar_list_events`, `gws_sheets_get_values`, `gws_tasks_list`, `gws_mcp_start`, `gws_config`.
