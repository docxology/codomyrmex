"""Tests for logistics MCP tools.

Zero-mock tests that exercise queue stats, scheduled task listing,
and module status reporting.
"""

from __future__ import annotations

from codomyrmex.logistics.mcp_tools import (
    logistics_list_scheduled,
    logistics_queue_stats,
    logistics_status,
)


class TestLogisticsQueueStats:
    """Tests for logistics_queue_stats."""

    def test_default_backend(self):
        """Queue stats with default in_memory backend returns success."""
        result = logistics_queue_stats()
        assert result["status"] == "success"
        assert result["backend"] == "in_memory"
        assert isinstance(result["stats"], dict)

    def test_explicit_in_memory(self):
        """Explicit in_memory backend works."""
        result = logistics_queue_stats(backend="in_memory")
        assert result["status"] == "success"


class TestLogisticsListScheduled:
    """Tests for logistics_list_scheduled."""

    def test_empty_schedule(self):
        """Fresh schedule manager has no tasks."""
        result = logistics_list_scheduled()
        assert result["status"] == "success"
        assert result["task_ids"] == []
        assert result["count"] == 0


class TestLogisticsStatus:
    """Tests for logistics_status."""

    def test_returns_version(self):
        """Status includes version string."""
        result = logistics_status()
        assert result["status"] == "success"
        assert "version" in result
        assert isinstance(result["version"], str)

    def test_returns_components(self):
        """Status includes component list."""
        result = logistics_status()
        assert result["status"] == "success"
        assert isinstance(result["components"], list)
        assert len(result["components"]) > 0

    def test_known_components_present(self):
        """Key components appear in the list."""
        result = logistics_status()
        components = result["components"]
        assert "WorkflowManager" in components
        assert "Queue" in components
        assert "ScheduleManager" in components
