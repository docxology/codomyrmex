"""CI/CD pipeline bridge for thin orchestration.

Provides ``StageConfig``, ``PipelineConfig``, and the ``CICDBridge``
class which bridges the thin orchestrator and the CI/CD pipeline
manager, converting pipeline configurations into executable
:class:`~codomyrmex.orchestrator.workflows.workflow.Workflow` instances.

These were extracted from ``integration.py`` to keep each module focused.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from ._shell_exec import shell
from .workflows.workflow import RetryPolicy, Workflow

logger = get_logger(__name__)

__all__ = [
    "CICDBridge",
    "PipelineConfig",
    "StageConfig",
]


@dataclass
class StageConfig:
    """Configuration for a CI/CD stage."""

    name: str
    commands: list[str]
    parallel: bool = True
    allow_failure: bool = False
    timeout: int = 300
    retry: int = 0
    environment: dict[str, str] = field(default_factory=dict)
    condition: Callable[[dict], bool] | None = None


@dataclass
class PipelineConfig:
    """Configuration for a CI/CD pipeline."""

    name: str
    stages: list[StageConfig]
    variables: dict[str, str] = field(default_factory=dict)
    timeout: int = 3600
    fail_fast: bool = True


class CICDBridge:
    """Bridge between thin orchestrator and CI/CD pipeline manager."""

    def __init__(self, workspace_dir: str | None = None):
        """Initialize CI/CD bridge.

        Args:
            workspace_dir: Directory for CI/CD workspaces
        """
        self._workspace_dir = workspace_dir
        self._manager = None

    @property
    def manager(self):
        """Get or create pipeline manager."""
        if self._manager is None:
            try:
                from codomyrmex.ci_cd_automation.pipeline import PipelineManager

                self._manager = PipelineManager(workspace_dir=self._workspace_dir)
            except ImportError:
                logger.warning("CI/CD automation not available")
        return self._manager

    def _normalize_pipeline_config(
        self, pipeline_config: PipelineConfig | dict[str, Any]
    ) -> PipelineConfig:
        """Coerce dict to PipelineConfig if needed."""
        if isinstance(pipeline_config, dict):
            return PipelineConfig(
                name=pipeline_config.get("name", "pipeline"),  # type: ignore[attr-defined]
                stages=[StageConfig(**s) for s in pipeline_config.get("stages", [])],  # type: ignore[arg-type]
                variables=pipeline_config.get("variables", {}),  # type: ignore[attr-defined]
                timeout=pipeline_config.get("timeout", 3600),  # type: ignore[attr-defined]
                fail_fast=pipeline_config.get("fail_fast", True),  # type: ignore[attr-defined]
            )
        return pipeline_config

    def create_workflow_from_pipeline(
        self, pipeline_config: PipelineConfig | dict[str, Any]
    ) -> Workflow:
        """Create a thin workflow from pipeline config.

        Args:
            pipeline_config: Pipeline configuration

        Returns:
            Workflow instance
        """
        pipeline_config = self._normalize_pipeline_config(pipeline_config)

        wf = Workflow(
            name=pipeline_config.name,
            timeout=pipeline_config.timeout,
            fail_fast=pipeline_config.fail_fast,
        )

        prev_stages: list[str] = []
        for stage_config in pipeline_config.stages:
            stage_action = self._create_stage_action(stage_config)
            retry_policy = None
            if stage_config.retry > 0:
                retry_policy = RetryPolicy(max_attempts=stage_config.retry + 1)

            wf.add_task(
                name=stage_config.name,
                action=stage_action,
                dependencies=prev_stages.copy() if not stage_config.parallel else [],
                timeout=stage_config.timeout,
                retry_policy=retry_policy,
                condition=stage_config.condition,
            )

            if not stage_config.parallel:
                prev_stages = [stage_config.name]
            else:
                prev_stages.append(stage_config.name)

        return wf

    def _create_stage_action(self, stage_config: StageConfig) -> Callable:
        """Create action function for a stage.

        Args:
            stage_config: Stage configuration

        Returns:
            Async action function
        """

        async def stage_action(_task_results: dict | None = None) -> dict[str, Any]:
            results = []
            overall_success = True

            for cmd in stage_config.commands:
                result = shell(
                    cmd,
                    timeout=stage_config.timeout // max(len(stage_config.commands), 1),
                    env=stage_config.environment,
                )
                results.append(result)

                if not result["success"] and not stage_config.allow_failure:
                    overall_success = False
                    break

            return {
                "success": overall_success,
                "stage": stage_config.name,
                "commands_executed": len(results),
                "results": results,
            }

        return stage_action

    async def run_stage(
        self, stage_config: StageConfig, env: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Run a single CI/CD stage.

        Args:
            stage_config: Stage configuration
            env: Additional environment variables

        Returns:
            Stage result
        """
        if env:
            stage_config.environment.update(env)

        action = self._create_stage_action(stage_config)
        return await action()
