# edge_computing/scheduling — Technical Specification

## Overview

Single-module scheduler (`scheduler.py`) providing in-process job management for edge function invocations with support for one-shot, interval, and cron-like schedule types.

## Architecture

The `EdgeScheduler` maintains a thread-safe dict of `ScheduledJob` entries. It does not run its own event loop; callers poll `get_due_jobs()` and call `mark_executed()` after invocation. This design decouples scheduling from execution.

## Key Classes

### ScheduleType (Enum)

| Value | Behavior |
|-------|----------|
| `ONCE` | Runs once, then `enabled` set to False |
| `INTERVAL` | Repeats every `interval_seconds`; `next_run` advanced after each execution |
| `CRON_LIKE` | Placeholder for cron expression support (not yet implemented) |

### ScheduledJob (dataclass)

| Field | Type | Default |
|-------|------|---------|
| `id` | `str` | required |
| `function_id` | `str` | required |
| `schedule_type` | `ScheduleType` | required |
| `interval_seconds` | `float` | `60.0` |
| `next_run` | `datetime \| None` | `None` |
| `last_run` | `datetime \| None` | `None` |
| `run_count` | `int` | `0` |
| `max_runs` | `int \| None` | `None` |
| `enabled` | `bool` | `True` |
| `args` | `tuple` | `()` |
| `kwargs` | `dict[str, Any]` | `{}` |

Property: `exhausted -> bool` (True when `run_count >= max_runs`).

### EdgeScheduler

| Method | Signature | Returns |
|--------|-----------|---------|
| `add_job` | `(job_id, function_id, schedule_type, interval_seconds, max_runs, args, kwargs)` | `ScheduledJob` |
| `remove_job` | `(job_id: str)` | `bool` |
| `get_job` | `(job_id: str)` | `ScheduledJob \| None` |
| `list_jobs` | `(enabled_only: bool)` | `list[ScheduledJob]` |
| `get_due_jobs` | `()` | `list[ScheduledJob]` |
| `mark_executed` | `(job_id: str)` | None |
| `summary` | `()` | `dict` (total, enabled, exhausted, total_runs) |

## Dependencies

Standard library only: `threading`, `datetime`, `dataclasses`, `enum`.

## Constraints

- No built-in event loop; requires external polling of `get_due_jobs()`.
- `CRON_LIKE` schedule type is defined but has no cron-expression parser.
- Uses naive `datetime.now()` (no timezone awareness).
- In-process only; for distributed scheduling, integrate with an external scheduler.
