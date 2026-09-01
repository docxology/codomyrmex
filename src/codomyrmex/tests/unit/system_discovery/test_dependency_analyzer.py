import datetime
from pathlib import Path

import pytest

from codomyrmex.system_discovery.core.dependency_analyzer import DependencyAnalyzer


class TestGetLastModified:
    def test_get_last_modified_with_files(self, tmp_path):
        """Test get_last_modified returns correctly formatted string based on file mtime."""
        analyzer = DependencyAnalyzer(project_root=tmp_path, testing_path=tmp_path)

        # Create module directory and files
        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()

        f1 = mod_dir / "file1.py"
        f2 = mod_dir / "file2.py"
        f1.write_text("print('f1')")
        f2.write_text("print('f2')")

        result = analyzer.get_last_modified(mod_dir)
        assert result != "unknown"
        assert "-" in result  # YYYY-MM-DD
        assert ":" in result  # HH:MM:SS

    def test_get_last_modified_no_files(self, tmp_path):
        """Test get_last_modified handles directory with no python files."""
        analyzer = DependencyAnalyzer(project_root=tmp_path, testing_path=tmp_path)
        mod_dir = tmp_path / "emptymod"
        mod_dir.mkdir()

        result = analyzer.get_last_modified(mod_dir)
        assert result == "unknown"

    def test_get_last_modified_exception(self, tmp_path):
        """Test get_last_modified handles exceptions without mocking."""
        analyzer = DependencyAnalyzer(project_root=tmp_path, testing_path=tmp_path)
        mod_dir = tmp_path / "errormod"
        mod_dir.mkdir()

        # To trigger an exception during glob or stat without mocking (due to zero-mock policy),
        # we can pass a file path instead of a directory to cause NotADirectoryError,
        # or pass an unreadable directory (PermissionError).

        # We will create a file instead of a directory so that glob() raises an error
        file_as_dir = tmp_path / "not_a_dir.py"
        file_as_dir.write_text("print('hello')")

        # When glob is called on a file instead of a directory, it may fail,
        # or stat may fail. Let's create a directory with no permissions.
        import os

        unreadable_dir = tmp_path / "unreadable"
        unreadable_dir.mkdir()
        # Create a file inside first
        (unreadable_dir / "file.py").write_text("test")

        # Remove read permissions
        unreadable_dir.chmod(0o000)

        try:
            result = analyzer.get_last_modified(unreadable_dir)
            assert result == "unknown"
        finally:
            # Restore permissions so pytest can clean up
            unreadable_dir.chmod(0o777)
