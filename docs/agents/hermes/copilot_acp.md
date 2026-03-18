# Hermes — GitHub Copilot ACP Backend

**Version**: v0.3.0 | **Last Updated**: March 2026 (73-commit update)

## Overview

The March 2026 Hermes update (`73 commits`) introduced `agent/copilot_acp_client.py` — a
first-class backend adapter that lets Hermes use **GitHub Copilot** (via the Copilot CLI's
`--acp --stdio` interface) as a model provider.

This is useful when:

- You have a GitHub Copilot subscription and want to use it without paying for OpenRouter credits.
- You want to route requests through an on-device ACP session for privacy.
- You need GPT-4o or other Copilot-backed models free with your GitHub subscription.

## How It Works

```text
Hermes request
     │
     ▼
CopilotACPClient  (agent/copilot_acp_client.py)
     │  OpenAI-compatible facade
     ▼
copilot --acp --stdio  (short-lived subprocess)
     │  JSON-RPC 2.0 over stdin/stdout
     ▼
GitHub Copilot backend  (GPT-4o, Claude, etc.)
     │
     ▼
Response assembled → returned to Hermes as OpenAI-style object
```

Each request is a **short-lived ACP session**:

1. `initialize` — handshake with protocol version and client capabilities
2. `session/new` — create a session with `cwd` and optional MCP servers
3. `session/prompt` — send formatted transcript, collect streaming chunks
4. Session closed after response

### Authentication

The adapter reads from environment variables:

| Variable | Purpose | Default |
| :--- | :--- | :--- |
| `HERMES_COPILOT_ACP_COMMAND` | Path to `copilot` binary | `copilot` (from PATH) |
| `COPILOT_CLI_PATH` | Alternative binary path | — |
| `HERMES_COPILOT_ACP_ARGS` | Override default CLI args | `--acp --stdio` |

Authenticate Copilot CLI first:

```bash
gh auth login          # GitHub CLI auth
copilot auth login     # or: authenticate Copilot CLI specifically
```

Then authenticate Hermes copilot backend:

```bash
hermes copilot login   # new command from 73-commit update
```

## Configuration

Set `acp://copilot` as the base URL to activate the adapter:

```bash
# In HERMES_HOME/.env
HERMES_COPILOT_ACP_COMMAND=copilot
```

Or in the Hermes model selector:

```bash
hermes model   # interactive model/provider picker — select "GitHub Copilot (ACP)"
```

### Manual Config Override

```yaml
# config.yaml — experimental, prefer hermes model picker
model: acp://copilot/gpt-4o
```

## File System Safety

The adapter enforces a sandbox restriction: all ACP `fs/read_text_file` and `fs/write_text_file`
requests are validated to be within the session `cwd`. Any attempt to read/write outside this
boundary raises `PermissionError`.

```python
# Enforced in _ensure_path_within_cwd():
# Absolute paths required; files must be within session cwd
```

## Capabilities & Limitations

| Feature | Status |
| :--- | :--- |
| Basic chat / reasoning | ✅ |
| Streaming (chunk-based) | ✅ via `session/update` |
| Native tool calls (JSON) | ⚠️ Converted to natural-language prompt; no structured tool_calls |
| File system access | ✅ read/write within cwd sandbox |
| MCP server passthrough | ✅ passed in `session/new` |
| Session persistence | ❌ Each request is a fresh session |
| Timeout | 900s default (`HERMES_COPILOT_ACP_COMMAND` override) |

> **Note**: Because the Copilot ACP interface does not emit native OpenAI `tool_calls`, Hermes
> cannot use structured tool calling with this backend. Complex agentic tasks work better with
> OpenRouter or Anthropic direct.

## Authentication via `hermes_cli/copilot_auth.py`

The 73-commit update also added `hermes_cli/copilot_auth.py`, which handles the OAuth-style
flow for GitHub Copilot authentication in Hermes CLI:

```bash
hermes copilot login    # interactive device-flow auth
hermes copilot logout   # clears stored credentials
hermes copilot status   # shows auth state
```

Credentials are stored in `$HERMES_HOME/.env` as `GITHUB_TOKEN` (shared with other GitHub
CLI operations).

## Troubleshooting

| Symptom | Fix |
| :--- | :--- |
| `Could not start Copilot ACP command 'copilot'` | Install Copilot CLI: `gh extension install github/gh-copilot` |
| `Copilot ACP did not return a sessionId` | Re-run `hermes copilot login` or `gh auth login` |
| `TimeoutError` | Increase timeout or check Copilot CLI is responsive: `copilot --version` |
| Tool calls not working | Expected — use OpenRouter backend for agentic tasks |

## Related Documents

- [Models](models.md) — Model selection and provider overview
- [Configuration](configuration.md) — Full config.yaml reference
- [Setup Guide](setup_guide.md) — Initial installation
- [Troubleshooting](troubleshooting.md) — Common issues
