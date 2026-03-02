# Personal AI Infrastructure — Release Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Release module manages the full release lifecycle: validating that a version is
ready to ship, building distribution artifacts, and publishing to targets such as
PyPI, TestPyPI, GitHub Releases, and local directories.

Three components handle the pipeline end-to-end:

- **ReleaseValidator** — runs pre-release certification checks (test pass rate,
  coverage threshold, security scan, documentation completeness) and produces a
  `ReleaseCertification` with per-check status.
- **PackageBuilder** — invokes `build`/`hatch` to produce `sdist` and `wheel`
  artifacts, returning `BuildArtifact` records with checksums and paths.
- **DistributionManager** — handles publishing to `PyPI`, `TestPyPI`, `GitHub`, or
  `local` targets after running preflight validation.

## PAI Capabilities

### Python API (no MCP tools — use direct Python import)

Release does not expose MCP tools. Use it as a Python library within EXECUTE phase
scripts or CI/CD pipeline automation.

**Run pre-release certification:**

```python
from codomyrmex.release import ReleaseValidator, ReleaseCertification

validator = ReleaseValidator()
cert: ReleaseCertification = validator.certify(version="1.0.3")
# cert.status: CertificationStatus.PASS | FAIL | PARTIAL
# cert.checks: list[CertificationCheck] — per-check detail
for check in cert.checks:
    print(check.name, check.status, check.message)
```

**Build distribution artifacts:**

```python
from codomyrmex.release import PackageBuilder, BuildReport

builder = PackageBuilder()
report: BuildReport = builder.build(formats=["sdist", "wheel"])
# report.artifacts: list[BuildArtifact]
# report.artifacts[0].path: str — path to .whl or .tar.gz
# report.artifacts[0].checksum: str — SHA256 checksum
```

**Publish to a distribution target:**

```python
from codomyrmex.release import DistributionManager, DistributionTarget

manager = DistributionManager()
preflight: PreflightResult = manager.preflight(target=DistributionTarget.PYPI)
if preflight.ready:
    result = manager.publish(target=DistributionTarget.PYPI, artifacts=report.artifacts)
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `ReleaseValidator` | Class | Run pre-release certification checks |
| `ReleaseCertification` | Dataclass | Certification outcome with per-check detail |
| `CertificationCheck` | Dataclass | Individual check result (name, status, message) |
| `CertificationStatus` | Enum | `PASS`, `FAIL`, `PARTIAL` |
| `PackageBuilder` | Class | Build sdist and wheel distribution artifacts |
| `BuildReport` | Dataclass | Build outcome with artifact list and metadata |
| `BuildArtifact` | Dataclass | Single artifact: path, format, size, checksum |
| `PackageMetadata` | Dataclass | Package name, version, description, classifiers |
| `DistributionManager` | Class | Publish artifacts to PyPI, TestPyPI, GitHub, or local |
| `DistributionTarget` | Enum | `PYPI`, `TEST_PYPI`, `GITHUB`, `LOCAL` |
| `PreflightResult` | Dataclass | Preflight check result before publishing |
| `PublishResult` | Dataclass | Post-publish outcome with URL and status |

## PAI Algorithm Phase Mapping

| Phase | Release Contribution | Key Classes |
|-------|----------------------|-------------|
| **OBSERVE** (1/7) | Check current version certification status before planning release work | `ReleaseValidator` |
| **PLAN** (3/7) | Determine which checks are failing to plan remediation | `ReleaseCertification.checks` |
| **EXECUTE** (5/7) | Build and publish artifacts once all checks pass | `PackageBuilder`, `DistributionManager` |
| **VERIFY** (6/7) | Confirm artifacts were published and are downloadable | `PublishResult`, `PreflightResult` |

### Concrete PAI Usage Pattern

In an EXECUTE phase ISC criterion "Release v1.0.3 published to PyPI":

```python
from codomyrmex.release import ReleaseValidator, PackageBuilder, DistributionManager, DistributionTarget

# Step 1: Certify
cert = ReleaseValidator().certify(version="1.0.3")
assert cert.status.name == "PASS", f"Release not certified: {[c for c in cert.checks if c.status.name != 'PASS']}"

# Step 2: Build
report = PackageBuilder().build(formats=["sdist", "wheel"])
assert report.artifacts, "No artifacts produced"

# Step 3: Publish
result = DistributionManager().publish(target=DistributionTarget.PYPI, artifacts=report.artifacts)
assert result.url, "Publish failed — no URL returned"
```

## Architecture Role

**Service Layer** — Release pipeline. Depends on Foundation Layer (`environment_setup`,
`logging_monitoring`) and Core Layer (`static_analysis`, `git_operations`) for
certification checks. Consumed by CI/CD automation in the `.github/workflows/` release
pipeline.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.release import ...`
- CLI: `codomyrmex release <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
