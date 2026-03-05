"""Unit tests for coding/review/reviewer_impl/dashboard.py — zero-mock policy.

Tests DashboardMixin via a minimal concrete subclass that supplies controlled
stub implementations of all required collaborators (pyscn_analyzer, etc.).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from codomyrmex.coding.review.models import QualityDashboard
from codomyrmex.coding.review.reviewer_impl.dashboard import DashboardMixin

pytestmark = pytest.mark.unit
_PERFECT_SCORE = 100.0
_ZERO_SCORE = 0.0
_DEFAULT_MAINTAINABILITY = 75.0
_SCORE_THRESHOLD_A = 90.0


class _FakePyscnAnalyzer:
    """Minimal pyscn-analyzer stand-in returning controlled empty data."""

    def analyze_complexity(self, root: object) -> list:
        return []

    def detect_dead_code(self, root: object) -> list:
        return []

    def find_clones(self, files: object, threshold: float = 0.8) -> list:
        return []

    def analyze_coupling(self, root: object) -> list:
        return []


class _ConcreteDashboard(DashboardMixin):
    """Minimal concrete subclass of DashboardMixin used only in tests."""

    def __init__(self, project_root: object = None) -> None:
        self.project_root = project_root or Path("/tmp")
        self.pyscn_analyzer = _FakePyscnAnalyzer()
        self._root_str: str = str(self.project_root)
        self._analyzer_name: str = type(self.pyscn_analyzer).__name__

    def analyze_architecture_compliance(self) -> list:
        return []

    def analyze_complexity_patterns(self) -> list:
        return []

    def analyze_dead_code_patterns(self) -> list:
        return []


class TestCalculateGrade:
    """_calculate_grade returns correct letter grades across all thresholds."""

    def setup_method(self) -> None:
        self.dash = _ConcreteDashboard()

    def test_grade_a_at_90(self) -> None:
        assert self.dash._calculate_grade(90.0) == "A"

    def test_grade_a_at_100(self) -> None:
        assert self.dash._calculate_grade(100.0) == "A"

    def test_grade_b_at_80(self) -> None:
        assert self.dash._calculate_grade(80.0) == "B"

    def test_grade_b_at_89(self) -> None:
        assert self.dash._calculate_grade(89.0) == "B"

    def test_grade_c_at_70(self) -> None:
        assert self.dash._calculate_grade(70.0) == "C"

    def test_grade_c_at_79(self) -> None:
        assert self.dash._calculate_grade(79.0) == "C"

    def test_grade_d_at_60(self) -> None:
        assert self.dash._calculate_grade(60.0) == "D"

    def test_grade_d_at_69(self) -> None:
        assert self.dash._calculate_grade(69.0) == "D"

    def test_grade_f_at_59(self) -> None:
        assert self.dash._calculate_grade(59.0) == "F"

    def test_grade_f_at_zero(self) -> None:
        assert self.dash._calculate_grade(0.0) == "F"


class TestCalculateOverallScore:
    """_calculate_overall_score computes weighted average and clamps to [0, 100]."""

    def setup_method(self) -> None:
        self.dash = _ConcreteDashboard()

    @pytest.mark.parametrize(
        "score,expected",
        [(100.0, 100.0), (0.0, 0.0), (200.0, 100.0), (-50.0, 0.0)],
    )
    def test_uniform_score_round_trips(self, score: float, expected: float) -> None:
        c = {"score": score}
        result = self.dash._calculate_overall_score(c, c, c, c, c)
        assert result == expected

    def test_missing_score_key_treated_as_zero(self) -> None:
        empty: dict = {}
        assert self.dash._calculate_overall_score(empty, empty, empty, empty, empty) == 0.0

    def test_complexity_weight_is_25_pct(self) -> None:
        complexity = {"score": 100.0}
        zero = {"score": 0.0}
        result = self.dash._calculate_overall_score(complexity, zero, zero, zero, zero)
        assert abs(result - 25.0) < 0.001


class TestDetermineActions:
    """_determine_priority_actions_from_dashboard converts issues to actions."""

    def setup_method(self) -> None:
        self.dash = _ConcreteDashboard()

    def test_all_empty_gives_no_actions(self) -> None:
        assert self.dash._determine_priority_actions_from_dashboard([], [], []) == []

    def test_high_complexity_adds_action(self) -> None:
        issues = [{"function_name": "foo", "file_path": "a.py", "complexity": 25}]
        actions = self.dash._determine_priority_actions_from_dashboard(issues, [], [])
        assert len(actions) == 1
        assert actions[0]["type"] == "complexity_reduction"
        assert actions[0]["priority"] == "high"

    def test_low_complexity_not_actioned(self) -> None:
        issues = [{"function_name": "bar", "file_path": "a.py", "complexity": 10}]
        assert self.dash._determine_priority_actions_from_dashboard(issues, [], []) == []

    def test_critical_dead_code_adds_action(self) -> None:
        dead = [{"severity": "critical", "file_path": "a.py", "line_number": 10, "reason": "unused"}]
        actions = self.dash._determine_priority_actions_from_dashboard([], dead, [])
        assert len(actions) == 1
        assert actions[0]["type"] == "dead_code_removal"

    def test_warning_dead_code_not_actioned(self) -> None:
        dead = [{"severity": "warning", "file_path": "a.py", "line_number": 10, "reason": "unused"}]
        result = self.dash._determine_priority_actions_from_dashboard([], dead, [])
        assert result == []


class TestIdentifyQuickWins:
    """_identify_quick_wins surfaces critical dead code as low-effort wins."""

    def setup_method(self) -> None:
        self.dash = _ConcreteDashboard()

    def test_empty_gives_no_wins(self) -> None:
        assert self.dash._identify_quick_wins([]) == []

    def test_critical_dead_code_is_quick_win(self) -> None:
        issue = {"severity": "critical", "file_path": "a.py", "line_number": 5}
        wins = self.dash._identify_quick_wins([issue])
        assert len(wins) == 1
        assert wins[0]["effort"] == "low"
        assert wins[0]["impact"] == "high"

    def test_warning_not_a_quick_win(self) -> None:
        issue = {"severity": "warning", "file_path": "a.py", "line_number": 5}
        result = self.dash._identify_quick_wins([issue])
        assert result == []


class TestIdentifyLongTermImprovements:
    """_identify_long_term_improvements triggers on high_risk_count > 10."""

    def setup_method(self) -> None:
        self.dash = _ConcreteDashboard()

    def test_low_risk_count_no_improvement(self) -> None:
        assert self.dash._identify_long_term_improvements({"high_risk_count": 5}) == []

    def test_boundary_at_10_no_improvement(self) -> None:
        assert self.dash._identify_long_term_improvements({"high_risk_count": 10}) == []

    def test_11_risk_adds_improvement(self) -> None:
        result = self.dash._identify_long_term_improvements({"high_risk_count": 11})
        assert len(result) == 1
        assert result[0]["type"] == "architecture_refactoring"

    def test_missing_key_no_improvement(self) -> None:
        assert self.dash._identify_long_term_improvements({}) == []


class TestSuggestProperName:
    """_suggest_proper_name enforces test_ prefix naming convention."""

    def setup_method(self) -> None:
        self.dash = _ConcreteDashboard()

    def test_already_prefixed_unchanged(self) -> None:
        assert self.dash._suggest_proper_name("test_foo.py") == "test_foo.py"

    def test_non_test_file_unchanged(self) -> None:
        assert self.dash._suggest_proper_name("foo.py") == "foo.py"

    def test_suffix_test_converted(self) -> None:
        assert self.dash._suggest_proper_name("foo_test.py") == "test_foo.py"


class TestGetComplexityMetricsEmpty:
    """_get_complexity_metrics returns safe defaults when pyscn returns empty list."""

    def test_empty_results_give_zero_functions(self) -> None:
        result = _ConcreteDashboard()._get_complexity_metrics()
        assert result["total_functions"] == 0

    def test_empty_results_give_100_score(self) -> None:
        result = _ConcreteDashboard()._get_complexity_metrics()
        assert result["score"] == 100.0

    def test_result_has_required_keys(self) -> None:
        result = _ConcreteDashboard()._get_complexity_metrics()
        assert "average_complexity" in result
        assert "high_risk_count" in result


class TestGetDeadCodeMetricsEmpty:
    """_get_dead_code_metrics returns safe defaults when pyscn returns empty list."""

    def test_empty_gives_zero_findings(self) -> None:
        assert _ConcreteDashboard()._get_dead_code_metrics()["total_findings"] == 0

    def test_empty_gives_100_score(self) -> None:
        assert _ConcreteDashboard()._get_dead_code_metrics()["score"] == 100.0


class TestGetCouplingMetricsEmpty:
    """_get_coupling_metrics returns safe defaults when pyscn returns empty list."""

    def test_empty_gives_zero_classes(self) -> None:
        assert _ConcreteDashboard()._get_coupling_metrics()["total_classes"] == 0

    def test_empty_gives_100_score(self) -> None:
        assert _ConcreteDashboard()._get_coupling_metrics()["score"] == 100.0


class TestGetArchitectureMetricsEmpty:
    """_get_architecture_metrics returns perfect score with no violations."""

    def test_no_violations_zero_total(self) -> None:
        result = _ConcreteDashboard()._get_architecture_metrics()
        assert result["total_violations"] == 0

    def test_no_violations_score_100(self) -> None:
        assert _ConcreteDashboard()._get_architecture_metrics()["score"] == 100.0


class TestCalculateMaintainabilityEmpty:
    """_calculate_maintainability_score returns 100.0 when pyscn returns empty."""

    def test_empty_pyscn_gives_100(self) -> None:
        assert _ConcreteDashboard()._calculate_maintainability_score() == 100.0


class TestCalculateTestabilityEmpty:
    """_calculate_testability_score returns 75.0 when no complexity data."""

    def test_no_data_gives_75(self) -> None:
        assert _ConcreteDashboard()._calculate_testability_score() == 75.0


class TestCalculateReliabilityEmpty:
    """_calculate_reliability_score returns 95.0 when no dead code findings."""

    def test_empty_dir_gives_95(self, tmp_path: Path) -> None:
        assert _ConcreteDashboard(tmp_path)._calculate_reliability_score() == 95.0


class TestCalculateSecurityScoreEmptyDir:
    """_calculate_security_score returns 100.0 for directory with no .py files."""

    def test_empty_dir_gives_100(self, tmp_path: Path) -> None:
        assert _ConcreteDashboard(tmp_path)._calculate_security_score() == 100.0


class TestCalculatePerformanceScoreEmpty:
    """_calculate_performance_score returns 80.0 when no complexity data."""

    def test_empty_pyscn_gives_80(self, tmp_path: Path) -> None:
        assert _ConcreteDashboard(tmp_path)._calculate_performance_score() == 80.0


class TestCountTotalFiles:
    """_count_total_files counts .py files recursively, skips other types."""

    def test_empty_dir_returns_zero(self, tmp_path: Path) -> None:
        assert _ConcreteDashboard(tmp_path)._count_total_files() == 0

    def test_single_py_file_counted(self, tmp_path: Path) -> None:
        (tmp_path / "foo.py").write_text("# test\n")
        assert _ConcreteDashboard(tmp_path)._count_total_files() == 1

    def test_two_py_files_counted(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("")
        (tmp_path / "b.py").write_text("")
        assert _ConcreteDashboard(tmp_path)._count_total_files() == 2

    def test_non_py_files_excluded(self, tmp_path: Path) -> None:
        (tmp_path / "readme.txt").write_text("hello")
        assert _ConcreteDashboard(tmp_path)._count_total_files() == 0


class TestCountTotalLines:
    """_count_total_lines sums line counts across all .py files."""

    def test_empty_dir_returns_zero(self, tmp_path: Path) -> None:
        assert _ConcreteDashboard(tmp_path)._count_total_lines() == 0

    def test_file_with_three_lines(self, tmp_path: Path) -> None:
        (tmp_path / "foo.py").write_text("a\nb\nc\n")
        assert _ConcreteDashboard(tmp_path)._count_total_lines() == 3

    def test_two_files_summed(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("x\ny\n")
        (tmp_path / "b.py").write_text("z\n")
        assert _ConcreteDashboard(tmp_path)._count_total_lines() == 3


class TestGetTopIssuesEmpty:
    """Top-issue helpers all return empty lists when pyscn returns empty."""

    def test_complexity_issues_empty(self) -> None:
        assert _ConcreteDashboard()._get_top_complexity_issues() == []

    def test_dead_code_issues_empty(self) -> None:
        assert _ConcreteDashboard()._get_top_dead_code_issues() == []

    def test_duplication_issues_empty(self, tmp_path: Path) -> None:
        assert _ConcreteDashboard(tmp_path)._get_top_duplication_issues() == []


class TestDetectCodeSmells:
    """detect_code_smells and individual detectors return lists."""

    def test_returns_empty_list_when_no_findings(self) -> None:
        smells = _ConcreteDashboard().detect_code_smells()
        assert isinstance(smells, list) and smells == []

    def test_detect_long_methods_empty(self) -> None:
        assert _ConcreteDashboard()._detect_long_methods() == []

    def test_detect_large_classes_empty(self) -> None:
        assert _ConcreteDashboard()._detect_large_classes() == []

    def test_detect_feature_envy_always_empty(self) -> None:
        assert _ConcreteDashboard()._detect_feature_envy() == []

    def test_detect_data_clumps_always_empty(self) -> None:
        assert _ConcreteDashboard()._detect_data_clumps() == []

    def test_detect_primitive_obsession_always_empty(self) -> None:
        assert _ConcreteDashboard()._detect_primitive_obsession() == []


class TestSuggestAutomatedFixes:
    """suggest_automated_fixes returns dict with all required categories."""

    def test_returns_dict_with_correct_keys(self) -> None:
        fixes = _ConcreteDashboard().suggest_automated_fixes()
        assert isinstance(fixes, dict)
        assert "dead_code_removal" in fixes
        assert "import_optimization" in fixes
        assert "naming_convention_fixes" in fixes
        assert "complexity_reductions" in fixes

    def test_all_lists_are_empty_without_findings(self) -> None:
        fixes = _ConcreteDashboard().suggest_automated_fixes()
        assert fixes["dead_code_removal"] == []
        assert fixes["naming_convention_fixes"] == []


class TestAnalyzeTechnicalDebt:
    """analyze_technical_debt returns structured zero-debt analysis."""

    def test_returns_dict_with_expected_keys(self) -> None:
        debt = _ConcreteDashboard().analyze_technical_debt()
        assert isinstance(debt, dict)
        for key in ("total_debt_hours", "debt_by_category", "top_debt_items"):
            assert key in debt

    def test_zero_debt_when_no_findings(self) -> None:
        assert _ConcreteDashboard().analyze_technical_debt()["total_debt_hours"] == 0

    def test_top_items_empty_when_no_findings(self) -> None:
        assert _ConcreteDashboard().analyze_technical_debt()["top_debt_items"] == []


class TestGenerateQualityDashboard:
    """generate_quality_dashboard produces a valid QualityDashboard object."""

    def test_returns_quality_dashboard_instance(self, tmp_path: Path) -> None:
        result = _ConcreteDashboard(tmp_path).generate_quality_dashboard()
        assert isinstance(result, QualityDashboard)

    def test_overall_score_is_100_for_empty_project(self, tmp_path: Path) -> None:
        result = _ConcreteDashboard(tmp_path).generate_quality_dashboard()
        assert result.overall_score == 100.0

    def test_grade_a_for_perfect_score(self, tmp_path: Path) -> None:
        result = _ConcreteDashboard(tmp_path).generate_quality_dashboard()
        assert result.grade == "A"

    def test_total_files_zero_for_empty_dir(self, tmp_path: Path) -> None:
        result = _ConcreteDashboard(tmp_path).generate_quality_dashboard()
        assert result.total_files == 0

    def test_timestamp_is_nonempty_string(self, tmp_path: Path) -> None:
        result = _ConcreteDashboard(tmp_path).generate_quality_dashboard()
        assert isinstance(result.analysis_timestamp, str) and result.analysis_timestamp
