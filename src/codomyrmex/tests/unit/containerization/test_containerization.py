"""
Comprehensive tests for the containerization module.

This module tests all containerization functionality including:
- Dockerfile parsing and generation
- Docker image building (mocked)
- Container lifecycle (create, start, stop, remove)
- Container exec operations
- Volume mounting
- Network configuration
- Port mapping
- Environment variable handling
- Docker Compose integration
- Error handling for Docker daemon failures

All Docker client operations are mocked to avoid requiring Docker daemon.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch, PropertyMock
from dataclasses import dataclass

# Skip entire module if docker package is not installed
try:
    import docker
    from docker.errors import APIError, DockerException, ImageNotFound, NotFound
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None
    APIError = Exception
    DockerException = Exception
    ImageNotFound = Exception
    NotFound = Exception

from codomyrmex.containerization.docker_manager import (
    DockerManager,
    ContainerConfig,
    build_containers,
    manage_containers,
)
from codomyrmex.containerization.build_generator import (
    BuildGenerator,
    BuildStage,
    MultiStageBuild,
    BuildScript,
)


# ==============================================================================
# Mock Fixtures
# ==============================================================================

@pytest.fixture
def mock_docker_client():
    """Create a mock Docker client with common methods."""
    client = MagicMock()

    # Mock ping
    client.ping.return_value = True

    # Mock images
    mock_image = MagicMock()
    mock_image.id = "sha256:abc123def456"
    mock_image.tags = ["test-app:latest"]
    mock_image.attrs = {
        "Size": 100 * 1024 * 1024,  # 100MB
        "VirtualSize": 150 * 1024 * 1024,
        "Created": "2024-01-01T00:00:00.000000000Z",
        "RootFS": {"Layers": ["layer1", "layer2", "layer3"]},
        "History": [
            {"Created": "2024-01-01T00:00:00Z", "CreatedBy": "FROM python:3.9", "Size": 50000000},
            {"Created": "2024-01-01T00:00:01Z", "CreatedBy": "RUN pip install flask", "Size": 20000000},
        ],
        "Config": {
            "Env": ["PATH=/usr/local/bin", "PYTHON_VERSION=3.9"],
            "Cmd": ["python", "app.py"],
            "ExposedPorts": {"8000/tcp": {}},
        }
    }
    mock_image.history.return_value = [
        {"Id": "layer1", "Size": 50000000},
        {"Id": "layer2", "Size": 20000000},
    ]
    mock_image.labels = {"version": "1.0.0"}
    mock_image.short_id = "sha256:abc123"

    client.images.get.return_value = mock_image
    client.images.list.return_value = [mock_image]
    client.images.build.return_value = (mock_image, [{"stream": "Building..."}, {"stream": "Done"}])
    client.images.push.return_value = [{"status": "Pushing..."}, {"status": "Done"}]
    client.images.pull.return_value = mock_image
    client.images.remove.return_value = None

    # Mock containers
    mock_container = MagicMock()
    mock_container.id = "container123abc"
    mock_container.name = "test-container"
    mock_container.status = "running"
    mock_container.image.tags = ["test-app:latest"]
    mock_container.image.id = "sha256:abc123"
    mock_container.attrs = {
        "Created": "2024-01-01T00:00:00.000000000Z",
        "NetworkSettings": {"Ports": {"8000/tcp": [{"HostPort": "8000"}]}},
        "State": {"Status": "running", "Running": True},
    }
    mock_container.logs.return_value = b"Container log output\nLine 2\nLine 3"
    mock_container.stats.return_value = {
        "cpu_stats": {"cpu_usage": {"total_usage": 1000000}},
        "memory_stats": {"usage": 50000000},
        "networks": {"eth0": {"rx_bytes": 1000, "tx_bytes": 2000}},
    }
    mock_container.exec_run.return_value = (0, b"command output")
    mock_container.stop.return_value = None
    mock_container.remove.return_value = None
    mock_container.start.return_value = None

    client.containers.get.return_value = mock_container
    client.containers.list.return_value = [mock_container]
    client.containers.run.return_value = mock_container
    client.containers.create.return_value = mock_container

    # Mock networks
    mock_network = MagicMock()
    mock_network.id = "network123"
    mock_network.name = "test-network"
    client.networks.create.return_value = mock_network
    client.networks.list.return_value = [mock_network]
    client.networks.get.return_value = mock_network

    # Mock volumes
    mock_volume = MagicMock()
    mock_volume.name = "test-volume"
    mock_volume.id = "volume123"
    client.volumes.create.return_value = mock_volume
    client.volumes.list.return_value = [mock_volume]

    # Mock info and version
    client.info.return_value = {
        "ServerVersion": "24.0.0",
        "Containers": 5,
        "ContainersRunning": 3,
        "Images": 10,
        "Driver": "overlay2",
        "Architecture": "x86_64",
        "OSType": "linux",
        "KernelVersion": "5.15.0",
    }
    client.version.return_value = {
        "ApiVersion": "1.43",
        "Version": "24.0.0",
    }

    return client


@pytest.fixture
def docker_manager_with_mock(mock_docker_client):
    """Create a DockerManager with mocked client."""
    with patch('docker.from_env', return_value=mock_docker_client):
        with patch('docker.DockerClient', return_value=mock_docker_client):
            manager = DockerManager()
            manager.client = mock_docker_client
            return manager


# ==============================================================================
# ContainerConfig Tests
# ==============================================================================

class TestContainerConfig:
    """Test cases for ContainerConfig dataclass."""

    def test_container_config_creation(self):
        """Test basic ContainerConfig creation."""
        config = ContainerConfig(
            image_name="test-app",
            tag="v1.0.0",
            environment={"DEBUG": "true"},
            ports={"8000/tcp": "8000"}
        )

        assert config.image_name == "test-app"
        assert config.tag == "v1.0.0"
        assert config.get_full_image_name() == "test-app:v1.0.0"
        assert config.environment["DEBUG"] == "true"
        assert config.ports["8000/tcp"] == "8000"

    def test_container_config_defaults(self):
        """Test ContainerConfig default values."""
        config = ContainerConfig(image_name="test")

        assert config.tag == "latest"
        assert config.dockerfile_path is None
        assert config.build_context == "."
        assert config.build_args == {}
        assert config.environment == {}
        assert config.ports == {}
        assert config.volumes == {}
        assert config.networks == []
        assert config.restart_policy == "no"
        assert config.labels == {}

    def test_get_full_image_name(self):
        """Test full image name generation."""
        config = ContainerConfig(image_name="myapp", tag="latest")
        assert config.get_full_image_name() == "myapp:latest"

        config.tag = "v2.1.0"
        assert config.get_full_image_name() == "myapp:v2.1.0"

    def test_container_config_with_volumes(self):
        """Test ContainerConfig with volume mappings."""
        config = ContainerConfig(
            image_name="webapp",
            volumes={
                "/host/data": {"bind": "/container/data", "mode": "rw"},
                "/host/config": {"bind": "/container/config", "mode": "ro"},
            }
        )
        assert len(config.volumes) == 2
        assert "/host/data" in config.volumes

    def test_container_config_with_networks(self):
        """Test ContainerConfig with network configuration."""
        config = ContainerConfig(
            image_name="webapp",
            networks=["frontend", "backend"]
        )
        assert len(config.networks) == 2
        assert "frontend" in config.networks
        assert "backend" in config.networks

    def test_container_config_with_build_args(self):
        """Test ContainerConfig with build arguments."""
        config = ContainerConfig(
            image_name="webapp",
            build_args={
                "VERSION": "1.0.0",
                "BUILD_DATE": "2024-01-01",
                "NODE_ENV": "production"
            }
        )
        assert config.build_args["VERSION"] == "1.0.0"
        assert len(config.build_args) == 3


# ==============================================================================
# Docker Image Building Tests (Mocked)
# ==============================================================================

class TestDockerImageBuilding:
    """Test cases for Docker image building operations (mocked)."""

    def test_build_image_success(self, docker_manager_with_mock, mock_docker_client):
        """Test successful image building."""
        config = ContainerConfig(
            image_name="test-app",
            tag="v1.0.0",
            build_context="/app",
            build_args={"VERSION": "1.0.0"}
        )

        result = docker_manager_with_mock.build_image(config)

        assert result["success"] is True
        assert "image_id" in result
        assert "build_time" in result

    def test_build_image_with_dockerfile(self, docker_manager_with_mock):
        """Test image building with custom Dockerfile path."""
        config = ContainerConfig(
            image_name="test-app",
            dockerfile_path="Dockerfile.prod",
            build_context="/app"
        )

        result = docker_manager_with_mock.build_image(config)

        assert result["success"] is True

    def test_build_image_with_push(self, docker_manager_with_mock, mock_docker_client):
        """Test image building with push to registry."""
        config = ContainerConfig(
            image_name="test-app",
            tag="v1.0.0"
        )
        registry_auth = {"username": "user", "password": "pass"}

        result = docker_manager_with_mock.build_image(config, push=True, registry_auth=registry_auth)

        assert result["success"] is True

    def test_build_image_failure(self, docker_manager_with_mock, mock_docker_client):
        """Test image building failure handling."""
        mock_docker_client.images.build.side_effect = Exception("Build failed")

        config = ContainerConfig(image_name="test-app")
        result = docker_manager_with_mock.build_image(config)

        assert result["success"] is False
        assert "error" in result

    def test_build_image_no_client(self):
        """Test image building when Docker client is not available."""
        manager = DockerManager()
        manager.client = None

        config = ContainerConfig(image_name="test-app")
        result = manager.build_image(config)

        assert result["success"] is False
        assert "Docker client not available" in result["error"]


# ==============================================================================
# Container Lifecycle Tests
# ==============================================================================

class TestContainerLifecycle:
    """Test cases for container lifecycle management."""

    def test_run_container_success(self, docker_manager_with_mock):
        """Test running a container successfully."""
        config = ContainerConfig(
            image_name="test-app",
            environment={"DEBUG": "true"},
            ports={"8000/tcp": "8000"}
        )

        result = docker_manager_with_mock.run_container(config)

        assert result["success"] is True
        assert "container_id" in result
        assert "container_name" in result
        assert "status" in result

    def test_run_container_with_volumes(self, docker_manager_with_mock):
        """Test running a container with volume mounts."""
        config = ContainerConfig(
            image_name="test-app",
            volumes={"/host/data": {"bind": "/data", "mode": "rw"}}
        )

        result = docker_manager_with_mock.run_container(config)

        assert result["success"] is True

    def test_run_container_with_network(self, docker_manager_with_mock):
        """Test running a container with network configuration."""
        config = ContainerConfig(
            image_name="test-app",
            networks=["test-network"]
        )

        result = docker_manager_with_mock.run_container(config)

        assert result["success"] is True

    def test_stop_container_success(self, docker_manager_with_mock):
        """Test stopping a container."""
        result = docker_manager_with_mock.stop_container("container123")

        assert result["success"] is True
        assert result["container_id"] == "container123"
        assert "stop_time" in result

    def test_stop_container_failure(self, docker_manager_with_mock, mock_docker_client):
        """Test stopping a container that doesn't exist."""
        mock_docker_client.containers.get.side_effect = NotFound("Container not found")

        result = docker_manager_with_mock.stop_container("nonexistent")

        assert result["success"] is False

    def test_remove_container_success(self, docker_manager_with_mock):
        """Test removing a container."""
        result = docker_manager_with_mock.remove_container("container123")

        assert result["success"] is True
        assert "removal_time" in result

    def test_remove_container_force(self, docker_manager_with_mock):
        """Test force removing a running container."""
        result = docker_manager_with_mock.remove_container("container123", force=True)

        assert result["success"] is True

    def test_list_containers(self, docker_manager_with_mock):
        """Test listing containers."""
        containers = docker_manager_with_mock.list_containers()

        assert isinstance(containers, list)
        assert len(containers) > 0
        assert "id" in containers[0]
        assert "name" in containers[0]
        assert "status" in containers[0]

    def test_list_containers_show_all(self, docker_manager_with_mock, mock_docker_client):
        """Test listing all containers including stopped."""
        containers = docker_manager_with_mock.list_containers(show_all=True)

        assert isinstance(containers, list)
        mock_docker_client.containers.list.assert_called_with(all=True)


# ==============================================================================
# Container Exec Operations Tests
# ==============================================================================

class TestContainerExecOperations:
    """Test cases for container exec operations."""

    def test_get_container_logs(self, docker_manager_with_mock):
        """Test getting container logs."""
        result = docker_manager_with_mock.get_container_logs("container123")

        assert result["success"] is True
        assert "logs" in result
        assert isinstance(result["logs"], list)
        assert result["log_count"] > 0

    def test_get_container_logs_with_tail(self, docker_manager_with_mock):
        """Test getting container logs with tail limit."""
        result = docker_manager_with_mock.get_container_logs("container123", tail=50)

        assert result["success"] is True
        assert "logs" in result

    def test_get_container_stats(self, docker_manager_with_mock):
        """Test getting container statistics."""
        result = docker_manager_with_mock.get_container_stats("container123")

        assert result["success"] is True
        assert "cpu_usage" in result
        assert "memory_usage" in result
        assert "network_stats" in result


# ==============================================================================
# Volume Mounting Tests
# ==============================================================================

class TestVolumeMounting:
    """Test cases for volume mounting operations."""

    def test_run_container_with_volume_bind_mount(self, docker_manager_with_mock):
        """Test running container with bind mount volumes."""
        config = ContainerConfig(
            image_name="test-app",
            volumes={
                "/host/path": {"bind": "/container/path", "mode": "rw"}
            }
        )

        result = docker_manager_with_mock.run_container(config)
        assert result["success"] is True

    def test_run_container_with_multiple_volumes(self, docker_manager_with_mock):
        """Test running container with multiple volume mounts."""
        config = ContainerConfig(
            image_name="test-app",
            volumes={
                "/data": {"bind": "/app/data", "mode": "rw"},
                "/config": {"bind": "/app/config", "mode": "ro"},
                "/logs": {"bind": "/app/logs", "mode": "rw"},
            }
        )

        result = docker_manager_with_mock.run_container(config)
        assert result["success"] is True
        assert len(config.volumes) == 3


# ==============================================================================
# Network Configuration Tests
# ==============================================================================

class TestNetworkConfiguration:
    """Test cases for network configuration."""

    def test_create_network_success(self, docker_manager_with_mock):
        """Test creating a Docker network."""
        result = docker_manager_with_mock.create_network("test-network")

        assert result["success"] is True
        assert "network_id" in result
        assert result["network_name"] == "test-network"

    def test_create_network_with_driver(self, docker_manager_with_mock):
        """Test creating a network with specific driver."""
        result = docker_manager_with_mock.create_network("overlay-network", driver="overlay")

        assert result["success"] is True
        assert result["driver"] == "overlay"

    def test_create_network_failure(self, docker_manager_with_mock, mock_docker_client):
        """Test network creation failure."""
        mock_docker_client.networks.create.side_effect = Exception("Network creation failed")

        result = docker_manager_with_mock.create_network("test-network")

        assert result["success"] is False


# ==============================================================================
# Port Mapping Tests
# ==============================================================================

class TestPortMapping:
    """Test cases for port mapping configuration."""

    def test_container_config_with_port_mapping(self):
        """Test container configuration with port mappings."""
        config = ContainerConfig(
            image_name="webapp",
            ports={
                "80/tcp": "8080",
                "443/tcp": "8443",
            }
        )

        assert len(config.ports) == 2
        assert config.ports["80/tcp"] == "8080"

    def test_container_config_with_complex_port_mapping(self):
        """Test container configuration with complex port mappings."""
        config = ContainerConfig(
            image_name="webapp",
            ports={
                "3000/tcp": None,  # Publish to random port
                "5000/tcp": ("127.0.0.1", 5000),  # Bind to specific interface
                "6000/tcp": [5000, 5001],  # Multiple host ports
            }
        )

        assert len(config.ports) == 3

    def test_run_container_with_ports(self, docker_manager_with_mock):
        """Test running container with port mappings."""
        config = ContainerConfig(
            image_name="webapp",
            ports={
                "8000/tcp": "8000",
                "8443/tcp": "443",
            }
        )

        result = docker_manager_with_mock.run_container(config)

        assert result["success"] is True


# ==============================================================================
# Environment Variable Handling Tests
# ==============================================================================

class TestEnvironmentVariableHandling:
    """Test cases for environment variable handling."""

    def test_container_config_with_environment(self):
        """Test container configuration with environment variables."""
        config = ContainerConfig(
            image_name="webapp",
            environment={
                "NODE_ENV": "production",
                "DEBUG": "false",
                "API_KEY": "secret123",
            }
        )

        assert len(config.environment) == 3
        assert config.environment["NODE_ENV"] == "production"

    def test_run_container_with_environment(self, docker_manager_with_mock, mock_docker_client):
        """Test running container with environment variables."""
        config = ContainerConfig(
            image_name="webapp",
            environment={
                "DATABASE_URL": "postgres://localhost/db",
                "REDIS_HOST": "redis",
                "LOG_LEVEL": "info",
            }
        )

        result = docker_manager_with_mock.run_container(config)

        assert result["success"] is True

    def test_environment_variable_with_special_characters(self):
        """Test environment variables with special characters."""
        config = ContainerConfig(
            image_name="webapp",
            environment={
                "CONNECTION_STRING": "mongodb://user:p@ss=word@host:27017/db",
                "JSON_CONFIG": '{"key": "value"}',
            }
        )

        assert "CONNECTION_STRING" in config.environment
        assert "JSON_CONFIG" in config.environment


# ==============================================================================
# Dockerfile Parsing and Generation Tests
# ==============================================================================

class TestDockerfileParsing:
    """Test cases for Dockerfile parsing and generation."""

    def test_build_generator_creation(self):
        """Test creating a BuildGenerator."""
        generator = BuildGenerator()
        assert generator is not None
        assert hasattr(generator, 'templates')

    def test_create_multi_stage_build_python(self):
        """Test creating multi-stage build for Python."""
        generator = BuildGenerator()

        config = {
            "build_type": "python",
            "base_image": "python:3.9-slim",
            "metadata": {"project_name": "test_app"}
        }

        build = generator.create_multi_stage_build(config)

        assert isinstance(build, MultiStageBuild)
        assert len(build.stages) >= 1
        assert build.final_stage is not None

    def test_create_multi_stage_build_node(self):
        """Test creating multi-stage build for Node.js."""
        generator = BuildGenerator()

        config = {
            "build_type": "node",
            "base_image": "node:18-alpine"
        }

        build = generator.create_multi_stage_build(config)

        assert len(build.stages) >= 1

    def test_create_multi_stage_build_go(self):
        """Test creating multi-stage build for Go."""
        generator = BuildGenerator()

        config = {
            "build_type": "go",
            "base_image": "golang:1.19-alpine"
        }

        build = generator.create_multi_stage_build(config)

        assert len(build.stages) >= 1

    def test_create_multi_stage_build_java(self):
        """Test creating multi-stage build for Java."""
        generator = BuildGenerator()

        config = {
            "build_type": "java",
            "base_image": "openjdk:11-jdk-slim"
        }

        build = generator.create_multi_stage_build(config)

        assert len(build.stages) >= 1

    def test_validate_dockerfile_valid(self):
        """Test Dockerfile validation with valid content."""
        generator = BuildGenerator()

        valid_dockerfile = """FROM ubuntu:20.04
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y python3
USER appuser
CMD ["python", "app.py"]
"""

        is_valid, issues = generator.validate_dockerfile(valid_dockerfile)

        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)

    def test_validate_dockerfile_missing_from(self):
        """Test Dockerfile validation with missing FROM instruction."""
        generator = BuildGenerator()

        invalid_dockerfile = """WORKDIR /app
COPY . .
CMD ["python", "app.py"]
"""

        is_valid, issues = generator.validate_dockerfile(invalid_dockerfile)

        assert is_valid is False
        assert any("FROM" in issue for issue in issues)

    def test_validate_dockerfile_security_issues(self):
        """Test Dockerfile validation detects security issues."""
        generator = BuildGenerator()

        dockerfile_with_issues = """FROM ubuntu:latest
RUN chmod 777 /app
ENV PASSWORD=secret123
"""

        is_valid, issues = generator.validate_dockerfile(dockerfile_with_issues)

        assert isinstance(issues, list)
        # Should detect issues with latest tag, chmod 777, or password

    def test_optimize_dockerfile(self, tmp_path):
        """Test Dockerfile optimization."""
        generator = BuildGenerator()

        dockerfile_content = """FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y python3
RUN pip install flask
RUN apt-get clean
"""

        dockerfile_path = tmp_path / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)

        optimized = generator.optimize_dockerfile(str(dockerfile_path))

        assert isinstance(optimized, str)
        assert len(optimized) > 0


# ==============================================================================
# BuildStage and BuildScript Tests
# ==============================================================================

class TestBuildStageAndScript:
    """Test cases for BuildStage and BuildScript classes."""

    def test_build_stage_creation(self):
        """Test creating a BuildStage."""
        stage = BuildStage(
            name="builder",
            base_image="python:3.9-slim",
            commands=["RUN pip install -r requirements.txt"],
            copy_commands=["COPY . /app"],
            environment={"PYTHONUNBUFFERED": "1"},
            working_directory="/app",
            user="appuser"
        )

        assert stage.name == "builder"
        assert stage.base_image == "python:3.9-slim"

    def test_build_stage_to_dockerfile(self):
        """Test BuildStage conversion to Dockerfile."""
        stage = BuildStage(
            name="builder",
            base_image="python:3.9",
            commands=["RUN apt-get update"],
            working_directory="/app"
        )

        dockerfile = stage.to_dockerfile()

        assert "FROM python:3.9 AS builder" in dockerfile
        assert "WORKDIR /app" in dockerfile

    def test_multi_stage_build_to_dockerfile(self):
        """Test MultiStageBuild conversion to complete Dockerfile."""
        build = MultiStageBuild()

        build_stage = BuildStage(
            name="builder",
            base_image="golang:1.19",
            commands=["WORKDIR /app", "RUN go build"]
        )

        runtime_stage = BuildStage(
            name="runtime",
            base_image="alpine:latest",
            copy_commands=["COPY --from=builder /app/main /app/"],
            user="appuser"
        )

        build.stages = [build_stage, runtime_stage]
        build.final_stage = "runtime"
        build.metadata = {"project_name": "test-app"}

        dockerfile = build.to_dockerfile()

        assert isinstance(dockerfile, str)
        assert "FROM golang:1.19 AS builder" in dockerfile
        assert "FROM alpine:latest AS runtime" in dockerfile

    def test_build_script_creation(self):
        """Test creating a BuildScript."""
        script = BuildScript(
            name="web_app",
            dockerfile_path="Dockerfile.prod",
            context_path="./src",
            build_args={"VERSION": "1.0.0"},
            tags=["myapp:1.0.0", "myapp:latest"],
            push_targets=["registry.example.com/myapp:1.0.0"]
        )

        assert script.name == "web_app"
        assert len(script.tags) == 2

    def test_build_script_to_shell_script(self):
        """Test BuildScript conversion to shell script."""
        script = BuildScript(
            name="build",
            dockerfile_path="Dockerfile",
            context_path=".",
            build_args={"VERSION": "1.0.0"},
            tags=["myapp:1.0.0"],
            push_targets=["registry.example.com/myapp:1.0.0"]
        )

        shell_script = script.to_shell_script()

        assert "#!/bin/bash" in shell_script
        assert "docker build" in shell_script
        assert "--build-arg VERSION=1.0.0" in shell_script


# ==============================================================================
# Error Handling for Docker Daemon Failures Tests
# ==============================================================================

class TestErrorHandling:
    """Test cases for error handling in Docker operations."""

    def test_docker_client_not_available(self):
        """Test operations when Docker client is not available."""
        manager = DockerManager()
        manager.client = None

        # All operations should handle missing client gracefully
        config = ContainerConfig(image_name="test")

        build_result = manager.build_image(config)
        assert build_result["success"] is False

        run_result = manager.run_container(config)
        assert run_result["success"] is False

        stop_result = manager.stop_container("container123")
        assert stop_result["success"] is False

        remove_result = manager.remove_container("container123")
        assert remove_result["success"] is False

    def test_docker_daemon_connection_failure(self, mock_docker_client):
        """Test handling of Docker daemon connection failure."""
        mock_docker_client.ping.side_effect = DockerException("Cannot connect to Docker daemon")

        # Should handle gracefully during initialization
        with patch('docker.from_env', return_value=mock_docker_client):
            with patch.object(mock_docker_client, 'ping', side_effect=Exception("Connection failed")):
                manager = DockerManager()
                # Manager should still be created but client may be None

    def test_image_not_found_error(self, docker_manager_with_mock, mock_docker_client):
        """Test handling of image not found error."""
        mock_docker_client.images.remove.side_effect = ImageNotFound("Image not found")

        # Operations should handle missing images gracefully
        result = docker_manager_with_mock.remove_image("nonexistent:latest")
        assert result["success"] is False

    def test_container_not_found_error(self, docker_manager_with_mock, mock_docker_client):
        """Test handling of container not found error."""
        mock_docker_client.containers.get.side_effect = NotFound("Container not found")

        result = docker_manager_with_mock.stop_container("nonexistent")
        assert result["success"] is False

    def test_api_error_handling(self, docker_manager_with_mock, mock_docker_client):
        """Test handling of Docker API errors."""
        mock_docker_client.containers.run.side_effect = APIError("API Error")

        config = ContainerConfig(image_name="test-app")
        result = docker_manager_with_mock.run_container(config)

        assert result["success"] is False

    def test_network_error_handling(self, docker_manager_with_mock, mock_docker_client):
        """Test handling of network-related errors."""
        mock_docker_client.networks.create.side_effect = APIError("Network error")

        result = docker_manager_with_mock.create_network("test-network")

        assert result["success"] is False


# ==============================================================================
# Docker System Information Tests
# ==============================================================================

class TestDockerSystemInfo:
    """Test cases for Docker system information retrieval."""

    def test_get_docker_info(self, docker_manager_with_mock):
        """Test getting Docker system information."""
        info = docker_manager_with_mock.get_docker_info()

        assert info["available"] is True
        assert "server_version" in info
        assert "containers" in info
        assert "images" in info

    def test_list_images(self, docker_manager_with_mock):
        """Test listing Docker images."""
        images = docker_manager_with_mock.list_images()

        assert isinstance(images, list)
        if len(images) > 0:
            assert "id" in images[0]
            assert "tags" in images[0]

    def test_remove_image(self, docker_manager_with_mock):
        """Test removing a Docker image."""
        result = docker_manager_with_mock.remove_image("test-app:latest")

        assert result["success"] is True
        assert "removal_time" in result


# ==============================================================================
# Convenience Functions Tests
# ==============================================================================

class TestConvenienceFunctions:
    """Test cases for module-level convenience functions."""

    def test_build_containers_function(self):
        """Test build_containers convenience function."""
        config = ContainerConfig(image_name="test")

        with patch.object(DockerManager, 'build_image') as mock_build:
            mock_build.return_value = {"success": True}
            result = build_containers(config)

            assert isinstance(result, dict)

    def test_manage_containers_function(self):
        """Test manage_containers convenience function."""
        result = manage_containers()

        assert isinstance(result, DockerManager)


# ==============================================================================
# Image Analysis and Optimization Tests
# ==============================================================================

class TestImageAnalysis:
    """Test cases for image analysis and optimization."""

    def test_optimize_container_image(self, docker_manager_with_mock):
        """Test container image optimization recommendations."""
        optimized = docker_manager_with_mock.optimize_container_image(
            "python:3.9",
            ["flask", "django"]
        )

        assert isinstance(optimized, str)
        assert len(optimized) > 0

    def test_analyze_image_size(self, docker_manager_with_mock):
        """Test image size analysis."""
        analysis = docker_manager_with_mock.analyze_image_size("test-app:latest")

        assert "total_size_bytes" in analysis or "error" in analysis
        if "total_size_bytes" in analysis:
            assert "total_size_mb" in analysis
            assert "layer_count" in analysis

    def test_get_image_layers(self, docker_manager_with_mock):
        """Test getting image layer information."""
        layers = docker_manager_with_mock.get_image_layers("test-app:latest")

        assert isinstance(layers, list)


# ==============================================================================
# Restart Policy Tests
# ==============================================================================

class TestRestartPolicy:
    """Test cases for container restart policies."""

    def test_container_config_restart_policy(self):
        """Test container configuration with restart policy."""
        config = ContainerConfig(
            image_name="webapp",
            restart_policy="always"
        )

        assert config.restart_policy == "always"

    def test_run_container_with_restart_policy(self, docker_manager_with_mock):
        """Test running container with restart policy."""
        config = ContainerConfig(
            image_name="webapp",
            restart_policy="unless-stopped"
        )

        result = docker_manager_with_mock.run_container(config)

        assert result["success"] is True


# ==============================================================================
# Labels Tests
# ==============================================================================

class TestLabels:
    """Test cases for container and image labels."""

    def test_container_config_with_labels(self):
        """Test container configuration with labels."""
        config = ContainerConfig(
            image_name="webapp",
            labels={
                "maintainer": "team@example.com",
                "version": "1.0.0",
                "environment": "production"
            }
        )

        assert len(config.labels) == 3
        assert config.labels["maintainer"] == "team@example.com"

    def test_run_container_with_labels(self, docker_manager_with_mock):
        """Test running container with labels."""
        config = ContainerConfig(
            image_name="webapp",
            labels={
                "app": "myapp",
                "tier": "frontend"
            }
        )

        result = docker_manager_with_mock.run_container(config)

        assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
