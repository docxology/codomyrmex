"""Tests for codomyrmex.system_discovery.core.dependency_analyzer module."""

from pathlib import Path

import pytest

from codomyrmex.system_discovery.core.dependency_analyzer import DependencyAnalyzer


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
