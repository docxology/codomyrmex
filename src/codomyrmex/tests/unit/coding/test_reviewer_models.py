"""Unit tests for code reviewer data models -- enums, result types, metrics, and exceptions."""

import pytest

from codomyrmex.coding.review.models import (
    AnalysisResult,
    AnalysisSummary,
    AnalysisType,
    ArchitectureViolation,
    CodeMetrics,
    CodeReviewError,
    ComplexityReductionSuggestion,
    ConfigurationError,
    DeadCodeFinding,
    Language,
    PyscnError,
    QualityDashboard,
    QualityGateResult,
    SeverityLevel,
    ToolNotFoundError,
)


@pytest.mark.unit
class TestModels:
    """Tests for review data models and enums."""

    def test_severity_level_values(self):
        assert SeverityLevel.INFO.value == "info"
        assert SeverityLevel.WARNING.value == "warning"
        assert SeverityLevel.ERROR.value == "error"
        assert SeverityLevel.CRITICAL.value == "critical"

    def test_language_enum_members(self):
        assert Language.PYTHON.value == "python"
        assert Language.JAVASCRIPT.value == "javascript"
        assert Language.TYPESCRIPT.value == "typescript"
        assert Language.JAVA.value == "java"
        assert Language.CPP.value == "cpp"
        assert Language.CSHARP.value == "csharp"
        assert Language.GO.value == "go"
        assert Language.RUST.value == "rust"
        assert Language.PHP.value == "php"
        assert Language.RUBY.value == "ruby"

    def test_analysis_type_enum(self):
        assert AnalysisType.QUALITY.value == "quality"
        assert AnalysisType.SECURITY.value == "security"
        assert AnalysisType.PYSCN.value == "pyscn"

    def test_analysis_result_construction(self):
        ar = AnalysisResult(
            file_path="test.py",
            line_number=10,
            column_number=5,
            severity=SeverityLevel.WARNING,
            message="unused var",
            rule_id="W0612",
            category="quality",
        )
        assert ar.file_path == "test.py"
        assert ar.line_number == 10
        assert ar.column_number == 5
        assert ar.severity == SeverityLevel.WARNING
        assert ar.message == "unused var"
        assert ar.rule_id == "W0612"
        assert ar.category == "quality"
        assert ar.suggestion is None
        assert ar.context is None
        assert ar.fix_available is False
        assert ar.confidence == 1.0

    def test_analysis_result_with_optionals(self):
        ar = AnalysisResult(
            file_path="a.py",
            line_number=1,
            column_number=0,
            severity=SeverityLevel.ERROR,
            message="msg",
            rule_id="E001",
            category="sec",
            suggestion="fix it",
            context="ctx",
            fix_available=True,
            confidence=0.75,
        )
        assert ar.suggestion == "fix it"
        assert ar.context == "ctx"
        assert ar.fix_available is True
        assert ar.confidence == 0.75

    def test_analysis_summary_defaults(self):
        summary = AnalysisSummary(total_issues=5)
        assert summary.total_issues == 5
        assert summary.by_severity == {}
        assert summary.by_category == {}
        assert summary.by_rule == {}
        assert summary.files_analyzed == 0
        assert summary.analysis_time == 0.0
        assert summary.language is None
        assert summary.pyscn_metrics is None

    def test_code_metrics_construction(self):
        cm = CodeMetrics(
            lines_of_code=1000,
            cyclomatic_complexity=12,
            maintainability_index=85.0,
            technical_debt=4.5,
            code_duplication=3.2,
        )
        assert cm.lines_of_code == 1000
        assert cm.test_coverage is None
        assert cm.documentation_coverage is None

    def test_complexity_reduction_suggestion(self):
        crs = ComplexityReductionSuggestion(
            function_name="process",
            file_path="mod.py",
            current_complexity=20,
            suggested_refactoring="Extract method",
            estimated_effort="medium",
            benefits=["readability", "testability"],
        )
        assert crs.function_name == "process"
        assert crs.code_example is None

    def test_dead_code_finding(self):
        dcf = DeadCodeFinding(
            file_path="a.py",
            line_number=42,
            code_snippet="x = 1",
            reason="unused_variable",
            severity="warning",
            suggestion="Remove it",
        )
        assert dcf.fix_available is False
        assert dcf.estimated_savings == ""

    def test_architecture_violation(self):
        av = ArchitectureViolation(
            file_path="v.py",
            violation_type="layering_violation",
            description="Data depends on UI",
            severity="high",
            suggestion="Use DI",
        )
        assert av.affected_modules == []

    def test_quality_gate_result(self):
        qgr = QualityGateResult(
            passed=True, total_checks=3, passed_checks=3, failed_checks=0
        )
        assert qgr.passed is True
        assert qgr.failures == []

    def test_quality_gate_result_failures(self):
        failures = [{"gate": "complexity", "threshold": 15, "actual": 25}]
        qgr = QualityGateResult(
            passed=False, total_checks=1, passed_checks=0, failed_checks=1, failures=failures
        )
        assert not qgr.passed
        assert len(qgr.failures) == 1

    def test_exception_hierarchy(self):
        assert issubclass(CodeReviewError, Exception)
        assert issubclass(PyscnError, CodeReviewError)
        assert issubclass(ToolNotFoundError, CodeReviewError)
        assert issubclass(ConfigurationError, CodeReviewError)

    def test_quality_dashboard_construction(self):
        qd = QualityDashboard(
            overall_score=85.0,
            grade="B",
            analysis_timestamp="2026-02-25T12:00:00",
            total_files=10,
            total_functions=50,
            total_lines=2000,
            complexity_score=80.0,
            maintainability_score=90.0,
            testability_score=75.0,
            reliability_score=88.0,
            security_score=92.0,
            performance_score=70.0,
            complexity_metrics={"score": 80.0},
            dead_code_metrics={"score": 100.0},
            duplication_metrics={"score": 95.0},
            coupling_metrics={"score": 85.0},
            architecture_metrics={"score": 90.0},
            top_complexity_issues=[],
            top_dead_code_issues=[],
            top_duplication_issues=[],
            priority_actions=[],
            quick_wins=[],
            long_term_improvements=[],
        )
        assert qd.grade == "B"
        assert qd.trend_direction is None
        assert qd.trend_percentage is None
