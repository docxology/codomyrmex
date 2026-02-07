# Scheduler Module — Agent Coordination

## Purpose

Task scheduling and job queuing with support for cron and interval triggers.

## Key Capabilities

- **JobStatus**: Status of a scheduled job.
- **TriggerType**: Types of job triggers.
- **Trigger**: Base class for job triggers.
- **OnceTrigger**: Trigger that fires once at a specific time.
- **IntervalTrigger**: Trigger that fires at regular intervals.
- `every()`: Create an interval trigger.
- `at()`: Create a one-time trigger from time string (HH:MM).
- `cron()`: Create a cron trigger from expression.

## Agent Usage Patterns

```python
from codomyrmex.scheduler import JobStatus

# Agent initializes scheduler
instance = JobStatus()
```

## Integration Points

- **Source**: [src/codomyrmex/scheduler/](../../../src/codomyrmex/scheduler/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k scheduler -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
