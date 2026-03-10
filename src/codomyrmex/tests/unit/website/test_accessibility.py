"""Zero-mock tests for website/accessibility: models, checker, reporters, utils."""

from __future__ import annotations

import json

import pytest

from codomyrmex.website.accessibility.checker import A11yChecker
from codomyrmex.website.accessibility.models import (
    AccessibilityIssue,
    AccessibilityReport,
    IssueType,
    WCAGLevel,
    WCAGRule,
)
from codomyrmex.website.accessibility.reporters import AccessibilityReporter
from codomyrmex.website.accessibility.utils import (
    calculate_contrast_ratio,
    check_heading_hierarchy,
)

# ---------------------------------------------------------------------------
# WCAGLevel enum
# ---------------------------------------------------------------------------


class TestWCAGLevel:
    def test_level_a_value(self):
        assert WCAGLevel.A.value == "A"

    def test_level_aa_value(self):
        assert WCAGLevel.AA.value == "AA"

    def test_level_aaa_value(self):
        assert WCAGLevel.AAA.value == "AAA"

    def test_members_count(self):
        assert len(WCAGLevel) == 3

    def test_enum_from_value(self):
        assert WCAGLevel("AA") == WCAGLevel.AA


# ---------------------------------------------------------------------------
# IssueType enum
# ---------------------------------------------------------------------------


class TestIssueType:
    def test_error_value(self):
        assert IssueType.ERROR.value == "error"

    def test_warning_value(self):
        assert IssueType.WARNING.value == "warning"

    def test_notice_value(self):
        assert IssueType.NOTICE.value == "notice"

    def test_members_count(self):
        assert len(IssueType) == 3


# ---------------------------------------------------------------------------
# AccessibilityIssue dataclass
# ---------------------------------------------------------------------------


class TestAccessibilityIssue:
    def test_required_fields(self):
        issue = AccessibilityIssue(code="img-alt", message="Images need alt text")
        assert issue.code == "img-alt"
        assert issue.message == "Images need alt text"

    def test_defaults(self):
        issue = AccessibilityIssue(code="x", message="y")
        assert issue.selector == ""
        assert issue.issue_type == IssueType.ERROR
        assert issue.wcag_criterion == ""
        assert issue.wcag_level == WCAGLevel.A
        assert issue.suggestion == ""

    def test_explicit_fields(self):
        issue = AccessibilityIssue(
            code="form-label",
            message="Form must have label",
            selector="input#name",
            issue_type=IssueType.WARNING,
            wcag_criterion="1.3.1",
            wcag_level=WCAGLevel.AA,
            suggestion="Add aria-label",
        )
        assert issue.selector == "input#name"
        assert issue.issue_type == IssueType.WARNING
        assert issue.wcag_criterion == "1.3.1"
        assert issue.wcag_level == WCAGLevel.AA
        assert issue.suggestion == "Add aria-label"


# ---------------------------------------------------------------------------
# AccessibilityReport dataclass
# ---------------------------------------------------------------------------


class TestAccessibilityReport:
    def test_empty_report_defaults(self):
        report = AccessibilityReport()
        assert report.url == ""
        assert report.issues == []
        assert report.passed == 0
        assert report.errors == 0
        assert report.warnings == 0

    def test_score_empty_report(self):
        report = AccessibilityReport()
        assert report.score == 100.0

    def test_score_all_passed(self):
        report = AccessibilityReport(passed=10, errors=0)
        assert report.score == 100.0

    def test_score_all_errors(self):
        report = AccessibilityReport(passed=0, errors=5)
        assert report.score == 0.0

    def test_score_mixed(self):
        report = AccessibilityReport(passed=8, errors=2)
        assert report.score == pytest.approx(80.0)

    def test_score_ignores_warnings(self):
        # warnings do NOT contribute to score denominator
        report = AccessibilityReport(passed=10, errors=0, warnings=3)
        assert report.score == 100.0

    def test_url_stored(self):
        report = AccessibilityReport(url="https://example.com")
        assert report.url == "https://example.com"

    def test_issues_list_is_independent(self):
        r1 = AccessibilityReport()
        r2 = AccessibilityReport()
        r1.issues.append(AccessibilityIssue(code="x", message="y"))
        assert len(r2.issues) == 0


# ---------------------------------------------------------------------------
# WCAGRule
# ---------------------------------------------------------------------------


class TestWCAGRule:
    @pytest.fixture
    def passing_rule(self):
        return WCAGRule(
            code="test-rule",
            criterion="1.1.1",
            level=WCAGLevel.A,
            check_fn=lambda e: True,
            message="Must pass",
            suggestion="Do the thing",
        )

    @pytest.fixture
    def failing_rule(self):
        return WCAGRule(
            code="fail-rule",
            criterion="2.2.2",
            level=WCAGLevel.AA,
            check_fn=lambda e: False,
            message="Always fails",
            suggestion="Fix it",
        )

    def test_rule_attributes(self, passing_rule):
        assert passing_rule.code == "test-rule"
        assert passing_rule.criterion == "1.1.1"
        assert passing_rule.level == WCAGLevel.A
        assert passing_rule.message == "Must pass"
        assert passing_rule.suggestion == "Do the thing"

    def test_check_passes_returns_none(self, passing_rule):
        result = passing_rule.check({"tag": "div"})
        assert result is None

    def test_check_fails_returns_issue(self, failing_rule):
        result = failing_rule.check({"tag": "span", "selector": "span.foo"})
        assert isinstance(result, AccessibilityIssue)
        assert result.code == "fail-rule"
        assert result.message == "Always fails"
        assert result.wcag_criterion == "2.2.2"
        assert result.wcag_level == WCAGLevel.AA
        assert result.suggestion == "Fix it"

    def test_check_uses_selector_from_element(self, failing_rule):
        result = failing_rule.check({"selector": "#my-id"})
        assert result.selector == "#my-id"

    def test_check_uses_empty_selector_when_missing(self, failing_rule):
        result = failing_rule.check({})
        assert result.selector == ""

    def test_optional_suggestion_default(self):
        rule = WCAGRule(
            code="c",
            criterion="3.3.1",
            level=WCAGLevel.AAA,
            check_fn=lambda e: False,
            message="msg",
        )
        result = rule.check({})
        assert result.suggestion == ""


# ---------------------------------------------------------------------------
# A11yChecker
# ---------------------------------------------------------------------------


class TestA11ycheckerDefaultRules:
    @pytest.fixture
    def checker_aa(self):
        return A11yChecker(level=WCAGLevel.AA)

    @pytest.fixture
    def checker_a(self):
        return A11yChecker(level=WCAGLevel.A)

    def test_default_rules_loaded(self, checker_aa):
        assert len(checker_aa._rules) == 5

    def test_img_without_alt_fails(self, checker_aa):
        report = checker_aa.check_elements([{"tag": "img", "selector": "img.hero"}])
        codes = [i.code for i in report.issues]
        assert "img-alt" in codes

    def test_img_with_alt_passes(self, checker_aa):
        report = checker_aa.check_elements([{"tag": "img", "alt": "Logo"}])
        codes = [i.code for i in report.issues]
        assert "img-alt" not in codes

    def test_form_input_without_label_fails(self, checker_aa):
        report = checker_aa.check_elements([{"tag": "input", "selector": "input#name"}])
        codes = [i.code for i in report.issues]
        assert "form-label" in codes

    def test_form_input_with_label_passes(self, checker_aa):
        report = checker_aa.check_elements([{"tag": "input", "label": "Full name"}])
        codes = [i.code for i in report.issues]
        assert "form-label" not in codes

    def test_select_without_label_fails(self, checker_aa):
        report = checker_aa.check_elements([{"tag": "select"}])
        codes = [i.code for i in report.issues]
        assert "form-label" in codes

    def test_textarea_without_label_fails(self, checker_aa):
        report = checker_aa.check_elements([{"tag": "textarea"}])
        codes = [i.code for i in report.issues]
        assert "form-label" in codes

    def test_link_without_text_fails(self, checker_aa):
        report = checker_aa.check_elements([{"tag": "a", "text": "   "}])
        codes = [i.code for i in report.issues]
        assert "link-text" in codes

    def test_link_with_text_passes(self, checker_aa):
        report = checker_aa.check_elements([{"tag": "a", "text": "Read more"}])
        codes = [i.code for i in report.issues]
        assert "link-text" not in codes

    def test_low_contrast_fails(self, checker_aa):
        report = checker_aa.check_elements([{"contrast_ratio": 2.0}])
        codes = [i.code for i in report.issues]
        assert "color-contrast" in codes

    def test_sufficient_contrast_passes(self, checker_aa):
        report = checker_aa.check_elements([{"contrast_ratio": 5.0}])
        codes = [i.code for i in report.issues]
        assert "color-contrast" not in codes

    def test_exact_contrast_boundary_passes(self, checker_aa):
        report = checker_aa.check_elements([{"contrast_ratio": 4.5}])
        codes = [i.code for i in report.issues]
        assert "color-contrast" not in codes

    def test_focusable_without_focus_style_fails(self, checker_aa):
        report = checker_aa.check_elements([
            {"focusable": True, "has_focus_style": False}
        ])
        codes = [i.code for i in report.issues]
        assert "focus-visible" in codes

    def test_focusable_with_focus_style_passes(self, checker_aa):
        report = checker_aa.check_elements([
            {"focusable": True, "has_focus_style": True}
        ])
        codes = [i.code for i in report.issues]
        assert "focus-visible" not in codes

    def test_non_focusable_skip_focus_check(self, checker_aa):
        report = checker_aa.check_elements([{"focusable": False}])
        codes = [i.code for i in report.issues]
        assert "focus-visible" not in codes

    def test_level_a_skips_aa_rules(self, checker_a):
        # color-contrast is AA, focus-visible is AA — should be skipped
        report = checker_a.check_elements([
            {"contrast_ratio": 1.0, "focusable": True, "has_focus_style": False}
        ])
        codes = [i.code for i in report.issues]
        assert "color-contrast" not in codes
        assert "focus-visible" not in codes

    def test_empty_elements_empty_report(self, checker_aa):
        report = checker_aa.check_elements([])
        assert report.errors == 0
        assert report.warnings == 0
        assert report.passed == 0

    def test_passed_count_increments(self, checker_aa):
        report = checker_aa.check_elements([
            {"tag": "img", "alt": "ok"},
            {"tag": "a", "text": "click"},
        ])
        assert report.passed > 0

    def test_errors_count_increments(self, checker_aa):
        report = checker_aa.check_elements([
            {"tag": "img"},  # no alt — should fire img-alt
        ])
        assert report.errors > 0

    def test_report_type(self, checker_aa):
        report = checker_aa.check_elements([])
        assert isinstance(report, AccessibilityReport)

    def test_add_custom_rule(self, checker_aa):
        custom = WCAGRule(
            code="custom-check",
            criterion="4.1.2",
            level=WCAGLevel.A,
            check_fn=lambda e: bool(e.get("role")),
            message="Element must have ARIA role",
        )
        checker_aa.add_rule(custom)
        assert len(checker_aa._rules) == 6
        report = checker_aa.check_elements([{"tag": "div"}])
        codes = [i.code for i in report.issues]
        assert "custom-check" in codes

    def test_multiple_elements_aggregated(self, checker_aa):
        elements = [
            {"tag": "img"},       # fails img-alt
            {"tag": "img", "alt": "logo"},  # passes img-alt
        ]
        report = checker_aa.check_elements(elements)
        assert report.errors >= 1
        assert report.passed >= 1


# ---------------------------------------------------------------------------
# AccessibilityReporter
# ---------------------------------------------------------------------------


class TestAccessibilityReporter:
    @pytest.fixture
    def empty_report(self):
        return AccessibilityReport(url="https://example.com", passed=0)

    @pytest.fixture
    def report_with_issues(self):
        issue = AccessibilityIssue(
            code="img-alt",
            message="Images must have alt text",
            selector="img.hero",
            issue_type=IssueType.ERROR,
            wcag_criterion="1.1.1",
            wcag_level=WCAGLevel.A,
            suggestion="Add alt attribute",
        )
        return AccessibilityReport(
            url="https://test.com",
            issues=[issue],
            passed=5,
            errors=1,
            warnings=0,
        )

    def test_to_summary_format(self, report_with_issues):
        reporter = AccessibilityReporter(report_with_issues)
        summary = reporter.to_summary()
        assert "Score:" in summary
        assert "passed" in summary
        assert "errors" in summary
        assert "warnings" in summary

    def test_to_summary_score_value(self, report_with_issues):
        reporter = AccessibilityReporter(report_with_issues)
        summary = reporter.to_summary()
        # passed=5, errors=1 → score = 5/6 * 100 ≈ 83.3%
        assert "83.3%" in summary

    def test_to_summary_perfect_score(self):
        report = AccessibilityReport(passed=10, errors=0)
        reporter = AccessibilityReporter(report)
        assert "100.0%" in reporter.to_summary()

    def test_to_dict_keys(self, report_with_issues):
        reporter = AccessibilityReporter(report_with_issues)
        d = reporter.to_dict()
        assert set(d.keys()) == {"url", "score", "passed", "errors", "warnings", "issues"}

    def test_to_dict_url(self, report_with_issues):
        reporter = AccessibilityReporter(report_with_issues)
        assert reporter.to_dict()["url"] == "https://test.com"

    def test_to_dict_issues_list(self, report_with_issues):
        reporter = AccessibilityReporter(report_with_issues)
        d = reporter.to_dict()
        assert len(d["issues"]) == 1
        issue_d = d["issues"][0]
        assert issue_d["code"] == "img-alt"
        assert issue_d["issue_type"] == "error"
        assert issue_d["wcag_level"] == "A"

    def test_to_dict_empty_issues(self, empty_report):
        reporter = AccessibilityReporter(empty_report)
        assert reporter.to_dict()["issues"] == []

    def test_to_json_valid(self, report_with_issues):
        reporter = AccessibilityReporter(report_with_issues)
        raw = reporter.to_json()
        parsed = json.loads(raw)
        assert parsed["url"] == "https://test.com"
        assert isinstance(parsed["issues"], list)

    def test_to_json_indent(self, report_with_issues):
        reporter = AccessibilityReporter(report_with_issues)
        raw = reporter.to_json(indent=4)
        # 4-space indented JSON has 4-space lines
        assert "    " in raw

    def test_to_markdown_header(self, report_with_issues):
        reporter = AccessibilityReporter(report_with_issues)
        md = reporter.to_markdown()
        assert md.startswith("# Accessibility Report")

    def test_to_markdown_contains_score(self, report_with_issues):
        reporter = AccessibilityReporter(report_with_issues)
        md = reporter.to_markdown()
        assert "**Score**" in md

    def test_to_markdown_url_included_when_set(self, report_with_issues):
        reporter = AccessibilityReporter(report_with_issues)
        md = reporter.to_markdown()
        assert "https://test.com" in md

    def test_to_markdown_no_url_section_when_empty(self):
        report = AccessibilityReport(passed=3)
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert "**URL**" not in md

    def test_to_markdown_issues_table_present(self, report_with_issues):
        reporter = AccessibilityReporter(report_with_issues)
        md = reporter.to_markdown()
        assert "## Issues" in md
        assert "| Code" in md

    def test_to_markdown_no_issues_table_when_clean(self):
        report = AccessibilityReport(passed=10)
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert "## Issues" not in md

    def test_to_markdown_issue_row_content(self, report_with_issues):
        reporter = AccessibilityReporter(report_with_issues)
        md = reporter.to_markdown()
        assert "img-alt" in md
        assert "Add alt attribute" in md


# ---------------------------------------------------------------------------
# utils: calculate_contrast_ratio
# ---------------------------------------------------------------------------


class TestCalculateContrastRatio:
    def test_black_on_white(self):
        ratio = calculate_contrast_ratio("#000000", "#ffffff")
        assert ratio == pytest.approx(21.0, rel=0.01)

    def test_white_on_black(self):
        ratio = calculate_contrast_ratio("#ffffff", "#000000")
        assert ratio == pytest.approx(21.0, rel=0.01)

    def test_same_color_returns_one(self):
        ratio = calculate_contrast_ratio("#808080", "#808080")
        assert ratio == pytest.approx(1.0, rel=0.01)

    def test_invalid_color_returns_zero(self):
        ratio = calculate_contrast_ratio("not-a-color", "#ffffff")
        assert ratio == 0.0

    def test_short_hex_invalid_returns_zero(self):
        # only 4 chars after strip, int() parse will raise ValueError
        ratio = calculate_contrast_ratio("#xyz", "#ffffff")
        assert ratio == 0.0

    def test_without_hash_prefix(self):
        # lstrip("#") handles both with and without hash
        ratio_with = calculate_contrast_ratio("#000000", "#ffffff")
        ratio_without = calculate_contrast_ratio("000000", "ffffff")
        assert ratio_with == pytest.approx(ratio_without, rel=0.01)

    def test_grey_on_white_is_aa_insufficient(self):
        # #767676 on white is roughly at 4.54 (barely passes AA)
        ratio = calculate_contrast_ratio("#767676", "#ffffff")
        assert ratio >= 4.0

    def test_return_type_float(self):
        result = calculate_contrast_ratio("#000000", "#ffffff")
        assert isinstance(result, float)


# ---------------------------------------------------------------------------
# utils: check_heading_hierarchy
# ---------------------------------------------------------------------------


class TestCheckHeadingHierarchy:
    def test_proper_hierarchy_no_issues(self):
        issues = check_heading_hierarchy([1, 2, 3])
        assert issues == []

    def test_empty_headings_no_issues(self):
        issues = check_heading_hierarchy([])
        assert issues == []

    def test_starts_with_h2_reports_issue(self):
        issues = check_heading_hierarchy([2, 3])
        assert any("h1" in i for i in issues)

    def test_skipped_level_reports_issue(self):
        issues = check_heading_hierarchy([1, 3])
        assert any("Skipped" in i for i in issues)

    def test_h1_to_h3_skip_reported(self):
        issues = check_heading_hierarchy([1, 3])
        assert len(issues) == 1
        assert "h1 to h3" in issues[0]

    def test_multiple_skips_reported(self):
        # 1→4 skips 2 and 3
        issues = check_heading_hierarchy([1, 4])
        skip_issues = [i for i in issues if "Skipped" in i]
        assert len(skip_issues) == 1  # one check per consecutive pair

    def test_h1_single_no_issues(self):
        issues = check_heading_hierarchy([1])
        assert issues == []

    def test_same_level_repeated_ok(self):
        issues = check_heading_hierarchy([1, 2, 2, 3])
        assert issues == []

    def test_start_with_h3_gives_start_issue(self):
        issues = check_heading_hierarchy([3])
        assert any("h1" in i for i in issues)

    def test_proper_flat_h1_only(self):
        issues = check_heading_hierarchy([1, 1, 1])
        assert issues == []

    def test_return_type_is_list(self):
        result = check_heading_hierarchy([1, 2])
        assert isinstance(result, list)
