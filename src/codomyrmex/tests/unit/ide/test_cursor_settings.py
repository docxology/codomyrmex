"""Zero-Mock tests for Cursor IDE settings management.

Tests for CursorClient workspace initialization, .cursorrules management,
model selection, connection lifecycle, and settings persistence using
real filesystem operations in tmp_path.
"""

import json
from pathlib import Path

import pytest

from codomyrmex.ide import CommandExecutionError, IDEError
from codomyrmex.ide.cursor import CursorClient


@pytest.mark.unit
class TestCursorClientInitialization:
    """Tests for CursorClient construction and workspace setup."""

    def test_default_workspace_is_cwd(self):
        """Default workspace_path should be cwd."""
        client = CursorClient()
        assert client.workspace_path == Path.cwd()

    def test_custom_workspace_path(self, tmp_path):
        """Custom workspace_path should be stored."""
        client = CursorClient(workspace_path=str(tmp_path))
        assert client.workspace_path == tmp_path

    def test_cursorrules_path_derived_from_workspace(self, tmp_path):
        """_cursorrules_path should be workspace/.cursorrules."""
        client = CursorClient(workspace_path=str(tmp_path))
        assert client._cursorrules_path == tmp_path / ".cursorrules"

    def test_initial_not_connected(self):
        """Client should not be connected initially."""
        client = CursorClient()
        assert client.is_connected() is False

    def test_connect_with_existing_workspace(self, tmp_path):
        """connect() should succeed for existing workspace directory."""
        client = CursorClient(workspace_path=str(tmp_path))
        assert client.connect() is True
        assert client.is_connected() is True

    def test_connect_with_cursor_dir(self, tmp_path):
        """connect() should succeed when .cursor directory exists."""
        (tmp_path / ".cursor").mkdir()
        client = CursorClient(workspace_path=str(tmp_path))
        assert client.connect() is True

    def test_connect_with_cursorrules_file(self, tmp_path):
        """connect() should succeed when .cursorrules file exists."""
        (tmp_path / ".cursorrules").write_text("rules content")
        client = CursorClient(workspace_path=str(tmp_path))
        assert client.connect() is True


@pytest.mark.unit
class TestCursorRulesManagement:
    """Tests for .cursorrules get/set operations."""

    def test_get_rules_no_file(self, tmp_path):
        """get_rules should indicate file does not exist."""
        client = CursorClient(workspace_path=str(tmp_path))
        rules = client.get_rules()
        assert rules["exists"] is False
        assert rules["content"] == ""

    def test_get_rules_with_file(self, tmp_path):
        """get_rules should return content of .cursorrules file."""
        rules_content = "You are a helpful assistant.\nAlways use TypeScript."
        (tmp_path / ".cursorrules").write_text(rules_content)
        client = CursorClient(workspace_path=str(tmp_path))
        rules = client.get_rules()
        assert rules["content"] == rules_content
        assert "path" in rules

    def test_update_rules_writes_string(self, tmp_path):
        """update_rules should write string content to .cursorrules."""
        client = CursorClient(workspace_path=str(tmp_path))
        client.connect()
        result = client.update_rules({"content": "New rules content"})
        assert result is True
        assert (tmp_path / ".cursorrules").read_text() == "New rules content"

    def test_update_rules_writes_dict_as_json(self, tmp_path):
        """update_rules should serialize dict content to JSON."""
        client = CursorClient(workspace_path=str(tmp_path))
        client.connect()
        rules_dict = {"language": "typescript", "strict": True}
        result = client.update_rules({"content": rules_dict})
        assert result is True
        written = json.loads((tmp_path / ".cursorrules").read_text())
        assert written["language"] == "typescript"
        assert written["strict"] is True

    def test_update_rules_requires_connection(self, tmp_path):
        """update_rules should raise IDEError when not connected."""
        client = CursorClient(workspace_path=str(tmp_path))
        with pytest.raises(IDEError, match="Not connected"):
            client.update_rules({"content": "rules"})

    def test_get_rules_survives_update_cycle(self, tmp_path):
        """Rules should be readable after writing via update_rules."""
        client = CursorClient(workspace_path=str(tmp_path))
        client.connect()
        client.update_rules({"content": "Persistent rules"})
        rules = client.get_rules()
        assert rules["content"] == "Persistent rules"


@pytest.mark.unit
class TestCursorModelSelection:
    """Tests for AI model selection."""

    def test_get_models_returns_list(self):
        """get_models should return a list of model names."""
        client = CursorClient()
        models = client.get_models()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_set_model_valid(self):
        """set_model should return True for known model."""
        client = CursorClient()
        models = client.get_models()
        assert client.set_model(models[0]) is True

    def test_set_model_invalid(self):
        """set_model should return False for unknown model name."""
        client = CursorClient()
        assert client.set_model("nonexistent-model-xyz-123") is False

    def test_models_in_capabilities(self):
        """Models should be listed in get_capabilities output."""
        client = CursorClient()
        caps = client.get_capabilities()
        assert "models" in caps
        assert caps["models"] == client.get_models()

    def test_capabilities_features_non_empty(self):
        """Features in capabilities should be a non-empty list."""
        client = CursorClient()
        caps = client.get_capabilities()
        assert isinstance(caps["features"], list)
        assert "composer" in caps["features"]


@pytest.mark.unit
class TestCursorCommandExecution:
    """Tests for command execution in Cursor client."""

    def test_execute_command_when_connected(self, tmp_path):
        """execute_command should succeed when connected."""
        client = CursorClient(workspace_path=str(tmp_path))
        client.connect()
        result = client.execute_command("test_command", {"arg": "value"})
        assert result["status"] == "success"
        assert result["command"] == "test_command"

    def test_execute_command_when_disconnected(self, tmp_path):
        """execute_command should raise CommandExecutionError when disconnected."""
        client = CursorClient(workspace_path=str(tmp_path))
        with pytest.raises(CommandExecutionError, match="Not connected"):
            client.execute_command("any_command")

    def test_disconnect_prevents_commands(self, tmp_path):
        """After disconnect(), execute_command should fail."""
        client = CursorClient(workspace_path=str(tmp_path))
        client.connect()
        client.disconnect()
        assert client.is_connected() is False
        with pytest.raises(CommandExecutionError):
            client.execute_command("test")

    def test_open_file_checks_existence(self, tmp_path):
        """open_file should verify file exists on disk."""
        test_file = tmp_path / "real.py"
        test_file.write_text("# real")
        client = CursorClient(workspace_path=str(tmp_path))
        assert client.open_file(str(test_file)) is True
        assert client.open_file(str(tmp_path / "fake.py")) is False

    def test_get_open_files_returns_list(self):
        """get_open_files should return a list (currently empty)."""
        client = CursorClient()
        result = client.get_open_files()
        assert isinstance(result, list)


@pytest.mark.unit
class TestCursorSettingsPersistence:
    """Tests for settings write/read cycles using tmp_path."""

    def test_update_then_read_rules(self, tmp_path):
        """Written rules should be readable in a new client instance."""
        client1 = CursorClient(workspace_path=str(tmp_path))
        client1.connect()
        client1.update_rules({"content": "Rule set A"})

        client2 = CursorClient(workspace_path=str(tmp_path))
        rules = client2.get_rules()
        assert rules["content"] == "Rule set A"

    def test_overwrite_rules(self, tmp_path):
        """Updating rules twice should overwrite the first set."""
        client = CursorClient(workspace_path=str(tmp_path))
        client.connect()
        client.update_rules({"content": "Version 1"})
        client.update_rules({"content": "Version 2"})
        rules = client.get_rules()
        assert rules["content"] == "Version 2"

    def test_empty_rules_write(self, tmp_path):
        """Writing empty content should create an empty .cursorrules file."""
        client = CursorClient(workspace_path=str(tmp_path))
        client.connect()
        client.update_rules({"content": ""})
        assert (tmp_path / ".cursorrules").exists()
        assert (tmp_path / ".cursorrules").read_text() == ""

    def test_workspace_path_in_capabilities(self, tmp_path):
        """get_capabilities should include the workspace path."""
        client = CursorClient(workspace_path=str(tmp_path))
        caps = client.get_capabilities()
        assert caps["workspace"] == str(tmp_path)

    def test_capabilities_name_is_cursor(self):
        """get_capabilities name should be 'Cursor'."""
        client = CursorClient()
        assert client.get_capabilities()["name"] == "Cursor"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
