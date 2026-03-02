# Droid -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The droid package provides a thread-safe task execution framework built around `DroidController`, `DroidConfig`, and `TodoManager`. It processes structured TODO lists through resolved handler functions, with configurable operation permissions, retry settings, and real-time execution metrics.

## Architecture

The package follows a controller-configuration-manager pattern:

- **DroidConfig** (immutable frozen dataclass) holds all settings and is constructed via factory classmethods (`from_dict`, `from_json`, `from_file`, `from_env`).
- **DroidController** wraps the config with thread-safe lifecycle management (STOPPED -> IDLE -> RUNNING -> ERROR) and delegates task execution to resolved handler callables.
- **TodoManager** handles file-based TODO persistence in a two-section format (`[TODO]` / `[COMPLETED]`).
- **run_todo_droid** orchestrates the end-to-end flow: load TODOs, resolve handlers, execute through the controller, display progress, and rotate completed items.

## Key Classes

### `DroidConfig`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `from_dict` | `data: dict[str, Any]` | `DroidConfig` | Construct from dictionary, coercing mode strings to `DroidMode` |
| `from_json` | `raw: str` | `DroidConfig` | Construct from JSON string |
| `from_file` | `path: str \| PathLike` | `DroidConfig` | Construct from JSON file on disk |
| `from_env` | `prefix: str = "DROID_"` | `DroidConfig` | Construct from environment variables with given prefix |
| `with_overrides` | `**kwargs` | `DroidConfig` | Return new config with overrides applied (validates) |
| `validate` | -- | `None` | Raises `ValueError` if constraints violated (e.g. `max_parallel_tasks < 1`) |

### `DroidController`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `start` | -- | `None` | Transitions to IDLE, increments `sessions_started` |
| `stop` | -- | `None` | Transitions to STOPPED, increments `sessions_completed` |
| `execute_task` | `operation_id: str, handler: Callable, *args, **kwargs` | `Any` | Permission-checks, enters execution state, calls handler, tracks metrics |
| `update_config` | `**overrides` | `DroidConfig` | Thread-safe config update |
| `reset_metrics` | -- | `None` | Zeros all metric counters |
| `record_heartbeat` | -- | `None` | Stores current epoch as last heartbeat |

### `TodoManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `load` | -- | `tuple[list[TodoItem], list[TodoItem]]` | Parse TODO file into (pending, completed) lists |
| `save` | `todo_items, completed_items` | `None` | Write items back to file |
| `rotate` | `processed, remaining, completed` | `None` | Move processed items to completed section |
| `validate` | -- | `tuple[bool, list[tuple]]` | Check file for structural issues |
| `migrate_to_three_columns` | -- | `int` | Convert legacy entries to new format; returns count of changed lines |

### `TodoItem`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `parse` | `raw: str` | `TodoItem` | Parse a pipe-delimited line into a TodoItem (auto-detects legacy vs new format) |
| `serialise` | -- | `str` | Serialize in 3-column format |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`, `codomyrmex.performance`
- **External**: Standard library only (`threading`, `json`, `argparse`, `time`, `pathlib`, `dataclasses`, `enum`)

## Constraints

- `DroidConfig` fields are validated on construction: `max_parallel_tasks >= 1`, `max_retry_attempts >= 0`, `retry_backoff_seconds >= 0`, `heartbeat_interval_seconds > 0`.
- `execute_task` raises `RuntimeError` if controller is STOPPED, `PermissionError` for blocked/unallowed operations or `unsafe_*` handlers in safe mode, and `RuntimeError` if max parallel tasks exceeded.
- TODO file format requires `[TODO]` and `[COMPLETED]` section headers; entries without a preceding header cause `ValueError`.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `DroidConfig.validate()` raises `ValueError` for invalid configuration parameters.
- `DroidController.execute_task()` catches handler exceptions, records them in `DroidMetrics.last_error`, transitions to ERROR state, and re-raises.
- `TodoItem.parse()` raises `ValueError` for lines not matching the expected 3-column pipe format.
- `TodoManager.load()` logs warnings for malformed lines and continues (does not abort).
- All errors logged via `logging_monitoring` before propagation.
