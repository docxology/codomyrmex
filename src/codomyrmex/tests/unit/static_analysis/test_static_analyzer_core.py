"""Tests for StaticAnalyzer core data structures and initialization.

Tests enums, dataclasses, and StaticAnalyzer init/tool discovery.
No mocks. Import-safe: handles pyrefly_runner ImportError gracefully.
"""

import pytest

try:
    from codomyrmex.coding.static_analysis.static_analyzer import (
        AnalysisResult,
        AnalysisSummary,
        AnalysisType,
        CodeMetrics,
        Language,
        SeverityLevel,
        StaticAnalyzer,
    )
    STATIC_ANALYZER_AVAILABLE = True
except ImportError as e:
    STATIC_ANALYZER_AVAILABLE = False
    IMPORT_ERROR = str(e)

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(
        not STATIC_ANALYZER_AVAILABLE,
        reason=f"Static analyzer import failed: {IMPORT_ERROR if not STATIC_ANALYZER_AVAILABLE else ''}",
    ),
]


class TestAnalysisTypeEnum:
    """Tests for AnalysisType enum."""

    def test_quality_value(self):
        """Test functionality: quality value."""
        assert AnalysisType.QUALITY.value == "quality"

    def test_security_value(self):
        """Test functionality: security value."""
        assert AnalysisType.SECURITY.value == "security"

    def test_performance_value(self):
        """Test functionality: performance value."""
        assert AnalysisType.PERFORMANCE.value == "performance"

    def test_maintainability_value(self):
        """Test functionality: maintainability value."""
        assert AnalysisType.MAINTAINABILITY.value == "maintainability"

    def test_complexity_value(self):
        """Test functionality: complexity value."""
        assert AnalysisType.COMPLEXITY.value == "complexity"

    def test_style_value(self):
        """Test functionality: style value."""
        assert AnalysisType.STYLE.value == "style"

    def test_documentation_value(self):
        """Test functionality: documentation value."""
        assert AnalysisType.DOCUMENTATION.value == "documentation"

    def test_testing_value(self):
        """Test functionality: testing value."""
        assert AnalysisType.TESTING.value == "testing"

    def test_member_count(self):
        """Test functionality: member count."""
        assert len(list(AnalysisType)) == 8


class TestSeverityLevelEnum:
    """Tests for SeverityLevel enum."""

    def test_info_value(self):
        """Test functionality: info value."""
        assert SeverityLevel.INFO.value == "info"

    def test_warning_value(self):
        """Test functionality: warning value."""
        assert SeverityLevel.WARNING.value == "warning"

    def test_error_value(self):
        """Test functionality: error value."""
        assert SeverityLevel.ERROR.value == "error"

    def test_critical_value(self):
        """Test functionality: critical value."""
        assert SeverityLevel.CRITICAL.value == "critical"

    def test_member_count(self):
        """Test functionality: member count."""
        assert len(list(SeverityLevel)) == 4


class TestAnalysisResult:
    """Tests for AnalysisResult dataclass."""

    def test_creation_with_required_fields(self):
        """Test functionality: creation with required fields."""
        result = AnalysisResult(
            file_path="test.py",
            line_number=10,
            column_number=5,
            severity=SeverityLevel.WARNING,
            message="Unused variable",
            rule_id="W0611",
            category="style",
        )
        assert result.file_path == "test.py"
        assert result.line_number == 10
        assert result.column_number == 5
        assert result.severity == SeverityLevel.WARNING
        assert result.message == "Unused variable"
        assert result.rule_id == "W0611"
        assert result.category == "style"

    def test_optional_fields_have_defaults(self):
        """Test functionality: optional fields have defaults."""
        result = AnalysisResult(
            file_path="f.py",
            line_number=1,
            column_number=1,
            severity=SeverityLevel.INFO,
            message="msg",
            rule_id="R1",
            category="cat",
        )
        assert result.fix_available is False
        assert result.confidence == 1.0

    def test_creation_with_all_fields(self):
        """Test functionality: creation with all fields."""
        result = AnalysisResult(
            file_path="main.py",
            line_number=1,
            column_number=1,
            severity=SeverityLevel.ERROR,
            message="Undefined name",
            rule_id="E0102",
            category="error",
            suggestion="Import the module",
            fix_available=True,
            confidence=0.95,
        )
        assert result.suggestion == "Import the module"
        assert result.fix_available is True
        assert result.confidence == 0.95


class TestAnalysisSummary:
    """Tests for AnalysisSummary dataclass."""

    def test_creation_with_total_issues(self):
        """Test functionality: creation with total issues."""
        summary = AnalysisSummary(total_issues=5)
        assert summary.total_issues == 5

    def test_default_files_analyzed_is_zero(self):
        """Test functionality: default files analyzed is zero."""
        summary = AnalysisSummary(total_issues=0)
        assert summary.files_analyzed == 0

    def test_default_by_severity_is_empty(self):
        """Test functionality: default by severity is empty."""
        summary = AnalysisSummary(total_issues=0)
        assert summary.by_severity == {}


class TestCodeMetrics:
    """Tests for CodeMetrics dataclass."""

    def test_creation_with_required_fields(self):
        """Test functionality: creation with required fields."""
        m = CodeMetrics(
            lines_of_code=100,
            cyclomatic_complexity=5,
            maintainability_index=75.0,
            technical_debt=2.5,
            code_duplication=0.1,
        )
        assert m.lines_of_code == 100
        assert m.cyclomatic_complexity == 5
        assert m.maintainability_index == 75.0

    def test_optional_test_coverage_defaults_none(self):
        """Test functionality: optional coverage defaults none."""
        m = CodeMetrics(
            lines_of_code=50,
            cyclomatic_complexity=1,
            maintainability_index=80.0,
            technical_debt=0.5,
            code_duplication=0.0,
        )
        assert m.test_coverage is None


class TestStaticAnalyzerInit:
    """Tests for StaticAnalyzer initialization."""

    def test_init_default_project_root(self):
        """Test functionality: init default project root."""
        analyzer = StaticAnalyzer()
        assert analyzer.project_root is not None

    def test_init_custom_project_root(self, tmp_path):
        """Test functionality: init custom project root."""
        analyzer = StaticAnalyzer(project_root=str(tmp_path))
        assert analyzer.project_root == str(tmp_path)

    def test_tools_available_is_dict(self):
        """Test functionality: tools available is dict."""
        analyzer = StaticAnalyzer()
        assert isinstance(analyzer.tools_available, dict)
        for tool_name, available in analyzer.tools_available.items():
            assert isinstance(tool_name, str)
            assert isinstance(available, bool)

    def test_results_starts_empty(self):
        """Test functionality: results starts empty."""
        analyzer = StaticAnalyzer()
        assert analyzer.results == []

    def test_analyze_file_on_real_python_file(self, tmp_path):
        """Test functionality: analyze file on real python file."""
        code_file = tmp_path / "sample.py"
        code_file.write_text("x = 1\n")
        analyzer = StaticAnalyzer(project_root=str(tmp_path))
        results = analyzer.analyze_file(str(code_file))
        assert isinstance(results, list)

    def test_analyze_file_nonexistent_returns_empty_or_error(self):
        """Test functionality: analyze file nonexistent returns empty or error."""
        analyzer = StaticAnalyzer()
        results = analyzer.analyze_file("/nonexistent/path/file.py")
        assert isinstance(results, list)
