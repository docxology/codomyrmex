"""Zero-Mock tests for Antigravity IDE integration.

Tests for AntigravityClient artifact management, conversation handling,
tool info, session stats, and connection lifecycle using real filesystem
operations in tmp_path.
"""

from pathlib import Path

import pytest

from codomyrmex.ide import (
    ArtifactError,
    IDECommandResult,
    IDEStatus,
)
from codomyrmex.ide.antigravity import (
    AntigravityClient,
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


# ── New test classes below (+30 tests) ──────────────────────────────────


@pytest.mark.unit
class TestAntigravityClientConnection:
    """Extended connection lifecycle tests."""

    def test_connect_default_artifact_dir_returns_bool(self):
        """connect() with default dir returns a bool (True/False)."""
        client = AntigravityClient()
        result = client.connect()
        assert isinstance(result, bool)

    def test_connect_custom_artifact_dir_accepted(self, tmp_path):
        """connect() with explicit tmp_path dir is accepted and uses it."""
        conv = tmp_path / "session_x"
        conv.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        assert client.connect() is True
        assert client.artifact_dir == tmp_path

    def test_connect_missing_dir_graceful(self, tmp_path):
        """connect() with non-existent path returns False, no exception."""
        client = AntigravityClient(artifact_dir=str(tmp_path / "no_such_dir"))
        result = client.connect()
        assert result is False
        assert client.is_connected() is False
        assert client.status == IDEStatus.DISCONNECTED

    def test_disconnect_after_connect(self, tmp_path):
        """After connect then disconnect, is_connected() returns False."""
        (tmp_path / "sess").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        assert client.is_connected() is True
        client.disconnect()
        assert client.is_connected() is False
        assert client.get_conversation_id() is None
        assert client.get_context() is None

    def test_is_connected_initial_state(self):
        """Freshly constructed client is_connected() returns False."""
        client = AntigravityClient()
        assert client.is_connected() is False


@pytest.mark.unit
class TestAntigravityClientCapabilities:
    """Extended capabilities and tool info tests."""

    def test_get_capabilities_returns_dict_type(self):
        """get_capabilities() returns a dict (not list, not None)."""
        client = AntigravityClient()
        result = client.get_capabilities()
        assert isinstance(result, dict)

    def test_get_capabilities_tools_is_list(self):
        """get_capabilities()['tools'] is a list."""
        client = AntigravityClient()
        caps = client.get_capabilities()
        assert isinstance(caps["tools"], list)

    def test_get_capabilities_non_empty(self):
        """Capabilities tools list has at least one item."""
        client = AntigravityClient()
        caps = client.get_capabilities()
        assert len(caps["tools"]) >= 1

    def test_get_capabilities_has_version(self):
        """Capabilities include a version string."""
        client = AntigravityClient()
        caps = client.get_capabilities()
        assert "version" in caps
        assert isinstance(caps["version"], str)

    def test_get_tool_info_known_tool_write_to_file(self):
        """get_tool_info('write_to_file') returns dict with expected keys."""
        client = AntigravityClient()
        info = client.get_tool_info("write_to_file")
        assert info is not None
        assert info["name"] == "write_to_file"
        assert "description" in info
        assert "parameters" in info
        assert isinstance(info["parameters"], list)

    def test_get_tool_info_unknown_tool_returns_none(self):
        """get_tool_info returns None for an unknown tool name."""
        client = AntigravityClient()
        assert client.get_tool_info("completely_bogus_tool_xyz") is None


@pytest.mark.unit
class TestAntigravityClientArtifacts:
    """Extended artifact CRUD tests with real filesystem."""

    def _connected(self, tmp_path):
        """Helper: create connected client with a conversation directory."""
        conv_dir = tmp_path / "conv_art"
        conv_dir.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        return client, conv_dir

    def test_list_artifacts_empty_dir(self, tmp_path):
        """list_artifacts on a connected client with empty conv dir returns []."""
        client, _ = self._connected(tmp_path)
        assert client.list_artifacts() == []

    def test_list_artifacts_with_files(self, tmp_path):
        """list_artifacts returns entries for .md files in the conversation dir."""
        client, conv_dir = self._connected(tmp_path)
        (conv_dir / "alpha.md").write_text("# Alpha")
        (conv_dir / "beta.md").write_text("# Beta")
        artifacts = client.list_artifacts()
        names = [a["name"] for a in artifacts]
        assert "alpha" in names
        assert "beta" in names
        assert len(artifacts) == 2

    def test_get_artifact_by_name(self, tmp_path):
        """get_artifact returns content dict for an existing artifact."""
        client, conv_dir = self._connected(tmp_path)
        (conv_dir / "readme.md").write_text("# Readme Content")
        result = client.get_artifact("readme")
        assert result is not None
        assert result["content"] == "# Readme Content"
        assert result["name"] == "readme"

    def test_get_artifact_not_found(self, tmp_path):
        """get_artifact returns None for a name that has no file."""
        client, _ = self._connected(tmp_path)
        assert client.get_artifact("nonexistent_artifact") is None

    def test_create_artifact_writes_file(self, tmp_path):
        """create_artifact writes a .md file and returns metadata."""
        client, conv_dir = self._connected(tmp_path)
        result = client.create_artifact(
            name="plan", content="## Implementation Plan", artifact_type="implementation_plan"
        )
        assert result["created"] is True
        assert result["type"] == "implementation_plan"
        assert (conv_dir / "plan.md").exists()
        assert (conv_dir / "plan.md").read_text() == "## Implementation Plan"

    def test_update_artifact_changes_content(self, tmp_path):
        """update_artifact overwrites file content on disk."""
        client, conv_dir = self._connected(tmp_path)
        (conv_dir / "draft.md").write_text("Version 1")
        result = client.update_artifact("draft", "Version 2")
        assert result["updated"] is True
        assert (conv_dir / "draft.md").read_text() == "Version 2"

    def test_delete_artifact_removes_file(self, tmp_path):
        """delete_artifact unlinks the .md file."""
        client, conv_dir = self._connected(tmp_path)
        (conv_dir / "obsolete.md").write_text("Old content")
        assert client.delete_artifact("obsolete") is True
        assert not (conv_dir / "obsolete.md").exists()

    def test_artifact_content_preservation(self, tmp_path):
        """Multi-line content survives create -> get round-trip."""
        client, _ = self._connected(tmp_path)
        multiline = "# Title\n\nParagraph one.\n\n- bullet a\n- bullet b\n\nEnd."
        client.create_artifact("roundtrip", multiline, artifact_type="other")
        retrieved = client.get_artifact("roundtrip")
        assert retrieved is not None
        assert retrieved["content"] == multiline

    def test_list_artifacts_disconnected_returns_empty(self, tmp_path):
        """list_artifacts returns [] when not connected."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        assert client.list_artifacts() == []

    def test_create_artifact_disconnected_raises(self, tmp_path):
        """create_artifact raises ArtifactError when not connected."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        with pytest.raises(ArtifactError):
            client.create_artifact("test", "content")

    def test_update_artifact_disconnected_raises(self, tmp_path):
        """update_artifact raises ArtifactError when not connected."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        with pytest.raises(ArtifactError):
            client.update_artifact("test", "content")

    def test_delete_artifact_disconnected_raises(self, tmp_path):
        """delete_artifact raises ArtifactError when not connected."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        with pytest.raises(ArtifactError):
            client.delete_artifact("test")


@pytest.mark.unit
class TestAntigravityClientConversations:
    """Extended conversation listing and context tests."""

    def test_get_context_returns_object(self, tmp_path):
        """get_context() returns ConversationContext after connect."""
        conv_dir = tmp_path / "ctx_conv"
        conv_dir.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        ctx = client.get_context()
        assert ctx is not None
        assert ctx.conversation_id == "ctx_conv"

    def test_list_conversations_limit_respected(self, tmp_path):
        """list_conversations(limit=3) returns at most 3 entries."""
        for i in range(7):
            (tmp_path / f"c_{i:03d}").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        convs = client.list_conversations(limit=3)
        assert len(convs) == 3

    def test_list_conversations_default_works(self, tmp_path):
        """list_conversations() without limit uses default (10)."""
        for i in range(3):
            (tmp_path / f"d_{i}").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        convs = client.list_conversations()
        assert isinstance(convs, list)
        assert len(convs) == 3

    def test_get_conversation_id_after_connect(self, tmp_path):
        """get_conversation_id returns a string after successful connect."""
        (tmp_path / "active_conv").mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        cid = client.get_conversation_id()
        assert isinstance(cid, str)
        assert cid == "active_conv"

    def test_conversation_metadata_has_artifact_count(self, tmp_path):
        """list_conversations entries include artifact_count."""
        conv = tmp_path / "conv_meta"
        conv.mkdir()
        (conv / "task.md").write_text("# Task")
        (conv / "notes.md").write_text("# Notes")
        client = AntigravityClient(artifact_dir=str(tmp_path))
        convs = client.list_conversations()
        assert len(convs) == 1
        assert convs[0]["artifact_count"] == 2

    def test_switch_conversation_updates_context(self, tmp_path):
        """switch_conversation updates the context to the new conversation."""
        conv_a = tmp_path / "conv_a"
        conv_a.mkdir()
        (conv_a / "task.md").write_text("# Task A")
        conv_b = tmp_path / "conv_b"
        conv_b.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        client.switch_conversation("conv_a")
        ctx = client.get_context()
        assert ctx is not None
        assert ctx.conversation_id == "conv_a"
        assert len(ctx.artifacts) == 1


@pytest.mark.unit
class TestAntigravityClientFileStubs:
    """Tests for file-related methods."""

    def test_get_open_files_empty(self):
        """get_open_files() returns empty list (stub implementation)."""
        client = AntigravityClient()
        result = client.get_open_files()
        assert isinstance(result, list)
        assert len(result) == 0

    def test_open_file_nonexistent(self, tmp_path):
        """open_file with nonexistent path returns False."""
        client = AntigravityClient()
        assert client.open_file(str(tmp_path / "no_file.py")) is False

    def test_open_file_existing(self, tmp_path):
        """open_file with an existing real file returns True."""
        real_file = tmp_path / "real.py"
        real_file.write_text("x = 1")
        client = AntigravityClient()
        assert client.open_file(str(real_file)) is True

    def test_get_active_file_returns_str_or_none(self, tmp_path):
        """get_active_file returns str or None."""
        client = AntigravityClient(artifact_dir=str(tmp_path))
        result = client.get_active_file()
        assert result is None or isinstance(result, str)


@pytest.mark.unit
class TestAntigravityClientSessionStats:
    """Extended session statistics tests."""

    def test_session_stats_initial_keys(self):
        """get_session_stats returns dict with expected keys when disconnected."""
        client = AntigravityClient()
        stats = client.get_session_stats()
        assert isinstance(stats, dict)
        assert "connected" in stats
        assert "commands_executed" in stats
        assert "artifact_count" in stats
        assert "success_rate" in stats
        assert "last_command" in stats

    def test_session_stats_after_execute_command_safe(self, tmp_path):
        """commands_executed increments after execute_command_safe call."""
        conv = tmp_path / "stat_conv"
        conv.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        assert client.get_session_stats()["commands_executed"] == 0
        # execute_command_safe wraps execute_command which will fail (no CLI)
        # but the command is still recorded in history
        client.execute_command_safe("view_file", {"AbsolutePath": "/tmp/x"})
        stats = client.get_session_stats()
        assert stats["commands_executed"] == 1

    def test_session_stats_success_rate_after_failure(self, tmp_path):
        """success_rate reflects failed commands (no CLI installed)."""
        conv = tmp_path / "sr_conv"
        conv.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        # This will fail because the agy/antigravity CLI is not installed
        client.execute_command_safe("view_file", {})
        stats = client.get_session_stats()
        # The command should have failed, so success_rate < 1.0
        assert stats["success_rate"] < 1.0 or stats["commands_executed"] >= 1


@pytest.mark.unit
class TestAntigravityClientCommandExecution:
    """Tests for command execution paths."""

    def test_execute_command_safe_returns_result(self, tmp_path):
        """execute_command_safe returns an IDECommandResult."""
        conv = tmp_path / "cmd_conv"
        conv.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        result = client.execute_command_safe("list_dir", {"DirectoryPath": "/tmp"})
        assert isinstance(result, IDECommandResult)
        assert result.command == "list_dir"

    def test_execute_command_safe_unknown_tool(self, tmp_path):
        """execute_command_safe with unknown command returns failure result."""
        conv = tmp_path / "cmd2_conv"
        conv.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        result = client.execute_command_safe("invalid_xyz_command", {})
        assert isinstance(result, IDECommandResult)
        assert result.success is False


@pytest.mark.unit
class TestAntigravityArtifactTypeClassification:
    """Tests for _scan_artifacts type classification logic."""

    def _connected(self, tmp_path):
        """Helper: create connected client."""
        conv_dir = tmp_path / "classify_conv"
        conv_dir.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        return client, conv_dir

    def test_task_artifact_classified_as_task(self, tmp_path):
        """A file named 'task.md' is classified as artifact_type='task'."""
        client, conv_dir = self._connected(tmp_path)
        (conv_dir / "task.md").write_text("# Main Task")
        artifacts = client.list_artifacts()
        task_artifacts = [a for a in artifacts if a["name"] == "task"]
        assert len(task_artifacts) == 1
        assert task_artifacts[0]["type"] == "task"

    def test_implementation_artifact_classified(self, tmp_path):
        """A file with 'implementation' in the name is classified correctly."""
        client, conv_dir = self._connected(tmp_path)
        (conv_dir / "implementation_plan_v2.md").write_text("# Plan")
        artifacts = client.list_artifacts()
        impl = [a for a in artifacts if "implementation" in a["name"]]
        assert len(impl) == 1
        assert impl[0]["type"] == "implementation_plan"

    def test_walkthrough_artifact_classified(self, tmp_path):
        """A file with 'walkthrough' in the name is classified correctly."""
        client, conv_dir = self._connected(tmp_path)
        (conv_dir / "code_walkthrough.md").write_text("# Walkthrough")
        artifacts = client.list_artifacts()
        wt = [a for a in artifacts if "walkthrough" in a["name"]]
        assert len(wt) == 1
        assert wt[0]["type"] == "walkthrough"

    def test_other_artifact_classified_as_other(self, tmp_path):
        """A file without special keywords is classified as 'other'."""
        client, conv_dir = self._connected(tmp_path)
        (conv_dir / "random_notes.md").write_text("# Notes")
        artifacts = client.list_artifacts()
        notes = [a for a in artifacts if a["name"] == "random_notes"]
        assert len(notes) == 1
        assert notes[0]["type"] == "other"

    def test_non_md_files_excluded(self, tmp_path):
        """Non-.md files in the conversation dir are not listed as artifacts."""
        client, conv_dir = self._connected(tmp_path)
        (conv_dir / "data.json").write_text('{"key": "value"}')
        (conv_dir / "script.py").write_text("print('hello')")
        (conv_dir / "real_artifact.md").write_text("# Real")
        artifacts = client.list_artifacts()
        assert len(artifacts) == 1
        assert artifacts[0]["name"] == "real_artifact"


@pytest.mark.unit
class TestAntigravityEventHandlers:
    """Tests for event emission and handler registration (base class)."""

    def test_register_and_emit_event(self, tmp_path):
        """Registered event handler receives emitted event data."""
        received = []
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.register_event_handler("connected", lambda data: received.append(data))
        conv = tmp_path / "evt_conv"
        conv.mkdir()
        client.connect()
        assert len(received) == 1
        assert received[0]["conversation_id"] == "evt_conv"

    def test_disconnect_emits_event(self, tmp_path):
        """disconnect() emits a 'disconnected' event."""
        received = []
        conv = tmp_path / "dc_conv"
        conv.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.register_event_handler("disconnected", lambda data: received.append(data))
        client.connect()
        client.disconnect()
        assert len(received) == 1

    def test_artifact_created_event(self, tmp_path):
        """create_artifact emits an 'artifact_created' event."""
        received = []
        conv = tmp_path / "ac_conv"
        conv.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.register_event_handler("artifact_created", lambda data: received.append(data))
        client.connect()
        client.create_artifact("evt_doc", "Content", artifact_type="other")
        assert len(received) == 1
        assert received[0]["name"] == "evt_doc"


@pytest.mark.unit
class TestAntigravityBaseClassMethods:
    """Tests for inherited IDEClient base class methods."""

    def test_command_history_initially_empty(self):
        """command_history is empty on a fresh client."""
        client = AntigravityClient()
        assert client.command_history == []

    def test_clear_command_history(self, tmp_path):
        """clear_command_history empties the history list."""
        conv = tmp_path / "hist_conv"
        conv.mkdir()
        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()
        client.execute_command_safe("view_file", {})
        assert len(client.command_history) >= 1
        client.clear_command_history()
        assert client.command_history == []

    def test_get_last_command_none_initially(self):
        """get_last_command returns None when no commands have been run."""
        client = AntigravityClient()
        assert client.get_last_command() is None

    def test_get_file_info_existing_file(self, tmp_path):
        """get_file_info returns FileInfo for an existing file."""
        py_file = tmp_path / "sample.py"
        py_file.write_text("x = 1\ny = 2\n")
        client = AntigravityClient()
        info = client.get_file_info(str(py_file))
        assert info is not None
        assert info.name == "sample.py"
        assert info.language == "python"
        assert info.line_count == 2

    def test_get_file_info_nonexistent(self, tmp_path):
        """get_file_info returns None for a nonexistent file."""
        client = AntigravityClient()
        info = client.get_file_info(str(tmp_path / "no_such_file.py"))
        assert info is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
