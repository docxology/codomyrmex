"""Distribution management.

Manages package distribution targets, pre-flight checks,
and publish operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from codomyrmex.release.package_builder import BuildReport


class DistributionTarget(Enum):
    """Package distribution targets."""

    PYPI = "pypi"
    TEST_PYPI = "test_pypi"
    GITHUB = "github"
    LOCAL = "local"


@dataclass
class PreflightResult:
    """Pre-flight check result before publishing.

    Attributes:
        target: Distribution target.
        checks_passed: Number of checks passed.
        checks_total: Total number of checks.
        ready: Whether ready to publish.
        issues: List of issues found.
    """

    target: DistributionTarget
    checks_passed: int = 0
    checks_total: int = 0
    ready: bool = False
    issues: list[str] = field(default_factory=list)


@dataclass
class PublishResult:
    """Result of a publish operation.

    Attributes:
        target: Distribution target.
        artifacts_published: Number of artifacts published.
        url: Published package URL.
        success: Whether publish succeeded.
        error: Error message if failed.
    """

    target: DistributionTarget
    artifacts_published: int = 0
    url: str = ""
    success: bool = False
    error: str = ""


class DistributionManager:
    """Manage package distribution and publishing.

    Example::

        dm = DistributionManager(build_report)
        preflight = dm.preflight(DistributionTarget.PYPI)
        if preflight.ready:
            result = dm.publish(DistributionTarget.PYPI)
    """

    def __init__(self, build: BuildReport | None = None) -> None:
        """Initialize this instance."""
        self._build = build
        self._published: list[PublishResult] = []

    @property
    def has_build(self) -> bool:
        """has Build ."""
        return self._build is not None and self._build.success

    def preflight(self, target: DistributionTarget) -> PreflightResult:
        """Run pre-flight checks for a distribution target.

        Args:
            target: Target to check.

        Returns:
            PreflightResult with check status.
        """
        issues: list[str] = []
        checks_total = 3
        checks_passed = 0

        # Check 1: Build exists and succeeded
        if not self.has_build:
            issues.append("No successful build available")
        else:
            checks_passed += 1

        # Check 2: Artifacts present
        if self._build and self._build.artifacts:
            checks_passed += 1
        else:
            issues.append("No build artifacts found")

        # Check 3: Metadata valid
        if self._build and self._build.metadata.name:
            checks_passed += 1
        else:
            issues.append("Package metadata incomplete")

        return PreflightResult(
            target=target,
            checks_passed=checks_passed,
            checks_total=checks_total,
            ready=checks_passed == checks_total,
            issues=issues,
        )

    def publish(self, target: DistributionTarget) -> PublishResult:
        """Publish artifacts to a distribution target.

        Args:
            target: Where to publish.

        Returns:
            PublishResult with status.
        """
        preflight = self.preflight(target)
        if not preflight.ready:
            return PublishResult(
                target=target,
                success=False,
                error=f"Pre-flight failed: {'; '.join(preflight.issues)}",
            )

        # Simulate publish
        artifacts_count = len(self._build.artifacts) if self._build else 0
        name = self._build.metadata.name if self._build else ""
        version = self._build.metadata.version if self._build else ""

        url = ""
        if target == DistributionTarget.PYPI:
            url = f"https://pypi.org/project/{name}/{version}/"
        elif target == DistributionTarget.TEST_PYPI:
            url = f"https://test.pypi.org/project/{name}/{version}/"
        elif target == DistributionTarget.GITHUB:
            url = f"https://github.com/docxology/{name}/releases/tag/v{version}"

        result = PublishResult(
            target=target,
            artifacts_published=artifacts_count,
            url=url,
            success=True,
        )
        self._published.append(result)
        return result

    def publish_history(self) -> list[PublishResult]:
        """Get history of publish operations."""
        return list(self._published)


__all__ = [
    "DistributionManager",
    "DistributionTarget",
    "PreflightResult",
    "PublishResult",
]
