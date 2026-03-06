"""Workflow and task models."""

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TaskState(Enum):
    """States a task can be in."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class TaskDefinition:
    """Definition of a task in a workflow."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    action: Callable | None = None
    dependencies: list[str] = field(default_factory=list)
    timeout: float | None = None
    retries: int = 0
    retry_delay: float = 1.0
    condition: Callable[[dict], bool] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Result of task execution."""

    task_id: str
    state: TaskState
    output: Any = None
    error: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    attempts: int = 0

    @property
    def duration_ms(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0


@dataclass
class WorkflowDefinition:
    """Definition of a workflow."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    tasks: list[TaskDefinition] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_task(
        self,
        name: str,
        action: Callable,
        dependencies: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        task = TaskDefinition(name=name, action=action, dependencies=dependencies or [], **kwargs)
        self.tasks.append(task)
        return task.id

    def get_task(self, task_id: str) -> TaskDefinition | None:
        for task in self.tasks:
            if task_id in (task.id, task.name):
                return task
        return None

    def get_execution_order(self) -> list[list[TaskDefinition]]:
        """Return tasks in topological order as parallelizable batches."""
        task_map = {t.id: t for t in self.tasks}
        task_map.update({t.name: t for t in self.tasks})
        in_degree = {t.id: 0 for t in self.tasks}
        dependents: dict[str, list[str]] = {t.id: [] for t in self.tasks}
        for task in self.tasks:
            for dep_id in task.dependencies:
                dep = task_map.get(dep_id)
                if dep:
                    in_degree[task.id] += 1
                    dependents[dep.id].append(task.id)
        levels: list[list[TaskDefinition]] = []
        current_level = [t for t in self.tasks if in_degree[t.id] == 0]
        while current_level:
            levels.append(current_level)
            next_level: list[TaskDefinition] = []
            for task in current_level:
                for dep_id in dependents[task.id]:
                    in_degree[dep_id] -= 1
                    if in_degree[dep_id] == 0:
                        dep_task = task_map[dep_id]
                        if dep_task not in next_level:
                            next_level.append(dep_task)
            current_level = next_level
        return levels


@dataclass
class WorkflowResult:
    """Result of workflow execution."""

    workflow_id: str
    success: bool
    task_results: dict[str, TaskResult] = field(default_factory=dict)
    start_time: datetime | None = None
    end_time: datetime | None = None
    error: str | None = None

    @property
    def duration_ms(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0

    def get_task_result(self, task_id: str) -> TaskResult | None:
        return self.task_results.get(task_id)
