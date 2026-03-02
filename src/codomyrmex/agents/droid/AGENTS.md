# Codomyrmex Agents -- src/codomyrmex/agents/droid

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The droid package implements a thread-safe autonomous task runner that processes TODO lists through configurable controllers, with support for handler resolution, interactive and non-interactive execution modes, and real-time progress metrics.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `controller.py` | `DroidController` | Thread-safe controller coordinating droid operations with lifecycle management (start/stop), task execution gated by permission checks, and performance-monitored methods |
| `controller.py` | `DroidConfig` | Frozen dataclass holding immutable configuration (LLM provider, mode, safe_mode, retry settings); constructed from dicts, JSON, files, or environment variables |
| `controller.py` | `DroidMetrics` | Mutable dataclass tracking sessions started/completed, tasks executed/failed, last error, and heartbeat timestamps |
| `controller.py` | `DroidMode` / `DroidStatus` | Enums for operating modes (DEVELOPMENT, PRODUCTION, TEST, MAINTENANCE) and lifecycle states (STOPPED, IDLE, RUNNING, ERROR) |
| `todo.py` | `TodoItem` | Dataclass representing a single TODO entry; parses both new 3-column format (`task_name | description | outcomes`) and legacy handler-based format |
| `todo.py` | `TodoManager` | Manages TODO file I/O: load, save, rotate completed items, validate entries, and migrate legacy formats to 3-column |
| `tasks.py` | `ensure_documentation_exists` | Task handler verifying DroidController has docstrings |
| `tasks.py` | `verify_real_methods` | Task handler confirming required symbols exist in the controller module |
| `tasks.py` | `verify_readiness` | Task handler checking that required project directories exist on disk |
| `run_todo_droid.py` | `run_todos` | Core execution loop: processes N items sequentially with progress bars, per-task timing, ETA, and summary statistics |
| `run_todo_droid.py` | `resolve_handler` | Resolves `module:function` handler strings to callables, with short-name expansion for `droid:` and `ai_code:` prefixes |
| `run_todo_droid.py` | `main` | CLI entry point with argparse: supports `--count`, `--list`, `--dry-run`, `--non-interactive`, `--config` |

## Operating Contracts

- `DroidController` uses an `RLock` for all state mutations; callers must not assume single-threaded access.
- `DroidConfig` is immutable (`frozen=True`); updates return new instances via `with_overrides()`.
- Safe mode (`safe_mode=True` by default) rejects handlers whose names start with `unsafe_`.
- Operations are permission-gated: `allowed_operations` whitelist and `blocked_operations` blacklist are checked before every `execute_task` call.
- `TodoManager.load()` skips malformed entries with a warning rather than aborting the entire file.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring.core.logger_config`, `codomyrmex.performance` (`monitor_performance`, `performance_context`)
- **Used by**: CLI invocation via `python -m codomyrmex.agents.droid.run_todo_droid`, droid task handlers in `generators/` subpackage

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [Root](../../../../README.md)
