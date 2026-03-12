# Pi Coding Agent — MCP Tool Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Tools

### `pi_status`

Check pi CLI installation and report version.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| — | — | — | No parameters |

**Returns**: `{status, version?, path?}` or `{status: "not_installed"}`

---

### `pi_prompt`

Execute a one-shot prompt via `pi -p`.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `message` | `str` | *required* | Prompt text |
| `provider` | `str` | `"google"` | LLM provider |
| `model` | `str` | `""` | Model ID |
| `thinking` | `str` | `""` | Thinking level |
| `tools` | `str` | `"read,bash,edit,write"` | Active tools |
| `cwd` | `str` | `""` | Working directory |
| `timeout` | `float` | `120.0` | Timeout in seconds |

**Returns**: `{status, output}` or `{status: "error", message}`

---

### `pi_list_models`

List available models.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `search` | `str` | `""` | Fuzzy search filter |
| `provider` | `str` | `""` | Provider filter |

**Returns**: `{status, models: list, count: int}`

---

### `pi_start_rpc`

Start pi RPC session.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `provider` | `str` | `"google"` | LLM provider |
| `model` | `str` | `""` | Model ID |
| `no_session` | `bool` | `True` | Ephemeral session |

**Returns**: `{status, pid, message}`

---

### `pi_install_package`

Install a pi package.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `source` | `str` | *required* | npm or git source |

**Returns**: `{status, output}`

---

### `pi_list_packages`

List installed packages.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| — | — | — | No parameters |

**Returns**: `{status, output}`
