"""
Unit tests for exceptions.specialized — Zero-Mock compliant.

Covers every exception class in specialized.py:
PerformanceError, LoggingError, SystemDiscoveryError, CapabilityScanError,
Modeling3DError, PhysicalManagementError, SimulationError, TerminalError,
InteractiveShellError, DatabaseError, CICDError, DeploymentError,
ResourceError, MemoryError (shadow), SpatialError, EventError, SkillError,
TemplateError, PluginError (plugin_name/plugin_version context injection),
AuthenticationError, CircuitOpenError, BulkheadFullError, CompressionError,
EncryptionError, IDEError, IDEConnectionError, CommandExecutionError,
SessionError, ArtifactError, CacheError, SerializationError.
"""

import pytest

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
    SerializationError,
    SessionError,
    SimulationError,
    SkillError,
    SpatialError,
    SystemDiscoveryError,
    TemplateError,
    TerminalError,
)

# ── Simple CodomyrmexError subclasses ─────────────────────────────────


@pytest.mark.unit
class TestSimpleSpecializedExceptions:
    """All pass-through subclasses share the same pattern."""

    _SIMPLE_CLASSES = [
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
        AuthenticationError,
        CompressionError,
        EncryptionError,
        IDEError,
        IDEConnectionError,
        CommandExecutionError,
        SessionError,
        ArtifactError,
    ]

    def test_all_are_exception_subclasses(self):
        for cls in self._SIMPLE_CLASSES:
            assert issubclass(cls, Exception), f"{cls.__name__} is not Exception"

    def test_all_carry_message(self):
        for cls in self._SIMPLE_CLASSES:
            exc = cls("test message")
            assert "test message" in str(exc), f"{cls.__name__} missing message"

    def test_raise_and_catch_each(self):
        for cls in self._SIMPLE_CLASSES:
            with pytest.raises(cls):
                raise cls("boom")

    def test_catch_as_base_exception(self):
        from codomyrmex.exceptions.base import CodomyrmexError
        for cls in self._SIMPLE_CLASSES:
            with pytest.raises(CodomyrmexError):
                raise cls("err")


# ── PluginError ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestPluginError:
    def test_is_exception(self):
        assert isinstance(PluginError("err"), Exception)

    def test_message_stored(self):
        e = PluginError("plugin failed")
        assert "plugin failed" in str(e)

    def test_plugin_name_in_context(self):
        e = PluginError("err", plugin_name="my-plugin")
        assert e.context.get("plugin_name") == "my-plugin"

    def test_plugin_version_in_context(self):
        e = PluginError("err", plugin_version="1.2.3")
        assert e.context.get("plugin_version") == "1.2.3"

    def test_both_plugin_fields(self):
        e = PluginError("err", plugin_name="x", plugin_version="0.1")
        assert e.context["plugin_name"] == "x"
        assert e.context["plugin_version"] == "0.1"

    def test_no_plugin_fields_no_context_keys(self):
        e = PluginError("err")
        assert "plugin_name" not in e.context
        assert "plugin_version" not in e.context


# ── CircuitOpenError / BulkheadFullError (plain Exception) ───────────


@pytest.mark.unit
class TestCircuitAndBulkheadErrors:
    def test_circuit_open_is_exception(self):
        assert isinstance(CircuitOpenError("circuit open"), Exception)

    def test_circuit_open_message(self):
        e = CircuitOpenError("circuit is open")
        assert "circuit is open" in str(e)

    def test_bulkhead_full_is_exception(self):
        assert isinstance(BulkheadFullError("full"), Exception)

    def test_bulkhead_full_message(self):
        e = BulkheadFullError("semaphore exhausted")
        assert "semaphore exhausted" in str(e)

    def test_raise_circuit_open(self):
        with pytest.raises(CircuitOpenError):
            raise CircuitOpenError("open")

    def test_raise_bulkhead_full(self):
        with pytest.raises(BulkheadFullError):
            raise BulkheadFullError("full")

    def test_circuit_not_codomyrmex_error(self):
        from codomyrmex.exceptions.base import CodomyrmexError
        e = CircuitOpenError("err")
        assert not isinstance(e, CodomyrmexError)

    def test_bulkhead_not_codomyrmex_error(self):
        from codomyrmex.exceptions.base import CodomyrmexError
        e = BulkheadFullError("err")
        assert not isinstance(e, CodomyrmexError)


# ── IDEError hierarchy ────────────────────────────────────────────────


@pytest.mark.unit
class TestIDEExceptionHierarchy:
    def test_ide_connection_is_ide_error(self):
        assert issubclass(IDEConnectionError, IDEError)

    def test_command_execution_is_ide_error(self):
        assert issubclass(CommandExecutionError, IDEError)

    def test_session_error_is_ide_error(self):
        assert issubclass(SessionError, IDEError)

    def test_artifact_error_is_ide_error(self):
        assert issubclass(ArtifactError, IDEError)

    def test_catch_as_ide_error(self):
        with pytest.raises(IDEError):
            raise IDEConnectionError("connection refused")


# ── CacheError ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCacheError:
    def test_is_exception(self):
        assert isinstance(CacheError("cache miss"), Exception)

    def test_message_stored(self):
        e = CacheError("key not found")
        assert "key not found" in str(e)

    def test_cache_key_in_context(self):
        e = CacheError("err", cache_key="user:42")
        assert e.context.get("cache_key") == "user:42"

    def test_backend_in_context(self):
        e = CacheError("err", backend="redis")
        assert e.context.get("backend") == "redis"

    def test_both_cache_fields(self):
        e = CacheError("err", cache_key="k", backend="memcache")
        assert e.context["cache_key"] == "k"
        assert e.context["backend"] == "memcache"

    def test_no_optional_fields_no_context_keys(self):
        e = CacheError("err")
        assert "cache_key" not in e.context
        assert "backend" not in e.context


# ── SerializationError ────────────────────────────────────────────────


@pytest.mark.unit
class TestSerializationError:
    def test_is_exception(self):
        assert isinstance(SerializationError("err"), Exception)

    def test_message_stored(self):
        e = SerializationError("JSON decode failed")
        assert "JSON decode failed" in str(e)

    def test_format_type_in_context(self):
        e = SerializationError("err", format_type="json")
        assert e.context.get("format_type") == "json"

    def test_data_type_in_context(self):
        e = SerializationError("err", data_type="dict")
        assert e.context.get("data_type") == "dict"

    def test_both_fields(self):
        e = SerializationError("err", format_type="msgpack", data_type="list")
        assert e.context["format_type"] == "msgpack"
        assert e.context["data_type"] == "list"

    def test_no_optional_fields(self):
        e = SerializationError("err")
        assert "format_type" not in e.context
        assert "data_type" not in e.context
