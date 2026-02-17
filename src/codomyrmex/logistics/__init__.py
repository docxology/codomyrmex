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

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

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


def cli_commands():
    """Return CLI commands for the logistics module."""
    def _list_routes():
        """List logistics routes."""
        print("Logistics Module - Routing:")
        print("  orchestration - Workflow and project orchestration")
        print("  task          - Task queue management and job execution")
        print("  schedule      - Advanced scheduling (cron, recurring, timezone)")
        print("  routing       - Task routing algorithms")
        print("  optimization  - Schedule optimization")
        print("  resources     - Resource allocation")
        print("  tracking      - Progress and status tracking")

    def _logistics_status():
        """Show logistics status."""
        print(f"Logistics module v{__version__}")
        print("Components:")
        print(f"  WorkflowManager: available")
        print(f"  TaskOrchestrator: available")
        print(f"  ProjectManager: available")
        print(f"  ScheduleManager: available")
        print(f"  CronScheduler: available")
        print(f"  JobScheduler: available")

    return {
        "routes": _list_routes,
        "status": _logistics_status,
    }


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
    "cli_commands",
]
