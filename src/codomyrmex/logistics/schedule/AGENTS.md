# Codomyrmex Agents — src/codomyrmex/logistics/schedule

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides advanced scheduling capabilities including cron-like patterns, recurring schedules, and timezone-aware scheduling. This module enables precise control over when tasks and workflows execute.

## Active Components

- `scheduler.py` - Central schedule management and coordination
- `cron.py` - Cron expression parsing and scheduling
- `recurring.py` - Recurring schedule definitions and management
- `timezone.py` - Timezone-aware scheduling utilities
- `__init__.py` - Module exports
- `SPEC.md` - Module specification
- `README.md` - Module documentation

## Key Classes and Functions

### scheduler.py
- **`ScheduleManager`** - Central manager for all scheduling operations
  - Coordinates between cron, recurring, and timezone schedulers
  - Manages schedule registration and cancellation
  - Provides unified interface for schedule queries

### cron.py
- **`CronScheduler`** - Executes tasks based on cron expressions
- **`CronExpression`** - Parses and validates cron expressions
  - Supports standard 5-field cron syntax (minute, hour, day, month, weekday)
  - Supports special characters: *, /, -, ,
  - `next_run()` - Calculates next execution time
  - `matches(datetime)` - Checks if datetime matches expression

### recurring.py
- **`RecurringScheduler`** - Manages recurring task schedules
- **`RecurringSchedule`** - Defines recurring schedule patterns
  - Supports intervals: MINUTELY, HOURLY, DAILY, WEEKLY, MONTHLY
  - Configurable start time, end time, and repetition count
  - Skip conditions for holidays or specific dates

### timezone.py
- **`TimezoneManager`** - Handles timezone conversions and awareness
  - Converts schedules between timezones
  - Handles DST transitions correctly
  - Provides current time in any timezone
  - Validates timezone identifiers

## Operating Contracts

- All times stored internally as UTC
- Timezone conversions applied at schedule creation and display
- Cron expressions validated on creation (raises ValueError for invalid)
- Recurring schedules respect end time and max repetition limits
- DST transitions handled by advancing/retarding schedules appropriately

## Signposting

- **Dependencies**: Standard library `datetime`, `zoneinfo` for timezone support
- **Parent Directory**: [logistics](../README.md) - Parent module documentation
- **Related Modules**:
  - `orchestration/` - Uses schedules for workflow execution
  - `task/` - Job scheduler integration
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
