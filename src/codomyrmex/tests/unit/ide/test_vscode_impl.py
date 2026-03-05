"""Zero-mock tests for VSCodeClient implementation."""

import tempfile
from pathlib import Path

import pytest

from codomyrmex.ide import IDEStatus
from codomyrmex.ide.vscode import VSCodeClient


@pytest.mark.unit
class TestVSCodeClientImplementation:
    """Detailed tests for VSCodeClient."""

    def test_connect_lifecycle(self):
        """Test connection lifecycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = VSCodeClient(workspace_path=tmpdir)
            assert client.status == IDEStatus.DISCONNECTED
            assert client.connect() is True
            assert client.is_connected() is True
            client.disconnect()
            assert client.is_connected() is False

    def test_open_close_file(self):
        """Test opening and closing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "test.py"
            f.write_text("print('hello')")

            client = VSCodeClient(workspace_path=tmpdir)
            client.connect()

            assert client.open_file(str(f)) is True
            assert client.open_file("/nonexistent") is False
            assert client.close_file(str(f)) is True

    def test_get_open_files(self):
        """Test getting open files (simulated)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "a.py").write_text("a")
            (Path(tmpdir) / "b.py").write_text("b")

            client = VSCodeClient(workspace_path=tmpdir)
            client.connect()

            open_files = client.get_open_files()
            assert isinstance(open_files, list)
            assert len(open_files) > 0
            assert all(f.endswith(".py") for f in open_files)

    def test_save_operations(self):
        """Test save and save_all."""
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "test.py"
            f.write_text("data")

            client = VSCodeClient(workspace_path=tmpdir)
            client.connect()

            assert client.save_file(str(f)) is True
            assert client.save_all() is True

    def test_settings_management(self):
        """Test reading and updating settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = VSCodeClient(workspace_path=tmpdir)
            client.connect()

            # Initial settings empty
            assert client.get_settings() == {}

            # Update settings
            client.update_settings({"editor.tabSize": 2})
            settings = client.get_settings()
            assert settings["editor.tabSize"] == 2

            # Verify file on disk
            settings_path = Path(tmpdir) / ".vscode" / "settings.json"
            assert settings_path.exists()

    def test_execute_command(self):
        """Test command execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = VSCodeClient(workspace_path=tmpdir)
            client.connect()

            result = client.execute_command("workbench.action.files.save")
            assert result["status"] == "success"
            assert result["command"] == "workbench.action.files.save"
