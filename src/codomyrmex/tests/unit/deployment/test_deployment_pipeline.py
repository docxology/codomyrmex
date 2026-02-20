"""Tests for Sprint 19: Deployment Pipeline.

Tests for auto_build, health, canary.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from codomyrmex.containerization.auto_build import (
    AutoBuilder, DockerStage, DockerfileSpec,
)
from codomyrmex.api.health import (
    ComponentHealth, HealthChecker, HealthReport, HealthStatus,
)
from codomyrmex.deployment.canary import (
    CanaryAnalyzer, CanaryDecision, CanaryReport, MetricComparison,
)


# ── AutoBuilder ──────────────────────────────────────────────────


class TestDockerStage:
    def test_render(self) -> None:
        stage = DockerStage("builder", "python:3.12", ["WORKDIR /build"])
        rendered = stage.render()
        assert "FROM python:3.12 AS builder" in rendered
        assert "WORKDIR /build" in rendered


class TestDockerfileSpec:
    def test_render_multi_stage(self) -> None:
        spec = DockerfileSpec(stages=[
            DockerStage("builder", "python:3.12", ["WORKDIR /build"]),
            DockerStage("runtime", "python:3.12-slim", ["WORKDIR /app"]),
        ])
        rendered = spec.render()
        assert "AS builder" in rendered
        assert "AS runtime" in rendered
        assert spec.stage_count == 2

    def test_labels(self) -> None:
        spec = DockerfileSpec(
            stages=[DockerStage("app", "python:3.12")],
            labels={"version": "1.0"},
        )
        rendered = spec.render()
        assert 'LABEL version="1.0"' in rendered


class TestAutoBuilder:
    def test_from_pyproject(self) -> None:
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
        builder = AutoBuilder()
        spec = builder.default_spec()
        assert spec.stage_count == 2
        assert "python" in spec.render().lower()

    def test_from_config(self) -> None:
        builder = AutoBuilder()
        spec = builder.from_config("myapp", "3.13", "server.py")
        rendered = spec.render()
        assert "server.py" in rendered

    def test_missing_file(self) -> None:
        builder = AutoBuilder()
        spec = builder.from_pyproject("/nonexistent.toml")
        assert spec.stage_count == 2  # Falls back to defaults


# ── HealthChecker ────────────────────────────────────────────────


class TestComponentHealth:
    def test_to_dict(self) -> None:
        h = ComponentHealth("db", HealthStatus.HEALTHY, 5.2)
        d = h.to_dict()
        assert d["status"] == "healthy"


class TestHealthReport:
    def test_is_healthy(self) -> None:
        r = HealthReport(status=HealthStatus.HEALTHY)
        assert r.is_healthy
        r2 = HealthReport(status=HealthStatus.UNHEALTHY)
        assert not r2.is_healthy


class TestHealthChecker:
    def test_all_healthy(self) -> None:
        checker = HealthChecker()
        checker.register("db", lambda: ComponentHealth("db"))
        checker.register("cache", lambda: ComponentHealth("cache"))
        report = checker.check()
        assert report.is_healthy
        assert report.component_count == 2

    def test_unhealthy_component(self) -> None:
        checker = HealthChecker()
        checker.register("db", lambda: ComponentHealth("db", HealthStatus.UNHEALTHY))
        report = checker.check()
        assert not report.is_healthy

    def test_degraded_escalation(self) -> None:
        checker = HealthChecker()
        checker.register("a", lambda: ComponentHealth("a", HealthStatus.DEGRADED))
        report = checker.check()
        assert report.status == HealthStatus.DEGRADED

    def test_check_fn_exception(self) -> None:
        checker = HealthChecker()
        checker.register("bad", lambda: 1 / 0)
        report = checker.check()
        assert not report.is_healthy

    def test_liveness(self) -> None:
        checker = HealthChecker()
        live = checker.liveness()
        assert live["status"] == "alive"

    def test_readiness(self) -> None:
        checker = HealthChecker()
        checker.register("ok", lambda: ComponentHealth("ok"))
        ready = checker.readiness()
        assert ready["ready"] is True


# ── CanaryAnalyzer ───────────────────────────────────────────────


class TestMetricComparison:
    def test_within_threshold(self) -> None:
        mc = MetricComparison("err_rate", 0.01, 0.011, threshold=0.15)
        assert mc.passed

    def test_exceeds_threshold(self) -> None:
        mc = MetricComparison("err_rate", 0.01, 0.05, threshold=0.1)
        assert not mc.passed

    def test_zero_baseline(self) -> None:
        mc = MetricComparison("err_rate", 0.0, 0.005, threshold=0.01)
        assert mc.passed


class TestCanaryAnalyzer:
    def test_promote(self) -> None:
        analyzer = CanaryAnalyzer(promote_threshold=0.9)
        report = analyzer.analyze(
            baseline={"err": 0.01, "latency": 200},
            canary={"err": 0.011, "latency": 205},
        )
        assert report.decision == CanaryDecision.PROMOTE

    def test_rollback(self) -> None:
        analyzer = CanaryAnalyzer(rollback_threshold=0.5)
        report = analyzer.analyze(
            baseline={"err": 0.01, "latency": 200},
            canary={"err": 0.1, "latency": 500},
        )
        assert report.decision == CanaryDecision.ROLLBACK

    def test_continue(self) -> None:
        analyzer = CanaryAnalyzer(promote_threshold=0.9, rollback_threshold=0.3)
        report = analyzer.analyze(
            baseline={"a": 1.0, "b": 1.0, "c": 1.0},
            canary={"a": 1.0, "b": 2.0, "c": 1.0},  # b fails
        )
        assert report.decision == CanaryDecision.CONTINUE

    def test_custom_tolerances(self) -> None:
        analyzer = CanaryAnalyzer()
        report = analyzer.analyze(
            baseline={"err": 0.01},
            canary={"err": 0.05},
            tolerances={"err": 5.0},  # Very tolerant
        )
        assert report.decision == CanaryDecision.PROMOTE

    def test_report_to_dict(self) -> None:
        r = CanaryReport(decision=CanaryDecision.PROMOTE, pass_rate=1.0)
        d = r.to_dict()
        assert d["decision"] == "promote"
