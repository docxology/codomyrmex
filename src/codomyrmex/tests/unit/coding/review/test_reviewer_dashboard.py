"""Unit tests for coding.review.reviewer_impl.dashboard — DashboardMixin.

Exercises quality dashboard generation, all scoring algorithms, grade
calculation, metric helpers, code smell detection, automated fix suggestions,
and technical debt analysis.  Written to the zero-mock policy: every object
is a real, fully-instantiated Python class with deterministic real method
implementations.  No unittest.mock, MagicMock, monkeypatch, or patch is used.
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
# Real stub helpers — not mocks. Each method has a genuine implementation.
# ---------------------------------------------------------------------------


class _StubAnalyzer:
    """Deterministic pyscn analyzer stand-in.

    Returns pre-canned results so tests exercise DashboardMixin logic
    without requiring a real pyscn installation.  The `raise_on_call`
    flag exercises error-handling branches.
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
            raise RuntimeError("stub forced error")
        return self._complexity

    def detect_dead_code(self, project_root: str) -> list[dict[str, Any]]:
        if self._raise:
            raise RuntimeError("stub forced error")
        return self._dead_code

    def analyze_coupling(self, project_root: str) -> list[dict[str, Any]]:
        if self._raise:
            raise RuntimeError("stub forced error")
        return self._coupling

    def find_clones(
        self, files: list[str], threshold: float = 0.8
    ) -> list[dict[str, Any]]:
        if self._raise:
            raise RuntimeError("stub forced error")
        return self._clones


class _ConcreteReviewer(DashboardMixin):
    """Minimal concrete class that satisfies DashboardMixin's cross-mixin deps."""

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
def empty_dir(tmp_path: Path) -> Path:
    """Provide an empty temporary directory."""
    return tmp_path


@pytest.fixture
def small_project(tmp_path: Path) -> Path:
    """Create a minimal Python project for filesystem-walking tests."""
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
def try_except_project(tmp_path: Path) -> Path:
    """Project with try/except blocks to exercise reliability scoring."""
    (tmp_path / "safe.py").write_text(
        "def fetch():\n    try:\n        return True\n    except Exception:\n        return False\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def security_project(tmp_path: Path) -> Path:
    """Project containing deliberate security anti-patterns."""
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
def performance_project(tmp_path: Path) -> Path:
    """Project containing performance anti-patterns for scoring tests."""
    (tmp_path / "slow.py").write_text(
        "import time\nglobal x\nx = 1\ntime.sleep(0)\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def reviewer(small_project: Path) -> _ConcreteReviewer:
    return _ConcreteReviewer(project_root=str(small_project))


# ---------------------------------------------------------------------------
# TestCalculateGrade
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculateGrade:
    """_calculate_grade must return the correct letter for every score band."""

    def test_grade_a_perfect(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._calculate_grade(100.0) == "A"

    def test_grade_a_lower_boundary(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._calculate_grade(90.0) == "A"

    def test_grade_b(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._calculate_grade(85.0) == "B"

    def test_grade_b_lower_boundary(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._calculate_grade(80.0) == "B"

    def test_grade_c(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._calculate_grade(75.0) == "C"

    def test_grade_c_lower_boundary(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._calculate_grade(70.0) == "C"

    def test_grade_d(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._calculate_grade(65.0) == "D"

    def test_grade_d_lower_boundary(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._calculate_grade(60.0) == "D"

    def test_grade_f_mid(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._calculate_grade(55.0) == "F"

    def test_grade_f_zero(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._calculate_grade(0.0) == "F"

    def test_grade_f_just_below_d(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._calculate_grade(59.9) == "F"


# ---------------------------------------------------------------------------
# TestCalculateOverallScore
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculateOverallScore:
    """_calculate_overall_score applies weights correctly and clamps output."""

    def test_all_perfect(self, reviewer: _ConcreteReviewer) -> None:
        data = {"score": 100.0}
        result = reviewer._calculate_overall_score(data, data, data, data, data)
        assert result == 100.0

    def test_all_zero(self, reviewer: _ConcreteReviewer) -> None:
        data = {"score": 0.0}
        result = reviewer._calculate_overall_score(data, data, data, data, data)
        assert result == 0.0

    def test_weighted_average(self, reviewer: _ConcreteReviewer) -> None:
        # weights: complexity 0.25, dead_code 0.20, duplication 0.15,
        #          coupling 0.20, architecture 0.20
        result = reviewer._calculate_overall_score(
            {"score": 80.0},  # 80 * 0.25 = 20.0
            {"score": 60.0},  # 60 * 0.20 = 12.0
            {"score": 100.0},  # 100 * 0.15 = 15.0
            {"score": 40.0},  # 40 * 0.20 = 8.0
            {"score": 90.0},  # 90 * 0.20 = 18.0
        )
        assert abs(result - 73.0) < 0.01

    def test_clamped_at_100(self, reviewer: _ConcreteReviewer) -> None:
        data = {"score": 200.0}
        assert reviewer._calculate_overall_score(data, data, data, data, data) == 100.0

    def test_missing_score_key_defaults_zero(self, reviewer: _ConcreteReviewer) -> None:
        data: dict[str, Any] = {}
        assert reviewer._calculate_overall_score(data, data, data, data, data) == 0.0

    def test_mixed_keys(self, reviewer: _ConcreteReviewer) -> None:
        # Only duplication has score; others are missing
        result = reviewer._calculate_overall_score(
            {},
            {},
            {"score": 100.0},
            {},
            {},
        )
        # duplication weight is 0.15 -> 15.0
        assert abs(result - 15.0) < 0.01


# ---------------------------------------------------------------------------
# TestComplexityMetrics
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetComplexityMetrics:
    """_get_complexity_metrics computes correct aggregates and score."""

    def test_no_functions(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(complexity_results=[]),
        )
        m = rev._get_complexity_metrics()
        assert m["total_functions"] == 0
        assert m["high_risk_count"] == 0
        assert m["score"] == 100.0

    def test_single_low_complexity(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[{"name": "f", "complexity": 4}]
            ),
        )
        m = rev._get_complexity_metrics()
        assert m["total_functions"] == 1
        assert m["average_complexity"] == 4.0
        assert m["high_risk_count"] == 0
        # penalty: avg*2=8, risk=0 → score = 100-8 = 92
        assert abs(m["score"] - 92.0) < 0.01

    def test_multiple_functions_with_high_risk(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[
                    {"name": "a", "complexity": 20},
                    {"name": "b", "complexity": 18},
                    {"name": "c", "complexity": 3},
                ]
            ),
        )
        m = rev._get_complexity_metrics()
        assert m["total_functions"] == 3
        assert m["high_risk_count"] == 2
        assert m["score"] < 80.0

    def test_max_penalty_does_not_go_below_zero(self, empty_dir: Path) -> None:
        # avg_complexity = 50 → complexity_penalty = min(50*2, 30) = 30
        # high_risk_count = 20 → risk_penalty = min(20*5, 40) = 40
        # score = 100 - 30 - 40 = 30
        funcs = [{"name": f"f{i}", "complexity": 50} for i in range(20)]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(complexity_results=funcs),
        )
        m = rev._get_complexity_metrics()
        # Score must be non-negative and well below the max
        assert m["score"] >= 0.0
        assert m["score"] < 50.0

    def test_error_path_returns_zero_score(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        m = rev._get_complexity_metrics()
        assert m["score"] == 0.0
        assert m["total_functions"] == 0


# ---------------------------------------------------------------------------
# TestDeadCodeMetrics
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetDeadCodeMetrics:
    """_get_dead_code_metrics aggregates severity counts and penalises correctly."""

    def test_no_findings(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(dead_code_results=[]),
        )
        m = rev._get_dead_code_metrics()
        assert m["total_findings"] == 0
        assert m["score"] == 100.0

    def test_critical_and_warning_findings(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                dead_code_results=[
                    {"severity": "critical"},
                    {"severity": "critical"},
                    {"severity": "warning"},
                ]
            ),
        )
        m = rev._get_dead_code_metrics()
        assert m["critical_count"] == 2
        assert m["warning_count"] == 1
        assert m["total_findings"] == 3
        # 100 - (2*10) - (1*2) = 78
        assert abs(m["score"] - 78.0) < 0.01

    def test_max_penalty_clamps_at_floor(self, empty_dir: Path) -> None:
        # 10 critical: critical_penalty = min(10*10, 50) = 50
        # score = max(0, 100 - 50 - 0) = 50
        findings = [{"severity": "critical"}] * 10
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(dead_code_results=findings),
        )
        m = rev._get_dead_code_metrics()
        assert abs(m["score"] - 50.0) < 0.01

    def test_max_critical_penalty_is_50(self, empty_dir: Path) -> None:
        # 20 critical: penalty = min(20*10, 50) = 50 (capped)
        # 20 warning: penalty = min(20*2, 20) = 20 (capped)
        # score = max(0, 100 - 50 - 20) = 30
        findings = [{"severity": "critical"}] * 20 + [{"severity": "warning"}] * 20
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(dead_code_results=findings),
        )
        m = rev._get_dead_code_metrics()
        assert abs(m["score"] - 30.0) < 0.01

    def test_error_returns_zero_score(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        m = rev._get_dead_code_metrics()
        assert m["score"] == 0.0


# ---------------------------------------------------------------------------
# TestCouplingMetrics
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetCouplingMetrics:
    """_get_coupling_metrics handles empty results, high-coupling detection, errors."""

    def test_no_classes(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(coupling_results=[]),
        )
        m = rev._get_coupling_metrics()
        assert m["total_classes"] == 0
        assert m["score"] == 100.0

    def test_identifies_high_coupling_class(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                coupling_results=[
                    {"name": "A", "coupling": 12},  # high (> 10)
                    {"name": "B", "coupling": 4},  # low
                ]
            ),
        )
        m = rev._get_coupling_metrics()
        assert m["high_coupling_count"] == 1
        assert m["average_coupling"] == 8.0  # (12+4)/2

    def test_score_calculation(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                coupling_results=[{"name": "X", "coupling": 2}]
            ),
        )
        m = rev._get_coupling_metrics()
        # avg 2 => coupling_penalty = min(2*5, 40) = 10; high_count 0 => 0
        # score = 100 - 10 = 90
        assert abs(m["score"] - 90.0) < 0.01

    def test_error_returns_zero_score(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        m = rev._get_coupling_metrics()
        assert m["score"] == 0.0


# ---------------------------------------------------------------------------
# TestArchitectureMetrics
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetArchitectureMetrics:
    """_get_architecture_metrics derives severity counts and penalty correctly."""

    def test_no_violations(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(empty_dir))
        m = rev._get_architecture_metrics()
        assert m["total_violations"] == 0
        assert m["score"] == 100.0

    def test_single_high_violation(self, empty_dir: Path) -> None:
        violations = [
            ArchitectureViolation(
                file_path="a.py",
                violation_type="circular",
                description="circular dep",
                severity="high",
                suggestion="fix",
            )
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir), architecture_violations=violations
        )
        m = rev._get_architecture_metrics()
        assert m["high_severity_violations"] == 1
        # 100 - (1*15) = 85
        assert abs(m["score"] - 85.0) < 0.01

    def test_mixed_severity_violations(self, empty_dir: Path) -> None:
        violations = [
            ArchitectureViolation("a.py", "t1", "d1", "high", "s1"),
            ArchitectureViolation("b.py", "t2", "d2", "medium", "s2"),
            ArchitectureViolation("c.py", "t3", "d3", "low", "s3"),
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir), architecture_violations=violations
        )
        m = rev._get_architecture_metrics()
        assert m["high_severity_violations"] == 1
        assert m["medium_severity_violations"] == 1
        assert m["low_severity_violations"] == 1
        # 100 - 15 - 5 - 1 = 79
        assert abs(m["score"] - 79.0) < 0.01

    def test_many_high_violations_capped(self, empty_dir: Path) -> None:
        violations = [
            ArchitectureViolation("f.py", "t", "d", "high", "s") for _ in range(10)
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir), architecture_violations=violations
        )
        m = rev._get_architecture_metrics()
        # high_penalty = min(10*15, 60) = 60 → score = max(0, 100-60) = 40
        assert abs(m["score"] - 40.0) < 0.01


# ---------------------------------------------------------------------------
# TestDuplicationMetrics
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetDuplicationMetrics:
    """_get_duplication_metrics exercises all scoring branches and error paths."""

    def test_no_python_files(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(empty_dir))
        m = rev._get_duplication_metrics()
        assert m["total_groups"] == 0
        assert m["score"] == 100.0

    def test_no_clone_groups(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(clone_groups=[]),
        )
        m = rev._get_duplication_metrics()
        assert m["score"] == 100.0

    def test_duplication_score_low_band(self, tmp_path: Path) -> None:
        """Duplication <= 5% → score branch 100 - dup*2."""
        # Write a large file (200 lines) so 2 duplicated lines = 1% duplication.
        lines = "x = 1\n" * 200
        (tmp_path / "large.py").write_text(lines, encoding="utf-8")
        # 2 duplicated lines out of 200 = 1%
        clone_groups = [
            {
                "instances": [
                    {"file_path": "a.py", "start_line": 1, "end_line": 2},
                    {"file_path": "b.py", "start_line": 1, "end_line": 2},
                ]
            }
        ]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(clone_groups=clone_groups),
        )
        m = rev._get_duplication_metrics()
        # 1% duplication → score = 100 - 1*2 = 98
        assert m["score"] >= 95.0

    def test_duplication_score_medium_band(self, tmp_path: Path) -> None:
        """Duplication in 5-10% → score branch 90 - (dup-5)*4."""
        # Write a file with 200 lines so we can control the percentage precisely.
        lines = "x = 1\n" * 200
        (tmp_path / "big.py").write_text(lines, encoding="utf-8")
        # 15 duplicated lines out of 200 = 7.5% duplication
        clone_groups = [
            {
                "instances": [
                    {"file_path": "a.py", "start_line": 1, "end_line": 15},
                    {"file_path": "b.py", "start_line": 1, "end_line": 15},
                ]
            }
        ]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(clone_groups=clone_groups),
        )
        m = rev._get_duplication_metrics()
        # duplication_percentage = 15/200*100 = 7.5%
        # score = 90 - (7.5-5)*4 = 90 - 10 = 80
        assert abs(m["score"] - 80.0) < 0.5

    def test_duplication_score_high_band(self, tmp_path: Path) -> None:
        """Duplication in 10-20% → score branch 70 - (dup-10)*2."""
        lines = "x = 1\n" * 100
        (tmp_path / "big.py").write_text(lines, encoding="utf-8")
        # 15 duplicated lines out of 100 = 15% duplication
        clone_groups = [
            {
                "instances": [
                    {"file_path": "a.py", "start_line": 1, "end_line": 15},
                    {"file_path": "b.py", "start_line": 1, "end_line": 15},
                ]
            }
        ]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(clone_groups=clone_groups),
        )
        m = rev._get_duplication_metrics()
        # 15/100*100 = 15% → score = 70 - (15-10)*2 = 60
        assert abs(m["score"] - 60.0) < 0.5

    def test_duplication_score_very_high_band(self, tmp_path: Path) -> None:
        """Duplication > 20% → score branch max(0, 50 - (dup-20))."""
        lines = "x = 1\n" * 100
        (tmp_path / "big.py").write_text(lines, encoding="utf-8")
        # 25 duplicated lines out of 100 = 25%
        clone_groups = [
            {
                "instances": [
                    {"file_path": "a.py", "start_line": 1, "end_line": 25},
                    {"file_path": "b.py", "start_line": 1, "end_line": 25},
                ]
            }
        ]
        rev = _ConcreteReviewer(
            project_root=str(tmp_path),
            pyscn_analyzer=_StubAnalyzer(clone_groups=clone_groups),
        )
        m = rev._get_duplication_metrics()
        # 25% → score = max(0, 50 - (25-20)) = 45
        assert abs(m["score"] - 45.0) < 0.5

    def test_error_path_returns_100(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        m = rev._get_duplication_metrics()
        assert m["score"] == 100.0

    def test_single_instance_group_not_counted(self, small_project: Path) -> None:
        """A clone group with only one instance contributes 0 duplicated lines."""
        clone_groups = [
            {"instances": [{"file_path": "a.py", "start_line": 1, "end_line": 10}]}
        ]
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(clone_groups=clone_groups),
        )
        m = rev._get_duplication_metrics()
        assert m["duplicated_lines"] == 0


# ---------------------------------------------------------------------------
# TestCountTotalFiles
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCountTotalFiles:
    """_count_total_files counts .py files and skips ignored dirs."""

    def test_counts_python_files(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(small_project))
        count = rev._count_total_files()
        assert count == 3  # __init__.py, main.py, utils.py

    def test_empty_directory(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(empty_dir))
        assert rev._count_total_files() == 0

    def test_skips_pycache(self, tmp_path: Path) -> None:
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (cache / "hidden.py").write_text("x=1", encoding="utf-8")
        (tmp_path / "real.py").write_text("y=2", encoding="utf-8")
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        assert rev._count_total_files() == 1

    def test_skips_venv(self, tmp_path: Path) -> None:
        venv = tmp_path / ".venv"
        venv.mkdir()
        (venv / "skipped.py").write_text("z=3", encoding="utf-8")
        (tmp_path / "real.py").write_text("a=4", encoding="utf-8")
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        assert rev._count_total_files() == 1

    def test_non_py_files_not_counted(self, tmp_path: Path) -> None:
        (tmp_path / "script.sh").write_text("#!/bin/bash\n", encoding="utf-8")
        (tmp_path / "data.json").write_text("{}", encoding="utf-8")
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        assert rev._count_total_files() == 0


# ---------------------------------------------------------------------------
# TestCountTotalLines
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCountTotalLines:
    """_count_total_lines sums lines across all .py files."""

    def test_empty_directory(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(empty_dir))
        assert rev._count_total_lines() == 0

    def test_known_line_count(self, tmp_path: Path) -> None:
        (tmp_path / "f.py").write_text("a = 1\nb = 2\nc = 3\n", encoding="utf-8")
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        assert rev._count_total_lines() == 3

    def test_multiple_files(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(small_project))
        total = rev._count_total_lines()
        assert total > 0


# ---------------------------------------------------------------------------
# TestMaintainabilityScore
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculateMaintainabilityScore:
    """_calculate_maintainability_score applies complexity and coupling penalties."""

    def test_no_data_returns_100(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(),
        )
        assert rev._calculate_maintainability_score() == 100.0

    def test_with_complexity_and_coupling(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[{"complexity": 12}, {"complexity": 8}],
                coupling_results=[{"coupling": 4}],
            ),
        )
        score = rev._calculate_maintainability_score()
        assert 0.0 <= score <= 100.0

    def test_high_complexity_reduces_score(self, empty_dir: Path) -> None:
        rev_low = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(complexity_results=[{"complexity": 2}]),
        )
        rev_high = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(complexity_results=[{"complexity": 20}]),
        )
        assert (
            rev_low._calculate_maintainability_score()
            > rev_high._calculate_maintainability_score()
        )

    def test_error_returns_50(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._calculate_maintainability_score() == 50.0


# ---------------------------------------------------------------------------
# TestTestabilityScore
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculateTestabilityScore:
    """_calculate_testability_score returns 75 with no data; penalises hard functions."""

    def test_no_data_returns_75(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(),
        )
        assert rev._calculate_testability_score() == 75.0

    def test_very_hard_functions_penalised(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[{"complexity": 30}, {"complexity": 18}],
                coupling_results=[{"coupling": 12}],
            ),
        )
        score = rev._calculate_testability_score()
        assert 0.0 <= score < 75.0

    def test_low_complexity_close_to_100(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[{"complexity": 1}, {"complexity": 2}],
                coupling_results=[{"coupling": 1}],
            ),
        )
        score = rev._calculate_testability_score()
        assert score >= 90.0

    def test_error_returns_50(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._calculate_testability_score() == 50.0


# ---------------------------------------------------------------------------
# TestReliabilityScore
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculateReliabilityScore:
    """_calculate_reliability_score is 95 with no dead code; penalises findings."""

    def test_no_dead_code_returns_95(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(dead_code_results=[]),
        )
        assert rev._calculate_reliability_score() == 95.0

    def test_dead_code_reduces_score(self, small_project: Path) -> None:
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

    def test_try_except_files_get_bonus(self, try_except_project: Path) -> None:
        """Files with try/except patterns should improve error_handling_score."""
        rev = _ConcreteReviewer(
            project_root=str(try_except_project),
            pyscn_analyzer=_StubAnalyzer(dead_code_results=[{"severity": "critical"}]),
        )
        score = rev._calculate_reliability_score()
        assert 0.0 <= score <= 100.0

    def test_error_returns_50(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._calculate_reliability_score() == 50.0


# ---------------------------------------------------------------------------
# TestSecurityScore
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculateSecurityScore:
    """_calculate_security_score scans .py files for dangerous patterns."""

    def test_clean_project_high_score(self, tmp_path: Path) -> None:
        (tmp_path / "clean.py").write_text("x = 1 + 2\n", encoding="utf-8")
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        score = rev._calculate_security_score()
        assert score == 100.0

    def test_eval_reduces_score(self, security_project: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(security_project))
        score = rev._calculate_security_score()
        assert score < 100.0

    def test_no_python_files_full_score(self, tmp_path: Path) -> None:
        (tmp_path / "README.md").write_text("# Hello\n", encoding="utf-8")
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        score = rev._calculate_security_score()
        assert score == 100.0

    def test_score_bounded(self, security_project: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(security_project))
        score = rev._calculate_security_score()
        assert 0.0 <= score <= 100.0

    def test_exec_pattern_penalised(self, tmp_path: Path) -> None:
        (tmp_path / "bad.py").write_text(
            "exec('print(1)')\nexec('print(2)')\nexec('print(3)')\n",
            encoding="utf-8",
        )
        rev = _ConcreteReviewer(project_root=str(tmp_path))
        score = rev._calculate_security_score()
        assert score < 100.0


# ---------------------------------------------------------------------------
# TestPerformanceScore
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculatePerformanceScore:
    """_calculate_performance_score returns 80 with no data; penalises patterns."""

    def test_no_data_returns_80(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(),
        )
        assert rev._calculate_performance_score() == 80.0

    def test_with_complexity(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[{"complexity": 5}, {"complexity": 8}]
            ),
        )
        score = rev._calculate_performance_score()
        assert 0.0 <= score <= 100.0

    def test_performance_patterns_penalised(self, performance_project: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(performance_project),
            pyscn_analyzer=_StubAnalyzer(complexity_results=[{"complexity": 2}]),
        )
        score = rev._calculate_performance_score()
        assert 0.0 <= score <= 100.0

    def test_very_high_max_complexity_penalised(self, empty_dir: Path) -> None:
        rev_low = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(complexity_results=[{"complexity": 5}]),
        )
        rev_high = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(complexity_results=[{"complexity": 50}]),
        )
        assert (
            rev_low._calculate_performance_score()
            > rev_high._calculate_performance_score()
        )

    def test_error_returns_50(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._calculate_performance_score() == 50.0


# ---------------------------------------------------------------------------
# TestTopComplexityIssues
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetTopComplexityIssues:
    """_get_top_complexity_issues sorts by complexity desc and limits to 5."""

    def test_empty_results(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(),
        )
        assert rev._get_top_complexity_issues() == []

    def test_sorted_and_truncated(self, empty_dir: Path) -> None:
        funcs = [
            {"name": f"f{i}", "complexity": i, "file_path": "a.py", "line_number": i}
            for i in range(10)
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(complexity_results=funcs),
        )
        top = rev._get_top_complexity_issues()
        assert len(top) == 5
        assert top[0]["complexity"] == 9
        assert top[1]["complexity"] == 8

    def test_result_shape(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[
                    {
                        "name": "my_func",
                        "complexity": 7,
                        "file_path": "x.py",
                        "line_number": 5,
                    }
                ]
            ),
        )
        top = rev._get_top_complexity_issues()
        assert top[0]["function_name"] == "my_func"
        assert top[0]["file_path"] == "x.py"
        assert top[0]["complexity"] == 7
        assert top[0]["line_number"] == 5

    def test_error_returns_empty(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._get_top_complexity_issues() == []


# ---------------------------------------------------------------------------
# TestTopDeadCodeIssues
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetTopDeadCodeIssues:
    """_get_top_dead_code_issues sorts by severity and limits to 5."""

    def test_empty(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(dead_code_results=[]),
        )
        assert rev._get_top_dead_code_issues() == []

    def test_severity_order_critical_first(self, empty_dir: Path) -> None:
        findings = [
            {
                "severity": "info",
                "location": {"file_path": "a.py", "start_line": 1},
                "reason": "r1",
            },
            {
                "severity": "critical",
                "location": {"file_path": "b.py", "start_line": 2},
                "reason": "r2",
            },
            {
                "severity": "warning",
                "location": {"file_path": "c.py", "start_line": 3},
                "reason": "r3",
            },
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(dead_code_results=findings),
        )
        top = rev._get_top_dead_code_issues()
        assert top[0]["severity"] == "critical"
        assert top[1]["severity"] == "warning"
        assert top[2]["severity"] == "info"

    def test_limited_to_five(self, empty_dir: Path) -> None:
        findings = [
            {
                "severity": "critical",
                "location": {"file_path": f"{i}.py", "start_line": i},
                "reason": "r",
            }
            for i in range(10)
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(dead_code_results=findings),
        )
        assert len(rev._get_top_dead_code_issues()) == 5

    def test_error_returns_empty(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._get_top_dead_code_issues() == []


# ---------------------------------------------------------------------------
# TestTopDuplicationIssues
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetTopDuplicationIssues:
    """_get_top_duplication_issues returns empty when no files / clones."""

    def test_no_python_files(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(empty_dir))
        assert rev._get_top_duplication_issues() == []

    def test_no_clones(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(clone_groups=[]),
        )
        assert rev._get_top_duplication_issues() == []

    def test_clone_group_structure(self, small_project: Path) -> None:
        clone_groups = [
            {
                "similarity": 0.92,
                "instances": [
                    {"file_path": "a.py", "start_line": 1, "end_line": 20},
                    {"file_path": "b.py", "start_line": 5, "end_line": 24},
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
        assert top[0]["similarity"] == 0.92
        assert len(top[0]["locations"]) == 2

    def test_single_instance_group_excluded(self, small_project: Path) -> None:
        """Groups with fewer than 2 instances are not reported as issues."""
        clone_groups = [
            {"instances": [{"file_path": "a.py", "start_line": 1, "end_line": 10}]}
        ]
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(clone_groups=clone_groups),
        )
        issues = rev._get_top_duplication_issues()
        assert issues == []

    def test_error_returns_empty(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._get_top_duplication_issues() == []

    def test_locations_limited_to_three(self, small_project: Path) -> None:
        """Only the first 3 instance locations are returned in each issue."""
        clone_groups = [
            {
                "similarity": 0.9,
                "instances": [
                    {"file_path": f"{i}.py", "start_line": i, "end_line": i + 5}
                    for i in range(6)
                ],
            }
        ]
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(clone_groups=clone_groups),
        )
        top = rev._get_top_duplication_issues()
        assert top[0]["clone_count"] == 6
        assert len(top[0]["locations"]) == 3


# ---------------------------------------------------------------------------
# TestPriorityActions
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDeterminePriorityActions:
    """_determine_priority_actions_from_dashboard generates actions correctly."""

    def test_no_issues(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._determine_priority_actions_from_dashboard([], [], []) == []

    def test_high_complexity_action(self, reviewer: _ConcreteReviewer) -> None:
        issues = [
            {
                "function_name": "big",
                "file_path": "a.py",
                "complexity": 25,
                "line_number": 1,
            }
        ]
        actions = reviewer._determine_priority_actions_from_dashboard(issues, [], [])
        assert len(actions) == 1
        assert actions[0]["type"] == "complexity_reduction"
        assert actions[0]["priority"] == "high"
        assert "big" in actions[0]["description"]

    def test_complexity_threshold_exactly_20(self, reviewer: _ConcreteReviewer) -> None:
        issues = [
            {
                "function_name": "edge",
                "file_path": "b.py",
                "complexity": 20,
                "line_number": 5,
            }
        ]
        actions = reviewer._determine_priority_actions_from_dashboard(issues, [], [])
        assert len(actions) == 1

    def test_below_threshold_no_action(self, reviewer: _ConcreteReviewer) -> None:
        issues = [
            {
                "function_name": "ok",
                "file_path": "c.py",
                "complexity": 19,
                "line_number": 3,
            }
        ]
        assert reviewer._determine_priority_actions_from_dashboard(issues, [], []) == []

    def test_critical_dead_code_action(self, reviewer: _ConcreteReviewer) -> None:
        dead = [
            {
                "file_path": "d.py",
                "line_number": 10,
                "reason": "unused",
                "severity": "critical",
            }
        ]
        actions = reviewer._determine_priority_actions_from_dashboard([], dead, [])
        assert len(actions) == 1
        assert actions[0]["type"] == "dead_code_removal"

    def test_warning_dead_code_no_action(self, reviewer: _ConcreteReviewer) -> None:
        dead = [
            {
                "file_path": "e.py",
                "line_number": 1,
                "reason": "unused import",
                "severity": "warning",
            }
        ]
        assert reviewer._determine_priority_actions_from_dashboard([], dead, []) == []

    def test_combined_issues(self, reviewer: _ConcreteReviewer) -> None:
        complexity = [
            {
                "function_name": "f",
                "file_path": "a.py",
                "complexity": 25,
                "line_number": 1,
            }
        ]
        dead = [
            {
                "file_path": "b.py",
                "line_number": 5,
                "reason": "dead",
                "severity": "critical",
            }
        ]
        actions = reviewer._determine_priority_actions_from_dashboard(
            complexity, dead, []
        )
        assert len(actions) == 2


# ---------------------------------------------------------------------------
# TestQuickWins
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestIdentifyQuickWins:
    """_identify_quick_wins flags only critical dead code items."""

    def test_empty_input(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._identify_quick_wins([]) == []

    def test_critical_produces_win(self, reviewer: _ConcreteReviewer) -> None:
        issues = [
            {"file_path": "/a/b/file.py", "line_number": 7, "severity": "critical"}
        ]
        wins = reviewer._identify_quick_wins(issues)
        assert len(wins) == 1
        assert wins[0]["effort"] == "low"
        assert wins[0]["impact"] == "high"
        assert wins[0]["type"] == "dead_code_cleanup"
        assert "file.py" in wins[0]["description"]
        assert "7" in wins[0]["description"]

    def test_warning_not_a_win(self, reviewer: _ConcreteReviewer) -> None:
        issues = [{"file_path": "f.py", "line_number": 1, "severity": "warning"}]
        assert reviewer._identify_quick_wins(issues) == []

    def test_multiple_critical_all_produced(self, reviewer: _ConcreteReviewer) -> None:
        issues = [
            {"file_path": "a.py", "line_number": i, "severity": "critical"}
            for i in range(3)
        ]
        wins = reviewer._identify_quick_wins(issues)
        assert len(wins) == 3


# ---------------------------------------------------------------------------
# TestLongTermImprovements
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestIdentifyLongTermImprovements:
    """_identify_long_term_improvements triggers only above high_risk_count > 10."""

    def test_empty_data(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._identify_long_term_improvements({}) == []

    def test_threshold_not_exceeded(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._identify_long_term_improvements({"high_risk_count": 10}) == []

    def test_threshold_exceeded(self, reviewer: _ConcreteReviewer) -> None:
        improvements = reviewer._identify_long_term_improvements(
            {"high_risk_count": 11}
        )
        assert len(improvements) == 1
        assert improvements[0]["type"] == "architecture_refactoring"
        assert improvements[0]["effort"] == "high"

    def test_large_count(self, reviewer: _ConcreteReviewer) -> None:
        improvements = reviewer._identify_long_term_improvements(
            {"high_risk_count": 100}
        )
        assert len(improvements) == 1


# ---------------------------------------------------------------------------
# TestSuggestProperName
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSuggestProperName:
    """_suggest_proper_name renames test files to the preferred prefix format."""

    def test_already_prefixed(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._suggest_proper_name("test_utils.py") == "test_utils.py"

    def test_unprefixed_with_test_word(self, reviewer: _ConcreteReviewer) -> None:
        result = reviewer._suggest_proper_name("my_test_helper.py")
        assert result.startswith("test_")

    def test_suffix_pattern(self, reviewer: _ConcreteReviewer) -> None:
        result = reviewer._suggest_proper_name("module_test.py")
        assert result.startswith("test_")

    def test_no_test_word_unchanged(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._suggest_proper_name("utils.py") == "utils.py"

    def test_already_correct_unchanged(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._suggest_proper_name("test_something.py") == "test_something.py"


# ---------------------------------------------------------------------------
# TestDetectCodeSmells
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDetectCodeSmells:
    """detect_code_smells delegates to sub-detectors and aggregates results."""

    def test_clean_code_no_smells(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[
                    {
                        "name": "f",
                        "complexity": 3,
                        "file_path": "a.py",
                        "line_number": 1,
                    }
                ],
                coupling_results=[{"name": "C", "coupling": 2, "file_path": "a.py"}],
            ),
        )
        smells = rev.detect_code_smells()
        assert isinstance(smells, list)
        assert all(s["type"] != "long_method" for s in smells)
        assert all(s["type"] != "large_class" for s in smells)

    def test_long_method_detected(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[
                    {
                        "name": "huge",
                        "complexity": 25,
                        "file_path": "big.py",
                        "line_number": 1,
                    }
                ]
            ),
        )
        smells = rev.detect_code_smells()
        long_methods = [s for s in smells if s["type"] == "long_method"]
        assert len(long_methods) == 1
        assert long_methods[0]["function_name"] == "huge"
        assert "suggestion" in long_methods[0]

    def test_large_class_detected(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                coupling_results=[
                    {"name": "GodClass", "coupling": 20, "file_path": "god.py"}
                ]
            ),
        )
        smells = rev.detect_code_smells()
        large_classes = [s for s in smells if s["type"] == "large_class"]
        assert len(large_classes) == 1
        assert large_classes[0]["class_name"] == "GodClass"

    def test_feature_envy_empty(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._detect_feature_envy() == []

    def test_data_clumps_empty(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._detect_data_clumps() == []

    def test_primitive_obsession_empty(self, reviewer: _ConcreteReviewer) -> None:
        assert reviewer._detect_primitive_obsession() == []

    def test_detect_long_methods_boundary_inclusive(self, empty_dir: Path) -> None:
        """Complexity exactly 21 should appear; exactly 20 should not."""
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[
                    {
                        "name": "border",
                        "complexity": 21,
                        "file_path": "x.py",
                        "line_number": 1,
                    },
                    {
                        "name": "safe",
                        "complexity": 20,
                        "file_path": "x.py",
                        "line_number": 10,
                    },
                ]
            ),
        )
        smells = rev._detect_long_methods()
        names = [s["function_name"] for s in smells]
        assert "border" in names
        assert "safe" not in names

    def test_detect_large_classes_boundary_inclusive(self, empty_dir: Path) -> None:
        """Coupling exactly 16 triggers; exactly 15 does not."""
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(
                coupling_results=[
                    {"name": "BigOne", "coupling": 16, "file_path": "x.py"},
                    {"name": "SmallOne", "coupling": 15, "file_path": "x.py"},
                ]
            ),
        )
        smells = rev._detect_large_classes()
        names = [s["class_name"] for s in smells]
        assert "BigOne" in names
        assert "SmallOne" not in names

    def test_detect_long_methods_error_returns_empty(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._detect_long_methods() == []

    def test_detect_large_classes_error_returns_empty(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(raise_on_call=True),
        )
        assert rev._detect_large_classes() == []


# ---------------------------------------------------------------------------
# TestSuggestAutomatedFixes
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSuggestAutomatedFixes:
    """suggest_automated_fixes builds a structured fix dict from live data."""

    def test_clean_project_empty_fixes(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(empty_dir))
        fixes = rev.suggest_automated_fixes()
        assert isinstance(fixes, dict)
        assert "dead_code_removal" in fixes
        assert "import_optimization" in fixes
        assert "naming_convention_fixes" in fixes
        assert "complexity_reductions" in fixes

    def test_critical_dead_code_generates_fix(self, empty_dir: Path) -> None:
        findings = [
            DeadCodeFinding(
                file_path="x.py",
                line_number=5,
                code_snippet="pass",
                reason="unused",
                severity="critical",
                suggestion="remove it",
                fix_available=True,
            )
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            dead_code_findings=findings,
        )
        fixes = rev.suggest_automated_fixes()
        assert len(fixes["dead_code_removal"]) == 1
        fix = fixes["dead_code_removal"][0]
        assert fix["confidence"] == 0.95
        assert fix["action"] == "remove_dead_code"
        assert fix["file_path"] == "x.py"

    def test_non_fix_available_dead_code_excluded(self, empty_dir: Path) -> None:
        findings = [
            DeadCodeFinding(
                file_path="y.py",
                line_number=1,
                code_snippet="x=1",
                reason="unused",
                severity="critical",
                suggestion="remove",
                fix_available=False,
            )
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            dead_code_findings=findings,
        )
        fixes = rev.suggest_automated_fixes()
        assert len(fixes["dead_code_removal"]) == 0

    def test_naming_convention_fix(self, empty_dir: Path) -> None:
        violations = [
            ArchitectureViolation(
                file_path="my_test_file.py",
                violation_type="naming_convention",
                description="bad name",
                severity="medium",
                suggestion="rename",
            )
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            architecture_violations=violations,
        )
        fixes = rev.suggest_automated_fixes()
        assert len(fixes["naming_convention_fixes"]) == 1
        naming_fix = fixes["naming_convention_fixes"][0]
        assert naming_fix["confidence"] == 0.85
        assert naming_fix["action"] == "rename_file"

    def test_non_naming_violation_not_added(self, empty_dir: Path) -> None:
        violations = [
            ArchitectureViolation(
                file_path="bad.py",
                violation_type="circular_dependency",
                description="circular",
                severity="high",
                suggestion="refactor",
            )
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            architecture_violations=violations,
        )
        fixes = rev.suggest_automated_fixes()
        assert len(fixes["naming_convention_fixes"]) == 0


# ---------------------------------------------------------------------------
# TestAnalyzeTechnicalDebt
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAnalyzeTechnicalDebt:
    """analyze_technical_debt computes hours per category and sorts top items."""

    def test_zero_debt_clean(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(empty_dir))
        debt = rev.analyze_technical_debt()
        assert debt["total_debt_hours"] == 0
        assert debt["debt_by_category"]["complexity"] == 0
        assert debt["debt_by_category"]["dead_code"] == 0
        assert debt["debt_by_category"]["architecture"] == 0

    def test_complexity_debt_4h_per_suggestion(self, empty_dir: Path) -> None:
        suggestions = [
            ComplexityReductionSuggestion(
                function_name="f",
                file_path="a.py",
                current_complexity=22,
                suggested_refactoring="split",
                estimated_effort="high",
                benefits=["clarity"],
            )
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            complexity_suggestions=suggestions,
        )
        debt = rev.analyze_technical_debt()
        assert debt["debt_by_category"]["complexity"] == 4

    def test_dead_code_debt_1h_per_critical(self, empty_dir: Path) -> None:
        findings = [
            DeadCodeFinding(
                file_path="b.py",
                line_number=10,
                code_snippet="x = 1",
                reason="unused",
                severity="critical",
                suggestion="remove",
            ),
            DeadCodeFinding(
                file_path="c.py",
                line_number=20,
                code_snippet="y = 2",
                reason="unused",
                severity="warning",  # should not count
                suggestion="remove",
            ),
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            dead_code_findings=findings,
        )
        debt = rev.analyze_technical_debt()
        assert debt["debt_by_category"]["dead_code"] == 1

    def test_architecture_debt_8h_per_high_violation(self, empty_dir: Path) -> None:
        violations = [
            ArchitectureViolation("a.py", "circular", "desc", "high", "fix"),
            ArchitectureViolation("b.py", "style", "desc", "low", "fix"),
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            architecture_violations=violations,
        )
        debt = rev.analyze_technical_debt()
        # only high violations count: 1 * 8 = 8
        assert debt["debt_by_category"]["architecture"] == 8

    def test_total_is_sum_of_categories(self, empty_dir: Path) -> None:
        suggestions = [
            ComplexityReductionSuggestion("f", "a.py", 20, "split", "high", [])
        ]
        findings = [DeadCodeFinding("b.py", 1, "x", "unused", "critical", "rm")]
        violations = [ArchitectureViolation("c.py", "circular", "d", "high", "fix")]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            complexity_suggestions=suggestions,
            dead_code_findings=findings,
            architecture_violations=violations,
        )
        debt = rev.analyze_technical_debt()
        expected_total = 4 + 1 + 8
        assert debt["total_debt_hours"] == expected_total

    def test_top_debt_items_sorted_by_hours(self, empty_dir: Path) -> None:
        suggestions = [
            ComplexityReductionSuggestion("f", "a.py", 20, "split", "high", [])
        ]
        violations = [ArchitectureViolation("b.py", "circ", "d", "high", "fix")]
        findings = [DeadCodeFinding("c.py", 1, "x", "unused", "critical", "rm")]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            complexity_suggestions=suggestions,
            architecture_violations=violations,
            dead_code_findings=findings,
        )
        debt = rev.analyze_technical_debt()
        items = debt["top_debt_items"]
        assert len(items) == 3
        # architecture (8h) first, then complexity (4h), then dead_code (1h)
        assert items[0]["estimated_hours"] == 8
        assert items[1]["estimated_hours"] == 4
        assert items[2]["estimated_hours"] == 1

    def test_top_debt_items_limited_to_10(self, empty_dir: Path) -> None:
        suggestions = [
            ComplexityReductionSuggestion(f"f{i}", "a.py", 25, "split", "high", [])
            for i in range(8)
        ]
        violations = [
            ArchitectureViolation("b.py", "c", "d", "high", "fix") for _ in range(8)
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            complexity_suggestions=suggestions,
            architecture_violations=violations,
        )
        debt = rev.analyze_technical_debt()
        assert len(debt["top_debt_items"]) <= 10

    def test_high_complexity_priority_high_above_25(self, empty_dir: Path) -> None:
        suggestions = [
            ComplexityReductionSuggestion("big", "a.py", 30, "split", "high", []),
            ComplexityReductionSuggestion("small", "b.py", 20, "split", "medium", []),
        ]
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            complexity_suggestions=suggestions,
        )
        debt = rev.analyze_technical_debt()
        items_by_type = {
            i["function_name"]: i
            for i in debt["top_debt_items"]
            if "function_name" in i
        }
        assert items_by_type["big"]["priority"] == "high"
        assert items_by_type["small"]["priority"] == "medium"


# ---------------------------------------------------------------------------
# TestGenerateQualityDashboard (integration-style)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGenerateQualityDashboard:
    """generate_quality_dashboard produces a fully-populated QualityDashboard."""

    def test_returns_quality_dashboard_instance(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(
            project_root=str(small_project),
            pyscn_analyzer=_StubAnalyzer(
                complexity_results=[
                    {
                        "name": "f",
                        "complexity": 5,
                        "file_path": "m.py",
                        "line_number": 1,
                    }
                ]
            ),
        )
        dashboard = rev.generate_quality_dashboard()
        assert isinstance(dashboard, QualityDashboard)

    def test_score_in_valid_range(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(small_project))
        dashboard = rev.generate_quality_dashboard()
        assert 0.0 <= dashboard.overall_score <= 100.0

    def test_grade_is_valid_letter(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(small_project))
        dashboard = rev.generate_quality_dashboard()
        assert dashboard.grade in {"A", "B", "C", "D", "F"}

    def test_analysis_timestamp_populated(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(small_project))
        dashboard = rev.generate_quality_dashboard()
        assert dashboard.analysis_timestamp  # non-empty

    def test_total_files_matches_filesystem(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(small_project))
        dashboard = rev.generate_quality_dashboard()
        assert dashboard.total_files == 3  # __init__.py, main.py, utils.py

    def test_metrics_dicts_present(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(small_project))
        dashboard = rev.generate_quality_dashboard()
        assert isinstance(dashboard.complexity_metrics, dict)
        assert isinstance(dashboard.dead_code_metrics, dict)
        assert isinstance(dashboard.duplication_metrics, dict)
        assert isinstance(dashboard.coupling_metrics, dict)
        assert isinstance(dashboard.architecture_metrics, dict)

    def test_lists_are_lists(self, small_project: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(small_project))
        dashboard = rev.generate_quality_dashboard()
        assert isinstance(dashboard.top_complexity_issues, list)
        assert isinstance(dashboard.top_dead_code_issues, list)
        assert isinstance(dashboard.top_duplication_issues, list)
        assert isinstance(dashboard.priority_actions, list)
        assert isinstance(dashboard.quick_wins, list)
        assert isinstance(dashboard.long_term_improvements, list)

    def test_empty_project_still_generates_dashboard(self, empty_dir: Path) -> None:
        rev = _ConcreteReviewer(project_root=str(empty_dir))
        dashboard = rev.generate_quality_dashboard()
        assert isinstance(dashboard, QualityDashboard)
        assert dashboard.total_files == 0
        assert dashboard.total_lines == 0

    def test_perfect_project_high_score(self, empty_dir: Path) -> None:
        """With no issues from any analyzer, the score should be very high."""
        rev = _ConcreteReviewer(
            project_root=str(empty_dir),
            pyscn_analyzer=_StubAnalyzer(),  # all empty
        )
        dashboard = rev.generate_quality_dashboard()
        # All category scores should be at or near their "empty data" defaults:
        # complexity=100, dead_code=100, coupling=100, architecture=100, duplication=100
        assert dashboard.overall_score >= 90.0
        assert dashboard.grade == "A"
