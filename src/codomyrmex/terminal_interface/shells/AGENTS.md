# Codomyrmex Agents -- terminal_interface/shells

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Shell management utilities for executing commands, managing interactive shell sessions, and building shell command strings programmatically.

## Key Components

| Component | Role |
|-----------|------|
| `ShellType` | Enum: `BASH`, `ZSH`, `SH`, `FISH`, `POWERSHELL`, `CMD` |
| `ShellConfig` | Configuration dataclass with `detect()` classmethod for auto-detecting the default shell from `$SHELL` |
| `CommandResult` | Result dataclass: `command`, `exit_code`, `stdout`, `stderr`, `duration_ms`, `success` property |
| `Shell` | Execute commands synchronously via `run()` or in background via `run_background()`; maintains command history |
| `InteractiveShell` | Long-lived interactive shell session with threaded output reader; supports `send()`, `read_output()`, `execute()`, `stop()` |
| `CommandBuilder` | Fluent API for constructing shell commands with `add()`, `flag()`, `env()`, `pipe()`, `redirect_stdout/stderr()`, `background()`, `build()` |
| `create_shell(shell_type)` | Factory function returning a `Shell` with the specified or auto-detected shell type |

## Operating Contracts

- `Shell.run()` uses `subprocess.run()` with `capture_output=True, text=True`; returns `CommandResult` with exit code `-1` on timeout or exception.
- `InteractiveShell.start()` spawns a subprocess with `-i` flag and a daemon reader thread; `stop()` terminates then kills if timeout.
- `CommandBuilder.build()` produces a single command string with env var prefixes, arguments, and redirects joined by spaces; paths are `shlex.quote()`-escaped.
- `ShellConfig.detect()` reads `$SHELL` and maps the basename to a `ShellType`; defaults to `SH`.
- `Shell` maintains a `_history: list[CommandResult]` of all executed commands.

## Integration Points

- Used by `terminal_interface` parent module for shell execution in interactive CLI sessions.
- `CommandResult.to_dict()` provides JSON-serializable output for logging and telemetry.

## Navigation

- [README](../README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- Parent: [terminal_interface](../README.md)
