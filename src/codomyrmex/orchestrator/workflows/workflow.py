
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
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


@dataclass
class RetryPolicy:
    """Retry configuration for tasks."""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    retry_on: tuple = (Exception,)  # Exception types to retry on

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt using exponential backoff."""
        delay = self.initial_delay * (self.exponential_base ** (attempt - 1))
        return min(delay, self.max_delay)


@dataclass
class TaskResult:
    """Result of a task execution."""
    success: bool
    value: Any = None
    error: str | None = None
    execution_time: float = 0.0
    attempts: int = 1


@dataclass
class Task:
    """Represents a single unit of work in a workflow."""
    name: str
    action: Callable[..., Any]
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    dependencies: set[str] = field(default_factory=set)
    timeout: float | None = None

    # Retry configuration
    retry_policy: RetryPolicy | None = None

    # Conditional execution: function that receives task results dict
    # and returns True if task should run
    condition: Callable[[dict[str, TaskResult]], bool] | None = None

    # Result transformation: function to transform result before passing
    transform_result: Callable[[Any], Any] | None = None

    # Tags for filtering and grouping
    tags: set[str] = field(default_factory=set)

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # State
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Exception | None = None
    attempts: int = 0
    execution_time: float = 0.0

    def __hash__(self):
        """hash ."""
        return hash(self.name)

    def should_run(self, results: dict[str, TaskResult]) -> bool:
        """Check if task should run based on condition."""
        if self.condition is None:
            return True
        try:
            return self.condition(results)
        except Exception as e:
            logger.warning(f"Condition check failed for {self.name}: {e}")
            return False

    def get_result(self) -> TaskResult:
        """Get task result as TaskResult object."""
        return TaskResult(
            success=self.status == TaskStatus.COMPLETED,
            value=self.result,
            error=str(self.error) if self.error else None,
            execution_time=self.execution_time,
            attempts=self.attempts
        )

class WorkflowError(Exception):
    """Base exception for workflow errors."""
    pass


class CycleError(WorkflowError):
    """Raised when a circular dependency is detected."""
    pass


class TaskFailedError(WorkflowError):
    """Raised when a required task fails."""
    pass


ProgressCallback = Callable[[str, str, dict[str, Any]], None]


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
                self.logger.warning(f"EventBus publish failed: {exc}")

    def add_task(
        self,
        name: str,
        action: Callable[..., Any],
        dependencies: list[str] | None = None,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
        timeout: float | None = None,
        retry_policy: RetryPolicy | None = None,
        condition: Callable[[dict[str, TaskResult]], bool] | None = None,
        transform_result: Callable[[Any], Any] | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None
    ) -> 'Workflow':
        """Add a task to the workflow.

        Args:
            name: Unique task name
            action: Callable to execute (sync or async)
            dependencies: List of task names that must complete first
            args: Positional arguments for action
            kwargs: Keyword arguments for action
            timeout: Task-specific timeout in seconds
            retry_policy: Retry configuration for failures
            condition: Function to determine if task should run based on results
            transform_result: Function to transform result before storing
            tags: Tags for filtering and grouping
            metadata: Additional metadata

        Returns:
            Self for chaining
        """
        if name in self.tasks:
            raise WorkflowError(f"Task '{name}' already exists in workflow.")

        deps = set(dependencies) if dependencies else set()

        task = Task(
            name=name,
            action=action,
            dependencies=deps,
            args=args or [],
            kwargs=kwargs or {},
            timeout=timeout,
            retry_policy=retry_policy,
            condition=condition,
            transform_result=transform_result,
            tags=set(tags) if tags else set(),
            metadata=metadata or {}
        )
        self.tasks[name] = task
        return self

    def cancel(self):
        """Cancel the workflow execution."""
        self._cancelled = True
        self.logger.info(f"Workflow '{self.name}' cancellation requested")

    def _emit_progress(self, task_name: str, status: str, details: dict[str, Any] = None):
        """Emit progress update if callback is registered."""
        if self.progress_callback:
            try:
                self.progress_callback(task_name, status, details or {})
            except Exception as e:
                self.logger.warning(f"Progress callback error: {e}")

    def validate(self):
        """Validate workflow structure (check dependencies exist, check for cycles)."""
        # 1. Check dependencies exist
        for name, task in self.tasks.items():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    raise WorkflowError(f"Task '{name}' depends on unknown task '{dep}'")

        # 2. Check for cycles
        visited = set()
        path = set()

        def check_cycle(task_name):
            visited.add(task_name)
            path.add(task_name)

            for dep in self.tasks[task_name].dependencies:
                if dep in path:
                    raise CycleError(f"Circular dependency detected: {task_name} -> {dep}")
                if dep not in visited:
                    check_cycle(dep)

            path.remove(task_name)

        for name in self.tasks:
            if name not in visited:
                check_cycle(name)

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

        self.logger.info(f"Starting workflow '{self.name}' with {len(self.tasks)} tasks.")
        self._emit_progress("workflow", "started", {"total_tasks": len(self.tasks)})

        # Emit typed event
        try:
            from .observability.orchestrator_events import workflow_started as _ws
            self._publish_event(_ws(self.name, len(self.tasks)))
        except ImportError as e:
            self.logger.debug("Observability events not available: %s", e)
            pass

        # Reset task states
        for task in self.tasks.values():
            task.status = TaskStatus.PENDING
            task.result = None
            task.error = None
            task.attempts = 0
            task.execution_time = 0.0

        # Topological execution with parallel batching
        completed_tasks = set()
        failed_tasks = set()
        skipped_tasks = set()

        while len(completed_tasks) + len(failed_tasks) + len(skipped_tasks) < len(self.tasks):
            # Check cancellation
            if self._cancelled:
                self.logger.info("Workflow cancelled")
                break

            # Check workflow timeout
            if self.timeout and (time.time() - self._start_time) > self.timeout:
                raise WorkflowError(f"Workflow timeout after {self.timeout}s")

            # Find runnable tasks
            runnable = []
            for name, task in self.tasks.items():
                if task.status == TaskStatus.PENDING:
                    if task.dependencies.issubset(completed_tasks):
                        # Check condition
                        if task.should_run(self.task_results):
                            runnable.append(task)
                        else:
                            self.logger.info(f"Task '{name}' skipped by condition")
                            task.status = TaskStatus.SKIPPED
                            skipped_tasks.add(name)
                            self.task_results[name] = task.get_result()
                            self._emit_progress(name, "skipped", {"reason": "condition"})

            # Handle blocked tasks
            if not runnable and (len(completed_tasks) + len(failed_tasks) + len(skipped_tasks) < len(self.tasks)):
                blocked = False
                for name, task in self.tasks.items():
                    if task.status == TaskStatus.PENDING:
                        if not task.dependencies.isdisjoint(failed_tasks):
                            self.logger.warning(f"Task '{name}' skipped due to failed dependencies.")
                            task.status = TaskStatus.SKIPPED
                            task.error = Exception("Dependency failed")
                            skipped_tasks.add(name)
                            self.task_results[name] = task.get_result()
                            self._emit_progress(name, "skipped", {"reason": "dependency_failed"})
                            blocked = True

                if blocked:
                    continue

                raise WorkflowError("Deadlock detected during execution.")

            if not runnable:
                break

            self.logger.info(f"Running batch: {[t.name for t in runnable]}")

            # Run tasks concurrently
            coroutines = []
            for task in runnable:
                task.status = TaskStatus.RUNNING
                self._emit_progress(task.name, "running", {})
                try:
                    from .observability.orchestrator_events import task_started as _ts
                    self._publish_event(_ts(self.name, task.name))
                except ImportError as e:
                    self.logger.debug("Observability events not available: %s", e)
                    pass
                coroutines.append(self._execute_task_with_retry(task))

            results = await asyncio.gather(*coroutines, return_exceptions=True)

            for task, result in zip(runnable, results, strict=False):
                if isinstance(result, Exception):
                    task.status = TaskStatus.FAILED
                    task.error = result
                    failed_tasks.add(task.name)
                    self.task_results[task.name] = task.get_result()
                    self.logger.error(f"Task '{task.name}' failed: {result}")
                    self._emit_progress(task.name, "failed", {"error": str(result)})
                    try:
                        from .observability.orchestrator_events import (
                            task_failed as _tf,
                        )
                        self._publish_event(_tf(self.name, task.name, str(result)))
                    except ImportError as e:
                        self.logger.debug("Observability events not available: %s", e)
                        pass

                    if self.fail_fast:
                        self.logger.info("Fail-fast: stopping workflow")
                        self._cancelled = True
                else:
                    # Apply transform if specified
                    if task.transform_result:
                        try:
                            result = task.transform_result(result)
                        except Exception as e:
                            self.logger.warning(f"Result transform failed for {task.name}: {e}")

                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    completed_tasks.add(task.name)
                    self.task_results[task.name] = task.get_result()
                    self.logger.info(f"Task '{task.name}' completed in {task.execution_time:.2f}s")
                    self._emit_progress(task.name, "completed", {
                        "execution_time": task.execution_time,
                        "attempts": task.attempts
                    })
                    try:
                        from .observability.orchestrator_events import (
                            task_completed as _tc,
                        )
                        self._publish_event(_tc(
                            self.name, task.name,
                            execution_time=task.execution_time,
                            attempts=task.attempts,
                        ))
                    except ImportError as e:
                        self.logger.debug("Observability events not available: %s", e)
                        pass

        # Summary
        elapsed = time.time() - self._start_time
        self._emit_progress("workflow", "completed", {
            "completed": len(completed_tasks),
            "failed": len(failed_tasks),
            "skipped": len(skipped_tasks),
            "elapsed": elapsed
        })

        # Emit typed workflow completed/failed event
        try:
            from .observability.orchestrator_events import workflow_completed as _wc
            from .observability.orchestrator_events import workflow_failed as _wf
            if failed_tasks:
                self._publish_event(_wf(self.name, f"{len(failed_tasks)} tasks failed"))
            else:
                self._publish_event(_wc(
                    self.name,
                    completed=len(completed_tasks),
                    failed=len(failed_tasks),
                    skipped=len(skipped_tasks),
                    elapsed=elapsed,
                ))
        except ImportError as e:
            self.logger.debug("Observability events not available: %s", e)
            pass

        results = {name: task.result for name, task in self.tasks.items()}
        return results

    async def _execute_task_with_retry(self, task: Task) -> Any:
        """Execute a task with retry logic."""
        policy = task.retry_policy or RetryPolicy(max_attempts=1)
        last_error = None

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
                        f"Task '{task.name}' failed (attempt {attempt}/{policy.max_attempts}), "
                        f"retrying in {delay:.1f}s: {e}"
                    )
                    task.status = TaskStatus.RETRYING
                    self._emit_progress(task.name, "retrying", {
                        "attempt": attempt,
                        "delay": delay,
                        "error": str(e)
                    })
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(
                        f"Task '{task.name}' failed after {policy.max_attempts} attempts: {e}"
                    )
                    raise
            except Exception:
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
                        task.action(*task.args, **kwargs),
                        timeout=task.timeout
                    )
                else:
                    return await task.action(*task.args, **kwargs)
            else:
                # Run sync functions in thread pool to avoid blocking
                loop = asyncio.get_running_loop()
                # Remove injected results for sync functions that might not expect them
                if "_task_results" in kwargs and "_task_results" not in task.kwargs:
                    del kwargs["_task_results"]
                def func():
                    return task.action(*task.args, **kwargs)
                if task.timeout:
                    return await asyncio.wait_for(
                        loop.run_in_executor(None, func),
                        timeout=task.timeout
                    )
                else:
                    return await loop.run_in_executor(None, func)
        except TimeoutError:
            raise TimeoutError(f"Task '{task.name}' timed out after {task.timeout}s") from None

    def get_task_result(self, task_name: str) -> TaskResult | None:
        """Get result of a specific task."""
        return self.task_results.get(task_name)

    def get_summary(self) -> dict[str, Any]:
        """Get workflow execution summary."""
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
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
                    "error": str(task.error) if task.error else None
                }
                for name, task in self.tasks.items()
            }
        }


# Convenience functions for creating common workflows


def chain(*actions: Callable, names: list[str] | None = None) -> Workflow:
    """Create a linear workflow where each task depends on the previous.

    Args:
        *actions: Callables to execute in order
        names: Optional task names (defaults to action names or indices)

    Returns:
        Configured Workflow
    """
    workflow = Workflow(name="chain")
    prev_name = None

    for i, action in enumerate(actions):
        name = names[i] if names and i < len(names) else getattr(action, "__name__", f"task_{i}")
        deps = [prev_name] if prev_name else None
        workflow.add_task(name=name, action=action, dependencies=deps)
        prev_name = name

    return workflow


def parallel(*actions: Callable, names: list[str] | None = None) -> Workflow:
    """Create a workflow where all tasks run in parallel.

    Args:
        *actions: Callables to execute in parallel
        names: Optional task names

    Returns:
        Configured Workflow
    """
    workflow = Workflow(name="parallel")

    for i, action in enumerate(actions):
        name = names[i] if names and i < len(names) else getattr(action, "__name__", f"task_{i}")
        workflow.add_task(name=name, action=action)

    return workflow


def fan_out_fan_in(
    initial: Callable,
    parallel_tasks: list[Callable],
    final: Callable,
    initial_name: str = "initial",
    final_name: str = "final"
) -> Workflow:
    """Create a fan-out/fan-in workflow pattern.

    initial -> [parallel_tasks...] -> final

    Args:
        initial: Initial task to run first
        parallel_tasks: Tasks to run in parallel after initial
        final: Final task to run after all parallel tasks complete

    Returns:
        Configured Workflow
    """
    workflow = Workflow(name="fan_out_fan_in")

    # Initial task
    workflow.add_task(name=initial_name, action=initial)

    # Parallel tasks
    parallel_names = []
    for i, action in enumerate(parallel_tasks):
        name = getattr(action, "__name__", f"parallel_{i}")
        workflow.add_task(name=name, action=action, dependencies=[initial_name])
        parallel_names.append(name)

    # Final task depends on all parallel tasks
    workflow.add_task(name=final_name, action=final, dependencies=parallel_names)

    return workflow

