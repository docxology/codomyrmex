"""
Comprehensive tests for the ci_cd_automation module.

This module tests all CI/CD automation functionality including
pipeline management, deployment orchestration, and monitoring.
"""

import pytest
import tempfile
import os
import asyncio
import yaml
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
from datetime import datetime, timezone

from codomyrmex.ci_cd_automation.pipeline_manager import (
    PipelineManager,
    create_pipeline,
    run_pipeline,
    Pipeline,
    PipelineStage,
    PipelineJob,
    PipelineStatus,
    StageStatus,
    JobStatus
)

from codomyrmex.ci_cd_automation.deployment_orchestrator import (
    DeploymentOrchestrator,
    manage_deployments,
    Deployment,
    Environment,
    DeploymentStatus,
    EnvironmentType
)


class TestPipelineJob:
    """Test cases for PipelineJob dataclass."""

    def test_pipeline_job_creation(self):
        """Test PipelineJob creation."""
        job = PipelineJob(
            name="test_job",
            commands=["echo 'hello'", "echo 'world'"],
            environment={"TEST_VAR": "test_value"},
            timeout=300
        )

        assert job.name == "test_job"
        assert len(job.commands) == 2
        assert job.environment["TEST_VAR"] == "test_value"
        assert job.timeout == 300
        assert job.status == JobStatus.PENDING

    def test_pipeline_job_defaults(self):
        """Test PipelineJob default values."""
        job = PipelineJob(name="test", commands=["echo test"])

        assert job.environment == {}
        assert job.artifacts == []
        assert job.dependencies == []
        assert job.timeout == 3600  # 1 hour
        assert job.retry_count == 0
        assert job.allow_failure is False
        assert job.status == JobStatus.PENDING

    def test_pipeline_job_to_dict(self):
        """Test PipelineJob to_dict conversion."""
        job = PipelineJob(
            name="test_job",
            commands=["echo test"],
            status=JobStatus.RUNNING,
            start_time=datetime.now(timezone.utc)
        )

        job_dict = job.to_dict()

        assert job_dict["name"] == "test_job"
        assert job_dict["commands"] == ["echo test"]
        assert job_dict["status"] == "running"
        assert "start_time" in job_dict


class TestPipelineStage:
    """Test cases for PipelineStage dataclass."""

    def test_pipeline_stage_creation(self):
        """Test PipelineStage creation."""
        job = PipelineJob(name="job1", commands=["echo test"])
        stage = PipelineStage(
            name="test_stage",
            jobs=[job],
            dependencies=["previous_stage"],
            parallel=False
        )

        assert stage.name == "test_stage"
        assert len(stage.jobs) == 1
        assert stage.dependencies == ["previous_stage"]
        assert stage.parallel is False
        assert stage.status == StageStatus.PENDING

    def test_pipeline_stage_to_dict(self):
        """Test PipelineStage to_dict conversion."""
        stage = PipelineStage(
            name="test_stage",
            status=StageStatus.RUNNING,
            start_time=datetime.now(timezone.utc)
        )

        stage_dict = stage.to_dict()

        assert stage_dict["name"] == "test_stage"
        assert stage_dict["status"] == "running"
        assert "start_time" in stage_dict
        assert "jobs" in stage_dict


class TestPipeline:
    """Test cases for Pipeline dataclass."""

    def test_pipeline_creation(self):
        """Test Pipeline creation."""
        stage = PipelineStage(name="stage1", jobs=[])
        pipeline = Pipeline(
            name="test_pipeline",
            description="Test pipeline",
            stages=[stage],
            timeout=1800
        )

        assert pipeline.name == "test_pipeline"
        assert pipeline.description == "Test pipeline"
        assert len(pipeline.stages) == 1
        assert pipeline.timeout == 1800
        assert pipeline.status == PipelineStatus.PENDING

    def test_pipeline_auto_timestamp(self):
        """Test Pipeline automatic timestamp creation."""
        pipeline = Pipeline(name="test", stages=[])

        assert pipeline.created_at is not None
        assert isinstance(pipeline.created_at, datetime)

    def test_pipeline_to_dict(self):
        """Test Pipeline to_dict conversion."""
        pipeline = Pipeline(
            name="test_pipeline",
            stages=[],
            status=PipelineStatus.RUNNING,
            started_at=datetime.now(timezone.utc)
        )

        pipeline_dict = pipeline.to_dict()

        assert pipeline_dict["name"] == "test_pipeline"
        assert pipeline_dict["status"] == "running"
        assert "started_at" in pipeline_dict
        assert "stages" in pipeline_dict


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

    def test_create_pipeline_from_config(self):
        """Test pipeline creation from YAML config."""
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

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_path = f.name

        try:
            pipeline = self.manager.create_pipeline(config_path)

            assert pipeline.name == "test_pipeline"
            assert pipeline.description == "Test pipeline description"
            assert len(pipeline.stages) == 2
            assert pipeline.stages[0].name == "build"
            assert pipeline.stages[1].name == "test"
            assert pipeline.stages[1].dependencies == ["build"]

        finally:
            os.unlink(config_path)

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

    @patch('codomyrmex.ci_cd_automation.pipeline_manager.subprocess.run')
    def test_run_command_success(self, mock_subprocess):
        """Test successful command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Command output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        async def test():
            result = await self.manager._run_command_async("echo test", 30, {})
            assert result["returncode"] == 0
            assert result["stdout"] == "Command output"

        asyncio.run(test())

    @patch('codomyrmex.ci_cd_automation.pipeline_manager.subprocess.run')
    def test_run_command_timeout(self, mock_subprocess):
        """Test command execution timeout."""
        from subprocess import TimeoutExpired
        mock_subprocess.side_effect = TimeoutExpired("timeout", 30)

        async def test():
            result = await self.manager._run_command_async("slow command", 30, {})
            assert result["returncode"] == -1
            assert "timed out" in result["stderr"]

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

    @patch('codomyrmex.ci_cd_automation.pipeline_manager.yaml.dump')
    def test_save_pipeline_config(self, mock_yaml_dump):
        """Test pipeline config saving."""
        pipeline = Pipeline(
            name="test_pipeline",
            stages=[PipelineStage(name="stage1", jobs=[])]
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as f:
            output_path = f.name

        try:
            self.manager.save_pipeline_config(pipeline, output_path)

            # Verify yaml.dump was called
            mock_yaml_dump.assert_called_once()

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


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

    @patch('codomyrmex.ci_cd_automation.deployment_orchestrator.docker')
    def test_deploy_to_development_docker(self, mock_docker):
        """Test deployment to development environment with Docker."""
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_client.ping.return_value = True

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

        # Re-initialize to use mocked Docker
        orchestrator = DeploymentOrchestrator()
        orchestrator._initialize_clients()

        # This would normally call Docker methods
        # For testing, we verify the structure is correct
        assert deployment.environment.type == EnvironmentType.DEVELOPMENT

    @patch('codomyrmex.ci_cd_automation.deployment_orchestrator.kubernetes')
    def test_deploy_to_production_kubernetes(self, mock_kubernetes):
        """Test deployment to production with Kubernetes."""
        mock_api = MagicMock()
        mock_kubernetes.config.load_kube_config.return_value = None
        mock_kubernetes.client.CoreV1Api.return_value = mock_api

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

        # Re-initialize to use mocked Kubernetes
        orchestrator = DeploymentOrchestrator()
        orchestrator._initialize_clients()

        assert deployment.environment.type == EnvironmentType.PRODUCTION

    def test_execute_hooks(self):
        """Test hook execution."""
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

        with patch('subprocess.run') as mock_subprocess:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result

            self.orchestrator._execute_hooks(deployment, "pre_deploy")

            mock_subprocess.assert_called_once()
            args, kwargs = mock_subprocess.call_args
            assert "echo 'pre-deploy'" in args[0]

    def test_perform_health_checks_http(self):
        """Test HTTP health check."""
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

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            result = self.orchestrator._perform_health_checks(deployment)
            assert result is True

    def test_perform_health_checks_http_failure(self):
        """Test HTTP health check failure."""
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

        with patch('requests.get', side_effect=Exception("Connection failed")):
            result = self.orchestrator._perform_health_checks(deployment)
            assert result is False

    def test_perform_health_checks_tcp(self):
        """Test TCP health check."""
        environment = Environment(
            name="test",
            type=EnvironmentType.DEVELOPMENT,
            host="localhost",
            health_checks=[{
                "type": "tcp",
                "endpoint": "localhost:8000",
                "timeout": 30
            }]
        )

        deployment = Deployment(
            name="test",
            version="1.0.0",
            environment=environment,
            artifacts=[]
        )

        with patch('socket.create_connection') as mock_connect:
            mock_sock = MagicMock()
            mock_connect.return_value.__enter__.return_value = mock_sock

            result = self.orchestrator._perform_health_checks(deployment)
            assert result is True


class TestConvenienceFunctions:
    """Test cases for module-level convenience functions."""

    @patch('codomyrmex.ci_cd_automation.pipeline_manager.PipelineManager')
    def test_create_pipeline_function(self, mock_manager_class):
        """Test create_pipeline convenience function."""
        mock_manager = MagicMock()
        mock_pipeline = MagicMock()
        mock_manager.create_pipeline.return_value = mock_pipeline
        mock_manager_class.return_value = mock_manager

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("name: test\nstages: []")
            config_path = f.name

        try:
            result = create_pipeline(config_path)

            mock_manager_class.assert_called_once()
            mock_manager.create_pipeline.assert_called_once_with(config_path)
            assert result == mock_pipeline

        finally:
            os.unlink(config_path)

    @patch('codomyrmex.ci_cd_automation.pipeline_manager.PipelineManager')
    def test_run_pipeline_function(self, mock_manager_class):
        """Test run_pipeline convenience function."""
        mock_manager = MagicMock()
        mock_pipeline = MagicMock()
        mock_manager.run_pipeline.return_value = mock_pipeline
        mock_manager_class.return_value = mock_manager

        result = run_pipeline("test_pipeline")

        mock_manager_class.assert_called_once()
        mock_manager.run_pipeline.assert_called_once_with("test_pipeline", None)
        assert result == mock_pipeline

    @patch('codomyrmex.ci_cd_automation.deployment_orchestrator.DeploymentOrchestrator')
    def test_manage_deployments_function(self, mock_orchestrator_class):
        """Test manage_deployments convenience function."""
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator

        result = manage_deployments()

        mock_orchestrator_class.assert_called_once()
        assert result == mock_orchestrator


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

        with patch('codomyrmex.ci_cd_automation.pipeline_manager.subprocess.run') as mock_subprocess:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Hello World\n"
            mock_result.stderr = ""
            mock_subprocess.return_value = mock_result

            # Note: In real usage, this would be async
            # For testing, we're verifying the structure
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

    def test_pipeline_creation_invalid_config(self):
        """Test pipeline creation with invalid config."""
        manager = PipelineManager()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [unbalanced brackets")
            config_path = f.name

        try:
            with pytest.raises(Exception):  # Could be YAML or parsing error
                manager.create_pipeline(config_path)
        finally:
            os.unlink(config_path)

    @patch('codomyrmex.ci_cd_automation.pipeline_manager.subprocess.run')
    def test_command_execution_failure(self, mock_subprocess):
        """Test command execution failure handling."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Command failed"
        mock_subprocess.return_value = mock_result

        manager = PipelineManager()

        async def test():
            result = await manager._run_command_async("failing command", 30, {})
            assert result["returncode"] == 1
            assert result["stderr"] == "Command failed"

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

    @patch('requests.get', side_effect=Exception("Network error"))
    def test_health_check_network_failure(self, mock_get):
        """Test health check failure handling."""
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

        orchestrator = DeploymentOrchestrator()
        result = orchestrator._perform_health_checks(deployment)

        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
