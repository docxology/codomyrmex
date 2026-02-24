"""Release management module for Codomyrmex.

Provides tools for validating release readiness, building distribution
packages, and managing publication to distribution targets.

Components:
    - ReleaseValidator: Validate release readiness (tests, coverage, security, docs)
    - PackageBuilder: Build sdist and wheel distribution artifacts
    - DistributionManager: Manage publishing to PyPI, TestPyPI, GitHub, and local targets
"""

from codomyrmex.release.release_validator import (
    CertificationCheck,
    CertificationStatus,
    ReleaseCertification,
    ReleaseValidator,
)
from codomyrmex.release.package_builder import (
    BuildArtifact,
    BuildReport,
    PackageBuilder,
    PackageMetadata,
)
from codomyrmex.release.distribution import (
    DistributionManager,
    DistributionTarget,
    PreflightResult,
    PublishResult,
)

__all__ = [
    # Validation
    "CertificationCheck",
    "CertificationStatus",
    "ReleaseCertification",
    "ReleaseValidator",
    # Building
    "BuildArtifact",
    "BuildReport",
    "PackageBuilder",
    "PackageMetadata",
    # Distribution
    "DistributionManager",
    "DistributionTarget",
    "PreflightResult",
    "PublishResult",
]
