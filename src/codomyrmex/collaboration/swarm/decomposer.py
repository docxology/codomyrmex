"""DAG-based task decomposition for complex missions.

Breaks high-level tasks into sub-tasks with dependency edges
and produces a topological execution order.
"""

from __future__ import annotations

import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.collaboration.swarm.protocol import AgentRole
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class SubTask:
    """A decomposed sub-task with dependencies.

    Attributes:
        task_id: Unique identifier.
        description: What this sub-task does.
        role: Recommended agent role.
        depends_on: IDs of prerequisite sub-tasks.
        priority: Task priority (lower = higher).
    """

    task_id: str = ""
    description: str = ""
    role: AgentRole = AgentRole.CODER
    depends_on: list[str] = field(default_factory=list)
    priority: int = 5

    def __post_init__(self) -> None:
        """post Init ."""
        if not self.task_id:
            self.task_id = str(uuid.uuid4())[:8]

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "role": self.role.value,
            "depends_on": self.depends_on,
            "priority": self.priority,
        }


class CyclicDependencyError(Exception):
    """Raised when sub-task dependencies form a cycle."""


class TaskDecomposer:
    """Decompose complex tasks into dependency-ordered sub-tasks.

    Usage::

        decomposer = TaskDecomposer()
        subtasks = decomposer.decompose(
            "Add user authentication with tests and docs"
        )
        order = decomposer.execution_order(subtasks)
    """

    # Keyword → (role, description_template, priority)
    _PHASE_MAP: list[tuple[set[str], AgentRole, str, int]] = [
        ({"design", "architect", "plan", "structure"},
         AgentRole.ARCHITECT, "Design architecture for: {task}", 1),
        ({"implement", "code", "build", "add", "create", "fix", "write"},
         AgentRole.CODER, "Implement: {task}", 3),
        ({"test", "verify", "validate", "check"},
         AgentRole.TESTER, "Write tests for: {task}", 4),
        ({"review", "inspect", "audit"},
         AgentRole.REVIEWER, "Review: {task}", 5),
        ({"document", "docs", "readme", "docstring"},
         AgentRole.DOCUMENTER, "Document: {task}", 6),
        ({"deploy", "ci", "cd", "pipeline", "release"},
         AgentRole.DEVOPS, "Deploy: {task}", 7),
    ]

    def decompose(self, task: str) -> list[SubTask]:
        """Decompose a task into role-based sub-tasks with dependencies.

        Uses keyword heuristics to determine which phases are needed.

        Args:
            task: High-level task description.

        Returns:
            List of ``SubTask`` objects with ``depends_on`` edges.
        """
        task_lower = task.lower()
        subtasks: list[SubTask] = []
        prev_id: str | None = None

        # Determine which phases this task requires
        matched_phases = []
        for keywords, role, template, priority in self._PHASE_MAP:
            if any(kw in task_lower for kw in keywords):
                matched_phases.append((keywords, role, template, priority))

        # If no specific phases matched, default to code → test → review
        if not matched_phases:
            matched_phases = [
                (set(), AgentRole.CODER, "Implement: {task}", 3),
                (set(), AgentRole.TESTER, "Test: {task}", 4),
                (set(), AgentRole.REVIEWER, "Review: {task}", 5),
            ]

        # Build sub-tasks with sequential dependencies
        for _, role, template, priority in matched_phases:
            st = SubTask(
                description=template.format(task=task),
                role=role,
                depends_on=[prev_id] if prev_id else [],
                priority=priority,
            )
            subtasks.append(st)
            prev_id = st.task_id

        logger.info(
            "Task decomposed",
            extra={"task": task[:50], "subtasks": len(subtasks)},
        )

        return subtasks

    @staticmethod
    def execution_order(subtasks: list[SubTask]) -> list[SubTask]:
        """Topologically sort sub-tasks by their dependency edges.

        Args:
            subtasks: List of sub-tasks with ``depends_on`` edges.

        Returns:
            Sub-tasks in valid execution order.

        Raises:
            CyclicDependencyError: If dependencies form a cycle.
        """
        task_map = {st.task_id: st for st in subtasks}
        in_degree: dict[str, int] = {st.task_id: 0 for st in subtasks}
        adj: dict[str, list[str]] = {st.task_id: [] for st in subtasks}

        for st in subtasks:
            for dep_id in st.depends_on:
                if dep_id in adj:
                    adj[dep_id].append(st.task_id)
                    in_degree[st.task_id] += 1

        # Kahn's algorithm
        queue: deque[str] = deque(
            tid for tid, deg in in_degree.items() if deg == 0
        )
        result: list[SubTask] = []

        while queue:
            tid = queue.popleft()
            result.append(task_map[tid])
            for neighbor in adj[tid]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(subtasks):
            raise CyclicDependencyError(
                f"Cycle detected: processed {len(result)}/{len(subtasks)}"
            )

        return result

    @staticmethod
    def leaf_tasks(subtasks: list[SubTask]) -> list[SubTask]:
        """Return sub-tasks with no dependents (terminal tasks)."""
        all_deps: set[str] = set()
        all_ids = {st.task_id for st in subtasks}
        for st in subtasks:
            all_deps.update(st.depends_on)
        # Leaves are tasks that no other task depends on
        leaf_ids = all_ids - all_deps
        return [st for st in subtasks if st.task_id in leaf_ids]


__all__ = [
    "CyclicDependencyError",
    "SubTask",
    "TaskDecomposer",
]
