# Agent Guidelines - Scheduler

## Module Context

The `scheduler` module provides task scheduling for automated pipelines, maintenance jobs, and recurring agent tasks.

## Key Classes

- `Scheduler` - Central job coordinator
- `Job` - Individual task with status tracking
- `*Trigger` - Timing specifications

## Integration Points

- **ci_cd_automation**: Schedule build/deploy jobs
- **cache**: Schedule cache cleanup
- **logging_monitoring**: Schedule log rotation
- **agents**: Schedule autonomous agent tasks

## Best Practices

1. **Use appropriate triggers**: `IntervalTrigger` for simple recurring, `CronTrigger` for complex schedules
2. **Set max_runs** for jobs that should only run a limited number of times
3. **Handle errors** in job functions - failures are recorded but don't stop the scheduler
4. **Daemon mode** - scheduler runs in background thread
