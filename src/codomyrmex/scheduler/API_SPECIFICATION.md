# Scheduler API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `scheduler` module provides task scheduling with cron, interval, and one-time triggers. Jobs execute in a thread pool, support max-run limits, and expose full lifecycle status tracking via `JobStatus`.

## Core API

### Enums

```python
from codomyrmex.scheduler import JobStatus, TriggerType

JobStatus.PENDING     # Waiting to execute
JobStatus.RUNNING     # Currently executing
JobStatus.COMPLETED   # Finished successfully
JobStatus.FAILED      # Execution raised an exception
JobStatus.CANCELLED   # Cancelled by user

TriggerType.ONCE      # Fire once at a specific time
TriggerType.INTERVAL  # Fire at regular intervals
TriggerType.CRON      # Fire on a cron schedule
```

### Triggers

All triggers extend `Trigger(ABC)` and implement `get_next_run(from_time) -> datetime | None`.

```python
from codomyrmex.scheduler import OnceTrigger, IntervalTrigger, CronTrigger
from datetime import datetime, timedelta

# One-time: run at a specific datetime
trigger = OnceTrigger(run_at=datetime.now() + timedelta(hours=1))

# Interval: every 30 minutes, optional start/end bounds
trigger = IntervalTrigger(minutes=30, start_time=datetime(...), end_time=datetime(...))
trigger.interval_seconds  # -> 1800

# Cron: standard 5-field expression (minute hour dom month dow)
trigger = CronTrigger.from_expression("0 */2 * * *")  # every 2 hours
trigger = CronTrigger(minute="30", hour="9", day_of_week="1-5")  # 9:30 weekdays
```

### Job (dataclass)

| Field | Type | Description |
|:------|:-----|:------------|
| `id` | `str` | Unique job identifier |
| `name` | `str` | Human-readable name |
| `func` | `Callable` | Function to execute |
| `args` | `tuple` | Positional arguments |
| `kwargs` | `dict` | Keyword arguments |
| `trigger` | `Trigger` | Schedule trigger |
| `status` | `JobStatus` | Current lifecycle status |
| `created_at` | `datetime` | Creation timestamp |
| `last_run` | `datetime \| None` | Last execution time |
| `next_run` | `datetime \| None` | Next scheduled execution |
| `run_count` | `int` | Total successful executions |
| `max_runs` | `int \| None` | Maximum executions (None = unlimited) |
| `result` | `Any` | Last return value |
| `error` | `str \| None` | Last error message |

### Scheduler

```python
from codomyrmex.scheduler import Scheduler, IntervalTrigger

scheduler = Scheduler(max_workers=4)

# Schedule a job
job_id = scheduler.schedule(
    func=my_task,
    name="cleanup",
    trigger=IntervalTrigger(hours=1),
    args=("/tmp",),
    max_runs=24,
)

# Lifecycle
scheduler.start()                           # Start background thread
scheduler.stop()                            # Stop scheduler and thread pool

# Management
scheduler.cancel(job_id) -> bool            # Cancel by ID
scheduler.get_job(job_id) -> Job | None     # Get job details
scheduler.list_jobs(status=JobStatus.PENDING) -> list[Job]
scheduler.run_now(job_id) -> Any            # Execute immediately
```

### Convenience Functions

```python
from codomyrmex.scheduler import every, at, cron

trigger = every(minutes=30)                 # IntervalTrigger
trigger = at("09:30")                       # OnceTrigger (today or tomorrow)
trigger = cron("0 */2 * * *")               # CronTrigger from expression
```

## Error Handling

| Exception | Raised When |
|:----------|:------------|
| `ValueError` | Invalid cron expression (not 5 fields), unknown job ID in `run_now()` |
| Job-level errors | Captured in `job.error`; job status set to `FAILED` |

## Thread Safety

The `Scheduler` uses `threading.Lock` for job queue access and `ThreadPoolExecutor` for concurrent job execution. Safe for multi-threaded environments.

## Integration Points

- `logging_monitoring` -- Job execution events logged
- `notification` -- Can trigger alerts on job failure
- `metrics` -- Run count and timing available for dashboards

## Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
