"""Unit tests for documentation linting: consistency checking and quality assessment.

Tests cover: DocumentationConsistencyChecker, ConsistencyIssue, ConsistencyReport,
check_documentation_consistency, DocumentationQualityAnalyzer, and generate_quality_report.

Zero-mock policy: All tests use real filesystem via tmp_path fixtures.
"""

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# ConsistencyIssue / ConsistencyReport dataclasses
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConsistencyDataclasses:
    """Test ConsistencyIssue and ConsistencyReport dataclass instantiation."""

    def test_consistency_issue_fields(self):
        from codomyrmex.documentation.quality.consistency_checker import (
            ConsistencyIssue,
        )

        issue = ConsistencyIssue(
            file_path="/path/to/file.md",
            line_number=42,
            issue_type="trailing_whitespace",
            description="Line has trailing whitespace",
        )
        assert issue.file_path == "/path/to/file.md"
        assert issue.line_number == 42
        assert issue.issue_type == "trailing_whitespace"
        assert issue.severity == "warning"  # default

    def test_consistency_issue_custom_severity(self):
        from codomyrmex.documentation.quality.consistency_checker import (
            ConsistencyIssue,
        )

        issue = ConsistencyIssue(
            file_path="x.md",
            line_number=1,
            issue_type="tabs",
            description="Tab found",
            severity="error",
        )
        assert issue.severity == "error"

    def test_consistency_issue_suggestion(self):
        from codomyrmex.documentation.quality.consistency_checker import (
            ConsistencyIssue,
        )

        issue = ConsistencyIssue(
            file_path="x.md",
            line_number=1,
            issue_type="tabs",
            description="Tab found",
            suggestion="Replace with 4 spaces",
        )
        assert issue.suggestion == "Replace with 4 spaces"

    def test_consistency_report_defaults(self):
        from codomyrmex.documentation.quality.consistency_checker import (
            ConsistencyReport,
        )

        report = ConsistencyReport(total_files=5, files_checked=3)
        assert report.total_files == 5
        assert report.files_checked == 3
        assert report.issues == []
        assert report.passed is True

    def test_consistency_report_with_issues(self):
        from codomyrmex.documentation.quality.consistency_checker import (
            ConsistencyIssue,
            ConsistencyReport,
        )

        issue = ConsistencyIssue(
            file_path="a.md", line_number=1, issue_type="tabs", description="Tab"
        )
        report = ConsistencyReport(
            total_files=1, files_checked=1, issues=[issue], passed=False
        )
        assert len(report.issues) == 1
        assert report.passed is False


# ---------------------------------------------------------------------------
# DocumentationConsistencyChecker
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDocumentationConsistencyChecker:
    """Test the consistency checker for documentation files."""

    def test_init_loads_naming_patterns(self):
        from codomyrmex.documentation.quality.consistency_checker import (
            DocumentationConsistencyChecker,
        )

        checker = DocumentationConsistencyChecker()
        assert "snake_case" in checker.naming_patterns
        assert "UPPER_SNAKE" in checker.naming_patterns
        assert "PascalCase" in checker.naming_patterns

    def test_check_file_detects_trailing_whitespace(self, tmp_path: Path):
        from codomyrmex.documentation.quality.consistency_checker import (
            DocumentationConsistencyChecker,
        )

        f = tmp_path / "whitespace.md"
        f.write_text("# Title\nLine with trailing space   \nClean line\n")

        checker = DocumentationConsistencyChecker()
        issues = checker.check_file(str(f))
        trailing = [i for i in issues if i.issue_type == "trailing_whitespace"]
        assert len(trailing) >= 1

    def test_check_file_detects_tabs(self, tmp_path: Path):
        from codomyrmex.documentation.quality.consistency_checker import (
            DocumentationConsistencyChecker,
        )

        f = tmp_path / "tabs.md"
        f.write_text("# Title\n\tIndented with tab\n")

        checker = DocumentationConsistencyChecker()
        issues = checker.check_file(str(f))
        tab_issues = [i for i in issues if i.issue_type == "tabs"]
        assert len(tab_issues) >= 1

    def test_check_file_clean_document(self, tmp_path: Path):
        from codomyrmex.documentation.quality.consistency_checker import (
            DocumentationConsistencyChecker,
        )

        f = tmp_path / "clean.md"
        f.write_text("# Title\n\nClean document with no issues.\n")

        checker = DocumentationConsistencyChecker()
        issues = checker.check_file(str(f))
        assert len(issues) == 0

    def test_check_file_nonexistent_no_crash(self, tmp_path: Path):
        from codomyrmex.documentation.quality.consistency_checker import (
            DocumentationConsistencyChecker,
        )

        checker = DocumentationConsistencyChecker()
        issues = checker.check_file(str(tmp_path / "nonexistent.md"))
        # Should not crash; returns empty or logs error
        assert isinstance(issues, list)

    def test_check_directory_returns_report(self, tmp_path: Path):
        from codomyrmex.documentation.quality.consistency_checker import (
            DocumentationConsistencyChecker,
        )

        (tmp_path / "a.md").write_text("# A\n")
        (tmp_path / "b.md").write_text("# B\n")

        checker = DocumentationConsistencyChecker()
        report = checker.check_directory(str(tmp_path))
        assert report.total_files == 2
        assert report.files_checked == 2

    def test_check_directory_recursive(self, tmp_path: Path):
        from codomyrmex.documentation.quality.consistency_checker import (
            DocumentationConsistencyChecker,
        )

        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "root.md").write_text("# Root\n")
        (sub / "nested.md").write_text("# Nested\n")

        checker = DocumentationConsistencyChecker()
        report = checker.check_directory(str(tmp_path), recursive=True)
        assert report.total_files == 2

    def test_check_directory_non_recursive(self, tmp_path: Path):
        from codomyrmex.documentation.quality.consistency_checker import (
            DocumentationConsistencyChecker,
        )

        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "root.md").write_text("# Root\n")
        (sub / "nested.md").write_text("# Nested\n")

        checker = DocumentationConsistencyChecker()
        report = checker.check_directory(str(tmp_path), recursive=False)
        assert report.total_files == 1

    def test_check_directory_passed_is_true_when_clean(self, tmp_path: Path):
        from codomyrmex.documentation.quality.consistency_checker import (
            DocumentationConsistencyChecker,
        )

        (tmp_path / "clean.md").write_text("# Clean\n\nNo issues here.\n")

        checker = DocumentationConsistencyChecker()
        report = checker.check_directory(str(tmp_path))
        assert report.passed is True

    def test_check_directory_passed_is_false_with_issues(self, tmp_path: Path):
        from codomyrmex.documentation.quality.consistency_checker import (
            DocumentationConsistencyChecker,
        )

        (tmp_path / "dirty.md").write_text("# Dirty\nTrailing spaces   \n")

        checker = DocumentationConsistencyChecker()
        report = checker.check_directory(str(tmp_path))
        assert report.passed is False


# ---------------------------------------------------------------------------
# check_documentation_consistency convenience function
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCheckDocumentationConsistency:
    """Test the convenience function for consistency checking."""

    def test_single_file_path(self, tmp_path: Path):
        from codomyrmex.documentation.quality.consistency_checker import (
            check_documentation_consistency,
        )

        f = tmp_path / "single.md"
        f.write_text("# Single\n\nClean content.\n")
        report = check_documentation_consistency(str(f))
        assert report.total_files == 1
        assert report.files_checked == 1

    def test_directory_path(self, tmp_path: Path):
        from codomyrmex.documentation.quality.consistency_checker import (
            check_documentation_consistency,
        )

        (tmp_path / "a.md").write_text("# A\n")
        report = check_documentation_consistency(str(tmp_path))
        assert report.total_files >= 1


# ---------------------------------------------------------------------------
# DocumentationQualityAnalyzer
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDocumentationQualityAnalyzer:
    """Test the quality assessment analyzer."""

    def test_analyze_file_returns_metrics(self, tmp_path: Path):
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )

        f = tmp_path / "doc.md"
        f.write_text(
            "# Title\n\n## Overview\n\nThis module provides API access.\n\n"
            "## Usage\n\n```python\nimport module\n```\n\n## Examples\n\nSee below.\n"
        )

        analyzer = DocumentationQualityAnalyzer()
        result = analyzer.analyze_file(f)
        assert "completeness" in result
        assert "consistency" in result
        assert "readability" in result
        assert "structure" in result
        assert "overall_score" in result

    def test_analyze_missing_file_returns_error(self, tmp_path: Path):
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )

        analyzer = DocumentationQualityAnalyzer()
        result = analyzer.analyze_file(tmp_path / "nonexistent.md")
        assert "error" in result

    def test_completeness_increases_with_sections(self, tmp_path: Path):
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )

        analyzer = DocumentationQualityAnalyzer()

        minimal = tmp_path / "minimal.md"
        minimal.write_text("# Title\n\nSome text.\n")

        rich = tmp_path / "rich.md"
        rich.write_text(
            "# Title\n\n## Overview\n\nText.\n\n## Installation\n\nStep 1.\n\n"
            "## Usage\n\nCode here.\n\n## API\n\nEndpoints.\n\n## Examples\n\n```python\nfoo()\n```\n"
        )

        minimal_score = analyzer.analyze_file(minimal)["completeness"]
        rich_score = analyzer.analyze_file(rich)["completeness"]
        assert rich_score > minimal_score

    def test_consistency_penalizes_unmatched_code_blocks(self, tmp_path: Path):
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )

        f = tmp_path / "odd_blocks.md"
        # 3 backtick markers = odd = unclosed code block
        f.write_text("# Title\n\n```python\ncode\n```\n\nMore text\n\n```\n")

        analyzer = DocumentationQualityAnalyzer()
        result = analyzer.analyze_file(f)
        assert result["consistency"] < 100.0

    def test_readability_penalizes_long_paragraphs(self, tmp_path: Path):
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )

        # Create 3+ paragraphs each over 500 chars
        long_para = "A" * 600
        content = f"# Title\n\n{long_para}\n\n{long_para}\n\n{long_para}\n"

        f = tmp_path / "verbose.md"
        f.write_text(content)

        analyzer = DocumentationQualityAnalyzer()
        result = analyzer.analyze_file(f)
        assert result["readability"] < 100.0

    def test_structure_rewards_headings(self, tmp_path: Path):
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )

        f = tmp_path / "structured.md"
        f.write_text(
            "# Main\n\n## Section A\n\nText.\n\n## Section B\n\nText.\n\n"
            "## Section C\n\nText.\n"
        )

        analyzer = DocumentationQualityAnalyzer()
        result = analyzer.analyze_file(f)
        assert result["structure"] > 0.0

    def test_overall_score_is_average(self, tmp_path: Path):
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )

        f = tmp_path / "average.md"
        f.write_text("# Title\n\n## Overview\n\nContent.\n")

        analyzer = DocumentationQualityAnalyzer()
        result = analyzer.analyze_file(f)
        expected_avg = (
            result["completeness"]
            + result["consistency"]
            + result["technical_accuracy"]
            + result["readability"]
            + result["structure"]
        ) / 5
        assert abs(result["overall_score"] - expected_avg) < 0.01

    def test_initial_quality_metrics_zeroed(self):
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )

        analyzer = DocumentationQualityAnalyzer()
        for _metric, value in analyzer.quality_metrics.items():
            assert value == 0


# ---------------------------------------------------------------------------
# generate_quality_report
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGenerateQualityReport:
    """Test the generate_quality_report function."""

    def test_returns_string(self, tmp_path: Path):
        from codomyrmex.documentation.quality.quality_assessment import (
            generate_quality_report,
        )

        (tmp_path / "README.md").write_text("# Project\n\nDescription.\n")
        report = generate_quality_report(tmp_path)
        assert isinstance(report, str)

    def test_report_contains_header(self, tmp_path: Path):
        from codomyrmex.documentation.quality.quality_assessment import (
            generate_quality_report,
        )

        (tmp_path / "README.md").write_text("# Project\n")
        report = generate_quality_report(tmp_path)
        assert "# Documentation Quality Report" in report

    def test_report_contains_file_scores(self, tmp_path: Path):
        from codomyrmex.documentation.quality.quality_assessment import (
            generate_quality_report,
        )

        (tmp_path / "README.md").write_text(
            "# Project\n\n## Overview\n\nGreat project.\n"
        )
        report = generate_quality_report(tmp_path)
        assert "README.md" in report
        assert "/100" in report

    def test_report_handles_no_files(self, tmp_path: Path):
        from codomyrmex.documentation.quality.quality_assessment import (
            generate_quality_report,
        )

        # No README.md, src/README.md, or AGENTS.md
        report = generate_quality_report(tmp_path)
        assert isinstance(report, str)
        assert "Quality Report" in report

    def test_report_average_score_section(self, tmp_path: Path):
        from codomyrmex.documentation.quality.quality_assessment import (
            generate_quality_report,
        )

        (tmp_path / "README.md").write_text(
            "# Project\n\n## Overview\n\nA comprehensive project with API.\n\n"
            "## Installation\n\npip install project\n\n## Usage\n\nSee examples.\n"
        )
        report = generate_quality_report(tmp_path)
        assert "Overall Average Score" in report
