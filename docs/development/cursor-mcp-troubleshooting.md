# Cursor MCP troubleshooting (`spawn … ENOENT`)

Cursor starts MCP servers as **child processes** with a **minimal environment**. On macOS, the GUI often does **not** inherit your shell `PATH` (`~/.local/bin`, nvm, fnm, Homebrew Apple Silicon paths, etc.). Any `command` that is not an **absolute path** to a real binary can fail with:

```text
A system error occurred (spawn <name> ENOENT)
```

`No server info found` in the same log usually means the client never finished `initialize` because the process never started.

**Cursor `mcp.json` (stdio):** each local server should include **`"type": "stdio"`** (required in [Cursor MCP docs](https://cursor.com/docs/mcp)). Without it, servers may not connect reliably.

## `uv` (Codomyrmex server)

Use the repo **virtualenv interpreter** (after `uv sync`), not bare `uv`:

- `type`: `"stdio"`
- `command`: `/absolute/path/to/codomyrmex/.venv/bin/python`
- `args`: `["scripts/model_context_protocol/run_pai_mcp_stdio.py"]`
- `cwd`: repo root

See [cursor-mcp.json.example](cursor-mcp.json.example) and [cursor-integration.md](cursor-integration.md).

## `codex` (e.g. `plugin-second-opinion-codex`)

Logs such as `Starting new stdio process with command: codex mcp-server` followed by **`spawn codex ENOENT`** mean the **OpenAI Codex CLI** is missing or not on the PATH Cursor uses.

### 1. Install the CLI (official)

Per [OpenAI Codex CLI](https://developers.openai.com/codex/cli/):

```bash
npm i -g @openai/codex
```

Confirm in **Terminal**:

```bash
which codex
codex --version
```

Typical **Homebrew on Apple Silicon** installs the binary at:

`/opt/homebrew/bin/codex`

### 2. If Terminal finds `codex` but Cursor does not

Cursor’s GUI often omits Homebrew and shell-only PATH entries. **Use the absolute path from `which codex`**, not the bare name `codex`.

**Add a user MCP server** in `~/.cursor/mcp.json` (works even when an extension still fails):

```json
"codex": {
  "type": "stdio",
  "command": "/opt/homebrew/bin/codex",
  "args": ["mcp-server"],
  "env": {
    "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
  }
}
```

On **Intel Mac / Homebrew**, `which codex` is often `/usr/local/bin/codex` — use that path instead.

**Extension-only (`plugin-second-opinion-codex`):** if the plugin keeps spawning `codex` with no path, fix it in that extension’s settings (custom command) **or** symlink:

```bash
sudo ln -sf "$(which codex)" /usr/local/bin/codex
```

(if Cursor’s minimal PATH includes `/usr/local/bin` on your machine).

**Other options:**

- **Use the absolute path** from `which codex` anywhere the extension lets you override the MCP command.

- **Login-shell wrapper** (fragile, but sometimes enough):

  ```json
  "command": "/bin/zsh",
  "args": ["-ilc", "exec codex mcp-server"]
  ```

  Only use if your extension or `mcp.json` allows replacing the default `codex mcp-server` invocation.

### 3. If you do not use Codex

Disable or remove the **Second Opinion / Codex** MCP integration in Cursor (Extensions or MCP server list) so it stops spawning `codex mcp-server`.

## Verify Codomyrmex MCP (repo)

```bash
uv run pytest src/codomyrmex/tests/integration/pai/test_mcp_stdio_bidirectional.py --no-cov -q
```

## Navigation

- [Cursor integration](cursor-integration.md)
- [Documentation hub](../README.md)
