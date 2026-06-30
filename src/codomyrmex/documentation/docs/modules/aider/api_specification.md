# aider -- API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Module: `codomyrmex.aider`

### Module-Level Exports

| Name | Type | Description |
|------|------|-------------|
| `HAS_AIDER` | `bool` | `True` when `aider` binary is found in PATH at import time |
| `AiderRunner` | class | Subprocess wrapper for aider CLI |
| `AiderConfig` | dataclass | Environment-sourced configuration |
| `get_config` | function | Factory for `AiderConfig` |
| `get_aider_version` | function | Returns installed aider version string |
| `AiderError` | exception | Base exception class |
| `AiderNotInstalledError` | exception | Aider binary not found |
| `AiderTimeoutError` | exception | Subprocess timeout exceeded |
| `AiderAPIKeyError` | exception | API key missing or invalid |

---

## `AiderRunner`

**Module**: `codomyrmex.aider.core`

### Constructor

```python
AiderRunner(model: str = "", timeout: int = 300)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str` | `""` | LLM model name. If empty, reads from `AiderConfig.model` |
| `timeout` | `int` | `300` | Subprocess timeout in seconds |

**Behavior**: Calls `get_config()` internally to resolve default model. Does not validate that aider is installed -- validation happens at method call time.

---

### `run_message(files, instruction)`

```python
def run_message(self, files: list[str], instruction: str) -> dict[str, str]
```

Run aider in code mode with a single instruction.

| Parameter | Type | Description |
|-----------|------|-------------|
| `files` | `list[str]` | File paths to include in aider context |
| `instruction` | `str` | Natural-language instruction for the edit |

**Returns**: `dict` with keys:
- `stdout` (`str`) -- captured standard output
- `stderr` (`str`) -- captured standard error
- `returncode` (`str`) -- process exit code as string

**Raises**:
- `AiderNotInstalledError` -- aider binary not in PATH
- `AiderTimeoutError` -- subprocess exceeded timeout

---

### `run_ask(files, question)`

```python
def run_ask(self, files: list[str], question: str) -> dict[str, str]
```

Run aider in ask mode (no file changes).

| Parameter | Type | Description |
|-----------|------|-------------|
| `files` | `list[str]` | File paths to include as context |
| `question` | `str` | Question to ask about the code |

**Returns**: `dict` with keys: `stdout`, `stderr`, `returncode`

**Raises**: `AiderNotInstalledError`, `AiderTimeoutError`

---

### `run_architect(files, task, editor_model)`

```python
def run_architect(
    self, files: list[str], task: str, editor_model: str = ""
) -> dict[str, str]
```

Run aider in architect mode for complex multi-step tasks.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `files` | `list[str]` | -- | File paths to include |
| `task` | `str` | -- | Complex task description |
| `editor_model` | `str` | `""` | Separate editor model (defaults to architect model) |

**Returns**: `dict` with keys: `stdout`, `stderr`, `returncode`

**Raises**: `AiderNotInstalledError`, `AiderTimeoutError`

---

## `AiderConfig`

**Module**: `codomyrmex.aider.config`

```python
@dataclass
class AiderConfig:
    model: str           # default: os.getenv("AIDER_MODEL", "claude-sonnet-4-6")
    anthropic_api_key: str  # default: os.getenv("ANTHROPIC_API_KEY", "")
    openai_api_key: str     # default: os.getenv("OPENAI_API_KEY", "")
    timeout: int            # default: int(os.getenv("AIDER_TIMEOUT", "300"))
```

### Properties

| Property | Return Type | Description |
|----------|-------------|-------------|
| `has_anthropic_key` | `bool` | `True` if `anthropic_api_key` is non-empty |
| `has_openai_key` | `bool` | `True` if `openai_api_key` is non-empty |
| `has_any_key` | `bool` | `True` if at least one API key is set |

---

## `get_config()`

**Module**: `codomyrmex.aider.config`

```python
def get_config() -> AiderConfig
```

Returns a fresh `AiderConfig` populated from current environment variables. Each call reads env vars anew -- no caching.

---

## `get_aider_version()`

**Module**: `codomyrmex.aider.core`

```python
def get_aider_version() -> str
```

Returns the installed aider version string (e.g. `"aider v0.77.0"`). Returns empty string `""` if aider is not installed or the version check fails.

**Behavior**: Runs `aider --version` as a subprocess with a 10-second timeout. Does not raise exceptions.

---

## Exception Hierarchy

**Module**: `codomyrmex.aider.exceptions`

### `AiderError`

```python
class AiderError(Exception)
```

Base exception for all aider-related errors.

### `AiderNotInstalledError`

```python
class AiderNotInstalledError(AiderError)
```

Raised when `shutil.which("aider")` returns `None`. Message includes install instructions.

### `AiderTimeoutError`

```python
class AiderTimeoutError(AiderError)
```

Raised when a subprocess call exceeds the configured timeout. Wraps `subprocess.TimeoutExpired` via `raise ... from exc`.

### `AiderAPIKeyError`

```python
class AiderAPIKeyError(AiderError)
```

Raised when a required API key is missing or invalid for the selected model. Currently not raised by core module -- available for consumer use.

---

## Navigation

- **Module README**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Agent Capabilities**: [AGENTS.md](AGENTS.md)
- **Technical Spec**: [SPEC.md](SPEC.md)
- **PAI Integration**: [PAI.md](PAI.md)
