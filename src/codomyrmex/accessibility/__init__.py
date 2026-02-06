"""
Accessibility Module

WCAG compliance checking and accessibility utilities.
"""

__version__ = "0.1.0"

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class WCAGLevel(Enum):
    """WCAG conformance levels."""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class IssueType(Enum):
    """Types of accessibility issues."""
    ERROR = "error"
    WARNING = "warning"
    NOTICE = "notice"


@dataclass
class AccessibilityIssue:
    """An accessibility issue."""
    code: str
    message: str
    selector: str = ""
    issue_type: IssueType = IssueType.ERROR
    wcag_criterion: str = ""
    wcag_level: WCAGLevel = WCAGLevel.A
    suggestion: str = ""


@dataclass
class AccessibilityReport:
    """Accessibility audit report."""
    url: str = ""
    issues: list[AccessibilityIssue] = field(default_factory=list)
    passed: int = 0
    warnings: int = 0
    errors: int = 0

    @property
    def score(self) -> float:
        total = self.passed + self.errors
        if total == 0:
            return 100.0
        return (self.passed / total) * 100


class WCAGRule:
    """A WCAG accessibility rule."""

    def __init__(
        self,
        code: str,
        criterion: str,
        level: WCAGLevel,
        check_fn,
        message: str,
        suggestion: str = "",
    ):
        self.code = code
        self.criterion = criterion
        self.level = level
        self.check_fn = check_fn
        self.message = message
        self.suggestion = suggestion

    def check(self, element: dict[str, Any]) -> AccessibilityIssue | None:
        if not self.check_fn(element):
            return AccessibilityIssue(
                code=self.code,
                message=self.message,
                selector=element.get("selector", ""),
                wcag_criterion=self.criterion,
                wcag_level=self.level,
                suggestion=self.suggestion,
            )
        return None


class A11yChecker:
    """Accessibility checker."""

    def __init__(self, level: WCAGLevel = WCAGLevel.AA):
        self.level = level
        self._rules: list[WCAGRule] = []
        self._setup_default_rules()

    def _setup_default_rules(self):
        # Image alt text
        self._rules.append(WCAGRule(
            code="img-alt",
            criterion="1.1.1",
            level=WCAGLevel.A,
            check_fn=lambda e: e.get("tag") != "img" or bool(e.get("alt")),
            message="Images must have alt text",
            suggestion="Add alt attribute to img element",
        ))

        # Form labels
        self._rules.append(WCAGRule(
            code="form-label",
            criterion="1.3.1",
            level=WCAGLevel.A,
            check_fn=lambda e: e.get("tag") not in ["input", "select", "textarea"] or bool(e.get("label")),
            message="Form elements must have labels",
            suggestion="Add a label element or aria-label attribute",
        ))

        # Link text
        self._rules.append(WCAGRule(
            code="link-text",
            criterion="2.4.4",
            level=WCAGLevel.A,
            check_fn=lambda e: e.get("tag") != "a" or bool(e.get("text", "").strip()),
            message="Links must have descriptive text",
            suggestion="Add meaningful link text or aria-label",
        ))

        # Color contrast (simplified)
        self._rules.append(WCAGRule(
            code="color-contrast",
            criterion="1.4.3",
            level=WCAGLevel.AA,
            check_fn=lambda e: e.get("contrast_ratio", 4.5) >= 4.5,
            message="Text must have sufficient color contrast",
            suggestion="Increase color contrast ratio to at least 4.5:1",
        ))

        # Focus indicator
        self._rules.append(WCAGRule(
            code="focus-visible",
            criterion="2.4.7",
            level=WCAGLevel.AA,
            check_fn=lambda e: not e.get("focusable") or e.get("has_focus_style", True),
            message="Interactive elements must have visible focus indicator",
            suggestion="Add :focus-visible styles",
        ))

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


def calculate_contrast_ratio(fg: str, bg: str) -> float:
    """Calculate WCAG contrast ratio between two colors."""
    def hex_to_luminance(hex_color: str) -> float:
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]

        def adjust(c):
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

    try:
        l1 = hex_to_luminance(fg)
        l2 = hex_to_luminance(bg)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)
    except (ValueError, IndexError):
        return 0.0


def check_heading_hierarchy(headings: list[int]) -> list[str]:
    """Check heading level hierarchy."""
    issues = []
    prev_level = 0

    for level in headings:
        if level > prev_level + 1:
            issues.append(f"Skipped heading level: h{prev_level} to h{level}")
        prev_level = level

    if headings and headings[0] != 1:
        issues.append("Document should start with h1")

    return issues


__all__ = [
    "A11yChecker",
    "AccessibilityIssue",
    "AccessibilityReport",
    "WCAGLevel",
    "WCAGRule",
    "IssueType",
    "calculate_contrast_ratio",
    "check_heading_hierarchy",
]
