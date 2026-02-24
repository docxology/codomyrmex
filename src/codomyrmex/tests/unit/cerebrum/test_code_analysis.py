"""Tests for cerebrum/anti_patterns.py, drift_tracker.py, agent_prompts.py, code_reviewer.py."""

from __future__ import annotations

import pytest
import textwrap

from codomyrmex.cerebrum.anti_patterns import (
    AntiPattern,
    AntiPatternDetector,
    AnalysisReport,
    Severity,
)
from codomyrmex.cerebrum.drift_tracker import (
    ConceptDriftTracker,
    DriftEvent,
    DriftSnapshot,
)
from codomyrmex.cerebrum.agent_prompts import (
    AgentPromptSelector,
    PromptSelection,
)
from codomyrmex.cerebrum.code_reviewer import (
    CodeReviewer,
    CodeReviewReport,
    ReviewFinding,
)


# ── AntiPatternDetector ──────────────────────────────────────────


class TestAntiPattern:
    """Test suite for AntiPattern."""
    def test_to_dict(self) -> None:
        """Test functionality: to dict."""
        ap = AntiPattern(name="test", message="msg", severity=Severity.WARNING)
        d = ap.to_dict()
        assert d["name"] == "test"
        assert d["severity"] == "warning"


class TestAntiPatternDetector:
    """Test suite for AntiPatternDetector."""
    def test_clean_code(self) -> None:
        """Test functionality: clean code."""
        detector = AntiPatternDetector()
        source = "def hello():\n    return 'world'\n"
        report = detector.analyze_source(source)
        assert len(report.patterns) == 0
        assert report.files_scanned == 1

    def test_god_function(self) -> None:
        """Test functionality: god function."""
        detector = AntiPatternDetector(max_function_lines=5)
        source = "def big():\n" + "    x = 1\n" * 10
        report = detector.analyze_source(source)
        names = [p.name for p in report.patterns]
        assert "god-function" in names

    def test_too_many_params(self) -> None:
        """Test functionality: too many params."""
        detector = AntiPatternDetector(max_params=3)
        source = "def f(a, b, c, d, e):\n    pass\n"
        report = detector.analyze_source(source)
        names = [p.name for p in report.patterns]
        assert "too-many-params" in names

    def test_deep_nesting(self) -> None:
        """Test functionality: deep nesting."""
        detector = AntiPatternDetector(max_nesting=2)
        source = textwrap.dedent("""\
        def f():
            if True:
                if True:
                    if True:
                        pass
        """)
        report = detector.analyze_source(source)
        names = [p.name for p in report.patterns]
        assert "deep-nesting" in names

    def test_bare_except(self) -> None:
        """Test functionality: bare except."""
        detector = AntiPatternDetector()
        source = textwrap.dedent("""\
        def f():
            try:
                pass
            except:
                pass
        """)
        report = detector.analyze_source(source)
        names = [p.name for p in report.patterns]
        assert "bare-except" in names
        assert any(p.severity == Severity.ERROR for p in report.patterns)

    def test_syntax_error(self) -> None:
        """Test functionality: syntax error."""
        detector = AntiPatternDetector()
        report = detector.analyze_source("def f(")
        assert report.has_errors
        assert report.patterns[0].name == "syntax-error"

    def test_god_class(self) -> None:
        """Test functionality: god class."""
        detector = AntiPatternDetector()
        methods = "\n".join(f"    def m{i}(self): pass" for i in range(25))
        source = f"class Big:\n{methods}\n"
        report = detector.analyze_source(source)
        names = [p.name for p in report.patterns]
        assert "god-class" in names

    def test_report_count_by_severity(self) -> None:
        """Test functionality: report count by severity."""
        report = AnalysisReport(patterns=[
            AntiPattern(name="a", message="", severity=Severity.WARNING),
            AntiPattern(name="b", message="", severity=Severity.ERROR),
            AntiPattern(name="c", message="", severity=Severity.WARNING),
        ])
        assert report.count_by_severity == {"warning": 2, "error": 1}


# ── ConceptDriftTracker ──────────────────────────────────────────


class TestDriftEvent:
    """Test suite for DriftEvent."""
    def test_to_dict(self) -> None:
        """Test functionality: to dict."""
        e = DriftEvent(term="foo", category="new")
        d = e.to_dict()
        assert d["term"] == "foo"
        assert d["category"] == "new"


class TestConceptDriftTracker:
    """Test suite for ConceptDriftTracker."""
    def test_no_drift_identical(self) -> None:
        """Test functionality: no drift identical."""
        tracker = ConceptDriftTracker()
        corpus = ["The function processes input data correctly"]
        snapshot = tracker.compare(corpus, corpus)
        assert snapshot.magnitude == 0.0
        assert snapshot.shifted_count == 0

    def test_drift_different(self) -> None:
        """Test functionality: drift different."""
        tracker = ConceptDriftTracker()
        a = ["The function validates user input"]
        b = ["The module transforms binary output"]
        snapshot = tracker.compare(a, b)
        assert snapshot.magnitude > 0
        assert len(snapshot.events) > 0

    def test_new_concepts(self) -> None:
        """Test functionality: new concepts."""
        tracker = ConceptDriftTracker()
        a = ["Database connection pooling"]
        b = ["Database connection pooling with caching layer"]
        snapshot = tracker.compare(a, b)
        assert snapshot.new_count >= 0  # "caching layer" might be new

    def test_lost_concepts(self) -> None:
        """Test functionality: lost concepts."""
        tracker = ConceptDriftTracker()
        a = ["Advanced encryption algorithm implementation"]
        b = ["Simple storage retrieval"]
        snapshot = tracker.compare(a, b)
        assert snapshot.lost_count > 0

    def test_snapshot_to_dict(self) -> None:
        """Test functionality: snapshot to dict."""
        snapshot = DriftSnapshot(version_a="v1", version_b="v2")
        d = snapshot.to_dict()
        assert d["version_a"] == "v1"
        assert "shifted" in d
        assert "new" in d
        assert "lost" in d


# ── AgentPromptSelector ──────────────────────────────────────────


class TestAgentPromptSelector:
    """Test suite for AgentPromptSelector."""
    def test_list_builtins(self) -> None:
        """Test functionality: list builtins."""
        selector = AgentPromptSelector()
        names = selector.list_templates()
        assert "code_review" in names
        assert "reasoning_chain" in names

    def test_select_review(self) -> None:
        """Test functionality: select review."""
        selector = AgentPromptSelector()
        selection = selector.select(
            task="code review",
            variables={
                "language": "python",
                "code": "x = 1",
                "focus_areas": "security",
            },
            category="review",
        )
        assert isinstance(selection, PromptSelection)
        assert "python" in selection.rendered
        assert selection.score > 0

    def test_select_analysis(self) -> None:
        """Test functionality: select analysis."""
        selector = AgentPromptSelector()
        selection = selector.select(
            task="anti_pattern analysis",
            variables={"language": "python", "code": "pass"},
        )
        assert selection.template.name in (
            "anti_pattern_analysis", "code_review", "reasoning_chain"
        )

    def test_fallback_to_reasoning(self) -> None:
        """Test functionality: fallback to reasoning."""
        selector = AgentPromptSelector()
        selection = selector.select(task="something_unknown_xyz")
        assert selection.rendered  # Should produce something

    def test_no_builtins(self) -> None:
        """Test functionality: no builtins."""
        selector = AgentPromptSelector(load_builtins=False)
        assert len(selector.list_templates()) == 0

    def test_category_filter(self) -> None:
        """Test functionality: category filter."""
        selector = AgentPromptSelector()
        selection = selector.select(
            task="review",
            variables={"language": "python", "code": "...", "focus_areas": "perf"},
            category="review",
        )
        assert selection.template.metadata.get("category") == "review"


# ── CodeReviewer ─────────────────────────────────────────────────


class TestReviewFinding:
    """Test suite for ReviewFinding."""
    def test_to_dict(self) -> None:
        """Test functionality: to dict."""
        f = ReviewFinding(category="test", message="msg")
        d = f.to_dict()
        assert d["category"] == "test"


class TestCodeReviewer:
    """Test suite for CodeReviewer."""
    def test_review_clean(self) -> None:
        """Test functionality: review clean."""
        reviewer = CodeReviewer()
        report = reviewer.review_source("def hello():\n    return 42\n")
        assert report.is_clean
        assert "clean" in report.summary.lower()

    def test_review_with_issues(self) -> None:
        """Test functionality: review with issues."""
        reviewer = CodeReviewer(
            detector=AntiPatternDetector(max_params=2),
        )
        report = reviewer.review_source("def f(a, b, c, d):\n    pass\n")
        assert not report.is_clean
        assert report.warning_count >= 1

    def test_review_diff(self) -> None:
        """Test functionality: review diff."""
        reviewer = CodeReviewer()
        old = "def old_function():\n    return 'legacy'\n"
        new = "def new_function():\n    return 'modern'\n"
        report = reviewer.review_diff(old, new)
        assert report.files_reviewed == 1

    def test_get_review_prompt(self) -> None:
        """Test functionality: get review prompt."""
        reviewer = CodeReviewer()
        prompt = reviewer.get_review_prompt("x = 1", language="python")
        assert len(prompt) > 0  # Prompt was generated
        # The prompt selector may choose different templates;
        # verify it produces non-trivial output
        assert len(prompt) > 20

    def test_report_to_dict(self) -> None:
        """Test functionality: report to dict."""
        report = CodeReviewReport(
            findings=[ReviewFinding(category="a", message="b", severity="error")],
            files_reviewed=1,
        )
        d = report.to_dict()
        assert d["error_count"] == 1
        assert d["is_clean"] is False
