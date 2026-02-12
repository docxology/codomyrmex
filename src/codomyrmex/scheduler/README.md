# Scheduler Module

**Version**: v0.1.0 | **Status**: Active

Task scheduling with cron, interval, and one-time triggers.

## Installation

```bash
uv uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes

- **`JobStatus`** — Status of a scheduled job.
- **`TriggerType`** — Types of job triggers.
- **`Trigger`** — Base class for job triggers.
- **`OnceTrigger`** — Trigger that fires once at a specific time.
- **`IntervalTrigger`** — Trigger that fires at regular intervals.
- **`CronTrigger`** — Cron-style trigger (simplified).
- **`Job`** — A scheduled job.
- **`Scheduler`** — Task scheduler with support for various trigger types.

### Functions

- **`every()`** — Create an interval trigger.
- **`at()`** — Create a one-time trigger from time string (HH:MM).
- **`cron()`** — Create a cron trigger from expression.

## Quick Start

```python
from codomyrmex.scheduler import (
    Scheduler, IntervalTrigger, CronTrigger, every, at, cron
)
from datetime import timedelta

scheduler = Scheduler()

# Interval job: every 5 minutes
def cleanup():
    print("Running cleanup...")

scheduler.schedule(
    func=cleanup,
    trigger=IntervalTrigger(minutes=5),
)

# Cron job: every day at midnight
scheduler.schedule(
    func=backup_database,
    trigger=cron("0 0 * * *"),  # minute hour day month weekday
)

# One-time job: tomorrow at 9 AM
scheduler.schedule(
    func=send_reminder,
    trigger=at("09:00"),
)

# Start scheduler
scheduler.start()

# List and manage jobs
for job in scheduler.list_jobs():
    print(f"{job.name}: next run at {job.next_run}")

scheduler.cancel(job_id)
scheduler.run_now(job_id)  # Execute immediately
```

## Convenience Functions

```python
every(seconds=30)        # IntervalTrigger
every(hours=1)           # IntervalTrigger
at("14:30")              # OnceTrigger at 2:30 PM today (or tomorrow)
cron("*/5 * * * *")      # CronTrigger: every 5 minutes
cron("0 9 * * 1-5")      # CronTrigger: 9 AM weekdays
```

## Directory Structure

- `models.py` — Data models (`Job`, `JobStatus`, `TriggerType`)
- `triggers.py` — Trigger implementations (`CronTrigger`, `IntervalTrigger`)
- `scheduler.py` — Core scheduler logic
- `__init__.py` — Public API re-exports

## Exports

| Class | Description |
| :--- | :--- |
| `Scheduler` | Main scheduler with start/stop control |
| `Job` | Scheduled job with status, run history |
| `JobStatus` | Enum: pending, running, completed, failed, cancelled |
| `IntervalTrigger` | Recurring at fixed intervals |
| `CronTrigger` | Cron expression scheduling |
| `OnceTrigger` | Single execution at specific time |
| `every(...)` | Create interval trigger |
| `at("HH:MM")` | Create one-time trigger |
| `cron("...")` | Parse cron expression |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k scheduler -v
```

## Documentation

- [Module Documentation](../../../docs/modules/scheduler/README.md)
- [Agent Guide](../../../docs/modules/scheduler/AGENTS.md)
- [Specification](../../../docs/modules/scheduler/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
