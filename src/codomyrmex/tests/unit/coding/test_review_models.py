"""Zero-mock tests for coding.review.models — edge cases, equality, enum membership,
error raising, and complementary dataclass coverage."""

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
from codomyrmex.exceptions import CodomyrmexError


# ──────────────────────────── Helpers ─────────────────────────────────────


def _make_analysis_result(**kwargs) -> AnalysisResult:
    defaults = dict(
        file_path="sample.py",
        line_number=1,
        column_number=0,
        severity=SeverityLevel.INFO,
        message="test finding",
        rule_id="T001",
        category="quality",
    )
    defaults.update(kwargs)
    return AnalysisResult(**defaults)


def _make_quality_dashboard(**kwargs) -> QualityDashboard:
    defaults = dict(
        overall_score=75.0,
        grade="C",
        analysis_timestamp="2026-03-07T12:00:00",
        total_files=5,
        total_functions=20,
        total_lines=500,
        complexity_score=70.0,
        maintainability_score=80.0,
        testability_score=65.0,
        reliability_score=77.0,
        security_score=90.0,
        performance_score=60.0,
        complexity_metrics={},
        dead_code_metrics={},
        duplication_metrics={},
        coupling_metrics={},
        architecture_metrics={},
        top_complexity_issues=[],
        top_dead_code_issues=[],
        top_duplication_issues=[],
        priority_actions=[],
        quick_wins=[],
        long_term_improvements=[],
    )
    defaults.update(kwargs)
    return QualityDashboard(**defaults)


# ──────────────────────────── AnalysisType ────────────────────────────────


@pytest.mark.unit
class TestAnalysisType:
    """Tests for the AnalysisType enum."""

    def test_all_nine_members_present(self):
        members = {m.name for m in AnalysisType}
        expected = {
            "QUALITY", "SECURITY", "PERFORMANCE", "MAINTAINABILITY",
            "COMPLEXITY", "STYLE", "DOCUMENTATION", "TESTING", "PYSCN",
        }
        assert members == expected

    def test_each_value_is_lowercase_string(self):
        for member in AnalysisType:
            assert member.value == member.value.lower()
            assert isinstance(member.value, str)

    def test_lookup_by_value(self):
        assert AnalysisType("quality") is AnalysisType.QUALITY
        assert AnalysisType("security") is AnalysisType.SECURITY
        assert AnalysisType("pyscn") is AnalysisType.PYSCN

    def test_enum_identity(self):
        a = AnalysisType.COMPLEXITY
        b = AnalysisType.COMPLEXITY
        assert a is b

    def test_enum_inequality(self):
        assert AnalysisType.QUALITY != AnalysisType.SECURITY


# ──────────────────────────── SeverityLevel ───────────────────────────────


@pytest.mark.unit
class TestSeverityLevel:
    """Tests for the SeverityLevel enum."""

    def test_exactly_four_members(self):
        assert len(list(SeverityLevel)) == 4

    def test_all_members_by_name(self):
        names = {m.name for m in SeverityLevel}
        assert names == {"INFO", "WARNING", "ERROR", "CRITICAL"}

    def test_lookup_by_value(self):
        assert SeverityLevel("critical") is SeverityLevel.CRITICAL
        assert SeverityLevel("info") is SeverityLevel.INFO

    def test_usable_as_dict_key(self):
        counts: dict[SeverityLevel, int] = {
            SeverityLevel.INFO: 3,
            SeverityLevel.WARNING: 7,
        }
        assert counts[SeverityLevel.INFO] == 3
        assert SeverityLevel.CRITICAL not in counts


# ──────────────────────────── Language ────────────────────────────────────


@pytest.mark.unit
class TestLanguage:
    """Tests for the Language enum."""

    def test_exactly_ten_members(self):
        assert len(list(Language)) == 10

    def test_lookup_by_value(self):
        assert Language("python") is Language.PYTHON
        assert Language("rust") is Language.RUST

    def test_as_annotation_on_analysis_summary(self):
        summary = AnalysisSummary(total_issues=0, language=Language.TYPESCRIPT)
        assert summary.language is Language.TYPESCRIPT
        assert summary.language.value == "typescript"


# ──────────────────────────── AnalysisResult ──────────────────────────────


@pytest.mark.unit
class TestAnalysisResult:
    """Tests for AnalysisResult dataclass edge cases."""

    def test_equality_when_fields_identical(self):
        r1 = _make_analysis_result()
        r2 = _make_analysis_result()
        assert r1 == r2

    def test_inequality_when_line_differs(self):
        r1 = _make_analysis_result(line_number=10)
        r2 = _make_analysis_result(line_number=20)
        assert r1 != r2

    def test_confidence_boundary_zero(self):
        ar = _make_analysis_result(confidence=0.0)
        assert ar.confidence == 0.0

    def test_confidence_boundary_one(self):
        ar = _make_analysis_result(confidence=1.0)
        assert ar.confidence == 1.0

    def test_fix_available_true(self):
        ar = _make_analysis_result(fix_available=True)
        assert ar.fix_available is True

    def test_suggestion_set(self):
        ar = _make_analysis_result(suggestion="Remove unused import")
        assert ar.suggestion == "Remove unused import"

    def test_context_set(self):
        ar = _make_analysis_result(context="x = 1  # noqa")
        assert ar.context == "x = 1  # noqa"

    def test_critical_severity_stored(self):
        ar = _make_analysis_result(severity=SeverityLevel.CRITICAL)
        assert ar.severity == SeverityLevel.CRITICAL

    def test_security_category(self):
        ar = _make_analysis_result(category="security")
        assert ar.category == "security"


# ──────────────────────────── AnalysisSummary ─────────────────────────────


@pytest.mark.unit
class TestAnalysisSummary:
    """Tests for AnalysisSummary dataclass."""

    def test_files_errored_default_empty(self):
        summary = AnalysisSummary(total_issues=0)
        assert summary.files_errored == []

    def test_files_errored_populated(self):
        summary = AnalysisSummary(total_issues=1, files_errored=["broken.py"])
        assert "broken.py" in summary.files_errored

    def test_by_severity_with_enum_keys(self):
        summary = AnalysisSummary(
            total_issues=10,
            by_severity={SeverityLevel.ERROR: 4, SeverityLevel.WARNING: 6},
        )
        assert summary.by_severity[SeverityLevel.ERROR] == 4
        assert summary.by_severity[SeverityLevel.WARNING] == 6

    def test_analysis_time_stored(self):
        summary = AnalysisSummary(total_issues=0, analysis_time=3.14)
        assert summary.analysis_time == pytest.approx(3.14)

    def test_pyscn_metrics_set(self):
        metrics = {"complexity": 15, "duplication": 0.05}
        summary = AnalysisSummary(total_issues=0, pyscn_metrics=metrics)
        assert summary.pyscn_metrics["complexity"] == 15


# ──────────────────────────── CodeMetrics ────────────────────────────────


@pytest.mark.unit
class TestCodeMetrics:
    """Tests for CodeMetrics dataclass."""

    def test_optional_coverages_set(self):
        cm = CodeMetrics(
            lines_of_code=500,
            cyclomatic_complexity=8,
            maintainability_index=78.5,
            technical_debt=2.0,
            code_duplication=1.5,
            test_coverage=85.0,
            documentation_coverage=60.0,
        )
        assert cm.test_coverage == pytest.approx(85.0)
        assert cm.documentation_coverage == pytest.approx(60.0)

    def test_zero_values_accepted(self):
        cm = CodeMetrics(
            lines_of_code=0,
            cyclomatic_complexity=0,
            maintainability_index=0.0,
            technical_debt=0.0,
            code_duplication=0.0,
        )
        assert cm.lines_of_code == 0


# ──────────────────────────── ComplexityReductionSuggestion ───────────────


@pytest.mark.unit
class TestComplexityReductionSuggestion:
    """Tests for ComplexityReductionSuggestion dataclass."""

    def test_benefits_list_stored(self):
        crs = ComplexityReductionSuggestion(
            function_name="render",
            file_path="views.py",
            current_complexity=25,
            suggested_refactoring="Split into smaller helpers",
            estimated_effort="high",
            benefits=["readability", "testability", "maintainability"],
        )
        assert len(crs.benefits) == 3
        assert "testability" in crs.benefits

    def test_code_example_set(self):
        crs = ComplexityReductionSuggestion(
            function_name="process",
            file_path="proc.py",
            current_complexity=18,
            suggested_refactoring="Extract validate step",
            estimated_effort="low",
            benefits=["clarity"],
            code_example="def validate(x): ...",
        )
        assert crs.code_example == "def validate(x): ..."

    def test_effort_low_medium_high(self):
        for effort in ("low", "medium", "high"):
            crs = ComplexityReductionSuggestion(
                function_name="f",
                file_path="f.py",
                current_complexity=10,
                suggested_refactoring="refactor",
                estimated_effort=effort,
                benefits=[],
            )
            assert crs.estimated_effort == effort


# ──────────────────────────── DeadCodeFinding ─────────────────────────────


@pytest.mark.unit
class TestDeadCodeFinding:
    """Tests for DeadCodeFinding dataclass."""

    def test_estimated_savings_set(self):
        dcf = DeadCodeFinding(
            file_path="legacy.py",
            line_number=99,
            code_snippet="def old_helper(): pass",
            reason="never_called",
            severity="low",
            suggestion="Delete function",
            estimated_savings="3 LOC",
        )
        assert dcf.estimated_savings == "3 LOC"

    def test_fix_available_true(self):
        dcf = DeadCodeFinding(
            file_path="x.py",
            line_number=1,
            code_snippet="pass",
            reason="unreachable",
            severity="info",
            suggestion="Remove",
            fix_available=True,
        )
        assert dcf.fix_available is True


# ──────────────────────────── ArchitectureViolation ───────────────────────


@pytest.mark.unit
class TestArchitectureViolation:
    """Tests for ArchitectureViolation dataclass."""

    def test_affected_modules_populated(self):
        av = ArchitectureViolation(
            file_path="bad_import.py",
            violation_type="circular_dependency",
            description="A imports B imports A",
            severity="critical",
            suggestion="Introduce interface",
            affected_modules=["module_a", "module_b"],
        )
        assert av.affected_modules == ["module_a", "module_b"]

    def test_equality_by_fields(self):
        av1 = ArchitectureViolation("f.py", "layering", "desc", "high", "fix")
        av2 = ArchitectureViolation("f.py", "layering", "desc", "high", "fix")
        assert av1 == av2


# ──────────────────────────── QualityGateResult ───────────────────────────


@pytest.mark.unit
class TestQualityGateResult:
    """Tests for QualityGateResult dataclass."""

    def test_passed_false_with_failures(self):
        failures = [
            {"gate": "coverage", "threshold": 80, "actual": 60},
            {"gate": "complexity", "threshold": 15, "actual": 30},
        ]
        qgr = QualityGateResult(
            passed=False, total_checks=2, passed_checks=0, failed_checks=2,
            failures=failures,
        )
        assert not qgr.passed
        assert qgr.total_checks == 2
        assert qgr.failed_checks == 2
        assert len(qgr.failures) == 2

    def test_check_counts_consistent(self):
        qgr = QualityGateResult(
            passed=True, total_checks=5, passed_checks=5, failed_checks=0
        )
        assert qgr.passed_checks + qgr.failed_checks == qgr.total_checks


# ──────────────────────────── QualityDashboard ────────────────────────────


@pytest.mark.unit
class TestQualityDashboard:
    """Tests for QualityDashboard dataclass."""

    def test_trend_direction_improving(self):
        qd = _make_quality_dashboard(trend_direction="improving", trend_percentage=5.2)
        assert qd.trend_direction == "improving"
        assert qd.trend_percentage == pytest.approx(5.2)

    def test_trend_direction_declining(self):
        qd = _make_quality_dashboard(trend_direction="declining", trend_percentage=-3.1)
        assert qd.trend_direction == "declining"
        assert qd.trend_percentage == pytest.approx(-3.1)

    def test_top_issues_populated(self):
        issues = [{"function": "parse", "complexity": 22}]
        qd = _make_quality_dashboard(top_complexity_issues=issues)
        assert len(qd.top_complexity_issues) == 1
        assert qd.top_complexity_issues[0]["complexity"] == 22

    def test_grades_stored(self):
        for grade in ("A", "B", "C", "D", "F"):
            qd = _make_quality_dashboard(grade=grade)
            assert qd.grade == grade


# ──────────────────────────── Exceptions ──────────────────────────────────


@pytest.mark.unit
class TestCodeReviewExceptions:
    """Tests for the exception hierarchy."""

    def test_code_review_error_is_codomyrmex_error(self):
        assert issubclass(CodeReviewError, CodomyrmexError)

    def test_pyscn_error_is_code_review_error(self):
        assert issubclass(PyscnError, CodeReviewError)

    def test_tool_not_found_error_is_code_review_error(self):
        assert issubclass(ToolNotFoundError, CodeReviewError)

    def test_configuration_error_is_code_review_error(self):
        assert issubclass(ConfigurationError, CodeReviewError)

    def test_code_review_error_raise_with_message(self):
        with pytest.raises(CodeReviewError, match="something went wrong"):
            raise CodeReviewError("something went wrong")

    def test_pyscn_error_raise_with_message(self):
        with pytest.raises(PyscnError, match="pyscn failed"):
            raise PyscnError("pyscn failed")

    def test_tool_not_found_raise_with_message(self):
        with pytest.raises(ToolNotFoundError, match="pylint not found"):
            raise ToolNotFoundError("pylint not found")

    def test_configuration_error_raise_with_message(self):
        with pytest.raises(ConfigurationError, match="invalid config"):
            raise ConfigurationError("invalid config")

    def test_exception_caught_by_parent_type(self):
        with pytest.raises(CodeReviewError):
            raise PyscnError("nested")

    def test_exception_caught_by_codomyrmex_base(self):
        with pytest.raises(CodomyrmexError):
            raise ConfigurationError("base catch")
