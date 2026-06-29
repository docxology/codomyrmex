from pathlib import Path

import pytest

from codomyrmex.system_discovery.core.dependency_analyzer import DependencyAnalyzer


@pytest.mark.unit
class TestDependencyAnalyzerHasTests:
    def test_has_tests_exists(self, tmp_path):
        testing_path = tmp_path / "testing"
        unit_dir = testing_path / "unit"
        unit_dir.mkdir(parents=True)
        (unit_dir / "test_mymod.py").write_text("# test")

        analyzer = DependencyAnalyzer(project_root=tmp_path, testing_path=testing_path)
        assert analyzer.has_tests("mymod") is True

    def test_has_tests_not_exists(self, tmp_path):
        testing_path = tmp_path / "testing"
        testing_path.mkdir(parents=True)

        analyzer = DependencyAnalyzer(project_root=tmp_path, testing_path=testing_path)
        assert analyzer.has_tests("mymod") is False
