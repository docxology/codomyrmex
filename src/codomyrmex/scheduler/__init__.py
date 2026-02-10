"""
Scheduler Module

Task scheduling and job queuing with support for cron and interval triggers.
"""

__version__ = "0.1.0"

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .models import Job, JobStatus
from .triggers import CronTrigger, IntervalTrigger, OnceTrigger, Trigger, TriggerType
from .scheduler import Scheduler, at, cron, every

# Advanced scheduler extensions
try:
    from .advanced import DependencyScheduler, JobPipeline, PersistentScheduler, ScheduledRecurrence
except ImportError:
    pass

def cli_commands():
    """Return CLI commands for the scheduler module."""
    def _list_jobs():
        """List scheduled jobs."""
        try:
            scheduler = Scheduler()
            jobs = scheduler.get_jobs() if hasattr(scheduler, 'get_jobs') else []
            if jobs:
                for job in jobs:
                    print(f"  {job}")
            else:
                print("No scheduled jobs.")
        except Exception:
            print("Scheduler: no active jobs (scheduler not running)")

    def _scheduler_status():
        """Show scheduler status."""
        print(f"Scheduler module v{__version__}")
        print(f"Trigger types: cron, interval, once")
        print(f"Job statuses: {', '.join(s.value for s in JobStatus)}")

    return {
        "jobs": _list_jobs,
        "status": _scheduler_status,
    }


__all__ = [
    # Core classes
    "Scheduler",
    "Job",
    "JobStatus",
    # Triggers
    "Trigger",
    "TriggerType",
    "OnceTrigger",
    "IntervalTrigger",
    "CronTrigger",
    # Convenience functions
    "every",
    "at",
    "cron",
    # Advanced
    "DependencyScheduler",
    "PersistentScheduler",
    "JobPipeline",
    "ScheduledRecurrence",
    "cli_commands",
]
