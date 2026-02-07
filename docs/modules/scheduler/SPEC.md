# Scheduler — Functional Specification

**Module**: `codomyrmex.scheduler`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Task scheduling and job queuing with support for cron and interval triggers.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `JobStatus` | Class | Status of a scheduled job. |
| `TriggerType` | Class | Types of job triggers. |
| `Trigger` | Class | Base class for job triggers. |
| `OnceTrigger` | Class | Trigger that fires once at a specific time. |
| `IntervalTrigger` | Class | Trigger that fires at regular intervals. |
| `CronTrigger` | Class | Cron-style trigger (simplified). |
| `Job` | Class | A scheduled job. |
| `Scheduler` | Class | Task scheduler with support for various trigger types. |
| `every()` | Function | Create an interval trigger. |
| `at()` | Function | Create a one-time trigger from time string (HH:MM). |
| `cron()` | Function | Create a cron trigger from expression. |
| `get_next_run()` | Function | Get the next run time. |
| `get_type()` | Function | Get trigger type. |

### Source Files

- `advanced.py`

## 3. Dependencies

See `src/codomyrmex/scheduler/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.scheduler import JobStatus, TriggerType, Trigger, OnceTrigger, IntervalTrigger
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k scheduler -v
```
