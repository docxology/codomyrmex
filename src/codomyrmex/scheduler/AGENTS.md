# Agent Guidelines - Scheduler

## Module Overview

Task scheduling for automated pipelines, maintenance, and recurring jobs.

## Key Classes

- **Scheduler** — Central job coordinator
- **Job** — Task with status and execution history
- **OnceTrigger** — Run once at specific time
- **IntervalTrigger** — Recurring at fixed intervals
- **CronTrigger** — Cron expression scheduling

## Agent Instructions

1. **Use appropriate trigger** — Interval for simple, Cron for complex
2. **Set max_runs** — Limit for jobs that shouldn't run forever
3. **Handle errors** — Failures are recorded but don't stop scheduler
4. **Use daemon mode** — Scheduler runs in background thread
5. **Name jobs descriptively** — For debugging and monitoring

## Common Patterns

```python
from codomyrmex.scheduler import Scheduler, every, cron, at

scheduler = Scheduler()

# Recurring job every 5 minutes
@scheduler.every(minutes=5)
def cleanup_cache():
    cache.cleanup_expired()

# Cron-based job (daily at 2 AM)
@scheduler.cron("0 2 * * *")
def daily_backup():
    backup.run()

# One-time job
@scheduler.at("2026-12-01T00:00:00")
def new_year_notification():
    send_notification("Happy New Year!")

# Start scheduler
scheduler.start()  # Runs in background thread
```

## Testing Patterns

```python
# Verify job scheduling
scheduler = Scheduler()
executed = []

@scheduler.every(seconds=1)
def test_job():
    executed.append(True)

scheduler.start()
time.sleep(2.5)
scheduler.stop()
assert len(executed) >= 2
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
