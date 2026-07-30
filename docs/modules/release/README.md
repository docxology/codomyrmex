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

## Primary Interfaces

- `ReleasePolicy`, `ReleaseValidator`, `ReleaseCertification`
- `PackageBuilder`, `BuildReport`, `BuildArtifact`
- `DistributionManager`, `PublishResult`
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
