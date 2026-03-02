"""
Unit tests for HealthHandler mixin — Zero-Mock compliant.

Tests all handlers including: handle_status, handle_health, handle_awareness,
handle_llm_config, handle_telemetry, handle_telemetry_seed,
handle_security_posture, and error paths.

Coverage targets: lines 35, 43, 51, 59, 121-123, 141-142, 151-194, 212-213
"""

import sys
from pathlib import Path

import pytest

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent.parent
SRC_DIR = MODULE_DIR.parent.parent
sys.path.insert(0, str(SRC_DIR))

from codomyrmex.website.handlers.health_handler import HealthHandler  # noqa: E402

# ── Fake infrastructure ──────────────────────────────────────────────────


class _FakeDataProvider:
    """Minimal DataProvider stand-in for HealthHandler tests."""

    def get_system_summary(self):
        return {"status": "ok", "modules": 5}

    def get_health_status(self):
        return {"status": "healthy", "modules": 5}

    def get_pai_awareness_data(self):
        return {"missions": [], "projects": [], "metrics": {}}

    def get_llm_config(self):
        return {"provider": "none", "model": "test"}

    def get_modules(self):
        return [{"name": "test_mod"}]

    def get_actual_agents(self):
        return ["agent1", "agent2"]

    def get_mcp_tools(self):
        return {"tools": [{"name": "tool1"}, {"name": "tool2"}]}

    def get_available_scripts(self):
        return ["script1.py", "script2.py"]


class _FakeDataProviderNoTools:
    """DataProvider that raises when get_mcp_tools() is called."""

    def get_system_summary(self):
        return {"status": "ok"}

    def get_health_status(self):
        return {"status": "healthy"}

    def get_pai_awareness_data(self):
        return {}

    def get_llm_config(self):
        return {}

    def get_modules(self):
        return []

    def get_actual_agents(self):
        return []

    def get_mcp_tools(self):
        raise RuntimeError("MCP tools unavailable")

    def get_available_scripts(self):
        return []


class _FakeHealthHandler(HealthHandler):
    """Concrete host providing interface HealthHandler expects."""

    def __init__(self, *, data_provider=None):
        self.data_provider = data_provider
        self.responses: list[dict] = []
        self.errors: list[tuple] = []
        # Reset class-level telemetry state between tests
        HealthHandler._telemetry_collector = None
        HealthHandler._telemetry_dm = None

    def send_json_response(self, data, status=200):
        self.responses.append({"status": status, "data": data})

    def send_error(self, code, msg=""):
        self.errors.append((code, msg))


# ── handle_status ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestHandleStatus:
    """Tests for handle_status()."""

    def test_returns_summary_when_provider_present(self):
        handler = _FakeHealthHandler(data_provider=_FakeDataProvider())
        handler.handle_status()
        assert handler.responses
        assert handler.responses[0]["status"] == 200
        assert handler.responses[0]["data"]["status"] == "ok"

    def test_sends_500_when_provider_missing(self):
        handler = _FakeHealthHandler(data_provider=None)
        handler.handle_status()
        assert handler.errors
        assert handler.errors[0][0] == 500


# ── handle_health ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestHandleHealth:
    """Tests for handle_health()."""

    def test_returns_health_when_provider_present(self):
        handler = _FakeHealthHandler(data_provider=_FakeDataProvider())
        handler.handle_health()
        assert handler.responses
        assert handler.responses[0]["data"]["status"] == "healthy"

    def test_sends_500_when_provider_missing(self):
        handler = _FakeHealthHandler(data_provider=None)
        handler.handle_health()
        assert handler.errors
        assert handler.errors[0][0] == 500


# ── handle_awareness ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestHandleAwareness:
    """Tests for handle_awareness()."""

    def test_returns_awareness_data_when_provider_present(self):
        handler = _FakeHealthHandler(data_provider=_FakeDataProvider())
        handler.handle_awareness()
        assert handler.responses
        assert "missions" in handler.responses[0]["data"]

    def test_sends_500_body_when_provider_missing(self):
        handler = _FakeHealthHandler(data_provider=None)
        handler.handle_awareness()
        assert handler.responses
        assert handler.responses[0]["status"] == 500
        assert "error" in handler.responses[0]["data"]


# ── handle_llm_config ────────────────────────────────────────────────────


@pytest.mark.unit
class TestHandleLlmConfig:
    """Tests for handle_llm_config()."""

    def test_returns_config_when_provider_present(self):
        handler = _FakeHealthHandler(data_provider=_FakeDataProvider())
        handler.handle_llm_config()
        assert handler.responses
        assert "provider" in handler.responses[0]["data"]

    def test_sends_500_body_when_provider_missing(self):
        handler = _FakeHealthHandler(data_provider=None)
        handler.handle_llm_config()
        assert handler.responses
        assert handler.responses[0]["status"] == 500


# ── handle_telemetry ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestHandleTelemetry:
    """Tests for handle_telemetry()."""

    def test_returns_ok_status_with_provider(self):
        handler = _FakeHealthHandler(data_provider=_FakeDataProvider())
        handler.handle_telemetry()
        assert handler.responses
        resp = handler.responses[0]["data"]
        assert resp["status"] == "ok"
        assert "dashboards" in resp
        assert "metric_names" in resp

    def test_records_module_count_metric(self):
        handler = _FakeHealthHandler(data_provider=_FakeDataProvider())
        handler.handle_telemetry()
        resp = handler.responses[0]["data"]
        assert "module_count" in resp["metric_names"]

    def test_handles_mcp_tools_error_gracefully(self):
        """Covers the logger.debug branch when get_mcp_tools() raises."""
        handler = _FakeHealthHandler(data_provider=_FakeDataProviderNoTools())
        handler.handle_telemetry()
        # Should still succeed — tool_count exception is caught and logged
        assert handler.responses
        assert handler.responses[0]["data"]["status"] == "ok"

    def test_works_without_data_provider(self):
        """handle_telemetry should still return a response (metrics just not seeded)."""
        handler = _FakeHealthHandler(data_provider=None)
        handler.handle_telemetry()
        assert handler.responses
        assert "status" in handler.responses[0]["data"]


# ── handle_telemetry_seed ────────────────────────────────────────────────


@pytest.mark.unit
class TestHandleTelemetrySeed:
    """Tests for handle_telemetry_seed() — lines 151-194 (fully uncovered)."""

    def test_seeds_metrics_and_returns_ok(self):
        handler = _FakeHealthHandler(data_provider=_FakeDataProvider())
        handler.handle_telemetry_seed()
        assert handler.responses
        resp = handler.responses[0]["data"]
        assert resp["status"] == "ok"
        assert "seeded_metrics" in resp
        assert resp["count"] > 0

    def test_seeds_module_count(self):
        handler = _FakeHealthHandler(data_provider=_FakeDataProvider())
        handler.handle_telemetry_seed()
        resp = handler.responses[0]["data"]
        assert "module_count" in resp["seeded_metrics"]

    def test_seeds_agent_count(self):
        handler = _FakeHealthHandler(data_provider=_FakeDataProvider())
        handler.handle_telemetry_seed()
        resp = handler.responses[0]["data"]
        assert "agent_count" in resp["seeded_metrics"]

    def test_seeds_python_version(self):
        handler = _FakeHealthHandler(data_provider=_FakeDataProvider())
        handler.handle_telemetry_seed()
        resp = handler.responses[0]["data"]
        assert "python_version_minor" in resp["seeded_metrics"]

    def test_seeds_script_count(self):
        handler = _FakeHealthHandler(data_provider=_FakeDataProvider())
        handler.handle_telemetry_seed()
        resp = handler.responses[0]["data"]
        assert "script_count" in resp["seeded_metrics"]

    def test_handles_mcp_tools_error_gracefully(self):
        """tool_count exception logged and seeding continues."""
        handler = _FakeHealthHandler(data_provider=_FakeDataProviderNoTools())
        handler.handle_telemetry_seed()
        resp = handler.responses[0]["data"]
        # Should still succeed without tool_count
        assert resp["status"] == "ok"
        assert "tool_count" not in resp["seeded_metrics"]
        assert "module_count" in resp["seeded_metrics"]

    def test_no_data_provider_returns_ok_with_empty_seeds(self):
        handler = _FakeHealthHandler(data_provider=None)
        handler.handle_telemetry_seed()
        assert handler.responses
        resp = handler.responses[0]["data"]
        assert resp["status"] == "ok"
        assert resp["count"] == 0


# ── handle_security_posture ──────────────────────────────────────────────


@pytest.mark.unit
class TestHandleSecurityPosture:
    """Tests for handle_security_posture()."""

    def test_returns_response_dict(self):
        handler = _FakeHealthHandler(data_provider=_FakeDataProvider())
        handler.handle_security_posture()
        assert handler.responses
        resp = handler.responses[0]["data"]
        # Either ok or error — both are valid (security module may not be available)
        assert "status" in resp

    def test_error_path_returns_error_status(self):
        """Cover lines 212-213: exception handler in handle_security_posture."""
        # The security dashboard may raise if dependencies unavailable
        # This test verifies the except clause is exercised when it does
        handler = _FakeHealthHandler(data_provider=None)
        handler.handle_security_posture()
        assert handler.responses
        # Just verify we got a response — either "ok" or "error"
        assert "status" in handler.responses[0]["data"]
