# release -- Release & Distribution Management

**Version**: v1.0.2 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `release` module manages the full release lifecycle for Codomyrmex packages:
validating that a version is ready to ship, building distribution artifacts (sdist
and wheel), and publishing them to targets such as PyPI, TestPyPI, GitHub Releases,
and local directories.

Three classes handle the pipeline end-to-end. `ReleaseValidator` runs pre-release
certification checks (tests, coverage, type safety, security, documentation) and
produces a `ReleaseCertification` report with per-check status. `PackageBuilder`
validates package metadata and builds `sdist` and `wheel` artifacts, returning
`BuildArtifact` records with SHA-256 checksums. `DistributionManager` runs preflight
checks and publishes artifacts to a chosen `DistributionTarget`.

This module does **not** expose MCP tools. It is consumed as a Python library by
CI/CD pipelines and EXECUTE-phase scripts.

## Key Capabilities

- **Pre-release certification** -- test pass rate, code coverage (overall >= 65%,
  tier1 >= 80%), type safety, security posture (CVEs, secrets), documentation
  completeness.
- **Custom certification checks** -- add arbitrary `CertificationCheck` instances
  via `ReleaseValidator.add_custom_check()`.
- **Certification markdown report** -- `ReleaseValidator.to_markdown()` renders a
  human-readable certification table with status icons and blocker list.
- **Package metadata validation** -- name, version, and `python_requires` are
  validated before any build proceeds.
- **Dual-format artifact builds** -- produces both `.tar.gz` (sdist) and `.whl`
  (wheel) with SHA-256 checksums.
- **Preflight checks** -- verifies build success, artifact presence, and metadata
  completeness before any publish attempt.
- **Four distribution targets** -- `PYPI`, `TEST_PYPI`, `GITHUB`, `LOCAL`.
- **Publish history** -- `DistributionManager.publish_history()` tracks all
  publish operations in the current session.

## Quick Start

```python
from codomyrmex.release import (
    ReleaseValidator,
    PackageBuilder,
    PackageMetadata,
    DistributionManager,
    DistributionTarget,
)

# Step 1: Certify release readiness
validator = ReleaseValidator(version="1.0.3")
validator.check_tests(failures=0, total=9000)
validator.check_coverage(overall=67, tier1=82)
validator.check_type_safety(errors=0)
validator.check_security(cve_count=0, secrets_found=0)
validator.check_documentation(complete=True)
cert = validator.certify()
assert cert.certified, f"Blockers: {cert.blockers}"

# Step 2: Build artifacts
metadata = PackageMetadata(name="codomyrmex", version="1.0.3")
builder = PackageBuilder(metadata)
report = builder.build()
assert report.success and report.artifacts

# Step 3: Publish
manager = DistributionManager(report)
preflight = manager.preflight(DistributionTarget.PYPI)
if preflight.ready:
    result = manager.publish(DistributionTarget.PYPI)
    print(result.url)  # https://pypi.org/project/codomyrmex/1.0.3/
```

## Module Structure

| File | Purpose |
|------|---------|
| `__init__.py` | Public API -- re-exports all 12 symbols |
| `release_validator.py` | `ReleaseValidator`, `ReleaseCertification`, `CertificationCheck`, `CertificationStatus` |
| `package_builder.py` | `PackageBuilder`, `BuildReport`, `BuildArtifact`, `PackageMetadata` |
| `distribution.py` | `DistributionManager`, `DistributionTarget`, `PreflightResult`, `PublishResult` |
| `PAI.md` | PAI integration guide with phase mapping |
| `AGENTS.md` | Agentic operating contracts |
| `SPEC.md` | Formal specification |

## Configuration

`PackageMetadata` controls build configuration:

| Field | Default | Description |
|-------|---------|-------------|
| `name` | `"codomyrmex"` | Package name |
| `version` | `"1.0.0"` | Semantic version string |
| `description` | `""` | Package description |
| `author` | `""` | Author name |
| `license` | `"MIT"` | License identifier |
| `python_requires` | `">=3.11"` | Minimum Python version |
| `dependencies` | `[]` | Runtime dependencies |
| `entry_points` | `{}` | CLI entry points |

Certification thresholds in `ReleaseValidator`:

| Check | Threshold | Blocking |
|-------|-----------|----------|
| Test Suite | 0 failures | Yes (FAIL) |
| Code Coverage | overall >= 65%, tier1 >= 80% | Yes (FAIL) |
| Type Safety | 0 errors | No (WARN) |
| Security | 0 CVEs, 0 secrets | Yes (FAIL) |
| Documentation | all docs current | No (WARN) |

## Dependencies

- Python standard library only (`hashlib`, `time`, `dataclasses`, `enum`).
- No external runtime dependencies.
- Consumed by: `ci_cd_automation`, `.github/workflows/release.yml`.

## Architecture Layer

**Service Layer** -- depends on Foundation Layer (`environment_setup`,
`logging_monitoring`) and Core Layer (`static_analysis`, `git_operations`) for
certification checks during real CI pipeline runs.

## Related Modules

- [ci_cd_automation](../ci_cd_automation/) -- pipeline orchestration that invokes release
- [git_operations](../git_operations/) -- version tagging and changelog generation
- [security](../security/) -- vulnerability scanning consumed by `check_security`
- [static_analysis](../coding/static_analysis/) -- linting and type-check results
- [documentation](../documentation/) -- doc completeness for `check_documentation`

## Navigation

- [PAI.md](PAI.md) -- PAI integration and phase mapping
- [AGENTS.md](AGENTS.md) -- Agentic operating contracts
- [SPEC.md](SPEC.md) -- Formal specification
- [Parent README](../README.md) -- Source-level overview
