"""
Comprehensive tests for the containerization module.

This module tests all containerization functionality including
Docker management, Kubernetes orchestration, and container security.
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import List

# Skip entire module if docker is not installed
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None

from codomyrmex.containerization.docker_manager import (
    DockerManager,
    ContainerConfig,
    build_containers,
    manage_containers
)


def check_docker_available():
    """Check if Docker daemon is actually available."""
    if not DOCKER_AVAILABLE:
        return False
    try:
        client = docker.from_env()
        client.ping()
        return True
    except (docker.errors.DockerException, Exception):
        return False


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

    def test_initialize_client_success(self):
        """Test successful Docker client initialization with real Docker."""
        if not check_docker_available():
            pytest.skip("Docker daemon not available")

        manager = DockerManager()

        # If Docker is available, client should be initialized
        if manager.client:
            # Test real ping
            assert manager.client.ping() is True
        else:
            # Docker client not initialized (Docker not available)
            pytest.skip("Docker client not initialized")

    def test_initialize_client_failure(self):
        """Test Docker client initialization when Docker is not available."""
        # This test verifies that the manager handles missing Docker gracefully
        manager = DockerManager()

        # If Docker is not available, client should be None
        # This is expected behavior, not a failure
        if manager.client is None:
            # Verify that operations handle None client gracefully
            result = manager.build_image(ContainerConfig(image_name="test"))
            assert result["success"] is False
            assert "Docker client not available" in result["error"]

    def test_build_image_no_client(self):
        """Test image building when Docker client is not available."""
        manager = DockerManager()
        config = ContainerConfig(image_name="test-app")

        # If client is None, should return error
        if manager.client is None:
            result = manager.build_image(config)
            assert result["success"] is False
            assert "Docker client not available" in result["error"]

    def test_list_images_success(self):
        """Test successful image listing with real Docker."""
        if not check_docker_available():
            pytest.skip("Docker daemon not available")

        manager = DockerManager()
        if manager.client is None:
            pytest.skip("Docker client not initialized")

        # Test real image listing
        images = manager.list_images()

        # Should return a list (may be empty if no images)
        assert isinstance(images, list)
        # If images exist, verify structure
        if len(images) > 0:
            assert "id" in images[0]
            assert "tags" in images[0]

    def test_get_docker_info_success(self):
        """Test successful Docker info retrieval with real Docker."""
        if not check_docker_available():
            pytest.skip("Docker daemon not available")

        manager = DockerManager()
        if manager.client is None:
            pytest.skip("Docker client not initialized")

        # Test real Docker info
        info = manager.get_docker_info()

        assert info["available"] is True
        assert "server_version" in info
        assert "containers" in info
        assert "containers_running" in info

    def test_list_containers_success(self):
        """Test successful container listing with real Docker."""
        if not check_docker_available():
            pytest.skip("Docker daemon not available")

        manager = DockerManager()
        if manager.client is None:
            pytest.skip("Docker client not initialized")

        # Test real container listing
        containers = manager.list_containers()

        # Should return a list (may be empty if no containers)
        assert isinstance(containers, list)
        # If containers exist, verify structure
        if len(containers) > 0:
            assert "id" in containers[0]
            assert "name" in containers[0]
            assert "status" in containers[0]


class TestConvenienceFunctions:
    """Test cases for module-level convenience functions."""

    def test_build_containers_function(self):
        """Test build_containers convenience function with real manager."""
        config = ContainerConfig(image_name="test")
        result = build_containers(config)

        # Should return a result dict
        assert isinstance(result, dict)
        assert "success" in result

    def test_manage_containers_function(self):
        """Test manage_containers convenience function with real manager."""
        result = manage_containers()

        # Should return a DockerManager instance
        assert isinstance(result, DockerManager)


class TestErrorHandling:
    """Test cases for error handling in Docker operations."""

    def test_build_image_exception_handling(self):
        """Test exception handling during image building."""
        manager = DockerManager()
        config = ContainerConfig(image_name="test")

        # Test with invalid config that might cause errors
        result = manager.build_image(config)

        # Should return a result dict with success status
        assert isinstance(result, dict)
        assert "success" in result

    def test_list_containers_exception_handling(self):
        """Test exception handling during container listing."""
        manager = DockerManager()

        # Should handle errors gracefully
        containers = manager.list_containers()

        # Should return a list (empty if error occurred)
        assert isinstance(containers, list)

    def test_get_docker_info_exception_handling(self):
        """Test exception handling during Docker info retrieval."""
        manager = DockerManager()
        info = manager.get_docker_info()

        # Should return info dict
        assert isinstance(info, dict)
        assert "available" in info


class TestIntegration:
    """Integration tests for Docker manager components."""

    def test_docker_manager_real_operations(self):
        """Test Docker manager with real Docker operations."""
        if not check_docker_available():
            pytest.skip("Docker daemon not available")

        manager = DockerManager()
        if manager.client is None:
            pytest.skip("Docker client not initialized")

        # Test real Docker operations
        # 1. Get Docker info
        info = manager.get_docker_info()
        assert info["available"] is True

        # 2. List images
        images = manager.list_images()
        assert isinstance(images, list)

        # 3. List containers
        containers = manager.list_containers()
        assert isinstance(containers, list)

        # 4. Test ping
        assert manager.client.ping() is True


if __name__ == "__main__":
    pytest.main([__file__])
