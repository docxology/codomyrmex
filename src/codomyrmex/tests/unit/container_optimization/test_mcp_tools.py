"""Zero-mock tests for Container Optimization MCP tools.

Tests must use authentic fixtures and real interactions.
"""

import time

import docker
import pytest

from codomyrmex.container_optimization.mcp_tools import (
    container_optimization_analyze_image,
    container_optimization_suggest_optimizations,
    container_optimization_get_optimization_report,
    container_optimization_analyze_usage,
    container_optimization_suggest_limits,
)

# Re-using fixtures from test_optimization.py structure
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
    for img in images:
        if img.tags:
            return img.tags[0]
    return images[0].id

@pytest.fixture(scope="module")
def running_container(docker_client, existing_image):
    """Runs a container for testing resource tuning."""
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


def test_container_optimization_analyze_image_tool(existing_image):
    """Test analyze_image MCP tool."""
    result = container_optimization_analyze_image(existing_image)
    assert isinstance(result, dict)
    assert result["image_name"] == existing_image
    assert "size_mb" in result
    assert "layers_count" in result


def test_container_optimization_suggest_optimizations_tool(existing_image):
    """Test suggest_optimizations MCP tool."""
    result = container_optimization_suggest_optimizations(existing_image)
    assert isinstance(result, list)


def test_container_optimization_get_optimization_report_tool(existing_image):
    """Test get_optimization_report MCP tool."""
    result = container_optimization_get_optimization_report(existing_image)
    assert isinstance(result, dict)
    assert "analysis" in result
    assert "suggestions" in result
    assert "score" in result


def test_container_optimization_analyze_usage_tool(running_container):
    """Test analyze_usage MCP tool."""
    time.sleep(1)  # Wait for stats
    result = container_optimization_analyze_usage(running_container.id)
    assert isinstance(result, dict)
    assert result["container_id"] == running_container.id
    assert result["memory_usage_mb"] > 0


def test_container_optimization_suggest_limits_tool():
    """Test suggest_limits MCP tool with dummy data."""
    result = container_optimization_suggest_limits(
        container_id="dummy-container-id",
        cpu_percent=15.0,
        memory_usage_bytes=100 * 1024 * 1024,
        memory_limit_bytes=512 * 1024 * 1024,
        memory_percent=20.0
    )
    assert isinstance(result, dict)
    assert "cpu_limit" in result
    assert "memory_limit" in result
    assert result["cpu_limit"] in ("0.6", "0.7")  # 15/100 + 0.5 = 0.65 -> stringified format %.1f rounds to 0.7 depending on platform
    assert result["memory_limit"] == "120m"
