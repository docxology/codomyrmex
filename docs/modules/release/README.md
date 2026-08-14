# Release

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

The release module converts measured local evidence into real, verifiable
package and technical-report artifacts. Its default policy fails closed:
testing, coverage, typing, security, documentation, and artifact verification
must all be explicitly present and passing.

The implementation:

- runs a real isolated `uv build`, inspects metadata and member paths, and
  rejects traversal, absolute, SCM, cache, private-environment, and
  checkout-specific entries or content;
- records local paths, media types, byte sizes, SHA-256, and SHA-512;
- performs verified local copies;
- produces non-mutating dry-run receipts for remote package targets;
- prepares and verifies a portable technical-report bundle;
- plans GitHub and Zenodo-sandbox publication without uploading anything.

## Canonical Commands

```bash
uv run --locked pytest tests/unit/release -q
uv run --locked python -m codomyrmex.release publication prepare
uv run --locked python -m codomyrmex.release publication verify \
  output/release/codomyrmex-1.3.0
uv run --locked python -m codomyrmex.release publication plan \
  output/release/codomyrmex-1.3.0 --target github
```

The `plan` command always writes `dry_run: true` and `executed: false`.

For source-bound release test evidence, use the explicit release profile so
coverage cannot be confused with an ordinary local test run:

```bash
uv run --locked python -m codomyrmex.release.test_evidence \
  --repo-root . \
  --receipt release-test-evidence.json \
  --test-path tests/unit/ \
  --profile release \
  --coverage-report coverage.xml \
  --coverage-floor 60 \
  --required-output-path coverage.xml \
  --max-skips 600 \
  --max-warnings 0 \
  --require-clean \
  --pytest-arg=--cov=src/codomyrmex \
  --pytest-arg=--cov-report=xml \
  --pytest-arg=--cov-fail-under=60
```

The local profile is useful for developer diagnostics, but a dirty local
receipt is never certified. The release unit tree includes bounded optional
provider and infrastructure probes; the release workflow currently permits up
to 600 such outcomes and the receipt preserves every node ID and reason.
Missing or malformed JUnit/coverage reports, skips without reasons, stale
required outputs, and tracked-source output paths are blocking evidence errors.

## Primary Interfaces

- `ReleasePolicy`, `ReleaseValidator`, `ReleaseCertification`
- `PackageBuilder`, `BuildReport`, `BuildArtifact`
- `DistributionManager`, `PublishResult`
- `run_release_test_evidence()`, `ReleaseTestEvidence`, and JUnit/warning
  evidence parsing for source-bound release gates. Evidence has explicit
  `local` and `release` profiles; required outputs must be freshly generated,
  coverage is validated against an explicit floor, and missing or malformed
  JUnit evidence fails closed. The evidence invocation disables the
  pytest-benchmark plugin; performance measurements remain a separate opt-in
  lane.
- `PublicationMetadata`, `PublicationArtifact`, `PublicationManifest`,
  `PublicationBundle`, `PublicationVerification`
- `prepare_publication_bundle()`, `verify_publication_bundle()`,
  `plan_publication()`

## Evidence Boundary

A valid local bundle proves that the recorded files match their detached
digests and declared source receipt. It does not prove that an external archive
accepted the files, that a DOI was assigned, or that a deployment is safe.

## Navigation

- [Specification](SPEC.md)
- [PAI integration](PAI.md)
- [Agent guide](AGENTS.md)
- [Source API specification](../../../src/codomyrmex/release/API_SPECIFICATION.md)
- [Source MCP specification](../../../src/codomyrmex/release/MCP_TOOL_SPECIFICATION.md)
- [Source changelog](../../../src/codomyrmex/release/CHANGELOG.md)
