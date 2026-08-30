<!-- readme: generated -->

# release

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/release/`

## Overview

Release management module for Codomyrmex.

Provides tools for validating release readiness, building distribution
packages, and managing publication to distribution targets.

Components:
    - ReleaseValidator: Validate release readiness (tests, coverage, security, docs)
    - PackageBuilder: Build sdist and wheel distribution artifacts
    - DistributionManager: Verified local copies and remote dry-run plans
    - PublicationBundle: Portable technical-report release artifacts

## Public Exports

`release` exports 22 public symbols via `__all__`:

`BuildArtifact`, `BuildReport`, `CertificationCheck`, `CertificationStatus`, `DistributionManager`, `DistributionTarget`, `PackageBuilder`, `PackageMetadata`, `PreflightResult`, `PublicationArtifact`, `PublicationBundle`, `PublicationManifest`, `PublicationMetadata`, `PublicationPlan`, `PublicationVerification`, `PublishResult`, `ReleaseCertification`, `ReleasePolicy`, `ReleaseValidator`, `plan_publication`, `prepare_publication_bundle`, `verify_publication_bundle`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../release/](../../../../release/)
