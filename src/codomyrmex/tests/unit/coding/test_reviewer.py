"""Comprehensive unit tests for codomyrmex.coding.review.reviewer.CodeReviewer.

Tests cover: constructor, language detection, file filtering, quality gates,
report generation, complexity suggestions, dead code analysis, architecture
compliance, refactoring plan generation, performance optimization, quality
dashboard, code smell detection, automated fix suggestions, technical debt
analysis, and comprehensive report generation.

Zero-mock policy: All tests use real objects and tmp_path for filesystem ops.
PyscnAnalyzer requires the `pyscn` CLI tool; tests that need full CodeReviewer
initialization are guarded with skipif.
"""

import json
import os
import subprocess

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

# ---------- pyscn availability check ----------

_PYSCN_AVAILABLE = False
try:
    result = subprocess.run(
        ["pyscn", "--version"], capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0:
        _PYSCN_AVAILABLE = True
except (FileNotFoundError, subprocess.TimeoutExpired):
    pass

requires_pyscn = pytest.mark.skipif(
    not _PYSCN_AVAILABLE, reason="pyscn CLI tool not installed"
)


def _make_reviewer(project_root, config=None):
    """Build a CodeReviewer without calling __init__ (avoids pyscn check).

    This is NOT mocking -- we construct a real CodeReviewer and set its
    attributes to real values.  The only thing we skip is
    PyscnAnalyzer._check_pyscn_availability which shells out to `pyscn`.
    """
    from codomyrmex.coding.review.reviewer import CodeReviewer

    reviewer = object.__new__(CodeReviewer)
    reviewer.project_root = str(project_root)
    reviewer.config_path = None
    reviewer.results = []
    reviewer.metrics = {}
    reviewer.config = config or {
        "analysis_types": ["quality", "security", "style"],
        "max_complexity": 15,
        "min_clone_similarity": 0.8,
        "output_format": "html",
        "output_directory": "reports",
        "parallel_processing": True,
        "max_workers": 4,
        "quality_gates": {
            "max_complexity": 15,
            "max_clone_similarity": 0.8,
            "max_issues_per_file": 50,
        },
        "pyscn": {"enabled": True, "auto_lsh": True, "lsh_threshold": 500},
    }
    reviewer.tools_available = {
        "pylint": False,
        "flake8": False,
        "mypy": False,
        "bandit": False,
        "black": False,
        "isort": False,
        "pytest": False,
        "coverage": False,
        "radon": False,
        "vulture": False,
        "safety": False,
        "semgrep": False,
        "pyscn": False,
    }

    # Create a PyscnAnalyzer the same way -- skip its __init__ check
    from codomyrmex.coding.review.analyzer import PyscnAnalyzer

    analyzer = object.__new__(PyscnAnalyzer)
    analyzer.config = {}
    reviewer.pyscn_analyzer = analyzer

    return reviewer


# ============================================================================
# 1.  Model / Enum Tests
# ============================================================================


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


# ============================================================================
# 2.  CodeReviewer Pure Method Tests (no pyscn required)
# ============================================================================


@pytest.mark.unit
class TestCodeReviewerLanguageDetection:
    """Test _detect_language on the CodeReviewer."""

    def test_python(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_language("app.py") == Language.PYTHON

    def test_javascript(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_language("app.js") == Language.JAVASCRIPT
        assert r._detect_language("app.jsx") == Language.JAVASCRIPT

    def test_typescript(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_language("app.ts") == Language.TYPESCRIPT
        assert r._detect_language("app.tsx") == Language.TYPESCRIPT

    def test_java(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_language("App.java") == Language.JAVA

    def test_cpp(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_language("main.cpp") == Language.CPP
        assert r._detect_language("main.cc") == Language.CPP
        assert r._detect_language("main.cxx") == Language.CPP

    def test_csharp(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_language("Program.cs") == Language.CSHARP

    def test_go(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_language("main.go") == Language.GO

    def test_rust(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_language("lib.rs") == Language.RUST

    def test_php(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_language("index.php") == Language.PHP

    def test_ruby(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_language("app.rb") == Language.RUBY

    def test_unknown_defaults_to_python(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_language("readme.txt") == Language.PYTHON
        assert r._detect_language("Makefile") == Language.PYTHON


@pytest.mark.unit
class TestShouldAnalyzeFile:
    """Test _should_analyze_file filtering."""

    def test_python_included(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._should_analyze_file("module.py") is True

    def test_js_included(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._should_analyze_file("app.js") is True

    def test_ts_included(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._should_analyze_file("app.ts") is True

    def test_java_included(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._should_analyze_file("Main.java") is True

    def test_markdown_excluded(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._should_analyze_file("README.md") is False

    def test_text_excluded(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._should_analyze_file("notes.txt") is False

    def test_yaml_excluded(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._should_analyze_file("config.yml") is False

    def test_dockerfile_excluded(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._should_analyze_file("Dockerfile") is False


@pytest.mark.unit
class TestCalculateGrade:
    """Test _calculate_grade letter-grade boundaries."""

    def test_grade_a(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._calculate_grade(90.0) == "A"
        assert r._calculate_grade(100.0) == "A"
        assert r._calculate_grade(95.5) == "A"

    def test_grade_b(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._calculate_grade(80.0) == "B"
        assert r._calculate_grade(89.9) == "B"

    def test_grade_c(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._calculate_grade(70.0) == "C"
        assert r._calculate_grade(79.9) == "C"

    def test_grade_d(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._calculate_grade(60.0) == "D"
        assert r._calculate_grade(69.9) == "D"

    def test_grade_f(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._calculate_grade(59.9) == "F"
        assert r._calculate_grade(0.0) == "F"


@pytest.mark.unit
class TestGetScoreColor:
    """Test _get_score_color returns correct CSS colors."""

    def test_green_above_90(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._get_score_color(95.0) == "#28a745"

    def test_yellow_80_to_90(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._get_score_color(85.0) == "#ffc107"

    def test_orange_70_to_80(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._get_score_color(75.0) == "#fd7e14"

    def test_red_below_70(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._get_score_color(65.0) == "#dc3545"
        assert r._get_score_color(0.0) == "#dc3545"


@pytest.mark.unit
class TestCalculateOverallScore:
    """Test _calculate_overall_score weighted computation."""

    def test_perfect_scores(self, tmp_path):
        r = _make_reviewer(tmp_path)
        score = r._calculate_overall_score(
            {"score": 100.0},
            {"score": 100.0},
            {"score": 100.0},
            {"score": 100.0},
            {"score": 100.0},
        )
        assert score == 100.0

    def test_zero_scores(self, tmp_path):
        r = _make_reviewer(tmp_path)
        score = r._calculate_overall_score(
            {"score": 0.0},
            {"score": 0.0},
            {"score": 0.0},
            {"score": 0.0},
            {"score": 0.0},
        )
        assert score == 0.0

    def test_weighted_average(self, tmp_path):
        r = _make_reviewer(tmp_path)
        # complexity=0.25, dead_code=0.20, duplication=0.15, coupling=0.20, architecture=0.20
        score = r._calculate_overall_score(
            {"score": 80.0},   # complexity  -> 80 * 0.25 = 20
            {"score": 60.0},   # dead_code   -> 60 * 0.20 = 12
            {"score": 100.0},  # duplication  -> 100 * 0.15 = 15
            {"score": 50.0},   # coupling    -> 50 * 0.20 = 10
            {"score": 70.0},   # architecture -> 70 * 0.20 = 14
        )
        # Total = 20 + 12 + 15 + 10 + 14 = 71.0
        assert abs(score - 71.0) < 0.01

    def test_clamps_to_100(self, tmp_path):
        r = _make_reviewer(tmp_path)
        # Even if all are 100, should not exceed 100
        score = r._calculate_overall_score(
            {"score": 100.0},
            {"score": 100.0},
            {"score": 100.0},
            {"score": 100.0},
            {"score": 100.0},
        )
        assert score <= 100.0

    def test_clamps_to_zero(self, tmp_path):
        r = _make_reviewer(tmp_path)
        score = r._calculate_overall_score(
            {"score": -10.0},
            {"score": -10.0},
            {"score": -10.0},
            {"score": -10.0},
            {"score": -10.0},
        )
        assert score >= 0.0


@pytest.mark.unit
class TestSuggestProperName:
    """Test _suggest_proper_name for file renaming."""

    def test_adds_test_prefix(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._suggest_proper_name("mytest_file.py") == "test_mytest_file.py"

    def test_already_correct_prefix(self, tmp_path):
        r = _make_reviewer(tmp_path)
        # If it already has test_ prefix, the code still prepends test_ if
        # 'test' is in the name but doesn't start with test_ -- but test_file.py
        # starts with test_ so the first branch condition is False
        result = r._suggest_proper_name("test_file.py")
        # 'test' in 'test_file.py'.lower() == True, but starts with test_ == True
        # so the outer if is False -> falls through to return current_name
        assert result == "test_file.py"

    def test_non_test_file_unchanged(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._suggest_proper_name("module.py") == "module.py"


@pytest.mark.unit
class TestGetDeadCodeSuggestion:
    """Test _get_dead_code_suggestion returns proper text."""

    def test_known_reasons(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert "return statement" in r._get_dead_code_suggestion("unreachable_after_return", "critical")
        assert "exception" in r._get_dead_code_suggestion("unreachable_after_raise", "warning")
        assert "break" in r._get_dead_code_suggestion("unreachable_after_break", "warning")
        assert "continue" in r._get_dead_code_suggestion("unreachable_after_continue", "warning")
        assert "unused" in r._get_dead_code_suggestion("unused_variable", "info").lower()
        assert "unused" in r._get_dead_code_suggestion("unused_function", "info").lower()
        assert "unused" in r._get_dead_code_suggestion("unused_import", "info").lower()
        assert "unused" in r._get_dead_code_suggestion("unused_class", "info").lower()

    def test_unknown_reason_fallback(self, tmp_path):
        r = _make_reviewer(tmp_path)
        result = r._get_dead_code_suggestion("some_new_reason", "warning")
        assert "some_new_reason" in result


@pytest.mark.unit
class TestCanAutoFixDeadCode:
    """Test _can_auto_fix_dead_code returns correct booleans."""

    def test_fixable_reasons(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._can_auto_fix_dead_code("unreachable_after_return") is True
        assert r._can_auto_fix_dead_code("unreachable_after_raise") is True
        assert r._can_auto_fix_dead_code("unreachable_after_break") is True
        assert r._can_auto_fix_dead_code("unreachable_after_continue") is True

    def test_non_fixable_reasons(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._can_auto_fix_dead_code("unused_variable") is False
        assert r._can_auto_fix_dead_code("unused_function") is False
        assert r._can_auto_fix_dead_code("unknown") is False


@pytest.mark.unit
class TestEstimateDeadCodeSavings:
    """Test _estimate_dead_code_savings strings."""

    def test_unreachable(self, tmp_path):
        r = _make_reviewer(tmp_path)
        result = r._estimate_dead_code_savings("unreachable_after_return")
        assert "file size" in result.lower() or "readability" in result.lower()

    def test_unused(self, tmp_path):
        r = _make_reviewer(tmp_path)
        result = r._estimate_dead_code_savings("unused_variable")
        assert "memory" in result.lower() or "namespace" in result.lower()

    def test_other(self, tmp_path):
        r = _make_reviewer(tmp_path)
        result = r._estimate_dead_code_savings("other_reason")
        assert "clarity" in result.lower() or "maintainability" in result.lower()


# ============================================================================
# 3.  Complexity Suggestion Generation
# ============================================================================


@pytest.mark.unit
class TestGenerateComplexitySuggestion:
    """Test _generate_complexity_suggestion for various complexity levels."""

    def test_very_high_complexity_extract_method(self, tmp_path):
        r = _make_reviewer(tmp_path)
        suggestion = r._generate_complexity_suggestion({
            "name": "big_func",
            "complexity": 30,
            "file_path": "module.py",
        })
        assert suggestion is not None
        assert suggestion.function_name == "big_func"
        assert suggestion.current_complexity == 30
        assert "extract" in suggestion.suggested_refactoring.lower()
        assert suggestion.estimated_effort == "medium"
        assert len(suggestion.benefits) > 0
        assert suggestion.code_example is not None

    def test_high_complexity_guard_clause(self, tmp_path):
        r = _make_reviewer(tmp_path)
        suggestion = r._generate_complexity_suggestion({
            "name": "medium_func",
            "complexity": 18,
            "file_path": "mod.py",
        })
        assert suggestion is not None
        assert "guard" in suggestion.suggested_refactoring.lower()
        assert suggestion.estimated_effort == "low"

    def test_moderate_complexity_returns_none(self, tmp_path):
        r = _make_reviewer(tmp_path)
        suggestion = r._generate_complexity_suggestion({
            "name": "ok_func",
            "complexity": 10,
            "file_path": "mod.py",
        })
        assert suggestion is None

    def test_boundary_complexity_15(self, tmp_path):
        r = _make_reviewer(tmp_path)
        # Exactly 15 should return guard clause suggestion
        suggestion = r._generate_complexity_suggestion({
            "name": "boundary_func",
            "complexity": 15,
            "file_path": "mod.py",
        })
        assert suggestion is not None
        assert "guard" in suggestion.suggested_refactoring.lower()

    def test_boundary_complexity_25(self, tmp_path):
        r = _make_reviewer(tmp_path)
        # Exactly 25 should return extract method suggestion
        suggestion = r._generate_complexity_suggestion({
            "name": "boundary_func",
            "complexity": 25,
            "file_path": "mod.py",
        })
        assert suggestion is not None
        assert "extract" in suggestion.suggested_refactoring.lower()


# ============================================================================
# 4.  Dead Code Finding Enhancement
# ============================================================================


@pytest.mark.unit
class TestEnhanceDeadCodeFinding:
    """Test _enhance_dead_code_finding builds proper DeadCodeFinding objects."""

    def test_basic_finding(self, tmp_path):
        r = _make_reviewer(tmp_path)
        finding = r._enhance_dead_code_finding({
            "location": {"file_path": "a.py", "start_line": 10, "start_column": 0},
            "reason": "unused_variable",
            "severity": "warning",
            "code": "x = 1",
            "description": "unused",
        })
        assert finding is not None
        assert isinstance(finding, DeadCodeFinding)
        assert finding.file_path == "a.py"
        assert finding.line_number == 10
        assert finding.code_snippet == "x = 1"
        assert finding.reason == "unused_variable"
        assert finding.severity == "warning"
        assert finding.fix_available is False  # unused_variable not auto-fixable
        assert len(finding.suggestion) > 0

    def test_unreachable_finding_is_fixable(self, tmp_path):
        r = _make_reviewer(tmp_path)
        finding = r._enhance_dead_code_finding({
            "location": {"file_path": "b.py", "start_line": 5},
            "reason": "unreachable_after_return",
            "severity": "critical",
            "code": "print('never')",
        })
        assert finding.fix_available is True

    def test_empty_location_defaults(self, tmp_path):
        r = _make_reviewer(tmp_path)
        finding = r._enhance_dead_code_finding({
            "reason": "unknown",
            "severity": "info",
        })
        assert finding.file_path == ""
        assert finding.line_number == 0
        # finding.get("code", "") returns "" when key is absent
        assert finding.code_snippet == ""


# ============================================================================
# 5.  Quality Gates
# ============================================================================


@pytest.mark.unit
class TestCheckQualityGates:
    """Test check_quality_gates with pre-populated results."""

    def test_no_issues_all_pass(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.results = []  # no issues
        gate = r.check_quality_gates()
        assert gate.passed is True
        assert gate.total_checks == 2
        assert gate.passed_checks == 2
        assert gate.failed_checks == 0

    def test_complexity_issues_fail(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.results = [
            AnalysisResult(
                file_path="a.py",
                line_number=1,
                column_number=0,
                severity=SeverityLevel.WARNING,
                message="High complexity",
                rule_id="PYSCN_COMPLEXITY",
                category="complexity",
            )
        ]
        gate = r.check_quality_gates()
        assert gate.passed is False
        assert gate.failed_checks >= 1

    def test_many_issues_per_file_fail(self, tmp_path):
        r = _make_reviewer(tmp_path)
        # Create 51 issues for one file (default max is 50)
        r.results = [
            AnalysisResult(
                file_path="big.py",
                line_number=i,
                column_number=0,
                severity=SeverityLevel.WARNING,
                message=f"Issue {i}",
                rule_id="LINT",
                category="quality",
            )
            for i in range(51)
        ]
        gate = r.check_quality_gates()
        assert gate.passed is False
        # Should have a max_issues_per_file failure
        failure_gates = [f["gate"] for f in gate.failures]
        assert "max_issues_per_file" in failure_gates

    def test_custom_thresholds(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.results = [
            AnalysisResult(
                file_path="a.py",
                line_number=1,
                column_number=0,
                severity=SeverityLevel.WARNING,
                message="complexity",
                rule_id="PYSCN_COMPLEXITY",
                category="complexity",
            )
        ]
        # With strict threshold
        gate = r.check_quality_gates(thresholds={
            "max_complexity": 5,
            "max_issues_per_file": 100,
        })
        assert gate.passed is False


# ============================================================================
# 6.  Summary Generation
# ============================================================================


@pytest.mark.unit
class TestGenerateSummary:
    """Test _generate_summary builds correct AnalysisSummary."""

    def test_empty_results(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.results = []
        summary = r._generate_summary(files_analyzed=0, analysis_time=1.5)
        assert isinstance(summary, AnalysisSummary)
        assert summary.total_issues == 0
        assert summary.files_analyzed == 0
        assert summary.analysis_time == 1.5

    def test_populated_results(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.results = [
            AnalysisResult("a.py", 1, 0, SeverityLevel.WARNING, "warn", "W01", "quality"),
            AnalysisResult("a.py", 2, 0, SeverityLevel.ERROR, "err", "E01", "security"),
            AnalysisResult("b.py", 1, 0, SeverityLevel.WARNING, "warn2", "W01", "quality"),
        ]
        summary = r._generate_summary(files_analyzed=2, analysis_time=0.5)
        assert summary.total_issues == 3
        assert summary.files_analyzed == 2
        assert summary.by_severity[SeverityLevel.WARNING] == 2
        assert summary.by_severity[SeverityLevel.ERROR] == 1
        assert summary.by_category["quality"] == 2
        assert summary.by_category["security"] == 1
        assert summary.by_rule["W01"] == 2
        assert summary.by_rule["E01"] == 1


# ============================================================================
# 7.  Clear Results
# ============================================================================


@pytest.mark.unit
class TestClearResults:
    """Test clear_results empties internal state."""

    def test_clear(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.results = [
            AnalysisResult("a.py", 1, 0, SeverityLevel.INFO, "msg", "R01", "cat"),
        ]
        r.metrics = {"key": CodeMetrics(100, 5, 80.0, 2.0, 1.0)}
        r.clear_results()
        assert r.results == []
        assert r.metrics == {}


# ============================================================================
# 8.  Report Generation (JSON / Markdown / HTML / unsupported)
# ============================================================================


@pytest.mark.unit
class TestReportGeneration:
    """Test report generation to various formats."""

    def test_json_report(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.results = [
            AnalysisResult("a.py", 10, 5, SeverityLevel.WARNING, "warn", "W01", "quality"),
        ]
        output = str(tmp_path / "report.json")
        result = r.generate_report(output, format="json")
        assert result is True
        with open(output) as f:
            data = json.load(f)
        assert data["summary"]["total_issues"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["file_path"] == "a.py"
        assert data["results"][0]["severity"] == "warning"

    def test_markdown_report(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.results = [
            AnalysisResult("b.py", 5, 0, SeverityLevel.ERROR, "error msg", "E01", "security", suggestion="fix it"),
        ]
        output = str(tmp_path / "report.md")
        result = r.generate_report(output, format="markdown")
        assert result is True
        with open(output) as f:
            content = f.read()
        assert "# Code Review Report" in content
        assert "error msg" in content
        assert "fix it" in content
        assert "Total Issues" in content

    def test_html_report_fallback(self, tmp_path):
        """HTML report falls back to basic HTML when pyscn report isn't available."""
        r = _make_reviewer(tmp_path)
        r.results = [
            AnalysisResult("c.py", 1, 0, SeverityLevel.INFO, "info msg", "I01", "style"),
        ]
        output = str(tmp_path / "report.html")
        result = r.generate_report(output, format="html")
        assert result is True
        with open(output) as f:
            content = f.read()
        assert "<!DOCTYPE html>" in content
        assert "Code Review Report" in content
        assert "info msg" in content

    def test_unsupported_format_returns_false(self, tmp_path):
        r = _make_reviewer(tmp_path)
        output = str(tmp_path / "report.xml")
        result = r.generate_report(output, format="xml")
        assert result is False

    def test_json_report_empty_results(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.results = []
        output = str(tmp_path / "empty.json")
        result = r.generate_report(output, format="json")
        assert result is True
        with open(output) as f:
            data = json.load(f)
        assert data["summary"]["total_issues"] == 0
        assert data["results"] == []

    def test_markdown_report_no_issues(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.results = []
        output = str(tmp_path / "empty.md")
        result = r.generate_report(output, format="markdown")
        assert result is True
        with open(output) as f:
            content = f.read()
        assert "Total Issues**: 0" in content


# ============================================================================
# 9.  Performance Optimization (static suggestions)
# ============================================================================


@pytest.mark.unit
class TestOptimizePerformance:
    """Test optimize_performance returns suggestion categories."""

    def test_returns_all_categories(self, tmp_path):
        r = _make_reviewer(tmp_path)
        result = r.optimize_performance()
        assert "memory_optimizations" in result
        assert "cpu_optimizations" in result
        assert "io_optimizations" in result
        assert "caching_opportunities" in result

    def test_suggestions_are_non_empty_lists(self, tmp_path):
        r = _make_reviewer(tmp_path)
        result = r.optimize_performance()
        for key in ["memory_optimizations", "cpu_optimizations", "io_optimizations", "caching_opportunities"]:
            assert isinstance(result[key], list)
            assert len(result[key]) > 0

    def test_memory_suggestions_content(self, tmp_path):
        r = _make_reviewer(tmp_path)
        result = r.optimize_performance()
        mem_text = " ".join(result["memory_optimizations"]).lower()
        assert "generator" in mem_text or "lazy" in mem_text


# ============================================================================
# 10.  Architecture Compliance: Naming Conventions
# ============================================================================


@pytest.mark.unit
class TestArchitectureCompliance:
    """Test _check_naming_conventions and related arch checks."""

    def test_naming_convention_detects_bad_test_name(self, tmp_path):
        """Create a file with 'test' in name that doesn't follow convention."""
        r = _make_reviewer(tmp_path)
        # Create a file named 'mytest.py' (has 'test' but no test_ prefix)
        bad_file = tmp_path / "mytest.py"
        bad_file.write_text("# test file")
        violations = r._check_naming_conventions()
        naming_violations = [v for v in violations if v.violation_type == "naming_convention"]
        assert len(naming_violations) >= 1
        assert any("mytest.py" in v.file_path for v in naming_violations)

    def test_naming_convention_ignores_good_names(self, tmp_path):
        r = _make_reviewer(tmp_path)
        good_file = tmp_path / "test_module.py"
        good_file.write_text("# correct test file")
        violations = r._check_naming_conventions()
        naming_violations = [v for v in violations if v.violation_type == "naming_convention"]
        assert not any("test_module.py" in v.file_path for v in naming_violations)

    def test_naming_convention_ignores_suffix_test(self, tmp_path):
        r = _make_reviewer(tmp_path)
        good_file = tmp_path / "module_test.py"
        good_file.write_text("# correct suffix test file")
        violations = r._check_naming_conventions()
        naming_violations = [v for v in violations if v.violation_type == "naming_convention"]
        assert not any("module_test.py" in v.file_path for v in naming_violations)

    def test_check_circular_dependencies_empty(self, tmp_path):
        r = _make_reviewer(tmp_path)
        violations = r._check_circular_dependencies()
        assert violations == []


@pytest.mark.unit
class TestFindFilesInLayer:
    """Test _find_files_in_layer pattern matching."""

    def test_presentation_layer_match(self, tmp_path):
        r = _make_reviewer(tmp_path)
        # Create matching file
        (tmp_path / "view.py").write_text("# view")
        (tmp_path / "controller.py").write_text("# controller")
        (tmp_path / "utils.py").write_text("# utils")
        files = r._find_files_in_layer("presentation")
        basenames = [os.path.basename(f) for f in files]
        assert "view.py" in basenames
        assert "controller.py" in basenames
        assert "utils.py" not in basenames

    def test_data_layer_match(self, tmp_path):
        r = _make_reviewer(tmp_path)
        (tmp_path / "repository.py").write_text("# repo")
        (tmp_path / "worker.py").write_text("# worker")
        files = r._find_files_in_layer("data")
        basenames = [os.path.basename(f) for f in files]
        assert "repository.py" in basenames
        assert "worker.py" not in basenames

    def test_unknown_layer_returns_empty(self, tmp_path):
        r = _make_reviewer(tmp_path)
        files = r._find_files_in_layer("nonexistent_layer")
        assert files == []


@pytest.mark.unit
class TestFileImportsPresentationLayer:
    """Test _file_imports_presentation_layer simplified import check."""

    def test_detects_import(self, tmp_path):
        r = _make_reviewer(tmp_path)
        data_file = tmp_path / "data.py"
        data_file.write_text("from view import something\n")
        pres_file = str(tmp_path / "view.py")
        assert r._file_imports_presentation_layer(str(data_file), [pres_file]) is True

    def test_no_import(self, tmp_path):
        r = _make_reviewer(tmp_path)
        data_file = tmp_path / "data.py"
        data_file.write_text("from utils import helper\n")
        pres_file = str(tmp_path / "view.py")
        assert r._file_imports_presentation_layer(str(data_file), [pres_file]) is False

    def test_nonexistent_file(self, tmp_path):
        r = _make_reviewer(tmp_path)
        result = r._file_imports_presentation_layer(str(tmp_path / "missing.py"), [])
        assert result is False


# ============================================================================
# 11.  Priority Actions
# ============================================================================


@pytest.mark.unit
class TestDeterminePriorityActions:
    """Test _determine_priority_actions with constructed objects."""

    def test_high_complexity_creates_action(self, tmp_path):
        r = _make_reviewer(tmp_path)
        suggestion = ComplexityReductionSuggestion(
            function_name="big_fn",
            file_path="f.py",
            current_complexity=25,
            suggested_refactoring="extract method",
            estimated_effort="medium",
            benefits=["readability"],
        )
        actions = r._determine_priority_actions([suggestion], [], [])
        assert len(actions) == 1
        assert actions[0]["type"] == "complexity_reduction"
        assert actions[0]["priority"] == "high"

    def test_low_complexity_no_action(self, tmp_path):
        r = _make_reviewer(tmp_path)
        suggestion = ComplexityReductionSuggestion(
            function_name="small_fn",
            file_path="f.py",
            current_complexity=16,
            suggested_refactoring="guard clause",
            estimated_effort="low",
            benefits=["readability"],
        )
        actions = r._determine_priority_actions([suggestion], [], [])
        assert len(actions) == 0  # < 20 not included

    def test_critical_dead_code_creates_action(self, tmp_path):
        r = _make_reviewer(tmp_path)
        finding = DeadCodeFinding(
            file_path="a.py",
            line_number=10,
            code_snippet="x = 1",
            reason="unused_variable",
            severity="critical",
            suggestion="Remove it",
        )
        actions = r._determine_priority_actions([], [finding], [])
        assert len(actions) == 1
        assert actions[0]["type"] == "dead_code_removal"

    def test_high_severity_violation_creates_action(self, tmp_path):
        r = _make_reviewer(tmp_path)
        violation = ArchitectureViolation(
            file_path="v.py",
            violation_type="layering",
            description="Bad dependency",
            severity="high",
            suggestion="Fix it",
        )
        actions = r._determine_priority_actions([], [], [violation])
        assert len(actions) == 1
        assert actions[0]["type"] == "architecture_fix"
        assert actions[0]["priority"] == "medium"


# ============================================================================
# 12.  Project Analysis (with filesystem)
# ============================================================================


@pytest.mark.unit
class TestAnalyzeProject:
    """Test analyze_project with a real temp directory of Python files."""

    def test_analyze_project_finds_python_files(self, tmp_path):
        """analyze_project walks directories and finds .py files."""
        r = _make_reviewer(tmp_path)
        r.config["pyscn"]["enabled"] = False  # disable pyscn to avoid subprocess calls
        # Create some files
        (tmp_path / "module.py").write_text("x = 1\n")
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "helper.py").write_text("def f(): pass\n")
        (subdir / "readme.md").write_text("# Docs\n")

        summary = r.analyze_project()
        assert isinstance(summary, AnalysisSummary)
        # Should have analyzed 2 python files (module.py + helper.py)
        assert summary.files_analyzed == 2

    def test_analyze_project_skips_ignored_dirs(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.config["pyscn"]["enabled"] = False
        # Create files in ignored directories
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "hooks.py").write_text("# git internals\n")
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        (pycache / "mod.py").write_text("# compiled\n")
        (tmp_path / "real.py").write_text("# real\n")

        summary = r.analyze_project()
        assert summary.files_analyzed == 1  # only real.py

    def test_analyze_project_with_specific_path(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.config["pyscn"]["enabled"] = False
        target = tmp_path / "target"
        target.mkdir()
        (target / "a.py").write_text("a = 1\n")
        (tmp_path / "outside.py").write_text("b = 2\n")

        summary = r.analyze_project(target_paths=[str(target)])
        assert summary.files_analyzed == 1  # only a.py


# ============================================================================
# 13.  Detect Code Smells (stub methods)
# ============================================================================


@pytest.mark.unit
class TestDetectCodeSmells:
    """Test detect_code_smells and its sub-detectors."""

    def test_feature_envy_returns_empty(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_feature_envy() == []

    def test_data_clumps_returns_empty(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_data_clumps() == []

    def test_primitive_obsession_returns_empty(self, tmp_path):
        r = _make_reviewer(tmp_path)
        assert r._detect_primitive_obsession() == []

    def test_detect_code_smells_returns_list(self, tmp_path):
        r = _make_reviewer(tmp_path)
        result = r.detect_code_smells()
        assert isinstance(result, list)


# ============================================================================
# 14.  Technical Debt Skeleton
# ============================================================================


@pytest.mark.unit
class TestAnalyzeTechnicalDebt:
    """Test analyze_technical_debt returns expected structure."""

    def test_returns_debt_structure(self, tmp_path):
        r = _make_reviewer(tmp_path)
        result = r.analyze_technical_debt()
        assert "total_debt_hours" in result
        assert "debt_by_category" in result
        assert "debt_by_severity" in result
        assert "debt_by_file" in result
        assert "top_debt_items" in result
        assert isinstance(result["total_debt_hours"], (int, float))


@pytest.mark.unit
class TestGetTopTechnicalDebtItems:
    """Test _get_top_technical_debt_items sorting and limiting."""

    def test_sorts_by_hours_and_limits(self, tmp_path):
        r = _make_reviewer(tmp_path)
        suggestions = [
            ComplexityReductionSuggestion("f1", "a.py", 30, "extract", "medium", []),
            ComplexityReductionSuggestion("f2", "b.py", 20, "guard", "low", []),
        ]
        findings = [
            DeadCodeFinding("c.py", 10, "x=1", "unused", "critical", "Remove"),
        ]
        violations = [
            ArchitectureViolation("d.py", "layering", "Bad dep", "high", "Fix"),
        ]
        items = r._get_top_technical_debt_items(suggestions, findings, violations)
        # Should have items from all three categories
        types = [item["type"] for item in items]
        assert "complexity" in types
        assert "dead_code" in types
        assert "architecture" in types
        # Sorted by estimated hours descending
        assert items[0]["estimated_hours"] >= items[-1]["estimated_hours"]


# ============================================================================
# 15.  Dashboard helper methods
# ============================================================================


@pytest.mark.unit
class TestDashboardHelpers:
    """Test identify_quick_wins and identify_long_term_improvements."""

    def test_quick_wins_from_critical_dead_code(self, tmp_path):
        r = _make_reviewer(tmp_path)
        issues = [
            {"file_path": "/a.py", "line_number": 5, "severity": "critical", "reason": "unused"},
            {"file_path": "/b.py", "line_number": 10, "severity": "warning", "reason": "unused"},
        ]
        wins = r._identify_quick_wins(issues)
        assert len(wins) == 1  # only critical
        assert wins[0]["effort"] == "low"
        assert wins[0]["impact"] == "high"

    def test_long_term_improvements_high_risk(self, tmp_path):
        r = _make_reviewer(tmp_path)
        improvements = r._identify_long_term_improvements({"high_risk_count": 15})
        assert len(improvements) >= 1
        assert improvements[0]["effort"] == "high"

    def test_long_term_improvements_low_risk(self, tmp_path):
        r = _make_reviewer(tmp_path)
        improvements = r._identify_long_term_improvements({"high_risk_count": 5})
        assert improvements == []

    def test_count_total_files(self, tmp_path):
        r = _make_reviewer(tmp_path)
        (tmp_path / "a.py").write_text("# a")
        (tmp_path / "b.py").write_text("# b")
        (tmp_path / "c.txt").write_text("# c")
        assert r._count_total_files() == 2

    def test_count_total_lines(self, tmp_path):
        r = _make_reviewer(tmp_path)
        (tmp_path / "a.py").write_text("line1\nline2\nline3\n")
        (tmp_path / "b.py").write_text("x\n")
        assert r._count_total_lines() == 4

    def test_count_skips_ignored_dirs(self, tmp_path):
        r = _make_reviewer(tmp_path)
        (tmp_path / "a.py").write_text("# a")
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        (pycache / "cached.py").write_text("# cached")
        assert r._count_total_files() == 1


# ============================================================================
# 16.  Comprehensive Report Generation
# ============================================================================


@pytest.mark.unit
class TestComprehensiveReportGeneration:
    """Test generate_comprehensive_report writes HTML file."""

    def test_generates_html_file(self, tmp_path):
        r = _make_reviewer(tmp_path)
        # Create some python files for the dashboard to count
        (tmp_path / "mod.py").write_text("def f(): pass\n")
        output = str(tmp_path / "dashboard.html")
        result = r.generate_comprehensive_report(output)
        assert result is True
        assert os.path.exists(output)
        with open(output) as f:
            content = f.read()
        assert "Code Quality Dashboard" in content
        assert "<!DOCTYPE html>" in content

    def test_report_at_bad_path_returns_false(self, tmp_path):
        r = _make_reviewer(tmp_path)
        result = r.generate_comprehensive_report("/nonexistent/path/report.html")
        assert result is False


# ============================================================================
# 17.  Pyscn Analysis (when pyscn disabled or unavailable)
# ============================================================================


@pytest.mark.unit
class TestPyscnAnalysisDisabled:
    """Test _run_pyscn_analysis when pyscn is disabled."""

    def test_disabled_returns_empty(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.config["pyscn"]["enabled"] = False
        results = r._run_pyscn_analysis("test.py")
        assert results == []

    def test_non_python_returns_empty(self, tmp_path):
        r = _make_reviewer(tmp_path)
        results = r._run_pyscn_analysis("test.js")
        assert results == []


# ============================================================================
# 18.  Traditional Analysis (when tools unavailable)
# ============================================================================


@pytest.mark.unit
class TestTraditionalAnalysis:
    """Test _run_traditional_analysis and tool runners when tools not available."""

    def test_no_tools_returns_empty(self, tmp_path):
        r = _make_reviewer(tmp_path)
        # All tools marked as unavailable
        results = r._run_traditional_analysis("test.py", ["quality", "security", "style"])
        assert results == []

    def test_non_python_returns_empty(self, tmp_path):
        r = _make_reviewer(tmp_path)
        results = r._run_traditional_analysis("test.js", ["quality"])
        assert results == []


# ============================================================================
# 19.  Load Config
# ============================================================================


@pytest.mark.unit
class TestLoadConfig:
    """Test _load_config defaults and file loading."""

    def test_default_config_no_file(self, tmp_path):
        r = _make_reviewer(tmp_path)
        # Manually call _load_config with no config_path set
        r.config_path = None
        config = r._load_config()
        assert config["max_complexity"] == 15
        assert "quality" in config["analysis_types"]
        assert config["pyscn"]["enabled"] is True

    def test_config_from_nonexistent_file(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.config_path = str(tmp_path / "nonexistent.toml")
        config = r._load_config()
        # Should fall back to defaults
        assert config["max_complexity"] == 15


# ============================================================================
# 20.  Analyze File
# ============================================================================


@pytest.mark.unit
class TestAnalyzeFile:
    """Test analyze_file with pyscn disabled and no tools."""

    def test_analyze_file_stores_results(self, tmp_path):
        r = _make_reviewer(tmp_path)
        r.config["pyscn"]["enabled"] = False
        py_file = tmp_path / "sample.py"
        py_file.write_text("x = 1\n")
        results = r.analyze_file(str(py_file))
        # No tools available, no pyscn, so results should be empty but stored
        assert isinstance(results, list)
        # Results get appended to r.results
        assert r.results == results


# ============================================================================
# 21.  Full CodeReviewer init (pyscn required)
# ============================================================================


@requires_pyscn
@pytest.mark.unit
class TestCodeReviewerInit:
    """Test CodeReviewer full initialization when pyscn is available."""

    def test_init_with_defaults(self, tmp_path):
        from codomyrmex.coding.review.reviewer import CodeReviewer

        reviewer = CodeReviewer(project_root=str(tmp_path))
        assert reviewer.project_root == str(tmp_path)
        assert reviewer.config is not None
        assert reviewer.tools_available["pyscn"] is True

    def test_init_with_config(self, tmp_path):
        from codomyrmex.coding.review.reviewer import CodeReviewer

        config = tmp_path / "config.toml"
        config.write_text("")  # empty config
        reviewer = CodeReviewer(project_root=str(tmp_path), config_path=str(config))
        assert reviewer.config_path == str(config)


# ============================================================================
# 22.  Dashboard Priority Actions from Dashboard
# ============================================================================


@pytest.mark.unit
class TestDeterminePriorityActionsFromDashboard:
    """Test _determine_priority_actions_from_dashboard."""

    def test_high_complexity_action(self, tmp_path):
        r = _make_reviewer(tmp_path)
        complexity_issues = [
            {"function_name": "fn", "file_path": "a.py", "complexity": 25, "line_number": 1},
        ]
        actions = r._determine_priority_actions_from_dashboard(complexity_issues, [], [])
        assert len(actions) == 1
        assert actions[0]["priority"] == "high"

    def test_low_complexity_no_action(self, tmp_path):
        r = _make_reviewer(tmp_path)
        complexity_issues = [
            {"function_name": "fn", "file_path": "a.py", "complexity": 15, "line_number": 1},
        ]
        actions = r._determine_priority_actions_from_dashboard(complexity_issues, [], [])
        assert len(actions) == 0

    def test_critical_dead_code_action(self, tmp_path):
        r = _make_reviewer(tmp_path)
        dead_code_issues = [
            {"file_path": "a.py", "line_number": 1, "severity": "critical", "reason": "unused"},
        ]
        actions = r._determine_priority_actions_from_dashboard([], dead_code_issues, [])
        assert len(actions) == 1
        assert actions[0]["type"] == "dead_code_removal"
