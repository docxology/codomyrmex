# Terminal Shells -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Shell execution layer providing synchronous and interactive command execution, command history, and a fluent command builder.

## Architecture

```
shells/
├── __init__.py              # ShellType, ShellConfig, CommandResult, Shell, InteractiveShell, CommandBuilder, create_shell
└── interactive_shell.py     # InteractiveShell extending cmd.Cmd with module exploration commands
```

## Key Classes

### Shell

| Method | Signature | Description |
|--------|-----------|-------------|
| `run` | `(command: str, timeout=None, env=None, cwd=None) -> CommandResult` | Execute command synchronously via subprocess |
| `run_background` | `(command: str, env=None, cwd=None) -> subprocess.Popen` | Launch command as background process |
| `get_history` | `() -> list[CommandResult]` | Return copy of command history |
| `clear_history` | `() -> None` | Clear command history |

### InteractiveShell

| Method | Signature | Description |
|--------|-----------|-------------|
| `start` | `() -> None` | Spawn shell subprocess with daemon output reader thread |
| `send` | `(command: str) -> None` | Write command to shell stdin |
| `read_output` | `(timeout: float = 1.0) -> str` | Read available output from queue |
| `execute` | `(command: str, timeout: float = 5.0) -> str` | Clear pending output, send command, return output |
| `stop` | `() -> None` | Terminate shell process (kill after 2s timeout); join reader thread |
| `is_running` | Property | Whether shell process is active |

### CommandBuilder

| Method | Signature | Description |
|--------|-----------|-------------|
| `add` | `(*args: str) -> CommandBuilder` | Append arguments |
| `flag` | `(name: str, value=None) -> CommandBuilder` | Add flag with optional value |
| `env` | `(key: str, value: str) -> CommandBuilder` | Add env var prefix |
| `pipe` | `(command: str) -> CommandBuilder` | Pipe output to another command |
| `redirect_stdout` | `(path: str, append=False) -> CommandBuilder` | Redirect stdout (`>` or `>>`) |
| `redirect_stderr` | `(path: str) -> CommandBuilder` | Redirect stderr (`2>`) |
| `background` | `() -> CommandBuilder` | Append `&` |
| `build` | `() -> str` | Build final command string |

### ShellConfig

| Method | Signature | Description |
|--------|-----------|-------------|
| `detect` | `classmethod() -> ShellConfig` | Auto-detect shell from `$SHELL` env var |

Fields: `shell_type: ShellType`, `executable: str`, `args: list[str]`, `env: dict[str, str]`, `cwd: str | None`, `timeout: float | None`.

## Dependencies

- Python standard library: `subprocess`, `threading`, `queue`, `shlex`, `signal`, `os`, `time`
- No external dependencies

## Constraints

- `InteractiveShell` uses a daemon thread for output reading; the thread terminates when the shell process exits or `stop()` is called.
- `Shell.run()` merges `os.environ` with config env and per-call env in that priority order.
- `CommandBuilder` does not validate command syntax; `build()` produces a raw string.
- `ShellConfig.detect()` does not handle Windows shells; defaults to `SH` for unknown shell names.

## Navigation

- [README](../README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
