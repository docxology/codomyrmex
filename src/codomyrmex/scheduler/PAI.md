# Personal AI Infrastructure — Scheduler Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Scheduler module provides PAI integration for task scheduling and cron jobs.

## PAI Capabilities

### Task Scheduling

Schedule recurring tasks:

```python
from codomyrmex.scheduler import Scheduler

scheduler = Scheduler()

@scheduler.every(minutes=30)
async def refresh_data():
    await sync_data()

scheduler.start()
```

### Cron Jobs

Use cron expressions:

```python
from codomyrmex.scheduler import CronJob

job = CronJob("0 0 * * *", cleanup_function)
job.start()  # Runs at midnight daily
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Scheduler` | Schedule tasks |
| `CronJob` | Cron expressions |
| `TaskQueue` | Async task queue |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
