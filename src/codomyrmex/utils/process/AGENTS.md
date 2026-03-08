# Process Utilities - Agent Coordination

> **Codomyrmex v1.1.9** | Sub-module of `utils` | March 2026

## Overview

The `utils.process` sub-module is the standard way for agents to execute
external commands, scripts, and long-running processes. It provides structured
results, timeout handling, and retry logic so agents do not need to interact
with `subprocess` directly.

## Key Files

| File | Purpose |
|------|---------|
| `subprocess.py` | `run_command`, `run_command_async`, `SubprocessResult`, `CommandError` |
| `subprocess_advanced.py` | `stream_command` (real-time output), `run_with_retry` |
| `script_base.py` | `ScriptBase` ABC for building standardised scripts with CLI, logging, output management |
| `__init__.py` | Re-exports all public symbols from the above modules |

## MCP Tools Available

No MCP tools defined in this sub-module. Command execution is exposed at a
higher level through the PAI trust gateway (`run_command` destructive tool).

## Agent Instructions

1. **Always use `run_command` instead of raw `subprocess.run`** -- it provides
   consistent `SubprocessResult` objects, automatic timeout handling, and
   structured error types via `CommandError`.
2. **Use `check=True` for must-succeed commands** -- this raises `CommandError`
   on non-zero exit codes, preventing silent failures.
3. **Prefer `run_command_async` in async agent loops** -- it uses
   `asyncio.create_subprocess_exec/shell` so the event loop is not blocked.
4. **Use `stream_command` for long-running processes** -- the generator yields
   lines as they arrive, allowing agents to monitor progress or detect errors
   early.
5. **Subclass `ScriptBase` for reusable scripts** -- it provides argument
   parsing, structured logging, timestamped output directories, and JSON/YAML
   result serialisation out of the box.

## Operating Contracts

- `SubprocessResult.success` is `True` only when `return_code == 0` and
  `timed_out is False`.
- `CommandError` always carries `error_type` (a `CommandErrorType` enum),
  the original command, captured stdout/stderr, and the underlying exception.
- `stream_command` yields prefixed lines (`stdout:` / `stderr:`) unless
  `combine_streams=True`.
- `ScriptBase.execute()` returns an integer exit code suitable for `sys.exit`.

## Common Patterns

```python
# Pattern: safe command execution with error propagation
from codomyrmex.utils.process import run_command, CommandError

try:
    result = run_command(["git", "diff", "--stat"], check=True, timeout=30)
    print(result.stdout)
except CommandError as err:
    logger.error("Git diff failed: %s (type=%s)", err.message, err.error_type.value)
    raise
```

```python
# Pattern: check tool availability before use
from codomyrmex.utils.process import check_command_available, get_command_version

if check_command_available("ruff"):
    version = get_command_version("ruff")
    logger.info("Using ruff %s", version)
```

## PAI Agent Role Access Matrix

| Agent Role | Permitted Operations |
|------------|---------------------|
| Engineer   | Full access -- execute commands, stream output, build scripts |
| Architect  | Read-only inspection (check_command_available, get_command_version) |
| QATester   | Execute test runners and linters via run_command |

## Navigation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Module overview and quick start |
| [SPEC.md](SPEC.md) | Technical specification |
| [Parent README](../README.md) | `utils` module overview |
