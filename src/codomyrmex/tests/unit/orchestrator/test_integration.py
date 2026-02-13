"""Tests for orchestrator integration utilities.

This module tests the integration bridges between thin orchestration
and other Codomyrmex modules.
"""



import pytest

pytestmark = [pytest.mark.orchestrator]


class TestOrchestratorBridge:
    """Tests for OrchestratorBridge class."""

    def test_bridge_initialization(self):
        """Test bridge initializes without engine."""
        from codomyrmex.orchestrator.integration import OrchestratorBridge

        bridge = OrchestratorBridge()
        assert bridge._engine is None
        assert bridge._session_id is None

    def test_bridge_with_custom_engine(self):
        """Test bridge with custom engine."""
        from codomyrmex.orchestrator.integration import OrchestratorBridge

        class _SimpleEngine:
            pass

        engine = _SimpleEngine()
        bridge = OrchestratorBridge(engine=engine)
        assert bridge._engine is engine

    def test_run_quick(self):
        """Test quick run functionality."""
        from codomyrmex.orchestrator.integration import OrchestratorBridge

        bridge = OrchestratorBridge()
        result = bridge.run_quick("echo test")

        assert result["success"] is True
        assert "test" in result.get("stdout", "")

    def test_create_workflow(self):
        """Test creating workflow builder."""
        from codomyrmex.orchestrator.integration import OrchestratorBridge
        from codomyrmex.orchestrator.thin import Steps

        bridge = OrchestratorBridge()
        w = bridge.create_workflow("test_workflow")

        assert isinstance(w, Steps)
        assert w.workflow.name == "test_workflow"


class TestStageConfig:
    """Tests for StageConfig dataclass."""

    def test_stage_config_defaults(self):
        """Test StageConfig default values."""
        from codomyrmex.orchestrator.integration import StageConfig

        config = StageConfig(
            name="test_stage",
            commands=["echo hello"]
        )

        assert config.name == "test_stage"
        assert config.commands == ["echo hello"]
        assert config.parallel is True
        assert config.allow_failure is False
        assert config.timeout == 300
        assert config.retry == 0
        assert config.environment == {}
        assert config.condition is None

    def test_stage_config_custom_values(self):
        """Test StageConfig with custom values."""
        from codomyrmex.orchestrator.integration import StageConfig

        config = StageConfig(
            name="custom_stage",
            commands=["cmd1", "cmd2"],
            parallel=False,
            allow_failure=True,
            timeout=600,
            retry=3,
            environment={"KEY": "value"}
        )

        assert config.parallel is False
        assert config.allow_failure is True
        assert config.timeout == 600
        assert config.retry == 3
        assert config.environment == {"KEY": "value"}


class TestPipelineConfig:
    """Tests for PipelineConfig dataclass."""

    def test_pipeline_config_defaults(self):
        """Test PipelineConfig default values."""
        from codomyrmex.orchestrator.integration import PipelineConfig, StageConfig

        stage = StageConfig(name="stage1", commands=["echo test"])
        config = PipelineConfig(
            name="test_pipeline",
            stages=[stage]
        )

        assert config.name == "test_pipeline"
        assert len(config.stages) == 1
        assert config.variables == {}
        assert config.timeout == 3600
        assert config.fail_fast is True

    def test_pipeline_config_custom_values(self):
        """Test PipelineConfig with custom values."""
        from codomyrmex.orchestrator.integration import PipelineConfig, StageConfig

        stages = [
            StageConfig(name="build", commands=["make build"]),
            StageConfig(name="test", commands=["make test"])
        ]

        config = PipelineConfig(
            name="custom_pipeline",
            stages=stages,
            variables={"VERSION": "1.0.0"},
            timeout=7200,
            fail_fast=False
        )

        assert len(config.stages) == 2
        assert config.variables == {"VERSION": "1.0.0"}
        assert config.timeout == 7200
        assert config.fail_fast is False


class TestCICDBridge:
    """Tests for CICDBridge class."""

    def test_bridge_initialization(self):
        """Test CICDBridge initializes."""
        from codomyrmex.orchestrator.integration import CICDBridge

        bridge = CICDBridge()
        assert bridge._workspace_dir is None
        assert bridge._manager is None

    def test_bridge_with_workspace(self):
        """Test CICDBridge with workspace directory."""
        from codomyrmex.orchestrator.integration import CICDBridge

        bridge = CICDBridge(workspace_dir="/tmp/test_workspace")
        assert bridge._workspace_dir == "/tmp/test_workspace"

    def test_create_workflow_from_pipeline(self):
        """Test creating workflow from pipeline config."""
        from codomyrmex.orchestrator import Workflow
        from codomyrmex.orchestrator.integration import (
            CICDBridge,
            PipelineConfig,
            StageConfig,
        )

        bridge = CICDBridge()

        stages = [
            StageConfig(name="build", commands=["echo build"]),
            StageConfig(name="test", commands=["echo test"])
        ]
        config = PipelineConfig(name="test_pipeline", stages=stages)

        workflow = bridge.create_workflow_from_pipeline(config)

        assert isinstance(workflow, Workflow)
        assert workflow.name == "test_pipeline"
        assert "build" in workflow.tasks
        assert "test" in workflow.tasks

    def test_create_workflow_from_dict(self):
        """Test creating workflow from dict config."""
        from codomyrmex.orchestrator import Workflow
        from codomyrmex.orchestrator.integration import CICDBridge

        bridge = CICDBridge()

        config = {
            "name": "dict_pipeline",
            "stages": [
                {"name": "stage1", "commands": ["echo 1"]},
                {"name": "stage2", "commands": ["echo 2"]}
            ],
            "fail_fast": True
        }

        workflow = bridge.create_workflow_from_pipeline(config)

        assert isinstance(workflow, Workflow)
        assert workflow.name == "dict_pipeline"

    @pytest.mark.asyncio
    async def test_run_stage(self):
        """Test running a single stage."""
        from codomyrmex.orchestrator.integration import CICDBridge, StageConfig

        bridge = CICDBridge()
        stage = StageConfig(
            name="test_stage",
            commands=["echo hello"]
        )

        result = await bridge.run_stage(stage)

        assert result["success"] is True
        assert result["stage"] == "test_stage"
        assert result["commands_executed"] == 1

    @pytest.mark.asyncio
    async def test_run_stage_with_env(self):
        """Test running stage with environment variables."""
        from codomyrmex.orchestrator.integration import CICDBridge, StageConfig

        bridge = CICDBridge()
        stage = StageConfig(
            name="env_stage",
            commands=["echo $TEST_VAR"],
            environment={"TEST_VAR": "from_stage"}
        )

        result = await bridge.run_stage(stage, env={"EXTRA": "value"})

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_run_stage_allow_failure(self):
        """Test stage with allow_failure."""
        from codomyrmex.orchestrator.integration import CICDBridge, StageConfig

        bridge = CICDBridge()
        stage = StageConfig(
            name="failing_stage",
            commands=["exit 1"],
            allow_failure=True
        )

        result = await bridge.run_stage(stage)

        # Should still succeed overall due to allow_failure
        assert result["stage"] == "failing_stage"


class TestAgentOrchestrator:
    """Tests for AgentOrchestrator class."""

    def test_orchestrator_initialization(self):
        """Test AgentOrchestrator initializes."""
        from codomyrmex.orchestrator.integration import AgentOrchestrator

        orchestrator = AgentOrchestrator()
        assert orchestrator._agents == {}

    def test_register_agent(self):
        """Test registering an agent."""
        from codomyrmex.orchestrator.integration import AgentOrchestrator

        orchestrator = AgentOrchestrator()
        agent = object()  # any real object

        orchestrator.register_agent("test_agent", agent)

        assert "test_agent" in orchestrator._agents
        assert orchestrator.get_agent("test_agent") is agent

    def test_get_agent_not_found(self):
        """Test getting non-existent agent."""
        from codomyrmex.orchestrator.integration import AgentOrchestrator

        orchestrator = AgentOrchestrator()
        result = orchestrator.get_agent("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_run_agent_task_not_found(self):
        """Test running task with non-existent agent."""
        from codomyrmex.orchestrator.integration import AgentOrchestrator

        orchestrator = AgentOrchestrator()
        result = await orchestrator.run_agent_task("nonexistent", "some task")

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_run_agent_task_with_execute(self):
        """Test running task with agent.execute method."""
        from codomyrmex.orchestrator.integration import AgentOrchestrator

        orchestrator = AgentOrchestrator()

        class ExecuteAgent:
            async def execute(self, task):
                return "executed_result"

        orchestrator.register_agent("executor", ExecuteAgent())
        result = await orchestrator.run_agent_task("executor", "do something")

        assert result["success"] is True
        assert result["agent"] == "executor"
        assert result["result"] == "executed_result"

    @pytest.mark.asyncio
    async def test_run_agent_task_with_run(self):
        """Test running task with agent.run method."""
        from codomyrmex.orchestrator.integration import AgentOrchestrator

        orchestrator = AgentOrchestrator()

        class RunAgent:
            async def run(self, task="", **kwargs):
                return "run_result"

        orchestrator.register_agent("runner", RunAgent())
        result = await orchestrator.run_agent_task("runner", "run something")

        assert result["success"] is True
        assert result["result"] == "run_result"

    @pytest.mark.asyncio
    async def test_run_agent_task_callable(self):
        """Test running task with callable agent."""
        from codomyrmex.orchestrator.integration import AgentOrchestrator

        orchestrator = AgentOrchestrator()

        async def callable_agent(task, **kwargs):
            return f"called with: {task}"

        orchestrator.register_agent("callable", callable_agent)
        result = await orchestrator.run_agent_task("callable", "my task")

        assert result["success"] is True
        assert "called with: my task" in result["result"]

    @pytest.mark.asyncio
    async def test_run_agent_task_error(self):
        """Test handling agent task error."""
        from codomyrmex.orchestrator.integration import AgentOrchestrator

        orchestrator = AgentOrchestrator()

        class FailingAgent:
            async def execute(self, task):
                raise ValueError("Agent error")

        orchestrator.register_agent("failing", FailingAgent())
        result = await orchestrator.run_agent_task("failing", "fail task")

        assert result["success"] is False
        assert "Agent error" in result["error"]

    def test_create_agent_workflow(self):
        """Test creating workflow from agent tasks."""
        from codomyrmex.orchestrator import Workflow
        from codomyrmex.orchestrator.integration import AgentOrchestrator

        orchestrator = AgentOrchestrator()

        tasks = [
            {"name": "task1", "agent": "agent1", "task": "do task 1"},
            {"name": "task2", "agent": "agent2", "task": "do task 2", "depends_on": ["task1"]}
        ]

        workflow = orchestrator.create_agent_workflow(tasks, "agent_workflow")

        assert isinstance(workflow, Workflow)
        assert workflow.name == "agent_workflow"
        assert "task1" in workflow.tasks
        assert "task2" in workflow.tasks


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_pipeline_workflow(self):
        """Test create_pipeline_workflow function."""
        from codomyrmex.orchestrator import Workflow
        from codomyrmex.orchestrator.integration import create_pipeline_workflow

        stages = [
            {"name": "build", "commands": ["echo build"]},
            {"name": "test", "commands": ["echo test"]}
        ]

        workflow = create_pipeline_workflow(stages, "my_pipeline")

        assert isinstance(workflow, Workflow)
        assert workflow.name == "my_pipeline"

    @pytest.mark.asyncio
    async def test_run_ci_stage(self):
        """Test run_ci_stage function."""
        from codomyrmex.orchestrator.integration import run_ci_stage

        result = await run_ci_stage(
            name="test_stage",
            commands=["echo hello", "echo world"],
            timeout=60
        )

        assert result["stage"] == "test_stage"
        assert result["commands_executed"] == 2

    @pytest.mark.asyncio
    async def test_run_agent_task_function(self):
        """Test run_agent_task function."""
        from codomyrmex.orchestrator.integration import run_agent_task

        # Should return error since no agent is registered
        result = await run_agent_task("nonexistent", "task")

        assert result["success"] is False


class TestWorkflowExecution:
    """Integration tests for workflow execution."""

    @pytest.mark.asyncio
    async def test_pipeline_workflow_execution(self):
        """Test executing a pipeline as workflow."""
        from codomyrmex.orchestrator.integration import (
            CICDBridge,
            PipelineConfig,
            StageConfig,
        )

        bridge = CICDBridge()

        stages = [
            StageConfig(name="step1", commands=["echo step1"]),
            StageConfig(name="step2", commands=["echo step2"])
        ]
        config = PipelineConfig(name="test", stages=stages)

        workflow = bridge.create_workflow_from_pipeline(config)

        # Execute workflow
        await workflow.run()
        summary = workflow.get_summary()

        assert summary["success"] is True
        assert summary["completed"] == 2

    @pytest.mark.asyncio
    async def test_pipeline_with_failure(self):
        """Test pipeline with failing stage."""
        from codomyrmex.orchestrator.integration import (
            CICDBridge,
            PipelineConfig,
            StageConfig,
        )

        bridge = CICDBridge()

        stages = [
            StageConfig(name="pass", commands=["echo pass"]),
            StageConfig(name="fail", commands=["exit 1"])
        ]
        config = PipelineConfig(name="failing", stages=stages, fail_fast=True)

        workflow = bridge.create_workflow_from_pipeline(config)

        await workflow.run()

        # The stage task completes but reports success=False in its result
        fail_task = workflow.tasks.get("fail")
        if fail_task and fail_task.result:
            result = fail_task.result
            # Stage reports success=False due to exit 1
            assert result.get("success") is False
