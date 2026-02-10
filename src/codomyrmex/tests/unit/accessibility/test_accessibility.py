"""Tests for accessibility module."""

import json

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
    from codomyrmex.accessibility.reporters import AccessibilityReporter

    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("accessibility module not available", allow_module_level=True)


# =============================================================================
# EXISTING 20 TESTS (preserved exactly)
# =============================================================================


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


# =============================================================================
# NEW BEHAVIORAL TESTS
# =============================================================================


@pytest.mark.unit
class TestAccessibilityReportScore:
    """Deep tests for AccessibilityReport.score property."""

    def test_score_zero_errors_is_100(self):
        """No errors and some passes yields 100%."""
        report = AccessibilityReport(passed=10, errors=0)
        assert report.score == 100.0

    def test_score_all_errors_is_zero(self):
        """All errors, no passes yields 0%."""
        report = AccessibilityReport(passed=0, errors=5)
        assert report.score == 0.0

    def test_score_half_errors(self):
        """Half errors yields 50%."""
        report = AccessibilityReport(passed=5, errors=5)
        assert report.score == 50.0

    def test_score_no_checks_is_100(self):
        """No checks at all yields 100% (vacuously true)."""
        report = AccessibilityReport(passed=0, errors=0)
        assert report.score == 100.0

    def test_score_one_error_many_passed(self):
        """1 error out of 100 total checks yields 99%."""
        report = AccessibilityReport(passed=99, errors=1)
        assert report.score == 99.0

    def test_score_ignores_warnings_in_calculation(self):
        """Warnings are not part of the score formula (only passed + errors)."""
        report = AccessibilityReport(passed=8, errors=2, warnings=50)
        assert report.score == 80.0

    def test_score_returns_float(self):
        """Score is always a float."""
        report = AccessibilityReport(passed=3, errors=1)
        assert isinstance(report.score, float)
        assert report.score == 75.0


@pytest.mark.unit
class TestWCAGRuleCheck:
    """Behavioral tests for WCAGRule.check() method."""

    def test_check_returns_issue_when_check_fn_fails(self):
        """When check_fn returns False, check() returns an AccessibilityIssue."""
        rule = WCAGRule(
            code="always-fail",
            criterion="1.1.1",
            level=WCAGLevel.A,
            check_fn=lambda e: False,
            message="Always fails",
            suggestion="Do something",
        )
        issue = rule.check({"tag": "div", "selector": "#test"})
        assert issue is not None
        assert isinstance(issue, AccessibilityIssue)
        assert issue.code == "always-fail"
        assert issue.message == "Always fails"
        assert issue.selector == "#test"
        assert issue.wcag_criterion == "1.1.1"
        assert issue.wcag_level == WCAGLevel.A
        assert issue.suggestion == "Do something"

    def test_check_returns_none_when_check_fn_passes(self):
        """When check_fn returns True, check() returns None."""
        rule = WCAGRule(
            code="always-pass",
            criterion="2.4.4",
            level=WCAGLevel.AA,
            check_fn=lambda e: True,
            message="Never triggers",
        )
        result = rule.check({"tag": "a", "text": "Click here"})
        assert result is None

    def test_check_uses_element_selector(self):
        """Issue picks up the 'selector' key from the element dict."""
        rule = WCAGRule(
            code="sel-test",
            criterion="1.1.1",
            level=WCAGLevel.A,
            check_fn=lambda e: False,
            message="Selector test",
        )
        issue = rule.check({"selector": "nav > ul > li:first-child"})
        assert issue.selector == "nav > ul > li:first-child"

    def test_check_missing_selector_defaults_to_empty(self):
        """If element dict has no 'selector' key, issue selector is empty."""
        rule = WCAGRule(
            code="no-sel",
            criterion="1.1.1",
            level=WCAGLevel.A,
            check_fn=lambda e: False,
            message="No selector test",
        )
        issue = rule.check({"tag": "img"})
        assert issue.selector == ""

    def test_check_issue_type_defaults_to_error(self):
        """Generated issues default to IssueType.ERROR."""
        rule = WCAGRule(
            code="type-test",
            criterion="1.1.1",
            level=WCAGLevel.A,
            check_fn=lambda e: False,
            message="Type test",
        )
        issue = rule.check({"tag": "div"})
        assert issue.issue_type == IssueType.ERROR


@pytest.mark.unit
class TestA11yCheckerCheckElements:
    """Tests for A11yChecker.check_elements() with concrete failing elements."""

    def test_img_missing_alt_produces_error(self):
        """An img element without alt attribute triggers img-alt rule."""
        checker = A11yChecker(level=WCAGLevel.AA)
        report = checker.check_elements([{"tag": "img", "selector": "#logo"}])
        assert report.errors >= 1
        codes = [i.code for i in report.issues]
        assert "img-alt" in codes

    def test_img_with_alt_passes(self):
        """An img element with alt attribute passes img-alt rule."""
        checker = A11yChecker(level=WCAGLevel.AA)
        report = checker.check_elements(
            [{"tag": "img", "alt": "Company logo", "selector": "#logo"}]
        )
        img_issues = [i for i in report.issues if i.code == "img-alt"]
        assert len(img_issues) == 0

    def test_form_input_missing_label_produces_error(self):
        """An input element without a label triggers form-label rule."""
        checker = A11yChecker(level=WCAGLevel.AA)
        report = checker.check_elements(
            [{"tag": "input", "selector": "#email"}]
        )
        codes = [i.code for i in report.issues]
        assert "form-label" in codes

    def test_form_select_missing_label(self):
        """A select element without a label triggers form-label rule."""
        checker = A11yChecker(level=WCAGLevel.AA)
        report = checker.check_elements(
            [{"tag": "select", "selector": "#country"}]
        )
        codes = [i.code for i in report.issues]
        assert "form-label" in codes

    def test_form_textarea_missing_label(self):
        """A textarea element without a label triggers form-label rule."""
        checker = A11yChecker(level=WCAGLevel.AA)
        report = checker.check_elements(
            [{"tag": "textarea", "selector": "#bio"}]
        )
        codes = [i.code for i in report.issues]
        assert "form-label" in codes

    def test_link_without_text_produces_error(self):
        """A link with empty text triggers link-text rule."""
        checker = A11yChecker(level=WCAGLevel.AA)
        report = checker.check_elements(
            [{"tag": "a", "text": "", "selector": ".skip-link"}]
        )
        codes = [i.code for i in report.issues]
        assert "link-text" in codes

    def test_link_with_whitespace_only_produces_error(self):
        """A link with only whitespace text triggers link-text rule."""
        checker = A11yChecker(level=WCAGLevel.AA)
        report = checker.check_elements(
            [{"tag": "a", "text": "   ", "selector": ".empty-link"}]
        )
        codes = [i.code for i in report.issues]
        assert "link-text" in codes

    def test_color_contrast_failure(self):
        """An element with contrast_ratio below 4.5 triggers color-contrast rule."""
        checker = A11yChecker(level=WCAGLevel.AA)
        report = checker.check_elements(
            [{"tag": "p", "contrast_ratio": 2.1, "selector": ".low-contrast"}]
        )
        codes = [i.code for i in report.issues]
        assert "color-contrast" in codes

    def test_color_contrast_passes_at_threshold(self):
        """An element with contrast_ratio of exactly 4.5 passes."""
        checker = A11yChecker(level=WCAGLevel.AA)
        report = checker.check_elements(
            [{"tag": "p", "contrast_ratio": 4.5, "selector": ".ok-contrast"}]
        )
        contrast_issues = [i for i in report.issues if i.code == "color-contrast"]
        assert len(contrast_issues) == 0

    def test_focus_indicator_missing(self):
        """A focusable element without focus style triggers focus-visible rule."""
        checker = A11yChecker(level=WCAGLevel.AA)
        report = checker.check_elements(
            [
                {
                    "tag": "button",
                    "focusable": True,
                    "has_focus_style": False,
                    "selector": "#submit",
                }
            ]
        )
        codes = [i.code for i in report.issues]
        assert "focus-visible" in codes

    def test_focus_indicator_present_passes(self):
        """A focusable element with focus style passes focus-visible rule."""
        checker = A11yChecker(level=WCAGLevel.AA)
        report = checker.check_elements(
            [
                {
                    "tag": "button",
                    "focusable": True,
                    "has_focus_style": True,
                    "selector": "#submit",
                }
            ]
        )
        focus_issues = [i for i in report.issues if i.code == "focus-visible"]
        assert len(focus_issues) == 0

    def test_multiple_elements_accumulate_errors(self):
        """Multiple failing elements each produce separate errors."""
        checker = A11yChecker(level=WCAGLevel.AA)
        elements = [
            {"tag": "img", "selector": "#img1"},
            {"tag": "img", "selector": "#img2"},
            {"tag": "a", "text": "", "selector": "#link1"},
        ]
        report = checker.check_elements(elements)
        img_issues = [i for i in report.issues if i.code == "img-alt"]
        link_issues = [i for i in report.issues if i.code == "link-text"]
        assert len(img_issues) == 2
        assert len(link_issues) == 1

    def test_empty_elements_list(self):
        """Empty element list yields clean report."""
        checker = A11yChecker(level=WCAGLevel.AA)
        report = checker.check_elements([])
        assert report.errors == 0
        assert report.passed == 0
        assert report.warnings == 0
        assert report.issues == []

    def test_report_passed_count_increments_per_rule_pass(self):
        """Each rule that passes for an element increments 'passed' count."""
        checker = A11yChecker(level=WCAGLevel.A)
        # A div element should pass all 3 A-level rules (img-alt, form-label, link-text)
        report = checker.check_elements([{"tag": "div", "selector": "#main"}])
        assert report.passed == 3
        assert report.errors == 0


@pytest.mark.unit
class TestA11yCheckerLevelFiltering:
    """Tests for WCAG level filtering in A11yChecker."""

    def test_level_a_skips_aa_rules(self):
        """Level A checker does not run AA-level rules (color-contrast, focus-visible)."""
        checker = A11yChecker(level=WCAGLevel.A)
        # Element that would fail color-contrast (AA) but passes A-level rules
        report = checker.check_elements(
            [{"tag": "p", "contrast_ratio": 1.0, "selector": ".text"}]
        )
        codes = [i.code for i in report.issues]
        assert "color-contrast" not in codes
        assert "focus-visible" not in codes

    def test_level_a_skips_aaa_rules(self):
        """Level A checker does not run AAA-level rules."""
        checker = A11yChecker(level=WCAGLevel.A)
        checker.add_rule(
            WCAGRule(
                code="aaa-only",
                criterion="3.1.2",
                level=WCAGLevel.AAA,
                check_fn=lambda e: False,
                message="AAA only rule",
            )
        )
        report = checker.check_elements([{"tag": "div", "selector": "#x"}])
        codes = [i.code for i in report.issues]
        assert "aaa-only" not in codes

    def test_level_aa_includes_a_and_aa(self):
        """Level AA checker runs both A-level and AA-level rules."""
        checker = A11yChecker(level=WCAGLevel.AA)
        # img missing alt (A-level) + low contrast (AA-level)
        report = checker.check_elements(
            [
                {
                    "tag": "img",
                    "contrast_ratio": 2.0,
                    "selector": "#hero",
                }
            ]
        )
        codes = [i.code for i in report.issues]
        assert "img-alt" in codes
        assert "color-contrast" in codes

    def test_level_aa_skips_aaa(self):
        """Level AA checker does not run AAA-level rules."""
        checker = A11yChecker(level=WCAGLevel.AA)
        checker.add_rule(
            WCAGRule(
                code="aaa-skip",
                criterion="3.1.2",
                level=WCAGLevel.AAA,
                check_fn=lambda e: False,
                message="AAA rule skipped",
            )
        )
        report = checker.check_elements([{"tag": "div", "selector": "#y"}])
        codes = [i.code for i in report.issues]
        assert "aaa-skip" not in codes

    def test_level_aaa_includes_all(self):
        """Level AAA checker runs A, AA, and AAA rules."""
        checker = A11yChecker(level=WCAGLevel.AAA)
        checker.add_rule(
            WCAGRule(
                code="aaa-rule",
                criterion="3.1.2",
                level=WCAGLevel.AAA,
                check_fn=lambda e: False,
                message="AAA rule triggered",
            )
        )
        # Failing element triggers A-level (img-alt), AA-level (color-contrast), AAA
        report = checker.check_elements(
            [{"tag": "img", "contrast_ratio": 1.0, "selector": "#img"}]
        )
        codes = [i.code for i in report.issues]
        assert "img-alt" in codes
        assert "color-contrast" in codes
        assert "aaa-rule" in codes


@pytest.mark.unit
class TestA11yCheckerAddRule:
    """Tests for A11yChecker.add_rule() with custom rules."""

    def test_custom_rule_is_applied(self):
        """A custom rule added via add_rule() is evaluated during check."""
        checker = A11yChecker(level=WCAGLevel.AA)
        checker.add_rule(
            WCAGRule(
                code="custom-aria",
                criterion="4.1.2",
                level=WCAGLevel.A,
                check_fn=lambda e: bool(e.get("aria_label")),
                message="Must have aria-label",
                suggestion="Add aria-label attribute",
            )
        )
        report = checker.check_elements(
            [{"tag": "div", "role": "button", "selector": "#btn"}]
        )
        codes = [i.code for i in report.issues]
        assert "custom-aria" in codes

    def test_custom_rule_passes_when_satisfied(self):
        """A custom rule does not produce an issue when the check passes."""
        checker = A11yChecker(level=WCAGLevel.AA)
        checker.add_rule(
            WCAGRule(
                code="custom-aria",
                criterion="4.1.2",
                level=WCAGLevel.A,
                check_fn=lambda e: bool(e.get("aria_label")),
                message="Must have aria-label",
            )
        )
        report = checker.check_elements(
            [{"tag": "div", "aria_label": "Close dialog", "selector": "#btn"}]
        )
        custom_issues = [i for i in report.issues if i.code == "custom-aria"]
        assert len(custom_issues) == 0

    def test_multiple_custom_rules(self):
        """Multiple custom rules can be added and all are evaluated."""
        checker = A11yChecker(level=WCAGLevel.AA)
        checker.add_rule(
            WCAGRule(
                code="custom-1",
                criterion="1.0.0",
                level=WCAGLevel.A,
                check_fn=lambda e: False,
                message="Custom 1",
            )
        )
        checker.add_rule(
            WCAGRule(
                code="custom-2",
                criterion="2.0.0",
                level=WCAGLevel.A,
                check_fn=lambda e: False,
                message="Custom 2",
            )
        )
        report = checker.check_elements([{"tag": "div", "selector": "#z"}])
        codes = [i.code for i in report.issues]
        assert "custom-1" in codes
        assert "custom-2" in codes


@pytest.mark.unit
class TestCalculateContrastRatioEdgeCases:
    """Edge case tests for calculate_contrast_ratio."""

    def test_invalid_hex_returns_zero(self):
        """Invalid hex color strings return 0.0."""
        assert calculate_contrast_ratio("invalid", "#ffffff") == 0.0

    def test_partially_invalid_hex_returns_zero(self):
        """A hex that is too short returns 0.0."""
        assert calculate_contrast_ratio("#ff", "#ffffff") == 0.0

    def test_empty_string_returns_zero(self):
        """Empty strings return 0.0."""
        assert calculate_contrast_ratio("", "") == 0.0

    def test_three_char_hex_not_supported(self):
        """3-char hex shorthand (#fff) is not expanded -- returns 0.0."""
        # The implementation slices hex_color[i:i+2] for i in (0,2,4),
        # so '#fff' (3 chars after strip) produces a ValueError/IndexError.
        result = calculate_contrast_ratio("#fff", "#000")
        assert result == 0.0

    def test_without_hash_prefix(self):
        """Hex without '#' prefix also works (lstrip removes '#')."""
        ratio = calculate_contrast_ratio("000000", "ffffff")
        assert ratio >= 21.0

    def test_white_on_white(self):
        """White on white yields ratio of 1.0."""
        assert calculate_contrast_ratio("#ffffff", "#ffffff") == 1.0

    def test_symmetric(self):
        """Contrast ratio is the same regardless of fg/bg order."""
        r1 = calculate_contrast_ratio("#123456", "#abcdef")
        r2 = calculate_contrast_ratio("#abcdef", "#123456")
        assert r1 == r2

    def test_known_contrast_ratio(self):
        """Black on white should be 21:1."""
        ratio = calculate_contrast_ratio("#000000", "#ffffff")
        assert abs(ratio - 21.0) < 0.1


@pytest.mark.unit
class TestCheckHeadingHierarchyBehavioral:
    """Behavioral tests for check_heading_hierarchy."""

    def test_document_not_starting_with_h1(self):
        """Document starting with h2 reports 'Document should start with h1'."""
        issues = check_heading_hierarchy([2, 3])
        assert any("should start with h1" in msg for msg in issues)

    def test_document_starting_with_h3(self):
        """Document starting with h3 reports skip AND missing h1."""
        issues = check_heading_hierarchy([3])
        skip_issues = [i for i in issues if "Skipped" in i]
        h1_issues = [i for i in issues if "h1" in i]
        assert len(skip_issues) >= 1
        assert len(h1_issues) >= 1

    def test_multiple_skips(self):
        """Multiple heading skips produce multiple issues."""
        # h1 -> h3 (skip h2) -> h6 (skip h4,h5)
        issues = check_heading_hierarchy([1, 3, 6])
        skip_issues = [i for i in issues if "Skipped" in i]
        assert len(skip_issues) == 2

    def test_valid_hierarchy_no_issues(self):
        """A valid heading hierarchy [1, 2, 3] produces no issues."""
        issues = check_heading_hierarchy([1, 2, 3])
        assert len(issues) == 0

    def test_repeated_same_level(self):
        """Repeated same level headings [1, 2, 2, 2] are valid."""
        issues = check_heading_hierarchy([1, 2, 2, 2])
        assert len(issues) == 0

    def test_going_back_up_levels(self):
        """Going from h3 back to h2 is valid (no skip)."""
        issues = check_heading_hierarchy([1, 2, 3, 2, 3])
        assert len(issues) == 0

    def test_single_h1(self):
        """A single h1 heading produces no issues."""
        issues = check_heading_hierarchy([1])
        assert len(issues) == 0

    def test_skip_message_contains_levels(self):
        """Skip message indicates which levels were skipped."""
        issues = check_heading_hierarchy([1, 4])
        assert any("h1" in i and "h4" in i for i in issues)


# =============================================================================
# REPORTER TESTS
# =============================================================================


@pytest.mark.unit
class TestAccessibilityReporterSummary:
    """Tests for AccessibilityReporter.to_summary()."""

    def test_summary_format(self):
        """Summary follows 'Score: X% | N passed, N errors, N warnings' format."""
        report = AccessibilityReport(passed=17, errors=2, warnings=1)
        reporter = AccessibilityReporter(report)
        summary = reporter.to_summary()
        assert "Score: " in summary
        assert "17 passed" in summary
        assert "2 errors" in summary
        assert "1 warnings" in summary

    def test_summary_score_value(self):
        """Summary reflects the correct score percentage."""
        report = AccessibilityReport(passed=8, errors=2, warnings=0)
        reporter = AccessibilityReporter(report)
        summary = reporter.to_summary()
        assert "Score: 80.0%" in summary

    def test_summary_clean_report(self):
        """Clean report shows 100.0%."""
        report = AccessibilityReport(passed=10, errors=0, warnings=0)
        reporter = AccessibilityReporter(report)
        summary = reporter.to_summary()
        assert "Score: 100.0%" in summary
        assert "0 errors" in summary

    def test_summary_empty_report(self):
        """Empty report (no checks) shows 100.0%."""
        report = AccessibilityReport()
        reporter = AccessibilityReporter(report)
        summary = reporter.to_summary()
        assert "Score: 100.0%" in summary


@pytest.mark.unit
class TestAccessibilityReporterDict:
    """Tests for AccessibilityReporter.to_dict()."""

    def test_dict_contains_all_keys(self):
        """Dict has url, score, passed, errors, warnings, issues keys."""
        report = AccessibilityReport(passed=5, errors=1, warnings=2)
        reporter = AccessibilityReporter(report)
        d = reporter.to_dict()
        assert "url" in d
        assert "score" in d
        assert "passed" in d
        assert "errors" in d
        assert "warnings" in d
        assert "issues" in d

    def test_dict_score_is_rounded(self):
        """Score in dict is rounded to 1 decimal place."""
        report = AccessibilityReport(passed=2, errors=1)
        reporter = AccessibilityReporter(report)
        d = reporter.to_dict()
        # 2/(2+1) * 100 = 66.666... -> 66.7
        assert d["score"] == 66.7

    def test_dict_issues_serialized(self):
        """Issues in dict are serialized with all fields."""
        issue = AccessibilityIssue(
            code="img-alt",
            message="Missing alt",
            selector="#logo",
            issue_type=IssueType.ERROR,
            wcag_criterion="1.1.1",
            wcag_level=WCAGLevel.A,
            suggestion="Add alt",
        )
        report = AccessibilityReport(issues=[issue], errors=1)
        reporter = AccessibilityReporter(report)
        d = reporter.to_dict()
        assert len(d["issues"]) == 1
        i = d["issues"][0]
        assert i["code"] == "img-alt"
        assert i["issue_type"] == "error"
        assert i["wcag_level"] == "A"
        assert i["suggestion"] == "Add alt"

    def test_dict_empty_issues(self):
        """Empty report has empty issues list in dict."""
        report = AccessibilityReport()
        reporter = AccessibilityReporter(report)
        d = reporter.to_dict()
        assert d["issues"] == []


@pytest.mark.unit
class TestAccessibilityReporterJSON:
    """Tests for AccessibilityReporter.to_json()."""

    def test_json_is_valid(self):
        """to_json() produces valid JSON."""
        report = AccessibilityReport(passed=3, errors=1)
        reporter = AccessibilityReporter(report)
        parsed = json.loads(reporter.to_json())
        assert isinstance(parsed, dict)

    def test_json_default_indent(self):
        """Default indent is 2."""
        report = AccessibilityReport()
        reporter = AccessibilityReporter(report)
        j = reporter.to_json()
        # indent=2 produces lines starting with 2 spaces
        assert "\n  " in j

    def test_json_custom_indent(self):
        """Custom indent value is respected."""
        report = AccessibilityReport()
        reporter = AccessibilityReporter(report)
        j = reporter.to_json(indent=4)
        assert "\n    " in j

    def test_json_roundtrip_matches_dict(self):
        """JSON parses back to the same structure as to_dict()."""
        issue = AccessibilityIssue(code="test", message="test msg")
        report = AccessibilityReport(
            url="https://example.com", issues=[issue], passed=5, errors=1
        )
        reporter = AccessibilityReporter(report)
        assert json.loads(reporter.to_json()) == reporter.to_dict()


@pytest.mark.unit
class TestAccessibilityReporterMarkdown:
    """Tests for AccessibilityReporter.to_markdown()."""

    def test_markdown_has_heading(self):
        """Markdown output starts with an h1 heading."""
        report = AccessibilityReport()
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert md.startswith("# Accessibility Report")

    def test_markdown_contains_score(self):
        """Markdown includes the score percentage."""
        report = AccessibilityReport(passed=9, errors=1)
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert "90.0%" in md

    def test_markdown_includes_url_when_set(self):
        """Markdown includes URL when report has one."""
        report = AccessibilityReport(url="https://example.com")
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert "https://example.com" in md

    def test_markdown_no_url_when_empty(self):
        """Markdown omits URL line when report URL is empty."""
        report = AccessibilityReport(url="")
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert "**URL**" not in md

    def test_markdown_has_issues_table_when_issues_exist(self):
        """Markdown includes a table of issues when there are issues."""
        issue = AccessibilityIssue(
            code="img-alt",
            message="Missing alt text",
            selector="#logo",
            wcag_level=WCAGLevel.A,
            suggestion="Add alt attribute",
        )
        report = AccessibilityReport(issues=[issue], errors=1)
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert "## Issues" in md
        assert "| Code |" in md
        assert "img-alt" in md
        assert "Missing alt text" in md

    def test_markdown_no_issues_table_when_clean(self):
        """Markdown does not include issues table when there are no issues."""
        report = AccessibilityReport(passed=5)
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert "## Issues" not in md

    def test_markdown_is_string(self):
        """to_markdown() returns a string."""
        report = AccessibilityReport()
        reporter = AccessibilityReporter(report)
        assert isinstance(reporter.to_markdown(), str)
