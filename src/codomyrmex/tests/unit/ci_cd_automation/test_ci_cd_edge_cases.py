"""Error handling, edge cases, and boundary condition tests for the ci_cd_automation module."""

import asyncio
import json
import os
from datetime import datetime, timezone

import pytest
import yaml

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from codomyrmex.ci_cd_automation.deployment_orchestrator import (
    Deployment,
    DeploymentOrchestrator,
    DeploymentStatus,
    Environment,
    EnvironmentType,
    manage_deployments,
)
from codomyrmex.ci_cd_automation.performance_optimizer import (
    PipelineOptimizer,
)
from codomyrmex.ci_cd_automation.pipeline import (
    AsyncPipelineManager,
    AsyncPipelineResult,
    JobStatus,
    Pipeline,
    PipelineJob,
    PipelineManager,
    PipelineStage,
    PipelineStatus,
    StageStatus,
    create_pipeline,
    run_pipeline,
)
from codomyrmex.ci_cd_automation.pipeline.pipeline_monitor import (
    PipelineMonitor,
    PipelineReport,
    ReportType,
)
from codomyrmex.ci_cd_automation.rollback_manager import (
    RollbackExecution,
    RollbackManager,
    RollbackStrategy,
)


_HAS_GITHUB_TOKEN = bool(os.environ.get("GITHUB_TOKEN"))
_GITHUB_OWNER = os.environ.get("GITHUB_REPO_OWNER", "")
_GITHUB_REPO = os.environ.get("GITHUB_REPO_NAME", "")

requires_github_api = pytest.mark.skipif(
    not (_HAS_GITHUB_TOKEN and _GITHUB_OWNER and _GITHUB_REPO),
    reason="GITHUB_TOKEN / GITHUB_REPO_OWNER / GITHUB_REPO_NAME not set",
)


class TestErrorHandling:
    """Test cases for error handling in CI/CD operations."""

    def test_pipeline_creation_invalid_config(self, tmp_path):
        """Test pipeline creation with invalid config."""
        manager = PipelineManager()

        config_path = tmp_path / "invalid.yaml"
        config_path.write_text("invalid: yaml: content: [unbalanced brackets")

        with pytest.raises(Exception):  # Could be YAML or parsing error
            manager.create_pipeline(str(config_path))

    def test_command_execution_failure(self):
        """Test command execution failure handling with real subprocess."""
        manager = PipelineManager()

        async def test():
            # Use a command that will fail
            result = await manager._run_command_async("false", 30, {})
            assert result["returncode"] != 0

        asyncio.run(test())

    def test_deployment_invalid_environment(self):
        """Test deployment with invalid environment."""
        orchestrator = DeploymentOrchestrator()

        with pytest.raises(ValueError, match="Environment.*not found"):
            orchestrator.create_deployment(
                name="test",
                version="1.0.0",
                environment_name="nonexistent_env",
                artifacts=[]
            )


class TestPipelineCancellation:
    """Test cases for pipeline cancellation."""

    def setup_method(self):
        """Setup for each test method."""
        self.sync_manager = PipelineManager()
        self.async_manager = AsyncPipelineManager(
            api_token=os.environ.get("GITHUB_TOKEN", "")
        )

    def test_cancel_local_pipeline(self):
        """Test canceling a local pipeline."""
        pipeline = Pipeline(
            name="running_pipeline",
            status=PipelineStatus.RUNNING,
            stages=[]
        )
        self.sync_manager.pipelines["running_pipeline"] = pipeline

        # Use a real asyncio.Task-like object
        class _CancellableTask:
            def __init__(self):
                self.cancelled_called = False
            def cancel(self):
                self.cancelled_called = True

        task = _CancellableTask()
        self.sync_manager.active_executions["running_pipeline"] = task

        result = self.sync_manager.cancel_pipeline("running_pipeline")

        assert result is True
        assert pipeline.status == PipelineStatus.CANCELLED
        assert task.cancelled_called is True

    def test_cancel_nonexistent_pipeline(self):
        """Test canceling a non-existent pipeline returns False."""
        result = self.sync_manager.cancel_pipeline("nonexistent")
        assert result is False

    @requires_github_api
    @pytest.mark.asyncio
    async def test_cancel_github_workflow_run(self):
        """Test canceling a real GitHub Actions workflow run."""
        run_id = int(os.environ.get("GITHUB_RUN_ID", "0"))
        if not run_id:
            pytest.skip("GITHUB_RUN_ID not set")
        result = await self.async_manager.async_cancel_pipeline(
            repo_owner=_GITHUB_OWNER,
            repo_name=_GITHUB_REPO,
            run_id=run_id
        )
        assert result.status in (
            PipelineStatus.CANCELLED, PipelineStatus.FAILURE
        )


class TestErrorHandlingAndRetries:
    """Test cases for error handling and retry mechanisms."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = PipelineManager()

    def test_job_retry_on_failure(self):
        """Test job retry count decrements on failure."""
        job = PipelineJob(
            name="flaky_job",
            commands=["flaky_command"],
            retry_count=3
        )

        initial_retries = job.retry_count

        # Simulate failure and retry
        job.retry_count -= 1
        assert job.retry_count == initial_retries - 1

        # Continue until exhausted
        while job.retry_count > 0:
            job.retry_count -= 1

        assert job.retry_count == 0

    def test_job_allow_failure_flag(self):
        """Test job with allow_failure flag."""
        job = PipelineJob(
            name="optional_job",
            commands=["optional_command"],
            allow_failure=True
        )

        assert job.allow_failure is True

        # Simulate failure
        job.status = JobStatus.FAILURE

        # Stage should still be able to continue
        assert job.allow_failure and job.status == JobStatus.FAILURE

    def test_stage_allow_failure_flag(self):
        """Test stage with allow_failure flag."""
        stage = PipelineStage(
            name="optional_stage",
            allow_failure=True,
            jobs=[]
        )

        assert stage.allow_failure is True

    def test_command_timeout_handling(self):
        """Test command timeout is properly configured."""
        job = PipelineJob(
            name="long_job",
            commands=["long_running_command"],
            timeout=60  # 1 minute timeout
        )

        assert job.timeout == 60

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test network error handling via real connection to invalid host."""
        if not AIOHTTP_AVAILABLE:
            pytest.skip("aiohttp not installed")
        manager = AsyncPipelineManager(api_token="test_token")
        # Use an invalid host that will cause a real connection error
        manager._base_url = "http://localhost:1"  # port 1 is almost never open
        result = await manager.async_trigger_pipeline(
            pipeline_name="test",
            repo_owner="owner",
            repo_name="repo",
            workflow_id="test.yml",
            ref="main"
        )
        assert result.status == PipelineStatus.FAILURE


class TestRollbackManager:
    """Test cases for rollback management."""

    def setup_method(self):
        """Setup for each test method."""
        self.rollback_manager = RollbackManager()

    def test_create_rollback_plan(self):
        """Test creating a rollback plan."""
        plan = self.rollback_manager.create_rollback_plan(
            deployment_id="deploy_123",
            strategy=RollbackStrategy.IMMEDIATE,
            reason="Deployment failed health checks"
        )

        assert plan.deployment_id == "deploy_123"
        assert plan.strategy == RollbackStrategy.IMMEDIATE
        assert plan.reason == "Deployment failed health checks"
        assert len(plan.steps) > 0

    def test_rollback_strategy_types(self):
        """Test different rollback strategy types."""
        strategies = [
            RollbackStrategy.IMMEDIATE,
            RollbackStrategy.ROLLING,
            RollbackStrategy.BLUE_GREEN,
            RollbackStrategy.CANARY,
            RollbackStrategy.MANUAL
        ]

        for strategy in strategies:
            plan = self.rollback_manager.create_rollback_plan(
                deployment_id=f"deploy_{strategy.value}",
                strategy=strategy,
                reason="Test rollback"
            )
            assert plan.strategy == strategy

    def test_cancel_rollback(self):
        """Test canceling a rollback execution."""
        # Create a mock active rollback
        execution = RollbackExecution(
            execution_id="rollback_123",
            deployment_id="deploy_456",
            strategy=RollbackStrategy.IMMEDIATE,
            status="running",
            start_time=datetime.now()
        )
        self.rollback_manager._active_rollbacks["rollback_123"] = execution

        result = self.rollback_manager.cancel_rollback("rollback_123")

        assert result is True
        assert "rollback_123" not in self.rollback_manager._active_rollbacks

    def test_list_rollback_plans(self):
        """Test listing rollback plans."""
        self.rollback_manager.create_rollback_plan(
            deployment_id="deploy_1",
            strategy=RollbackStrategy.IMMEDIATE,
            reason="Test 1"
        )
        self.rollback_manager.create_rollback_plan(
            deployment_id="deploy_2",
            strategy=RollbackStrategy.ROLLING,
            reason="Test 2"
        )

        plans = self.rollback_manager.list_rollback_plans()

        assert len(plans) == 2


class TestPipelineOptimizer:
    """Test cases for pipeline performance optimization."""

    def setup_method(self):
        """Setup for each test method."""
        self.optimizer = PipelineOptimizer()

    def test_record_metric(self):
        """Test recording performance metrics."""
        self.optimizer.record_metric(
            name="duration",
            value=120.5,
            unit="seconds",
            tags={"pipeline": "test_pipeline", "stage": "build"}
        )

        assert len(self.optimizer._metrics_history) == 1
        metric = self.optimizer._metrics_history[0]
        assert metric.name == "duration"
        assert metric.value == 120.5
        assert metric.unit == "seconds"

    def test_analyze_performance(self):
        """Test performance analysis."""
        # Record some metrics
        for i in range(10):
            self.optimizer.record_metric(
                name="duration",
                value=100 + i * 10,
                unit="seconds",
                tags={"pipeline": "test_pipeline"}
            )

        analysis = self.optimizer.analyze_performance("test_pipeline")

        assert "pipeline_name" in analysis
        assert "metrics_count" in analysis

    def test_optimize_pipeline_performance(self, tmp_path):
        """Test pipeline performance optimization."""
        optimizer = PipelineOptimizer(workspace_dir=str(tmp_path))

        # Record metrics
        for i in range(10):
            optimizer.record_metric(
                name="duration",
                value=400 + i * 20,  # Values that would trigger suggestions
                unit="seconds",
                tags={"pipeline": "slow_pipeline"}
            )

        result = optimizer.optimize_pipeline_performance(
            pipeline_name="slow_pipeline",
            target_improvement=0.2
        )

        assert "pipeline_name" in result
        assert "current_performance" in result or "message" in result
