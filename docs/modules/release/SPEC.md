# Release — Functional Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Package and verify release artifacts locally while ensuring external
publication remains an explicit, separately authorized action.

## Contracts

| Surface | Required behavior |
|---|---|
| Certification | strict by default; missing or failing required evidence blocks |
| Package build | real isolated `uv build`; exactly one metadata- and member-safe wheel and sdist |
| Artifact identity | path, media type, size, full SHA-256 and SHA-512 |
| Local distribution | explicit destination, real copy, post-copy verification |
| Remote distribution | dry-run receipt only; execution rejected |
| Report bundle | content PDF, final PDF, HTML, shared metadata, checksums, receipts, inputs |
| Manifest | schema v1, portable paths, source state, producers, roles, hashes, outcomes |
| Remote publication | GitHub and Zenodo-sandbox plan receipts only |

## Publication Bundle

`prepare_publication_bundle()` requires all three rendered report artifacts and
generates `CITATION.cff`, `.zenodo.json`, publication metadata, source-state
receipt, detached manifest, and checksum files. `verify_publication_bundle()`
checks required roles, portability, sizes, both digest algorithms, and the
visible content hash when PDF text extraction is available.

The report compiler writes the unbookended content hash into visible first and
last bookends. The final distribution PDF hash is detached, avoiding a circular
self-reference.

## Failure Behavior

No missing evidence, placeholder file, unsafe archive member, simulated
upload, inferred DOI, or unverified copied artifact may be reported as release
success. Archive paths must be relative and traversal-free; SCM markers,
private environment files, cache directories, and content embedding the active
checkout or user-home path are forbidden.

## Navigation

- [README](README.md)
- [Agent guide](AGENTS.md)
- [PAI integration](PAI.md)
- [Detailed source specification](../../../src/codomyrmex/release/SPEC.md)
