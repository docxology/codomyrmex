# Release Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `release` module provides Python-native tools for validating release readiness, building distribution artifacts, and managing publication to distribution targets (PyPI, TestPyPI, GitHub, local). It is designed for use in CI/CD pipelines and release automation scripts.

## 2. Core Components

### 2.1 Release Validation (`release_validator.py`)

**`CertificationStatus`** (enum): `PASS`, `FAIL`, `SKIP`, `WARN`

**`CertificationCheck`** (dataclass):
| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Check name |
| `category` | `str` | Category (testing, quality, security, docs) |
| `status` | `CertificationStatus` | Result |
| `value` | `str` | Measured value |
| `threshold` | `str` | Required threshold |
| `message` | `str` | Human-readable result message |

**`ReleaseCertification`** (dataclass): Complete certification report.
| Field/Property | Type | Description |
|----------------|------|-------------|
| `version` | `str` | Release version |
| `checks` | `list[CertificationCheck]` | All checks run |
| `certified` | `bool` | True if zero FAIL checks |
| `certified_at` | `float` | Unix timestamp (0 if not certified) |
| `blockers` | `list[str]` | Names of FAIL checks |
| `total_checks` | property `int` | Total check count |
| `passed_checks` | property `int` | PASS check count |
| `pass_rate` | property `float` | passed/total ratio |

**`ReleaseValidator`** class:

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `(version="1.0.0")` | — | Initialize with version string |
| `check_tests` | `(failures, total, max_skips=50)` | `CertificationCheck` | Pass if `failures == 0` |
| `check_coverage` | `(overall, tier1=0)` | `CertificationCheck` | Pass if `overall >= 65%` and `tier1 >= 80%` (when tier1 > 0) |
| `check_type_safety` | `(errors: int)` | `CertificationCheck` | WARN (not FAIL) if errors > 0 |
| `check_security` | `(cve_count, secrets_found)` | `CertificationCheck` | Pass if both are 0 |
| `check_documentation` | `(complete: bool)` | `CertificationCheck` | WARN (not FAIL) if incomplete |
| `add_custom_check` | `(check: CertificationCheck)` | `None` | Add a custom check |
| `certify` | `()` | `ReleaseCertification` | Run certification; certified = zero FAIL checks |
| `to_markdown` | `(cert: ReleaseCertification)` | `str` | Render report as Markdown table |
| `check_count` | property `int` | — | Number of checks added |

### 2.2 Package Building (`package_builder.py`)

**`PackageMetadata`** (dataclass): `name`, `version`, `description`, `author`, `license`, `python_requires` (default `">=3.11"`), `dependencies: list[str]`, `entry_points: dict[str, str]`

**`BuildArtifact`** (dataclass): `filename`, `format` (`"wheel"` or `"sdist"`), `size_bytes`, `checksum` (SHA-256 prefix), `built_at: float`

**`BuildReport`** (dataclass): `metadata`, `artifacts: list[BuildArtifact]`, `warnings: list[str]`, `success: bool`

**`PackageBuilder`** class:

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `(metadata: PackageMetadata \| None)` | — | Initialize with metadata; defaults to `PackageMetadata()` |
| `validate_metadata` | `()` | `list[str]` | Validate name, version, python_requires; returns errors |
| `build` | `()` | `BuildReport` | Build sdist + wheel artifacts; fails if metadata invalid |
| `metadata` | property | `PackageMetadata` | Access current metadata |

### 2.3 Distribution Management (`distribution.py`)

**`DistributionTarget`** (enum): `PYPI`, `TEST_PYPI`, `GITHUB`, `LOCAL`

**`PreflightResult`** (dataclass): `target`, `checks_passed`, `checks_total`, `ready: bool`, `issues: list[str]`

**`PublishResult`** (dataclass): `target`, `artifacts_published`, `url`, `success: bool`, `error: str`

**`DistributionManager`** class:

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `(build: BuildReport \| None)` | — | Initialize with a build report |
| `preflight` | `(target: DistributionTarget)` | `PreflightResult` | Check build, artifacts, and metadata (3 checks) |
| `publish` | `(target: DistributionTarget)` | `PublishResult` | Run preflight; publish if ready; sets URL for PyPI/TestPyPI/GitHub |
| `publish_history` | `()` | `list[PublishResult]` | All previous publish operations |
| `has_build` | property `bool` | — | True if build report exists and succeeded |

## 3. Usage Example

```python
from codomyrmex.release import (
    ReleaseValidator, PackageBuilder, PackageMetadata,
    DistributionManager, DistributionTarget
)

# Validate release
validator = ReleaseValidator(version="1.2.0")
validator.check_tests(failures=0, total=9000)
validator.check_coverage(overall=68.5, tier1=83.0)
validator.check_security(cve_count=0, secrets_found=0)
cert = validator.certify()
print(f"Certified: {cert.certified} ({cert.passed_checks}/{cert.total_checks})")

# Build package
metadata = PackageMetadata(name="codomyrmex", version="1.2.0",
                           python_requires=">=3.11")
builder = PackageBuilder(metadata)
report = builder.build()
assert report.success

# Publish
dm = DistributionManager(report)
preflight = dm.preflight(DistributionTarget.PYPI)
if preflight.ready:
    result = dm.publish(DistributionTarget.PYPI)
    print(f"Published: {result.url}")
```
