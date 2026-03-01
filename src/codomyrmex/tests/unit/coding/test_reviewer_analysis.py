"""Unit tests for code reviewer analysis -- language detection, file filtering, grading, and scoring."""

import subprocess

import pytest

from codomyrmex.coding.review.models import (
    Language,
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
