# Scheduler Module

Task scheduling and job queuing with cron and interval triggers.

## Features

- **Multiple Trigger Types**: One-time, interval, and cron-style scheduling
- **Concurrent Execution**: Thread pool for parallel job execution
- **Job Management**: Cancel, reschedule, and monitor jobs
- **Convenience Functions**: `every()`, `at()`, `cron()` helpers

## Quick Start

```python
from codomyrmex.scheduler import Scheduler, every, cron

scheduler = Scheduler()

# Run every 5 minutes
scheduler.schedule(
    func=cleanup_temp_files,
    trigger=every(minutes=5),
)

# Run at specific cron schedule (every day at 3am)
scheduler.schedule(
    func=backup_database,
    trigger=cron("0 3 * * *"),
)

# Start scheduler
scheduler.start()
```

## Navigation

- [Technical Spec](SPEC.md)
- [Agent Guidelines](AGENTS.md)
- [PAI Context](PAI.md)
