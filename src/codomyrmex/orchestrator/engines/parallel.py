"""Parallel workflow execution engine."""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any

from .base import ExecutionEngine
from .models import (
    TaskDefinition,
    TaskResult,
    TaskState,
    WorkflowDefinition,
    WorkflowResult,
)


class ParallelEngine(ExecutionEngine):
    """Executes independent tasks in parallel."""

    def __init__(self, max_workers: int = 4, max_retries: int = 3) -> None:
        self.max_workers = max_workers
        self.max_retries = max_retries

    def execute(
        self,
        workflow: WorkflowDefinition,
        initial_context: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        context = initial_context or {}
        task_results: dict[str, TaskResult] = {}
        start_time = datetime.now()
        context_lock = threading.Lock()
        try:
            for level in workflow.get_execution_order():
                result = self._execute_level(
                    level, workflow, context, task_results, context_lock, start_time
                )
                if result is not None:
                    return result
            return WorkflowResult(
                workflow_id=workflow.id,
                success=True,
                task_results=task_results,
                start_time=start_time,
                end_time=datetime.now(),
            )
        except Exception as e:
            return WorkflowResult(
                workflow_id=workflow.id,
                success=False,
                task_results=task_results,
                start_time=start_time,
                end_time=datetime.now(),
                error=str(e),
            )

    def _execute_level(
        self,
        level: list[TaskDefinition],
        workflow: WorkflowDefinition,
        context: dict[str, Any],
        task_results: dict[str, TaskResult],
        context_lock: threading.Lock,
        start_time: datetime,
    ) -> WorkflowResult | None:
        """Execute one parallelizable level. Returns a failure result or None on success."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self._execute_task, task, dict(context), task_results
                ): task
                for task in level
            }
            for future in as_completed(futures):
                task = futures[future]
                try:
                    result = future.result()
                    with context_lock:
                        task_results[task.id] = result
                        if result.state == TaskState.COMPLETED:
                            context[task.id] = result.output
                            context[task.name] = result.output
                    if result.state == TaskState.FAILED:
                        for f in futures:
                            f.cancel()
                        return WorkflowResult(
                            workflow_id=workflow.id,
                            success=False,
                            task_results=task_results,
                            start_time=start_time,
                            end_time=datetime.now(),
                            error=f"Task {task.name} failed",
                        )
                except Exception as e:
                    task_results[task.id] = TaskResult(
                        task_id=task.id, state=TaskState.FAILED, error=str(e)
                    )
        return None

    def _execute_task(
        self,
        task: TaskDefinition,
        context: dict[str, Any],
        previous_results: dict[str, TaskResult],
    ) -> TaskResult:
        if task.condition and not task.condition(context):
            return TaskResult(task_id=task.id, state=TaskState.SKIPPED)
        attempts = 0
        max_attempts = task.retries + 1
        start_time = datetime.now()
        while attempts < max_attempts:
            attempts += 1
            start_time = datetime.now()
            try:
                output = task.action(context) if task.action else None
                return TaskResult(
                    task_id=task.id,
                    state=TaskState.COMPLETED,
                    output=output,
                    start_time=start_time,
                    end_time=datetime.now(),
                    attempts=attempts,
                )
            except Exception as e:
                if attempts < max_attempts:
                    time.sleep(task.retry_delay)
                else:
                    return TaskResult(
                        task_id=task.id,
                        state=TaskState.FAILED,
                        error=str(e),
                        start_time=start_time,
                        end_time=datetime.now(),
                        attempts=attempts,
                    )
        return TaskResult(task_id=task.id, state=TaskState.FAILED)

    async def execute_async(
        self,
        workflow: WorkflowDefinition,
        initial_context: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute, workflow, initial_context)
