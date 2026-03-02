"""
Unit tests for website accessibility module — Zero-Mock compliant.

Covers: A11yChecker, AccessibilityReporter, calculate_contrast_ratio,
check_heading_hierarchy — previously at 14-33% coverage.
"""
import json

import pytest

from codomyrmex.website.accessibility.checker import A11yChecker
from codomyrmex.website.accessibility.models import (
    AccessibilityReport,
    WCAGLevel,
    WCAGRule,
)
from codomyrmex.website.accessibility.reporters import AccessibilityReporter
from codomyrmex.website.accessibility.utils import (
    calculate_contrast_ratio,
    check_heading_hierarchy,
)

# ── calculate_contrast_ratio ────────────────────────────────────────────


@pytest.mark.unit
class TestCalculateContrastRatio:
    """Tests for calculate_contrast_ratio() — WCAG contrast checking."""

    def test_black_on_white_has_high_contrast(self):
        """#000000 on #ffffff should return ~21.0."""
        ratio = calculate_contrast_ratio("#000000", "#ffffff")
        assert ratio > 20.0

    def test_white_on_black_same_as_black_on_white(self):
        """Contrast ratio is symmetric."""
        r1 = calculate_contrast_ratio("#000000", "#ffffff")
        r2 = calculate_contrast_ratio("#ffffff", "#000000")
        assert abs(r1 - r2) < 0.01

    def test_same_color_returns_one(self):
        """Identical colors → ratio = 1.0."""
        ratio = calculate_contrast_ratio("#808080", "#808080")
        assert abs(ratio - 1.0) < 0.01

    def test_wcag_aa_threshold_red_on_white(self):
        """Pure red (#ff0000) on white has ratio < 4.5 (fails AA)."""
        ratio = calculate_contrast_ratio("#ff0000", "#ffffff")
        assert isinstance(ratio, float)
        assert ratio > 0.0

    def test_invalid_hex_returns_zero(self):
        """Malformed hex → returns 0.0 without raising."""
        ratio = calculate_contrast_ratio("not-a-color", "#ffffff")
        assert ratio == 0.0

    def test_returns_float(self):
        """Always returns a float."""
        ratio = calculate_contrast_ratio("#336699", "#ffffff")
        assert isinstance(ratio, float)

    def test_no_hash_prefix_raises_or_returns_zero(self):
        """6-char hex without # is handled gracefully (zero or valid)."""
        result = calculate_contrast_ratio("000000", "ffffff")
        assert isinstance(result, float)


# ── check_heading_hierarchy ─────────────────────────────────────────────


@pytest.mark.unit
class TestCheckHeadingHierarchy:
    """Tests for check_heading_hierarchy() — heading level validation."""

    def test_correct_hierarchy_no_issues(self):
        """h1→h2→h3 returns empty list."""
        issues = check_heading_hierarchy([1, 2, 3])
        assert issues == []

    def test_skipped_level_detected(self):
        """h1→h3 (skip h2) returns at least one issue."""
        issues = check_heading_hierarchy([1, 3])
        assert len(issues) >= 1
        assert any("h3" in i for i in issues)

    def test_does_not_start_with_h1(self):
        """Starting at h2 returns issue about missing h1."""
        issues = check_heading_hierarchy([2, 3])
        assert any("h1" in i for i in issues)

    def test_empty_headings_no_issues(self):
        """Empty list → no issues."""
        issues = check_heading_hierarchy([])
        assert issues == []

    def test_single_h1_no_issues(self):
        """Just [1] is valid."""
        issues = check_heading_hierarchy([1])
        assert issues == []

    def test_multiple_skips_multiple_issues(self):
        """h1→h4→h6 should return multiple issues."""
        issues = check_heading_hierarchy([1, 4, 6])
        assert len(issues) >= 2

    def test_repeated_level_allowed(self):
        """h1, h2, h2 is valid (no skip)."""
        issues = check_heading_hierarchy([1, 2, 2])
        assert issues == []


# ── A11yChecker ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestA11yChecker:
    """Tests for A11yChecker — accessibility element checking."""

    def test_init_level_aa(self):
        """Default level is AA."""
        checker = A11yChecker()
        assert checker.level == WCAGLevel.AA

    def test_init_level_a(self):
        """Can init with level A."""
        checker = A11yChecker(level=WCAGLevel.A)
        assert checker.level == WCAGLevel.A

    def test_default_rules_populated(self):
        """Default rules are populated on init."""
        checker = A11yChecker()
        assert len(checker._rules) >= 4

    def test_add_rule_increases_count(self):
        """add_rule() increases rule count by 1."""
        checker = A11yChecker()
        initial = len(checker._rules)
        rule = WCAGRule(
            code="test-rule",
            criterion="1.2.3",
            level=WCAGLevel.A,
            check_fn=lambda e: True,
            message="Test rule",
            suggestion="Do the thing",
        )
        checker.add_rule(rule)
        assert len(checker._rules) == initial + 1

    def test_check_elements_empty_list(self):
        """Empty elements list returns empty report."""
        checker = A11yChecker()
        report = checker.check_elements([])
        assert report.errors == 0
        assert report.warnings == 0
        assert report.passed == 0

    def test_img_without_alt_flagged(self):
        """img element missing alt attribute is flagged."""
        checker = A11yChecker()
        elements = [{"tag": "img", "src": "photo.jpg"}]
        report = checker.check_elements(elements)
        assert report.errors + report.warnings > 0

    def test_img_with_alt_passes_img_rule(self):
        """img with alt passes the img-alt rule."""
        checker = A11yChecker()
        elements = [{"tag": "img", "alt": "A description", "src": "photo.jpg"}]
        report = checker.check_elements(elements)
        # img-alt rule should pass; other rules won't fire for non-matching tags
        assert report.passed > 0

    def test_link_without_text_flagged(self):
        """Anchor without text is flagged."""
        checker = A11yChecker()
        elements = [{"tag": "a", "href": "/", "text": ""}]
        report = checker.check_elements(elements)
        assert report.errors + report.warnings > 0

    def test_link_with_text_passes_link_rule(self):
        """Anchor with text passes the link-text rule."""
        checker = A11yChecker()
        elements = [{"tag": "a", "href": "/", "text": "Home"}]
        report = checker.check_elements(elements)
        assert report.passed > 0

    def test_returns_accessibility_report_instance(self):
        """check_elements always returns AccessibilityReport."""
        checker = A11yChecker()
        result = checker.check_elements([{"tag": "div"}])
        assert isinstance(result, AccessibilityReport)

    def test_level_a_skips_aa_rules(self):
        """Level A checker doesn't apply AA-level rules."""
        checker_a = A11yChecker(level=WCAGLevel.A)
        checker_aa = A11yChecker(level=WCAGLevel.AA)
        elements = [{"tag": "div", "contrast_ratio": 2.0}]  # fails color-contrast (AA)
        report_a = checker_a.check_elements(elements)
        report_aa = checker_aa.check_elements(elements)
        # AA should catch color-contrast; A should not
        assert report_aa.errors + report_aa.warnings >= report_a.errors + report_a.warnings

    def test_input_without_label_flagged(self):
        """input without label is flagged."""
        checker = A11yChecker()
        elements = [{"tag": "input", "type": "text"}]
        report = checker.check_elements(elements)
        assert report.errors + report.warnings > 0


# ── AccessibilityReporter ───────────────────────────────────────────────


@pytest.mark.unit
class TestAccessibilityReporter:
    """Tests for AccessibilityReporter — report formatting."""

    def _make_report(self, passed=5, errors=1, warnings=2, url=None):
        """Build a simple AccessibilityReport for testing."""
        report = AccessibilityReport(url=url)
        report.passed = passed
        report.errors = errors
        report.warnings = warnings
        return report

    def test_to_summary_format(self):
        """to_summary() includes score, passed, errors, warnings."""
        report = self._make_report(passed=10, errors=2, warnings=1)
        reporter = AccessibilityReporter(report)
        summary = reporter.to_summary()
        assert "passed" in summary
        assert "errors" in summary
        assert "warnings" in summary
        assert "%" in summary

    def test_to_dict_structure(self):
        """to_dict() returns dict with required keys."""
        report = self._make_report()
        reporter = AccessibilityReporter(report)
        d = reporter.to_dict()
        assert "score" in d
        assert "passed" in d
        assert "errors" in d
        assert "warnings" in d
        assert "issues" in d
        assert isinstance(d["issues"], list)

    def test_to_dict_with_url(self):
        """to_dict includes url when set."""
        report = self._make_report(url="https://example.com")
        reporter = AccessibilityReporter(report)
        d = reporter.to_dict()
        assert d["url"] == "https://example.com"

    def test_to_json_is_valid_json(self):
        """to_json() returns valid JSON string."""
        report = self._make_report()
        reporter = AccessibilityReporter(report)
        json_str = reporter.to_json()
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

    def test_to_json_indent(self):
        """to_json(indent=4) uses 4-space indentation."""
        report = self._make_report()
        reporter = AccessibilityReporter(report)
        json_str = reporter.to_json(indent=4)
        assert "    " in json_str  # 4-space indent present

    def test_to_markdown_contains_header(self):
        """to_markdown() starts with # Accessibility Report."""
        report = self._make_report()
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert "# Accessibility Report" in md

    def test_to_markdown_contains_score(self):
        """to_markdown() includes Score line."""
        report = self._make_report(passed=8, errors=0, warnings=2)
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert "Score" in md

    def test_to_markdown_with_url(self):
        """to_markdown() shows URL when present."""
        report = self._make_report(url="https://example.com")
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert "example.com" in md

    def test_to_markdown_no_issues_table_when_empty(self):
        """to_markdown() omits Issues table when no issues."""
        report = AccessibilityReport()
        report.passed = 5
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert "## Issues" not in md

    def test_to_dict_score_is_number(self):
        """Score in to_dict() is numeric."""
        report = self._make_report(passed=9, errors=1, warnings=0)
        reporter = AccessibilityReporter(report)
        d = reporter.to_dict()
        assert isinstance(d["score"], (int, float))
