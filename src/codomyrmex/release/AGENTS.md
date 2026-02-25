# release -- Agentic Context

**Version**: v1.0.2 | **Status**: Active | **Last Updated**: February 2026

## Purpose

This document provides operating contracts and integration guidance for autonomous
agents working within or consuming the `release` module. The module manages the
three-phase release pipeline: **certify** (validate readiness), **build** (produce
sdist and wheel artifacts with checksums), and **publish** (distribute to PyPI,
TestPyPI, GitHub, or local targets). Agents must follow the contracts below to
interact with this module correctly and safely.

## Active Components

| Component | Type | File | Status |
|-----------|------|------|--------|
| `ReleaseValidator` | Class | `release_validator.py` | Active -- runs 5 built-in certification checks |
| `ReleaseCertification` | Dataclass | `release_validator.py` | Active -- certification report with per-check detail |
| `CertificationCheck` | Dataclass | `release_validator.py` | Active -- individual check result |
| `CertificationStatus` | Enum | `release_validator.py` | Active -- PASS, FAIL, SKIP, WARN |
| `PackageBuilder` | Class | `package_builder.py` | Active -- validates metadata and builds artifacts |
| `BuildReport` | Dataclass | `package_builder.py` | Active -- build outcome with artifact list |
| `BuildArtifact` | Dataclass | `package_builder.py` | Active -- single artifact (path, format, size, checksum) |
| `PackageMetadata` | Dataclass | `package_builder.py` | Active -- package name, version, deps, entry points |
| `DistributionManager` | Class | `distribution.py` | Active -- preflight and publish to targets |
| `DistributionTarget` | Enum | `distribution.py` | Active -- PYPI, TEST_PYPI, GITHUB, LOCAL |
| `PreflightResult` | Dataclass | `distribution.py` | Active -- preflight check outcome |
| `PublishResult` | Dataclass | `distribution.py` | Active -- post-publish outcome with URL |

## Quick Verification

```bash
# Verify module imports cleanly
uv run python -c "
from codomyrmex.release import (
    ReleaseValidator, ReleaseCertification, CertificationCheck, CertificationStatus,
    PackageBuilder, BuildReport, BuildArtifact, PackageMetadata,
    DistributionManager, DistributionTarget, PreflightResult, PublishResult,
)
print('release: all 12 exports loaded')
"

# Verify certification pipeline
uv run python -c "
from codomyrmex.release import ReleaseValidator
v = ReleaseValidator(version='0.0.1-test')
v.check_tests(failures=0, total=10)
v.check_coverage(overall=70, tier1=85)
cert = v.certify()
print(f'Certified: {cert.certified}, Checks: {cert.passed_checks}/{cert.total_checks}')
"

# Verify build pipeline
uv run python -c "
from codomyrmex.release import PackageBuilder, PackageMetadata
b = PackageBuilder(PackageMetadata(name='test-pkg', version='0.1.0'))
r = b.build()
print(f'Build success: {r.success}, Artifacts: {[a.filename for a in r.artifacts]}')
"

# Verify distribution preflight
uv run python -c "
from codomyrmex.release import PackageBuilder, DistributionManager, DistributionTarget
report = PackageBuilder().build()
dm = DistributionManager(report)
pf = dm.preflight(DistributionTarget.TEST_PYPI)
print(f'Preflight ready: {pf.ready}, Checks: {pf.checks_passed}/{pf.checks_total}')
"
```

## Operating Contracts

1. **Certify before build, preflight before publish.** Always run
   `ReleaseValidator.certify()` and confirm `cert.certified is True` before
   invoking `PackageBuilder.build()`. Always check `preflight.ready` before
   calling `DistributionManager.publish()`. The pipeline enforces this order
   internally via preflight checks but agents must not skip certification.

2. **Never publish to PYPI without full certification.** Only publish to
   `DistributionTarget.PYPI` when all FAIL-level checks pass. Use
   `DistributionTarget.TEST_PYPI` or `DistributionTarget.LOCAL` for dry runs
   and validation cycles.

3. **Treat WARN checks as informational, FAIL checks as blockers.** Type safety
   and documentation checks produce WARN status, not FAIL. Agents may proceed
   with WARN-only certifications but must log warnings. FAIL checks block
   certification entirely via `cert.blockers`.

4. **Do not invent MCP tools.** This module has no `mcp_tools.py` and exposes
   zero MCP tools. Agents must consume it as a Python library import. Do not
   register wrapper MCP tools around release functions.

5. **Preserve publish history.** `DistributionManager.publish_history()` returns
   all publish results in the current session. Agents should inspect history
   before re-publishing to avoid duplicate uploads.

## Certification Checks Reference

| Check Method | Category | FAIL Threshold | WARN Threshold |
|-------------|----------|----------------|----------------|
| `check_tests(failures, total)` | testing | failures > 0 | -- |
| `check_coverage(overall, tier1)` | quality | overall < 65% or tier1 < 80% | -- |
| `check_type_safety(errors)` | quality | -- | errors > 0 |
| `check_security(cve_count, secrets_found)` | security | cve_count > 0 or secrets_found > 0 | -- |
| `check_documentation(complete)` | docs | -- | complete is False |
| `add_custom_check(check)` | user-defined | user-defined | user-defined |

## Integration Points

- **ci_cd_automation** -- CI pipelines call `ReleaseValidator` then
  `PackageBuilder` then `DistributionManager` in sequence.
- **git_operations** -- version tags and changelogs feed into `PackageMetadata`.
- **security** -- CVE and secrets scan results feed into `check_security()`.
- **static_analysis** -- type-check error counts feed into `check_type_safety()`.
- **documentation** -- doc completeness status feeds into `check_documentation()`.
- **logging_monitoring** -- certification reports should be logged for audit trail.

## PAI Phase Mapping

| PAI Phase | Release Role |
|-----------|-------------|
| OBSERVE | Check current certification status |
| PLAN | Identify failing checks and plan remediation |
| EXECUTE | Build and publish artifacts |
| VERIFY | Confirm publish result URL is accessible |

## Navigation

- **Module**: `src/codomyrmex/release/`
- **PAI integration**: [PAI.md](PAI.md)
- **Specification**: [SPEC.md](SPEC.md)
- **Module overview**: [README.md](README.md)
- **Root bridge**: [/PAI.md](../../../PAI.md)
