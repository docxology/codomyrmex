# schedule

## Signposting
- **Parent**: [logistics](../README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Schedule submodule providing advanced scheduling capabilities including cron-like patterns, recurring schedules, and timezone-aware scheduling.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `scheduler.py` – Main scheduler interface
- `cron.py` – Cron-like scheduling with pattern parsing
- `recurring.py` – Recurring schedule definitions
- `timezone.py` – Timezone-aware scheduling

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [logistics](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.logistics.schedule import ScheduleManager, CronScheduler, RecurringSchedule, RecurrenceType
from datetime import time

# Create scheduler
scheduler = ScheduleManager(timezone="America/New_York")

# Schedule with cron expression
scheduler.schedule_cron("daily_backup", "0 2 * * *", backup_function)

# Schedule recurring task
from datetime import time
schedule = RecurringSchedule(
    recurrence_type=RecurrenceType.DAILY,
    time=time(2, 0)  # 2 AM
)
scheduler.schedule_recurring("daily_task", schedule, my_function)

# Start scheduler
scheduler.start()
```

