"""
Scheduler Module

Task scheduling and job queuing with support for cron and interval triggers.
"""

__version__ = "0.1.0"

from .models import Job, JobStatus
from .triggers import CronTrigger, IntervalTrigger, OnceTrigger, Trigger, TriggerType
from .scheduler import Scheduler, at, cron, every

# Advanced scheduler extensions
try:
    from .advanced import DependencyScheduler, JobPipeline, PersistentScheduler, ScheduledRecurrence
except ImportError:
    pass

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
]
