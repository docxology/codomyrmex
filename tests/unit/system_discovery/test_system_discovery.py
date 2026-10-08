"""Tests for the system_discovery module.

Covers:
- HealthStatus enum
- HealthCheckResult dataclass (to_dict, add_issue, add_metric)
- HealthChecker (perform_health_check, module availability, status determination)
- HealthReporter
- DiscoveryEngine
- CapabilityScanner
"""

import pytest

# ===================================================================
# HealthStatus & HealthCheckResult
# ===================================================================


@pytest.mark.unit
class TestHealthCheckResult:
    """Test HealthCheckResult dataclass."""

    def test_creation_defaults(self):
        from codomyrmex.system_discovery.health.health_checker import (
            HealthCheckResult,
            HealthStatus,
        )

        r = HealthCheckResult(module_name="test", status=HealthStatus.HEALTHY)
        assert r.module_name == "test"
        assert r.status == HealthStatus.HEALTHY
        assert r.checks_performed == []
        assert r.issues == []

    def test_to_dict(self):
        from codomyrmex.system_discovery.health.health_checker import (
            HealthCheckResult,
            HealthStatus,
        )

        r = HealthCheckResult(module_name="test", status=HealthStatus.HEALTHY)
        d = r.to_dict()
        assert d["module_name"] == "test"
        assert d["status"] == "healthy"
        assert "timestamp" in d
        assert isinstance(d["checks_performed"], list)

    def test_add_issue(self):
        from codomyrmex.system_discovery.health.health_checker import (
            HealthCheckResult,
            HealthStatus,
        )

        r = HealthCheckResult(module_name="test", status=HealthStatus.HEALTHY)
        r.add_issue("something broke", recommendation="fix it")
        assert len(r.issues) >= 1
        # Issues may be stored as strings or dicts depending on implementation
        assert any("something broke" in str(i) for i in r.issues)

    def test_add_issue_without_recommendation(self):
        from codomyrmex.system_discovery.health.health_checker import (
            HealthCheckResult,
            HealthStatus,
        )

        r = HealthCheckResult(module_name="test", status=HealthStatus.HEALTHY)
        r.add_issue("minor issue")
        assert len(r.issues) == 1

    def test_add_metric(self):
        from codomyrmex.system_discovery.health.health_checker import (
            HealthCheckResult,
            HealthStatus,
        )

        r = HealthCheckResult(module_name="test", status=HealthStatus.HEALTHY)
        r.add_metric("latency_ms", 42)
        assert r.metrics["latency_ms"] == 42

    def test_multiple_metrics(self):
        from codomyrmex.system_discovery.health.health_checker import (
            HealthCheckResult,
            HealthStatus,
        )

        r = HealthCheckResult(module_name="test", status=HealthStatus.HEALTHY)
        r.add_metric("cpu", 50)
        r.add_metric("memory", 80)
        assert len(r.metrics) == 2


@pytest.mark.unit
class TestHealthStatus:
    """Test HealthStatus enum."""

    def test_values(self):
        from codomyrmex.system_discovery.health.health_checker import HealthStatus

        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"


# ===================================================================
# HealthChecker
# ===================================================================


@pytest.mark.unit
class TestHealthChecker:
    """Test HealthChecker functionality."""

    def test_init(self):
        from codomyrmex.system_discovery.health.health_checker import HealthChecker

        checker = HealthChecker()
        assert checker is not None

    def test_check_known_module(self):
        from codomyrmex.system_discovery.health.health_checker import (
            HealthChecker,
            HealthCheckResult,
        )

        checker = HealthChecker()
        result = checker.perform_health_check("logging_monitoring")
        assert isinstance(result, HealthCheckResult)
        assert result.module_name == "logging_monitoring"

    def test_check_unknown_module(self):
        from codomyrmex.system_discovery.health.health_checker import (
            HealthChecker,
            HealthCheckResult,
        )

        checker = HealthChecker()
        result = checker.perform_health_check("nonexistent_module_xyz")
        assert isinstance(result, HealthCheckResult)

    def test_check_multiple_modules(self):
        from codomyrmex.system_discovery.health.health_checker import HealthChecker

        checker = HealthChecker()
        modules = ["logging_monitoring", "events", "agents"]
        for mod in modules:
            result = checker.perform_health_check(mod)
            assert result.module_name == mod

    def test_result_has_checks_performed(self):
        from codomyrmex.system_discovery.health.health_checker import HealthChecker

        checker = HealthChecker()
        result = checker.perform_health_check("logging_monitoring")
        assert isinstance(result.checks_performed, list)


@pytest.mark.unit
class TestHealthChecksExerciseRealModules:
    """Dedicated checks, the MCP tool and the CLI command run real checks."""

    def test_dedicated_checks_name_real_packages(self):
        from tests.support.repo_paths import PACKAGE_ROOT

        from codomyrmex.system_discovery.health.health_checker import HealthChecker

        for name in HealthChecker().module_checks:
            assert (PACKAGE_ROOT / name / "__init__.py").is_file(), name

    def test_run_checks_covers_every_dedicated_check(self):
        from codomyrmex.system_discovery.health.health_checker import (
            HealthChecker,
            HealthStatus,
        )

        checker = HealthChecker()
        results = checker.run_checks()
        assert list(results) == list(checker.module_checks)
        for name, result in results.items():
            # Each dedicated check records what it did beyond importing.
            assert len(result.checks_performed) > 1, name
            assert result.status is not HealthStatus.UNKNOWN, (name, result.issues)

    def test_data_visualization_check_renders_a_plot(self):
        from codomyrmex.system_discovery.health.health_checker import (
            HealthChecker,
            HealthStatus,
        )

        result = HealthChecker().perform_health_check("data_visualization")
        assert result.status is HealthStatus.HEALTHY, result.issues
        assert result.metrics["plot_rendered"] is True

    def test_mcp_health_check_single_module(self):
        from codomyrmex.system_discovery.mcp_tools import health_check

        response = health_check("logging_monitoring")
        assert response["status"] == "success"
        assert response["healthy"] is True
        assert response["details"]["logging_monitoring"]["status"] == "healthy"

    def test_mcp_health_check_reports_unavailable_module(self):
        from codomyrmex.system_discovery.mcp_tools import health_check

        response = health_check("nonexistent_module_xyz")
        assert response["status"] == "success"
        assert response["healthy"] is False
        assert response["details"]["nonexistent_module_xyz"]["status"] == "unhealthy"

    def test_cli_health_command_prints_each_checked_module(self, capsys):
        from codomyrmex.system_discovery import cli_commands
        from codomyrmex.system_discovery.health.health_checker import (
            HealthChecker,
            HealthStatus,
        )

        cli_commands()["health"]["handler"]()
        # Log records may share stdout when an earlier test configured
        # logging, so look at the report's own lines.
        lines = capsys.readouterr().out.splitlines()
        report = lines[lines.index("System Health Check:") + 1 :]
        statuses = {s.value for s in HealthStatus}
        for name in HealthChecker().module_checks:
            status = next(line for line in report if line.startswith(f"  {name}: "))
            assert status.split(": ", 1)[1] in statuses
        assert not any(line.endswith(": available") for line in report)


@pytest.mark.unit
class TestDemoWorkflows:
    """SystemHealthChecker.run_demo_workflows uses the real module names."""

    def test_demo_plot_is_written_to_output_dir(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import ModuleInfo
        from codomyrmex.system_discovery.core.health_checker import (
            SystemHealthChecker,
        )

        def info(name: str) -> ModuleInfo:
            return ModuleInfo(
                name=name,
                path="",
                description="",
                version="",
                capabilities=[],
                dependencies=[],
                is_importable=True,
                has_tests=True,
                has_docs=True,
                last_modified="",
            )

        modules = {
            name: info(name)
            for name in ("data_visualization", "logging_monitoring", "coding")
        }
        checker = SystemHealthChecker(tmp_path, tmp_path / "src", tmp_path / "tests")
        completed = checker.run_demo_workflows(modules, output_dir=tmp_path)

        out = capsys.readouterr().out
        assert (tmp_path / "demo_plot.png").stat().st_size > 0
        # The code execution demo runs for the "coding" module; it needs a
        # Docker sandbox, so it succeeds or reports why it could not run.
        assert "Testing Code Execution..." in out
        assert completed >= 2


# ===================================================================
# DiscoveryEngine
# ===================================================================


@pytest.mark.unit
class TestDiscoveryEngine:
    """Test SystemDiscovery."""

    def test_import(self):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        assert SystemDiscovery is not None

    def test_init(self):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        engine = SystemDiscovery()
        assert engine is not None


# ===================================================================
# CapabilityScanner
# ===================================================================


@pytest.mark.unit
class TestCapabilityScanner:
    """Test CapabilityScanner."""

    def test_import(self):
        from codomyrmex.system_discovery.core.capability_scanner import (
            CapabilityScanner,
        )

        assert CapabilityScanner is not None

    def test_init(self):
        from codomyrmex.system_discovery.core.capability_scanner import (
            CapabilityScanner,
        )

        scanner = CapabilityScanner()
        assert scanner is not None


# ===================================================================
# Context
# ===================================================================


@pytest.mark.unit
class TestDiscoveryContext:
    """Test discovery context."""

    def test_import(self):
        from codomyrmex.system_discovery.core.context import get_system_context

        assert get_system_context is not None

    def test_call(self):
        from codomyrmex.system_discovery.core.context import get_system_context

        ctx = get_system_context()
        assert ctx is not None
