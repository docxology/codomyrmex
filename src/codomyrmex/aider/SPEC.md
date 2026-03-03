# aider -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Wrap the `aider` CLI tool as a first-class Codomyrmex module with subprocess-based execution, environment-sourced configuration, and MCP tool exposure for agent consumption.

---

## Core Classes

### `AiderRunner`

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(model: str = "", timeout: int = 300)` | Construct runner; resolves model from `AiderConfig` if empty |
| `run_message` | `(files: list[str], instruction: str) -> dict[str, str]` | Run aider in code mode; returns `{"stdout", "stderr", "returncode"}` |
| `run_ask` | `(files: list[str], question: str) -> dict[str, str]` | Run aider in ask mode (no file changes); returns `{"stdout", "stderr", "returncode"}` |
| `run_architect` | `(files: list[str], task: str, editor_model: str = "") -> dict[str, str]` | Run aider in architect mode; returns `{"stdout", "stderr", "returncode"}` |

**Internal methods** (not part of public API):
- `_find_aider() -> str` -- locates aider binary via `shutil.which`; raises `AiderNotInstalledError`
- `_build_cmd(...) -> list[str]` -- constructs the subprocess command list
- `_run_subprocess(cmd) -> subprocess.CompletedProcess` -- executes with timeout

---

### `AiderConfig`

Dataclass populated from environment variables.

| Field | Type | Default | Env Var | Description |
|-------|------|---------|---------|-------------|
| `model` | `str` | `"claude-sonnet-4-6"` | `AIDER_MODEL` | Default LLM model |
| `anthropic_api_key` | `str` | `""` | `ANTHROPIC_API_KEY` | Anthropic API key |
| `openai_api_key` | `str` | `""` | `OPENAI_API_KEY` | OpenAI API key |
| `timeout` | `int` | `300` | `AIDER_TIMEOUT` | Default subprocess timeout (seconds) |

**Properties**:

| Property | Type | Description |
|----------|------|-------------|
| `has_anthropic_key` | `bool` | True when `anthropic_api_key` is non-empty |
| `has_openai_key` | `bool` | True when `openai_api_key` is non-empty |
| `has_any_key` | `bool` | True when at least one API key is set |

---

## Module-Level Constants and Functions

| Name | Type | Description |
|------|------|-------------|
| `HAS_AIDER` | `bool` | True when `aider` binary is found in PATH at import time |
| `get_aider_version()` | `() -> str` | Returns installed version string, or `""` if not installed |
| `get_config()` | `() -> AiderConfig` | Returns a fresh config populated from env vars |

---

## Subprocess Contract

Every `AiderRunner` subprocess call applies these flags unconditionally:

| Flag | Purpose |
|------|---------|
| `--yes` | Auto-confirm all prompts (prevents hanging) |
| `--no-pretty` | Strip ANSI escape codes (clean output capture) |
| `--no-auto-commits` | Disable automatic git commits (caller controls commit) |

The full command structure:

```
aider --model <model> --message <instruction> --yes --no-pretty --no-auto-commits [--chat-mode ask] [--architect] [--editor-model <model>] <files...>
```

- Architect mode uses `--architect` flag instead of `--chat-mode architect`
- Files are passed as trailing positional arguments
- Output is captured via `subprocess.run(capture_output=True, text=True)`

---

## Exception Hierarchy

```
Exception
  +-- AiderError                  # Base for all aider errors
       +-- AiderNotInstalledError  # aider binary not in PATH
       +-- AiderTimeoutError       # subprocess exceeded timeout
       +-- AiderAPIKeyError        # required API key missing
```

All exceptions are defined in `exceptions.py`. MCP tools catch `Exception` and return `{"status": "error", "message": str}`.

---

## MCP Tool Parameter Schemas

### `aider_check()`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| (none) | | | | No parameters |

**Returns**: `{"status", "installed", "version", "model", "install_hint?"}`

### `aider_edit(file_paths, instruction, model, timeout)`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_paths` | `list[str]` | Yes | | Files to edit |
| `instruction` | `str` | Yes | | Natural-language instruction |
| `model` | `str` | No | `"claude-sonnet-4-6"` | LLM model |
| `timeout` | `int` | No | `300` | Timeout in seconds |

**Returns**: `{"status", "output", "stderr", "returncode"}`

### `aider_ask(file_paths, question, model, timeout)`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_paths` | `list[str]` | Yes | | Files as context |
| `question` | `str` | Yes | | Question to ask |
| `model` | `str` | No | `"claude-sonnet-4-6"` | LLM model |
| `timeout` | `int` | No | `120` | Timeout in seconds |

**Returns**: `{"status", "answer", "stderr"}`

### `aider_architect(file_paths, task, model, editor_model, timeout)`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_paths` | `list[str]` | Yes | | Files to include |
| `task` | `str` | Yes | | Task description |
| `model` | `str` | No | `"claude-sonnet-4-6"` | Architect model |
| `editor_model` | `str` | No | `""` | Editor model (defaults to architect model) |
| `timeout` | `int` | No | `600` | Timeout in seconds |

**Returns**: `{"status", "output", "stderr", "returncode"}`

### `aider_config()`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| (none) | | | | No parameters |

**Returns**: `{"status", "model", "has_anthropic_key", "has_openai_key", "has_any_key", "timeout"}`

---

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `AIDER_MODEL` | Default LLM model for aider | `claude-sonnet-4-6` |
| `ANTHROPIC_API_KEY` | API key for Anthropic Claude models | (none) |
| `OPENAI_API_KEY` | API key for OpenAI models | (none) |
| `AIDER_TIMEOUT` | Default subprocess timeout in seconds | `300` |

---

## Dependencies

| Package | Version | Purpose | Optional |
|---|---|---|---|
| `aider-chat` | >= 0.77.0 | CLI binary for AI code editing | Yes (`uv tool install aider-chat`) |
| Python | >= 3.10 | Required by aider | No |

The aider binary is located via `shutil.which("aider")`. No Python import of aider internals is performed -- all interaction is via subprocess.

---

## Thread Safety

- `AiderRunner` instances are thread-safe (no shared mutable state; each call spawns a subprocess).
- MCP tools create fresh `AiderRunner` instances per call.
- Multiple concurrent aider subprocesses editing the same files may conflict on git operations.

---

## Design Principles

1. **Subprocess-only interaction** -- no import of aider internals; binary interface is stable.
2. **Safe defaults** -- `--yes --no-pretty --no-auto-commits` applied unconditionally.
3. **Env-key resolution** -- API keys sourced from environment; never hardcoded.
4. **Import guard** -- `HAS_AIDER` flag evaluated at import time; no silent fallback.
5. **Stateless MCP tools** -- fresh runner per call; no session state.

---

## Navigation

- **Human Guide**: [README.md](README.md)
- **Agent Access**: [AGENTS.md](AGENTS.md)
- **PAI Integration**: [PAI.md](PAI.md)
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent**: [codomyrmex](../SPEC.md)
