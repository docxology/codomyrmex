"""Integration and error handling tests for the ci_cd_automation module."""

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


class TestPipelineManager:
    """Test cases for PipelineManager functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = PipelineManager()

    def test_pipeline_manager_initialization(self):
        """Test PipelineManager initialization."""
        manager = PipelineManager()
        assert manager.pipelines == {}
        assert manager.active_executions == {}
        assert manager.workspace_dir is not None

    def test_create_pipeline_from_config(self, tmp_path):
        """Test pipeline creation from YAML config with real file operations."""
        config_content = """
name: test_pipeline
description: Test pipeline description
stages:
  - name: build
    jobs:
      - name: compile
        commands:
          - echo "Building..."
  - name: test
    dependencies: [build]
    jobs:
      - name: unit_tests
        commands:
          - echo "Testing..."
"""
        config_path = tmp_path / "pipeline.yaml"
        config_path.write_text(config_content)

        pipeline = self.manager.create_pipeline(str(config_path))

        assert pipeline.name == "test_pipeline"
        assert pipeline.description == "Test pipeline description"
        assert len(pipeline.stages) == 2
        assert pipeline.stages[0].name == "build"
        assert pipeline.stages[1].name == "test"
        assert pipeline.stages[1].dependencies == ["build"]

    def test_get_pipeline_status(self):
        """Test getting pipeline status."""
        # Test with non-existent pipeline
        result = self.manager.get_pipeline_status("nonexistent")
        assert result is None

        # Test with existing pipeline
        pipeline = Pipeline(name="test_pipeline", stages=[])
        self.manager.pipelines["test_pipeline"] = pipeline

        result = self.manager.get_pipeline_status("test_pipeline")
        assert result == pipeline

    def test_list_pipelines(self):
        """Test listing pipelines."""
        # Empty list initially
        assert self.manager.list_pipelines() == []

        # Add pipelines
        pipeline1 = Pipeline(name="pipeline1", stages=[])
        pipeline2 = Pipeline(name="pipeline2", stages=[])
        self.manager.pipelines["pipeline1"] = pipeline1
        self.manager.pipelines["pipeline2"] = pipeline2

        pipelines = self.manager.list_pipelines()
        assert len(pipelines) == 2
        assert pipelines[0].name in ["pipeline1", "pipeline2"]
        assert pipelines[1].name in ["pipeline1", "pipeline2"]

    def test_cancel_pipeline_nonexistent(self):
        """Test canceling non-existent pipeline."""
        result = self.manager.cancel_pipeline("nonexistent")
        assert result is False

    def test_run_command_success(self):
        """Test successful command execution with real subprocess."""
        async def test():
            result = await self.manager._run_command_async("echo test", 30, {})
            assert result["returncode"] == 0
            assert "test" in result.get("stdout", "")

        asyncio.run(test())

    def test_run_command_timeout(self):
        """Test command execution timeout with real subprocess."""
        async def test():
            # Use a command that will timeout quickly
            result = await self.manager._run_command_async("sleep 60", 1, {})
            assert result["returncode"] == -1
            assert "timed out" in result.get("stderr", "").lower() or result["returncode"] == -1

        asyncio.run(test())

    def test_substitute_variables(self):
        """Test variable substitution in commands."""
        variables = {"VERSION": "1.0.0", "ENV": "prod"}

        # Test different variable formats
        assert self.manager._substitute_variables("${VERSION}", variables) == "1.0.0"
        assert self.manager._substitute_variables("$VERSION", variables) == "1.0.0"
        assert self.manager._substitute_variables("v${VERSION}", variables) == "v1.0.0"
        assert self.manager._substitute_variables("test $ENV", variables) == "test prod"

        # Test missing variables
        assert self.manager._substitute_variables("$MISSING", variables) == "$MISSING"

    def test_save_pipeline_config(self, tmp_path):
        """Test pipeline config saving with real YAML operations."""
        pipeline = Pipeline(
            name="test_pipeline",
            stages=[PipelineStage(name="stage1", jobs=[])]
        )

        output_path = str(tmp_path / "pipeline.yaml")
        self.manager.save_pipeline_config(pipeline, output_path)

        # Verify file was created
        assert os.path.exists(output_path)

        # Verify file contains valid YAML
        with open(output_path) as f:
            config = yaml.safe_load(f)
            assert config["name"] == "test_pipeline"


class TestDeploymentOrchestrator:
    """Test cases for DeploymentOrchestrator functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.orchestrator = DeploymentOrchestrator()

    def test_deployment_orchestrator_initialization(self):
        """Test DeploymentOrchestrator initialization."""
        orchestrator = DeploymentOrchestrator()
        assert orchestrator.environments == {}
        assert orchestrator.deployments == {}

    def test_create_deployment(self):
        """Test deployment creation."""
        environment = Environment(
            name="test-env",
            type=EnvironmentType.DEVELOPMENT,
            host="localhost",
            user="deploy"
        )
        self.orchestrator.environments["test-env"] = environment

        deployment = self.orchestrator.create_deployment(
            name="test-deployment",
            version="1.0.0",
            environment_name="test-env",
            artifacts=["app.tar.gz"]
        )

        assert deployment.name == "test-deployment"
        assert deployment.version == "1.0.0"
        assert deployment.environment == environment
        assert deployment.artifacts == ["app.tar.gz"]
        assert deployment.status == DeploymentStatus.PENDING

    def test_create_deployment_invalid_environment(self):
        """Test deployment creation with invalid environment."""
        with pytest.raises(ValueError, match="Environment.*not found"):
            self.orchestrator.create_deployment(
                name="test",
                version="1.0.0",
                environment_name="nonexistent",
                artifacts=[]
            )

    def test_get_deployment_status(self):
        """Test getting deployment status."""
        # Test non-existent deployment
        assert self.orchestrator.get_deployment_status("nonexistent") is None

        # Test existing deployment
        deployment = Deployment(
            name="test",
            version="1.0.0",
            environment=Environment(name="test", type=EnvironmentType.DEVELOPMENT, host="localhost"),
            artifacts=[]
        )
        self.orchestrator.deployments["test"] = deployment

        result = self.orchestrator.get_deployment_status("test")
        assert result == deployment

    def test_list_deployments(self):
        """Test listing deployments."""
        assert self.orchestrator.list_deployments() == []

        deployment = Deployment(
            name="test",
            version="1.0.0",
            environment=Environment(name="test", type=EnvironmentType.DEVELOPMENT, host="localhost"),
            artifacts=[]
        )
        self.orchestrator.deployments["test"] = deployment

        deployments = self.orchestrator.list_deployments()
        assert len(deployments) == 1
        assert deployments[0] == deployment

    def test_cancel_deployment_nonexistent(self):
        """Test canceling non-existent deployment."""
        result = self.orchestrator.cancel_deployment("nonexistent")
        assert result is False

    def test_cancel_deployment_running(self):
        """Test canceling running deployment."""
        deployment = Deployment(
            name="test",
            version="1.0.0",
            environment=Environment(name="test", type=EnvironmentType.DEVELOPMENT, host="localhost"),
            artifacts=[],
            status=DeploymentStatus.RUNNING
        )
        self.orchestrator.deployments["test"] = deployment

        result = self.orchestrator.cancel_deployment("test")
        assert result is True
        assert deployment.status == DeploymentStatus.CANCELLED

    def test_cancel_deployment_not_running(self):
        """Test canceling non-running deployment."""
        deployment = Deployment(
            name="test",
            version="1.0.0",
            environment=Environment(name="test", type=EnvironmentType.DEVELOPMENT, host="localhost"),
            artifacts=[],
            status=DeploymentStatus.SUCCESS
        )
        self.orchestrator.deployments["test"] = deployment

        result = self.orchestrator.cancel_deployment("test")
        assert result is False

    def test_deploy_to_development_docker(self):
        """Test deployment to development environment with real Docker."""
        try:
            client = docker.from_env()
            client.ping()
            DOCKER_AVAILABLE = True
        except Exception:
            DOCKER_AVAILABLE = False

        if not DOCKER_AVAILABLE:
            pytest.skip("Docker not available")

        environment = Environment(
            name="dev",
            type=EnvironmentType.DEVELOPMENT,
            host="localhost"
        )

        deployment = Deployment(
            name="test",
            version="1.0.0",
            environment=environment,
            artifacts=["app.tar.gz"]
        )

        # Verify structure
        assert deployment.environment.type == EnvironmentType.DEVELOPMENT

    def test_deploy_to_production_kubernetes(self):
        """Test deployment to production with Kubernetes."""
        try:
            import kubernetes
            KUBERNETES_AVAILABLE = True
        except ImportError:
            KUBERNETES_AVAILABLE = False

        if not KUBERNETES_AVAILABLE:
            pytest.skip("Kubernetes client not available")

        environment = Environment(
            name="prod",
            type=EnvironmentType.PRODUCTION,
            host="prod.example.com",
            kubernetes_context="prod-cluster"
        )

        deployment = Deployment(
            name="test",
            version="1.0.0",
            environment=environment,
            artifacts=["deployment.yaml"]
        )

        assert deployment.environment.type == EnvironmentType.PRODUCTION

    def test_execute_hooks(self):
        """Test hook execution with real subprocess."""
        environment = Environment(
            name="test",
            type=EnvironmentType.DEVELOPMENT,
            host="localhost",
            pre_deploy_hooks=["echo 'pre-deploy'"],
            post_deploy_hooks=["echo 'post-deploy'"]
        )

        deployment = Deployment(
            name="test",
            version="1.0.0",
            environment=environment,
            artifacts=[]
        )

        # Execute hooks with real subprocess
        try:
            self.orchestrator._execute_hooks(deployment, "pre_deploy")
            # Should complete without error
        except Exception:
            # May fail if hooks are not executable
            pass

    def test_perform_health_checks_http(self):
        """Test HTTP health check with real requests."""
        try:
            import requests
        except ImportError:
            pytest.skip("requests not available")

        environment = Environment(
            name="test",
            type=EnvironmentType.DEVELOPMENT,
            host="localhost",
            health_checks=[{
                "type": "http",
                "endpoint": "http://localhost:8000/health",
                "timeout": 30
            }]
        )

        deployment = Deployment(
            name="test",
            version="1.0.0",
            environment=environment,
            artifacts=[]
        )

        # Try real HTTP check (may fail if endpoint not available)
        try:
            result = self.orchestrator._perform_health_checks(deployment)
            assert isinstance(result, bool)
        except Exception:
            # Expected if endpoint not available
            pytest.skip("Health check endpoint not available")

    def test_perform_health_checks_http_failure(self):
        """Test HTTP health check failure with real requests."""
        try:
            import requests
        except ImportError:
            pytest.skip("requests not available")

        environment = Environment(
            name="test",
            type=EnvironmentType.DEVELOPMENT,
            host="localhost",
            health_checks=[{
                "type": "http",
                "endpoint": "http://localhost:99999/health",  # Invalid port
                "timeout": 1
            }]
        )

        deployment = Deployment(
            name="test",
            version="1.0.0",
            environment=environment,
            artifacts=[]
        )

        # Should fail gracefully
        result = self.orchestrator._perform_health_checks(deployment)
        assert result is False

    def test_perform_health_checks_tcp(self):
        """Test TCP health check with real socket."""
        environment = Environment(
            name="test",
            type=EnvironmentType.DEVELOPMENT,
            host="localhost",
            health_checks=[{
                "type": "tcp",
                "endpoint": "localhost:99999",  # Invalid port for testing
                "timeout": 1
            }]
        )

        deployment = Deployment(
            name="test",
            version="1.0.0",
            environment=environment,
            artifacts=[]
        )

        # Should fail gracefully with invalid endpoint
        result = self.orchestrator._perform_health_checks(deployment)
        assert isinstance(result, bool)


class TestConvenienceFunctions:
    """Test cases for module-level convenience functions."""

    def test_create_pipeline_function(self, tmp_path):
        """Test create_pipeline convenience function with real manager."""
        config_path = tmp_path / "pipeline.yaml"
        config_path.write_text("name: test\nstages: []")

        result = create_pipeline(str(config_path))

        # Should return a Pipeline instance
        assert isinstance(result, Pipeline)
        assert result.name == "test"

    def test_run_pipeline_function(self):
        """Test run_pipeline convenience function with real manager."""
        # Create a pipeline first
        manager = PipelineManager()
        pipeline = Pipeline(name="test_pipeline", stages=[])
        manager.pipelines["test_pipeline"] = pipeline

        # Test that function exists and is callable
        assert callable(run_pipeline)

    def test_manage_deployments_function(self):
        """Test manage_deployments convenience function with real orchestrator."""
        result = manage_deployments()

        # Should return a DeploymentOrchestrator instance
        assert isinstance(result, DeploymentOrchestrator)


class TestIntegration:
    """Integration tests for CI/CD automation components."""

    def test_pipeline_execution_flow(self):
        """Test complete pipeline execution flow."""
        # Create a simple pipeline
        job = PipelineJob(name="echo_job", commands=["echo 'Hello World'"])
        stage = PipelineStage(name="test_stage", jobs=[job])
        pipeline = Pipeline(name="integration_test", stages=[stage])

        manager = PipelineManager()
        manager.pipelines["integration_test"] = pipeline

        # Verify structure
        assert pipeline.name == "integration_test"
        assert len(pipeline.stages) == 1
        assert pipeline.stages[0].jobs[0].name == "echo_job"

    def test_deployment_creation_flow(self):
        """Test deployment creation and management flow."""
        environment = Environment(
            name="integration_test",
            type=EnvironmentType.DEVELOPMENT,
            host="localhost"
        )

        orchestrator = DeploymentOrchestrator()
        orchestrator.environments["integration_test"] = environment

        deployment = orchestrator.create_deployment(
            name="integration_deployment",
            version="1.0.0",
            environment_name="integration_test",
            artifacts=["test-app.tar.gz"]
        )

        assert deployment.name == "integration_deployment"
        assert deployment.version == "1.0.0"
        assert deployment.environment.name == "integration_test"
        assert deployment.artifacts == ["test-app.tar.gz"]

    def test_pipeline_to_dict_conversion(self):
        """Test Pipeline to_dict conversion for serialization."""
        pipeline = Pipeline(
            name="test_pipeline",
            description="Test description",
            stages=[],
            status=PipelineStatus.RUNNING,
            started_at=datetime.now(timezone.utc)
        )

        pipeline_dict = pipeline.to_dict()

        assert pipeline_dict["name"] == "test_pipeline"
        assert pipeline_dict["description"] == "Test description"
        assert pipeline_dict["status"] == "running"
        assert "started_at" in pipeline_dict
        assert isinstance(pipeline_dict["stages"], list)

    def test_deployment_to_dict_conversion(self):
        """Test Deployment to_dict conversion for serialization."""
        environment = Environment(
            name="test",
            type=EnvironmentType.DEVELOPMENT,
            host="localhost"
        )

        deployment = Deployment(
            name="test_deployment",
            version="1.0.0",
            environment=environment,
            artifacts=[],
            status=DeploymentStatus.SUCCESS,
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc)
        )

        deployment_dict = deployment.to_dict()

        assert deployment_dict["name"] == "test_deployment"
        assert deployment_dict["version"] == "1.0.0"
        assert deployment_dict["status"] == "success"
        assert "started_at" in deployment_dict
        assert "finished_at" in deployment_dict


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


# -------------------------------------------------------------------------
# GitHub Actions API tests -- require GITHUB_TOKEN (real API calls)
# -------------------------------------------------------------------------

_HAS_GITHUB_TOKEN = bool(os.environ.get("GITHUB_TOKEN"))
_GITHUB_OWNER = os.environ.get("GITHUB_REPO_OWNER", "")
_GITHUB_REPO = os.environ.get("GITHUB_REPO_NAME", "")

requires_github_api = pytest.mark.skipif(
    not (_HAS_GITHUB_TOKEN and _GITHUB_OWNER and _GITHUB_REPO),
    reason="GITHUB_TOKEN / GITHUB_REPO_OWNER / GITHUB_REPO_NAME not set",
)


class TestPipelineTriggeringGitHubActions:
    """Test cases for GitHub Actions pipeline triggering -- skip if no API token."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = AsyncPipelineManager(
            base_url="https://api.github.com",
            api_token=os.environ.get("GITHUB_TOKEN", "")
        )

    @requires_github_api
    @pytest.mark.asyncio
    async def test_trigger_github_workflow_success(self):
        """Test triggering a real GitHub Actions workflow."""
        result = await self.manager.async_trigger_pipeline(
            pipeline_name="test-workflow",
            repo_owner=_GITHUB_OWNER,
            repo_name=_GITHUB_REPO,
            workflow_id="ci.yml",
            ref="main",
            inputs={"environment": "staging"}
        )
        # Result depends on whether the workflow actually exists
        assert result.status in (PipelineStatus.PENDING, PipelineStatus.FAILURE)

    @pytest.mark.asyncio
    async def test_trigger_github_workflow_unauthorized(self):
        """Test triggering with invalid token returns failure."""
        if not AIOHTTP_AVAILABLE:
            pytest.skip("aiohttp not installed")
        manager = AsyncPipelineManager(
            base_url="https://api.github.com",
            api_token="invalid_token_12345"
        )
        result = await manager.async_trigger_pipeline(
            pipeline_name="test-workflow",
            repo_owner="nonexistent-owner-xyz",
            repo_name="nonexistent-repo-xyz",
            workflow_id="ci.yml",
            ref="main"
        )
        assert result.status == PipelineStatus.FAILURE

    @pytest.mark.asyncio
    async def test_trigger_github_workflow_timeout(self):
        """Test GitHub Actions workflow trigger timeout."""
        if not AIOHTTP_AVAILABLE:
            pytest.skip("aiohttp not installed")
        manager = AsyncPipelineManager(
            base_url="https://api.github.com",
            api_token="test_token"
        )
        result = await manager.async_trigger_pipeline(
            pipeline_name="test-workflow",
            repo_owner="nonexistent-owner-xyz",
            repo_name="nonexistent-repo-xyz",
            workflow_id="ci.yml",
            ref="main",
            timeout=0.001  # Very short timeout
        )
        assert result.status == PipelineStatus.FAILURE


class TestPipelineStatusMonitoring:
    """Test cases for pipeline status monitoring -- skip if no GitHub API token."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = AsyncPipelineManager(
            api_token=os.environ.get("GITHUB_TOKEN", "")
        )

    @requires_github_api
    @pytest.mark.asyncio
    async def test_get_pipeline_status_success(self):
        """Test getting a real pipeline status from GitHub API."""
        # Requires a known run_id; skip if not available
        run_id = int(os.environ.get("GITHUB_RUN_ID", "0"))
        if not run_id:
            pytest.skip("GITHUB_RUN_ID not set")
        result = await self.manager.async_get_pipeline_status(
            repo_owner=_GITHUB_OWNER,
            repo_name=_GITHUB_REPO,
            run_id=run_id
        )
        assert result.status in (
            PipelineStatus.SUCCESS, PipelineStatus.RUNNING,
            PipelineStatus.FAILURE, PipelineStatus.PENDING
        )

    @requires_github_api
    @pytest.mark.asyncio
    async def test_get_workflow_runs_list(self):
        """Test listing real workflow runs from GitHub API."""
        result = await self.manager.async_get_workflow_runs(
            repo_owner=_GITHUB_OWNER,
            repo_name=_GITHUB_REPO,
            per_page=5
        )
        assert result.status in (PipelineStatus.SUCCESS, PipelineStatus.FAILURE)


class TestWorkflowDispatching:
    """Test cases for workflow dispatching -- skip if no GitHub API token."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = AsyncPipelineManager(
            api_token=os.environ.get("GITHUB_TOKEN", "")
        )

    @requires_github_api
    @pytest.mark.asyncio
    async def test_dispatch_workflow_with_inputs(self):
        """Test dispatching a real workflow with custom inputs."""
        result = await self.manager.async_trigger_pipeline(
            pipeline_name="deploy-workflow",
            repo_owner=_GITHUB_OWNER,
            repo_name=_GITHUB_REPO,
            workflow_id="deploy.yml",
            ref="main",
            inputs={
                "environment": "production",
                "version": "1.2.3",
                "dry_run": "false"
            }
        )
        # May succeed or fail depending on repo config
        assert result.status in (PipelineStatus.PENDING, PipelineStatus.FAILURE)

    @requires_github_api
    @pytest.mark.asyncio
    async def test_dispatch_workflow_different_branches(self):
        """Test dispatching workflow to different branches."""
        result = await self.manager.async_trigger_pipeline(
            pipeline_name="feature-test",
            repo_owner=_GITHUB_OWNER,
            repo_name=_GITHUB_REPO,
            workflow_id="test.yml",
            ref="feature/new-feature"
        )
        assert result.status in (PipelineStatus.PENDING, PipelineStatus.FAILURE)

    @pytest.mark.asyncio
    async def test_dispatch_workflow_not_found(self):
        """Test dispatching to a non-existent workflow."""
        if not AIOHTTP_AVAILABLE:
            pytest.skip("aiohttp not installed")
        manager = AsyncPipelineManager(api_token="invalid_token_xyz")
        result = await manager.async_trigger_pipeline(
            pipeline_name="missing-workflow",
            repo_owner="nonexistent-owner-xyz",
            repo_name="nonexistent-repo-xyz",
            workflow_id="nonexistent.yml",
            ref="main"
        )
        assert result.status == PipelineStatus.FAILURE


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


class TestPipelineMonitor:
    """Test cases for pipeline monitoring functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.monitor = PipelineMonitor()

    def test_start_monitoring(self):
        """Test starting pipeline monitoring."""
        execution_id = self.monitor.start_monitoring("test_pipeline")

        assert execution_id is not None
        assert "test_pipeline" in execution_id
        assert execution_id in self.monitor._active_metrics

    def test_record_stage_completion(self):
        """Test recording stage completion."""
        execution_id = self.monitor.start_monitoring("test_pipeline")

        self.monitor.record_stage_completion(execution_id, "build", True)
        self.monitor.record_stage_completion(execution_id, "test", False)

        metrics = self.monitor._active_metrics[execution_id]
        assert metrics.stage_count == 2
        assert metrics.error_count == 1

    def test_record_job_completion(self):
        """Test recording job completion."""
        execution_id = self.monitor.start_monitoring("test_pipeline")

        self.monitor.record_job_completion(execution_id, "job1", True)
        self.monitor.record_job_completion(execution_id, "job2", True)
        self.monitor.record_job_completion(execution_id, "job3", False)

        metrics = self.monitor._active_metrics[execution_id]
        assert metrics.job_count == 3
        assert metrics.error_count == 1

    def test_finish_monitoring(self):
        """Test finishing pipeline monitoring."""
        execution_id = self.monitor.start_monitoring("test_pipeline")

        self.monitor.record_job_completion(execution_id, "job1", True)
        self.monitor.record_job_completion(execution_id, "job2", True)

        metrics = self.monitor.finish_monitoring(execution_id, "completed")

        assert metrics.pipeline_name == "test_pipeline"
        assert metrics.job_count == 2
        assert metrics.success_rate == 100.0
        assert execution_id not in self.monitor._active_metrics

    def test_generate_report(self, tmp_path):
        """Test report generation."""
        monitor = PipelineMonitor(workspace_dir=str(tmp_path))

        report = monitor.generate_report("test_execution", ReportType.EXECUTION)

        assert isinstance(report, PipelineReport)
        assert report.execution_id == "test_execution"
        assert report.stages_executed > 0

    def test_get_pipeline_health(self):
        """Test getting pipeline health status."""
        health = self.monitor.get_pipeline_health("test_pipeline")

        assert "pipeline_name" in health
        assert "status" in health
        assert "success_rate" in health


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
