"""Tests for Sprint 19: Deployment Pipeline.

Tests for auto_build, health, canary.
"""

from __future__ import annotations

import os
import tempfile

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

# ── AutoBuilder ──────────────────────────────────────────────────


class TestDockerStage:
    """Test suite for DockerStage."""
    def test_render(self) -> None:
        """Test functionality: render."""
        stage = DockerStage("builder", "python:3.12", ["WORKDIR /build"])
        rendered = stage.render()
        assert "FROM python:3.12 AS builder" in rendered
        assert "WORKDIR /build" in rendered


class TestDockerfileSpec:
    """Test suite for DockerfileSpec."""
    def test_render_multi_stage(self) -> None:
        """Test functionality: render multi stage."""
        spec = DockerfileSpec(stages=[
            DockerStage("builder", "python:3.12", ["WORKDIR /build"]),
            DockerStage("runtime", "python:3.12-slim", ["WORKDIR /app"]),
        ])
        rendered = spec.render()
        assert "AS builder" in rendered
        assert "AS runtime" in rendered
        assert spec.stage_count == 2

    def test_labels(self) -> None:
        """Test functionality: labels."""
        spec = DockerfileSpec(
            stages=[DockerStage("app", "python:3.12")],
            labels={"version": "1.0"},
        )
        rendered = spec.render()
        assert 'LABEL version="1.0"' in rendered


class TestAutoBuilder:
    """Test suite for AutoBuilder."""
    def test_from_pyproject(self) -> None:
        """Test functionality: from pyproject."""
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
        """Test functionality: default spec."""
        builder = AutoBuilder()
        spec = builder.default_spec()
        assert spec.stage_count == 2
        assert "python" in spec.render().lower()

    def test_from_config(self) -> None:
        """Test functionality: from config."""
        builder = AutoBuilder()
        spec = builder.from_config("myapp", "3.13", "server.py")
        rendered = spec.render()
        assert "server.py" in rendered

    def test_missing_file(self) -> None:
        """Test functionality: missing file."""
        builder = AutoBuilder()
        spec = builder.from_pyproject("/nonexistent.toml")
        assert spec.stage_count == 2  # Falls back to defaults


# ── HealthChecker ────────────────────────────────────────────────


class TestComponentHealth:
    """Test suite for ComponentHealth."""
    def test_to_dict(self) -> None:
        """Test functionality: to dict."""
        h = ComponentHealth("db", HealthStatus.HEALTHY, 5.2)
        d = h.to_dict()
        assert d["status"] == "healthy"


class TestHealthReport:
    """Test suite for HealthReport."""
    def test_is_healthy(self) -> None:
        """Test functionality: is healthy."""
        r = HealthReport(status=HealthStatus.HEALTHY)
        assert r.is_healthy
        r2 = HealthReport(status=HealthStatus.UNHEALTHY)
        assert not r2.is_healthy


class TestHealthChecker:
    """Test suite for HealthChecker."""
    def test_all_healthy(self) -> None:
        """Test functionality: all healthy."""
        checker = HealthChecker()
        checker.register("db", lambda: ComponentHealth("db"))
        checker.register("cache", lambda: ComponentHealth("cache"))
        report = checker.check()
        assert report.is_healthy
        assert report.component_count == 2

    def test_unhealthy_component(self) -> None:
        """Test functionality: unhealthy component."""
        checker = HealthChecker()
        checker.register("db", lambda: ComponentHealth("db", HealthStatus.UNHEALTHY))
        report = checker.check()
        assert not report.is_healthy

    def test_degraded_escalation(self) -> None:
        """Test functionality: degraded escalation."""
        checker = HealthChecker()
        checker.register("a", lambda: ComponentHealth("a", HealthStatus.DEGRADED))
        report = checker.check()
        assert report.status == HealthStatus.DEGRADED

    def test_check_fn_exception(self) -> None:
        """Test functionality: check fn exception."""
        checker = HealthChecker()
        checker.register("bad", lambda: 1 / 0)
        report = checker.check()
        assert not report.is_healthy

    def test_liveness(self) -> None:
        """Test functionality: liveness."""
        checker = HealthChecker()
        live = checker.liveness()
        assert live["status"] == "alive"

    def test_readiness(self) -> None:
        """Test functionality: readiness."""
        checker = HealthChecker()
        checker.register("ok", lambda: ComponentHealth("ok"))
        ready = checker.readiness()
        assert ready["ready"] is True


# ── CanaryAnalyzer ───────────────────────────────────────────────


class TestMetricComparison:
    """Test suite for MetricComparison."""
    def test_within_threshold(self) -> None:
        """Test functionality: within threshold."""
        mc = MetricComparison("err_rate", 0.01, 0.011, threshold=0.15)
        assert mc.passed

    def test_exceeds_threshold(self) -> None:
        """Test functionality: exceeds threshold."""
        mc = MetricComparison("err_rate", 0.01, 0.05, threshold=0.1)
        assert not mc.passed

    def test_zero_baseline(self) -> None:
        """Test functionality: zero baseline."""
        mc = MetricComparison("err_rate", 0.0, 0.005, threshold=0.01)
        assert mc.passed


class TestCanaryAnalyzer:
    """Test suite for CanaryAnalyzer."""
    def test_promote(self) -> None:
        """Test functionality: promote."""
        analyzer = CanaryAnalyzer(promote_threshold=0.9)
        report = analyzer.analyze(
            baseline={"err": 0.01, "latency": 200},
            canary={"err": 0.011, "latency": 205},
        )
        assert report.decision == CanaryDecision.PROMOTE

    def test_rollback(self) -> None:
        """Test functionality: rollback."""
        analyzer = CanaryAnalyzer(rollback_threshold=0.5)
        report = analyzer.analyze(
            baseline={"err": 0.01, "latency": 200},
            canary={"err": 0.1, "latency": 500},
        )
        assert report.decision == CanaryDecision.ROLLBACK

    def test_continue(self) -> None:
        """Test functionality: continue."""
        analyzer = CanaryAnalyzer(promote_threshold=0.9, rollback_threshold=0.3)
        report = analyzer.analyze(
            baseline={"a": 1.0, "b": 1.0, "c": 1.0},
            canary={"a": 1.0, "b": 2.0, "c": 1.0},  # b fails
        )
        assert report.decision == CanaryDecision.CONTINUE

    def test_custom_tolerances(self) -> None:
        """Test functionality: custom tolerances."""
        analyzer = CanaryAnalyzer()
        report = analyzer.analyze(
            baseline={"err": 0.01},
            canary={"err": 0.05},
            tolerances={"err": 5.0},  # Very tolerant
        )
        assert report.decision == CanaryDecision.PROMOTE

    def test_report_to_dict(self) -> None:
        """Test functionality: report to dict."""
        r = CanaryReport(decision=CanaryDecision.PROMOTE, pass_rate=1.0)
        d = r.to_dict()
        assert d["decision"] == "promote"
