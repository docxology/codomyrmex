"""Sequential workflow execution engine."""

import asyncio
import time
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


class SequentialEngine(ExecutionEngine):
    """Executes tasks sequentially in dependency order."""

    def __init__(self, max_retries: int = 3) -> None:
        self.max_retries = max_retries

    def execute(
        self,
        workflow: WorkflowDefinition,
        initial_context: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        context = initial_context or {}
        task_results: dict[str, TaskResult] = {}
        start_time = datetime.now()
        try:
            for level in workflow.get_execution_order():
                for task in level:
                    result = self._execute_task(task, context, task_results)
                    task_results[task.id] = result
                    if result.state == TaskState.FAILED:
                        return WorkflowResult(
                            workflow_id=workflow.id,
                            success=False,
                            task_results=task_results,
                            start_time=start_time,
                            end_time=datetime.now(),
                            error=f"Task {task.name} failed: {result.error}",
                        )
                    context[task.id] = result.output
                    context[task.name] = result.output
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
        last_error = None
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
                last_error = str(e)
                if attempts < max_attempts:
                    time.sleep(task.retry_delay)
        return TaskResult(
            task_id=task.id,
            state=TaskState.FAILED,
            error=last_error,
            start_time=start_time,
            end_time=datetime.now(),
            attempts=attempts,
        )

    async def execute_async(
        self,
        workflow: WorkflowDefinition,
        initial_context: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute, workflow, initial_context)
