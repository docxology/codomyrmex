# `release` — Functional Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Provide a fail-closed release boundary that separates local evidence and
artifact construction from externally authorized publication.

## Requirements

### Certification

- The default `ReleasePolicy` is strict.
- Certification requires supplied and passing evidence for tests, coverage,
  typing, security, documentation, and artifacts.
- Zero executed tests is not valid evidence.
- Missing required categories are named as blockers.
- Relaxed policy may downgrade typing and documentation failures to warnings,
  but must be explicitly selected.

### Test evidence profiles

- `run_release_test_evidence()` defaults to `profile="local"` so a developer
  can collect truthful evidence from a dirty checkout without changing the
  checkout or hiding skips and warnings.
- `profile="release"` is fail-closed: it requires a clean source checkout and
  `max_warnings=0`. The receipt records the profile, a SHA-256 digest of the
  parsed JUnit report, every skipped test and warning, and named blockers. It
  also requires a repository-local coverage XML report and explicit percentage
  floor; the measured line rate and detached SHA-256 digest are recorded and
  compared to that floor. The evidence invocation disables the
  pytest-benchmark plugin; performance measurement is a separate opt-in lane.
- `allowed_output_paths` only permits expected checkout mutations. It does not
  prove that an artifact was generated. `required_output_paths` additionally
  requires each report to be a repository-local file refreshed during the
  invocation; release runs reject pre-existing required outputs to prevent
  stale coverage reports from becoming green evidence.
- A missing, empty, malformed, ambiguous, or count-inconsistent JUnit report is
  an error. A zero-test report is never successful evidence.

### Package construction

- `PackageBuilder` runs `uv build` in an isolated build environment.
- A successful report contains exactly one wheel and one sdist.
- Embedded `Name` and `Version` metadata must match expected metadata.
- Archive members must be relative and traversal-free. Private-worktree and
  cache components such as `.git`, `.env`, and `__pycache__` are forbidden.
- File contents must not embed the active source directory or user-home path.
- Each artifact records a real absolute local path, media type, byte size,
  complete SHA-256, complete SHA-512, and build time.
- `SOURCE_DATE_EPOCH` is forwarded when requested.
- Build failures and metadata mismatches return unsuccessful receipts; no
  placeholder artifact is created.

### Distribution

- Preflight verifies success, artifact presence, metadata, file size, and both
  hashes.
- A local target requires an explicit destination, copies real files, and
  verifies the copies.
- PyPI, TestPyPI, and GitHub targets default to dry-run receipts.
- Remote execution is disabled and must never be represented as successful
  publication.
- `PublishResult.executed` and `dry_run` disambiguate plans from actions.

### Technical-report publication

- Publication metadata is shared across the manifest, citation file, and Zenodo
  metadata.
- `prepare_publication_bundle()` requires an existing content PDF,
  distribution PDF, and semantic HTML report.
- Manifest v1 contains only portable artifact paths and contains no
  credentials.
- It records source commit, dirty state and its digest, tool versions, input
  hashes, artifact roles and hashes, and validation outcomes.
- When `manuscript_variables.json` is included, `receipts/source-state.json` also
  records the rendered commit, manuscript configuration digest, and first-party
  Colony Kernel/manuscript source digest.
- The final distribution PDF hash appears only in the detached manifest and
  checksum files.
- `verify_publication_bundle()` detects missing, malformed, moved, resized, or
  tampered artifacts.
- GitHub and Zenodo-sandbox plans require `dry_run=True`, write receipts with
  `executed: false`, and perform no network mutation.

## Required Bundle Layout

```text
output/release/codomyrmex-<version>/
├── codomyrmex-<version>-content.pdf
├── codomyrmex-<version>.pdf
├── codomyrmex-<version>.html
├── CITATION.cff
├── .zenodo.json
├── publication_metadata.json
├── publication_manifest.json
├── SHA256SUMS
├── SHA512SUMS
├── receipts/
└── reproducibility/
```

## Failure Semantics

| Condition | Required result |
|---|---|
| Required certification evidence absent | uncertified receipt with named blocker |
| Real build command fails | unsuccessful `BuildReport`, no invented files |
| Built metadata differs | unsuccessful `BuildReport` |
| Archive member is unsafe or private | unsuccessful `BuildReport`, no copied artifact |
| Archive content embeds a local checkout/home path | unsuccessful `BuildReport`, no copied artifact |
| Artifact bytes change | preflight or bundle verification fails |
| Remote distribution requests execution | unsuccessful `PublishResult` |
| Publication plan sets `dry_run=False` | `ValueError` |
| Required report artifact is absent | `FileNotFoundError` |
| Manifest path is absolute or escapes root | verification failure |

## Verification

Use real temporary package repositories and rendered fixture files. Tests must
cover deterministic fixed-epoch timestamps, artifact tampering, portable paths,
required roles, visible content hashes, verified local copies, and remote
dry-run immutability.

## Navigation

- [README](README.md)
- [API specification](API_SPECIFICATION.md)
- [MCP tools](MCP_TOOL_SPECIFICATION.md)
- [PAI integration](PAI.md)
- [Changelog](CHANGELOG.md)
