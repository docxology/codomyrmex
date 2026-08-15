# Release

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

`codomyrmex.release` provides fail-closed release evidence, real Python package
builds, verified local distribution, and portable technical-report publication
bundles. It does not upload artifacts or fabricate remote publication success.

The module has four cooperating surfaces:

- `ReleaseValidator` requires explicit test, coverage, typing, security,
  documentation, and artifact evidence under the default strict policy.
- `test_evidence` runs source-bound pytest evidence, preserves every skipped-test
  and warning detail, records an explicit `local` or `release` profile, and
  fails closed on stale or mutated checkout state. Required report outputs must
  be freshly produced by the invocation; merely allowing a path does not make
  a stale coverage report valid. The evidence invocation disables the
  pytest-benchmark plugin; performance measurements remain a separate opt-in
  lane so xdist cannot turn release evidence into a warning-producing benchmark
  run.
- `PackageBuilder` runs an isolated `uv build`, inspects wheel and sdist
  metadata and member paths, rejects traversal, absolute, SCM, cache, and
  private-environment entries plus checkout-specific content, and records each
  real file's path, media type, size, SHA-256, and SHA-512.
- `DistributionManager` performs a verified local copy. PyPI, TestPyPI, and
  GitHub targets return non-mutating dry-run receipts and reject execution.
- `prepare_publication_bundle()`, `verify_publication_bundle()`, and
  `plan_publication()` assemble and verify a portable report bundle and write
  GitHub or Zenodo-sandbox plans without contacting either service.

## Quick Start

```python
from pathlib import Path

from codomyrmex.release import (
    DistributionManager,
    DistributionTarget,
    PackageBuilder,
    PackageMetadata,
    ReleaseValidator,
)

validator = ReleaseValidator(version="1.3.0")
validator.check_tests(failures=0, total=1, skipped=0)
validator.check_coverage(overall=60.0)
validator.check_type_safety(errors=0)
validator.check_security(cve_count=0, secrets_found=0)
validator.check_documentation(complete=True)

report = PackageBuilder(
    PackageMetadata(name="codomyrmex", version="1.3.0"),
    source_dir=Path.cwd(),
).build()
validator.check_artifacts(
    verified=report.success,
    artifact_count=len(report.artifacts),
)
certification = validator.certify()
assert certification.certified

result = DistributionManager(report).publish(
    DistributionTarget.LOCAL,
    destination=Path("output/local-distribution"),
)
assert result.success and result.executed and not result.dry_run
```

Prepare and inspect the technical-report bundle only after the manuscript has
produced `output/paper-content.pdf`, `output/paper.pdf`, and
`output/paper.html`:

```bash
uv run --locked python -m codomyrmex.release publication prepare
uv run --locked python -m codomyrmex.release publication verify \
  output/release/codomyrmex-1.3.0
uv run --locked python -m codomyrmex.release publication plan \
  output/release/codomyrmex-1.3.0 --target github
uv run --locked python -m codomyrmex.release publication plan \
  output/release/codomyrmex-1.3.0 --target zenodo-sandbox
```

Both `plan` commands are always dry runs. They write receipts with
`executed: false`; they do not create a release, reserve a DOI, or upload files.

## Publication Manifest v1

`publication_manifest.json` uses portable relative paths and records:

- shared publication metadata, with an absent DOI represented as `null`;
- source commit, dirty-state boolean, and a digest of the captured status;
- producer versions and `SOURCE_DATE_EPOCH`;
- reproducibility-input identities;
- artifact roles, media types, sizes, SHA-256, and SHA-512;
- caller-supplied validation outcomes.

The `receipts/source-state.json` receipt is schema v2 when a manuscript variable
snapshot is included. In addition to the checkout commit, dirty state, and status
digest, it records the rendered commit, manuscript configuration digest, and
Colony Kernel/manuscript source digest. The manuscript source-current validator
compares those fields with the live checkout and released artifacts.

The bundle also contains `CITATION.cff`, `.zenodo.json`,
`publication_metadata.json`, `SHA256SUMS`, `SHA512SUMS`, source-state and other
validation receipts, the content and distribution PDFs, and semantic HTML.
Checksum files and the manifest are detached from the visible PDF, avoiding
circular self-hashing. No credentials or absolute home paths are written into
the manifest.

## Compatibility Notes

- `BuildArtifact.checksum` remains as an alias for the complete SHA-256 digest;
  callers should prefer `sha256` and also verify `sha512`.
- The default `ReleasePolicy` is strict. Missing evidence, nonzero typing
  diagnostics, incomplete documentation, and failed artifact verification now
  block certification.
- `run_release_test_evidence()` defaults to the usable `local` profile. The
  `release` profile requires a clean checkout, zero warnings, a parsed JUnit
  report with a digest, an explicitly validated coverage XML report and floor,
  and any required output refreshed during the same run. A local receipt is not
  release evidence merely because its tests pass.
- Remote `DistributionManager.publish()` calls default to dry-run receipts.
  Passing `dry_run=False` for a remote target fails.
- Local publication requires an explicit destination and verifies the copied
  bytes against both recorded digests.

## Files

- `release_validator.py` — evidence policy and certification receipts
- `package_builder.py` — isolated real builds and artifact inspection
- `distribution.py` — verified local copies and remote dry-run plans
- `publication.py` — immutable publication types, manifest, bundle, and plans
- `__main__.py` — `python -m codomyrmex.release publication ...`
- `mcp_tools.py` — strict validation, real build, and report tools

## Navigation

- [API specification](API_SPECIFICATION.md)
- [Functional specification](SPEC.md)
- [MCP tools](MCP_TOOL_SPECIFICATION.md)
- [PAI integration](PAI.md)
- [Agent guide](AGENTS.md)
- [Module documentation mirror](../../../docs/modules/release/README.md)
