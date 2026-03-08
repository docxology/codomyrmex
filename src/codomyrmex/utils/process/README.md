# Process Utilities

> **Codomyrmex v1.1.9** | Sub-module of `utils` | March 2026

## Overview

The `utils.process` sub-module provides a unified foundation for subprocess
execution and script orchestration across the codomyrmex platform. It
consolidates synchronous/asynchronous command execution, real-time output
streaming, configurable retry logic, and a reusable `ScriptBase` class that
standardises CLI argument parsing, logging, output management, and result
collection for all project scripts.

## PAI Integration

| PAI Phase | Usage |
|-----------|-------|
| BUILD     | Execute build commands, compile steps, code-generation scripts |
| EXECUTE   | Run arbitrary system commands during agent workflows |
| VERIFY    | Invoke test runners, linters, and validation scripts |

## Key Exports

| Export | Source | Description |
|--------|--------|-------------|
| `run_command` | `subprocess.py` | Synchronous command execution with timeout and error handling |
| `run_command_async` | `subprocess.py` | Async command execution via `asyncio` |
| `stream_command` | `subprocess_advanced.py` | Generator that yields output lines in real time |
| `run_with_retry` | `subprocess_advanced.py` | Execute a command with configurable retry logic |
| `SubprocessResult` | `subprocess.py` | Dataclass encapsulating execution result, timing, and exit code |
| `CommandError` | `subprocess.py` | Rich exception with error type, captured output, and original exception |
| `CommandErrorType` | `subprocess.py` | Enum categorising failure reasons (timeout, permission, not found, etc.) |
| `check_command_available` | `subprocess.py` | Check whether a CLI tool is installed on the system |
| `get_command_version` | `subprocess.py` | Retrieve the version string of an installed command |
| `quote_command` | `subprocess.py` | Shell-safe quoting via `shlex.join` |
| `split_command` | `subprocess.py` | Split a shell command string into an argument list via `shlex.split` |
| `ScriptBase` | `script_base.py` | Abstract base class for standardised script execution |
| `ScriptConfig` | `script_base.py` | Dataclass holding runtime, output, and logging configuration |
| `ScriptResult` | `script_base.py` | Dataclass for structured script execution results |

## Quick Start

```python
from codomyrmex.utils.process import run_command, SubprocessResult

# Synchronous execution
result: SubprocessResult = run_command(["git", "status"], timeout=30)
if result.success:
    print(result.stdout)

# Raise on failure
run_command(["uv", "run", "pytest"], check=True)
```

```python
from codomyrmex.utils.process import stream_command

# Stream output line-by-line
for line in stream_command(["python", "-m", "pytest", "-v"]):
    print(line)
```

```python
from codomyrmex.utils.process.script_base import ScriptBase

class AuditScript(ScriptBase):
    def add_arguments(self, parser):
        parser.add_argument("--target", required=True)

    def run(self, args, config):
        return {"status": "success", "findings": []}

script = AuditScript(name="audit", description="Run audit")
```

## Architecture

```
utils/process/
  __init__.py              # Re-exports from subprocess + script_base
  subprocess.py            # Core sync/async execution, SubprocessResult, CommandError
  subprocess_advanced.py   # stream_command, run_with_retry (built on subprocess.py)
  script_base.py           # ScriptBase ABC, ScriptConfig, ScriptResult
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/utils/ -v
```

## Navigation

| Document | Purpose |
|----------|---------|
| [AGENTS.md](AGENTS.md) | Agent coordination guidance |
| [SPEC.md](SPEC.md) | Technical specification |
| [Parent README](../README.md) | `utils` module overview |
