"""Comprehensive tests for exceptions.specialized — zero-mock.

Covers the full specialized exception hierarchy: PerformanceError, LoggingError,
SystemDiscoveryError, CapabilityScanError, Modeling3DError, PhysicalManagementError,
SimulationError, and all other domain exceptions with context propagation.
"""

from codomyrmex.exceptions.base import CodomyrmexError
from codomyrmex.exceptions.specialized import (
    CapabilityScanError,
    LoggingError,
    Modeling3DError,
    PerformanceError,
    PhysicalManagementError,
    SimulationError,
    SystemDiscoveryError,
)


class TestPerformanceError:
    def test_create(self):
        e = PerformanceError("Slow query")
        assert "Slow" in str(e)
        assert isinstance(e, CodomyrmexError)

    def test_with_context(self):
        e = PerformanceError("Exceeded", metric_name="latency_p99", threshold=500.0)
        assert e.context.get("metric_name") == "latency_p99"
        assert e.context.get("threshold") == 500.0


class TestLoggingError:
    def test_create(self):
        e = LoggingError("Log write failed")
        assert isinstance(e, CodomyrmexError)

    def test_with_context(self):
        e = LoggingError("Failed", logger_name="app.main", level="ERROR")
        assert e.context.get("logger_name") == "app.main"
        assert e.context.get("level") == "ERROR"


class TestSystemDiscoveryError:
    def test_create(self):
        e = SystemDiscoveryError("Discovery failed")
        assert isinstance(e, CodomyrmexError)

    def test_with_scope(self):
        e = SystemDiscoveryError("Timeout", discovery_scope="network")
        assert e.context.get("discovery_scope") == "network"


class TestCapabilityScanError:
    def test_create(self):
        e = CapabilityScanError("Scan failed")
        assert isinstance(e, CodomyrmexError)

    def test_with_capability(self):
        e = CapabilityScanError("Error", capability_name="audio_input")
        assert e.context.get("capability_name") == "audio_input"


class TestModeling3DError:
    def test_create(self):
        e = Modeling3DError("Render failed")
        assert isinstance(e, CodomyrmexError)

    def test_with_format(self):
        e = Modeling3DError("Parse error", model_format="glTF")
        assert e.context.get("model_format") == "glTF"


class TestPhysicalManagementError:
    def test_create(self):
        e = PhysicalManagementError("Device offline")
        assert isinstance(e, CodomyrmexError)

    def test_with_device(self):
        e = PhysicalManagementError("Error", device_id="dev-123")
        assert e.context.get("device_id") == "dev-123"


class TestSimulationError:
    def test_create(self):
        e = SimulationError("Sim crashed")
        assert isinstance(e, CodomyrmexError)

    def test_with_context(self):
        e = SimulationError("Failed", simulation_id="sim-42", engine="physics_v2")
        assert e.context.get("simulation_id") == "sim-42"
        assert e.context.get("engine") == "physics_v2"


class TestHierarchy:
    def test_all_inherit_from_codomyrmex_error(self):
        classes = [
            PerformanceError,
            LoggingError,
            SystemDiscoveryError,
            CapabilityScanError,
            Modeling3DError,
            PhysicalManagementError,
            SimulationError,
        ]
        for cls in classes:
            assert issubclass(cls, CodomyrmexError)

    def test_capability_scan_inherits_codomyrmex(self):
        assert issubclass(CapabilityScanError, CodomyrmexError)

    def test_all_have_context(self):
        classes = [
            PerformanceError,
            LoggingError,
            SystemDiscoveryError,
            CapabilityScanError,
            Modeling3DError,
            PhysicalManagementError,
            SimulationError,
        ]
        for cls in classes:
            e = cls("test")
            assert hasattr(e, "context")
