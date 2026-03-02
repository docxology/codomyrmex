"""Zero-Mock tests for Antigravity IDE integration.

Tests for AntigravityClient artifact management, conversation handling,
tool info, session stats, and connection lifecycle using real filesystem
operations in tmp_path.
"""

import tempfile
from pathlib import Path

import pytest

from codomyrmex.ide import (
    ArtifactError,
    CommandExecutionError,
    IDECommandResult,
    IDEStatus,
)
from codomyrmex.ide.antigravity import (
    AntigravityClient,
    Artifact,
    ConversationContext,
)


@pytest.mark.unit
class TestAntigravityClientInstantiation:
    """Tests for AntigravityClient construction and default state."""

    def test_default_artifact_dir(self):
        """Default artifact_dir should point to ~/.gemini/antigravity/brain/."""
        client = AntigravityClient()
        assert client.artifact_dir == Path.home() / ".gemini" / "antigravity" / "brain"

    def test_custom_artifact_dir(self, tmp_path):
        """Custom artifact_dir should be accepted."""
        client = AntigravityClient(artifact_dir=str(tmp_path / "custom"))
        assert client.artifact_dir == tmp_path / "custom"

    def test_initial_status_is_disconnected(self):
        """Client status should be DISCONNECTED on creation."""
        client = AntigravityClient()
        assert client.status == IDEStatus.DISCONNECTED

    def test_is_connected_returns_false_initially(self):
        """is_connected() should return False on fresh client."""
        client = AntigravityClient()
        assert client.is_connected() is False

    def test_conversation_id_is_none_initially(self):
        """Conversation ID should be None before connecting."""
        client = AntigravityClient()
        assert client.get_conversation_id() is None

    def test_context_is_none_initially(self):
        """Context should be None before connecting."""
        client = AntigravityClient()
        assert client.get_context() is None


@pytest.mark.unit
class TestAntigravityConnection:
    """Tests for connect/disconnect lifecycle with real filesystem."""

    def test_connect_with_conversation_dir(self, tmp_path):
        """connect() should succeed when conversation directory exists."""
        conv_dir = tmp_path / "conv_001"
        conv_dir.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        result = client.connect()
        assert result is True
        assert client.is_connected() is True
        assert client.status == IDEStatus.CONNECTED

    def test_connect_picks_most_recent_conversation(self, tmp_path):
        """connect() should select the most recently modified conversation."""
        import time

        old_dir = tmp_path / "conv_old"
        old_dir.mkdir()
        time.sleep(0.05)
        new_dir = tmp_path / "conv_new"
        new_dir.mkdir()

        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        assert client.get_conversation_id() == "conv_new"

    def test_connect_fails_without_dirs(self, tmp_path):
        """connect() should return False when no conversation dirs exist."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        result = client.connect()
        assert result is False
        assert client.is_connected() is False

    def test_connect_fails_nonexistent_path(self, tmp_path):
        """connect() should return False for nonexistent artifact_dir."""
        client = AntigravityClient(artifact_dir=str(tmp_path / "doesnotexist"))
        result = client.connect()
        assert result is False

    def test_disconnect_resets_state(self, tmp_path):
        """disconnect() should clear connected state and context."""
        conv_dir = tmp_path / "conv_001"
        conv_dir.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        assert client.is_connected() is True

        client.disconnect()
        assert client.is_connected() is False
        assert client.status == IDEStatus.DISCONNECTED
        assert client.get_conversation_id() is None
        assert client.get_context() is None


@pytest.mark.unit
class TestAntigravityCapabilities:
    """Tests for get_capabilities and tool metadata."""

    def test_capabilities_returns_dict(self):
        """get_capabilities() should return a dict with expected keys."""
        client = AntigravityClient()
        caps = client.get_capabilities()
        assert isinstance(caps, dict)
        assert caps["name"] == "Antigravity"
        assert caps["provider"] == "Google DeepMind"

    def test_capabilities_include_tools(self):
        """Capabilities should include a non-empty tools list."""
        client = AntigravityClient()
        caps = client.get_capabilities()
        assert isinstance(caps["tools"], list)
        assert len(caps["tools"]) > 0

    def test_capabilities_include_features(self):
        """Capabilities should include a non-empty features list."""
        client = AntigravityClient()
        caps = client.get_capabilities()
        assert isinstance(caps["features"], list)
        assert "artifact_management" in caps["features"]

    def test_capabilities_reflect_connection_status(self, tmp_path):
        """Capabilities should reflect current connection status."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        caps_before = client.get_capabilities()
        assert caps_before["connected"] is False

        conv_dir = tmp_path / "conv_001"
        conv_dir.mkdir()
        client.connect()
        caps_after = client.get_capabilities()
        assert caps_after["connected"] is True

    def test_get_tool_info_known_tools(self):
        """get_tool_info should return info for documented tools."""
        client = AntigravityClient()
        for tool_name in ("task_boundary", "view_file", "run_command", "grep_search"):
            info = client.get_tool_info(tool_name)
            assert info is not None
            assert info["name"] == tool_name
            assert "description" in info
            assert "parameters" in info

    def test_get_tool_info_unknown_returns_none(self):
        """get_tool_info should return None for unknown tool."""
        client = AntigravityClient()
        assert client.get_tool_info("totally_fake_tool") is None


@pytest.mark.unit
class TestAntigravityArtifactCRUD:
    """Tests for artifact create/read/update/delete with real files."""

    def _make_connected_client(self, tmp_path):
        """Helper to create a connected client with a conversation dir."""
        conv_dir = tmp_path / "conv_test"
        conv_dir.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        return client, conv_dir

    def test_create_artifact_writes_file(self, tmp_path):
        """create_artifact should write a .md file to disk."""
        client, conv_dir = self._make_connected_client(tmp_path)
        result = client.create_artifact("my_task", "# Task content", artifact_type="task")
        assert result["created"] is True
        assert (conv_dir / "my_task.md").exists()
        assert (conv_dir / "my_task.md").read_text() == "# Task content"

    def test_create_artifact_invalid_type_raises(self, tmp_path):
        """create_artifact should raise ArtifactError for invalid type."""
        client, _ = self._make_connected_client(tmp_path)
        with pytest.raises(ArtifactError, match="Invalid artifact type"):
            client.create_artifact("bad", "content", artifact_type="invalid_type")

    def test_get_artifact_returns_content(self, tmp_path):
        """get_artifact should return dict with content field."""
        client, conv_dir = self._make_connected_client(tmp_path)
        (conv_dir / "notes.md").write_text("# Notes")
        result = client.get_artifact("notes")
        assert result is not None
        assert result["content"] == "# Notes"

    def test_get_artifact_nonexistent_returns_none(self, tmp_path):
        """get_artifact should return None for nonexistent artifact."""
        client, _ = self._make_connected_client(tmp_path)
        assert client.get_artifact("does_not_exist") is None

    def test_update_artifact_modifies_file(self, tmp_path):
        """update_artifact should overwrite artifact content on disk."""
        client, conv_dir = self._make_connected_client(tmp_path)
        (conv_dir / "doc.md").write_text("Original")
        result = client.update_artifact("doc", "Updated text")
        assert result["updated"] is True
        assert (conv_dir / "doc.md").read_text() == "Updated text"

    def test_update_artifact_nonexistent_raises(self, tmp_path):
        """update_artifact should raise ArtifactError for missing artifact."""
        client, _ = self._make_connected_client(tmp_path)
        with pytest.raises(ArtifactError, match="Artifact not found"):
            client.update_artifact("ghost", "content")

    def test_delete_artifact_removes_file(self, tmp_path):
        """delete_artifact should remove the .md file from disk."""
        client, conv_dir = self._make_connected_client(tmp_path)
        (conv_dir / "temp.md").write_text("Temporary")
        result = client.delete_artifact("temp")
        assert result is True
        assert not (conv_dir / "temp.md").exists()

    def test_delete_artifact_nonexistent_raises(self, tmp_path):
        """delete_artifact should raise ArtifactError for missing artifact."""
        client, _ = self._make_connected_client(tmp_path)
        with pytest.raises(ArtifactError, match="Artifact not found"):
            client.delete_artifact("nonexistent")

    def test_list_artifacts_returns_created(self, tmp_path):
        """list_artifacts should include artifacts on disk."""
        client, conv_dir = self._make_connected_client(tmp_path)
        (conv_dir / "task.md").write_text("# Task")
        (conv_dir / "walkthrough.md").write_text("# Walkthrough")
        artifacts = client.list_artifacts()
        names = [a["name"] for a in artifacts]
        assert "task" in names
        assert "walkthrough" in names


@pytest.mark.unit
class TestAntigravityConversations:
    """Tests for conversation listing and switching."""

    def test_list_conversations_with_dirs(self, tmp_path):
        """list_conversations should return metadata for each conversation dir."""
        (tmp_path / "conv_a").mkdir()
        (tmp_path / "conv_b").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        convs = client.list_conversations()
        assert len(convs) == 2
        ids = [c["id"] for c in convs]
        assert "conv_a" in ids
        assert "conv_b" in ids

    def test_list_conversations_limit(self, tmp_path):
        """list_conversations should respect the limit parameter."""
        for i in range(5):
            (tmp_path / f"conv_{i:03d}").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        convs = client.list_conversations(limit=2)
        assert len(convs) == 2

    def test_switch_conversation_valid(self, tmp_path):
        """switch_conversation should switch to existing conversation."""
        (tmp_path / "conv_a").mkdir()
        (tmp_path / "conv_b").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        result = client.switch_conversation("conv_a")
        assert result is True
        assert client.get_conversation_id() == "conv_a"

    def test_switch_conversation_invalid(self, tmp_path):
        """switch_conversation should return False for nonexistent conversation."""
        (tmp_path / "conv_real").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        result = client.switch_conversation("conv_fake")
        assert result is False

    def test_list_conversations_empty_dir(self, tmp_path):
        """list_conversations should return empty list for empty artifact_dir."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        assert client.list_conversations() == []


@pytest.mark.unit
class TestAntigravitySessionStats:
    """Tests for session statistics."""

    def test_session_stats_disconnected(self):
        """get_session_stats should work when disconnected."""
        client = AntigravityClient()
        stats = client.get_session_stats()
        assert stats["connected"] is False
        assert stats["artifact_count"] == 0
        assert stats["commands_executed"] == 0
        assert stats["success_rate"] == 1.0

    def test_session_stats_connected(self, tmp_path):
        """get_session_stats should reflect connected state."""
        conv_dir = tmp_path / "conv_001"
        conv_dir.mkdir()
        (conv_dir / "task.md").write_text("# Task")
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        stats = client.get_session_stats()
        assert stats["connected"] is True
        assert stats["artifact_count"] >= 1
        assert stats["conversation_id"] is not None

    def test_session_stats_tracks_commands(self, tmp_path):
        """get_session_stats should track command count."""
        conv_dir = tmp_path / "conv_001"
        conv_dir.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        client.execute_command_safe("view_file", {"path": "/test"})
        stats = client.get_session_stats()
        assert stats["commands_executed"] == 1

    def test_invoke_tool_unknown_returns_failure(self):
        """invoke_tool should return failure IDECommandResult for unknown tool."""
        client = AntigravityClient()
        result = client.invoke_tool("nonexistent_tool", {})
        assert isinstance(result, IDECommandResult)
        assert result.success is False
        assert "Unknown tool" in result.error

    def test_open_file_checks_real_path(self, tmp_path):
        """open_file should return True for existing file, False otherwise."""
        test_file = tmp_path / "exists.py"
        test_file.write_text("# exists")
        client = AntigravityClient()
        assert client.open_file(str(test_file)) is True
        assert client.open_file(str(tmp_path / "missing.py")) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
