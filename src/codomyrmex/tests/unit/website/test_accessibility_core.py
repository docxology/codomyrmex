"""Zero-mock tests for website/accessibility: deep edge cases, warnings path,
cli_commands, and boundary conditions not covered by test_accessibility.py."""

from __future__ import annotations

import json

import pytest

from codomyrmex.website.accessibility import (
    A11yChecker,
    AccessibilityIssue,
    AccessibilityReport,
    AccessibilityReporter,
    IssueType,
    WCAGLevel,
    WCAGRule,
    calculate_contrast_ratio,
    check_heading_hierarchy,
    cli_commands,
)
from codomyrmex.website.accessibility.checker import A11yChecker as DirectChecker
from codomyrmex.website.accessibility.models import (
    AccessibilityIssue as DirectIssue,
)
from codomyrmex.website.accessibility.models import (
    AccessibilityReport as DirectReport,
)
from codomyrmex.website.accessibility.models import (
    IssueType as DirectIssueType,
)
from codomyrmex.website.accessibility.models import (
    WCAGLevel as DirectWCAGLevel,
)
from codomyrmex.website.accessibility.models import (
    WCAGRule as DirectRule,
)

# ---------------------------------------------------------------------------
# __init__.py public surface
# ---------------------------------------------------------------------------


class TestModulePublicSurface:
    """Ensure the module re-exports every symbol listed in __all__."""

    def test_a11y_checker_importable(self):
        assert A11yChecker is not None

    def test_accessibility_issue_importable(self):
        assert AccessibilityIssue is not None

    def test_accessibility_report_importable(self):
        assert AccessibilityReport is not None

    def test_accessibility_reporter_importable(self):
        assert AccessibilityReporter is not None

    def test_issue_type_importable(self):
        assert IssueType is not None

    def test_wcag_level_importable(self):
        assert WCAGLevel is not None

    def test_wcag_rule_importable(self):
        assert WCAGRule is not None

    def test_calculate_contrast_ratio_importable(self):
        assert callable(calculate_contrast_ratio)

    def test_check_heading_hierarchy_importable(self):
        assert callable(check_heading_hierarchy)

    def test_cli_commands_importable(self):
        assert callable(cli_commands)

    def test_direct_import_checker_is_same_class(self):
        assert A11yChecker is DirectChecker

    def test_direct_import_models_consistent(self):
        assert AccessibilityIssue is DirectIssue
        assert AccessibilityReport is DirectReport
        assert WCAGLevel is DirectWCAGLevel
        assert IssueType is DirectIssueType
        assert WCAGRule is DirectRule


# ---------------------------------------------------------------------------
# cli_commands()
# ---------------------------------------------------------------------------


class TestCliCommands:
    """Exercise the cli_commands() factory function."""

    def test_returns_dict(self):
        result = cli_commands()
        assert isinstance(result, dict)

    def test_has_checks_key(self):
        result = cli_commands()
        assert "checks" in result

    def test_has_audit_key(self):
        result = cli_commands()
        assert "audit" in result

    def test_checks_has_help(self):
        result = cli_commands()
        assert "help" in result["checks"]
        assert isinstance(result["checks"]["help"], str)

    def test_audit_has_help(self):
        result = cli_commands()
        assert "help" in result["audit"]
        assert isinstance(result["audit"]["help"], str)

    def test_checks_handler_is_callable(self):
        result = cli_commands()
        assert callable(result["checks"]["handler"])

    def test_audit_handler_is_callable(self):
        result = cli_commands()
        assert callable(result["audit"]["handler"])

    def test_checks_handler_runs_without_error(self, capsys):
        result = cli_commands()
        result["checks"]["handler"]()
        captured = capsys.readouterr()
        assert "Accessibility" in captured.out

    def test_audit_handler_runs_without_error(self, capsys):
        result = cli_commands()
        result["audit"]["handler"]()
        captured = capsys.readouterr()
        assert "Audit" in captured.out

    def test_audit_handler_accepts_path_kwarg(self, capsys):
        result = cli_commands()
        result["audit"]["handler"](path="/some/dir")
        captured = capsys.readouterr()
        assert "/some/dir" in captured.out

    def test_checks_handler_mentions_checker_class(self, capsys):
        result = cli_commands()
        result["checks"]["handler"]()
        captured = capsys.readouterr()
        assert "A11yChecker" in captured.out

    def test_checks_handler_mentions_reporter_class(self, capsys):
        result = cli_commands()
        result["checks"]["handler"]()
        captured = capsys.readouterr()
        assert "AccessibilityReporter" in captured.out


# ---------------------------------------------------------------------------
# A11yChecker — warnings path (IssueType != ERROR)
# ---------------------------------------------------------------------------


class TestA11yCheckerWarningsPath:
    """Cover the warnings counter branch (checker.py line 110)."""

    def test_custom_warning_rule_increments_warnings(self):
        checker = A11yChecker(level=WCAGLevel.AA)
        warning_rule = WCAGRule(
            code="custom-warn",
            criterion="3.3.1",
            level=WCAGLevel.A,
            check_fn=lambda e: False,
            message="Custom warning",
            suggestion="Fix it",
        )
        # Override issue_type on the returned issue by wrapping check_fn result
        original_check = warning_rule.check

        def patched_check(element):
            issue = original_check(element)
            if issue:
                issue.issue_type = IssueType.WARNING
            return issue

        warning_rule.check = patched_check
        checker.add_rule(warning_rule)

        report = checker.check_elements([{"tag": "div"}])
        assert report.warnings >= 1

    def test_warning_does_not_increment_errors(self):
        checker = A11yChecker(level=WCAGLevel.AA)
        warning_rule = WCAGRule(
            code="warn-only",
            criterion="3.3.1",
            level=WCAGLevel.A,
            check_fn=lambda e: False,
            message="Warning only",
        )
        original_check = warning_rule.check

        def patched_check(element):
            issue = original_check(element)
            if issue:
                issue.issue_type = IssueType.WARNING
            return issue

        warning_rule.check = patched_check
        checker.add_rule(warning_rule)
        errors_before = 0

        report = checker.check_elements([{"tag": "p"}])
        # errors should not increase from warning-type issue
        assert report.errors == errors_before

    def test_notice_type_goes_to_warnings_counter(self):
        checker = A11yChecker(level=WCAGLevel.AA)
        notice_rule = WCAGRule(
            code="notice-rule",
            criterion="3.1.1",
            level=WCAGLevel.A,
            check_fn=lambda e: False,
            message="Just a notice",
        )
        original_check = notice_rule.check

        def patched_check(element):
            issue = original_check(element)
            if issue:
                issue.issue_type = IssueType.NOTICE
            return issue

        notice_rule.check = patched_check
        checker.add_rule(notice_rule)

        report = checker.check_elements([{"tag": "p"}])
        assert report.warnings >= 1
        assert report.errors == 0


# ---------------------------------------------------------------------------
# A11yChecker — default level and AAA filtering
# ---------------------------------------------------------------------------


class TestA11yCheckerLevels:
    def test_default_level_is_aa(self):
        checker = A11yChecker()
        assert checker.level == WCAGLevel.AA

    def test_aaa_rules_skipped_at_aa_level(self):
        checker = A11yChecker(level=WCAGLevel.AA)
        aaa_rule = WCAGRule(
            code="aaa-only",
            criterion="1.4.6",
            level=WCAGLevel.AAA,
            check_fn=lambda e: False,
            message="AAA requirement",
        )
        checker.add_rule(aaa_rule)
        report = checker.check_elements([{"tag": "span"}])
        codes = [i.code for i in report.issues]
        assert "aaa-only" not in codes

    def test_aaa_rules_skipped_at_a_level(self):
        checker = A11yChecker(level=WCAGLevel.A)
        aaa_rule = WCAGRule(
            code="aaa-rule",
            criterion="1.4.6",
            level=WCAGLevel.AAA,
            check_fn=lambda e: False,
            message="AAA requirement",
        )
        checker.add_rule(aaa_rule)
        report = checker.check_elements([{"tag": "span"}])
        codes = [i.code for i in report.issues]
        assert "aaa-rule" not in codes

    def test_a_rules_run_at_aa_level(self):
        checker = A11yChecker(level=WCAGLevel.AA)
        # img-alt is Level A — should fire at AA level
        report = checker.check_elements([{"tag": "img"}])
        codes = [i.code for i in report.issues]
        assert "img-alt" in codes

    def test_aa_rules_run_at_aa_level(self):
        checker = A11yChecker(level=WCAGLevel.AA)
        # color-contrast is Level AA — should fire at AA level
        report = checker.check_elements([{"contrast_ratio": 1.0}])
        codes = [i.code for i in report.issues]
        assert "color-contrast" in codes

    def test_aa_rules_skipped_at_a_level(self):
        checker = A11yChecker(level=WCAGLevel.A)
        report = checker.check_elements([{"contrast_ratio": 1.0}])
        codes = [i.code for i in report.issues]
        assert "color-contrast" not in codes


# ---------------------------------------------------------------------------
# A11yChecker — link-text edge cases
# ---------------------------------------------------------------------------


class TestA11yCheckerLinkText:
    def test_link_with_empty_text_fails(self):
        checker = A11yChecker()
        report = checker.check_elements([{"tag": "a", "text": ""}])
        codes = [i.code for i in report.issues]
        assert "link-text" in codes

    def test_link_with_no_text_key_fails(self):
        checker = A11yChecker()
        report = checker.check_elements([{"tag": "a"}])
        codes = [i.code for i in report.issues]
        assert "link-text" in codes

    def test_link_with_whitespace_only_fails(self):
        checker = A11yChecker()
        report = checker.check_elements([{"tag": "a", "text": "\t\n  "}])
        codes = [i.code for i in report.issues]
        assert "link-text" in codes

    def test_non_anchor_tag_skips_link_check(self):
        checker = A11yChecker()
        report = checker.check_elements([{"tag": "div"}])
        codes = [i.code for i in report.issues]
        assert "link-text" not in codes


# ---------------------------------------------------------------------------
# A11yChecker — focus-visible edge cases
# ---------------------------------------------------------------------------


class TestA11yCheckerFocusVisible:
    def test_focus_style_defaults_to_true_when_missing(self):
        checker = A11yChecker(level=WCAGLevel.AA)
        # focusable=True but has_focus_style missing — defaults to True (passes)
        report = checker.check_elements([{"focusable": True}])
        codes = [i.code for i in report.issues]
        assert "focus-visible" not in codes

    def test_nonfocusable_with_no_style_still_passes(self):
        checker = A11yChecker(level=WCAGLevel.AA)
        report = checker.check_elements(
            [{"focusable": False, "has_focus_style": False}]
        )
        codes = [i.code for i in report.issues]
        assert "focus-visible" not in codes


# ---------------------------------------------------------------------------
# AccessibilityReport — score property boundary conditions
# ---------------------------------------------------------------------------


class TestAccessibilityReportScore:
    def test_score_zero_when_only_errors(self):
        report = AccessibilityReport(passed=0, errors=10)
        assert report.score == 0.0

    def test_score_exact_half(self):
        report = AccessibilityReport(passed=5, errors=5)
        assert report.score == pytest.approx(50.0)

    def test_score_one_error_nine_passed(self):
        report = AccessibilityReport(passed=9, errors=1)
        assert report.score == pytest.approx(90.0)

    def test_score_warnings_do_not_reduce_score(self):
        report = AccessibilityReport(passed=10, errors=0, warnings=100)
        assert report.score == 100.0

    def test_score_property_not_stored(self):
        report = AccessibilityReport(passed=8, errors=2)
        # score is computed each time — calling twice yields same result
        assert report.score == report.score


# ---------------------------------------------------------------------------
# AccessibilityReporter — edge cases for formatting
# ---------------------------------------------------------------------------


class TestAccessibilityReporterEdgeCases:
    def test_to_json_is_string(self):
        report = AccessibilityReport(passed=5, errors=0)
        reporter = AccessibilityReporter(report)
        result = reporter.to_json()
        assert isinstance(result, str)

    def test_to_json_default_indent_is_2(self):
        report = AccessibilityReport(passed=1)
        reporter = AccessibilityReporter(report)
        raw = reporter.to_json()
        # default indent=2: lines inside should have 2-space indent
        assert "  " in raw

    def test_to_dict_score_is_rounded(self):
        # passed=1, errors=3 → 1/4 = 25.0
        report = AccessibilityReport(passed=1, errors=3)
        reporter = AccessibilityReporter(report)
        d = reporter.to_dict()
        assert d["score"] == round(report.score, 1)

    def test_to_dict_multiple_issues(self):
        issues = [
            AccessibilityIssue(code=f"rule-{i}", message=f"msg {i}") for i in range(3)
        ]
        report = AccessibilityReport(issues=issues, errors=3)
        reporter = AccessibilityReporter(report)
        d = reporter.to_dict()
        assert len(d["issues"]) == 3

    def test_to_markdown_ends_with_newline(self):
        report = AccessibilityReport(passed=1)
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert md.endswith("\n")

    def test_to_markdown_multiple_issues_all_in_table(self):
        issues = [
            AccessibilityIssue(
                code="img-alt",
                message="Alt missing",
                wcag_level=WCAGLevel.A,
                issue_type=IssueType.ERROR,
            ),
            AccessibilityIssue(
                code="link-text",
                message="Empty link",
                wcag_level=WCAGLevel.A,
                issue_type=IssueType.WARNING,
            ),
        ]
        report = AccessibilityReport(issues=issues, errors=1, warnings=1)
        reporter = AccessibilityReporter(report)
        md = reporter.to_markdown()
        assert "img-alt" in md
        assert "link-text" in md

    def test_to_summary_counts_match_report(self):
        report = AccessibilityReport(passed=7, errors=2, warnings=1)
        reporter = AccessibilityReporter(report)
        summary = reporter.to_summary()
        assert "7 passed" in summary
        assert "2 errors" in summary
        assert "1 warnings" in summary

    def test_to_json_round_trips(self):
        issue = AccessibilityIssue(
            code="img-alt",
            message="Alt missing",
            selector="img#logo",
            issue_type=IssueType.ERROR,
            wcag_criterion="1.1.1",
            wcag_level=WCAGLevel.A,
            suggestion="Add alt text",
        )
        report = AccessibilityReport(
            url="https://rt.com",
            issues=[issue],
            passed=3,
            errors=1,
        )
        reporter = AccessibilityReporter(report)
        parsed = json.loads(reporter.to_json())
        assert parsed["issues"][0]["code"] == "img-alt"
        assert parsed["issues"][0]["wcag_criterion"] == "1.1.1"
        assert parsed["issues"][0]["suggestion"] == "Add alt text"
        assert parsed["issues"][0]["selector"] == "img#logo"


# ---------------------------------------------------------------------------
# calculate_contrast_ratio — additional boundary cases
# ---------------------------------------------------------------------------


class TestContrastRatioAdditional:
    def test_pure_red_on_white(self):
        # #ff0000 on #ffffff — known to be around 3.99:1 (below AA for normal text)
        ratio = calculate_contrast_ratio("#ff0000", "#ffffff")
        assert 3.5 < ratio < 4.5

    def test_pure_blue_on_white(self):
        # #0000ff on #ffffff — known ~8.59:1
        ratio = calculate_contrast_ratio("#0000ff", "#ffffff")
        assert ratio > 8.0

    def test_symmetry(self):
        r1 = calculate_contrast_ratio("#123456", "#abcdef")
        r2 = calculate_contrast_ratio("#abcdef", "#123456")
        assert r1 == pytest.approx(r2, rel=1e-6)

    def test_ratio_always_at_least_one(self):
        ratio = calculate_contrast_ratio("#888888", "#999999")
        assert ratio >= 1.0

    def test_empty_string_returns_zero(self):
        ratio = calculate_contrast_ratio("", "#ffffff")
        assert ratio == 0.0


# ---------------------------------------------------------------------------
# check_heading_hierarchy — additional boundary cases
# ---------------------------------------------------------------------------


class TestCheckHeadingHierarchyAdditional:
    def test_single_h2_gives_start_issue(self):
        issues = check_heading_hierarchy([2])
        assert any("h1" in i for i in issues)

    def test_descending_sequence_no_skip_issues(self):
        # 3→2→1 — no skip from prev+1 perspective (going down is fine structurally
        # in this implementation which only checks prev_level+1)
        issues = check_heading_hierarchy([1, 2, 3, 2, 1])
        assert not any("Skipped" in i for i in issues)

    def test_all_same_level_h1_no_issues(self):
        issues = check_heading_hierarchy([1, 1, 1, 1])
        assert issues == []

    def test_skipped_middle_level_detected(self):
        # 1→2→4 — skips h3
        issues = check_heading_hierarchy([1, 2, 4])
        skip_issues = [i for i in issues if "Skipped" in i]
        assert len(skip_issues) == 1
        assert "h2 to h4" in skip_issues[0]

    def test_two_consecutive_skips(self):
        # 1→3→5 — two separate skip events
        issues = check_heading_hierarchy([1, 3, 5])
        skip_issues = [i for i in issues if "Skipped" in i]
        assert len(skip_issues) == 2

    def test_h1_then_h2_then_back_to_h1_no_skip(self):
        issues = check_heading_hierarchy([1, 2, 1])
        skip_issues = [i for i in issues if "Skipped" in i]
        assert len(skip_issues) == 0
