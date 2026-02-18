"""Accessibility checker implementation."""

from typing import Any

from .models import (
    AccessibilityReport,
    IssueType,
    WCAGLevel,
    WCAGRule,
)


class A11yChecker:
    """Accessibility checker."""

    def __init__(self, level: WCAGLevel = WCAGLevel.AA):
        self.level = level
        self._rules: list[WCAGRule] = []
        self._setup_default_rules()

    def _setup_default_rules(self):
        # Image alt text
        self._rules.append(
            WCAGRule(
                code="img-alt",
                criterion="1.1.1",
                level=WCAGLevel.A,
                check_fn=lambda e: e.get("tag") != "img" or bool(e.get("alt")),
                message="Images must have alt text",
                suggestion="Add alt attribute to img element",
            )
        )

        # Form labels
        self._rules.append(
            WCAGRule(
                code="form-label",
                criterion="1.3.1",
                level=WCAGLevel.A,
                check_fn=lambda e: e.get("tag") not in ["input", "select", "textarea"]
                or bool(e.get("label")),
                message="Form elements must have labels",
                suggestion="Add a label element or aria-label attribute",
            )
        )

        # Link text
        self._rules.append(
            WCAGRule(
                code="link-text",
                criterion="2.4.4",
                level=WCAGLevel.A,
                check_fn=lambda e: e.get("tag") != "a"
                or bool(e.get("text", "").strip()),
                message="Links must have descriptive text",
                suggestion="Add meaningful link text or aria-label",
            )
        )

        # Color contrast (simplified)
        self._rules.append(
            WCAGRule(
                code="color-contrast",
                criterion="1.4.3",
                level=WCAGLevel.AA,
                check_fn=lambda e: e.get("contrast_ratio", 4.5) >= 4.5,
                message="Text must have sufficient color contrast",
                suggestion="Increase color contrast ratio to at least 4.5:1",
            )
        )

        # Focus indicator
        self._rules.append(
            WCAGRule(
                code="focus-visible",
                criterion="2.4.7",
                level=WCAGLevel.AA,
                check_fn=lambda e: not e.get("focusable")
                or e.get("has_focus_style", True),
                message="Interactive elements must have visible focus indicator",
                suggestion="Add :focus-visible styles",
            )
        )

    def add_rule(self, rule: WCAGRule) -> None:
        self._rules.append(rule)

    def check_elements(self, elements: list[dict[str, Any]]) -> AccessibilityReport:
        """Check a list of elements."""
        report = AccessibilityReport()

        for element in elements:
            for rule in self._rules:
                # Skip rules above target level
                if self.level == WCAGLevel.A and rule.level != WCAGLevel.A:
                    continue
                if self.level == WCAGLevel.AA and rule.level == WCAGLevel.AAA:
                    continue

                issue = rule.check(element)
                if issue:
                    report.issues.append(issue)
                    if issue.issue_type == IssueType.ERROR:
                        report.errors += 1
                    else:
                        report.warnings += 1
                else:
                    report.passed += 1

        return report
