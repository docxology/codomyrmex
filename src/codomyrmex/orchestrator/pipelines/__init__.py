"""
Orchestrator Pipelines Module

Pipeline definitions, stages, and execution management.
"""

__version__ = "0.1.0"

import concurrent.futures
import threading
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

T = TypeVar('T')


class StageStatus(Enum):
    """Status of a pipeline stage."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class PipelineStatus(Enum):
    """Status of a pipeline."""
    CREATED = "created"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StageResult:
    """Result of a stage execution."""
    stage_id: str
    status: StageStatus
    output: Any = None
    error: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None

    @property
    def duration_ms(self) -> float:
        """Get execution duration in milliseconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0

    @property
    def is_success(self) -> bool:
        """is Success ."""
        return self.status == StageStatus.SUCCESS


@dataclass
class PipelineResult:
    """Result of a pipeline execution."""
    pipeline_id: str
    status: PipelineStatus
    stages: list[StageResult] = field(default_factory=list)
    start_time: datetime | None = None
    end_time: datetime | None = None

    @property
    def duration_ms(self) -> float:
        """Get total execution duration."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0

    @property
    def successful_stages(self) -> int:
        """successful Stages ."""
        return sum(1 for s in self.stages if s.is_success)

    @property
    def failed_stages(self) -> int:
        """failed Stages ."""
        return sum(1 for s in self.stages if s.status == StageStatus.FAILED)


class Stage(ABC):
    """Base class for pipeline stages."""

    def __init__(
        self,
        stage_id: str,
        name: str | None = None,
        depends_on: list[str] | None = None,
        retry_count: int = 0,
        timeout_s: float | None = None,
    ):
        """Initialize this instance."""
        self.stage_id = stage_id
        self.name = name or stage_id
        self.depends_on = depends_on or []
        self.retry_count = retry_count
        self.timeout_s = timeout_s

    @abstractmethod
    def execute(self, context: dict[str, Any]) -> Any:
        """Execute the stage."""
        pass

    def on_success(self, result: StageResult, context: dict[str, Any]) -> None:
        """Called on successful execution."""
        return None  # Optional hook — subclass may override

    def on_failure(self, result: StageResult, context: dict[str, Any]) -> None:
        """Called on failed execution."""
        return None  # Optional hook — subclass may override


class FunctionStage(Stage):
    """Stage that executes a function."""

    def __init__(
        self,
        stage_id: str,
        func: Callable[[dict[str, Any]], Any],
        **kwargs,
    ):
        """Initialize this instance."""
        super().__init__(stage_id, **kwargs)
        self._func = func

    def execute(self, context: dict[str, Any]) -> Any:
        """Execute the operation."""
        return self._func(context)


class ConditionalStage(Stage):
    """Stage that executes conditionally."""

    def __init__(
        self,
        stage_id: str,
        condition: Callable[[dict[str, Any]], bool],
        stage: Stage,
        **kwargs,
    ):
        """Initialize this instance."""
        super().__init__(stage_id, **kwargs)
        self.condition = condition
        self.stage = stage

    def execute(self, context: dict[str, Any]) -> Any:
        """Execute the operation."""
        if self.condition(context):
            return self.stage.execute(context)
        return None


class ParallelStage(Stage):
    """Stage that executes multiple stages in parallel."""

    def __init__(
        self,
        stage_id: str,
        stages: list[Stage],
        max_workers: int = 4,
        **kwargs,
    ):
        """Initialize this instance."""
        super().__init__(stage_id, **kwargs)
        self.stages = stages
        self.max_workers = max_workers

    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute the operation."""
        results = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(stage.execute, context): stage.stage_id
                for stage in self.stages
            }

            for future in concurrent.futures.as_completed(futures):
                stage_id = futures[future]
                try:
                    results[stage_id] = future.result()
                except Exception as e:
                    results[stage_id] = {"error": str(e)}

        return results


class Pipeline:
    """
    Pipeline for orchestrating multi-stage workflows.

    Usage:
        pipeline = Pipeline("data_processing")

        pipeline.add_stage(FunctionStage("extract", extract_data))
        pipeline.add_stage(FunctionStage("transform", transform_data, depends_on=["extract"]))
        pipeline.add_stage(FunctionStage("load", load_data, depends_on=["transform"]))

        result = pipeline.run()

        if result.status == PipelineStatus.SUCCESS:
            print("Pipeline completed successfully")
    """

    def __init__(
        self,
        pipeline_id: str | None = None,
        name: str | None = None,
        fail_fast: bool = True,
    ):
        """Initialize this instance."""
        self.pipeline_id = pipeline_id or str(uuid.uuid4())[:8]
        self.name = name or self.pipeline_id
        self.fail_fast = fail_fast
        self._stages: dict[str, Stage] = {}
        self._order: list[str] = []
        self._context: dict[str, Any] = {}

    def add_stage(self, stage: Stage) -> "Pipeline":
        """Add a stage to the pipeline."""
        self._stages[stage.stage_id] = stage
        return self

    def set_context(self, key: str, value: Any) -> "Pipeline":
        """Set a context value."""
        self._context[key] = value
        return self

    def _resolve_order(self) -> list[str]:
        """Resolve stage execution order (topological sort)."""
        visited = set()
        order = []

        def visit(stage_id: str):
            """visit ."""
            if stage_id in visited:
                return
            visited.add(stage_id)

            stage = self._stages.get(stage_id)
            if stage:
                for dep in stage.depends_on:
                    visit(dep)
                order.append(stage_id)

        for stage_id in self._stages:
            visit(stage_id)

        return order

    def _execute_stage(
        self,
        stage: Stage,
        context: dict[str, Any],
    ) -> StageResult:
        """Execute a single stage with retries."""
        result = StageResult(stage_id=stage.stage_id, status=StageStatus.PENDING)

        for attempt in range(stage.retry_count + 1):
            result.start_time = datetime.now()

            try:
                output = stage.execute(context)
                result.output = output
                result.status = StageStatus.SUCCESS
                result.end_time = datetime.now()
                stage.on_success(result, context)
                return result

            except Exception as e:
                result.error = str(e)
                result.status = StageStatus.FAILED
                result.end_time = datetime.now()

                if attempt < stage.retry_count:
                    time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                else:
                    stage.on_failure(result, context)

        return result

    def run(self, initial_context: dict[str, Any] | None = None) -> PipelineResult:
        """
        Execute the pipeline.

        Args:
            initial_context: Initial context values

        Returns:
            PipelineResult with all stage results
        """
        context = self._context.copy()
        if initial_context:
            context.update(initial_context)

        result = PipelineResult(
            pipeline_id=self.pipeline_id,
            status=PipelineStatus.RUNNING,
            start_time=datetime.now(),
        )

        order = self._resolve_order()
        completed: dict[str, StageResult] = {}

        for stage_id in order:
            stage = self._stages.get(stage_id)
            if not stage:
                continue

            # Check dependencies
            deps_ok = all(
                dep in completed and completed[dep].is_success
                for dep in stage.depends_on
            )

            if not deps_ok:
                stage_result = StageResult(
                    stage_id=stage_id,
                    status=StageStatus.SKIPPED,
                    error="Dependencies not satisfied",
                )
            else:
                # Add dependency outputs to context
                for dep in stage.depends_on:
                    if dep in completed:
                        context[f"stage_{dep}_output"] = completed[dep].output

                stage_result = self._execute_stage(stage, context)

            completed[stage_id] = stage_result
            result.stages.append(stage_result)

            # Fail fast if configured
            if self.fail_fast and stage_result.status == StageStatus.FAILED:
                result.status = PipelineStatus.FAILED
                result.end_time = datetime.now()
                return result

        # Determine final status
        if any(s.status == StageStatus.FAILED for s in result.stages):
            result.status = PipelineStatus.FAILED
        else:
            result.status = PipelineStatus.SUCCESS

        result.end_time = datetime.now()
        return result


class PipelineBuilder:
    """
    Fluent builder for pipelines.

    Usage:
        pipeline = (PipelineBuilder("my_pipeline")
            .stage("step1", lambda ctx: "result1")
            .stage("step2", lambda ctx: ctx["stage_step1_output"] + "_processed", depends_on=["step1"])
            .stage("step3", lambda ctx: "final", depends_on=["step2"])
            .build())
    """

    def __init__(self, name: str):
        """Initialize this instance."""
        self._pipeline = Pipeline(name=name)

    def stage(
        self,
        stage_id: str,
        func: Callable[[dict[str, Any]], Any],
        depends_on: list[str] | None = None,
        retry_count: int = 0,
    ) -> "PipelineBuilder":
        """Add a function stage."""
        self._pipeline.add_stage(FunctionStage(
            stage_id=stage_id,
            func=func,
            depends_on=depends_on,
            retry_count=retry_count,
        ))
        return self

    def parallel(
        self,
        stage_id: str,
        stages: list[Stage],
        depends_on: list[str] | None = None,
    ) -> "PipelineBuilder":
        """Add a parallel stage."""
        self._pipeline.add_stage(ParallelStage(
            stage_id=stage_id,
            stages=stages,
            depends_on=depends_on,
        ))
        return self

    def context(self, key: str, value: Any) -> "PipelineBuilder":
        """Set context value."""
        self._pipeline.set_context(key, value)
        return self

    def build(self) -> Pipeline:
        """Build the pipeline."""
        return self._pipeline


__all__ = [
    # Enums
    "StageStatus",
    "PipelineStatus",
    # Data classes
    "StageResult",
    "PipelineResult",
    # Stages
    "Stage",
    "FunctionStage",
    "ConditionalStage",
    "ParallelStage",
    # Pipeline
    "Pipeline",
    "PipelineBuilder",
]
