# Orchestrator Observability -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides structured observability for the orchestrator through two complementary subsystems: typed event factories for workflow/task lifecycle events, and reporting utilities for log persistence and summary generation.

## Architecture

Event factories follow a pure-function pattern: each function accepts workflow/task context and returns an `Event` instance without side effects. Reporting functions handle I/O (disk writes, subprocess calls) and are responsible for their own error handling and logging.

## Key Functions

### `orchestrator_events.py` -- Event Factories

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `workflow_started` | `workflow_name: str, total_tasks: int` | `Event` | WORKFLOW_STARTED event |
| `workflow_completed` | `workflow_name, completed, failed, skipped, elapsed` | `Event` | WORKFLOW_COMPLETED with success flag |
| `workflow_failed` | `workflow_name: str, error: str` | `Event` | WORKFLOW_FAILED at priority 2 |
| `task_started` | `workflow_name: str, task_name: str` | `Event` | TASK_STARTED event |
| `task_completed` | `workflow_name, task_name, execution_time, attempts` | `Event` | TASK_COMPLETED with timing |
| `task_failed` | `workflow_name, task_name, error` | `Event` | TASK_FAILED at priority 2 |
| `task_retrying` | `workflow_name, task_name, attempt, delay, error` | `Event` | TASK_RETRYING with retry context |

### `reporting.py` -- Report Generation

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `save_log` | `result: dict, output_dir: Path, run_id: str` | `Path` | Write per-script log file with stdout/stderr |
| `generate_report` | `results: list[dict], output_dir: Path, run_id: str` | `dict` | JSON summary grouped by subdirectory |
| `generate_script_documentation` | `scripts_dir: Path, output_file: Path` | `bool` | Markdown docs via `--help` invocation |

## Dependencies

- **Internal**: `codomyrmex.events.core.event_schema` (Event, EventType), `codomyrmex.logging_monitoring`, `codomyrmex.utils.cli_helpers`, `orchestrator.discovery`
- **External**: `json`, `subprocess`, `pathlib` (stdlib)

## Constraints

- Event source format is always `orchestrator.{workflow_name}` for consistent filtering.
- `generate_report` strips stdout/stderr from the JSON summary to keep file size manageable.
- `generate_script_documentation` runs scripts with `--help` and a 5-second timeout per script; timeouts are logged but do not halt generation.
- Zero-mock: real subprocess calls and file I/O only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `save_log` handles bytes-to-string decoding with `errors="replace"`.
- `generate_script_documentation` catches `TimeoutExpired`, `ValueError`, `RuntimeError`, `OSError` per script and records failure without aborting.
- All errors logged before propagation.
