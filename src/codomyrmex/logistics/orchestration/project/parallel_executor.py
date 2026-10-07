"""
Parallel Executor for Codomyrmex Workflow Management

This module provides parallel execution capabilities for workflow tasks,
including dependency management, worker pools, and execution monitoring.

Each task dictionary names its code with ``module`` and ``action``; these are
dispatched exactly like :class:`~.task_orchestrator.TaskOrchestrator` tasks
(explicit :class:`~.task_orchestrator.ActionRegistry` registrations first, then
``codomyrmex.<module>.<action>`` by import) and called with
``**task["parameters"]``.
"""

import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .task_orchestrator import ActionRegistry, describe_exception, invoke_action

# Import logging
try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of task execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class ExecutionResult:
    """Result of a task execution."""

    task_name: str
    status: ExecutionStatus
    result: Any = None
    error: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    duration: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_name": self.task_name,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
        }


class ParallelExecutor:
    """
    Executor for running workflow tasks in parallel with dependency management.

    Features:
    - Parallel execution with configurable worker pool
    - Dependency-aware task scheduling
    - Timeout and cancellation support
    - Execution monitoring and metrics
    - Error handling and recovery
    """

    def __init__(
        self,
        max_workers: int = 4,
        timeout: float = 300.0,
        actions: ActionRegistry | None = None,
    ):
        """
        Initialize the parallel executor.

        Args:
            max_workers: Maximum number of worker threads
            timeout: Default timeout for task execution in seconds
            actions: Registry consulted before import-based dispatch of
                ``module``/``action``. A new, empty registry is used if omitted.
        """
        self.max_workers = max_workers
        self.default_timeout = timeout
        self.actions = actions if actions is not None else ActionRegistry()
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="workflow_executor"
        )
        self._shutdown = False

    def execute_tasks(
        self,
        tasks: list[dict[str, Any]],
        dependencies: dict[str, list[str]],
        timeout: float | None = None,
    ) -> dict[str, ExecutionResult]:
        """
        Execute tasks with dependency management.

        A task runs once all of its dependencies (the union of
        ``dependencies[name]`` and the task's own ``"dependencies"`` key)
        completed successfully. A task whose dependency failed is marked
        ``FAILED`` without running.

        Args:
            tasks: list of task dictionaries
            dependencies: dict mapping task names to their dependencies
            timeout: Overall timeout for execution

        Returns:
            Dictionary mapping task names to their execution results

        Raises:
            ValueError: If task names are duplicated or the dependencies name
                unknown tasks or contain a cycle.
        """
        if timeout is None:
            timeout = self.default_timeout

        dependencies = _merge_dependencies(tasks, dependencies)

        # Convert tasks to execution format
        task_dict = {task["name"]: task for task in tasks}

        # Initialize results
        results = {}
        for task_name in task_dict:
            results[task_name] = ExecutionResult(
                task_name=task_name, status=ExecutionStatus.PENDING
            )

        # Track finished tasks (any final state) and successful ones
        completed: set[str] = set()
        succeeded: set[str] = set()
        futures = {}

        start_time = time.time()

        try:
            while len(completed) < len(tasks) and (time.time() - start_time) < timeout:
                # Tasks whose dependency failed can never run
                for task in tasks:
                    name = task["name"]
                    if name in completed:
                        continue
                    failed_deps = [
                        dep
                        for dep in dependencies.get(name, [])
                        if dep in completed and dep not in succeeded
                    ]
                    if failed_deps:
                        now = time.time()
                        results[name] = ExecutionResult(
                            task_name=name,
                            status=ExecutionStatus.FAILED,
                            error=f"Dependencies did not complete: {failed_deps}",
                            end_time=now,
                        )
                        completed.add(name)

                # Find ready tasks (all dependencies completed successfully)
                ready_tasks = self._get_ready_tasks(tasks, succeeded, dependencies)
                ready_tasks = [t for t in ready_tasks if t["name"] not in completed]

                if not ready_tasks:
                    # No tasks ready, wait a bit and check again
                    time.sleep(0.1)
                    continue

                # Submit ready tasks for execution
                for task in ready_tasks:
                    if task["name"] in futures:
                        continue  # Already submitted

                    future = self.executor.submit(self._execute_task, task)
                    futures[task["name"]] = future

                    # Update status
                    results[task["name"]].status = ExecutionStatus.RUNNING
                    results[task["name"]].start_time = time.time()

                # Check for completed futures
                for task_name, future in list(futures.items()):
                    if future.done():
                        try:
                            result = future.result(timeout=1.0)
                            completed.add(task_name)
                            results[task_name] = result

                            if result.status == ExecutionStatus.COMPLETED:
                                succeeded.add(task_name)
                                logger.info(
                                    "Task '%s' completed successfully", task_name
                                )
                            else:
                                logger.error(
                                    "Task '%s' failed: %s", task_name, result.error
                                )

                        except Exception as e:
                            logger.error(
                                "Error getting result for task '%s': %s", task_name, e
                            )
                            results[task_name].status = ExecutionStatus.FAILED
                            results[task_name].error = str(e)
                            results[task_name].end_time = time.time()
                            completed.add(task_name)

                        del futures[task_name]

                # Small delay to prevent busy waiting
                time.sleep(0.05)

            # Handle timeout
            if len(completed) < len(tasks):
                logger.warning(
                    "Execution timed out. Completed %s/%s tasks",
                    len(completed),
                    len(tasks),
                )
                for task_name in task_dict:
                    if task_name not in completed:
                        results[task_name].status = ExecutionStatus.TIMEOUT
                        results[task_name].end_time = time.time()

        except Exception as e:
            logger.error("Error during parallel execution: %s", e)
            # Mark remaining tasks as failed
            for task_name in task_dict:
                if results[task_name].status in [
                    ExecutionStatus.PENDING,
                    ExecutionStatus.RUNNING,
                ]:
                    results[task_name].status = ExecutionStatus.FAILED
                    results[task_name].error = f"Execution failed: {e}"
                    results[task_name].end_time = time.time()

        return results

    def execute_task_group(
        self, tasks: list[dict[str, Any]], timeout: float | None = None
    ) -> list[ExecutionResult]:
        """
        Execute a group of independent tasks in parallel.

        Args:
            tasks: list of task dictionaries (assumed to be independent)
            timeout: Timeout for the entire group execution

        Returns:
            list of execution results
        """
        if timeout is None:
            timeout = self.default_timeout

        futures = {}
        results = []

        # Submit all tasks
        for task in tasks:
            future = self.executor.submit(self._execute_task, task)
            futures[task["name"]] = (future, task)

        # Wait for completion with timeout
        start_time = time.time()
        while futures and (time.time() - start_time) < timeout:
            for task_name, (future, _task) in list(futures.items()):
                if future.done():
                    try:
                        result = future.result(timeout=1.0)
                        results.append(result)
                    except Exception as e:
                        # Create failed result
                        result = ExecutionResult(
                            task_name=task_name,
                            status=ExecutionStatus.FAILED,
                            error=str(e),
                            start_time=time.time(),
                            end_time=time.time(),
                        )
                        results.append(result)

                    del futures[task_name]

            time.sleep(0.05)

        # Handle remaining futures (timed out)
        for task_name, (future, _task) in futures.items():
            future.cancel()
            result = ExecutionResult(
                task_name=task_name,
                status=ExecutionStatus.TIMEOUT,
                error="Task timed out",
                start_time=time.time(),
                end_time=time.time(),
            )
            results.append(result)

        return results

    def wait_for_dependencies(self, task: dict[str, Any], completed: set[str]) -> bool:
        """
        Check if all dependencies of a task are completed.

        Args:
            task: Task dictionary
            completed: set of completed task names

        Returns:
            True if all dependencies are satisfied
        """
        dependencies = task.get("dependencies", [])
        return all(dep in completed for dep in dependencies)

    def _get_ready_tasks(
        self,
        tasks: list[dict[str, Any]],
        completed: set[str],
        dependencies: dict[str, list[str]],
    ) -> list[dict[str, Any]]:
        """
        Get tasks that are ready to execute (all dependencies completed).

        Args:
            tasks: list of all tasks
            completed: set of completed task names
            dependencies: Dependency mapping

        Returns:
            list of ready tasks
        """
        ready = []
        for task in tasks:
            task_name = task["name"]
            if task_name in completed:
                continue

            task_deps = dependencies.get(task_name, [])
            if all(dep in completed for dep in task_deps):
                ready.append(task)

        return ready

    def _execute_task(self, task: dict[str, Any]) -> ExecutionResult:
        """
        Execute a single task.

        Args:
            task: Task dictionary

        Returns:
            Execution result
        """
        task_name = task["name"]
        start_time = time.time()

        try:
            module = task.get("module", "")
            action = task.get("action", "")
            parameters = task.get("parameters", {})

            logger.info("Executing task '%s': %s.%s", task_name, module, action)
            func = self.actions.resolve(module, action)
            result = invoke_action(func, parameters)

            end_time = time.time()
            duration = end_time - start_time

            return ExecutionResult(
                task_name=task_name,
                status=ExecutionStatus.COMPLETED,
                result=result,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
            )

        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time

            logger.error("Task '%s' failed: %s", task_name, e)

            return ExecutionResult(
                task_name=task_name,
                status=ExecutionStatus.FAILED,
                error=describe_exception(e),
                start_time=start_time,
                end_time=end_time,
                duration=duration,
            )

    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the executor.

        Args:
            wait: Whether to wait for running tasks to complete
        """
        self._shutdown = True
        self.executor.shutdown(wait=wait)
        logger.info("ParallelExecutor shutdown complete")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown(wait=True)


# Utility functions for workflow management


def _merge_dependencies(
    tasks: list[dict[str, Any]], dependencies: dict[str, list[str]]
) -> dict[str, list[str]]:
    """Combine the dependency mapping with per-task ``dependencies`` and validate.

    Raises:
        ValueError: On duplicate task names, unknown dependencies or cycles.
    """
    from .workflow_dag import WorkflowDAG

    names = [task["name"] for task in tasks]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"Duplicate task names: {duplicates}")

    unknown_keys = sorted(set(dependencies) - set(names))
    if unknown_keys:
        raise ValueError(f"Dependencies given for unknown tasks: {unknown_keys}")

    merged: dict[str, list[str]] = {}
    for task in tasks:
        name = task["name"]
        deps = list(dependencies.get(name, []))
        deps += [dep for dep in task.get("dependencies", []) if dep not in deps]
        merged[name] = deps

    dag = WorkflowDAG(
        [{"name": name, "dependencies": deps} for name, deps in merged.items()]
    )
    is_valid, errors = dag.validate_dag()
    if not is_valid:
        raise ValueError(f"Invalid task dependencies: {'; '.join(errors)}")
    return merged


def validate_workflow_dependencies(tasks: list[dict[str, Any]]) -> list[str]:
    """
    Validate workflow task dependencies.

    Args:
        tasks: list of task dictionaries

    Returns:
        list of validation error messages
    """
    errors = []
    task_names = {task["name"] for task in tasks}

    for task in tasks:
        task_name = task["name"]
        dependencies = task.get("dependencies", [])

        # Check for self-dependency
        if task_name in dependencies:
            errors.append(f"Task '{task_name}' cannot depend on itself")

        # Check for missing dependencies
        for dep in dependencies:
            if dep not in task_names:
                errors.append(f"Task '{task_name}' depends on missing task '{dep}'")

    return errors


def get_workflow_execution_order(tasks: list[dict[str, Any]]) -> list[list[str]]:
    """
    Get the topological execution order for workflow tasks.

    Args:
        tasks: list of task dictionaries

    Returns:
        list of lists, where each inner list contains tasks that can be
        executed in parallel at that level
    """
    from .workflow_dag import WorkflowDAG

    # Convert tasks to DAG format
    dag_tasks = []
    for task in tasks:
        dag_task = {
            "name": task["name"],
            "module": task.get("module", ""),
            "action": task.get("action", ""),
            "dependencies": task.get("dependencies", []),
        }
        dag_tasks.append(dag_task)

    # Create DAG and get execution order
    dag = WorkflowDAG(dag_tasks)
    is_valid, errors = dag.validate_dag()

    if not is_valid:
        raise ValueError(f"Invalid workflow dependencies: {errors}")

    return dag.get_execution_order()
