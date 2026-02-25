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
        """Test functionality: creation defaults."""
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
        """Test functionality: to dict."""
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
        """Test functionality: add issue."""
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
        """Test functionality: add issue without recommendation."""
        from codomyrmex.system_discovery.health.health_checker import (
            HealthCheckResult,
            HealthStatus,
        )
        r = HealthCheckResult(module_name="test", status=HealthStatus.HEALTHY)
        r.add_issue("minor issue")
        assert len(r.issues) == 1

    def test_add_metric(self):
        """Test functionality: add metric."""
        from codomyrmex.system_discovery.health.health_checker import (
            HealthCheckResult,
            HealthStatus,
        )
        r = HealthCheckResult(module_name="test", status=HealthStatus.HEALTHY)
        r.add_metric("latency_ms", 42)
        assert r.metrics["latency_ms"] == 42

    def test_multiple_metrics(self):
        """Test functionality: multiple metrics."""
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
        """Test functionality: values."""
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
        """Test functionality: init."""
        from codomyrmex.system_discovery.health.health_checker import HealthChecker
        checker = HealthChecker()
        assert checker is not None

    def test_check_known_module(self):
        """Test functionality: check known module."""
        from codomyrmex.system_discovery.health.health_checker import (
            HealthChecker,
            HealthCheckResult,
        )
        checker = HealthChecker()
        result = checker.perform_health_check("logging_monitoring")
        assert isinstance(result, HealthCheckResult)
        assert result.module_name == "logging_monitoring"

    def test_check_unknown_module(self):
        """Test functionality: check unknown module."""
        from codomyrmex.system_discovery.health.health_checker import (
            HealthChecker,
            HealthCheckResult,
        )
        checker = HealthChecker()
        result = checker.perform_health_check("nonexistent_module_xyz")
        assert isinstance(result, HealthCheckResult)

    def test_check_multiple_modules(self):
        """Test functionality: check multiple modules."""
        from codomyrmex.system_discovery.health.health_checker import HealthChecker
        checker = HealthChecker()
        modules = ["logging_monitoring", "events", "agents"]
        for mod in modules:
            result = checker.perform_health_check(mod)
            assert result.module_name == mod

    def test_result_has_checks_performed(self):
        """Test functionality: result has checks performed."""
        from codomyrmex.system_discovery.health.health_checker import HealthChecker
        checker = HealthChecker()
        result = checker.perform_health_check("logging_monitoring")
        assert isinstance(result.checks_performed, list)


# ===================================================================
# DiscoveryEngine
# ===================================================================

@pytest.mark.unit
class TestDiscoveryEngine:
    """Test SystemDiscovery."""

    def test_import(self):
        """Test functionality: import."""
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery
        assert SystemDiscovery is not None

    def test_init(self):
        """Test functionality: init."""
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
        """Test functionality: import."""
        from codomyrmex.system_discovery.core.capability_scanner import (
            CapabilityScanner,
        )
        assert CapabilityScanner is not None

    def test_init(self):
        """Test functionality: init."""
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
        """Test functionality: import."""
        from codomyrmex.system_discovery.core.context import get_system_context
        assert get_system_context is not None

    def test_call(self):
        """Test functionality: call."""
        from codomyrmex.system_discovery.core.context import get_system_context
        ctx = get_system_context()
        assert ctx is not None
