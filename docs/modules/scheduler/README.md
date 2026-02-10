# Scheduler Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Task scheduling and job queuing with support for cron and interval triggers.

## Key Features

- **JobStatus** — Status of a scheduled job.
- **TriggerType** — Types of job triggers.
- **Trigger** — Base class for job triggers.
- **OnceTrigger** — Trigger that fires once at a specific time.
- **IntervalTrigger** — Trigger that fires at regular intervals.
- **CronTrigger** — Cron-style trigger (simplified).
- `every()` — Create an interval trigger.
- `at()` — Create a one-time trigger from time string (HH:MM).
- `cron()` — Create a cron trigger from expression.
- `get_next_run()` — Get the next run time.

## Quick Start

```python
from codomyrmex.scheduler import JobStatus, TriggerType, Trigger

# Initialize
instance = JobStatus()
```


## Installation

```bash
uv pip install codomyrmex
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `JobStatus` | Status of a scheduled job. |
| `TriggerType` | Types of job triggers. |
| `Trigger` | Base class for job triggers. |
| `OnceTrigger` | Trigger that fires once at a specific time. |
| `IntervalTrigger` | Trigger that fires at regular intervals. |
| `CronTrigger` | Cron-style trigger (simplified). |
| `Job` | A scheduled job. |
| `Scheduler` | Task scheduler with support for various trigger types. |

### Functions

| Function | Description |
|----------|-------------|
| `every()` | Create an interval trigger. |
| `at()` | Create a one-time trigger from time string (HH:MM). |
| `cron()` | Create a cron trigger from expression. |
| `get_next_run()` | Get the next run time. |
| `get_type()` | Get trigger type. |
| `interval_seconds()` | interval seconds |
| `from_expression()` | Parse cron expression (minute hour day month weekday). |
| `execute()` | Execute the job. |
| `schedule()` | Schedule a job. |
| `cancel()` | Cancel a scheduled job. |
| `get_job()` | Get job by ID. |
| `list_jobs()` | List all jobs, optionally filtered by status. |
| `start()` | Start the scheduler. |
| `stop()` | Stop the scheduler. |
| `run_now()` | Execute a job immediately. |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k scheduler -v
```

## Navigation

- **Source**: [src/codomyrmex/scheduler/](../../../src/codomyrmex/scheduler/)
- **Parent**: [Modules](../README.md)
