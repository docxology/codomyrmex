# Process Utilities - Specification

> **Codomyrmex v1.1.9** | Sub-module of `utils` | March 2026

## Overview

This specification defines the contracts, data structures, and behavioural
guarantees for the `utils.process` sub-module, which provides subprocess
execution and script orchestration infrastructure used across codomyrmex.

## Design Principles

- **Zero-Mock Policy**: Tests must execute real subprocesses. Use
  `@pytest.mark.skipif` when a required CLI tool is absent.
- **Explicit Failure**: Every non-zero exit code, timeout, or OS-level error
  produces a `CommandError` with a specific `CommandErrorType` -- never swallowed
  silently.
- **Structured Results**: All execution paths return a `SubprocessResult`
  dataclass rather than raw strings or exit codes.
- **Environment Isolation**: Custom `env` dictionaries can optionally replace
  or augment the inherited process environment.

## Architecture

```
utils/process/
  __init__.py              # Star-imports from subprocess + script_base
  subprocess.py            # Core execution: run_command, run_command_async
  subprocess_advanced.py   # stream_command, run_with_retry
  script_base.py           # ScriptBase, ScriptConfig, ScriptResult
```

## Functional Requirements

### FR-1: Synchronous Command Execution (`run_command`)

- Accept command as `str` (split via `shlex.split`) or `list[str]`.
- Support keyword-only parameters: `cwd`, `env`, `timeout`, `shell`,
  `capture_output`, `check`, `inherit_env`, `input_data`, `encoding`, `errors`.
- Return `SubprocessResult` on all code paths (success, failure, timeout,
  permission denied, file not found).
- When `check=True`, raise `CommandError` on non-zero exit or timeout.
- Validate `cwd` exists before execution; raise `CommandError` with
  `WORKING_DIR_NOT_FOUND` if missing.

### FR-2: Asynchronous Command Execution (`run_command_async`)

- Use `asyncio.create_subprocess_exec` (non-shell) or
  `asyncio.create_subprocess_shell` (shell mode).
- Timeout via `asyncio.wait_for`; kill process on expiry.
- Return `SubprocessResult` with `timed_out=True` on timeout.

### FR-3: Streaming Output (`stream_command`)

- Yield lines as they arrive from stdout (and optionally stderr).
- Prefix lines with `stdout:` / `stderr:` unless `combine_streams=True`.
- Return `SubprocessResult` when the generator is exhausted.

### FR-4: Retry Logic (`run_with_retry`)

- Accept `max_attempts`, retry delay, and optional `should_retry` callable.
- Delegate each attempt to `run_command`.

### FR-5: Script Base (`ScriptBase`)

- Abstract base class requiring `run(args, config) -> dict`.
- Provide `create_parser()` with standard argument groups (execution, output,
  logging, configuration).
- Manage timestamped output directories and save results as JSON/YAML.
- Track `ScriptResult` with timing, exit code, errors, warnings, and metrics.

## Interface Contracts

### SubprocessResult

```python
@dataclass
class SubprocessResult:
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    duration: float = 0.0
    command: str | list[str] = field(default_factory=list)
    success: bool = True        # True iff return_code == 0 and not timed_out
    timed_out: bool = False
    error_message: str | None = None

    def raise_on_error(self, message: str | None = None) -> SubprocessResult: ...
    def to_dict(self) -> dict[str, Any]: ...
    @property
    def output(self) -> str: ...       # Combined stdout + stderr
    @property
    def command_string(self) -> str: ...
```

### CommandError

```python
class CommandError(Exception):
    message: str
    error_type: CommandErrorType
    command: str | list[str] | None
    return_code: int | None
    stdout: str
    stderr: str
    original_exception: Exception | None
```

### CommandErrorType

```python
class CommandErrorType(Enum):
    EXECUTION_FAILED = "execution_failed"
    TIMEOUT = "timeout"
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    SUBPROCESS_ERROR = "subprocess_error"
    INVALID_COMMAND = "invalid_command"
    WORKING_DIR_NOT_FOUND = "working_dir_not_found"
    UNKNOWN = "unknown"
```

### ScriptConfig

```python
@dataclass
class ScriptConfig:
    dry_run: bool = False
    verbose: bool = False
    quiet: bool = False
    output_dir: Path | None = None
    output_format: str = "json"
    save_output: bool = True
    log_level: str = "INFO"
    log_file: Path | None = None
    log_format: str = "text"
    timeout: int = 300
    max_retries: int = 3
    retry_delay: float = 1.0
    custom: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScriptConfig: ...
    def to_dict(self) -> dict[str, Any]: ...
```

## Dependencies

| Dependency | Purpose |
|------------|---------|
| `asyncio` | Async subprocess execution |
| `shlex` | Safe command splitting and quoting |
| `subprocess` | Core process management |
| `yaml` | YAML config loading in ScriptBase |
| `codomyrmex.logging_monitoring` | Structured logging |

## Constraints

- Shell mode (`shell=True`) requires the command to be a string; list commands
  are joined with spaces.
- `stream_command` reads stdout/stderr line-by-line; binary output is not
  supported.
- `ScriptBase` requires `yaml` at import time; a fallback is provided when
  `codomyrmex.logging_monitoring` is not installed.

## Navigation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Module overview and quick start |
| [AGENTS.md](AGENTS.md) | Agent coordination guidance |
| [Parent README](../README.md) | `utils` module overview |
