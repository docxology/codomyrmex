import time
import pytest

import docker

from codomyrmex.container_optimization.mcp_tools import (
    container_optimization_analyze_image,
    container_optimization_suggest_optimizations,
    container_optimization_get_optimization_report,
    container_optimization_analyze_usage,
    container_optimization_suggest_limits,
)

@pytest.fixture(scope="session")
def docker_client():
    """Provides a Docker client for tests."""
    return docker.from_env()

@pytest.fixture(scope="module")
def existing_image(docker_client):
    """Uses an existing image to avoid build issues in restricted environments."""
    images = docker_client.images.list()
    if not images:
        pytest.skip("No Docker images available for testing")
    # Prefer non-sha256 tags if possible for better test visibility
    for img in images:
        if img.tags:
            return img.tags[0]
    return images[0].id

@pytest.fixture(scope="module")
def running_container(docker_client, existing_image):
    """Runs a container for testing resource tuning."""
    # We try to run the existing image if possible.
    # This might fail if the entrypoint is not suitable.
    try:
        container = docker_client.containers.run(
            existing_image,
            command="sleep 100",
            detach=True,
            remove=True
        )
        yield container
        try:
            container.stop(timeout=1)
        except Exception:
            pass
    except Exception as e:
        pytest.skip(f"Could not run container for test: {e}")

class TestContainerOptimizationMCPTools:
    """Zero-mock tests for Container Optimization MCP Tools."""

    def test_mcp_tool_analyze_image(self, existing_image):
        """Test container_optimization_analyze_image tool."""
        analysis = container_optimization_analyze_image(existing_image)
        assert isinstance(analysis, dict)
        assert "image_name" in analysis
        assert analysis["image_name"] == existing_image
        assert "size_mb" in analysis
        assert "layers_count" in analysis

    def test_mcp_tool_suggest_optimizations(self, existing_image):
        """Test container_optimization_suggest_optimizations tool."""
        suggestions = container_optimization_suggest_optimizations(existing_image)
        assert isinstance(suggestions, list)

    def test_mcp_tool_get_optimization_report(self, existing_image):
        """Test container_optimization_get_optimization_report tool."""
        report = container_optimization_get_optimization_report(existing_image)
        assert isinstance(report, dict)
        assert "analysis" in report
        assert "suggestions" in report
        assert "score" in report

    def test_mcp_tool_analyze_usage(self, running_container):
        """Test container_optimization_analyze_usage tool."""
        time.sleep(1) # Wait for stats to be available
        usage = container_optimization_analyze_usage(running_container.id)
        assert isinstance(usage, dict)
        assert "container_id" in usage
        assert usage["container_id"] == running_container.id
        assert "memory_usage_mb" in usage
        assert usage["memory_usage_mb"] > 0

    def test_mcp_tool_suggest_limits(self, running_container):
        """Test container_optimization_suggest_limits tool."""
        time.sleep(1) # Wait for stats to be available
        limits = container_optimization_suggest_limits(running_container.id)
        assert isinstance(limits, dict)
        assert "cpu_limit" in limits
        assert "memory_limit" in limits
        assert "reasoning" in limits
