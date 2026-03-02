"""
Workflow Runner

Orchestrates workflow test execution.
"""

from datetime import datetime
from typing import Any

from .executors import (
    AssertionExecutor,
    ScriptExecutor,
    StepExecutor,
    WaitExecutor,
)
from .models import (
    StepResult,
    StepStatus,
    Workflow,
    WorkflowResult,
    WorkflowStep,
    WorkflowStepType,
)


class WorkflowRunner:
    """
    Runs workflow tests.

    Usage:
        runner = WorkflowRunner()

        workflow = Workflow(id="test", name="API Test")
        workflow.add_step(WorkflowStep(
            id="check",
            name="Check response",
            step_type=WorkflowStepType.ASSERTION,
            config={"type": "equals", "actual": 200, "expected": 200},
        ))

        result = runner.run(workflow)
        print(f"Pass rate: {result.pass_rate:.1%}")
    """

    def __init__(self):
        self._executors: dict[WorkflowStepType, StepExecutor] = {
            WorkflowStepType.ASSERTION: AssertionExecutor(),
            WorkflowStepType.WAIT: WaitExecutor(),
            WorkflowStepType.SCRIPT: ScriptExecutor(),
        }

    def register_executor(self, step_type: WorkflowStepType, executor: StepExecutor) -> None:
        """Register a step executor."""
        self._executors[step_type] = executor

    def run(
        self,
        workflow: Workflow,
        initial_context: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        """
        Run a workflow.

        Args:
            workflow: The workflow to run
            initial_context: Initial context variables

        Returns:
            WorkflowResult with all step results
        """
        context = dict(workflow.variables)
        if initial_context:
            context.update(initial_context)

        result = WorkflowResult(
            workflow_id=workflow.id,
            status=StepStatus.RUNNING,
        )

        all_passed = True

        for step in workflow.steps:
            step_result = self._run_step(step, context)
            result.step_results.append(step_result)

            # Store output in context
            if step_result.output:
                context[f"step_{step.id}"] = step_result.output

            if not step_result.passed:
                all_passed = False
                if step_result.status == StepStatus.ERROR:
                    break

        result.status = StepStatus.PASSED if all_passed else StepStatus.FAILED
        result.completed_at = datetime.now()

        return result

    def _run_step(self, step: WorkflowStep, context: dict[str, Any]) -> StepResult:
        """Run a single step with retries."""
        executor = self._executors.get(step.step_type)

        if not executor:
            return StepResult(
                step_id=step.id,
                status=StepStatus.ERROR,
                error=f"No executor for step type: {step.step_type}",
            )

        last_result = None
        for attempt in range(step.retry_count + 1):
            last_result = executor.execute(step, context)
            last_result.retries = attempt

            if last_result.passed:
                break

        return last_result
