"""Tests for Cursor IDE get_active_file implementation -- zero-mock policy enforced.

Validates the CursorClient.get_active_file method which scans the workspace
for the most recently modified source file. No mocks, stubs, or monkeypatch.
"""

import tempfile
import time
from pathlib import Path

import pytest

from codomyrmex.ide.cursor import CursorClient


@pytest.mark.unit
class TestGetActiveFileBasic:
    """Basic contract tests for get_active_file."""

    def test_returns_none_when_not_connected(self):
        """get_active_file returns None when client is not connected."""
        client = CursorClient()
        assert client.is_connected() is False
        assert client.get_active_file() is None

    def test_returns_none_for_empty_workspace(self):
        """get_active_file returns None when workspace has no source files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = CursorClient(workspace_path=tmpdir)
            client.connect()
            assert client.get_active_file() is None

    def test_returns_string_for_workspace_with_files(self):
        """get_active_file returns a string path when source files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "main.py").write_text("# main")
            client = CursorClient(workspace_path=tmpdir)
            client.connect()
            result = client.get_active_file()
            assert isinstance(result, str)

    def test_returns_absolute_path(self):
        """get_active_file returns an absolute path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app.py").write_text("# app")
            client = CursorClient(workspace_path=tmpdir)
            client.connect()
            result = client.get_active_file()
            assert result is not None
            assert Path(result).is_absolute()

    def test_callable_attribute(self):
        """get_active_file is a callable method on CursorClient."""
        client = CursorClient()
        assert callable(client.get_active_file)


@pytest.mark.unit
class TestGetActiveFileMostRecent:
    """Tests that get_active_file returns the most recently modified file."""

    def test_returns_newest_file(self):
        """get_active_file returns the file with the latest mtime."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = CursorClient(workspace_path=tmpdir)
            client.connect()

            (Path(tmpdir) / "old.py").write_text("# old")
            time.sleep(0.05)
            (Path(tmpdir) / "new.py").write_text("# new")

            result = client.get_active_file()
            assert result is not None
            assert result.endswith("new.py")

    def test_handles_single_file(self):
        """get_active_file works with a single file in workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "only.py").write_text("# only file")
            client = CursorClient(workspace_path=tmpdir)
            client.connect()
            result = client.get_active_file()
            assert result is not None
            assert "only.py" in result


@pytest.mark.unit
class TestGetActiveFileExtensions:
    """Tests for file extension filtering in get_active_file."""

    def test_recognizes_python_files(self):
        """get_active_file returns .py files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "script.py").write_text("print('hello')")
            client = CursorClient(workspace_path=tmpdir)
            client.connect()
            result = client.get_active_file()
            assert result is not None
            assert result.endswith(".py")

    def test_recognizes_javascript_files(self):
        """get_active_file returns .js files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app.js").write_text("console.log('hi')")
            client = CursorClient(workspace_path=tmpdir)
            client.connect()
            result = client.get_active_file()
            assert result is not None
            assert result.endswith(".js")

    def test_recognizes_typescript_files(self):
        """get_active_file returns .ts files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "index.ts").write_text("const x: number = 1;")
            client = CursorClient(workspace_path=tmpdir)
            client.connect()
            result = client.get_active_file()
            assert result is not None
            assert result.endswith(".ts")

    def test_recognizes_markdown_files(self):
        """get_active_file returns .md files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "README.md").write_text("# README")
            client = CursorClient(workspace_path=tmpdir)
            client.connect()
            result = client.get_active_file()
            assert result is not None
            assert result.endswith(".md")

    def test_recognizes_json_files(self):
        """get_active_file returns .json files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "config.json").write_text('{"key": "value"}')
            client = CursorClient(workspace_path=tmpdir)
            client.connect()
            result = client.get_active_file()
            assert result is not None
            assert result.endswith(".json")

    def test_ignores_non_source_extensions(self):
        """get_active_file ignores non-source files like .log, .tmp, .exe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "debug.log").write_text("log content")
            (Path(tmpdir) / "data.tmp").write_text("temp data")
            (Path(tmpdir) / "binary.exe").write_text("fake binary")
            client = CursorClient(workspace_path=tmpdir)
            client.connect()
            result = client.get_active_file()
            assert result is None

    def test_prefers_newest_among_mixed_extensions(self):
        """get_active_file returns the newest source file among mixed types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "old.py").write_text("# old")
            (Path(tmpdir) / "data.log").write_text("log")
            time.sleep(0.05)
            (Path(tmpdir) / "new.ts").write_text("const x = 1;")

            client = CursorClient(workspace_path=tmpdir)
            client.connect()
            result = client.get_active_file()
            assert result is not None
            assert result.endswith(".ts")


@pytest.mark.unit
class TestGetActiveFileEdgeCases:
    """Edge case tests for get_active_file."""

    def test_nonexistent_workspace_returns_none(self):
        """get_active_file returns None for nonexistent workspace path."""
        client = CursorClient(workspace_path="/tmp/definitely_nonexistent_dir_xyz123")
        client._connected = True  # Force connected for edge case test
        result = client.get_active_file()
        assert result is None

    def test_ignores_directories(self):
        """get_active_file does not return directories, only files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "subdir.py").mkdir()  # dir named with .py extension
            client = CursorClient(workspace_path=tmpdir)
            client.connect()
            result = client.get_active_file()
            assert result is None

    def test_disconnect_then_get_active_file(self):
        """get_active_file returns None after disconnect."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "file.py").write_text("# code")
            client = CursorClient(workspace_path=tmpdir)
            client.connect()
            assert client.get_active_file() is not None
            client.disconnect()
            assert client.get_active_file() is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
