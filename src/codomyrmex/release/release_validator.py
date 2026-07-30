"""Fail-closed release evidence validation and certification."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

PROJECT_COVERAGE_FLOOR = 60.0
TIER1_COVERAGE_FLOOR = 80.0


class CertificationStatus(Enum):
    """Release certification status."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    WARN = "warn"


@dataclass(frozen=True)
class ReleasePolicy:
    """Policy describing evidence required for release certification."""

    strict: bool = True
    required_categories: tuple[str, ...] = (
        "testing",
        "coverage",
        "typing",
        "security",
        "documentation",
        "artifacts",
    )
    coverage_floor: float = PROJECT_COVERAGE_FLOOR
    tier1_coverage_floor: float = TIER1_COVERAGE_FLOOR


@dataclass(frozen=True)
class CertificationCheck:
    """One supplied release-evidence check."""

    name: str
    category: str = ""
    status: CertificationStatus = CertificationStatus.SKIP
    value: str = ""
    threshold: str = ""
    message: str = ""


@dataclass(frozen=True)
class ReleaseCertification:
    """Complete release certification receipt."""

    version: str
    checks: tuple[CertificationCheck, ...] = ()
    certified: bool = False
    certified_at: float = 0.0
    blockers: tuple[str, ...] = ()
    policy: ReleasePolicy = field(default_factory=ReleasePolicy)

    @property
    def total_checks(self) -> int:
        return len(self.checks)

    @property
    def passed_checks(self) -> int:
        return sum(
            1 for check in self.checks if check.status is CertificationStatus.PASS
        )

    @property
    def pass_rate(self) -> float:
        return self.passed_checks / self.total_checks if self.checks else 0.0


class ReleaseValidator:
    """Collect release evidence and certify only when policy is satisfied."""

    def __init__(
        self,
        version: str = "1.3.0",
        *,
        policy: ReleasePolicy | None = None,
    ) -> None:
        self._version = version
        self._policy = policy or ReleasePolicy()
        self._checks: list[CertificationCheck] = []

    @property
    def check_count(self) -> int:
        return len(self._checks)

    @property
    def policy(self) -> ReleasePolicy:
        return self._policy

    def check_tests(
        self,
        failures: int,
        total: int,
        max_skips: int = 50,
    ) -> CertificationCheck:
        """Record executed test evidence."""
        del max_skips
        passed = total > 0 and failures == 0
        check = CertificationCheck(
            name="Test Suite",
            category="testing",
            status=CertificationStatus.PASS if passed else CertificationStatus.FAIL,
            value=f"{failures} failures / {total} tests",
            threshold="at least 1 test and 0 failures",
            message=(
                "PASS"
                if passed
                else "Test evidence is absent or includes one or more failures"
            ),
        )
        self._checks.append(check)
        return check

    def check_coverage(self, overall: float, tier1: float = 0) -> CertificationCheck:
        """Record repository coverage evidence."""
        passed = overall >= self._policy.coverage_floor
        if tier1 > 0:
            passed = passed and tier1 >= self._policy.tier1_coverage_floor
        check = CertificationCheck(
            name="Code Coverage",
            category="coverage",
            status=CertificationStatus.PASS if passed else CertificationStatus.FAIL,
            value=f"overall={overall}%, tier1={tier1}%",
            threshold=(
                f"overall≥{self._policy.coverage_floor:.0f}%, "
                f"tier1≥{self._policy.tier1_coverage_floor:.0f}% when supplied"
            ),
        )
        self._checks.append(check)
        return check

    def check_type_safety(self, errors: int) -> CertificationCheck:
        """Record type-check evidence."""
        if errors == 0:
            status = CertificationStatus.PASS
        else:
            status = (
                CertificationStatus.FAIL
                if self._policy.strict
                else CertificationStatus.WARN
            )
        check = CertificationCheck(
            name="Type Safety",
            category="typing",
            status=status,
            value=f"{errors} type errors",
            threshold="0 errors",
        )
        self._checks.append(check)
        return check

    def check_security(self, cve_count: int, secrets_found: int) -> CertificationCheck:
        """Record dependency and secret-scan evidence."""
        passed = cve_count == 0 and secrets_found == 0
        check = CertificationCheck(
            name="Security",
            category="security",
            status=CertificationStatus.PASS if passed else CertificationStatus.FAIL,
            value=f"{cve_count} CVEs, {secrets_found} secrets",
            threshold="0 CVEs, 0 secrets",
        )
        self._checks.append(check)
        return check

    def check_documentation(self, complete: bool) -> CertificationCheck:
        """Record strict documentation-build evidence."""
        if complete:
            status = CertificationStatus.PASS
        else:
            status = (
                CertificationStatus.FAIL
                if self._policy.strict
                else CertificationStatus.WARN
            )
        check = CertificationCheck(
            name="Documentation",
            category="documentation",
            status=status,
            value="complete" if complete else "incomplete",
            threshold="strict documentation build passes",
        )
        self._checks.append(check)
        return check

    def check_artifacts(
        self,
        *,
        verified: bool,
        artifact_count: int,
    ) -> CertificationCheck:
        """Record wheel, sdist, and publication artifact verification."""
        passed = verified and artifact_count > 0
        check = CertificationCheck(
            name="Artifact Verification",
            category="artifacts",
            status=CertificationStatus.PASS if passed else CertificationStatus.FAIL,
            value=f"{artifact_count} artifacts; verified={verified}",
            threshold="at least 1 artifact with matching size and hashes",
        )
        self._checks.append(check)
        return check

    def add_custom_check(self, check: CertificationCheck) -> None:
        """Add caller-supplied evidence without weakening policy."""
        self._checks.append(check)

    def certify(self) -> ReleaseCertification:
        """Produce a fail-closed certification receipt."""
        supplied = {check.category for check in self._checks}
        missing = [
            category
            for category in self._policy.required_categories
            if category not in supplied
        ]
        blockers = [
            check.name
            for check in self._checks
            if check.status is CertificationStatus.FAIL
            or (
                self._policy.strict
                and check.category in self._policy.required_categories
                and check.status is not CertificationStatus.PASS
            )
        ]
        blockers.extend(
            f"Missing required evidence: {category}" for category in missing
        )
        blockers = list(dict.fromkeys(blockers))
        certified = not blockers

        return ReleaseCertification(
            version=self._version,
            checks=tuple(self._checks),
            certified=certified,
            certified_at=time.time() if certified else 0.0,
            blockers=tuple(blockers),
            policy=self._policy,
        )

    def to_markdown(self, cert: ReleaseCertification) -> str:
        """Render a human-readable certification receipt."""
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
        icons = {"pass": "✅", "fail": "❌", "warn": "⚠️", "skip": "⏭️"}
        for check in cert.checks:
            lines.append(
                f"| {check.name} | {check.category} | "
                f"{icons.get(check.status.value, '')} | {check.value} | "
                f"{check.threshold} |"
            )

        if cert.blockers:
            lines.extend(["", "## Blockers", ""])
            lines.extend(f"- ❌ {blocker}" for blocker in cert.blockers)

        return "\n".join(lines)


__all__ = [
    "CertificationCheck",
    "CertificationStatus",
    "ReleaseCertification",
    "ReleasePolicy",
    "ReleaseValidator",
]
