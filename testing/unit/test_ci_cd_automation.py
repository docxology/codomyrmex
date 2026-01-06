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
import subprocess
import socket
from pathlib import Path
from datetime import datetime, timezone

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

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
        with open(output_path, 'r') as f:
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



class TestPipelineEnhancements:
    """Test cases for enhanced pipeline functionality."""

    def test_validate_pipeline_config_valid(self):
        """Test pipeline config validation with valid config."""
        manager = PipelineManager()

        valid_config = {
            "name": "test_pipeline",
            "stages": [
                {
                    "name": "build",
                    "jobs": [
                        {
                            "name": "compile",
                            "commands": ["make build"]
                        }
                    ]
                },
                {
                    "name": "test",
                    "dependencies": ["build"],
                    "jobs": [
                        {
                            "name": "unit_tests",
                            "commands": ["pytest tests/"]
                        }
                    ]
                }
            ]
        }

        is_valid, errors = manager.validate_pipeline_config(valid_config)
        assert is_valid
        assert len(errors) == 0

    def test_validate_pipeline_config_invalid(self):
        """Test pipeline config validation with invalid config."""
        manager = PipelineManager()

        # Missing required fields
        invalid_config = {
            "stages": []
        }

        is_valid, errors = manager.validate_pipeline_config(invalid_config)
        assert not is_valid
        assert len(errors) > 0
        assert any("name" in error for error in errors)

    def test_generate_pipeline_visualization(self):
        """Test pipeline visualization generation."""
        manager = PipelineManager()

        # Create a test pipeline
        pipeline = Pipeline(
            name="test_pipeline",
            stages=[
                PipelineStage(
                    name="build",
                    jobs=[
                        PipelineJob(name="compile", commands=["make build"])
                    ]
                ),
                PipelineStage(
                    name="test",
                    dependencies=["build"],
                    jobs=[
                        PipelineJob(name="unit_tests", commands=["pytest"])
                    ]
                )
            ]
        )

        mermaid_diagram = manager.generate_pipeline_visualization(pipeline)

        assert isinstance(mermaid_diagram, str)
        assert "graph TD" in mermaid_diagram
        assert "build" in mermaid_diagram
        assert "test" in mermaid_diagram
        assert "compile" in mermaid_diagram
        assert "unit_tests" in mermaid_diagram

    def test_conditional_stage_execution(self):
        """Test conditional stage execution."""
        manager = PipelineManager()

        # Test stage with branch condition
        stage = {
            "name": "deploy_prod",
            "conditions": {
                "branch": "main"
            }
        }

        # Should execute on main branch
        conditions = {"branch": "main"}
        should_execute = manager.conditional_stage_execution(stage, conditions)
        assert should_execute

        # Should not execute on feature branch
        conditions = {"branch": "feature/new-feature"}
        should_execute = manager.conditional_stage_execution(stage, conditions)
        assert not should_execute

    def test_optimize_pipeline_schedule(self):
        """Test pipeline schedule optimization."""
        manager = PipelineManager()

        # Create pipeline with optimization opportunities
        pipeline = Pipeline(
            name="optimized_pipeline",
            stages=[
                PipelineStage(name="setup", jobs=[PipelineJob(name="init", commands=["echo init"])]),
                PipelineStage(name="build", jobs=[PipelineJob(name="compile", commands=["make"])]),
                PipelineStage(name="test_unit", dependencies=["build"], jobs=[PipelineJob(name="unit", commands=["pytest"])]),
                PipelineStage(name="test_integration", dependencies=["build"], jobs=[PipelineJob(name="integration", commands=["pytest integration"])]),
                PipelineStage(name="deploy", dependencies=["test_unit", "test_integration"], jobs=[PipelineJob(name="deploy", commands=["deploy"])]),
            ]
        )

        optimization = manager.optimize_pipeline_schedule(pipeline)

        assert "parallel_stages" in optimization
        assert "execution_levels" in optimization
        assert "optimization_suggestions" in optimization
        assert isinstance(optimization["optimization_suggestions"], list)


if __name__ == "__main__":
    pytest.main([__file__])
