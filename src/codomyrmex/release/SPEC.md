# release -- Specification

**Version**: v1.0.2 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `release` module provides a three-phase pipeline for validating, building, and
distributing Python packages within the Codomyrmex ecosystem. It is a pure Python
library (no MCP tools) that lives at the Service Layer and is consumed by CI/CD
pipelines and EXECUTE-phase automation scripts. All data structures are standard
`dataclass` instances. All enums use `str` values for serialization friendliness.

## Functional Requirements

### FR-1: Pre-Release Certification

The module must validate release readiness across five built-in check categories
and support user-defined custom checks.

| ID | Requirement |
|----|-------------|
| FR-1.1 | `ReleaseValidator` accepts a version string at construction |
| FR-1.2 | `check_tests(failures, total, max_skips)` records test suite pass/fail |
| FR-1.3 | `check_coverage(overall, tier1)` enforces overall >= 65% and tier1 >= 80% |
| FR-1.4 | `check_type_safety(errors)` records type-check error count (WARN, not FAIL) |
| FR-1.5 | `check_security(cve_count, secrets_found)` blocks on any CVE or leaked secret |
| FR-1.6 | `check_documentation(complete)` records doc completeness (WARN, not FAIL) |
| FR-1.7 | `add_custom_check(check)` accepts arbitrary `CertificationCheck` instances |
| FR-1.8 | `certify()` aggregates all checks; `certified=True` only when zero FAIL checks |
| FR-1.9 | `to_markdown(cert)` renders a certification report as a markdown table |

### FR-2: Package Building

The module must validate metadata, build dual-format artifacts, and compute
integrity checksums.

| ID | Requirement |
|----|-------------|
| FR-2.1 | `PackageBuilder` accepts optional `PackageMetadata` (defaults provided) |
| FR-2.2 | `validate_metadata()` returns errors for missing name, version, or python_requires |
| FR-2.3 | `build()` returns `BuildReport` with `success=False` if metadata validation fails |
| FR-2.4 | Successful build produces both sdist (`.tar.gz`) and wheel (`.whl`) artifacts |
| FR-2.5 | Each `BuildArtifact` includes filename, format, size_bytes, SHA-256 checksum, built_at |

### FR-3: Distribution

The module must run preflight checks and publish to multiple targets.

| ID | Requirement |
|----|-------------|
| FR-3.1 | `DistributionManager` accepts an optional `BuildReport` at construction |
| FR-3.2 | `preflight(target)` runs 3 checks: build exists, artifacts present, metadata valid |
| FR-3.3 | `publish(target)` runs preflight internally and fails if not ready |
| FR-3.4 | Four distribution targets: PYPI, TEST_PYPI, GITHUB, LOCAL |
| FR-3.5 | `PublishResult` includes target, artifacts_published count, URL, success, error |
| FR-3.6 | `publish_history()` returns all publish results in the current session |

## Interface Contract

### Public Exports (12 symbols from `__init__.py`)

**Validation:**

| Symbol | Kind | Description |
|--------|------|-------------|
| `ReleaseValidator` | Class | Orchestrates certification checks |
| `ReleaseCertification` | Dataclass | Aggregated certification report |
| `CertificationCheck` | Dataclass | Single check: name, category, status, value, threshold, message |
| `CertificationStatus` | Enum | `PASS`, `FAIL`, `SKIP`, `WARN` |

**Building:**

| Symbol | Kind | Description |
|--------|------|-------------|
| `PackageBuilder` | Class | Metadata validation and artifact construction |
| `BuildReport` | Dataclass | Build outcome: metadata, artifacts, warnings, success |
| `BuildArtifact` | Dataclass | Single artifact: filename, format, size_bytes, checksum, built_at |
| `PackageMetadata` | Dataclass | Package identity: name, version, description, author, license, python_requires, dependencies, entry_points |

**Distribution:**

| Symbol | Kind | Description |
|--------|------|-------------|
| `DistributionManager` | Class | Preflight and publish operations |
| `DistributionTarget` | Enum | `PYPI`, `TEST_PYPI`, `GITHUB`, `LOCAL` |
| `PreflightResult` | Dataclass | Preflight outcome: target, checks_passed, checks_total, ready, issues |
| `PublishResult` | Dataclass | Publish outcome: target, artifacts_published, url, success, error |

## Release Workflow

The canonical release workflow proceeds in strict order:

```
1. ReleaseValidator(version)
   |-- check_tests()
   |-- check_coverage()
   |-- check_type_safety()
   |-- check_security()
   |-- check_documentation()
   |-- add_custom_check()  (optional)
   v
2. certify() --> ReleaseCertification
   |-- certified? --NO--> abort, report blockers
   v (YES)
3. PackageBuilder(metadata).build() --> BuildReport
   |-- success? --NO--> abort, report warnings
   v (YES)
4. DistributionManager(report).preflight(target) --> PreflightResult
   |-- ready? --NO--> abort, report issues
   v (YES)
5. publish(target) --> PublishResult
   |-- success? --NO--> report error
   v (YES)
   Done. URL available at result.url
```

## Validation Rules

From `release_validator.py`:

- **Test Suite**: `failures == 0` required. Any nonzero failure count produces FAIL.
- **Code Coverage**: `overall >= 65.0` AND (if tier1 provided) `tier1 >= 80.0`.
  Both conditions must hold for PASS.
- **Type Safety**: `errors == 0` for PASS, nonzero produces WARN (not blocking).
- **Security**: `cve_count == 0 AND secrets_found == 0` required. Either nonzero
  produces FAIL.
- **Documentation**: `complete is True` for PASS, `False` produces WARN (not
  blocking).
- **Certification**: `certified = True` only when zero checks have
  `CertificationStatus.FAIL`. WARN and SKIP checks do not block.

## Distribution Formats

| Target | Enum Value | URL Pattern |
|--------|-----------|-------------|
| PyPI | `DistributionTarget.PYPI` | `https://pypi.org/project/{name}/{version}/` |
| TestPyPI | `DistributionTarget.TEST_PYPI` | `https://test.pypi.org/project/{name}/{version}/` |
| GitHub | `DistributionTarget.GITHUB` | `https://github.com/docxology/{name}/releases/tag/v{version}` |
| Local | `DistributionTarget.LOCAL` | No URL (local filesystem only) |

Artifact formats per build:

| Format | Extension | Description |
|--------|-----------|-------------|
| sdist | `.tar.gz` | Source distribution archive |
| wheel | `.whl` | Pre-built binary distribution (`py3-none-any`) |

## Error Handling

| Condition | Behavior |
|-----------|----------|
| Missing package name | `validate_metadata()` returns `["Package name is required"]` |
| Missing version | `validate_metadata()` returns `["Version is required"]` |
| Missing python_requires | `validate_metadata()` returns `["Python version requirement is missing"]` |
| Metadata validation fails | `build()` returns `BuildReport(success=False, warnings=errors)` |
| Preflight fails | `publish()` returns `PublishResult(success=False, error="Pre-flight failed: ...")` |
| No build provided | `preflight()` reports "No successful build available" |
| No artifacts | `preflight()` reports "No build artifacts found" |
| Incomplete metadata | `preflight()` reports "Package metadata incomplete" |

No exceptions are raised by the public API. All error conditions are reported via
return values (`success=False`, `certified=False`, `ready=False`).

## Dependencies

- **Runtime**: Python standard library only (`hashlib`, `time`, `dataclasses`,
  `enum`). Zero external dependencies.
- **Upstream consumers**: `ci_cd_automation`, `.github/workflows/release.yml`.
- **Data sources for checks**: `static_analysis` (type errors), `security`
  (CVEs, secrets), test runners (failures, coverage), `documentation` (completeness).

## Security Considerations

- **SHA-256 checksums**: Every `BuildArtifact` includes a SHA-256 checksum for
  integrity verification.
- **Preflight gating**: `DistributionManager.publish()` always runs preflight
  internally before proceeding -- there is no way to bypass preflight.
- **No credential storage**: The module does not store or manage PyPI tokens,
  GitHub tokens, or any authentication credentials. Credential management is
  the responsibility of the CI/CD environment.
- **Security check enforcement**: `check_security()` with any nonzero CVE or
  secret count produces a FAIL that blocks certification entirely.

## Testing Requirements

Tests for this module must follow the project zero-mock policy:

- **No mocks, stubs, or fake data.** All tests run against real `ReleaseValidator`,
  `PackageBuilder`, and `DistributionManager` instances.
- Use `@pytest.mark.skipif` for tests that require external services (PyPI upload,
  GitHub API).
- Core certification, build, and preflight logic requires no external services and
  must always be testable.
- Test files belong in `src/codomyrmex/tests/unit/release/`.

Example test structure:

```python
from codomyrmex.release import (
    ReleaseValidator, PackageBuilder, PackageMetadata,
    DistributionManager, DistributionTarget,
)

def test_certification_passes_when_no_failures():
    v = ReleaseValidator(version="1.0.0")
    v.check_tests(failures=0, total=100)
    v.check_coverage(overall=70, tier1=85)
    cert = v.certify()
    assert cert.certified is True
    assert cert.blockers == []

def test_certification_fails_on_test_failures():
    v = ReleaseValidator(version="1.0.0")
    v.check_tests(failures=3, total=100)
    cert = v.certify()
    assert cert.certified is False
    assert "Test Suite" in cert.blockers

def test_build_validates_metadata():
    builder = PackageBuilder(PackageMetadata(name="", version="1.0.0"))
    report = builder.build()
    assert report.success is False

def test_preflight_requires_build():
    dm = DistributionManager()
    pf = dm.preflight(DistributionTarget.PYPI)
    assert pf.ready is False
```

## Navigation

- [README.md](README.md) -- Module overview and quick start
- [AGENTS.md](AGENTS.md) -- Agentic operating contracts
- [PAI.md](PAI.md) -- PAI integration and phase mapping
- [Parent SPEC](../SPEC.md) -- Source-level specification
