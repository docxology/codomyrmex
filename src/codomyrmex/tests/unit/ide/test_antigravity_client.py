"""Tests for codomyrmex.ide.antigravity.client.AntigravityClient.

Zero-Mock compliant — all tests use real filesystem operations via tmp_path.
Imports directly from client.py (not __init__.py) to drive coverage of that
module.
"""

from pathlib import Path

import pytest

from codomyrmex.ide import IDECommandResult
from codomyrmex.ide.antigravity.client import AntigravityClient
from codomyrmex.ide.antigravity.models import (
    ArtifactError,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _connected_client(tmp_path: Path) -> tuple["AntigravityClient", Path]:
    """Create a connected AntigravityClient with a conversation directory."""
    conv_dir = tmp_path / "test_conv"
    conv_dir.mkdir()
    client = AntigravityClient(artifact_dir=str(tmp_path))
    client.connect()
    return client, conv_dir


# ---------------------------------------------------------------------------
# Construction and defaults
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestClientConstruction:
    """Construction and default state."""

    def test_default_artifact_dir(self):
        """Default artifact_dir points to ~/.gemini/antigravity/brain/."""
        client = AntigravityClient()
        assert client.artifact_dir == Path.home() / ".gemini" / "antigravity" / "brain"

    def test_custom_artifact_dir(self, tmp_path):
        """Explicit artifact_dir is accepted and stored."""
        client = AntigravityClient(artifact_dir=str(tmp_path / "custom"))
        assert client.artifact_dir == tmp_path / "custom"

    def test_initial_not_connected(self):
        """Freshly created client is not connected."""
        client = AntigravityClient()
        assert client.is_connected() is False

    def test_initial_conversation_id_none(self):
        """conversation_id is None before connect."""
        client = AntigravityClient()
        assert client.get_conversation_id() is None

    def test_initial_context_none(self):
        """Context is None before connect."""
        client = AntigravityClient()
        assert client.get_context() is None

    def test_tools_list_non_empty(self):
        """TOOLS class attribute is a non-empty list."""
        assert isinstance(AntigravityClient.TOOLS, list)
        assert len(AntigravityClient.TOOLS) > 0

    def test_artifact_types_list(self):
        """ARTIFACT_TYPES includes expected types."""
        types = AntigravityClient.ARTIFACT_TYPES
        assert "task" in types
        assert "other" in types


# ---------------------------------------------------------------------------
# Connection lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestClientConnection:
    """connect() / disconnect() lifecycle tests."""

    def test_connect_returns_false_empty_dir(self, tmp_path):
        """connect() returns False when no conversation dirs exist."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        assert client.connect() is False
        assert client.is_connected() is False

    def test_connect_returns_false_nonexistent_dir(self, tmp_path):
        """connect() returns False for nonexistent artifact_dir."""
        client = AntigravityClient(artifact_dir=str(tmp_path / "no_such"))
        assert client.connect() is False

    def test_connect_succeeds_with_conv_dir(self, tmp_path):
        """connect() returns True when at least one conversation dir exists."""
        (tmp_path / "conv_a").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        assert client.connect() is True
        assert client.is_connected() is True

    def test_connect_sets_conversation_id(self, tmp_path):
        """connect() sets conversation_id to the most-recent dir name."""
        (tmp_path / "sess_1").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        assert client.get_conversation_id() == "sess_1"

    def test_connect_picks_most_recent(self, tmp_path):
        """connect() picks the directory with the most recent mtime."""
        import time
        (tmp_path / "old").mkdir()
        time.sleep(0.05)
        (tmp_path / "new").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        assert client.get_conversation_id() == "new"

    def test_disconnect_resets_state(self, tmp_path):
        """disconnect() clears all connection state."""
        client, _ = _connected_client(tmp_path)
        assert client.is_connected() is True
        client.disconnect()
        assert client.is_connected() is False
        assert client.get_conversation_id() is None
        assert client.get_context() is None

    def test_connect_disconnect_connect_cycle(self, tmp_path):
        """Can connect, disconnect, and reconnect successfully."""
        (tmp_path / "c1").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        assert client.connect() is True
        client.disconnect()
        assert client.is_connected() is False
        assert client.connect() is True
        assert client.is_connected() is True


# ---------------------------------------------------------------------------
# Capabilities
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestClientCapabilities:
    """get_capabilities() and get_tool_info() tests."""

    def test_capabilities_returns_dict(self):
        """get_capabilities returns a dict."""
        caps = AntigravityClient().get_capabilities()
        assert isinstance(caps, dict)

    def test_capabilities_name_is_antigravity(self):
        """Capabilities name is 'Antigravity'."""
        caps = AntigravityClient().get_capabilities()
        assert caps["name"] == "Antigravity"

    def test_capabilities_tools_is_list(self):
        """Capabilities tools is a non-empty list."""
        caps = AntigravityClient().get_capabilities()
        assert isinstance(caps["tools"], list)
        assert len(caps["tools"]) > 0

    def test_capabilities_reflects_connected_false(self):
        """Capabilities connected field reflects disconnected state."""
        client = AntigravityClient()
        assert client.get_capabilities()["connected"] is False

    def test_capabilities_reflects_connected_true(self, tmp_path):
        """Capabilities connected field reflects connected state."""
        client, _ = _connected_client(tmp_path)
        assert client.get_capabilities()["connected"] is True

    def test_capabilities_has_artifact_types(self):
        """Capabilities includes artifact_types."""
        caps = AntigravityClient().get_capabilities()
        assert "artifact_types" in caps
        assert isinstance(caps["artifact_types"], list)

    def test_get_tool_info_known_tool(self):
        """get_tool_info returns dict for known tool."""
        client = AntigravityClient()
        info = client.get_tool_info("task_boundary")
        assert info is not None
        assert info["name"] == "task_boundary"
        assert "description" in info
        assert "parameters" in info

    def test_get_tool_info_view_file(self):
        """get_tool_info works for view_file."""
        info = AntigravityClient().get_tool_info("view_file")
        assert info is not None
        assert "AbsolutePath" in info["parameters"]

    def test_get_tool_info_unknown_returns_none(self):
        """get_tool_info returns None for unknown tool."""
        assert AntigravityClient().get_tool_info("nonexistent_xyz") is None

    def test_get_tool_info_grep_search(self):
        """get_tool_info returns info for grep_search."""
        info = AntigravityClient().get_tool_info("grep_search")
        assert info is not None
        assert "Query" in info["parameters"]


# ---------------------------------------------------------------------------
# execute_command
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestClientExecuteCommand:
    """execute_command() behavior."""

    def test_execute_command_when_not_connected_raises(self):
        """execute_command raises CommandExecutionError when disconnected."""
        from codomyrmex.ide import CommandExecutionError
        client = AntigravityClient()
        with pytest.raises(CommandExecutionError, match="Not connected"):
            client.execute_command("view_file")

    def test_execute_command_unknown_raises(self, tmp_path):
        """execute_command raises CommandExecutionError for unknown command."""
        from codomyrmex.ide import CommandExecutionError
        client, _ = _connected_client(tmp_path)
        with pytest.raises(CommandExecutionError, match="Unknown command"):
            client.execute_command("totally_unknown_cmd_xyz")

    def test_execute_command_returns_dict(self, tmp_path):
        """execute_command returns a dict with status and command keys."""
        client, _ = _connected_client(tmp_path)
        result = client.execute_command("view_file", {"AbsolutePath": "/tmp"})
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert result["command"] == "view_file"

    def test_execute_command_with_args(self, tmp_path):
        """execute_command passes args through to result."""
        client, _ = _connected_client(tmp_path)
        args = {"AbsolutePath": "/test/path"}
        result = client.execute_command("view_file", args)
        assert result["args"] == args


# ---------------------------------------------------------------------------
# File methods (open_file, get_open_files, get_active_file)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestClientFileMethods:
    """File-related methods."""

    def test_open_file_existing(self, tmp_path):
        """open_file returns True for an existing file."""
        f = tmp_path / "test.py"
        f.write_text("x = 1")
        client = AntigravityClient()
        assert client.open_file(str(f)) is True

    def test_open_file_nonexistent(self, tmp_path):
        """open_file returns False for nonexistent path."""
        client = AntigravityClient()
        assert client.open_file(str(tmp_path / "missing.py")) is False

    def test_get_open_files_empty(self):
        """get_open_files returns empty list."""
        result = AntigravityClient().get_open_files()
        assert result == []

    def test_get_active_file_no_context(self):
        """get_active_file returns None or a file path when no context (falls back to cwd scan)."""
        result = AntigravityClient().get_active_file()
        assert result is None or isinstance(result, str)


# ---------------------------------------------------------------------------
# Artifact CRUD
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestClientArtifactCRUD:
    """Artifact create / read / update / delete operations."""

    def test_create_artifact_writes_file(self, tmp_path):
        """create_artifact writes content to disk."""
        client, conv_dir = _connected_client(tmp_path)
        result = client.create_artifact("my_task", "# Task", artifact_type="task")
        assert result["created"] is True
        assert (conv_dir / "my_task.md").read_text() == "# Task"

    def test_create_artifact_invalid_type_raises(self, tmp_path):
        """create_artifact raises ArtifactError for invalid type."""
        client, _ = _connected_client(tmp_path)
        with pytest.raises(ArtifactError, match="Invalid artifact type"):
            client.create_artifact("x", "content", artifact_type="bogus_type")

    def test_create_artifact_disconnected_raises(self, tmp_path):
        """create_artifact raises ArtifactError when not connected."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        with pytest.raises(ArtifactError):
            client.create_artifact("x", "content")

    def test_get_artifact_returns_content(self, tmp_path):
        """get_artifact returns dict with content field."""
        client, conv_dir = _connected_client(tmp_path)
        (conv_dir / "notes.md").write_text("# Notes content")
        result = client.get_artifact("notes")
        assert result is not None
        assert result["content"] == "# Notes content"
        assert result["name"] == "notes"

    def test_get_artifact_nonexistent_returns_none(self, tmp_path):
        """get_artifact returns None for missing artifact."""
        client, _ = _connected_client(tmp_path)
        assert client.get_artifact("does_not_exist") is None

    def test_get_artifact_not_connected_returns_none(self, tmp_path):
        """get_artifact returns None when not connected."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        assert client.get_artifact("anything") is None

    def test_update_artifact_modifies_content(self, tmp_path):
        """update_artifact overwrites content on disk."""
        client, conv_dir = _connected_client(tmp_path)
        (conv_dir / "doc.md").write_text("Original")
        result = client.update_artifact("doc", "Updated")
        assert result["updated"] is True
        assert (conv_dir / "doc.md").read_text() == "Updated"

    def test_update_artifact_missing_raises(self, tmp_path):
        """update_artifact raises ArtifactError for missing file."""
        client, _ = _connected_client(tmp_path)
        with pytest.raises(ArtifactError, match="Artifact not found"):
            client.update_artifact("ghost", "content")

    def test_delete_artifact_removes_file(self, tmp_path):
        """delete_artifact removes the .md file."""
        client, conv_dir = _connected_client(tmp_path)
        (conv_dir / "temp.md").write_text("Temp")
        assert client.delete_artifact("temp") is True
        assert not (conv_dir / "temp.md").exists()

    def test_delete_artifact_missing_raises(self, tmp_path):
        """delete_artifact raises ArtifactError for nonexistent artifact."""
        client, _ = _connected_client(tmp_path)
        with pytest.raises(ArtifactError, match="Artifact not found"):
            client.delete_artifact("nonexistent")

    def test_list_artifacts_empty(self, tmp_path):
        """list_artifacts returns [] for empty conversation dir."""
        client, _ = _connected_client(tmp_path)
        assert client.list_artifacts() == []

    def test_list_artifacts_with_files(self, tmp_path):
        """list_artifacts includes all .md files."""
        client, conv_dir = _connected_client(tmp_path)
        (conv_dir / "task.md").write_text("# Task")
        (conv_dir / "notes.md").write_text("# Notes")
        artifacts = client.list_artifacts()
        names = {a["name"] for a in artifacts}
        assert "task" in names
        assert "notes" in names

    def test_list_artifacts_disconnected_empty(self, tmp_path):
        """list_artifacts returns [] when not connected."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        assert client.list_artifacts() == []

    def test_create_then_get_round_trip(self, tmp_path):
        """Create artifact then retrieve it returns same content."""
        client, _ = _connected_client(tmp_path)
        content = "# Round trip\n\nLine 2.\n"
        client.create_artifact("rt", content, artifact_type="other")
        retrieved = client.get_artifact("rt")
        assert retrieved is not None
        assert retrieved["content"] == content


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestClientConversations:
    """list_conversations() and switch_conversation() tests."""

    def test_list_conversations_empty_dir(self, tmp_path):
        """list_conversations returns [] for empty artifact_dir."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        assert client.list_conversations() == []

    def test_list_conversations_returns_metadata(self, tmp_path):
        """list_conversations returns dict with id, path, artifact_count."""
        (tmp_path / "conv_a").mkdir()
        (tmp_path / "conv_b").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        convs = client.list_conversations()
        assert len(convs) == 2
        ids = {c["id"] for c in convs}
        assert "conv_a" in ids
        assert "conv_b" in ids

    def test_list_conversations_limit(self, tmp_path):
        """list_conversations respects the limit parameter."""
        for i in range(5):
            (tmp_path / f"c_{i}").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        assert len(client.list_conversations(limit=2)) == 2

    def test_list_conversations_default_limit(self, tmp_path):
        """list_conversations default limit is 10."""
        for i in range(15):
            (tmp_path / f"d_{i:02d}").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        assert len(client.list_conversations()) == 10

    def test_switch_conversation_valid(self, tmp_path):
        """switch_conversation to existing dir returns True."""
        (tmp_path / "conv_x").mkdir()
        (tmp_path / "conv_y").mkdir()
        client, _ = _connected_client(tmp_path)
        # Note: _connected_client uses "test_conv", switch to conv_x
        assert client.switch_conversation("conv_x") is True
        assert client.get_conversation_id() == "conv_x"

    def test_switch_conversation_nonexistent(self, tmp_path):
        """switch_conversation returns False for nonexistent conversation."""
        client, _ = _connected_client(tmp_path)
        assert client.switch_conversation("does_not_exist") is False

    def test_switch_conversation_updates_context(self, tmp_path):
        """switch_conversation reloads context for new conversation."""
        conv_a = tmp_path / "conv_a"
        conv_a.mkdir()
        (conv_a / "task.md").write_text("# Task A")
        client, _ = _connected_client(tmp_path)
        client.switch_conversation("conv_a")
        ctx = client.get_context()
        assert ctx is not None
        assert ctx.conversation_id == "conv_a"

    def test_list_conversations_artifact_count(self, tmp_path):
        """list_conversations includes correct artifact_count."""
        conv = tmp_path / "conv_with_arts"
        conv.mkdir()
        (conv / "a.md").write_text("a")
        (conv / "b.md").write_text("b")
        client = AntigravityClient(artifact_dir=str(tmp_path))
        convs = client.list_conversations()
        assert len(convs) == 1
        assert convs[0]["artifact_count"] == 2


# ---------------------------------------------------------------------------
# Session statistics
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestClientSessionStats:
    """get_session_stats() tests."""

    def test_session_stats_keys(self):
        """get_session_stats returns dict with expected keys."""
        stats = AntigravityClient().get_session_stats()
        assert isinstance(stats, dict)
        for key in ("connected", "conversation_id", "artifact_count",
                    "commands_executed", "success_rate", "last_command"):
            assert key in stats

    def test_session_stats_disconnected_defaults(self):
        """Disconnected client has 0 artifacts and 0 commands."""
        stats = AntigravityClient().get_session_stats()
        assert stats["connected"] is False
        assert stats["artifact_count"] == 0
        assert stats["commands_executed"] == 0

    def test_session_stats_connected(self, tmp_path):
        """Connected client shows connected=True and has conversation_id."""
        client, _ = _connected_client(tmp_path)
        stats = client.get_session_stats()
        assert stats["connected"] is True
        assert stats["conversation_id"] is not None

    def test_session_stats_artifact_count(self, tmp_path):
        """get_session_stats artifact_count reflects artifacts in the context."""
        # Seed the artifact file before connecting so context picks it up.
        conv_dir = tmp_path / "test_conv"
        conv_dir.mkdir()
        (conv_dir / "art.md").write_text("# Art")
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        stats = client.get_session_stats()
        assert stats["artifact_count"] >= 1


# ---------------------------------------------------------------------------
# invoke_tool
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestClientInvokeTool:
    """invoke_tool() tests."""

    def test_invoke_tool_unknown_returns_failure(self):
        """invoke_tool for unknown tool returns IDECommandResult with failure."""
        client = AntigravityClient()
        result = client.invoke_tool("unknown_tool_xyz", {})
        assert isinstance(result, IDECommandResult)
        assert result.success is False
        assert "Unknown tool" in result.error

    def test_invoke_tool_known_tool_disconnected(self, tmp_path):
        """invoke_tool for known tool on disconnected client attempts execution."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        # Not connected, but tool name is valid — execute_command_safe handles it
        result = client.invoke_tool("list_dir", {"DirectoryPath": "/tmp"})
        assert isinstance(result, IDECommandResult)
        assert result.command == "list_dir"


# ---------------------------------------------------------------------------
# Artifact type classification (_scan_artifacts)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestClientArtifactClassification:
    """Artifact type detection from filename."""

    def test_task_md_classified_as_task(self, tmp_path):
        """task.md is classified as artifact_type='task'."""
        client, conv_dir = _connected_client(tmp_path)
        (conv_dir / "task.md").write_text("# Main task")
        arts = client.list_artifacts()
        task = [a for a in arts if a["name"] == "task"]
        assert len(task) == 1
        assert task[0]["type"] == "task"

    def test_implementation_name_classified(self, tmp_path):
        """File with 'implementation' in name is 'implementation_plan'."""
        client, conv_dir = _connected_client(tmp_path)
        (conv_dir / "implementation_v2.md").write_text("# Plan")
        arts = client.list_artifacts()
        impl = [a for a in arts if "implementation" in a["name"]]
        assert len(impl) == 1
        assert impl[0]["type"] == "implementation_plan"

    def test_walkthrough_classified(self, tmp_path):
        """File with 'walkthrough' in name is 'walkthrough'."""
        client, conv_dir = _connected_client(tmp_path)
        (conv_dir / "code_walkthrough.md").write_text("# Walkthrough")
        arts = client.list_artifacts()
        wt = [a for a in arts if "walkthrough" in a["name"]]
        assert len(wt) == 1
        assert wt[0]["type"] == "walkthrough"

    def test_unknown_classified_as_other(self, tmp_path):
        """File with no special name is classified as 'other'."""
        client, conv_dir = _connected_client(tmp_path)
        (conv_dir / "random_notes.md").write_text("# Notes")
        arts = client.list_artifacts()
        other = [a for a in arts if a["name"] == "random_notes"]
        assert len(other) == 1
        assert other[0]["type"] == "other"

    def test_non_md_files_excluded(self, tmp_path):
        """Only .md files are included in artifact scans."""
        client, conv_dir = _connected_client(tmp_path)
        (conv_dir / "data.json").write_text("{}")
        (conv_dir / "script.py").write_text("x = 1")
        (conv_dir / "real.md").write_text("# Real")
        arts = client.list_artifacts()
        assert len(arts) == 1
        assert arts[0]["name"] == "real"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
