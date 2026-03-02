"""Zero-Mock tests for shared IDE abstractions.

Tests for IDEClient base class contract, data classes (IDECommand,
IDECommandResult, FileInfo), IDEStatus enum, error type hierarchy,
event handler system, command history, and helper methods.
"""

import abc
from pathlib import Path

import pytest

from codomyrmex.ide import (
    ArtifactError,
    CommandExecutionError,
    ConnectionError,
    FileInfo,
    IDEClient,
    IDECommand,
    IDECommandResult,
    IDEError,
    IDEStatus,
    SessionError,
)
from codomyrmex.ide.antigravity import AntigravityClient
from codomyrmex.ide.cursor import CursorClient
from codomyrmex.ide.vscode import VSCodeClient


@pytest.mark.unit
class TestIDEClientAbstractContract:
    """Tests that IDEClient is a proper abstract base class with expected methods."""

    def test_ide_client_is_abc(self):
        """IDEClient should be an abstract base class."""
        assert issubclass(IDEClient, abc.ABC)

    def test_abstract_methods_exist(self):
        """IDEClient should declare the required abstract methods."""
        abstract_names = {
            "connect", "disconnect", "is_connected", "get_capabilities",
            "execute_command", "get_active_file", "open_file", "get_open_files",
        }
        client_abstract = {
            name for name, method in vars(IDEClient).items()
            if getattr(method, "__isabstractmethod__", False)
        }
        assert abstract_names.issubset(client_abstract)

    def test_concrete_helper_methods_exist(self):
        """IDEClient should provide concrete helper methods."""
        helpers = [
            "execute_command_safe", "execute_batch", "get_file_info",
            "register_event_handler", "emit_event", "clear_command_history",
            "get_last_command", "get_success_rate",
        ]
        for name in helpers:
            assert hasattr(IDEClient, name), f"Missing helper: {name}"

    def test_all_subclasses_implement_abstract(self):
        """All concrete IDE clients should be instantiable."""
        for cls in (AntigravityClient, CursorClient, VSCodeClient):
            instance = cls()
            assert isinstance(instance, IDEClient)

    def test_status_property_on_base(self):
        """IDEClient.status property should return IDEStatus."""
        client = AntigravityClient()
        assert isinstance(client.status, IDEStatus)

    def test_command_history_property_returns_list(self):
        """IDEClient.command_history should return a list."""
        client = AntigravityClient()
        history = client.command_history
        assert isinstance(history, list)
        assert len(history) == 0


@pytest.mark.unit
class TestIDEErrorHierarchy:
    """Tests for IDE exception class hierarchy."""

    def test_ide_error_is_exception(self):
        """IDEError should inherit from Exception."""
        assert issubclass(IDEError, Exception)

    def test_connection_error_inherits_ide_error(self):
        """ConnectionError should inherit from IDEError."""
        assert issubclass(ConnectionError, IDEError)

    def test_command_execution_error_inherits_ide_error(self):
        """CommandExecutionError should inherit from IDEError."""
        assert issubclass(CommandExecutionError, IDEError)

    def test_session_error_inherits_ide_error(self):
        """SessionError should inherit from IDEError."""
        assert issubclass(SessionError, IDEError)

    def test_artifact_error_inherits_ide_error(self):
        """ArtifactError should inherit from IDEError."""
        assert issubclass(ArtifactError, IDEError)

    def test_error_classes_are_raisable(self):
        """All IDE error classes should be raisable with a message."""
        for cls in (IDEError, ConnectionError, CommandExecutionError, SessionError, ArtifactError):
            with pytest.raises(cls):
                raise cls("test error message")

    def test_error_message_preserved(self):
        """Error message should be accessible via str()."""
        err = IDEError("Something went wrong")
        assert "Something went wrong" in str(err)


@pytest.mark.unit
class TestIDEStatusEnum:
    """Tests for the IDEStatus enumeration."""

    def test_disconnected_value(self):
        """DISCONNECTED should have value 'disconnected'."""
        assert IDEStatus.DISCONNECTED.value == "disconnected"

    def test_connecting_value(self):
        """CONNECTING should have value 'connecting'."""
        assert IDEStatus.CONNECTING.value == "connecting"

    def test_connected_value(self):
        """CONNECTED should have value 'connected'."""
        assert IDEStatus.CONNECTED.value == "connected"

    def test_error_value(self):
        """ERROR should have value 'error'."""
        assert IDEStatus.ERROR.value == "error"

    def test_exactly_four_members(self):
        """IDEStatus should have exactly four members."""
        assert len(IDEStatus) == 4


@pytest.mark.unit
class TestIDECommandDataClass:
    """Tests for the IDECommand dataclass."""

    def test_creation_with_defaults(self):
        """IDECommand should initialize with default args and timeout."""
        cmd = IDECommand(name="test")
        assert cmd.name == "test"
        assert cmd.args == {}
        assert cmd.timeout == 30.0

    def test_creation_with_custom_values(self):
        """IDECommand should accept custom args and timeout."""
        cmd = IDECommand(name="cmd", args={"k": "v"}, timeout=60.0)
        assert cmd.args == {"k": "v"}
        assert cmd.timeout == 60.0

    def test_to_dict_includes_all_fields(self):
        """IDECommand.to_dict should include name, args, and timeout."""
        cmd = IDECommand(name="test", args={"a": 1})
        d = cmd.to_dict()
        assert d["name"] == "test"
        assert d["args"] == {"a": 1}
        assert "timeout" in d

    def test_args_are_mutable(self):
        """Two IDECommand instances should have independent args dicts."""
        cmd1 = IDECommand(name="a")
        cmd2 = IDECommand(name="b")
        cmd1.args["key"] = "val"
        assert "key" not in cmd2.args

    def test_name_field_is_string(self):
        """name field should be a string."""
        cmd = IDECommand(name="test_name")
        assert isinstance(cmd.name, str)


@pytest.mark.unit
class TestIDECommandResultDataClass:
    """Tests for the IDECommandResult dataclass."""

    def test_success_result(self):
        """Successful result should have success=True and no error."""
        result = IDECommandResult(success=True, command="test", output="ok")
        assert result.success is True
        assert result.error is None

    def test_failure_result(self):
        """Failed result should have success=False and an error message."""
        result = IDECommandResult(success=False, command="fail", error="oops")
        assert result.success is False
        assert result.error == "oops"

    def test_to_dict_structure(self):
        """to_dict should include all expected keys."""
        result = IDECommandResult(success=True, command="test", output={"data": 1}, execution_time=0.5)
        d = result.to_dict()
        assert d["success"] is True
        assert d["command"] == "test"
        assert d["output"] == {"data": 1}
        assert d["execution_time"] == 0.5

    def test_default_execution_time(self):
        """Default execution_time should be 0.0."""
        result = IDECommandResult(success=True, command="cmd")
        assert result.execution_time == 0.0

    def test_default_output_is_none(self):
        """Default output should be None."""
        result = IDECommandResult(success=True, command="cmd")
        assert result.output is None


@pytest.mark.unit
class TestFileInfoDataClass:
    """Tests for the FileInfo dataclass."""

    def test_creation_with_required_fields(self):
        """FileInfo should initialize with path and name."""
        info = FileInfo(path="/path/to/file.py", name="file.py")
        assert info.path == "/path/to/file.py"
        assert info.name == "file.py"

    def test_default_optional_fields(self):
        """Optional fields should have sensible defaults."""
        info = FileInfo(path="/f.py", name="f.py")
        assert info.is_modified is False
        assert info.language is None
        assert info.line_count is None

    def test_to_dict_all_fields(self):
        """to_dict should include all fields."""
        info = FileInfo(path="/test.rs", name="test.rs", language="rust", line_count=42)
        d = info.to_dict()
        assert d["path"] == "/test.rs"
        assert d["language"] == "rust"
        assert d["line_count"] == 42

    def test_is_modified_flag(self):
        """is_modified should be settable."""
        info = FileInfo(path="/f.py", name="f.py", is_modified=True)
        assert info.is_modified is True

    def test_to_dict_returns_dict(self):
        """to_dict should always return a dict."""
        info = FileInfo(path="/f.py", name="f.py")
        assert isinstance(info.to_dict(), dict)


@pytest.mark.unit
class TestIDEClientEventSystem:
    """Tests for the event handler system on IDEClient."""

    def test_register_and_emit_event(self):
        """Registered handler should be called on emit."""
        client = AntigravityClient()
        received = []
        client.register_event_handler("test_event", lambda data: received.append(data))
        client.emit_event("test_event", {"key": "value"})
        assert len(received) == 1
        assert received[0] == {"key": "value"}

    def test_multiple_handlers_for_same_event(self):
        """Multiple handlers for the same event should all fire."""
        client = AntigravityClient()
        results = []
        client.register_event_handler("evt", lambda d: results.append("a"))
        client.register_event_handler("evt", lambda d: results.append("b"))
        client.emit_event("evt", None)
        assert results == ["a", "b"]

    def test_emit_unregistered_event_no_error(self):
        """Emitting an event with no handlers should not raise."""
        client = AntigravityClient()
        client.emit_event("unregistered_event", {"data": 1})

    def test_handler_receives_none_data(self):
        """Handler should receive None when emitted with no data."""
        client = AntigravityClient()
        received = []
        client.register_event_handler("evt", lambda d: received.append(d))
        client.emit_event("evt")
        assert received == [None]

    def test_failing_handler_does_not_crash(self):
        """A handler that raises should not prevent other handlers or crash."""
        client = AntigravityClient()
        results = []

        def bad_handler(data):
            raise ValueError("boom")

        def good_handler(data):
            results.append("ok")

        client.register_event_handler("evt", bad_handler)
        client.register_event_handler("evt", good_handler)
        client.emit_event("evt", None)
        assert results == ["ok"]


@pytest.mark.unit
class TestIDEClientCommandHistory:
    """Tests for command history and success rate tracking."""

    def test_empty_history_on_new_client(self):
        """New client should have empty command history."""
        client = AntigravityClient()
        assert client.command_history == []

    def test_get_last_command_empty(self):
        """get_last_command should return None on empty history."""
        client = AntigravityClient()
        assert client.get_last_command() is None

    def test_success_rate_empty_history(self):
        """get_success_rate should return 1.0 for empty history."""
        client = AntigravityClient()
        assert client.get_success_rate() == 1.0

    def test_clear_history(self):
        """clear_command_history should empty the history."""
        client = AntigravityClient()
        client._connected = True
        client.execute_command_safe("view_file")
        assert len(client.command_history) > 0
        client.clear_command_history()
        assert len(client.command_history) == 0

    def test_history_is_copy(self):
        """command_history should return a copy, not the original list."""
        client = AntigravityClient()
        client._connected = True
        client.execute_command_safe("view_file")
        history = client.command_history
        history.clear()
        assert len(client.command_history) > 0


@pytest.mark.unit
class TestIDEClientGetFileInfo:
    """Tests for get_file_info helper method."""

    def test_get_file_info_existing_python(self, tmp_path):
        """get_file_info should detect Python language for .py files."""
        py_file = tmp_path / "script.py"
        py_file.write_text("print('hello')\nprint('world')")
        client = AntigravityClient()
        info = client.get_file_info(str(py_file))
        assert info is not None
        assert info.name == "script.py"
        assert info.language == "python"
        assert info.line_count == 2

    def test_get_file_info_nonexistent(self):
        """get_file_info should return None for nonexistent file."""
        client = AntigravityClient()
        assert client.get_file_info("/nonexistent/path.py") is None

    def test_get_file_info_json_language(self, tmp_path):
        """get_file_info should detect JSON language."""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"key": "value"}')
        client = AntigravityClient()
        info = client.get_file_info(str(json_file))
        assert info is not None
        assert info.language == "json"

    def test_get_file_info_unknown_extension(self, tmp_path):
        """get_file_info should return None language for unknown extensions."""
        unknown_file = tmp_path / "data.xyz"
        unknown_file.write_text("content")
        client = AntigravityClient()
        info = client.get_file_info(str(unknown_file))
        assert info is not None
        assert info.language is None

    def test_get_file_info_markdown(self, tmp_path):
        """get_file_info should detect markdown language."""
        md_file = tmp_path / "README.md"
        md_file.write_text("# Title\n\nContent")
        client = AntigravityClient()
        info = client.get_file_info(str(md_file))
        assert info.language == "markdown"
        assert info.line_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
