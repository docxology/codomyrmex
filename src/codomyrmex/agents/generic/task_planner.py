from typing import Any, Optional

from dataclasses import dataclass, field
from enum import Enum

from codomyrmex.logging_monitoring import get_logger






"""Task planning and decomposition utilities."""



logger = get_logger(__name__)


class TaskStatus(Enum):
    """Task status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Task structure for task planning."""

    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = field(default_factory=list)
    result: Any = None
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class TaskPlanner:
    """Plans and decomposes complex tasks into subtasks."""

    def __init__(self):
        """Initialize task planner."""
        self.tasks: dict[str, Task] = {}
        self.logger = get_logger(__name__)

    def create_task(
        self,
        description: str,
        dependencies: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Task:
        """
        Create a new task.

        Args:
            description: Task description
            dependencies: List of task IDs this task depends on
            metadata: Optional task metadata

        Returns:
            Created task
        """
        task_id = f"task_{len(self.tasks) + 1}"
        task = Task(
            id=task_id,
            description=description,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )

        self.tasks[task_id] = task
        self.logger.debug(f"Created task: {task_id} - {description}")

        return task

    def decompose_task(
        self, main_task: Task, subtask_descriptions: list[str]
    ) -> list[Task]:
        """
        Decompose a task into subtasks.

        Args:
            main_task: Main task to decompose
            subtask_descriptions: List of subtask descriptions

        Returns:
            List of created subtasks
        """
        subtasks = []

        for i, description in enumerate(subtask_descriptions):
            subtask = self.create_task(
                description=description,
                dependencies=[main_task.id] if i > 0 else [],
                metadata={"parent_task": main_task.id},
            )
            subtasks.append(subtask)

        self.logger.info(
            f"Decomposed task {main_task.id} into {len(subtasks)} subtasks"
        )

        return subtasks

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task if found, None otherwise
        """
        return self.tasks.get(task_id)

    def update_task_status(
        self, task_id: str, status: TaskStatus, result: Any = None, error: Optional[str] = None
    ) -> None:
        """
        Update task status.

        Args:
            task_id: Task ID
            status: New status
            result: Task result (optional)
            error: Error message (optional)
        """
        task = self.tasks.get(task_id)
        if not task:
            self.logger.warning(f"Task not found: {task_id}")
            return

        task.status = status
        if result is not None:
            task.result = result
        if error is not None:
            task.error = error

        self.logger.debug(f"Updated task {task_id} status to {status.value}")

    def get_ready_tasks(self) -> list[Task]:
        """
        Get tasks that are ready to execute (dependencies completed).

        Returns:
            List of ready tasks
        """
        ready_tasks = []

        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue

            # Check if all dependencies are completed
            all_deps_completed = True
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    all_deps_completed = False
                    break

            if all_deps_completed:
                ready_tasks.append(task)

        return ready_tasks

    def get_task_execution_order(self) -> list[Task]:
        """
        Get tasks in execution order (respecting dependencies).

        Returns:
            List of tasks in execution order
        """
        # Simple topological sort
        executed = set()
        execution_order = []

        while len(executed) < len(self.tasks):
            progress = False

            for task in self.tasks.values():
                if task.id in executed:
                    continue

                # Check if all dependencies are executed
                all_deps_executed = all(
                    dep_id in executed for dep_id in task.dependencies
                )

                if all_deps_executed:
                    execution_order.append(task)
                    executed.add(task.id)
                    progress = True

            if not progress:
                # Circular dependency or missing task
                remaining = [
                    task.id
                    for task in self.tasks.values()
                    if task.id not in executed
                ]
                self.logger.warning(
                    f"Circular dependency or missing tasks: {remaining}"
                )
                break

        return execution_order

    def get_all_tasks(self) -> list[Task]:
        """
        Get all tasks.

        Returns:
            List of all tasks
        """
        return list(self.tasks.values())


