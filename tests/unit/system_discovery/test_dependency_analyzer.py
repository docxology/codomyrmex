import os
import pytest
from pathlib import Path

from codomyrmex.system_discovery.core.dependency_analyzer import DependencyAnalyzer


class TestDependencyAnalyzerHasDocs:
    """Tests for DependencyAnalyzer.has_docs."""

    def test_has_readme(self, tmp_path):
        """Test has_docs returns True when README.md exists."""
        analyzer = DependencyAnalyzer(tmp_path, tmp_path)
        mod_dir = tmp_path / "module"
        mod_dir.mkdir()
        (mod_dir / "README.md").write_text("Docs")

        assert analyzer.has_docs(mod_dir) is True

    def test_has_docs_dir(self, tmp_path):
        """Test has_docs returns True when docs directory exists."""
        analyzer = DependencyAnalyzer(tmp_path, tmp_path)
        mod_dir = tmp_path / "module"
        mod_dir.mkdir()
        (mod_dir / "docs").mkdir()

        assert analyzer.has_docs(mod_dir) is True

    def test_has_api_spec(self, tmp_path):
        """Test has_docs returns True when API_SPECIFICATION.md exists."""
        analyzer = DependencyAnalyzer(tmp_path, tmp_path)
        mod_dir = tmp_path / "module"
        mod_dir.mkdir()
        (mod_dir / "API_SPECIFICATION.md").write_text("Spec")

        assert analyzer.has_docs(mod_dir) is True

    def test_has_usage_examples(self, tmp_path):
        """Test has_docs returns True when USAGE_EXAMPLES.md exists."""
        analyzer = DependencyAnalyzer(tmp_path, tmp_path)
        mod_dir = tmp_path / "module"
        mod_dir.mkdir()
        (mod_dir / "USAGE_EXAMPLES.md").write_text("Examples")

        assert analyzer.has_docs(mod_dir) is True

    def test_no_docs(self, tmp_path):
        """Test has_docs returns False when no doc files exist."""
        analyzer = DependencyAnalyzer(tmp_path, tmp_path)
        mod_dir = tmp_path / "module"
        mod_dir.mkdir()
        (mod_dir / "code.py").write_text("print('hello')")

        assert analyzer.has_docs(mod_dir) is False


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


@pytest.mark.unit
class TestDependencyAnalyzerVersion:
    """Test get_module_version from DependencyAnalyzer."""

    def test_get_module_version_found(self, tmp_path: Path):
        """Test successfully parsing __version__ from __init__.py."""
        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "__init__.py").write_text('__version__ = "1.2.3"\n')

        analyzer = DependencyAnalyzer(
            project_root=tmp_path, testing_path=tmp_path / "tests"
        )
        assert analyzer.get_module_version(mod_dir) == "1.2.3"

    def test_get_module_version_not_found(self, tmp_path: Path):
        """Test returning 'unknown' when __version__ is not in __init__.py."""
        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "__init__.py").write_text('other_var = "1.2.3"\n')

        analyzer = DependencyAnalyzer(
            project_root=tmp_path, testing_path=tmp_path / "tests"
        )
        assert analyzer.get_module_version(mod_dir) == "unknown"

    def test_get_module_version_no_init(self, tmp_path: Path):
        """Test returning 'unknown' when __init__.py does not exist."""
        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()

        analyzer = DependencyAnalyzer(
            project_root=tmp_path, testing_path=tmp_path / "tests"
        )
        assert analyzer.get_module_version(mod_dir) == "unknown"

    def test_get_module_version_error(self, tmp_path: Path):
        """Test returning 'unknown' when an error occurs reading __init__.py."""
        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        init_file = mod_dir / "__init__.py"
        init_file.write_text('__version__ = "1.2.3"\n')

        # Make the file unreadable to trigger an exception
        init_file.chmod(0o000)

        analyzer = DependencyAnalyzer(
            project_root=tmp_path, testing_path=tmp_path / "tests"
        )
        try:
            assert analyzer.get_module_version(mod_dir) == "unknown"
        finally:
            # Restore permissions for cleanup
            init_file.chmod(0o644)
