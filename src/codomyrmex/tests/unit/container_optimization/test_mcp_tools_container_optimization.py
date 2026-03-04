"""Tests for container_optimization MCP tools.

Docker-dependent tools are skipped if Docker is not available.
"""

from __future__ import annotations

import pytest

try:
    import docker

    _client = docker.from_env()
    _client.ping()
    DOCKER_AVAILABLE = True
except Exception:
    DOCKER_AVAILABLE = False


class TestContainerOptimizationAnalyze:
    """Tests for container_optimization_analyze MCP tool."""

    @pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker not available")
    def test_analyze_nonexistent_image(self):
        from codomyrmex.container_optimization.mcp_tools import (
            container_optimization_analyze,
        )

        result = container_optimization_analyze(image_name="nonexistent_image_xyz_12345")
        assert result["status"] == "error"
        assert "message" in result

    def test_analyze_returns_dict(self):
        """Verify the tool function exists and is callable."""
        from codomyrmex.container_optimization.mcp_tools import (
            container_optimization_analyze,
        )

        assert callable(container_optimization_analyze)


class TestContainerOptimizationReport:
    """Tests for container_optimization_report MCP tool."""

    @pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker not available")
    def test_report_nonexistent_image(self):
        from codomyrmex.container_optimization.mcp_tools import (
            container_optimization_report,
        )

        result = container_optimization_report(image_name="nonexistent_image_xyz_12345")
        assert result["status"] == "error"

    def test_report_callable(self):
        from codomyrmex.container_optimization.mcp_tools import (
            container_optimization_report,
        )

        assert callable(container_optimization_report)


class TestContainerOptimizationTuneResources:
    """Tests for container_optimization_tune_resources MCP tool."""

    @pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker not available")
    def test_tune_nonexistent_container(self):
        from codomyrmex.container_optimization.mcp_tools import (
            container_optimization_tune_resources,
        )

        result = container_optimization_tune_resources(container_id="nonexistent_container_xyz")
        assert result["status"] == "error"

    def test_tune_callable(self):
        from codomyrmex.container_optimization.mcp_tools import (
            container_optimization_tune_resources,
        )

        assert callable(container_optimization_tune_resources)
