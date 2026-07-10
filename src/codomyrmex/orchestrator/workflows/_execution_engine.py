"""Task execution engine for the workflow DAG runner.

Handles the low-level mechanics of executing individual tasks with
retry policies and timeout support, plus the batch-launch /
result-processing helpers used by
:class:`~codomyrmex.orchestrator.workflows.workflow.Workflow`.

These were extracted from ``workflow.py`` to keep the Workflow class
focused on DAG topology and orchestration.
"""

from __future__ import annotations

import asyncio
import inspect
import time
from typing import TYPE_CHECKING, Any

from codomyrmex.logging_monitoring import get_logger

from ._models import RetryPolicy, Task, TaskResult, TaskStatus

logger = get_logger(__name__)

__all__ = [
    "WorkflowExecutionEngine",
]


class WorkflowExecutionEngine:
    """Encapsulates task execution and batch-launch logic for a Workflow.

    This is a stateless helper instantiated per ``Workflow.run()`` call;
    it operates on the Workflow's own ``tasks`` / ``task_results`` dicts
    so that the Workflow object remains the single source of truth.
    """

    def __init__(self, workflow: Any) -> None:
        self._wf = workflow
        self._logger = workflow.logger

    def _try_emit_event(self, factory_path: str, *args: Any, **kwargs: Any) -> None:
        """Emit an observability event, silently skipping if unavailable."""
        try:
            import importlib

            mod = importlib.import_module(
                ".observability.orchestrator_events",
                package=self._wf.__class__.__module__.rsplit(".", 1)[0],
            )
            factory = getattr(mod, factory_path)
            self._wf._publish_event(factory(*args, **kwargs))
        except (ImportError, AttributeError) as e:
            self._logger.debug("Observability events not available: %s", e)

    def _emit_progress(
        self, task_name: str, status: str, details: dict[str, Any] | None = None
    ) -> None:
        """Emit progress update if callback is registered."""
        if self._wf.progress_callback:
            try:
                self._wf.progress_callback(task_name, status, details or {})
            except Exception as e:
                self._logger.warning("Progress callback error: %s", e)

    def find_runnable_tasks(
        self,
        completed_tasks: set[str],
        skipped_tasks: set[str],
    ) -> list[Task]:
        """Identify pending tasks whose dependencies are satisfied.

        Tasks whose condition evaluates to False are marked SKIPPED.
        """
        runnable: list[Task] = []
        for name, task in self._wf.tasks.items():
            if task.status != TaskStatus.PENDING:
                continue
            if not task.dependencies.issubset(completed_tasks):
                continue
            if task.should_run(self._wf.task_results):
                runnable.append(task)
            else:
                self._logger.info("Task '%s' skipped by condition", name)
                task.status = TaskStatus.SKIPPED
                skipped_tasks.add(name)
                self._wf.task_results[name] = task.get_result()
                self._emit_progress(name, "skipped", {"reason": "condition"})
        return runnable

    def skip_blocked_tasks(
        self,
        failed_tasks: set[str],
        skipped_tasks: set[str],
    ) -> bool:
        """Mark pending tasks with failed dependencies as SKIPPED.

        Returns True if at least one task was newly skipped (so the main
        loop should re-evaluate), False if a deadlock is detected.
        """
        any_skipped = False
        for name, task in self._wf.tasks.items():
            if task.status == TaskStatus.PENDING:
                if not task.dependencies.isdisjoint(failed_tasks):
                    self._logger.warning(
                        "Task '%s' skipped due to failed dependencies.", name
                    )
                    task.status = TaskStatus.SKIPPED
                    task.error = Exception("Dependency failed")
                    skipped_tasks.add(name)
                    self._wf.task_results[name] = task.get_result()
                    self._emit_progress(
                        name, "skipped", {"reason": "dependency_failed"}
                    )
                    any_skipped = True
        return any_skipped

    async def launch_batch(self, runnable: list[Task]) -> list[Any]:
        """Start a batch of runnable tasks concurrently.

        Returns the list of results (or exceptions) from ``asyncio.gather``.
        """
        self._logger.info("Running batch: %s", [t.name for t in runnable])
        for task in runnable:
            task.status = TaskStatus.RUNNING
            self._emit_progress(task.name, "running", {})
            self._try_emit_event("task_started", self._wf.name, task.name)

        coroutines = [self.execute_task_with_retry(t) for t in runnable]
        return await asyncio.gather(*coroutines, return_exceptions=True)

    def process_batch_results(
        self,
        runnable: list[Task],
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
                self._wf.task_results[task.name] = task.get_result()
                self._logger.error("Task '%s' failed: %s", task.name, result)
                self._emit_progress(task.name, "failed", {"error": str(result)})
                self._try_emit_event(
                    "task_failed", self._wf.name, task.name, str(result)
                )
                if self._wf.fail_fast:
                    self._logger.info("Fail-fast: stopping workflow")
                    self._wf._cancelled = True
            else:
                if task.transform_result:
                    try:
                        result = task.transform_result(result)
                    except Exception as e:
                        self._logger.warning(
                            "Result transform failed for %s: %s", task.name, e
                        )
                task.status = TaskStatus.COMPLETED
                task.result = result
                completed_tasks.add(task.name)
                self._wf.task_results[task.name] = task.get_result()
                self._logger.info(
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
                    self._wf.name,
                    task.name,
                    execution_time=task.execution_time,
                    attempts=task.attempts,
                )

    async def execute_task_with_retry(self, task: Task) -> Any:
        """Execute a task with retry logic."""
        policy = task.retry_policy or RetryPolicy(max_attempts=1)

        last_error: BaseException = RuntimeError(
            f"Retry exhausted for task '{task.name}' without capturing an exception"
        )

        for attempt in range(1, policy.max_attempts + 1):
            task.attempts = attempt
            start_time = time.time()

            try:
                result = await self.execute_task(task)
                task.execution_time = time.time() - start_time
                return result
            except policy.retry_on as e:
                last_error = e
                task.execution_time = time.time() - start_time

                if attempt < policy.max_attempts:
                    delay = policy.get_delay(attempt)
                    self._logger.warning(
                        "Task '%s' failed (attempt %s/%s), retrying in %.1fs: %s",
                        task.name,
                        attempt,
                        policy.max_attempts,
                        delay,
                        e,
                    )
                    task.status = TaskStatus.RETRYING
                    self._emit_progress(
                        task.name,
                        "retrying",
                        {"attempt": attempt, "delay": delay, "error": str(e)},
                    )
                    await asyncio.sleep(delay)
                else:
                    self._logger.error(
                        "Task '%s' failed after %s attempts: %s",
                        task.name,
                        policy.max_attempts,
                        e,
                    )
                    raise
            except Exception as _exc:
                task.execution_time = time.time() - start_time
                raise

        raise last_error

    async def execute_task(self, task: Task) -> Any:
        """Execute a single task."""
        try:
            # Inject task results into kwargs if action accepts them
            kwargs = task.kwargs.copy()
            if "_task_results" not in kwargs:
                # Allow tasks to access previous results
                kwargs["_task_results"] = self._wf.task_results

            if inspect.iscoroutinefunction(task.action):
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
