# Scheduler — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Thread-based job scheduling system with trigger types (once, interval, cron), dependency-aware scheduling, persistent state, and multi-stage pipeline execution.

## Architecture

Three-tier design:

1. **Triggers** (`triggers.py`) -- Abstract `Trigger` base with `OnceTrigger`, `IntervalTrigger`, and `CronTrigger` implementations. Each computes `get_next_run(from_time)`.
2. **Core Scheduler** (`scheduler.py`, `models.py`) -- `Scheduler` manages a `heapq`-backed priority queue, daemon polling thread, and `ThreadPoolExecutor` for job execution.
3. **Advanced Extensions** (`advanced.py`) -- `DependencyScheduler` adds inter-job dependency graphs, `PersistentScheduler` adds JSON state save/load, and `JobPipeline` adds staged parallel execution.

## Key Classes

### `Scheduler`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `schedule` | `func, name, trigger, args, kwargs, max_runs` | `str` (job ID) | Schedule a job with trigger |
| `cancel` | `job_id: str` | `bool` | Cancel a pending job |
| `get_job` | `job_id: str` | `Job \| None` | Retrieve job by ID |
| `list_jobs` | `status: JobStatus \| None` | `list[Job]` | List jobs optionally filtered |
| `start` | none | `None` | Start background daemon thread |
| `stop` | none | `None` | Stop scheduler and shutdown executor |
| `run_now` | `job_id: str` | `Any` | Execute job immediately |

### `DependencyScheduler` (extends `Scheduler`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_dependency` | `job_id: str, depends_on: list[str]` | `None` | Declare dependency edges |
| `schedule_with_deps` | `func, depends_on, **kwargs` | `str` | Schedule job with dependencies in one call |

### `PersistentScheduler` (extends `Scheduler`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register_function` | `name: str, func: Callable` | `None` | Register function for persistent lookup |
| `schedule` | `func, function_name, **kwargs` | `str` | Schedule with auto-save if function_name given |
| `stop` | none | `None` | Stop and persist state to JSON |

### `CronTrigger`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `from_expression` | `expr: str` | `CronTrigger` | Parse 5-field cron string |
| `get_next_run` | `from_time: datetime \| None` | `datetime \| None` | Scan forward to find next matching minute |

## Dependencies

- **Internal**: `codomyrmex.validation.schemas` (optional)
- **External**: Standard library (`threading`, `concurrent.futures`, `heapq`, `json`, `pathlib`)

## Constraints

- Background thread sleeps 100ms between polls; not suitable for sub-100ms scheduling precision.
- `CronTrigger` uses brute-force minute scanning (max 525,600 iterations).
- `PersistentScheduler` state file stores function names, not closures; functions must be pre-registered.
- `JobPipeline.run` is async; polls job status at 100ms intervals waiting for stage completion.
- Zero-mock: real thread execution only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `Job.execute` catches broad exception tuple, sets `JobStatus.FAILED`, records error string, then re-raises.
- `Scheduler._execute_job` catches and logs failures without crashing the scheduler loop.
- `PersistentScheduler._load_state` catches `json.JSONDecodeError` / `KeyError` and logs warning.
- `CronTrigger.from_expression` raises `ValueError` for malformed expressions.
