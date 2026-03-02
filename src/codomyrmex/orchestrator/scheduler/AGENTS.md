# Codomyrmex Agents — src/codomyrmex/orchestrator/scheduler

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Task scheduling system supporting one-time, interval, and cron trigger types with a background execution loop. Extends to dependency-aware scheduling, persistent state, and multi-stage job pipelines.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `triggers.py` | `Trigger` (ABC) | Abstract base for all trigger types with `get_next_run` contract |
| `triggers.py` | `OnceTrigger` | Fires once at a specific `datetime` |
| `triggers.py` | `IntervalTrigger` | Fires at regular intervals with optional start/end bounds |
| `triggers.py` | `CronTrigger` | Simplified cron-expression trigger (minute-level scanning up to 1 year) |
| `models.py` | `Job` | Scheduled job dataclass with trigger, status, run count, and self-executing `execute()` method |
| `models.py` | `JobStatus` | Enum: pending, running, completed, failed, cancelled |
| `scheduler.py` | `Scheduler` | Core thread-based scheduler with heapq priority queue and `ThreadPoolExecutor` |
| `scheduler.py` | `every`, `at`, `cron` | Convenience functions for creating `IntervalTrigger`, `OnceTrigger`, `CronTrigger` |
| `advanced.py` | `DependencyScheduler` | Extends `Scheduler` with inter-job dependency tracking and blocked/satisfied states |
| `advanced.py` | `PersistentScheduler` | Extends `Scheduler` with JSON state persistence and registered-function reload |
| `advanced.py` | `JobPipeline` | Multi-stage pipeline runner with parallel jobs within each stage |
| `advanced.py` | `ScheduledRecurrence` / `parse_cron` / `describe_cron` | Recurrence model and cron expression parsing utilities |

## Operating Contracts

- `Scheduler` runs a background daemon thread polling at 100ms intervals.
- Jobs are ordered via `heapq` using `Job.__lt__` (next_run comparison).
- `DependencyScheduler` blocks jobs whose `depends_on` list includes failed or incomplete jobs.
- `PersistentScheduler` requires functions to be pre-registered by name for JSON-based reload.
- `CronTrigger.get_next_run` scans minute-by-minute up to 525,600 iterations (1 year).
- Errors must be logged via `logging` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.validation.schemas` (optional `Result`/`ResultStatus` for cross-module interop)
- **Used by**: `orchestrator` top-level, CI/CD automation, workflow triggers

## Navigation

- **Parent**: [orchestrator](../README.md)
- **Root**: [Root](../../../../README.md)
