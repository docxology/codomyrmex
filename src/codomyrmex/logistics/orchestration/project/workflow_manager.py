"""Workflow Manager for Codomyrmex Project Orchestration.

This module provides comprehensive workflow management capabilities for the Codomyrmex
project orchestration system. It handles the creation, listing, execution, and management
of workflows that coordinate multiple Codomyrmex modules.
"""

import json
import uuid
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .task_orchestrator import Task, TaskOrchestrator, TaskStatus, get_task_orchestrator
from .workflow_dag import WorkflowDAG

logger = get_logger(__name__)


class WorkflowStatus(Enum):
    """Status of a workflow."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """Definition of a step in a workflow."""

    name: str
    module: str
    action: str
    parameters: dict[str, Any] = field(default_factory=dict)
    run_if: str | None = None  # Condition expression
    dependencies: list[str] = field(default_factory=list)  # Step names
    required: bool = True
    timeout: float | None = None
    retry_count: int = 0


@dataclass
class WorkflowExecution:
    """Track execution of a workflow."""

    workflow_name: str
    execution_id: str
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: WorkflowStatus = WorkflowStatus.PENDING
    step_results: dict[str, Any] = field(default_factory=dict)
    end_time: datetime | None = None
    error: str | None = None

    @property
    def duration(self) -> float | None:
        """Duration."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def success(self) -> bool:
        """Return True if the workflow completed successfully."""
        return self.status == WorkflowStatus.COMPLETED


class WorkflowManager:
    """Manages workflow definitions and execution."""

    def __init__(
        self,
        persistence_dir: Path | None = None,
        config_dir: Path | None = None,
        task_orchestrator: TaskOrchestrator | None = None,
    ):
        """Initialize the workflow manager.

        Args:
            persistence_dir: Directory for workflow execution persistence data.
            config_dir: Directory containing workflow definition JSON files.
                        Defaults to ``config/workflows/production`` relative to cwd.
            task_orchestrator: Orchestrator that runs workflow steps. Defaults to
                the global task orchestrator.
        """
        self.workflows: dict[str, list[WorkflowStep]] = {}
        self.executions: dict[str, WorkflowExecution] = {}
        self.task_orchestrator = (
            task_orchestrator
            if task_orchestrator is not None
            else get_task_orchestrator()
        )
        self.persistence_dir = persistence_dir or Path(".workflows")
        self.persistence_dir.mkdir(parents=True, exist_ok=True)

        # Config directory for workflow JSON definitions
        self.config_dir: Path = config_dir or (
            Path.cwd() / "config" / "workflows" / "production"
        )
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load any workflow definitions found in config_dir
        self._load_workflows_from_config()

    def create_workflow(self, name: str, steps: list[WorkflowStep]) -> bool:
        """Create and register a new workflow."""
        if name in self.workflows:
            logger.warning("Overwriting existing workflow: %s", name)
        self.workflows[name] = steps
        logger.info("Created workflow: %s with %s steps", name, len(steps))
        return True

    def get_workflow(self, name: str) -> list[WorkflowStep] | None:
        """Get a workflow definition."""
        return self.workflows.get(name)

    def list_workflows(self) -> list[str]:
        """list available workflows."""
        return list(self.workflows.keys())

    def execute_workflow(self, name: str, **params) -> WorkflowExecution:
        """Execute a registered workflow and block until it finishes.

        See :meth:`execute_steps` for the execution semantics. ``params`` are
        merged over every step's own parameters.

        Raises:
            ValueError: If the workflow is not registered or its dependencies
                are invalid (missing step, cycle, duplicate step name).
            NotImplementedError: If a step uses a ``run_if`` condition.
        """
        steps = self.workflows.get(name)
        if steps is None:
            raise ValueError(f"Workflow not found: {name}")
        return self.execute_steps(name, steps, params)

    def execute_steps(
        self,
        workflow_name: str,
        steps: Sequence[WorkflowStep],
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> WorkflowExecution:
        """Run ``steps`` through the task orchestrator and wait for the outcome.

        Steps are submitted in topological order of their ``dependencies``
        (step names), whatever order they are listed in, so every dependency is
        enforced. Independent steps run concurrently. A step whose dependency
        failed is failed without running; other independent steps still run.

        Args:
            workflow_name: Name recorded on the execution.
            steps: Step definitions.
            params: Workflow-level parameters merged over each step's
                ``parameters`` and passed to the step's action as keyword
                arguments.
            timeout: Maximum seconds to wait for all steps. Unfinished steps
                are cancelled and the execution fails when it expires.
                ``None`` waits until every step has finished.

        Returns:
            The finished :class:`WorkflowExecution`: ``COMPLETED`` when every
            required step completed, otherwise ``FAILED`` with ``error``
            summarising the failed steps. ``step_results`` maps each step name
            to its task result dictionary and ``end_time`` is set.

        Raises:
            ValueError: If the step dependencies are invalid.
            NotImplementedError: If a step uses a ``run_if`` condition.
        """
        ordered_steps = self._order_steps(workflow_name, steps)
        workflow_params = dict(params or {})

        execution = WorkflowExecution(
            workflow_name=workflow_name, execution_id=str(uuid.uuid4())
        )
        self.executions[execution.execution_id] = execution
        execution.status = WorkflowStatus.RUNNING
        logger.info(
            "Starting workflow execution: %s (%s)",
            workflow_name,
            execution.execution_id,
        )

        step_tasks: dict[str, Task] = {}
        try:
            for step in ordered_steps:
                task = Task(
                    name=step.name,
                    module=step.module,
                    action=step.action,
                    parameters={**step.parameters, **workflow_params},
                    dependencies=[step_tasks[dep].id for dep in step.dependencies],
                    timeout=step.timeout,
                    retry_count=step.retry_count,
                )
                self.task_orchestrator.submit_task(task)
                step_tasks[step.name] = task

            finished = self.task_orchestrator.wait_for_tasks(
                [task.id for task in step_tasks.values()], timeout=timeout
            )
        except BaseException as exc:
            for task in step_tasks.values():
                self.task_orchestrator.cancel_task(task.id)
            execution.status = WorkflowStatus.FAILED
            execution.error = f"{type(exc).__name__}: {exc}"
            execution.end_time = datetime.now(UTC)
            logger.error("Workflow execution failed: %s", execution.error)
            raise

        failures: list[str] = []
        if not finished:
            unfinished = [
                step.name
                for step in ordered_steps
                if self.task_orchestrator.cancel_task(step_tasks[step.name].id)
            ]
            failures.append(
                f"timed out after {timeout}s; cancelled unfinished steps {unfinished}"
            )

        for step in steps:
            task = step_tasks[step.name]
            task_result = task.result
            execution.step_results[step.name] = (
                task_result.to_dict()
                if task_result is not None
                else {"status": task.status.value, "success": False}
            )
            if step.required and task.status != TaskStatus.COMPLETED:
                reason = task_result.error if task_result is not None else None
                failures.append(f"{step.name}: {reason or task.status.value}")

        execution.status = (
            WorkflowStatus.FAILED if failures else WorkflowStatus.COMPLETED
        )
        execution.error = "; ".join(failures) or None
        execution.end_time = datetime.now(UTC)
        logger.info(
            "Workflow execution %s (%s) finished: %s",
            workflow_name,
            execution.execution_id,
            execution.status.value,
        )
        return execution

    def _order_steps(
        self, workflow_name: str, steps: Sequence[WorkflowStep]
    ) -> list[WorkflowStep]:
        """Validate step dependencies and return the steps in execution order."""
        names = [step.name for step in steps]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            raise ValueError(
                f"Workflow '{workflow_name}' has duplicate step names: {duplicates}"
            )

        conditional = [step.name for step in steps if step.run_if]
        if conditional:
            raise NotImplementedError(
                f"Workflow '{workflow_name}': run_if conditions are not supported "
                f"(steps {conditional})"
            )

        dag = WorkflowDAG(
            [
                {
                    "name": step.name,
                    "module": step.module,
                    "action": step.action,
                    "dependencies": list(step.dependencies),
                }
                for step in steps
            ]
        )
        is_valid, errors = dag.validate_dag()
        if not is_valid:
            raise ValueError(
                f"Workflow '{workflow_name}' has invalid dependencies: "
                + "; ".join(errors)
            )

        by_name = {step.name: step for step in steps}
        return [by_name[name] for level in dag.get_execution_order() for name in level]

    # ------------------------------------------------------------------
    # Config-directory workflow loading
    # ------------------------------------------------------------------

    def _load_workflows_from_config(self) -> None:
        """Load workflow definitions from JSON files in ``self.config_dir``."""
        if not self.config_dir.exists():
            return

        for workflow_file in sorted(self.config_dir.glob("*.json")):
            try:
                with open(workflow_file) as f:
                    data = json.load(f)

                workflow_name = data.get("name", workflow_file.stem)
                raw_steps = data.get("steps", [])

                steps: list[WorkflowStep] = []
                for raw in raw_steps:
                    steps.append(
                        WorkflowStep(
                            name=raw.get("name", ""),
                            module=raw.get("module", ""),
                            action=raw.get("action", ""),
                            parameters=raw.get("parameters", {}),
                            dependencies=raw.get("dependencies", []),
                            timeout=raw.get("timeout"),
                            retry_count=raw.get("max_retries", 0),
                        )
                    )

                self.workflows[workflow_name] = steps
                logger.info(
                    "Loaded workflow '%s' from %s", workflow_name, workflow_file
                )
            except Exception as exc:
                logger.warning(
                    "Failed to load workflow from %s: %s", workflow_file, exc
                )

    # ------------------------------------------------------------------
    # DAG & dependency helpers
    # ------------------------------------------------------------------

    def create_workflow_dag(self, tasks: list[dict[str, Any]]) -> WorkflowDAG:
        """Create a :class:`WorkflowDAG` from a list of task dictionaries.

        Args:
            tasks: list of task dicts, each with at least ``name``, ``module``,
                   ``action``, and optionally ``dependencies``.

        Returns:
            A populated :class:`WorkflowDAG` instance.
        """
        return WorkflowDAG(tasks)

    def validate_workflow_dependencies(self, tasks: list[dict[str, Any]]) -> list[str]:
        """Validate that all task dependencies are satisfiable.

        Args:
            tasks: list of task dicts with ``name`` and ``dependencies`` keys.

        Returns:
            list of error strings. Empty list means valid.
        """
        from .parallel_executor import validate_workflow_dependencies

        return validate_workflow_dependencies(tasks)

    def get_workflow_execution_order(
        self, tasks: list[dict[str, Any]]
    ) -> list[list[str]]:
        """Get the topological execution order for a set of tasks.

        Args:
            tasks: list of task dicts (must include ``name`` and ``dependencies``).

        Returns:
            list of lists -- each inner list contains task names that can run
            in parallel at that level.
        """
        from .parallel_executor import get_workflow_execution_order

        return get_workflow_execution_order(tasks)

    def execute_parallel_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        """Execute a workflow using the :class:`ParallelExecutor`.

        Args:
            workflow: Dictionary with keys ``tasks`` (list of task dicts),
                      ``dependencies`` (dict mapping task name to list of dep names),
                      and optionally ``max_parallel`` (int).

        Returns:
            Result dictionary with ``status``, ``total_tasks``,
            ``completed_tasks``, ``failed_tasks``, and ``task_results``.
        """
        from .parallel_executor import ParallelExecutor

        tasks = workflow.get("tasks", [])
        dependencies = workflow.get("dependencies", {})
        max_parallel = workflow.get("max_parallel", 4)

        with ParallelExecutor(
            max_workers=max_parallel, actions=self.task_orchestrator.actions
        ) as executor:
            results = executor.execute_tasks(tasks, dependencies)

        completed_count = sum(
            1 for r in results.values() if r.status.value == "completed"
        )
        failed_count = sum(
            1
            for r in results.values()
            if r.status.value in ("failed", "timeout", "cancelled")
        )

        if failed_count == 0:
            status = "completed"
        elif completed_count > 0:
            status = "partial_failure"
        else:
            status = "failed"

        return {
            "status": status,
            "total_tasks": len(tasks),
            "completed_tasks": completed_count,
            "failed_tasks": failed_count,
            "task_results": {name: r.to_dict() for name, r in results.items()},
        }

    # ------------------------------------------------------------------

    def get_execution_status(self, execution_id: str) -> WorkflowExecution | None:
        """Get the status of a workflow execution."""
        return self.executions.get(execution_id)

    def get_performance_summary(self) -> dict[str, Any]:
        """Return aggregate execution counts and duration metrics."""
        executions = list(self.executions.values())
        return {
            "total_executions": len(executions),
            "successful_executions": sum(
                1 for e in executions if e.status == WorkflowStatus.COMPLETED
            ),
            "failed_executions": sum(
                1 for e in executions if e.status == WorkflowStatus.FAILED
            ),
            "running_executions": sum(
                1 for e in executions if e.status == WorkflowStatus.RUNNING
            ),
            "average_duration": sum(e.duration or 0 for e in executions)
            / max(1, len(executions)),
        }


# Global workflow manager instance
_workflow_manager = None


def get_workflow_manager() -> WorkflowManager:
    """Get the default workflow manager instance."""
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager()
    return _workflow_manager
