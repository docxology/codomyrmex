"""Validation summary with severity grouping, formatting, and aggregation.

Provides:
- ValidationSummary: aggregate reports over multiple validation issues
- Severity breakdown, field grouping, top-N worst fields
- Text/dict/markdown output formats
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .contextual import ValidationIssue


class ValidationSummary:
    """Summarizes multiple validation issues with severity analysis and formatting.

    Example::

        issues = [
            ValidationIssue("name", "required", severity="error"),
            ValidationIssue("age", "out of range", severity="warning"),
        ]
        summary = ValidationSummary(issues)
        print(summary.markdown())
    """

    def __init__(self, issues: list[ValidationIssue] | None = None) -> None:
        """Initialize this instance."""
        self.issues: list[ValidationIssue] = issues or []

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a single issue."""
        self.issues.append(issue)

    def add_issues(self, issues: list[ValidationIssue]) -> None:
        """Add multiple issues."""
        self.issues.extend(issues)

    @property
    def is_valid(self) -> bool:
        """True if no error-severity issues."""
        return not any(issue.severity == "error" for issue in self.issues)

    @property
    def total(self) -> int:
        """total ."""
        return len(self.issues)

    @property
    def error_count(self) -> int:
        """error Count ."""
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        """warning Count ."""
        return sum(1 for i in self.issues if i.severity == "warning")

    @property
    def info_count(self) -> int:
        """info Count ."""
        return sum(1 for i in self.issues if i.severity == "info")

    def by_severity(self) -> dict[str, list[ValidationIssue]]:
        """Group issues by severity level."""
        grouped: dict[str, list[ValidationIssue]] = defaultdict(list)
        for issue in self.issues:
            grouped[issue.severity].append(issue)
        return dict(grouped)

    def by_field(self) -> dict[str, list[ValidationIssue]]:
        """Group issues by field name."""
        grouped: dict[str, list[ValidationIssue]] = defaultdict(list)
        for issue in self.issues:
            grouped[issue.field].append(issue)
        return dict(grouped)

    def worst_fields(self, n: int = 5) -> list[tuple[str, int]]:
        """Return top-N fields with the most error-severity issues.

        Returns:
            List of (field_name, error_count) sorted descending.
        """
        field_counts: dict[str, int] = defaultdict(int)
        for issue in self.issues:
            if issue.severity == "error":
                field_counts[issue.field] += 1
        return sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:n]

    def filter(self, severity: str | None = None, field: str | None = None) -> list[ValidationIssue]:
        """Filter issues by severity and/or field."""
        result = self.issues
        if severity:
            result = [i for i in result if i.severity == severity]
        if field:
            result = [i for i in result if i.field == field]
        return result

    def to_dict(self) -> dict[str, Any]:
        """Convert summary to a dictionary."""
        return {
            "is_valid": self.is_valid,
            "total": self.total,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "issues": [
                {"field": i.field, "message": i.message, "severity": i.severity, "code": i.code}
                for i in self.issues
            ],
        }

    def text(self) -> str:
        """Format as plain text report."""
        if not self.issues:
            return "✅ Validation passed — no issues found."
        lines = [f"Validation: {'FAILED' if not self.is_valid else 'PASSED (with warnings)'}"]
        lines.append(f"  Errors: {self.error_count}  Warnings: {self.warning_count}  Info: {self.info_count}")
        for issue in self.issues:
            lines.append(f"  [{issue.severity.upper()}] {issue.field}: {issue.message}")
        return "\n".join(lines)

    def markdown(self) -> str:
        """Format as markdown report."""
        if not self.issues:
            return "✅ **Validation passed** — no issues found.\n"
        status = "❌ **FAILED**" if not self.is_valid else "⚠️ **PASSED** (with warnings)"
        lines = [f"## Validation: {status}", ""]
        lines.append("| Severity | Count |")
        lines.append("|----------|------:|")
        for sev in ("error", "warning", "info"):
            count = sum(1 for i in self.issues if i.severity == sev)
            if count:
                lines.append(f"| {sev} | {count} |")
        lines.append("")
        lines.append("| Field | Severity | Message |")
        lines.append("|-------|----------|---------|")
        for issue in self.issues:
            lines.append(f"| `{issue.field}` | {issue.severity} | {issue.message} |")
        return "\n".join(lines)

    @classmethod
    def merge(cls, *summaries: ValidationSummary) -> ValidationSummary:
        """Merge multiple summaries into one."""
        combined: list[ValidationIssue] = []
        for s in summaries:
            combined.extend(s.issues)
        return cls(combined)
