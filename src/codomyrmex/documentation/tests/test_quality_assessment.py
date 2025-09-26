"""Tests for documentation quality assessment modules."""

import pytest
from pathlib import Path
import tempfile
import os


class TestDocumentationQualityAnalyzer:
    """Test cases for DocumentationQualityAnalyzer."""

    def test_analyzer_creation(self):
        """Test creating a quality analyzer."""
        from codomyrmex.documentation.quality_assessment import DocumentationQualityAnalyzer

        analyzer = DocumentationQualityAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_file')

    def test_file_analysis(self):
        """Test analyzing a documentation file."""
        from codomyrmex.documentation.quality_assessment import DocumentationQualityAnalyzer

        analyzer = DocumentationQualityAnalyzer()

        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Documentation\n\n## Installation\n```bash\npip install test\n```\n## Usage\nExample usage here.")
            temp_path = Path(f.name)

        try:
            result = analyzer.analyze_file(temp_path)
            assert "overall_score" in result
            assert isinstance(result["overall_score"], float)
            assert 0 <= result["overall_score"] <= 100
        finally:
            temp_path.unlink()


class TestDocumentationConsistencyChecker:
    """Test cases for DocumentationConsistencyChecker."""

    def test_checker_creation(self):
        """Test creating a consistency checker."""
        from codomyrmex.documentation.consistency_checker import DocumentationConsistencyChecker

        checker = DocumentationConsistencyChecker()
        assert checker is not None
        assert hasattr(checker, 'check_project_consistency')

    def test_consistency_check(self):
        """Test checking project consistency."""
        from codomyrmex.documentation.consistency_checker import DocumentationConsistencyChecker

        checker = DocumentationConsistencyChecker()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create some test files
            (temp_path / "README.md").write_text("# Test Project\n\n## Installation\nTest installation.")
            (temp_path / "docs").mkdir()
            (temp_path / "docs" / "api.md").write_text("## API Reference\nTest API docs.")

            issues = checker.check_project_consistency(temp_path)
            assert isinstance(issues, dict)
            assert all(isinstance(issue_list, list) for issue_list in issues.values())


if __name__ == "__main__":
    pytest.main([__file__])
