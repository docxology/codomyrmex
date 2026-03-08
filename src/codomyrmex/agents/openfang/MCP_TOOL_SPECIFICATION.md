# agents/openfang — MCP Tool Specification

All 7 tools are auto-discovered via `@mcp_tool` in `mcp_tools.py`.

---

## openfang_check

**Category**: openfang
**Description**: Check if openfang is installed, return version and submodule status.

**Parameters**: None

**Returns**:
```json
{
  "status": "success",
  "installed": true,
  "version": "openfang 0.4.2",
  "submodule_initialized": false,
  "upstream_sha": "a1b2c3d",
  "vendor_dir": "/path/to/vendor/openfang"
}
```

---

## openfang_execute

**Category**: openfang
**Description**: Execute an agent query with openfang and return the response.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `prompt` | string | yes | — | Natural-language query for the openfang agent |
| `timeout` | integer | no | `120` | Subprocess timeout in seconds |

**Returns** (success):
```json
{"status": "success", "stdout": "...", "stderr": "", "returncode": "0"}
```

**Returns** (error):
```json
{"status": "error", "message": "openfang binary not found on PATH..."}
```

---

## openfang_hands_list

**Category**: openfang
**Description**: List available openfang autonomous Hands (scheduled agent packages).

**Parameters**: None

**Returns**:
```json
{
  "status": "success",
  "hands": [
    {"name": "daily-reporter", "description": "...", "schedule": "0 9 * * *", "enabled": true}
  ],
  "raw": "raw CLI output..."
}
```

---

## openfang_send_message

**Category**: openfang
**Description**: Send a message via an openfang channel adapter.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `channel` | string | yes | — | Channel adapter name (telegram, slack, discord, etc.) |
| `target` | string | yes | — | Recipient (username, channel ID, etc.) |
| `message` | string | yes | — | Message body to send |
| `timeout` | integer | no | `30` | Subprocess timeout in seconds |

---

## openfang_gateway

**Category**: openfang
**Description**: Control the openfang WebSocket gateway.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `action` | string | no | `"status"` | One of: `start`, `stop`, `status` |

---

## openfang_config

**Category**: openfang
**Description**: Show openfang configuration sourced from environment variables.

**Parameters**: None

**Returns**:
```json
{
  "status": "success",
  "command": "openfang",
  "timeout": 120,
  "gateway_url": "ws://localhost:3000",
  "vendor_dir": "/path/to/vendor/openfang",
  "install_dir": "/usr/local/bin",
  "submodule_initialized": false,
  "installed": true
}
```

---

## openfang_update

**Category**: openfang
**Description**: Pull latest openfang upstream, optionally rebuild and install.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `rebuild` | boolean | no | `false` | If true, run `cargo build --release` after sync |
| `install` | boolean | no | `false` | If true (requires rebuild=true), copy binary to install_dir |
| `vendor_dir` | string | no | `""` | Override vendor directory path |
| `install_dir` | string | no | `""` | Override install directory path |
