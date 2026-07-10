"""Integration utilities for thin orchestration.

This module provides integration between the thin orchestrator and
other Codomyrmex modules like CI/CD, logistics, and agents.

The bulk of the implementation lives in focused submodules:
    - :mod:`._cicd_bridge` — ``StageConfig``, ``PipelineConfig``, ``CICDBridge``
    - :mod:`._agent_orchestrator` — ``AgentOrchestrator``

This file re-exports the public surface and provides the thin
``OrchestratorBridge``, convenience functions (``create_pipeline_workflow``,
``run_ci_stage``, ``run_agent_task``).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from codomyrmex.logging_monitoring import get_logger

from ._agent_orchestrator import AgentOrchestrator
from ._cicd_bridge import CICDBridge, PipelineConfig, StageConfig
from .thin import Steps, run, workflow

if TYPE_CHECKING:
    from .workflows.workflow import Workflow

logger = get_logger(__name__)

__all__ = [
    "AgentOrchestrator",
    "CICDBridge",
    "OrchestratorBridge",
    "PipelineConfig",
    "StageConfig",
    "create_pipeline_workflow",
    "run_agent_task",
    "run_ci_stage",
]


class OrchestratorBridge:
    """Bridge between thin orchestrator and logistics orchestration engine."""

    def __init__(self, engine=None):
        """Initialize bridge.

        Args:
            engine: Optional OrchestrationEngine instance
        """
        self._engine = engine
        self._session_id = None

    @property
    def engine(self):
        """Get or create orchestration engine."""
        if self._engine is None:
            try:
                from codomyrmex.logistics.orchestration import get_orchestration_engine

                self._engine = get_orchestration_engine()
            except ImportError:
                logger.warning("Logistics orchestration not available")
        return self._engine

    def create_session(self, **kwargs) -> str | None:
        """Create an orchestration session.

        Args:
            **kwargs: Session configuration

        Returns:
            Session ID if successful
        """
        if self.engine:
            self._session_id = self.engine.create_session(**kwargs)
            return self._session_id
        return None

    def close_session(self) -> bool:
        """Close current session."""
        if self.engine and self._session_id:
            result = self.engine.close_session(self._session_id)
            self._session_id = None
            return result
        return False

    async def execute_workflow(self, workflow_name: str, **params) -> dict[str, Any]:
        """Execute a logistics workflow via thin orchestration.

        Args:
            workflow_name: Name of workflow to execute
            **params: Workflow parameters

        Returns:
            Execution result
        """
        if self.engine:
            return self.engine.execute_workflow(
                workflow_name, session_id=self._session_id, **params
            )
        return {"success": False, "error": "Engine not available"}

    def run_quick(
        self, target: str | Path, timeout: int = 60, **kwargs
    ) -> dict[str, Any]:
        """Quick run using thin orchestration.

        Args:
            target: Script path or command
            timeout: Execution timeout
            **kwargs: Additional arguments

        Returns:
            Execution result
        """
        return run(target, timeout=timeout, **kwargs)

    def create_workflow(self, name: str = "workflow") -> Steps:
        """Create a thin workflow builder.

        Args:
            name: Workflow name

        Returns:
            Steps builder instance
        """
        return workflow(name)


def create_pipeline_workflow(
    stages: list[dict[str, Any]], name: str = "pipeline", fail_fast: bool = True
) -> Workflow:
    """Create a workflow from pipeline stages.

    Args:
        stages: list of stage configurations
        name: Pipeline name
        fail_fast: Stop on first failure

    Returns:
        Workflow instance
    """
    bridge = CICDBridge()
    config = PipelineConfig(
        name=name, stages=[StageConfig(**s) for s in stages], fail_fast=fail_fast
    )
    return bridge.create_workflow_from_pipeline(config)


async def run_ci_stage(
    name: str,
    commands: list[str],
    timeout: int = 300,
    env: dict[str, str] | None = None,
    allow_failure: bool = False,
) -> dict[str, Any]:
    """Run a CI/CD stage.

    Args:
        name: Stage name
        commands: Commands to execute
        timeout: Stage timeout
        env: Environment variables
        allow_failure: Allow stage to fail

    Returns:
        Stage result
    """
    bridge = CICDBridge()
    stage = StageConfig(
        name=name,
        commands=commands,
        timeout=timeout,
        environment=env or {},
        allow_failure=allow_failure,
    )
    return await bridge.run_stage(stage)


async def run_agent_task(
    agent_name: str, task: str, orchestrator: AgentOrchestrator | None = None, **kwargs
) -> dict[str, Any]:
    """Run a task using an agent.

    Args:
        agent_name: Name of agent
        task: Task to execute
        orchestrator: Optional orchestrator instance
        **kwargs: Task parameters

    Returns:
        Task result
    """
    if orchestrator is None:
        orchestrator = AgentOrchestrator()
    return await orchestrator.run_agent_task(agent_name, task, **kwargs)
