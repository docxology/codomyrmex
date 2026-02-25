"""Accessibility report formatters."""

import json
from typing import Any

from .models import AccessibilityReport


class AccessibilityReporter:
    """Format accessibility reports for output."""

    def __init__(self, report: AccessibilityReport):
        """Execute   Init   operations natively."""
        self.report = report

    def to_summary(self) -> str:
        """One-line summary: 'Score: 85.0% | 17 passed, 2 errors, 1 warning'"""
        return (
            f"Score: {self.report.score:.1f}% | "
            f"{self.report.passed} passed, "
            f"{self.report.errors} errors, "
            f"{self.report.warnings} warnings"
        )

    def to_dict(self) -> dict[str, Any]:
        """Full report as serializable dict with score, issues list, counts."""
        return {
            "url": self.report.url,
            "score": round(self.report.score, 1),
            "passed": self.report.passed,
            "errors": self.report.errors,
            "warnings": self.report.warnings,
            "issues": [
                {
                    "code": issue.code,
                    "message": issue.message,
                    "selector": issue.selector,
                    "issue_type": issue.issue_type.value,
                    "wcag_criterion": issue.wcag_criterion,
                    "wcag_level": issue.wcag_level.value,
                    "suggestion": issue.suggestion,
                }
                for issue in self.report.issues
            ],
        }

    def to_json(self, indent: int = 2) -> str:
        """JSON string of the report."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        """Markdown formatted report with table of issues."""
        lines = [
            "# Accessibility Report",
            "",
            f"**Score**: {self.report.score:.1f}%",
            f"**Passed**: {self.report.passed} | "
            f"**Errors**: {self.report.errors} | "
            f"**Warnings**: {self.report.warnings}",
        ]

        if self.report.url:
            lines.insert(2, f"**URL**: {self.report.url}")
            lines.insert(3, "")

        if self.report.issues:
            lines.append("")
            lines.append("## Issues")
            lines.append("")
            lines.append("| Code | Level | Type | Message | Suggestion |")
            lines.append("|------|-------|------|---------|------------|")
            for issue in self.report.issues:
                lines.append(
                    f"| {issue.code} "
                    f"| {issue.wcag_level.value} "
                    f"| {issue.issue_type.value} "
                    f"| {issue.message} "
                    f"| {issue.suggestion} |"
                )

        lines.append("")
        return "\n".join(lines)
