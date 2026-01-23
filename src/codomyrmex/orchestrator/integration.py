"""Integration utilities for thin orchestration.

This module provides integration between the thin orchestrator and
other Codomyrmex modules like CI/CD, logistics, and agents.
"""

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from codomyrmex.logging_monitoring import get_logger

from .thin import run, shell, pipe, batch, chain_scripts, workflow, Steps
from .workflow import Workflow, Task, TaskStatus, RetryPolicy

logger = get_logger(__name__)

__all__ = [
    "OrchestratorBridge",
    "CICDBridge",
    "AgentOrchestrator",
    "create_pipeline_workflow",
    "run_ci_stage",
    "run_agent_task",
]


@dataclass
class StageConfig:
    """Configuration for a CI/CD stage."""
    name: str
    commands: List[str]
    parallel: bool = True
    allow_failure: bool = False
    timeout: int = 300
    retry: int = 0
    environment: Dict[str, str] = field(default_factory=dict)
    condition: Optional[Callable[[Dict], bool]] = None


@dataclass
class PipelineConfig:
    """Configuration for a CI/CD pipeline."""
    name: str
    stages: List[StageConfig]
    variables: Dict[str, str] = field(default_factory=dict)
    timeout: int = 3600
    fail_fast: bool = True


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

    def create_session(self, **kwargs) -> Optional[str]:
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

    async def execute_workflow(
        self,
        workflow_name: str,
        **params
    ) -> Dict[str, Any]:
        """Execute a logistics workflow via thin orchestration.

        Args:
            workflow_name: Name of workflow to execute
            **params: Workflow parameters

        Returns:
            Execution result
        """
        if self.engine:
            return self.engine.execute_workflow(
                workflow_name,
                session_id=self._session_id,
                **params
            )
        return {"success": False, "error": "Engine not available"}

    def run_quick(
        self,
        target: Union[str, Path],
        timeout: int = 60,
        **kwargs
    ) -> Dict[str, Any]:
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


class CICDBridge:
    """Bridge between thin orchestrator and CI/CD pipeline manager."""

    def __init__(self, workspace_dir: Optional[str] = None):
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
                from codomyrmex.ci_cd_automation.pipeline_manager import PipelineManager
                self._manager = PipelineManager(workspace_dir=self._workspace_dir)
            except ImportError:
                logger.warning("CI/CD automation not available")
        return self._manager

    def create_workflow_from_pipeline(
        self,
        pipeline_config: Union[PipelineConfig, Dict[str, Any]]
    ) -> Workflow:
        """Create a thin workflow from pipeline config.

        Args:
            pipeline_config: Pipeline configuration

        Returns:
            Workflow instance
        """
        if isinstance(pipeline_config, dict):
            pipeline_config = PipelineConfig(
                name=pipeline_config.get("name", "pipeline"),
                stages=[
                    StageConfig(**stage) for stage in pipeline_config.get("stages", [])
                ],
                variables=pipeline_config.get("variables", {}),
                timeout=pipeline_config.get("timeout", 3600),
                fail_fast=pipeline_config.get("fail_fast", True)
            )

        wf = Workflow(
            name=pipeline_config.name,
            timeout=pipeline_config.timeout,
            fail_fast=pipeline_config.fail_fast
        )

        prev_stages = []
        for stage_config in pipeline_config.stages:
            # Create task for each stage
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
                condition=stage_config.condition
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
        async def stage_action(_task_results: dict = None) -> Dict[str, Any]:
            results = []
            overall_success = True

            for cmd in stage_config.commands:
                result = shell(
                    cmd,
                    timeout=stage_config.timeout // max(len(stage_config.commands), 1),
                    env=stage_config.environment
                )
                results.append(result)

                if not result["success"] and not stage_config.allow_failure:
                    overall_success = False
                    break

            return {
                "success": overall_success,
                "stage": stage_config.name,
                "commands_executed": len(results),
                "results": results
            }

        return stage_action

    async def run_stage(
        self,
        stage_config: StageConfig,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
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


class AgentOrchestrator:
    """Orchestrator for agent tasks."""

    def __init__(self):
        """Initialize agent orchestrator."""
        self._agents: Dict[str, Any] = {}

    def register_agent(self, name: str, agent: Any):
        """Register an agent.

        Args:
            name: Agent name
            agent: Agent instance
        """
        self._agents[name] = agent

    def get_agent(self, name: str) -> Optional[Any]:
        """Get registered agent.

        Args:
            name: Agent name

        Returns:
            Agent instance if found
        """
        return self._agents.get(name)

    async def run_agent_task(
        self,
        agent_name: str,
        task: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Run a task using an agent.

        Args:
            agent_name: Name of agent to use
            task: Task to execute
            **kwargs: Task parameters

        Returns:
            Task result
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return {
                "success": False,
                "error": f"Agent '{agent_name}' not found"
            }

        try:
            # Try different agent interfaces
            if hasattr(agent, "execute"):
                result = await agent.execute(task, **kwargs)
            elif hasattr(agent, "run"):
                result = await agent.run(task, **kwargs)
            elif hasattr(agent, "__call__"):
                result = await agent(task, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Agent '{agent_name}' has no execute method"
                }

            return {
                "success": True,
                "agent": agent_name,
                "result": result
            }

        except Exception as e:
            return {
                "success": False,
                "agent": agent_name,
                "error": str(e)
            }

    def create_agent_workflow(
        self,
        tasks: List[Dict[str, Any]],
        name: str = "agent_workflow"
    ) -> Workflow:
        """Create a workflow from agent tasks.

        Args:
            tasks: List of task definitions
            name: Workflow name

        Returns:
            Workflow instance
        """
        wf = Workflow(name=name)

        for task_def in tasks:
            task_name = task_def.get("name", f"task_{len(wf.tasks)}")
            agent_name = task_def.get("agent")
            task_content = task_def.get("task", "")
            dependencies = task_def.get("depends_on", [])
            timeout = task_def.get("timeout", 300)

            async def agent_action(
                _task_results: dict = None,
                _agent=agent_name,
                _task=task_content,
                _kwargs=task_def.get("kwargs", {})
            ) -> Dict[str, Any]:
                return await self.run_agent_task(_agent, _task, **_kwargs)

            wf.add_task(
                name=task_name,
                action=agent_action,
                dependencies=dependencies,
                timeout=timeout
            )

        return wf


def create_pipeline_workflow(
    stages: List[Dict[str, Any]],
    name: str = "pipeline",
    fail_fast: bool = True
) -> Workflow:
    """Create a workflow from pipeline stages.

    Args:
        stages: List of stage configurations
        name: Pipeline name
        fail_fast: Stop on first failure

    Returns:
        Workflow instance
    """
    bridge = CICDBridge()
    config = PipelineConfig(
        name=name,
        stages=[StageConfig(**s) for s in stages],
        fail_fast=fail_fast
    )
    return bridge.create_workflow_from_pipeline(config)


async def run_ci_stage(
    name: str,
    commands: List[str],
    timeout: int = 300,
    env: Optional[Dict[str, str]] = None,
    allow_failure: bool = False
) -> Dict[str, Any]:
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
        allow_failure=allow_failure
    )
    return await bridge.run_stage(stage)


async def run_agent_task(
    agent_name: str,
    task: str,
    orchestrator: Optional[AgentOrchestrator] = None,
    **kwargs
) -> Dict[str, Any]:
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
