# edge_computing/scheduling — Agent Coordination

## Purpose

Provides periodic and one-shot scheduling of edge function invocations. The scheduler manages job registration, due-time evaluation, and execution tracking.

## Key Components

| Component | Role |
|-----------|------|
| `ScheduleType` | Enum: `ONCE` (single execution, auto-disables), `INTERVAL` (repeating with configurable period), `CRON_LIKE` (placeholder for cron expressions) |
| `ScheduledJob` | Job dataclass: function_id, schedule type, interval, next/last run, run count, max runs, enabled flag, args/kwargs |
| `EdgeScheduler` | Thread-safe job registry with add/remove/list, due-job detection, and execution marking |

## Operating Contracts

- `EdgeScheduler.add_job(job_id, function_id, ...)` creates a `ScheduledJob` with `next_run` set to `datetime.now()` (immediately eligible).
- `EdgeScheduler.get_due_jobs()` returns enabled, non-exhausted jobs whose `next_run <= now`.
- `EdgeScheduler.mark_executed(job_id)` increments `run_count`, updates `last_run`, and: for `ONCE` jobs sets `enabled = False`; for `INTERVAL` jobs advances `next_run` by `interval_seconds`.
- `ScheduledJob.exhausted` returns True when `run_count >= max_runs` (if `max_runs` is set).
- All job operations are protected by `threading.Lock`.

## Integration Points

- **Core runtime**: Scheduler references function IDs that are deployed in `EdgeRuntime`. The caller is responsible for invoking `runtime.invoke()` when jobs come due.
- **Metrics**: Invocation results from scheduled runs can be recorded in `EdgeMetrics`.
- **Infrastructure**: Scheduled jobs can trigger periodic cache purges or sync operations.

## Navigation

- **Parent**: [edge_computing README](../../edge_computing/README.md)
- **Siblings**: [core](../core/AGENTS.md) | [infrastructure](../infrastructure/AGENTS.md)
- **Spec**: [SPEC.md](SPEC.md)
