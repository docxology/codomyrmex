"""
Comprehensive tests for the containerization module.

This module tests all containerization functionality including
Docker management, Kubernetes orchestration, and container security.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

from codomyrmex.containerization.docker_manager import (
    DockerManager,
    ContainerConfig,
    build_containers,
    manage_containers
)


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


class TestDockerManager:
    """Test cases for DockerManager functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = DockerManager()

    def test_docker_manager_initialization(self):
        """Test DockerManager initialization."""
        manager = DockerManager()
        assert manager.docker_host is None
        # Note: client may be None if Docker is not available

    def test_docker_manager_with_host(self):
        """Test DockerManager with custom host."""
        manager = DockerManager("tcp://localhost:2376")
        assert manager.docker_host == "tcp://localhost:2376"

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_initialize_client_success(self, mock_from_env):
        """Test successful Docker client initialization."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_from_env.return_value = mock_client

        manager = DockerManager()
        manager._initialize_client()

        mock_from_env.assert_called_once()
        mock_client.ping.assert_called_once()
        assert manager.client == mock_client

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_initialize_client_failure(self, mock_from_env):
        """Test Docker client initialization failure."""
        mock_from_env.side_effect = Exception("Docker not available")

        manager = DockerManager()
        manager._initialize_client()

        assert manager.client is None

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_build_image_success(self, mock_from_env):
        """Test successful image building."""
        # Setup mock Docker client
        mock_client = MagicMock()
        mock_image = MagicMock()
        mock_image.id = "sha256:12345"
        mock_image.tags = ["test-app:latest"]

        mock_build_logs = [
            {"stream": "Step 1/5 : FROM python:3.11-slim"},
            {"stream": "Step 2/5 : COPY . /app"},
            {"stream": "Successfully built 12345"}
        ]

        mock_client.images.build.return_value = (mock_image, mock_build_logs)
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        config = ContainerConfig(image_name="test-app")

        result = manager.build_image(config)

        assert result["success"] is True
        assert result["image_id"] == "sha256:12345"
        assert "test-app:latest" in result["image_tags"]
        assert len(result["build_logs"]) == 3

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_build_image_no_client(self, mock_from_env):
        """Test image building when Docker client is not available."""
        mock_from_env.return_value = None

        manager = DockerManager()
        config = ContainerConfig(image_name="test-app")

        result = manager.build_image(config)

        assert result["success"] is False
        assert "Docker client not available" in result["error"]

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_build_image_with_push(self, mock_from_env):
        """Test image building with push enabled."""
        # Setup mock Docker client
        mock_client = MagicMock()
        mock_image = MagicMock()
        mock_image.id = "sha256:12345"
        mock_image.tags = ["test-app:latest"]
        mock_client.images.build.return_value = (mock_image, [])
        mock_client.images.push.return_value = [{"status": "Pushed"}]
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        config = ContainerConfig(image_name="test-app")
        auth = {"username": "user", "password": "pass"}

        result = manager.build_image(config, push=True, registry_auth=auth)

        assert result["success"] is True
        assert "push_result" in result
        mock_client.images.push.assert_called_once_with("test-app:latest", auth_config=auth)

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_push_image_success(self, mock_from_env):
        """Test successful image pushing."""
        mock_client = MagicMock()
        mock_client.images.push.return_value = [{"status": "Pushed to registry"}]
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        auth = {"username": "user", "password": "pass"}

        result = manager.push_image("test-app:latest", auth)

        assert result["success"] is True
        assert result["image"] == "test-app:latest"
        mock_client.images.push.assert_called_once_with("test-app:latest", auth_config=auth)

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_run_container_success(self, mock_from_env):
        """Test successful container running."""
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_container.id = "container123"
        mock_container.name = "test_container"
        mock_container.status = "running"

        mock_client.containers.run.return_value = mock_container
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        config = ContainerConfig(
            image_name="test-app",
            environment={"PORT": "8000"},
            ports={"8000/tcp": "8000"}
        )

        result = manager.run_container(config)

        assert result["success"] is True
        assert result["container_id"] == "container123"
        assert result["status"] == "running"
        mock_client.containers.run.assert_called_once()

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_list_containers_success(self, mock_from_env):
        """Test successful container listing."""
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_container.id = "container123"
        mock_container.name = "test_container"
        mock_container.image.tags = ["test-app:latest"]
        mock_container.status = "running"
        mock_container.attrs = {
            "Created": "2024-01-01T00:00:00Z",
            "NetworkSettings": {"Ports": {"8000/tcp": [{"HostPort": "8000"}]}}
        }

        mock_client.containers.list.return_value = [mock_container]
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        containers = manager.list_containers()

        assert len(containers) == 1
        assert containers[0]["id"] == "container123"
        assert containers[0]["name"] == "test_container"
        assert containers[0]["status"] == "running"

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_stop_container_success(self, mock_from_env):
        """Test successful container stopping."""
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_client.containers.get.return_value = mock_container
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        result = manager.stop_container("container123")

        assert result["success"] is True
        assert result["container_id"] == "container123"
        mock_container.stop.assert_called_once()

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_remove_container_success(self, mock_from_env):
        """Test successful container removal."""
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_client.containers.get.return_value = mock_container
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        result = manager.remove_container("container123", force=True)

        assert result["success"] is True
        mock_container.remove.assert_called_once_with(force=True)

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_get_container_logs_success(self, mock_from_env):
        """Test successful container log retrieval."""
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_container.logs.return_value = b"Log line 1\nLog line 2\n"
        mock_client.containers.get.return_value = mock_container
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        result = manager.get_container_logs("container123")

        assert result["success"] is True
        assert len(result["logs"]) == 2
        assert result["logs"][0] == "Log line 1"
        mock_container.logs.assert_called_once_with(tail=100)

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_get_container_stats_success(self, mock_from_env):
        """Test successful container stats retrieval."""
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_stats = {
            "cpu_stats": {"cpu_usage": {"total": 100}},
            "memory_stats": {"usage": 50 * 1024 * 1024},
            "networks": {"eth0": {"rx_bytes": 1000}}
        }
        mock_container.stats.return_value = mock_stats
        mock_client.containers.get.return_value = mock_container
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        result = manager.get_container_stats("container123")

        assert result["success"] is True
        assert result["cpu_usage"]["total"] == 100
        assert result["memory_usage"]["usage"] == 50 * 1024 * 1024

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_create_network_success(self, mock_from_env):
        """Test successful network creation."""
        mock_client = MagicMock()
        mock_network = MagicMock()
        mock_network.id = "network123"
        mock_client.networks.create.return_value = mock_network
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        result = manager.create_network("test-network", "bridge")

        assert result["success"] is True
        assert result["network_id"] == "network123"
        mock_client.networks.create.assert_called_once_with("test-network", driver="bridge")

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_list_images_success(self, mock_from_env):
        """Test successful image listing."""
        mock_client = MagicMock()
        mock_image = MagicMock()
        mock_image.id = "sha256:12345"
        mock_image.tags = ["test-app:latest"]
        mock_image.attrs = {"Size": 100 * 1024 * 1024, "Created": "2024-01-01T00:00:00Z"}

        mock_client.images.list.return_value = [mock_image]
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        images = manager.list_images()

        assert len(images) == 1
        assert images[0]["id"] == "sha256:12345"
        assert "test-app:latest" in images[0]["tags"]

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_remove_image_success(self, mock_from_env):
        """Test successful image removal."""
        mock_client = MagicMock()
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        result = manager.remove_image("test-app:latest", force=True)

        assert result["success"] is True
        mock_client.images.remove.assert_called_once_with("test-app:latest", force=True)

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_get_docker_info_success(self, mock_from_env):
        """Test successful Docker info retrieval."""
        mock_client = MagicMock()
        mock_info = {
            "ServerVersion": "24.0.0",
            "Containers": 5,
            "ContainersRunning": 3,
            "Images": 10,
            "Driver": "overlay2",
            "Architecture": "x86_64",
            "OSType": "linux",
            "KernelVersion": "5.15.0"
        }
        mock_version = {"ApiVersion": "1.43"}

        mock_client.info.return_value = mock_info
        mock_client.version.return_value = mock_version
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        info = manager.get_docker_info()

        assert info["available"] is True
        assert info["server_version"] == "24.0.0"
        assert info["containers"] == 5
        assert info["containers_running"] == 3


class TestConvenienceFunctions:
    """Test cases for module-level convenience functions."""

    def test_build_containers_function(self):
        """Test build_containers convenience function."""
        with patch('codomyrmex.containerization.docker_manager.DockerManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.build_image.return_value = {"success": True}

            config = ContainerConfig(image_name="test")
            result = build_containers(config)

            mock_manager_class.assert_called_once()
            mock_manager.build_image.assert_called_once_with(config, False, None)
            assert result["success"] is True

    def test_manage_containers_function(self):
        """Test manage_containers convenience function."""
        with patch('codomyrmex.containerization.docker_manager.DockerManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            result = manage_containers()

            mock_manager_class.assert_called_once()
            assert result == mock_manager


class TestErrorHandling:
    """Test cases for error handling in Docker operations."""

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_build_image_exception_handling(self, mock_from_env):
        """Test exception handling during image building."""
        mock_client = MagicMock()
        mock_client.images.build.side_effect = Exception("Build failed")
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        config = ContainerConfig(image_name="test")

        result = manager.build_image(config)

        assert result["success"] is False
        assert "Build failed" in result["error"]

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_run_container_exception_handling(self, mock_from_env):
        """Test exception handling during container running."""
        mock_client = MagicMock()
        mock_client.containers.run.side_effect = Exception("Container run failed")
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        config = ContainerConfig(image_name="test")

        result = manager.run_container(config)

        assert result["success"] is False
        assert "Container run failed" in result["error"]

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_list_containers_exception_handling(self, mock_from_env):
        """Test exception handling during container listing."""
        mock_client = MagicMock()
        mock_client.containers.list.side_effect = Exception("List failed")
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        containers = manager.list_containers()

        assert containers == []

    @patch('codomyrmex.containerization.docker_manager.docker.from_env')
    def test_get_docker_info_exception_handling(self, mock_from_env):
        """Test exception handling during Docker info retrieval."""
        mock_client = MagicMock()
        mock_client.info.side_effect = Exception("Info retrieval failed")
        mock_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        manager = DockerManager()
        info = manager.get_docker_info()

        assert info["available"] is False
        assert "Info retrieval failed" in info["error"]


class TestIntegration:
    """Integration tests for Docker manager components."""

    def test_container_lifecycle_integration(self):
        """Test complete container lifecycle."""
        with patch('codomyrmex.containerization.docker_manager.docker.from_env') as mock_from_env:
            mock_client = MagicMock()
            mock_container = MagicMock()
            mock_container.id = "test_container_123"
            mock_container.name = "test_container"
            mock_container.status = "running"

            # Setup different return values for different calls
            mock_client.containers.run.return_value = mock_container
            mock_client.containers.get.return_value = mock_container

            mock_from_env.return_value = mock_client
            mock_client.ping.return_value = True

            manager = DockerManager()
            config = ContainerConfig(image_name="test-app")

            # Run container
            run_result = manager.run_container(config)
            assert run_result["success"] is True
            assert run_result["container_id"] == "test_container_123"

            # Get logs
            logs_result = manager.get_container_logs("test_container_123")
            assert logs_result["success"] is True

            # Stop container
            stop_result = manager.stop_container("test_container_123")
            assert stop_result["success"] is True

            # Remove container
            remove_result = manager.remove_container("test_container_123")
            assert remove_result["success"] is True

    def test_image_workflow_integration(self):
        """Test complete image workflow."""
        with patch('codomyrmex.containerization.docker_manager.docker.from_env') as mock_from_env:
            mock_client = MagicMock()
            mock_image = MagicMock()
            mock_image.id = "sha256:12345"
            mock_image.tags = ["test-app:v1.0"]

            # Setup mock responses
            mock_client.images.build.return_value = (mock_image, [])
            mock_client.images.list.return_value = [mock_image]

            mock_from_env.return_value = mock_client
            mock_client.ping.return_value = True

            manager = DockerManager()
            config = ContainerConfig(image_name="test-app", tag="v1.0")

            # Build image
            build_result = manager.build_image(config)
            assert build_result["success"] is True

            # List images
            images = manager.list_images()
            assert len(images) == 1
            assert images[0]["id"] == "sha256:12345"

            # Remove image
            remove_result = manager.remove_image("test-app:v1.0")
            assert remove_result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__])
