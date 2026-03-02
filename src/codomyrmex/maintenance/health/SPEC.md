# Health - Technical Specification

## Overview

Two-part framework: `HealthChecker` for on-demand system health probes with aggregated reporting, and `MaintenanceScheduler` for recurring task execution with priority ordering and retry logic.

## Key Classes

### `HealthChecker` (health_check.py)

| Method | Parameters | Returns |
|--------|-----------|---------|
| `register` | `check: HealthCheck` | `None` |
| `unregister` | `name: str` | `bool` |
| `run` | `name: str` | `HealthCheckResult` |
| `run_all` | none | `AggregateHealthReport` |
| `last_result` | `name: str` | `HealthCheckResult \| None` |
| `summary_text` | `report: AggregateHealthReport` | `str` (multi-line summary) |
| `clear` | none | `None` |

Property: `check_count -> int`.

`AggregateHealthReport` fields: `overall_status`, `checks` (list), `total_duration_ms`, `healthy_count`, `degraded_count`, `unhealthy_count`.

Overall status logic: UNHEALTHY if any unhealthy, else DEGRADED if any degraded, else HEALTHY if any healthy, else UNKNOWN.

### `MaintenanceScheduler` (scheduler.py)

| Method | Parameters | Returns |
|--------|-----------|---------|
| `register` | `task: MaintenanceTask` | `None` |
| `unregister` | `name: str` | `bool` |
| `get_task` | `name: str` | `MaintenanceTask \| None` |
| `list_tasks` | none | `list[MaintenanceTask]` (sorted by priority) |
| `get_due_tasks` | `now: float` | `list[MaintenanceTask]` |
| `execute` | `name: str` | `TaskResult` |
| `history` | `limit: int = 50` | `list[TaskResult]` (most recent first) |
| `clear_history` | none | `None` |

Property: `task_count -> int`.

`execute()` retry loop: tries action up to `max_retries + 1` times. On success, returns COMPLETED. On exhausted retries, returns FAILED with last error message. Updates `last_run`, `last_result`, and `run_count` on the task.

## Dependencies

- **Internal**: None (standalone module using only stdlib)
- **External**: `time`, `collections.abc`, `dataclasses`, `enum`

## Constraints

- All data is in-memory only -- no persistence across process restarts.
- `run_on_startup` tasks execute on first `get_due_tasks()` call when `last_run == 0.0`.
- Exception in a health check function results in UNHEALTHY status (not propagated).

## Error Handling

| Error | Trigger |
|-------|---------|
| `KeyError` | `run()` or `execute()` called with unregistered name |
| Exception capture | Health check exceptions caught and returned as UNHEALTHY result |
