"""
Logistics Module for Codomyrmex

This module provides logistics capabilities including orchestration, task management,
and scheduling for coordinating workflows, jobs, and time-based execution.

Submodules:
- orchestration: Workflow and project orchestration
- task: Task queue management and job execution
- schedule: Advanced scheduling with cron, recurring, and timezone support
- routing: Task routing algorithms
- optimization: Schedule optimization
- resources: Resource allocation
- tracking: Progress and status tracking
"""

# New submodule exports
from . import optimization, resources, routing, tracking
from .orchestration import (
    OrchestrationEngine,
    OrchestrationSession,
    ProjectManager,
    ResourceManager,
    TaskOrchestrator,
    WorkflowManager,
)
from .schedule import (
    CronExpression,
    CronScheduler,
    RecurringSchedule,
    RecurringScheduler,
    ScheduleManager,
    TimezoneManager,
)
from .task import Job, JobScheduler, Queue

__version__ = "0.1.0"

__all__ = [
    # Orchestration
    "WorkflowManager",
    "TaskOrchestrator",
    "ProjectManager",
    "ResourceManager",
    "OrchestrationEngine",
    "OrchestrationSession",
    # Task
    "Queue",
    "Job",
    "JobScheduler",
    # Schedule
    "ScheduleManager",
    "CronScheduler",
    "CronExpression",
    "RecurringScheduler",
    "RecurringSchedule",
    "TimezoneManager",
    # Submodules
    "routing",
    "optimization",
    "resources",
    "tracking",
]
