"""Unit tests for coding.review.reviewer_impl.dashboard — DashboardMixin.

Tests the quality dashboard generation, scoring algorithms, grade
calculation, metric helpers, code smell detection, automated fix
suggestions, and technical debt analysis.

Zero-mock policy: all tests use real objects, real files (via tmp_path),
and real CodeReviewer instances.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from codomyrmex.coding.review.models import (
    ArchitectureViolation,
    ComplexityReductionSuggestion,
    DeadCodeFinding,
    QualityDashboard,
)
from codomyrmex.coding.review.reviewer_impl.dashboard import DashboardMixin

# ---------------------------------------------------------------------------
# Helper: lightweight concrete class that provides DashboardMixin's required
# attributes without requiring the full CodeReviewer + pyscn stack.
# ---------------------------------------------------------------------------

class _StubAnalyzer:
    """Minimal pyscn analyzer stand-in that returns controllable data.

    NOT a mock -- it is a real, fully instantiated object with real method
    implementations that return deterministic data for testing.
    """

    def __init__(
        self,
        complexity_results: list[dict[str, Any]] | None = None,
        dead_code_results: list[dict[str, Any]] | None = None,
        coupling_results: list[dict[str, Any]] | None = None,
        clone_groups: list[dict[str, Any]] | None = None,
        raise_on_call: bool = False,
    ):
        self._complexity = complexity_results or []
        self._dead_code = dead_code_results or []
        self._coupling = coupling_results or []
        self._clones = clone_groups or []
        self._raise = raise_on_call

    def analyze_complexity(self, project_root: str) -> list[dict[str, Any]]:
        if self._raise:
            raise RuntimeError("analyzer error")
        return self._complexity

    def detect_dead_code(self, project_root: str) -> list[dict[str, Any]]:
        if self._raise:
            raise RuntimeError("analyzer error")
        return self._dead_code

    def analyze_coupling(self, project_root: str) -> list[dict[str, Any]]:
        if self._raise:
            raise RuntimeError("analyzer error")
        return self._coupling

    def find_clones(self, files: list[str], threshold: float = 0.8) -> list[dict[str, Any]]:
        if self._raise:
            raise RuntimeError("analyzer error")
        return self._clones


class _ConcreteReviewer(DashboardMixin):
    """Concrete class mixing in DashboardMixin plus stubs for cross-mixin deps."""

    def __init__(
        self,
        project_root: str,
        pyscn_analyzer: _StubAnalyzer | None = None,
        architecture_violations: list[ArchitectureViolation] | None = None,
        dead_code_findings: list[DeadCodeFinding] | None = None,
        complexity_suggestions: list[ComplexityReductionSuggestion] | None = None,
    ):
        self.project_root = project_root
        self.pyscn_analyzer = pyscn_analyzer or _StubAnalyzer()
        self._arch_violations = architecture_violations or []
        self._dead_code_findings = dead_code_findings or []
        self._complexity_suggestions = complexity_suggestions or []
        self.config = {"max_complexity": 15}

    # Cross-mixin methods consumed by DashboardMixin
    def analyze_architecture_compliance(self) -> list[ArchitectureViolation]:
        return self._arch_violations

    def analyze_dead_code_patterns(self) -> list[DeadCodeFinding]:
        return self._dead_code_findings

    def analyze_complexity_patterns(self) -> list[ComplexityReductionSuggestion]:
        return self._complexity_suggestions


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def small_project(tmp_path: Path) -> Path:
    """Create a minimal Python project tree for file-walking tests."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()

    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "main.py").write_text(
        "def hello():\n    return 'world'\n\ndef add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )
    (pkg / "utils.py").write_text(
        "import os\n\ndef get_cwd():\n    return os.getcwd()\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def security_project(tmp_path: Path) -> Path:
    """Create a project with known security anti-patterns."""
    (tmp_path / "dangerous.py").write_text(
        "import os\nresult = eval('1+1')\nos.system('ls')\n",
        encoding="utf-8",
    )
    (tmp_path / "safe.py").write_text(
        "def add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def reviewer(small_project: Path) -> _ConcreteReviewer:
    """Provide a basic _ConcreteReviewer over the small project."""
    return _ConcreteReviewer(project_root=str(small_project))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculateGrade:
    """Test the _calculate_grade helper."""

    def test_grade_a(self, reviewer: _ConcreteReviewer):
        assert reviewer._calculate_grade(95.0) == "A"

    def test_grade_a_boundary(self, reviewer: _ConcreteReviewer):
        assert reviewer._calculate_grade(90.0) == "A"

    def test_grade_b(self, reviewer: _ConcreteReviewer):
        assert reviewer._calculate_grade(85.0) == "B"

    def test_grade_b_boundary(self, reviewer: _ConcreteReviewer):
        assert reviewer._calculate_grade(80.0) == "B"

    def test_grade_c(self, reviewer: _ConcreteReviewer):
        assert reviewer._calculate_grade(75.0) == "C"

    def test_grade_c_boundary(self, reviewer: _ConcreteReviewer):
        assert reviewer._calculate_grade(70.0) == "C"

    def test_grade_d(self, reviewer: _ConcreteReviewer):
        assert reviewer._calculate_grade(65.0) == "D"

    def test_grade_d_boundary(self, reviewer: _ConcreteReviewer):
        assert reviewer._calculate_grade(60.0) == "D"

    def test_grade_f(self, reviewer: _ConcreteReviewer):
        assert reviewer._calculate_grade(50.0) == "F"

    def test_grade_f_zero(self, reviewer: _ConcreteReviewer):
        assert reviewer._calculate_grade(0.0) == "F"

    def test_grade_perfect(self, reviewer: _ConcreteReviewer):
        assert reviewer._calculate_grade(100.0) == "A"


@pytest.mark.unit
class TestCalculateOverallScore:
    """Test the _calculate_overall_score weighted-average helper."""

    def test_all_perfect(self, reviewer: _ConcreteReviewer):
        data = {"score": 100.0}
        result = reviewer._calculate_overall_score(data, data, data, data, data)
        assert result == 100.0

    def test_all_zero(self, reviewer: _ConcreteReviewer):
        data = {"score": 0.0}
        result = reviewer._calculate_overall_score(data, data, data, data, data)
        assert result == 0.0

    def test_weighted_mix(self, reviewer: _ConcreteReviewer):
        # complexity weight 0.25, dead_code 0.20, duplication 0.15, coupling 0.20, architecture 0.20
        result = reviewer._calculate_overall_score(
            {"score": 80.0},  # complexity: 80 * 0.25 = 20
            {"score": 60.0},  # dead_code:  60 * 0.20 = 12
            {"score": 100.0}, # duplication: 100 * 0.15 = 15
            {"score": 40.0},  # coupling:   40 * 0.20 = 8
            {"score": 90.0},  # architecture: 90 * 0.20 = 18
        )
        expected = 20.0 + 12.0 + 15.0 + 8.0 + 18.0  # 73.0
        assert abs(result - expected) < 0.01

    def test_clamped_above_100(self, reviewer: _ConcreteReviewer):
        # Shouldn't happen in practice but tests the clamping
        data = {"score": 200.0}
        result = reviewer._calculate_overall_score(data, data, data, data, data)
        assert result == 100.0

    def test_missing_score_key_defaults_zero(self, reviewer: _ConcreteReviewer):
        data = {}  # no "score" key
        result = reviewer._calculate_overall_score(data, data, data, data, data)
        assert result == 0.0


@pytest.mark.unit
class TestDeterminePriorityActions:
    """Test the _determine_priority_actions_from_dashboard helper."""

    def test_no_issues(self, reviewer: _ConcreteReviewer):
        actions = reviewer._determine_priority_actions_from_dashboard([], [], [])
        assert actions == []

    def test_high_complexity_generates_action(self, reviewer: _ConcreteReviewer):
        complexity_issues = [
            {"function_name": "big_func", "file_path": "a.py", "complexity": 25, "line_number": 10}
        ]
        actions = reviewer._determine_priority_actions_from_dashboard(complexity_issues, [], [])
        assert len(actions) == 1
        assert actions[0]["type"] == "complexity_reduction"
        assert actions[0]["priority"] == "high"

    def test_low_complexity_no_action(self, reviewer: _ConcreteReviewer):
        complexity_issues = [
            {"function_name": "small_func", "file_path": "b.py", "complexity": 10, "line_number": 5}
        ]
        actions = reviewer._determine_priority_actions_from_dashboard(complexity_issues, [], [])
        assert len(actions) == 0

    def test_critical_dead_code_generates_action(self, reviewer: _ConcreteReviewer):
        dead_code_issues = [
            {"file_path": "c.py", "line_number": 3, "reason": "unused", "severity": "critical"}
        ]
        actions = reviewer._determine_priority_actions_from_dashboard([], dead_code_issues, [])
        assert len(actions) == 1
        assert actions[0]["type"] == "dead_code_removal"

    def test_warning_dead_code_no_action(self, reviewer: _ConcreteReviewer):
        dead_code_issues = [
            {"file_path": "d.py", "line_number": 7, "reason": "unused import", "severity": "warning"}
        ]
        actions = reviewer._determine_priority_actions_from_dashboard([], dead_code_issues, [])
        assert len(actions) == 0


@pytest.mark.unit
class TestIdentifyQuickWins:
    """Test the _identify_quick_wins helper."""

    def test_no_issues(self, reviewer: _ConcreteReviewer):
        assert reviewer._identify_quick_wins([]) == []

    def test_critical_dead_code_is_quick_win(self, reviewer: _ConcreteReviewer):
        issues = [{"file_path": "/path/to/file.py", "line_number": 10, "severity": "critical"}]
        wins = reviewer._identify_quick_wins(issues)
        assert len(wins) == 1
        assert wins[0]["type"] == "dead_code_cleanup"
        assert wins[0]["effort"] == "low"
        assert wins[0]["impact"] == "high"

    def test_warning_dead_code_not_quick_win(self, reviewer: _ConcreteReviewer):
        issues = [{"file_path": "file.py", "line_number": 1, "severity": "warning"}]
        assert reviewer._identify_quick_wins(issues) == []


@pytest.mark.unit
class TestIdentifyLongTermImprovements:
    """Test the _identify_long_term_improvements helper."""

    def test_low_risk_no_improvements(self, reviewer: _ConcreteReviewer):
        data = {"high_risk_count": 5}
        assert reviewer._identify_long_term_improvements(data) == []

    def test_high_risk_generates_improvement(self, reviewer: _ConcreteReviewer):
        data = {"high_risk_count": 15}
        improvements = reviewer._identify_long_term_improvements(data)
        assert len(improvements) == 1
        assert improvements[0]["type"] == "architecture_refactoring"

    def test_exact_threshold_no_improvement(self, reviewer: _ConcreteReviewer):
        data = {"high_risk_count": 10}
        assert reviewer._identify_long_term_improvements(data) == []

    def test_missing_key_no_improvement(self, reviewer: _ConcreteReviewer):
        assert reviewer._identify_long_term_improvements({}) == []


@pytest.mark.unit
class TestSuggestProperName:
    """Test the _suggest_proper_name helper."""

    def test_already_correct(self, reviewer: _ConcreteReviewer):
        assert reviewer._suggest_proper_name("test_example.py") == "test_example.py"

    def test_test_suffix_converted(self, reviewer: _ConcreteReviewer):
        # The first branch catches any name containing 'test' that lacks the prefix,
        # so "example_test.py" becomes "test_example_test.py" (prepend only).
        result = reviewer._suggest_proper_name("example_test.py")
        assert result == "test_example_test.py"

    def test_no_test_in_name(self, reviewer: _ConcreteReviewer):
        assert reviewer._suggest_proper_name("utils.py") == "utils.py"

    def test_test_in_middle(self, reviewer: _ConcreteReviewer):
        result = reviewer._suggest_proper_name("my_test_helper.py")
        # Contains 'test' but starts with it after prefix
        assert result == "test_my_test_helper.py"


@pytest.mark.unit
class TestCountTotalFiles:
    """Test the _count_total_files method with real filesystem."""

    def test_counts_python_files(self, small_project: Path):
        rev = _ConcreteReviewer(project_root=str(small_project))
        count = rev._count_total_files()
        # __init__.py + main.py + utils.py = 3
        assert count == 3

    def test_empty_directory(self, tmp_path: Path):
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        assert rev._count_total_files() == 0

    def test_skips_pycache(self, tmp_path: Path):
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "module.cpython-312.pyc").write_text("bytecode", encoding="utf-8")
        # Also put a .py in there to prove it's skipped
        (cache_dir / "leftover.py").write_text("# leftover", encoding="utf-8")
        (tmp_path / "real.py").write_text("x = 1\n", encoding="utf-8")
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        assert rev._count_total_files() == 1


@pytest.mark.unit
class TestCountTotalLines:
    """Test the _count_total_lines method with real filesystem."""

    def test_counts_lines(self, small_project: Path):
        rev = _ConcreteReviewer(project_root=str(small_project))
        total = rev._count_total_lines()
        assert total > 0

    def test_empty_directory(self, tmp_path: Path):
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        assert rev._count_total_lines() == 0


@pytest.mark.unit
class TestGetComplexityMetrics:
    """Test _get_complexity_metrics with controlled analyzer data."""

    def test_empty_results(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(complexity_results=[]),
        )
        metrics = rev._get_complexity_metrics()
        assert metrics["total_functions"] == 0
        assert metrics["score"] == 100.0

    def test_single_low_complexity(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[{"name": "f", "complexity": 3}]
            ),
        )
        metrics = rev._get_complexity_metrics()
        assert metrics["total_functions"] == 1
        assert metrics["average_complexity"] == 3.0
        assert metrics["high_risk_count"] == 0
        assert metrics["score"] > 90.0

    def test_high_risk_functions(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[
                    {"name": "f1", "complexity": 20},
                    {"name": "f2", "complexity": 25},
                ]
            ),
        )
        metrics = rev._get_complexity_metrics()
        assert metrics["high_risk_count"] == 2
        assert metrics["score"] < 80.0

    def test_analyzer_error_returns_zeros(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        metrics = rev._get_complexity_metrics()
        assert metrics["total_functions"] == 0
        assert metrics["score"] == 0.0


@pytest.mark.unit
class TestGetDeadCodeMetrics:
    """Test _get_dead_code_metrics with controlled analyzer data."""

    def test_no_dead_code(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(dead_code_results=[]),
        )
        metrics = rev._get_dead_code_metrics()
        assert metrics["total_findings"] == 0
        assert metrics["score"] == 100.0

    def test_critical_findings(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(
                dead_code_results=[
                    {"severity": "critical"},
                    {"severity": "critical"},
                    {"severity": "warning"},
                ]
            ),
        )
        metrics = rev._get_dead_code_metrics()
        assert metrics["total_findings"] == 3
        assert metrics["critical_count"] == 2
        assert metrics["warning_count"] == 1
        # 100 - 20 (2 critical * 10) - 2 (1 warning * 2) = 78
        assert abs(metrics["score"] - 78.0) < 0.01

    def test_analyzer_error(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        metrics = rev._get_dead_code_metrics()
        assert metrics["score"] == 0.0


@pytest.mark.unit
class TestGetCouplingMetrics:
    """Test _get_coupling_metrics with controlled analyzer data."""

    def test_no_coupling_data(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(coupling_results=[]),
        )
        metrics = rev._get_coupling_metrics()
        assert metrics["total_classes"] == 0
        assert metrics["score"] == 100.0

    def test_high_coupling(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(
                coupling_results=[
                    {"name": "A", "coupling": 15},
                    {"name": "B", "coupling": 5},
                ]
            ),
        )
        metrics = rev._get_coupling_metrics()
        assert metrics["total_classes"] == 2
        assert metrics["high_coupling_count"] == 1  # only A > 10
        assert metrics["average_coupling"] == 10.0

    def test_analyzer_error(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        metrics = rev._get_coupling_metrics()
        assert metrics["score"] == 0.0


@pytest.mark.unit
class TestGetArchitectureMetrics:
    """Test _get_architecture_metrics."""

    def test_no_violations(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            architecture_violations=[],
        )
        metrics = rev._get_architecture_metrics()
        assert metrics["total_violations"] == 0
        assert metrics["score"] == 100.0

    def test_mixed_severity_violations(self, tmp_path: Path):
        violations = [
            ArchitectureViolation(
                file_path="a.py", violation_type="circular", description="circ",
                severity="high", suggestion="fix it",
            ),
            ArchitectureViolation(
                file_path="b.py", violation_type="naming", description="bad name",
                severity="medium", suggestion="rename",
            ),
            ArchitectureViolation(
                file_path="c.py", violation_type="style", description="minor",
                severity="low", suggestion="minor fix",
            ),
        ]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            architecture_violations=violations,
        )
        metrics = rev._get_architecture_metrics()
        assert metrics["total_violations"] == 3
        assert metrics["high_severity_violations"] == 1
        assert metrics["medium_severity_violations"] == 1
        assert metrics["low_severity_violations"] == 1
        # 100 - 15 (1 high * 15) - 5 (1 medium * 5) - 1 (1 low * 1) = 79
        assert abs(metrics["score"] - 79.0) < 0.01


@pytest.mark.unit
class TestGetDuplicationMetrics:
    """Test _get_duplication_metrics with real filesystem + stub analyzer."""

    def test_no_python_files(self, tmp_path: Path):
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        metrics = rev._get_duplication_metrics()
        assert metrics["total_groups"] == 0
        assert metrics["score"] == 100.0

    def test_no_clones_found(self, small_project: Path):
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(clone_groups=[]),
        )
        metrics = rev._get_duplication_metrics()
        assert metrics["score"] == 100.0

    def test_clones_found(self, small_project: Path):
        clone_groups = [
            {
                "instances": [
                    {"file_path": "a.py", "start_line": 1, "end_line": 10},
                    {"file_path": "b.py", "start_line": 5, "end_line": 14},
                ]
            }
        ]
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(clone_groups=clone_groups),
        )
        metrics = rev._get_duplication_metrics()
        assert metrics["total_groups"] == 1
        assert metrics["duplicated_lines"] == 10  # second instance: 14 - 5 + 1

    def test_analyzer_error(self, small_project: Path):
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        metrics = rev._get_duplication_metrics()
        # Error path returns score 100.0
        assert metrics["score"] == 100.0


@pytest.mark.unit
class TestTopIssues:
    """Test _get_top_complexity_issues, _get_top_dead_code_issues, _get_top_duplication_issues."""

    def test_top_complexity_sorted(self, tmp_path: Path):
        funcs = [
            {"name": "a", "complexity": 5, "file_path": "x.py", "line_number": 1},
            {"name": "b", "complexity": 30, "file_path": "y.py", "line_number": 10},
            {"name": "c", "complexity": 15, "file_path": "z.py", "line_number": 20},
        ]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(complexity_results=funcs),
        )
        top = rev._get_top_complexity_issues()
        assert top[0]["complexity"] == 30
        assert top[1]["complexity"] == 15
        assert len(top) == 3

    def test_top_complexity_limits_to_five(self, tmp_path: Path):
        funcs = [{"name": f"f{i}", "complexity": i, "file_path": "f.py", "line_number": i} for i in range(10)]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(complexity_results=funcs),
        )
        assert len(rev._get_top_complexity_issues()) == 5

    def test_top_dead_code_sorted_by_severity(self, tmp_path: Path):
        findings = [
            {"severity": "info", "location": {"file_path": "a.py", "start_line": 1}, "reason": "r1"},
            {"severity": "critical", "location": {"file_path": "b.py", "start_line": 2}, "reason": "r2"},
            {"severity": "warning", "location": {"file_path": "c.py", "start_line": 3}, "reason": "r3"},
        ]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(dead_code_results=findings),
        )
        top = rev._get_top_dead_code_issues()
        assert top[0]["severity"] == "critical"
        assert top[1]["severity"] == "warning"

    def test_top_duplication_empty(self, tmp_path: Path):
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        # No python files => empty
        assert rev._get_top_duplication_issues() == []

    def test_top_duplication_with_clones(self, small_project: Path):
        clone_groups = [
            {
                "similarity": 0.95,
                "instances": [
                    {"file_path": "a.py", "start_line": 1, "end_line": 20},
                    {"file_path": "b.py", "start_line": 1, "end_line": 20},
                ],
            }
        ]
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(clone_groups=clone_groups),
        )
        top = rev._get_top_duplication_issues()
        assert len(top) == 1
        assert top[0]["clone_count"] == 2

    def test_top_complexity_analyzer_error(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._get_top_complexity_issues() == []

    def test_top_dead_code_analyzer_error(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._get_top_dead_code_issues() == []


@pytest.mark.unit
class TestCalculateScores:
    """Test _calculate_maintainability_score, _calculate_testability_score,
    _calculate_reliability_score, _calculate_security_score,
    _calculate_performance_score -- all with controlled data."""

    def test_maintainability_no_data(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(),
        )
        score = rev._calculate_maintainability_score()
        assert score == 100.0  # no data => base 100 minus 0 penalties

    def test_maintainability_with_complexity(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[{"complexity": 12}, {"complexity": 8}],
                coupling_results=[{"coupling": 4}],
            ),
        )
        score = rev._calculate_maintainability_score()
        assert 0.0 <= score <= 100.0

    def test_maintainability_error(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._calculate_maintainability_score() == 50.0

    def test_testability_no_data(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(),
        )
        assert rev._calculate_testability_score() == 75.0

    def test_testability_with_hard_functions(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[
                    {"complexity": 30},  # very hard to test
                    {"complexity": 18},  # hard to test
                    {"complexity": 3},
                ],
                coupling_results=[{"coupling": 12}],
            ),
        )
        score = rev._calculate_testability_score()
        assert 0.0 <= score <= 100.0
        assert score < 75.0  # should be penalized

    def test_testability_error(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._calculate_testability_score() == 50.0

    def test_reliability_no_dead_code(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(dead_code_results=[]),
        )
        assert rev._calculate_reliability_score() == 95.0

    def test_reliability_with_dead_code(self, small_project: Path):
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(
                dead_code_results=[
                    {"severity": "critical"},
                    {"severity": "warning"},
                ]
            ),
        )
        score = rev._calculate_reliability_score()
        assert 0.0 <= score <= 100.0

    def test_reliability_error(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._calculate_reliability_score() == 50.0

    def test_security_clean_project(self, tmp_path: Path):
        (tmp_path / "clean.py").write_text("x = 1 + 2\n", encoding="utf-8")
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        score = rev._calculate_security_score()
        assert score >= 90.0

    def test_security_dangerous_project(self, security_project: Path):
        rev = _ConcreteReviewer(project_root=str(security_project))
        score = rev._calculate_security_score()
        assert score < 100.0

    def test_security_error(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        # security_score doesn't call pyscn, so it won't error from that;
        # exercise with empty dir
        score = rev._calculate_security_score()
        assert 0.0 <= score <= 100.0

    def test_performance_no_data(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(),
        )
        assert rev._calculate_performance_score() == 80.0

    def test_performance_with_complexity(self, small_project: Path):
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[{"complexity": 5}, {"complexity": 8}]
            ),
        )
        score = rev._calculate_performance_score()
        assert 0.0 <= score <= 100.0

    def test_performance_error(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._calculate_performance_score() == 50.0


@pytest.mark.unit
class TestDetectCodeSmells:
    """Test detect_code_smells and its sub-detectors."""

    def test_no_smells_clean_data(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[{"name": "f", "complexity": 3, "file_path": "a.py", "line_number": 1}],
                coupling_results=[{"name": "C", "coupling": 2, "file_path": "a.py"}],
            ),
        )
        smells = rev.detect_code_smells()
        assert isinstance(smells, list)
        # No high-complexity or high-coupling => no smells from those detectors
        long_methods = [s for s in smells if s["type"] == "long_method"]
        large_classes = [s for s in smells if s["type"] == "large_class"]
        assert len(long_methods) == 0
        assert len(large_classes) == 0

    def test_long_method_detected(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[
                    {"name": "huge_func", "complexity": 25, "file_path": "big.py", "line_number": 1}
                ],
            ),
        )
        smells = rev.detect_code_smells()
        long_methods = [s for s in smells if s["type"] == "long_method"]
        assert len(long_methods) == 1
        assert long_methods[0]["function_name"] == "huge_func"

    def test_large_class_detected(self, tmp_path: Path):
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(
                coupling_results=[
                    {"name": "GodClass", "coupling": 20, "file_path": "god.py"}
                ],
            ),
        )
        smells = rev.detect_code_smells()
        large_classes = [s for s in smells if s["type"] == "large_class"]
        assert len(large_classes) == 1
        assert large_classes[0]["class_name"] == "GodClass"

    def test_feature_envy_returns_empty(self, reviewer: _ConcreteReviewer):
        assert reviewer._detect_feature_envy() == []

    def test_data_clumps_returns_empty(self, reviewer: _ConcreteReviewer):
        assert reviewer._detect_data_clumps() == []

    def test_primitive_obsession_returns_empty(self, reviewer: _ConcreteReviewer):
        assert reviewer._detect_primitive_obsession() == []


@pytest.mark.unit
class TestSuggestAutomatedFixes:
    """Test suggest_automated_fixes."""

    def test_no_fixes_when_clean(self, tmp_path: Path):
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        fixes = rev.suggest_automated_fixes()
        assert isinstance(fixes, dict)
        assert "dead_code_removal" in fixes
        assert "naming_convention_fixes" in fixes

    def test_dead_code_fix_suggested(self, tmp_path: Path):
        dead_findings = [
            DeadCodeFinding(
                file_path="x.py", line_number=5, code_snippet="pass",
                reason="unused", severity="critical", suggestion="remove it",
                fix_available=True,
            )
        ]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            dead_code_findings=dead_findings,
        )
        fixes = rev.suggest_automated_fixes()
        assert len(fixes["dead_code_removal"]) == 1
        assert fixes["dead_code_removal"][0]["confidence"] == 0.95

    def test_naming_convention_fix(self, tmp_path: Path):
        violations = [
            ArchitectureViolation(
                file_path="my_test_file.py", violation_type="naming_convention",
                description="bad name", severity="medium", suggestion="rename",
            )
        ]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            architecture_violations=violations,
        )
        fixes = rev.suggest_automated_fixes()
        assert len(fixes["naming_convention_fixes"]) == 1


@pytest.mark.unit
class TestAnalyzeTechnicalDebt:
    """Test analyze_technical_debt."""

    def test_zero_debt(self, tmp_path: Path):
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        debt = rev.analyze_technical_debt()
        assert debt["total_debt_hours"] == 0

    def test_debt_from_complexity(self, tmp_path: Path):
        suggestions = [
            ComplexityReductionSuggestion(
                function_name="big", file_path="a.py", current_complexity=20,
                suggested_refactoring="split it", estimated_effort="high", benefits=["clarity"],
            )
        ]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            complexity_suggestions=suggestions,
        )
        debt = rev.analyze_technical_debt()
        assert debt["debt_by_category"]["complexity"] == 4  # 1 suggestion * 4 hours

    def test_debt_from_dead_code(self, tmp_path: Path):
        findings = [
            DeadCodeFinding(
                file_path="b.py", line_number=10, code_snippet="x=1",
                reason="unused", severity="critical", suggestion="remove",
            )
        ]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            dead_code_findings=findings,
        )
        debt = rev.analyze_technical_debt()
        assert debt["debt_by_category"]["dead_code"] == 1

    def test_debt_from_architecture(self, tmp_path: Path):
        violations = [
            ArchitectureViolation(
                file_path="c.py", violation_type="circular",
                description="circular dep", severity="high", suggestion="refactor",
            )
        ]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            architecture_violations=violations,
        )
        debt = rev.analyze_technical_debt()
        assert debt["debt_by_category"]["architecture"] == 8

    def test_top_debt_items_sorted(self, tmp_path: Path):
        suggestions = [
            ComplexityReductionSuggestion(
                function_name="f1", file_path="a.py", current_complexity=30,
                suggested_refactoring="split", estimated_effort="high", benefits=[],
            )
        ]
        violations = [
            ArchitectureViolation(
                file_path="b.py", violation_type="circular",
                description="dep", severity="high", suggestion="fix",
            )
        ]
        findings = [
            DeadCodeFinding(
                file_path="c.py", line_number=1, code_snippet="x",
                reason="unused", severity="critical", suggestion="rm",
            )
        ]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            complexity_suggestions=suggestions,
            architecture_violations=violations,
            dead_code_findings=findings,
        )
        debt = rev.analyze_technical_debt()
        items = debt["top_debt_items"]
        assert len(items) == 3
        # Architecture items (8h) should come first
        assert items[0]["estimated_hours"] == 8


@pytest.mark.unit
class TestGenerateQualityDashboard:
    """Integration-style test for the full generate_quality_dashboard method."""

    def test_generates_dashboard_object(self, small_project: Path):
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[{"name": "f", "complexity": 5, "file_path": "m.py", "line_number": 1}],
            ),
        )
        dashboard = rev.generate_quality_dashboard()
        assert isinstance(dashboard, QualityDashboard)
        assert 0.0 <= dashboard.overall_score <= 100.0
        assert dashboard.grade in {"A", "B", "C", "D", "F"}
        assert dashboard.total_files >= 0
        assert dashboard.analysis_timestamp  # non-empty string
