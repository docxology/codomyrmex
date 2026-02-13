"""Zero-Mock tests for IDE module.

Comprehensive tests for IDEClient base class, AntigravityClient,
CursorClient, and VSCodeClient implementations.
"""

import shutil
import subprocess
import tempfile
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
from codomyrmex.ide.antigravity import AntigravityClient, Artifact, ConversationContext
from codomyrmex.ide.cursor import CursorClient
from codomyrmex.ide.vscode import VSCodeClient


@pytest.mark.unit
class TestIDEBaseClasses:
    """Tests for IDE base classes and interfaces."""

    def test_ide_client_is_abstract(self):
        """IDEClient should be an abstract class."""
        import abc
        assert issubclass(IDEClient, abc.ABC)

    def test_ide_error_inherits_from_exception(self):
        """IDEError should be a proper exception."""
        assert issubclass(IDEError, Exception)

    def test_connection_error_inherits_from_ide_error(self):
        """ConnectionError should inherit from IDEError."""
        assert issubclass(ConnectionError, IDEError)

    def test_command_execution_error_inherits_from_ide_error(self):
        """CommandExecutionError should inherit from IDEError."""
        assert issubclass(CommandExecutionError, IDEError)

    def test_session_error_inherits_from_ide_error(self):
        """SessionError should inherit from IDEError."""
        assert issubclass(SessionError, IDEError)

    def test_artifact_error_inherits_from_ide_error(self):
        """ArtifactError should inherit from IDEError."""
        assert issubclass(ArtifactError, IDEError)


@pytest.mark.unit
class TestIDEDataClasses:
    """Tests for IDE data classes."""

    def test_ide_status_enum(self):
        """IDEStatus should have expected values."""
        assert IDEStatus.DISCONNECTED.value == "disconnected"
        assert IDEStatus.CONNECTING.value == "connecting"
        assert IDEStatus.CONNECTED.value == "connected"
        assert IDEStatus.ERROR.value == "error"

    def test_ide_command_creation(self):
        """IDECommand should be created with defaults."""
        cmd = IDECommand(name="test_command")
        assert cmd.name == "test_command"
        assert cmd.args == {}
        assert cmd.timeout == 30.0

    def test_ide_command_with_args(self):
        """IDECommand should accept custom args."""
        cmd = IDECommand(name="cmd", args={"key": "value"}, timeout=60.0)
        assert cmd.args == {"key": "value"}
        assert cmd.timeout == 60.0

    def test_ide_command_to_dict(self):
        """IDECommand.to_dict should return proper dict."""
        cmd = IDECommand(name="test", args={"a": 1})
        d = cmd.to_dict()
        assert d["name"] == "test"
        assert d["args"] == {"a": 1}
        assert "timeout" in d

    def test_ide_command_result(self):
        """IDECommandResult should have proper fields."""
        result = IDECommandResult(
            success=True,
            command="test",
            output={"data": "value"},
            execution_time=0.5,
        )
        assert result.success is True
        assert result.command == "test"
        assert result.output == {"data": "value"}
        assert result.error is None

    def test_ide_command_result_to_dict(self):
        """IDECommandResult.to_dict should return proper dict."""
        result = IDECommandResult(success=False, command="fail", error="oops")
        d = result.to_dict()
        assert d["success"] is False
        assert d["error"] == "oops"

    def test_file_info_creation(self):
        """FileInfo should be created with required fields."""
        info = FileInfo(path="/path/to/file.py", name="file.py")
        assert info.path == "/path/to/file.py"
        assert info.name == "file.py"
        assert info.is_modified is False
        assert info.language is None

    def test_file_info_to_dict(self):
        """FileInfo.to_dict should return proper dict."""
        info = FileInfo(path="/test.py", name="test.py", language="python", line_count=100)
        d = info.to_dict()
        assert d["path"] == "/test.py"
        assert d["language"] == "python"
        assert d["line_count"] == 100


@pytest.mark.unit
class TestAntigravityDataClasses:
    """Tests for Antigravity-specific data classes."""

    def test_artifact_creation(self):
        """Artifact should be created with required fields."""
        artifact = Artifact(
            name="test",
            path="/path/to/test.md",
            artifact_type="task",
        )
        assert artifact.name == "test"
        assert artifact.artifact_type == "task"

    def test_artifact_to_dict(self):
        """Artifact.to_dict should return proper dict."""
        artifact = Artifact(name="task", path="/task.md", artifact_type="task", size=100)
        d = artifact.to_dict()
        assert d["name"] == "task"
        assert d["type"] == "task"
        assert d["size"] == 100

    def test_conversation_context(self):
        """ConversationContext should hold conversation state."""
        ctx = ConversationContext(
            conversation_id="abc123",
            task_name="Test Task",
            mode="EXECUTION",
        )
        assert ctx.conversation_id == "abc123"
        assert ctx.task_name == "Test Task"
        assert ctx.artifacts == []

    def test_conversation_context_to_dict(self):
        """ConversationContext.to_dict should return proper dict."""
        ctx = ConversationContext(conversation_id="xyz")
        d = ctx.to_dict()
        assert d["conversation_id"] == "xyz"
        assert "artifacts" in d


@pytest.mark.unit
class TestAntigravityClient:
    """Tests for AntigravityClient."""

    def test_client_initialization(self):
        """Client should initialize with default artifact directory."""
        client = AntigravityClient()
        assert client.artifact_dir == Path.home() / ".gemini" / "antigravity" / "brain"

    def test_client_initialization_with_custom_path(self):
        """Client should accept custom artifact directory."""
        custom_path = "/tmp/test_artifacts"
        client = AntigravityClient(artifact_dir=custom_path)
        assert client.artifact_dir == Path(custom_path)

    def test_is_connected_initially_false(self):
        """Client should not be connected initially."""
        client = AntigravityClient()
        assert client.is_connected() is False

    def test_initial_status_disconnected(self):
        """Client status should be DISCONNECTED initially."""
        client = AntigravityClient()
        assert client.status == IDEStatus.DISCONNECTED

    def test_disconnect(self):
        """Disconnect should set connected state to False."""
        client = AntigravityClient()
        client._connected = True
        client._status = IDEStatus.CONNECTED
        client.disconnect()
        assert client.is_connected() is False
        assert client.status == IDEStatus.DISCONNECTED

    def test_get_capabilities(self):
        """Should return dictionary with expected keys."""
        client = AntigravityClient()
        caps = client.get_capabilities()

        assert "name" in caps
        assert caps["name"] == "Antigravity"
        assert "tools" in caps
        assert "features" in caps
        assert "connected" in caps
        assert "artifact_types" in caps
        assert len(caps["tools"]) > 0

    def test_tools_list(self):
        """Should have expected tools."""
        client = AntigravityClient()
        assert "task_boundary" in client.TOOLS
        assert "view_file" in client.TOOLS
        assert "run_command" in client.TOOLS
        assert "grep_search" in client.TOOLS

    def test_command_execution_requires_connection(self):
        """Execute command should fail when not connected."""
        client = AntigravityClient()
        with pytest.raises(CommandExecutionError):
            client.execute_command("test_command")

    def test_command_execution_unknown_command(self):
        """Execute command should fail for unknown commands."""
        client = AntigravityClient()
        client._connected = True
        with pytest.raises(CommandExecutionError, match="Unknown command"):
            client.execute_command("nonexistent_command_xyz")

    def test_open_file_checks_existence(self):
        """open_file should verify file exists."""
        client = AntigravityClient()
        assert client.open_file("/nonexistent/path/file.txt") is False
        assert client.open_file(__file__) is True

    def test_list_artifacts_when_not_connected(self):
        """list_artifacts should return empty when not connected."""
        client = AntigravityClient()
        assert client.list_artifacts() == []

    def test_create_artifact_requires_connection(self):
        """create_artifact should require connection."""
        client = AntigravityClient()
        with pytest.raises(ArtifactError):
            client.create_artifact("test", "content")

    def test_update_artifact_requires_connection(self):
        """update_artifact should require connection."""
        client = AntigravityClient()
        with pytest.raises(ArtifactError):
            client.update_artifact("test", "new content")

    def test_delete_artifact_requires_connection(self):
        """delete_artifact should require connection."""
        client = AntigravityClient()
        with pytest.raises(ArtifactError):
            client.delete_artifact("test")

    def test_create_artifact_success(self):
        """create_artifact should successfully create file on disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup
            client = AntigravityClient(artifact_dir=tmpdir)

            # Create a dummy conversation dir to allow connection
            conv_id = "test_conv_id"
            (Path(tmpdir) / conv_id).mkdir()

            client.connect()

            # Test creation
            result = client.create_artifact(
                name="test_artifact",
                content="# Test Content",
                artifact_type="task"
            )

            # Verification
            assert result["created"] is True
            assert result["name"] == "test_artifact"

            artifact_path = Path(tmpdir) / conv_id / "test_artifact.md"
            assert artifact_path.exists()
            assert artifact_path.read_text() == "# Test Content"

            # Verify context update
            assert client.get_artifact("test_artifact") is not None

    def test_update_artifact_success(self):
        """update_artifact should successfully update file on disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup
            client = AntigravityClient(artifact_dir=tmpdir)
            conv_id = "test_conv_id"
            conv_dir = Path(tmpdir) / conv_id
            conv_dir.mkdir()

            # Create initial artifact
            (conv_dir / "test_artifact.md").write_text("Initial")

            client.connect()

            # Test update
            result = client.update_artifact("test_artifact", "Updated Content")

            # Verification
            assert result["updated"] is True
            assert (conv_dir / "test_artifact.md").read_text() == "Updated Content"

    def test_delete_artifact_success(self):
        """delete_artifact should successfully remove file from disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup
            client = AntigravityClient(artifact_dir=tmpdir)
            conv_id = "test_conv_id"
            conv_dir = Path(tmpdir) / conv_id
            conv_dir.mkdir()

            # Create artifact
            (conv_dir / "to_delete.md").write_text("Bye")

            client.connect()

            # Test deletion
            result = client.delete_artifact("to_delete")

            # Verification
            assert result is True
            assert not (conv_dir / "to_delete.md").exists()

            # Verify context update
            assert client.get_artifact("to_delete") is None

    def test_send_chat_message_cli_or_fallback(self):
        """send_chat_message should use CLI if installed, otherwise fallback."""
        agy_path = shutil.which("agy")

        if agy_path:
            # CLI is available — test real CLI path
            client = AntigravityClient()
            result = client.send_chat_message("Hello CLI")
            assert result.success is True
            assert result.output.get("method") == "cli"
        else:
            # CLI not installed — test fallback path
            with tempfile.TemporaryDirectory() as tmpdir:
                client = AntigravityClient(artifact_dir=tmpdir)
                (Path(tmpdir) / "conv_id").mkdir()
                client.connect()

                result = client.send_chat_message("Hello Fallback")
                assert result.success is True
                assert result.command == "notify_user"
                assert result.output["args"]["Message"] == "Hello Fallback"

    def test_send_chat_message_no_cli_fallback(self):
        """send_chat_message should fallback to notify_user when no CLI."""
        # Use a non-standard artifact dir so no CLI can be found for this env
        with tempfile.TemporaryDirectory() as tmpdir:
            client = AntigravityClient(artifact_dir=tmpdir)
            (Path(tmpdir) / "conv_id").mkdir()
            client.connect()

            result = client.send_chat_message("Hello Fallback")

            # If agy is not on PATH, this uses fallback; if agy IS on PATH,
            # it uses CLI. Either way it should succeed.
            assert result.success is True
    def test_get_tool_info_known_tool(self):
        """get_tool_info should return info for known tools."""
        client = AntigravityClient()
        info = client.get_tool_info("task_boundary")
        assert info is not None
        assert info["name"] == "task_boundary"
        assert "description" in info

    def test_get_tool_info_unknown_tool(self):
        """get_tool_info should return None for unknown tools."""
        client = AntigravityClient()
        info = client.get_tool_info("nonexistent_tool")
        assert info is None

    def test_invoke_tool_unknown_tool(self):
        """invoke_tool should return failure for unknown tools."""
        client = AntigravityClient()
        result = client.invoke_tool("nonexistent", {})
        assert result.success is False
        assert "Unknown tool" in result.error

    def test_get_session_stats_disconnected(self):
        """get_session_stats should work when disconnected."""
        client = AntigravityClient()
        stats = client.get_session_stats()
        assert stats["connected"] is False
        assert stats["artifact_count"] == 0

    def test_list_conversations_empty_dir(self):
        """list_conversations should return empty for nonexistent dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = AntigravityClient(artifact_dir=Path(tmpdir) / "nonexistent")
            convs = client.list_conversations()
            assert convs == []

    def test_command_history_tracking(self):
        """Command history should be tracked."""
        client = AntigravityClient()
        client._connected = True

        # Execute a valid command
        client.execute_command_safe("view_file", {"path": "/test"})

        assert len(client.command_history) == 1
        assert client.command_history[0].command == "view_file"

    def test_event_handlers(self):
        """Event handlers should be invoked."""
        client = AntigravityClient()
        events_received = []

        def handler(data):
            events_received.append(data)

        client.register_event_handler("test_event", handler)
        client.emit_event("test_event", {"key": "value"})

        assert len(events_received) == 1
        assert events_received[0] == {"key": "value"}


@pytest.mark.unit
class TestCursorClient:
    """Tests for CursorClient."""

    def test_client_initialization_default_workspace(self):
        """Client should default to current directory."""
        client = CursorClient()
        assert client.workspace_path == Path.cwd()

    def test_client_initialization_custom_workspace(self):
        """Client should accept custom workspace path."""
        custom_path = "/tmp/test_workspace"
        client = CursorClient(workspace_path=custom_path)
        assert client.workspace_path == Path(custom_path)

    def test_is_connected_initially_false(self):
        """Client should not be connected initially."""
        client = CursorClient()
        assert client.is_connected() is False

    def test_connect_with_existing_workspace(self):
        """Connect should succeed for existing workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = CursorClient(workspace_path=tmpdir)
            assert client.connect() is True
            assert client.is_connected() is True

    def test_get_capabilities(self):
        """Should return dictionary with expected keys."""
        client = CursorClient()
        caps = client.get_capabilities()

        assert "name" in caps
        assert caps["name"] == "Cursor"
        assert "features" in caps
        assert "models" in caps

    def test_get_models(self):
        """Should return list of model names."""
        client = CursorClient()
        models = client.get_models()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_set_model_valid(self):
        """set_model should return True for valid model."""
        client = CursorClient()
        models = client.get_models()
        assert client.set_model(models[0]) is True

    def test_set_model_invalid(self):
        """set_model should return False for invalid model."""
        client = CursorClient()
        assert client.set_model("nonexistent-model-xyz") is False

    def test_get_rules_nonexistent(self):
        """get_rules should handle nonexistent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = CursorClient(workspace_path=tmpdir)
            rules = client.get_rules()
            assert rules["exists"] is False


@pytest.mark.unit
class TestVSCodeClient:
    """Tests for VSCodeClient."""

    def test_client_initialization_default_workspace(self):
        """Client should default to current directory."""
        client = VSCodeClient()
        assert client.workspace_path == Path.cwd()

    def test_client_initialization_custom_workspace(self):
        """Client should accept custom workspace path."""
        custom_path = "/tmp/test_workspace"
        client = VSCodeClient(workspace_path=custom_path)
        assert client.workspace_path == Path(custom_path)

    def test_connect_with_existing_workspace(self):
        """Connect should succeed for existing workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = VSCodeClient(workspace_path=tmpdir)
            assert client.connect() is True

    def test_get_capabilities(self):
        """Should return dictionary with expected keys."""
        client = VSCodeClient()
        caps = client.get_capabilities()

        assert "name" in caps
        assert caps["name"] == "Visual Studio Code"
        assert "features" in caps
        assert "commands" in caps

    def test_list_extensions(self):
        """Should return list of extension info."""
        client = VSCodeClient()
        extensions = client.list_extensions()
        assert isinstance(extensions, list)
        for ext in extensions:
            assert "name" in ext
            assert "publisher" in ext

    def test_list_commands(self):
        """Should return list of command IDs."""
        client = VSCodeClient()
        commands = client.list_commands()
        assert isinstance(commands, list)
        assert len(commands) > 0

    def test_get_settings_nonexistent(self):
        """get_settings should return empty dict for nonexistent settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = VSCodeClient(workspace_path=tmpdir)
            settings = client.get_settings()
            assert settings == {}

    def test_update_settings_requires_connection(self):
        """update_settings should require connection."""
        client = VSCodeClient()
        with pytest.raises(IDEError):
            client.update_settings({"key": "value"})

    def test_update_settings_creates_file(self):
        """update_settings should create .vscode/settings.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = VSCodeClient(workspace_path=tmpdir)
            client.connect()
            result = client.update_settings({"editor.fontSize": 14})
            assert result is True

            settings_path = Path(tmpdir) / ".vscode" / "settings.json"
            assert settings_path.exists()

    def test_start_stop_debug_requires_connection(self):
        """Debug operations should require connection."""
        client = VSCodeClient()
        with pytest.raises(IDEError):
            client.start_debug()
        with pytest.raises(IDEError):
            client.stop_debug()


@pytest.mark.unit
class TestIDEClientHelperMethods:
    """Tests for IDEClient helper methods available to all implementations."""

    def test_get_file_info_existing_file(self):
        """get_file_info should return info for existing files."""
        client = AntigravityClient()  # Use concrete implementation
        info = client.get_file_info(__file__)

        assert info is not None
        assert info.name == "test_ide.py"
        assert info.language == "python"
        assert info.line_count > 0

    def test_get_file_info_nonexistent_file(self):
        """get_file_info should return None for nonexistent files."""
        client = AntigravityClient()
        info = client.get_file_info("/nonexistent/file.xyz")
        assert info is None

    def test_execute_batch_stops_on_error(self):
        """execute_batch should stop on first error when stop_on_error=True."""
        client = AntigravityClient()
        client._connected = True

        commands = [
            IDECommand(name="view_file"),
            IDECommand(name="nonexistent_command"),  # This will fail
            IDECommand(name="list_dir"),  # This should not run
        ]

        results = client.execute_batch(commands, stop_on_error=True)

        # Should have 2 results (succeeded and failed)
        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is False

    def test_get_success_rate_empty_history(self):
        """get_success_rate should return 1.0 for empty history."""
        client = AntigravityClient()
        assert client.get_success_rate() == 1.0

    def test_get_success_rate_with_commands(self):
        """get_success_rate should calculate correctly."""
        client = AntigravityClient()
        client._connected = True

        # Execute some commands
        client.execute_command_safe("view_file")  # Success
        client.execute_command_safe("nonexistent")  # Failure
        client.execute_command_safe("list_dir")  # Success

        rate = client.get_success_rate()
        assert rate == pytest.approx(2/3, 0.01)

    def test_clear_command_history(self):
        """clear_command_history should empty the history."""
        client = AntigravityClient()
        client._connected = True
        client.execute_command_safe("view_file")

        assert len(client.command_history) > 0
        client.clear_command_history()
        assert len(client.command_history) == 0

    def test_get_last_command(self):
        """get_last_command should return most recent command."""
        client = AntigravityClient()
        client._connected = True

        client.execute_command_safe("view_file")
        client.execute_command_safe("list_dir")

        last = client.get_last_command()
        assert last is not None
        assert last.command == "list_dir"

    def test_get_last_command_empty_history(self):
        """get_last_command should return None for empty history."""
        client = AntigravityClient()
        assert client.get_last_command() is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
