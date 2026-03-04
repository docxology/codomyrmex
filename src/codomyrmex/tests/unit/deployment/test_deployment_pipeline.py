"""Tests for Sprint 19: Deployment Pipeline.

Tests for auto_build, health, canary.
"""

from __future__ import annotations

import os
import tempfile

import pytest

try:
    from codomyrmex.api.health import HealthStatus as _probe  # noqa: F401
    _API_AVAILABLE = True
except ImportError:
    _API_AVAILABLE = False

pytestmark = pytest.mark.skipif(not _API_AVAILABLE, reason="api extra not installed; run: uv sync --extra api")

try:
    from codomyrmex.api.health import (
        ComponentHealth,
        HealthChecker,
        HealthReport,
        HealthStatus,
    )
    from codomyrmex.containerization.auto_build import (
        AutoBuilder,
        DockerfileSpec,
        DockerStage,
    )
    from codomyrmex.deployment.canary import (
        CanaryAnalyzer,
        CanaryDecision,
        CanaryReport,
        MetricComparison,
    )
except ImportError:
    pytest.skip("api extra not installed; run: uv sync --extra api", allow_module_level=True)

# ── AutoBuilder ──────────────────────────────────────────────────


class TestDockerStage:
    """Test suite for DockerStage."""
    def test_render(self) -> None:
        """Verify render behavior."""
        stage = DockerStage("builder", "python:3.12", ["WORKDIR /build"])
        rendered = stage.render()
        assert "FROM python:3.12 AS builder" in rendered
        assert "WORKDIR /build" in rendered


class TestDockerfileSpec:
    """Test suite for DockerfileSpec."""
    def test_render_multi_stage(self) -> None:
        """Verify render multi stage behavior."""
        spec = DockerfileSpec(stages=[
            DockerStage("builder", "python:3.12", ["WORKDIR /build"]),
            DockerStage("runtime", "python:3.12-slim", ["WORKDIR /app"]),
        ])
        rendered = spec.render()
        assert "AS builder" in rendered
        assert "AS runtime" in rendered
        assert spec.stage_count == 2

    def test_labels(self) -> None:
        """Verify labels behavior."""
        spec = DockerfileSpec(
            stages=[DockerStage("app", "python:3.12")],
            labels={"version": "1.0"},
        )
        rendered = spec.render()
        assert 'LABEL version="1.0"' in rendered


class TestAutoBuilder:
    """Test suite for AutoBuilder."""
    def test_from_pyproject(self) -> None:
        """Verify from pyproject behavior."""
        content = '''
[project]
name = "my-app"
version = "1.2.3"
requires-python = ">=3.11"
'''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(content)
            f.flush()
            builder = AutoBuilder()
            spec = builder.from_pyproject(f.name)
            os.unlink(f.name)

        assert spec.project_name == "my-app"
        assert spec.python_version == "3.11"
        assert spec.stage_count == 2

    def test_default_spec(self) -> None:
        """Verify default spec behavior."""
        builder = AutoBuilder()
        spec = builder.default_spec()
        assert spec.stage_count == 2
        assert "python" in spec.render().lower()

    def test_from_config(self) -> None:
        """Verify from config behavior."""
        builder = AutoBuilder()
        spec = builder.from_config("myapp", "3.13", "server.py")
        rendered = spec.render()
        assert "server.py" in rendered

    def test_missing_file(self) -> None:
        """Verify missing file behavior."""
        builder = AutoBuilder()
        spec = builder.from_pyproject("/nonexistent.toml")
        assert spec.stage_count == 2  # Falls back to defaults


# ── HealthChecker ────────────────────────────────────────────────


class TestComponentHealth:
    """Test suite for ComponentHealth."""
    def test_to_dict(self) -> None:
        """Verify to dict behavior."""
        h = ComponentHealth("db", HealthStatus.HEALTHY, 5.2)
        d = h.to_dict()
        assert d["status"] == "healthy"


class TestHealthReport:
    """Test suite for HealthReport."""
    def test_is_healthy(self) -> None:
        """Verify is healthy behavior."""
        r = HealthReport(status=HealthStatus.HEALTHY)
        assert r.is_healthy
        r2 = HealthReport(status=HealthStatus.UNHEALTHY)
        assert not r2.is_healthy


class TestHealthChecker:
    """Test suite for HealthChecker."""
    def test_all_healthy(self) -> None:
        """Verify all healthy behavior."""
        checker = HealthChecker()
        checker.register("db", lambda: ComponentHealth("db"))
        checker.register("cache", lambda: ComponentHealth("cache"))
        report = checker.check()
        assert report.is_healthy
        assert report.component_count == 2

    def test_unhealthy_component(self) -> None:
        """Verify unhealthy component behavior."""
        checker = HealthChecker()
        checker.register("db", lambda: ComponentHealth("db", HealthStatus.UNHEALTHY))
        report = checker.check()
        assert not report.is_healthy

    def test_degraded_escalation(self) -> None:
        """Verify degraded escalation behavior."""
        checker = HealthChecker()
        checker.register("a", lambda: ComponentHealth("a", HealthStatus.DEGRADED))
        report = checker.check()
        assert report.status == HealthStatus.DEGRADED

    def test_check_fn_exception(self) -> None:
        """Verify check fn exception behavior."""
        checker = HealthChecker()
        checker.register("bad", lambda: 1 / 0)
        report = checker.check()
        assert not report.is_healthy

    def test_liveness(self) -> None:
        """Verify liveness behavior."""
        checker = HealthChecker()
        live = checker.liveness()
        assert live["status"] == "alive"

    def test_readiness(self) -> None:
        """Verify readiness behavior."""
        checker = HealthChecker()
        checker.register("ok", lambda: ComponentHealth("ok"))
        ready = checker.readiness()
        assert ready["ready"] is True


# ── CanaryAnalyzer ───────────────────────────────────────────────


class TestMetricComparison:
    """Test suite for MetricComparison."""
    def test_within_threshold(self) -> None:
        """Verify within threshold behavior."""
        mc = MetricComparison("err_rate", 0.01, 0.011, threshold=0.15)
        assert mc.passed

    def test_exceeds_threshold(self) -> None:
        """Verify exceeds threshold behavior."""
        mc = MetricComparison("err_rate", 0.01, 0.05, threshold=0.1)
        assert not mc.passed

    def test_zero_baseline(self) -> None:
        """Verify zero baseline behavior."""
        mc = MetricComparison("err_rate", 0.0, 0.005, threshold=0.01)
        assert mc.passed


class TestCanaryAnalyzer:
    """Test suite for CanaryAnalyzer."""
    def test_promote(self) -> None:
        """Verify promote behavior."""
        analyzer = CanaryAnalyzer(promote_threshold=0.9)
        report = analyzer.analyze(
            baseline={"err": 0.01, "latency": 200},
            canary={"err": 0.011, "latency": 205},
        )
        assert report.decision == CanaryDecision.PROMOTE

    def test_rollback(self) -> None:
        """Verify rollback behavior."""
        analyzer = CanaryAnalyzer(rollback_threshold=0.5)
        report = analyzer.analyze(
            baseline={"err": 0.01, "latency": 200},
            canary={"err": 0.1, "latency": 500},
        )
        assert report.decision == CanaryDecision.ROLLBACK

    def test_continue(self) -> None:
        """Verify continue behavior."""
        analyzer = CanaryAnalyzer(promote_threshold=0.9, rollback_threshold=0.3)
        report = analyzer.analyze(
            baseline={"a": 1.0, "b": 1.0, "c": 1.0},
            canary={"a": 1.0, "b": 2.0, "c": 1.0},  # b fails
        )
        assert report.decision == CanaryDecision.CONTINUE

    def test_custom_tolerances(self) -> None:
        """Verify custom tolerances behavior."""
        analyzer = CanaryAnalyzer()
        report = analyzer.analyze(
            baseline={"err": 0.01},
            canary={"err": 0.05},
            tolerances={"err": 5.0},  # Very tolerant
        )
        assert report.decision == CanaryDecision.PROMOTE

    def test_report_to_dict(self) -> None:
        """Verify report to dict behavior."""
        r = CanaryReport(decision=CanaryDecision.PROMOTE, pass_rate=1.0)
        d = r.to_dict()
        assert d["decision"] == "promote"
