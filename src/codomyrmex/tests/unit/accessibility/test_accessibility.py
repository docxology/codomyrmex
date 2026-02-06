"""Tests for accessibility module."""

import pytest

try:
    from codomyrmex.accessibility import (
        A11yChecker,
        AccessibilityIssue,
        AccessibilityReport,
        IssueType,
        WCAGLevel,
        WCAGRule,
        calculate_contrast_ratio,
        check_heading_hierarchy,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("accessibility module not available", allow_module_level=True)


@pytest.mark.unit
class TestWCAGLevel:
    def test_level_a(self):
        assert WCAGLevel.A is not None

    def test_level_aa(self):
        assert WCAGLevel.AA is not None

    def test_level_aaa(self):
        assert WCAGLevel.AAA is not None


@pytest.mark.unit
class TestIssueType:
    def test_error_type(self):
        assert IssueType.ERROR is not None

    def test_warning_type(self):
        assert IssueType.WARNING is not None

    def test_notice_type(self):
        assert IssueType.NOTICE is not None


@pytest.mark.unit
class TestAccessibilityIssue:
    def test_create_issue(self):
        issue = AccessibilityIssue(code="img-alt", message="Missing alt text")
        assert issue.code == "img-alt"
        assert issue.message == "Missing alt text"

    def test_issue_defaults(self):
        issue = AccessibilityIssue(code="test", message="test")
        assert issue.selector == ""
        assert issue.issue_type == IssueType.ERROR
        assert issue.wcag_criterion == ""
        assert issue.wcag_level == WCAGLevel.A
        assert issue.suggestion == ""

    def test_issue_with_all_fields(self):
        issue = AccessibilityIssue(
            code="color-contrast",
            message="Low contrast",
            selector="div.main",
            issue_type=IssueType.WARNING,
            wcag_criterion="1.4.3",
            wcag_level=WCAGLevel.AA,
            suggestion="Increase contrast ratio",
        )
        assert issue.wcag_level == WCAGLevel.AA
        assert issue.suggestion == "Increase contrast ratio"


@pytest.mark.unit
class TestAccessibilityReport:
    def test_create_report(self):
        report = AccessibilityReport()
        assert report.url == ""
        assert report.issues == []
        assert report.passed == 0
        assert report.warnings == 0
        assert report.errors == 0


@pytest.mark.unit
class TestWCAGRule:
    def test_create_rule(self):
        rule = WCAGRule(
            code="img-alt",
            criterion="1.1.1",
            level=WCAGLevel.A,
            check_fn=lambda x: True,
            message="Images must have alt text",
        )
        assert rule.code == "img-alt"
        assert rule.level == WCAGLevel.A

    def test_rule_with_suggestion(self):
        rule = WCAGRule(
            code="test",
            criterion="1.1.1",
            level=WCAGLevel.A,
            check_fn=lambda x: True,
            message="test",
            suggestion="Fix this",
        )
        assert rule.suggestion == "Fix this"


@pytest.mark.unit
class TestA11yChecker:
    def test_create_checker(self):
        checker = A11yChecker()
        assert checker is not None

    def test_create_checker_with_level(self):
        checker = A11yChecker(level=WCAGLevel.AAA)
        assert checker is not None


@pytest.mark.unit
class TestCalculateContrastRatio:
    def test_black_white_contrast(self):
        ratio = calculate_contrast_ratio("#000000", "#ffffff")
        assert ratio >= 21.0

    def test_same_color_contrast(self):
        ratio = calculate_contrast_ratio("#000000", "#000000")
        assert ratio == 1.0

    def test_returns_float(self):
        ratio = calculate_contrast_ratio("#333333", "#cccccc")
        assert isinstance(ratio, float)
        assert ratio > 1.0


@pytest.mark.unit
class TestCheckHeadingHierarchy:
    def test_valid_hierarchy(self):
        issues = check_heading_hierarchy([1, 2, 3])
        assert isinstance(issues, list)

    def test_skipped_level(self):
        issues = check_heading_hierarchy([1, 3])
        assert len(issues) > 0

    def test_empty_headings(self):
        issues = check_heading_hierarchy([])
        assert isinstance(issues, list)
