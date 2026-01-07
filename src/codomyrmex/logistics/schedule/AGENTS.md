# Codomyrmex Agents — src/codomyrmex/logistics/schedule

## Signposting
- **Parent**: [logistics](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Schedule submodule providing advanced scheduling capabilities including cron-like patterns, recurring schedules, and timezone-aware scheduling.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module initialization
- `scheduler.py` – Main scheduler interface
- `cron.py` – Cron-like scheduling with pattern parsing
- `recurring.py` – Recurring schedule definitions
- `timezone.py` – Timezone-aware scheduling

## Key Classes and Functions

### ScheduleManager (`scheduler.py`)
- `ScheduleManager(timezone: Optional[str] = None)` – Initialize schedule manager
- `schedule_cron(task_id: str, cron_expression: str, callback: Callable, *args, **kwargs) -> str` – Schedule a task using cron expression
- `schedule_recurring(task_id: str, schedule: RecurringSchedule, callback: Callable, *args, **kwargs) -> str` – Schedule a recurring task
- `cancel(task_id: str) -> bool` – Cancel a scheduled task
- `start(check_interval: int = 60) -> None` – Start the scheduler
- `stop() -> None` – Stop the scheduler
- `list_tasks() -> List[str]` – List all scheduled task IDs

### CronScheduler (`cron.py`)
- `CronExpression` (dataclass) – Cron expression parser and evaluator
  - `parse(expression: str) -> CronExpression` – Parse a cron expression
  - `matches(dt: datetime) -> bool` – Check if a datetime matches this cron expression
- `CronScheduler(timezone_manager: TimezoneManager)` – Cron scheduler for evaluating cron expressions
  - `should_run(cron: CronExpression, now: Optional[datetime] = None) -> bool` – Check if a cron expression should run now

### RecurringScheduler (`recurring.py`)
- `RecurrenceType` (Enum) – Recurrence type enumeration (DAILY, WEEKLY, MONTHLY, YEARLY)
- `RecurringSchedule` (dataclass) – Recurring schedule definition
- `RecurringScheduler(timezone_manager: TimezoneManager)` – Recurring scheduler for evaluating recurring schedules
  - `should_run(schedule: RecurringSchedule, now: Optional[datetime] = None) -> bool` – Check if a recurring schedule should run now

### TimezoneManager (`timezone.py`)
- `TimezoneManager(timezone: Optional[str] = None)` – Initialize timezone manager
- `now() -> datetime` – Get current datetime in configured timezone
- `to_timezone(dt: datetime, timezone: str) -> datetime` – Convert datetime to specified timezone
- `localize(dt: datetime) -> datetime` – Localize a naive datetime to configured timezone

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [logistics](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation

