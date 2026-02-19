# Schedule

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Advanced scheduling capabilities for logistics operations. Provides cron-like pattern parsing, recurring schedule definitions, timezone-aware scheduling, and a unified schedule manager.

## Key Exports

- **`ScheduleManager`** -- Unified manager for creating and coordinating schedules
- **`CronScheduler`** -- Scheduler that executes tasks based on cron expression timing
- **`CronExpression`** -- Parser and evaluator for cron-style schedule expressions
- **`RecurringScheduler`** -- Scheduler for recurring task patterns
- **`RecurringSchedule`** -- Definition of a recurring schedule with interval and frequency
- **`TimezoneManager`** -- Timezone-aware scheduling utilities

## Directory Contents

- `__init__.py` - Package exports and version declaration
- `cron.py` - Cron expression parsing and cron-based scheduling
- `recurring.py` - Recurring schedule definitions and scheduler
- `scheduler.py` - Unified ScheduleManager implementation
- `timezone.py` - Timezone management utilities
- `py.typed` - PEP 561 type stub marker

## Navigation

- **Parent Module**: [logistics](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
