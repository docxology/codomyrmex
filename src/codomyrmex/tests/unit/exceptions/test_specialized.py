"""Tests for exceptions.specialized — all specialized domain exceptions.

Zero-mock policy: real exception instantiation. Each class is a simple
exception subclass with optional context fields — straightforward to test.
"""

import pytest

from codomyrmex.exceptions.base import CodomyrmexError
from codomyrmex.exceptions.specialized import (
    ArtifactError,
    AuthenticationError,
    BulkheadFullError,
    CacheError,
    CapabilityScanError,
    CICDError,
    CircuitOpenError,
    CommandExecutionError,
    CompressionError,
    DatabaseError,
    DeploymentError,
    EncryptionError,
    EventError,
    IDEConnectionError,
    IDEError,
    InteractiveShellError,
    LoggingError,
    Modeling3DError,
    PerformanceError,
    PhysicalManagementError,
    PluginError,
    ResourceError,
    SessionError,
    SimulationError,
    SkillError,
    SpatialError,
    SystemDiscoveryError,
    TemplateError,
    TerminalError,
)

# ──────────────────────────── Helpers ──────────────────────────────────────


def _assert_is_codomyrmex_error(exc):
    """All specialized exceptions must inherit CodomyrmexError."""
    assert isinstance(exc, CodomyrmexError)
    assert isinstance(exc, Exception)


# ──────────────────────────── Performance / Monitoring ─────────────────────


class TestPerformanceError:
    def test_basic_instantiation(self):
        e = PerformanceError("slow query")
        _assert_is_codomyrmex_error(e)

    def test_message_stored(self):
        e = PerformanceError("timeout exceeded")
        assert "timeout exceeded" in str(e)

    def test_metric_name_in_context(self):
        e = PerformanceError("too slow", metric_name="response_time")
        assert e.context.get("metric_name") == "response_time"

    def test_threshold_in_context(self):
        e = PerformanceError("exceeded", threshold=200.0)
        assert e.context.get("threshold") == 200.0

    def test_no_optional_fields(self):
        e = PerformanceError("fail")
        assert "metric_name" not in e.context
        assert "threshold" not in e.context

    def test_can_be_raised_and_caught(self):
        with pytest.raises(PerformanceError):
            raise PerformanceError("test")


class TestLoggingError:
    def test_basic_instantiation(self):
        e = LoggingError("log failed")
        _assert_is_codomyrmex_error(e)

    def test_logger_name_in_context(self):
        e = LoggingError("fail", logger_name="myapp")
        assert e.context.get("logger_name") == "myapp"

    def test_level_in_context(self):
        e = LoggingError("fail", level="ERROR")
        assert e.context.get("level") == "ERROR"


# ──────────────────────────── System Discovery ────────────────────────────


class TestSystemDiscoveryError:
    def test_instantiation(self):
        e = SystemDiscoveryError("discovery failed")
        _assert_is_codomyrmex_error(e)

    def test_can_be_raised(self):
        with pytest.raises(SystemDiscoveryError):
            raise SystemDiscoveryError("fail")


class TestCapabilityScanError:
    def test_instantiation(self):
        e = CapabilityScanError("scan failed")
        _assert_is_codomyrmex_error(e)


# ──────────────────────────── 3D / Physical ───────────────────────────────


class TestModeling3DError:
    def test_instantiation(self):
        e = Modeling3DError("mesh error")
        _assert_is_codomyrmex_error(e)


class TestPhysicalManagementError:
    def test_instantiation(self):
        e = PhysicalManagementError("physical fail")
        _assert_is_codomyrmex_error(e)


class TestSimulationError:
    def test_instantiation(self):
        e = SimulationError("sim crash")
        _assert_is_codomyrmex_error(e)

    def test_can_be_raised(self):
        with pytest.raises(SimulationError):
            raise SimulationError("crash")


# ──────────────────────────── Terminal / Shell ────────────────────────────


class TestTerminalError:
    def test_instantiation(self):
        e = TerminalError("terminal fail")
        _assert_is_codomyrmex_error(e)


class TestInteractiveShellError:
    def test_instantiation(self):
        e = InteractiveShellError("shell failed")
        _assert_is_codomyrmex_error(e)

    def test_is_also_terminal_error(self):
        e = InteractiveShellError("err")
        assert isinstance(e, TerminalError)

    def test_caught_as_terminal_error(self):
        with pytest.raises(TerminalError):
            raise InteractiveShellError("shell fail")


# ──────────────────────────── Database ────────────────────────────────────


class TestDatabaseError:
    def test_instantiation(self):
        e = DatabaseError("db fail")
        _assert_is_codomyrmex_error(e)

    def test_can_be_raised(self):
        with pytest.raises(DatabaseError):
            raise DatabaseError("fail")


# ──────────────────────────── CI/CD ───────────────────────────────────────


class TestCICDError:
    def test_instantiation(self):
        e = CICDError("pipeline failed")
        _assert_is_codomyrmex_error(e)


class TestDeploymentError:
    def test_instantiation(self):
        e = DeploymentError("deploy failed")
        _assert_is_codomyrmex_error(e)


# ──────────────────────────── Resources ───────────────────────────────────


class TestResourceError:
    def test_instantiation(self):
        e = ResourceError("resource exhausted")
        _assert_is_codomyrmex_error(e)


# Note: MemoryError is shadowed by Python builtins, skipping import


# ──────────────────────────── Spatial ─────────────────────────────────────


class TestSpatialError:
    def test_instantiation(self):
        e = SpatialError("spatial fail")
        _assert_is_codomyrmex_error(e)


# ──────────────────────────── Events ──────────────────────────────────────


class TestEventError:
    def test_instantiation(self):
        e = EventError("event fail")
        _assert_is_codomyrmex_error(e)


# ──────────────────────────── Skills ──────────────────────────────────────


class TestSkillError:
    def test_instantiation(self):
        e = SkillError("skill not found")
        _assert_is_codomyrmex_error(e)


# ──────────────────────────── Templates / Plugins ─────────────────────────


class TestTemplateError:
    def test_instantiation(self):
        e = TemplateError("template parse error")
        _assert_is_codomyrmex_error(e)


class TestPluginError:
    def test_instantiation(self):
        e = PluginError("plugin load failed")
        _assert_is_codomyrmex_error(e)


# ──────────────────────────── Auth / Circuit ──────────────────────────────


class TestAuthenticationError:
    def test_instantiation(self):
        e = AuthenticationError("invalid credentials")
        _assert_is_codomyrmex_error(e)

    def test_can_be_raised(self):
        with pytest.raises(AuthenticationError):
            raise AuthenticationError("denied")


class TestCircuitOpenError:
    def test_instantiation(self):
        e = CircuitOpenError("circuit is open")
        _assert_is_codomyrmex_error(e)

    def test_can_be_raised(self):
        with pytest.raises(CircuitOpenError):
            raise CircuitOpenError("open")


class TestBulkheadFullError:
    def test_instantiation(self):
        e = BulkheadFullError("bulkhead full")
        _assert_is_codomyrmex_error(e)


# ──────────────────────────── Compression / Encryption ───────────────────


class TestCompressionError:
    def test_instantiation(self):
        e = CompressionError("compress fail")
        _assert_is_codomyrmex_error(e)


class TestEncryptionError:
    def test_instantiation(self):
        e = EncryptionError("decrypt fail")
        _assert_is_codomyrmex_error(e)


# ──────────────────────────── IDE ─────────────────────────────────────────


class TestIDEError:
    def test_instantiation(self):
        e = IDEError("ide fail")
        _assert_is_codomyrmex_error(e)


class TestIDEConnectionError:
    def test_instantiation(self):
        e = IDEConnectionError("not connected")
        _assert_is_codomyrmex_error(e)

    def test_is_also_ide_error(self):
        e = IDEConnectionError("fail")
        assert isinstance(e, IDEError)

    def test_caught_as_ide_error(self):
        with pytest.raises(IDEError):
            raise IDEConnectionError("conn fail")


class TestCommandExecutionError:
    def test_instantiation(self):
        e = CommandExecutionError("command failed")
        _assert_is_codomyrmex_error(e)

    def test_is_also_ide_error(self):
        assert isinstance(CommandExecutionError("x"), IDEError)


class TestSessionError:
    def test_instantiation(self):
        e = SessionError("session expired")
        _assert_is_codomyrmex_error(e)

    def test_is_also_ide_error(self):
        assert isinstance(SessionError("x"), IDEError)


class TestArtifactError:
    def test_instantiation(self):
        e = ArtifactError("artifact missing")
        _assert_is_codomyrmex_error(e)

    def test_is_also_ide_error(self):
        assert isinstance(ArtifactError("x"), IDEError)


# ──────────────────────────── Cache ───────────────────────────────────────


class TestCacheError:
    def test_instantiation(self):
        e = CacheError("cache miss")
        _assert_is_codomyrmex_error(e)

    def test_can_be_raised(self):
        with pytest.raises(CacheError):
            raise CacheError("miss")


# ──────────────────────────── Cross-cutting ───────────────────────────────


class TestAllExceptionsHaveMessage:
    """All exceptions must store their message accessible via .message and str()."""

    @pytest.mark.parametrize(
        "exc_cls",
        [
            PerformanceError,
            LoggingError,
            SystemDiscoveryError,
            CapabilityScanError,
            Modeling3DError,
            PhysicalManagementError,
            SimulationError,
            TerminalError,
            InteractiveShellError,
            DatabaseError,
            CICDError,
            DeploymentError,
            ResourceError,
            SpatialError,
            EventError,
            SkillError,
            TemplateError,
            PluginError,
            AuthenticationError,
            CircuitOpenError,
            BulkheadFullError,
            CompressionError,
            EncryptionError,
            IDEError,
            IDEConnectionError,
            CommandExecutionError,
            SessionError,
            ArtifactError,
            CacheError,
        ],
    )
    def test_message_attribute(self, exc_cls):
        e = exc_cls("test message")
        assert e.message == "test message"

    @pytest.mark.parametrize(
        "exc_cls",
        [
            PerformanceError,
            AuthenticationError,
            DatabaseError,
            CacheError,
        ],
    )
    def test_error_code_defaults_to_class_name(self, exc_cls):
        e = exc_cls("err")
        assert e.error_code == exc_cls.__name__

    @pytest.mark.parametrize(
        "exc_cls",
        [
            PerformanceError,
            LoggingError,
            TerminalError,
            InteractiveShellError,
            IDEError,
            IDEConnectionError,
            ResourceError,
        ],
    )
    def test_to_dict_has_required_keys(self, exc_cls):
        e = exc_cls("test")
        d = e.to_dict()
        assert "error_type" in d
        assert "error_code" in d
        assert "message" in d
