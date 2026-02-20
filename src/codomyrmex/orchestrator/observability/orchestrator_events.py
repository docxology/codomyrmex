"""Typed orchestrator events for EventBus integration.

Factory functions that produce ``Event`` instances for workflow and task
lifecycle transitions.  Subscribe via:

    from codomyrmex.events import subscribe_to_events, EventType
    subscribe_to_events([EventType.WORKFLOW_STARTED], my_handler)
"""

from __future__ import annotations

from typing import Any

from codomyrmex.events.core.event_schema import Event, EventType


def workflow_started(workflow_name: str, total_tasks: int) -> Event:
    """Create a WORKFLOW_STARTED event."""
    return Event(
        event_type=EventType.WORKFLOW_STARTED,
        source=f"orchestrator.{workflow_name}",
        data={"workflow_name": workflow_name, "total_tasks": total_tasks},
    )


def workflow_completed(
    workflow_name: str,
    *,
    completed: int,
    failed: int,
    skipped: int,
    elapsed: float,
) -> Event:
    """Create a WORKFLOW_COMPLETED event."""
    return Event(
        event_type=EventType.WORKFLOW_COMPLETED,
        source=f"orchestrator.{workflow_name}",
        data={
            "workflow_name": workflow_name,
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "elapsed": elapsed,
            "success": failed == 0,
        },
    )


def workflow_failed(workflow_name: str, error: str) -> Event:
    """Create a WORKFLOW_FAILED event."""
    return Event(
        event_type=EventType.WORKFLOW_FAILED,
        source=f"orchestrator.{workflow_name}",
        data={"workflow_name": workflow_name, "error_message": error},
        priority=2,
    )


def task_started(workflow_name: str, task_name: str) -> Event:
    """Create a TASK_STARTED event."""
    return Event(
        event_type=EventType.TASK_STARTED,
        source=f"orchestrator.{workflow_name}",
        data={"workflow_name": workflow_name, "task_name": task_name},
    )


def task_completed(
    workflow_name: str,
    task_name: str,
    *,
    execution_time: float,
    attempts: int,
) -> Event:
    """Create a TASK_COMPLETED event."""
    return Event(
        event_type=EventType.TASK_COMPLETED,
        source=f"orchestrator.{workflow_name}",
        data={
            "workflow_name": workflow_name,
            "task_name": task_name,
            "execution_time": execution_time,
            "attempts": attempts,
        },
    )


def task_failed(workflow_name: str, task_name: str, error: str) -> Event:
    """Create a TASK_FAILED event."""
    return Event(
        event_type=EventType.TASK_FAILED,
        source=f"orchestrator.{workflow_name}",
        data={
            "workflow_name": workflow_name,
            "task_name": task_name,
            "error_message": error,
        },
        priority=2,
    )


def task_retrying(
    workflow_name: str, task_name: str, *, attempt: int, delay: float, error: str
) -> Event:
    """Create a TASK_RETRYING event."""
    return Event(
        event_type=EventType.TASK_RETRYING,
        source=f"orchestrator.{workflow_name}",
        data={
            "workflow_name": workflow_name,
            "task_name": task_name,
            "attempt": attempt,
            "delay": delay,
            "error_message": error,
        },
    )
