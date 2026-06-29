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
