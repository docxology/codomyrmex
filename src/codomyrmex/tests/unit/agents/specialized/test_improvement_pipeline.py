"""Tests for Sprint 30: Autonomous Code Improvement Pipeline.

Covers AntiPatternDetector, ImprovementPipeline (full cycle,
safety limits, confidence thresholds), and ImprovementReport
markdown rendering.
"""

import pytest

from codomyrmex.agents.specialized.improvement_config import ImprovementConfig
from codomyrmex.agents.specialized.improvement_pipeline import (
    AntiPatternDetector,
    ImprovementPipeline,
)
from codomyrmex.agents.specialized.improvement_report import (
    AntiPattern,
    ImprovementReport,
    ProposedChange,
    ReviewVerdict,
    RiskLevel,
    TestSuiteResult,
)


# ─── Anti-Pattern Detector ────────────────────────────────────────────

class TestAntiPatternDetector:
    """Test suite for AntiPatternDetector."""

    def test_detects_bare_except(self):
        """Test functionality: detects bare except."""
        source = "try:\n    pass\nexcept:\n    pass"
        detector = AntiPatternDetector()
        patterns = detector.analyze(source)
        names = [p.name for p in patterns]
        assert "bare_except" in names

    def test_detects_mutable_default(self):
        """Test functionality: detects mutable default."""
        source = "def foo(x=[]):\n    return x"
        detector = AntiPatternDetector()
        patterns = detector.analyze(source)
        names = [p.name for p in patterns]
        assert "mutable_default" in names

    def test_detects_star_import(self):
        """Test functionality: detects star import."""
        source = "from os import *"
        detector = AntiPatternDetector()
        patterns = detector.analyze(source)
        assert any(p.name == "star_import" for p in patterns)

    def test_severity_threshold_filters(self):
        """Test functionality: severity threshold filters."""
        source = "# TODO: fix this"
        detector = AntiPatternDetector(severity_threshold=0.5)
        patterns = detector.analyze(source)
        # TODO severity is 0.2, below 0.5 threshold
        assert len(patterns) == 0

    def test_no_patterns_in_clean_code(self):
        """Test functionality: no patterns in clean code."""
        source = "def foo(x: int) -> int:\n    return x + 1"
        detector = AntiPatternDetector()
        patterns = detector.analyze(source)
        assert len(patterns) == 0


# ─── ImprovementPipeline ──────────────────────────────────────────────

class TestImprovementPipeline:
    """Test suite for ImprovementPipeline."""

    def test_full_cycle(self):
        """Pipeline detects pattern → generates fix → review approves."""
        source = "try:\n    pass\nexcept:\n    pass"
        pipeline = ImprovementPipeline()
        report = pipeline.improve(source, file_path="test.py")

        assert len(report.anti_patterns) >= 1
        assert len(report.changes) >= 1
        assert report.review_verdict == ReviewVerdict.APPROVE

    def test_max_changes_limit(self):
        """Pipeline respects max_changes_per_run."""
        source = "\n".join([f"except:" for _ in range(20)])
        config = ImprovementConfig(max_changes_per_run=3)
        pipeline = ImprovementPipeline(config=config)
        report = pipeline.improve(source)
        assert report.change_count <= 3

    def test_min_confidence_threshold(self):
        """Below min_confidence → no changes applied."""
        source = "except:\n    pass"
        config = ImprovementConfig(min_confidence=0.99)
        pipeline = ImprovementPipeline(config=config)
        report = pipeline.improve(source)
        # Built-in fix generator has 0.85 confidence, below 0.99
        assert report.change_count == 0
        assert report.review_verdict == ReviewVerdict.REJECT

    def test_clean_code_approved(self):
        """Clean code → approved with no changes."""
        source = "x = 1\ny = x + 2"
        pipeline = ImprovementPipeline()
        report = pipeline.improve(source)
        assert report.change_count == 0
        assert report.review_verdict == ReviewVerdict.APPROVE

    def test_analyze_only(self):
        """analyze() returns patterns without generating fixes."""
        source = "from os import *"
        pipeline = ImprovementPipeline()
        patterns = pipeline.analyze(source)
        assert len(patterns) >= 1
        assert patterns[0].name == "star_import"


# ─── ImprovementReport ───────────────────────────────────────────────

class TestImprovementReport:
    """Test suite for ImprovementReport."""

    def test_report_to_markdown(self):
        """Test functionality: report to markdown."""
        report = ImprovementReport(
            source_file="app.py",
            anti_patterns=[AntiPattern(
                name="bare_except", description="Catches all",
                file_path="app.py", line_start=5, severity=0.7,
            )],
            changes=[ProposedChange(
                file_path="app.py", line_start=5, line_end=5,
                old_code="except:", new_code="except Exception:",
                rationale="Fix bare except", anti_pattern="bare_except",
            )],
            test_results=TestSuiteResult(total=1, passed=1),
            review_verdict=ReviewVerdict.APPROVE,
            overall_confidence=0.85,
        )
        md = report.to_markdown()
        assert "# Improvement Report" in md
        assert "bare_except" in md
        assert "APPROVE" in md.lower() or "approve" in md

    def test_change_count(self):
        """Test functionality: change count."""
        report = ImprovementReport(source_file="test.py")
        assert report.change_count == 0

    def test_approved_property(self):
        """Test functionality: approved property."""
        report = ImprovementReport(
            source_file="test.py",
            review_verdict=ReviewVerdict.APPROVE,
        )
        assert report.approved is True

    def test_test_suite_success_rate(self):
        """Test functionality: suite success rate."""
        result = TestSuiteResult(total=10, passed=8, failed=2)
        assert result.success_rate == pytest.approx(0.8)
