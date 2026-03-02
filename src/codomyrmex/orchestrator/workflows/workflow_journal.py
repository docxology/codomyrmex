"""Workflow execution journaling.

Observer that records workflow lifecycle events (start, step
completion, workflow completion) into LearningJournal for
pattern analysis and audit trails.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.agents.memory.store import MemoryStore
from codomyrmex.orchestrator.workflows.workflow_engine import (
    WorkflowResult,
    WorkflowRunner,
    WorkflowStep,
)


@dataclass
class JournalEntry:
    """A single journal entry from workflow execution.

    Attributes:
        workflow_id: Associated workflow ID.
        event_type: Type of event (start, step, complete).
        step_name: Step name (for step events).
        status: Step or workflow status.
        timestamp: When the event occurred.
        duration_ms: Duration of the step/workflow.
        details: Additional event data.
    """

    workflow_id: str
    event_type: str  # "start", "step", "complete"
    step_name: str = ""
    status: str = ""
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


class WorkflowJournal:
    """Records workflow execution events for audit and analysis.

    Subscribes to WorkflowRunner lifecycle and writes structured
    JournalEntry records to an internal store. Compatible with
    MemoryStore for persistent storage.

    Example::

        journal = WorkflowJournal()
        runner = WorkflowRunner()
        runner.add_step(WorkflowStep("build", action=build_fn))
        result = runner.run()

        # Record after execution
        journal.on_workflow_start(runner, result.workflow_id)
        for step in result.steps:
            journal.on_step_complete(result.workflow_id, step)
        journal.on_workflow_complete(result)
    """

    def __init__(self, memory: MemoryStore | None = None) -> None:
        """Initialize this instance."""
        self._entries: list[JournalEntry] = []
        self._memory = memory

    @property
    def entry_count(self) -> int:
        """Total number of journal entries."""
        return len(self._entries)

    def on_workflow_start(self, runner: WorkflowRunner, workflow_id: str) -> None:
        """Record a workflow start event.

        Args:
            runner: The workflow runner instance.
            workflow_id: Unique workflow identifier.
        """
        entry = JournalEntry(
            workflow_id=workflow_id,
            event_type="start",
            details={
                "step_count": runner.step_count,
                "step_names": runner.step_names(),
            },
        )
        self._entries.append(entry)
        self._persist(entry)

    def on_step_complete(self, workflow_id: str, step: WorkflowStep) -> None:
        """Record a step completion event.

        Args:
            workflow_id: Workflow this step belongs to.
            step: The completed workflow step.
        """
        entry = JournalEntry(
            workflow_id=workflow_id,
            event_type="step",
            step_name=step.name,
            status=step.status.value,
            duration_ms=step.duration_ms,
            details={
                "error": step.error,
                "depends_on": step.depends_on,
            },
        )
        self._entries.append(entry)
        self._persist(entry)

    def on_workflow_complete(self, result: WorkflowResult) -> None:
        """Record a workflow completion event.

        Args:
            result: The workflow execution result.
        """
        entry = JournalEntry(
            workflow_id=result.workflow_id,
            event_type="complete",
            status="success" if result.success else "failed",
            duration_ms=result.total_duration_ms,
            details={
                "completed": result.completed_count,
                "failed": result.failed_count,
                "total_steps": len(result.steps),
            },
        )
        self._entries.append(entry)
        self._persist(entry)

    def by_workflow_id(self, workflow_id: str) -> list[JournalEntry]:
        """Get all entries for a specific workflow."""
        return [e for e in self._entries if e.workflow_id == workflow_id]

    def by_event_type(self, event_type: str) -> list[JournalEntry]:
        """Get all entries of a specific event type."""
        return [e for e in self._entries if e.event_type == event_type]

    def recent(self, n: int = 20) -> list[JournalEntry]:
        """Return the most recent n entries."""
        return list(self._entries[-n:])

    def record_full_workflow(self, runner: WorkflowRunner, result: WorkflowResult) -> None:
        """Convenience: record all events for a completed workflow.

        Args:
            runner: The runner that executed the workflow.
            result: The execution result.
        """
        self.on_workflow_start(runner, result.workflow_id)
        for step in result.steps:
            self.on_step_complete(result.workflow_id, step)
        self.on_workflow_complete(result)

    def _persist(self, entry: JournalEntry) -> None:
        """Optionally persist an entry to MemoryStore."""
        if self._memory is not None:
            key = f"journal:{entry.workflow_id}:{entry.event_type}:{entry.step_name or 'wf'}"
            self._memory.put(
                key=key,
                value={
                    "workflow_id": entry.workflow_id,
                    "event_type": entry.event_type,
                    "step_name": entry.step_name,
                    "status": entry.status,
                    "duration_ms": entry.duration_ms,
                },
                tags=["journal", entry.event_type, entry.workflow_id],
            )

    def clear(self) -> None:
        """Clear all journal entries."""
        self._entries.clear()


__all__ = ["JournalEntry", "WorkflowJournal"]
