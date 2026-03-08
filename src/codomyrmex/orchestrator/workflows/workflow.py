"""Workflow Orchestration Module.

This module provides support for defining and executing Directed Acyclic Graphs (DAGs)
of tasks. It allows for complex dependency management between tasks.

Features:
- Task dependencies and parallel execution
- Retry logic with exponential backoff
- Conditional execution based on previous task results
- Result passing between tasks
- Timeout support per task and workflow-wide
- Progress callbacks for streaming updates
"""

import asyncio
import time
from collections.abc import Callable
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from ._models import (
    CycleError,
    ProgressCallback,
    RetryPolicy,
    Task,
    TaskFailedError,
    TaskResult,
    TaskStatus,
    WorkflowError,
)

logger = get_logger(__name__)

__all__ = [
    "CycleError",
    "RetryPolicy",
    "Task",
    "TaskFailedError",
    "TaskResult",
    "TaskStatus",
    "Workflow",
    "WorkflowError",
    "chain",
    "fan_out_fan_in",
    "parallel",
]


class Workflow:
    """Manages a collection of tasks and their dependencies.

    Supports:
    - Task dependencies with parallel execution
    - Retry logic with exponential backoff
    - Conditional task execution
    - Result passing between tasks
    - Progress callbacks for monitoring
    - Workflow-level timeout
    """

    def __init__(
        self,
        name: str,
        timeout: float | None = None,
        fail_fast: bool = True,
        progress_callback: ProgressCallback | None = None,
        event_bus: Any = None,
    ):
        """Initialize workflow.

        Args:
            name: Workflow name for identification
            timeout: Overall workflow timeout in seconds
            fail_fast: Stop on first failure if True
            progress_callback: Callback for progress updates (task_name, status, details)
            event_bus: Optional ``EventBus`` instance for typed event publishing
        """
        self.name = name
        self.timeout = timeout
        self.fail_fast = fail_fast
        self.progress_callback = progress_callback
        self._event_bus = event_bus
        self.tasks: dict[str, Task] = {}
        self.task_results: dict[str, TaskResult] = {}
        self.logger = get_logger(f"Workflow.{name}")
        self._start_time: float | None = None
        self._cancelled = False

    def _publish_event(self, event: Any) -> None:
        """Publish event to EventBus if one is attached."""
        if self._event_bus is not None:
            try:
                self._event_bus.publish(event)
            except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
                self.logger.warning("EventBus publish failed: %s", exc)

    def add_task(self, name: str, action: Callable[..., Any], **opts: Any) -> "Workflow":
        """Add a task to the workflow. Returns self for chaining.

        Keyword options: dependencies, args, kwargs, timeout, retry_policy,
        condition, transform_result, tags, metadata.
        """
        if name in self.tasks:
            raise WorkflowError(f"Task '{name}' already exists in workflow.")
        deps = opts.get("dependencies")
        tags = opts.get("tags")
        self.tasks[name] = Task(
            name=name, action=action,
            dependencies=set(deps) if deps else set(),
            args=opts.get("args") or [],
            kwargs=opts.get("kwargs") or {},
            timeout=opts.get("timeout"),
            retry_policy=opts.get("retry_policy"),
            condition=opts.get("condition"),
            transform_result=opts.get("transform_result"),
            tags=set(tags) if tags else set(),
            metadata=opts.get("metadata") or {},
        )
        return self

    def cancel(self):
        """Cancel the workflow execution."""
        self._cancelled = True
        self.logger.info("Workflow '%s' cancellation requested", self.name)

    def _emit_progress(
        self, task_name: str, status: str, details: dict[str, Any] | None = None
    ):
        """Emit progress update if callback is registered."""
        if self.progress_callback:
            try:
                self.progress_callback(task_name, status, details or {})
            except Exception as e:
                self.logger.warning("Progress callback error: %s", e)

    def validate(self):
        """Validate workflow structure (check dependencies exist, check for cycles)."""
        # 1. Check dependencies exist
        for name, task in self.tasks.items():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    raise WorkflowError(
                        f"Task '{name}' depends on unknown task '{dep}'"
                    )

        # 2. Check for cycles
        visited = set()
        path = set()

        def check_cycle(task_name):
            visited.add(task_name)
            path.add(task_name)

            for dep in self.tasks[task_name].dependencies:
                if dep in path:
                    raise CycleError(
                        f"Circular dependency detected: {task_name} -> {dep}"
                    )
                if dep not in visited:
                    check_cycle(dep)

            path.remove(task_name)

        for name in self.tasks:
            if name not in visited:
                check_cycle(name)

    def _try_emit_event(self, factory_path: str, *args: Any, **kwargs: Any) -> None:
        """Emit an observability event, silently skipping if unavailable."""
        try:
            import importlib

            mod = importlib.import_module(
                ".observability.orchestrator_events",
                package=__package__,
            )
            factory = getattr(mod, factory_path)
            self._publish_event(factory(*args, **kwargs))
        except (ImportError, AttributeError) as e:
            self.logger.debug("Observability events not available: %s", e)

    def _find_runnable_tasks(
        self,
        completed_tasks: set[str],
        skipped_tasks: set[str],
    ) -> list["Task"]:
        """Identify pending tasks whose dependencies are satisfied.

        Tasks whose condition evaluates to False are marked SKIPPED.
        """
        runnable: list[Task] = []
        for name, task in self.tasks.items():
            if task.status != TaskStatus.PENDING:
                continue
            if not task.dependencies.issubset(completed_tasks):
                continue
            if task.should_run(self.task_results):
                runnable.append(task)
            else:
                self.logger.info("Task '%s' skipped by condition", name)
                task.status = TaskStatus.SKIPPED
                skipped_tasks.add(name)
                self.task_results[name] = task.get_result()
                self._emit_progress(name, "skipped", {"reason": "condition"})
        return runnable

    def _skip_blocked_tasks(
        self,
        failed_tasks: set[str],
        skipped_tasks: set[str],
    ) -> bool:
        """Mark pending tasks with failed dependencies as SKIPPED.

        Returns True if at least one task was newly skipped (so the main
        loop should re-evaluate), False if a deadlock is detected.
        """
        any_skipped = False
        for name, task in self.tasks.items():
            if task.status == TaskStatus.PENDING:
                if not task.dependencies.isdisjoint(failed_tasks):
                    self.logger.warning(
                        "Task '%s' skipped due to failed dependencies.", name
                    )
                    task.status = TaskStatus.SKIPPED
                    task.error = Exception("Dependency failed")
                    skipped_tasks.add(name)
                    self.task_results[name] = task.get_result()
                    self._emit_progress(
                        name, "skipped", {"reason": "dependency_failed"}
                    )
                    any_skipped = True
        return any_skipped

    async def _launch_batch(self, runnable: list["Task"]) -> list[Any]:
        """Start a batch of runnable tasks concurrently.

        Returns the list of results (or exceptions) from ``asyncio.gather``.
        """
        self.logger.info("Running batch: %s", [t.name for t in runnable])
        for task in runnable:
            task.status = TaskStatus.RUNNING
            self._emit_progress(task.name, "running", {})
            self._try_emit_event("task_started", self.name, task.name)

        coroutines = [self._execute_task_with_retry(t) for t in runnable]
        return await asyncio.gather(*coroutines, return_exceptions=True)

    def _process_batch_results(
        self,
        runnable: list["Task"],
        results: list[Any],
        completed_tasks: set[str],
        failed_tasks: set[str],
    ) -> None:
        """Categorise batch results into completed / failed sets."""
        for task, result in zip(runnable, results, strict=False):
            if isinstance(result, Exception):
                task.status = TaskStatus.FAILED
                task.error = result
                failed_tasks.add(task.name)
                self.task_results[task.name] = task.get_result()
                self.logger.error("Task '%s' failed: %s", task.name, result)
                self._emit_progress(task.name, "failed", {"error": str(result)})
                self._try_emit_event(
                    "task_failed", self.name, task.name, str(result)
                )
                if self.fail_fast:
                    self.logger.info("Fail-fast: stopping workflow")
                    self._cancelled = True
            else:
                if task.transform_result:
                    try:
                        result = task.transform_result(result)
                    except Exception as e:
                        self.logger.warning(
                            "Result transform failed for %s: %s", task.name, e
                        )
                task.status = TaskStatus.COMPLETED
                task.result = result
                completed_tasks.add(task.name)
                self.task_results[task.name] = task.get_result()
                self.logger.info(
                    "Task '%s' completed in %.2fs", task.name, task.execution_time
                )
                self._emit_progress(
                    task.name,
                    "completed",
                    {
                        "execution_time": task.execution_time,
                        "attempts": task.attempts,
                    },
                )
                self._try_emit_event(
                    "task_completed",
                    self.name,
                    task.name,
                    execution_time=task.execution_time,
                    attempts=task.attempts,
                )

    async def run(self) -> dict[str, Any]:
        """Execute the workflow.

        Returns:
            Dictionary mapping task names to their results.

        Raises:
            WorkflowError: If workflow execution fails.
            CycleError: If circular dependencies detected.
        """
        self.validate()
        self._start_time = time.time()
        self._cancelled = False
        self.task_results.clear()

        self.logger.info(
            "Starting workflow '%s' with %s tasks.", self.name, len(self.tasks)
        )
        self._emit_progress("workflow", "started", {"total_tasks": len(self.tasks)})
        self._try_emit_event("workflow_started", self.name, len(self.tasks))

        # Reset task states
        for task in self.tasks.values():
            task.status = TaskStatus.PENDING
            task.result = None
            task.error = None
            task.attempts = 0
            task.execution_time = 0.0

        completed_tasks: set[str] = set()
        failed_tasks: set[str] = set()
        skipped_tasks: set[str] = set()

        while len(completed_tasks) + len(failed_tasks) + len(skipped_tasks) < len(
            self.tasks
        ):
            if self._cancelled:
                self.logger.info("Workflow cancelled")
                break
            if self.timeout and (time.time() - self._start_time) > self.timeout:
                raise WorkflowError(f"Workflow timeout after {self.timeout}s")

            runnable = self._find_runnable_tasks(completed_tasks, skipped_tasks)

            if not runnable and (
                len(completed_tasks) + len(failed_tasks) + len(skipped_tasks)
                < len(self.tasks)
            ):
                if not self._skip_blocked_tasks(failed_tasks, skipped_tasks):
                    raise WorkflowError("Deadlock detected during execution.")
                continue

            if not runnable:
                break

            results = await self._launch_batch(runnable)
            self._process_batch_results(
                runnable, results, completed_tasks, failed_tasks
            )

        # Summary
        elapsed = time.time() - self._start_time
        self._emit_progress(
            "workflow",
            "completed",
            {
                "completed": len(completed_tasks),
                "failed": len(failed_tasks),
                "skipped": len(skipped_tasks),
                "elapsed": elapsed,
            },
        )
        if failed_tasks:
            self._try_emit_event(
                "workflow_failed", self.name, f"{len(failed_tasks)} tasks failed"
            )
        else:
            self._try_emit_event(
                "workflow_completed",
                self.name,
                completed=len(completed_tasks),
                failed=len(failed_tasks),
                skipped=len(skipped_tasks),
                elapsed=elapsed,
            )

        return {name: task.result for name, task in self.tasks.items()}

    async def _execute_task_with_retry(self, task: Task) -> Any:
        """Execute a task with retry logic."""
        policy = task.retry_policy or RetryPolicy(max_attempts=1)

        for attempt in range(1, policy.max_attempts + 1):
            task.attempts = attempt
            start_time = time.time()

            try:
                result = await self._execute_task(task)
                task.execution_time = time.time() - start_time
                return result
            except policy.retry_on as e:
                last_error = e
                task.execution_time = time.time() - start_time

                if attempt < policy.max_attempts:
                    delay = policy.get_delay(attempt)
                    self.logger.warning(
                        "Task '%s' failed (attempt %s/%s), retrying in %.1fs: %s",
                        task.name, attempt, policy.max_attempts, delay, e,
                    )
                    task.status = TaskStatus.RETRYING
                    self._emit_progress(
                        task.name,
                        "retrying",
                        {"attempt": attempt, "delay": delay, "error": str(e)},
                    )
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(
                        "Task '%s' failed after %s attempts: %s", task.name, policy.max_attempts, e
                    )
                    raise
            except Exception as _exc:
                task.execution_time = time.time() - start_time
                raise

        raise last_error

    async def _execute_task(self, task: Task) -> Any:
        """Execute a single task."""
        try:
            # Inject task results into kwargs if action accepts them
            kwargs = task.kwargs.copy()
            if "_task_results" not in kwargs:
                # Allow tasks to access previous results
                kwargs["_task_results"] = self.task_results

            if asyncio.iscoroutinefunction(task.action):
                if task.timeout:
                    return await asyncio.wait_for(
                        task.action(*task.args, **kwargs), timeout=task.timeout
                    )
                return await task.action(*task.args, **kwargs)
            # Run sync functions in thread pool to avoid blocking
            loop = asyncio.get_running_loop()
            # Remove injected results for sync functions that might not expect them
            if "_task_results" in kwargs and "_task_results" not in task.kwargs:
                del kwargs["_task_results"]

            def func():
                return task.action(*task.args, **kwargs)

            if task.timeout:
                return await asyncio.wait_for(
                    loop.run_in_executor(None, func), timeout=task.timeout
                )
            return await loop.run_in_executor(None, func)
        except TimeoutError:
            raise TimeoutError(
                f"Task '{task.name}' timed out after {task.timeout}s"
            ) from None

    def get_task_result(self, task_name: str) -> TaskResult | None:
        """Get result of a specific task."""
        return self.task_results.get(task_name)

    def get_summary(self) -> dict[str, Any]:
        """Get workflow execution summary."""
        completed = sum(
            1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED
        )
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        skipped = sum(1 for t in self.tasks.values() if t.status == TaskStatus.SKIPPED)
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)

        total_time = sum(t.execution_time for t in self.tasks.values())
        elapsed = time.time() - self._start_time if self._start_time else 0

        return {
            "name": self.name,
            "total_tasks": len(self.tasks),
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "pending": pending,
            "success": failed == 0 and pending == 0,
            "total_execution_time": total_time,
            "elapsed_time": elapsed,
            "tasks": {
                name: {
                    "status": task.status.value,
                    "execution_time": task.execution_time,
                    "attempts": task.attempts,
                    "error": str(task.error) if task.error else None,
                }
                for name, task in self.tasks.items()
            },
        }


# Convenience functions for creating common workflows


from ._factories import chain, fan_out_fan_in, parallel
