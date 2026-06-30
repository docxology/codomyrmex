# languages — MCP Tool Specification

## Overview

Multi-language install checks and script execution. Implementations live in [`mcp_tools.py`](mcp_tools.py).

**PAI bridge:** tools are registered via `register_mcp_tools(mcp_server)` as:

| Exposed name | Underlying function |
|:-------------|:--------------------|
| `check_language_installed` | `mcp_check_language_installed` |
| `get_language_install_instructions` | `mcp_get_language_install_instructions` |
| `run_language_script` | `mcp_run_language_script` |

## Parameters

### `check_language_installed` / `get_language_install_instructions`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `language` | string | Yes | e.g. `python`, `javascript`, `bash` |

### `run_language_script`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `language` | string | Yes | Runtime id |
| `script_content` | string | Yes | **Executes on host** — use with care |

**Returns:** string result or error message.

## Navigation

- **Parent**: [codomyrmex](../README.md)
- **Project root**: [README.md](../../../README.md)
