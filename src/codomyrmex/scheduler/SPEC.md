# Technical Specification - Scheduler

**Module**: `codomyrmex.scheduler`  
**Version**: v0.1.0  
**Last Updated**: February 2026

## 1. Purpose

Task scheduling and job queuing with support for one-time, interval, and cron-style triggers.

## 2. Architecture

```
scheduler/
├── __init__.py          # Core implementation
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
└── PAI.md               # Personal AI context
```

## 3. Public API

```python
from codomyrmex.scheduler import (
    Scheduler,        # Main scheduler
    Job,              # Job definition
    JobStatus,        # Job status enum
    OnceTrigger,      # One-time trigger
    IntervalTrigger,  # Recurring interval
    CronTrigger,      # Cron-style scheduling
    every,            # Interval helper
    at,               # Time-based helper
    cron,             # Cron expression helper
)
```

## 4. Trigger Types

| Trigger | Use Case |
|---------|----------|
| `OnceTrigger` | Run once at specific time |
| `IntervalTrigger` | Run every N seconds/minutes/hours |
| `CronTrigger` | Complex schedules (cron expression) |

## 5. Testing

```bash
pytest tests/unit/test_scheduler.py -v
```

## Dependencies

See `src/codomyrmex/scheduler/__init__.py` for import dependencies.
