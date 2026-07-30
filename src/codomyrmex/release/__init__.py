"""Release management module for Codomyrmex.

Provides tools for validating release readiness, building distribution
packages, and managing publication to distribution targets.

Components:
    - ReleaseValidator: Validate release readiness (tests, coverage, security, docs)
    - PackageBuilder: Build sdist and wheel distribution artifacts
    - DistributionManager: Verified local copies and remote dry-run plans
    - PublicationBundle: Portable technical-report release artifacts
"""

from codomyrmex.release.distribution import (
    DistributionManager,
    DistributionTarget,
    PreflightResult,
    PublishResult,
)
from codomyrmex.release.package_builder import (
    BuildArtifact,
    BuildReport,
    PackageBuilder,
    PackageMetadata,
)
from codomyrmex.release.publication import (
    PublicationArtifact,
    PublicationBundle,
    PublicationManifest,
    PublicationMetadata,
    PublicationPlan,
    PublicationVerification,
    plan_publication,
    prepare_publication_bundle,
    verify_publication_bundle,
)
from codomyrmex.release.release_validator import (
    CertificationCheck,
    CertificationStatus,
    ReleaseCertification,
    ReleasePolicy,
    ReleaseValidator,
)

__all__ = [
    # Building
    "BuildArtifact",
    "BuildReport",
    # Validation
    "CertificationCheck",
    "CertificationStatus",
    # Distribution
    "DistributionManager",
    "DistributionTarget",
    "PackageBuilder",
    "PackageMetadata",
    "PreflightResult",
    "PublicationArtifact",
    "PublicationBundle",
    "PublicationManifest",
    "PublicationMetadata",
    "PublicationPlan",
    "PublicationVerification",
    "PublishResult",
    "ReleaseCertification",
    "ReleasePolicy",
    "ReleaseValidator",
    "plan_publication",
    "prepare_publication_bundle",
    "verify_publication_bundle",
]
