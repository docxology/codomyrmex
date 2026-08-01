# Release Module Changelog

## Unreleased

### Added

- Manuscript bundles now retain source-current configuration and first-party source
  digests in the schema-v2 `source-state.json` receipt when the variable snapshot is
  included.

- Immutable publication metadata, artifact, bundle, manifest, verification,
  plan, and strict policy types.
- Portable `publication_manifest.json` v1 with source-state, producer, input,
  artifact, validation, SHA-256, and SHA-512 receipts.
- `publication prepare`, `verify`, and dry-run `plan` CLI commands.

### Changed

- `PackageBuilder` now runs a real isolated `uv build` and inspects the wheel
  and sdist rather than creating simulated artifact records.
- Package builds now reject absolute or traversing archive members and
  private-worktree/cache components such as `.git`, `.env`, and `__pycache__`
  before copying an artifact from the isolated stage.
- Artifact inspection also rejects files containing the active source
  directory or user-home path.
- `BuildArtifact` now includes `path`, `media_type`, complete `sha256`, and
  complete `sha512`; `checksum` remains a compatibility alias for SHA-256.
- Default release certification is strict and fails when any required evidence
  category is missing or failing.
- `PublishResult` now distinguishes `executed` from `dry_run` and carries a
  machine-readable receipt.
- Remote distribution is planning-only. Local distribution performs and
  verifies a real copy to an explicit destination.

### Security

- Remote publication cannot be triggered by this module.
- Publication manifests reject non-portable paths and do not store
  credentials.
- Wheel and sdist inspection prevents nested SCM metadata from leaking local
  checkout paths into distributable artifacts.
