"""Integration tests for Resource Monitoring limits."""

from codomyrmex.agents.hermes import monitoring
from codomyrmex.agents.hermes.mcp_tools import hermes_system_health
from codomyrmex.coding.execution.executor import execute_code


def test_hermes_system_health_tool():
    """Verify that hermes_system_health returns active system constraints."""
    res = hermes_system_health()

    assert res["status"] == "success"
    metrics = res["metrics"]

    assert "cpu_percent" in metrics
    assert "ram_usage_percent" in metrics
    assert "ram_available_mb" in metrics
    assert "ram_total_mb" in metrics
    assert "swap_usage_percent" in metrics
    assert isinstance(metrics["ram_usage_percent"], float)
    assert isinstance(metrics["ram_available_mb"], float)


def test_execution_aborted_on_high_memory(monkeypatch):
    """Verify code execution aborts automatically if memory is constrained natively."""

    def mock_metrics():
        return {
            "cpu_percent": 50.0,
            "ram_usage_percent": 99.0,
            "ram_available_mb": 128.0,
            "ram_total_mb": 4096.0,
            "swap_usage_percent": 10.0,
        }

    monkeypatch.setattr(monitoring, "_get_system_metrics", mock_metrics)

    res = execute_code(language="python", code="print('hello')", timeout=5)

    assert res["status"] == "setup_error"
    assert res["exit_code"] == -1
    assert "critical capacity" in res["stderr"]
    assert "constraint exceeded" in res["error_message"]
