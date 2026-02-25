"""Compliance report generation.

Generates compliance reports covering OWASP checks,
dependency CVE status, and secret scan results.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ComplianceStatus(Enum):
    """Compliance check status."""

    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class ComplianceCheck:
    """A single compliance check result.

    Attributes:
        check_id: Check identifier.
        category: Check category (e.g. 'owasp', 'dependency').
        description: Check description.
        status: Pass/fail/warn.
        details: Additional details.
        severity: Impact severity.
    """

    check_id: str
    category: str
    description: str
    status: ComplianceStatus = ComplianceStatus.SKIP
    details: str = ""
    severity: str = "medium"


@dataclass
class ComplianceReport:
    """Full compliance report.

    Attributes:
        title: Report title.
        checks: Individual check results.
        generated_at: Report generation timestamp.
        summary: Summary statistics.
    """

    title: str = "Compliance Report"
    checks: list[ComplianceCheck] = field(default_factory=list)
    generated_at: float = field(default_factory=time.time)
    summary: dict[str, int] = field(default_factory=dict)

    @property
    def total_checks(self) -> int:
        """Execute Total Checks operations natively."""
        return len(self.checks)

    @property
    def pass_rate(self) -> float:
        """Execute Pass Rate operations natively."""
        if not self.checks:
            return 0.0
        passed = sum(1 for c in self.checks if c.status == ComplianceStatus.PASS)
        return passed / len(self.checks)

    def add_check(self, check: ComplianceCheck) -> None:
        """Add a compliance check result."""
        self.checks.append(check)

    def compute_summary(self) -> dict[str, int]:
        """Compute summary statistics."""
        summary: dict[str, int] = {}
        for status in ComplianceStatus:
            summary[status.value] = sum(
                1 for c in self.checks if c.status == status
            )
        self.summary = summary
        return summary

    def failed_checks(self) -> list[ComplianceCheck]:
        """Get all failed checks."""
        return [c for c in self.checks if c.status == ComplianceStatus.FAIL]

    def by_category(self, category: str) -> list[ComplianceCheck]:
        """Get checks by category."""
        return [c for c in self.checks if c.category == category]

    def to_markdown(self) -> str:
        """Render report as markdown."""
        self.compute_summary()
        lines = [
            f"# {self.title}",
            "",
            f"**Pass Rate**: {self.pass_rate:.0%} | "
            f"**Total**: {self.total_checks}",
            "",
            "| Check | Category | Status | Severity |",
            "|-------|----------|--------|----------|",
        ]
        for c in self.checks:
            icon = {"pass": "✅", "fail": "❌", "warn": "⚠️", "skip": "⏭️"}.get(c.status.value, "")
            lines.append(
                f"| {c.check_id} | {c.category} | {icon} {c.status.value} | {c.severity} |"
            )
        return "\n".join(lines)


class ComplianceGenerator:
    """Generate compliance reports with OWASP and custom checks.

    Example::

        gen = ComplianceGenerator()
        gen.add_owasp_checks()
        report = gen.generate()
    """

    _OWASP_CHECKS = [
        ("A01", "Broken Access Control", "Verify role-based access enforcement"),
        ("A02", "Cryptographic Failures", "Check encryption of sensitive data"),
        ("A03", "Injection", "Verify input validation and parameterized queries"),
        ("A04", "Insecure Design", "Review threat models and design patterns"),
        ("A05", "Security Misconfiguration", "Check default configs and hardening"),
        ("A06", "Vulnerable Components", "Scan dependencies for known CVEs"),
        ("A07", "Auth Failures", "Verify authentication mechanisms"),
        ("A08", "Data Integrity", "Check software and data integrity"),
        ("A09", "Logging Failures", "Verify security logging and monitoring"),
        ("A10", "SSRF", "Check server-side request validation"),
    ]

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._checks: list[ComplianceCheck] = []

    def add_owasp_checks(self, default_status: ComplianceStatus = ComplianceStatus.PASS) -> None:
        """Add OWASP Top 10 checks."""
        for check_id, name, desc in self._OWASP_CHECKS:
            self._checks.append(ComplianceCheck(
                check_id=check_id,
                category="owasp",
                description=f"{name}: {desc}",
                status=default_status,
                severity="high",
            ))

    def add_check(self, check: ComplianceCheck) -> None:
        """Add a custom check."""
        self._checks.append(check)

    def generate(self, title: str = "Compliance Report") -> ComplianceReport:
        """Generate the compliance report."""
        report = ComplianceReport(title=title, checks=list(self._checks))
        report.compute_summary()
        return report


__all__ = [
    "ComplianceCheck",
    "ComplianceGenerator",
    "ComplianceReport",
    "ComplianceStatus",
]
