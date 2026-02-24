"""Release validation and certification.

Validates release readiness: test pass rate, coverage,
type checking, security scans, and documentation status.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CertificationStatus(Enum):
    """Release certification status."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    WARN = "warn"


@dataclass
class CertificationCheck:
    """A single certification check.

    Attributes:
        name: Check name.
        category: Check category.
        status: Pass/fail result.
        value: Measured value.
        threshold: Required threshold.
        message: Result message.
    """

    name: str
    category: str = ""
    status: CertificationStatus = CertificationStatus.SKIP
    value: str = ""
    threshold: str = ""
    message: str = ""


@dataclass
class ReleaseCertification:
    """Complete release certification report.

    Attributes:
        version: Release version.
        checks: All certification checks.
        certified: Whether release is certified.
        certified_at: Certification timestamp.
        blockers: List of blocking issues.
    """

    version: str
    checks: list[CertificationCheck] = field(default_factory=list)
    certified: bool = False
    certified_at: float = 0.0
    blockers: list[str] = field(default_factory=list)

    @property
    def total_checks(self) -> int:
        """Execute Total Checks operations natively."""
        return len(self.checks)

    @property
    def passed_checks(self) -> int:
        """Execute Passed Checks operations natively."""
        return sum(1 for c in self.checks if c.status == CertificationStatus.PASS)

    @property
    def pass_rate(self) -> float:
        """Execute Pass Rate operations natively."""
        return self.passed_checks / self.total_checks if self.checks else 0.0


class ReleaseValidator:
    """Validate release readiness.

    Example::

        validator = ReleaseValidator(version="1.0.0")
        validator.check_tests(failures=0, total=9000)
        validator.check_coverage(overall=67, tier1=82)
        cert = validator.certify()
        assert cert.certified
    """

    def __init__(self, version: str = "1.0.0") -> None:
        """Execute   Init   operations natively."""
        self._version = version
        self._checks: list[CertificationCheck] = []

    @property
    def check_count(self) -> int:
        """Execute Check Count operations natively."""
        return len(self._checks)

    def check_tests(self, failures: int, total: int, max_skips: int = 50) -> CertificationCheck:
        """Validate test results."""
        status = CertificationStatus.PASS if failures == 0 else CertificationStatus.FAIL
        check = CertificationCheck(
            name="Test Suite",
            category="testing",
            status=status,
            value=f"{failures} failures / {total} tests",
            threshold="0 failures",
            message="PASS" if failures == 0 else f"{failures} test(s) failed",
        )
        self._checks.append(check)
        return check

    def check_coverage(self, overall: float, tier1: float = 0) -> CertificationCheck:
        """Validate code coverage."""
        passed = overall >= 65
        if tier1 > 0:
            passed = passed and tier1 >= 80
        status = CertificationStatus.PASS if passed else CertificationStatus.FAIL
        check = CertificationCheck(
            name="Code Coverage",
            category="quality",
            status=status,
            value=f"overall={overall}%, tier1={tier1}%",
            threshold="overall≥65%, tier1≥80%",
        )
        self._checks.append(check)
        return check

    def check_type_safety(self, errors: int) -> CertificationCheck:
        """Validate type checking results."""
        status = CertificationStatus.PASS if errors == 0 else CertificationStatus.WARN
        check = CertificationCheck(
            name="Type Safety",
            category="quality",
            status=status,
            value=f"{errors} type errors",
            threshold="0 errors (strict)",
        )
        self._checks.append(check)
        return check

    def check_security(self, cve_count: int, secrets_found: int) -> CertificationCheck:
        """Validate security posture."""
        passed = cve_count == 0 and secrets_found == 0
        status = CertificationStatus.PASS if passed else CertificationStatus.FAIL
        check = CertificationCheck(
            name="Security",
            category="security",
            status=status,
            value=f"{cve_count} CVEs, {secrets_found} secrets",
            threshold="0 CVEs, 0 secrets",
        )
        self._checks.append(check)
        return check

    def check_documentation(self, complete: bool) -> CertificationCheck:
        """Validate documentation status."""
        status = CertificationStatus.PASS if complete else CertificationStatus.WARN
        check = CertificationCheck(
            name="Documentation",
            category="docs",
            status=status,
            value="complete" if complete else "incomplete",
            threshold="all docs current",
        )
        self._checks.append(check)
        return check

    def add_custom_check(self, check: CertificationCheck) -> None:
        """Add a custom certification check."""
        self._checks.append(check)

    def certify(self) -> ReleaseCertification:
        """Run certification and produce report."""
        blockers = [
            c.name for c in self._checks
            if c.status == CertificationStatus.FAIL
        ]
        certified = len(blockers) == 0

        return ReleaseCertification(
            version=self._version,
            checks=list(self._checks),
            certified=certified,
            certified_at=time.time() if certified else 0.0,
            blockers=blockers,
        )

    def to_markdown(self, cert: ReleaseCertification) -> str:
        """Render certification as markdown."""
        icon = "✅" if cert.certified else "❌"
        lines = [
            f"# Release Certification — v{cert.version} {icon}",
            "",
            f"**Status**: {'CERTIFIED' if cert.certified else 'NOT CERTIFIED'} | "
            f"**Checks**: {cert.passed_checks}/{cert.total_checks}",
            "",
            "| Check | Category | Status | Value | Threshold |",
            "|-------|----------|--------|-------|-----------|",
        ]
        for c in cert.checks:
            status_icon = {"pass": "✅", "fail": "❌", "warn": "⚠️", "skip": "⏭️"}.get(c.status.value, "")
            lines.append(
                f"| {c.name} | {c.category} | {status_icon} | {c.value} | {c.threshold} |"
            )

        if cert.blockers:
            lines.extend(["", "## Blockers", ""])
            for b in cert.blockers:
                lines.append(f"- ❌ {b}")

        return "\n".join(lines)


__all__ = [
    "CertificationCheck",
    "CertificationStatus",
    "ReleaseCertification",
    "ReleaseValidator",
]
