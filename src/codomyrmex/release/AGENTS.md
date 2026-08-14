# Codomyrmex Agents — `src/codomyrmex/release`

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Maintain the fail-closed package and technical-report release boundary. The
module may build and verify local artifacts and generate non-mutating remote
plans; it must not silently upload, reserve a DOI, or report unexecuted work as
published.

## Operating Contracts

- Keep `README.md`, `SPEC.md`, `API_SPECIFICATION.md`,
  `MCP_TOOL_SPECIFICATION.md`, `PAI.md`, and the `docs/modules/release/` mirror
  synchronized with public behavior.
- Keep `ReleasePolicy(strict=True)` fail closed across testing, coverage,
  typing, security, documentation, and artifact evidence.
- Build with real `uv build` output. Validate metadata and archive-member
  safety inside both the wheel and sdist, and retain complete SHA-256 and
  SHA-512 values. SCM markers, private environment files, traversal, and
  absolute member paths or checkout-specific content must fail closed before
  artifacts are copied.
- Treat `BuildArtifact.path` as a local build receipt only. Publication
  manifests must contain portable relative paths and no home-directory paths.
- For `DistributionManager`, remote targets must remain dry-run-only. Local
  distribution must require an explicit destination and verify copied files.
- For report publication, require content PDF, distribution PDF, and semantic
  HTML before preparing a bundle. Never insert the final PDF digest into the
  PDF itself.
- Preserve shared metadata: generate citation and Zenodo metadata from
  `PublicationMetadata`; do not maintain independent hard-coded identities.
- Use real temporary projects and files in tests; follow the repository
  zero-mock policy.

## Key Files

| File | Contract |
|---|---|
| `release_validator.py` | `ReleasePolicy`, evidence checks, certification |
| `package_builder.py` | real isolated wheel/sdist build and inspection |
| `distribution.py` | verified local copy; remote dry-run receipts |
| `publication.py` | immutable publication records, manifest v1, verification, plans |
| `test_evidence.py` | source-bound pytest/JUnit/warning receipt and release gate |
| `__main__.py` | `publication prepare`, `verify`, and `plan` |
| `mcp_tools.py` | Diagnostic release validation/build/report tools; MCP scalar evidence never certifies a release |

## Validation

```bash
uv run --locked pytest tests/unit/release -q
uv run --locked ruff check src/codomyrmex/release tests/unit/release
uv run --locked ty check src/codomyrmex/release
uv run --locked python -m build --help >/dev/null
```

The package builder itself uses `uv build`; the final repository gate must also
perform a real root build and a clean-install public-API smoke test.

## Navigation

- [README](README.md)
- [Specification](SPEC.md)
- [API specification](API_SPECIFICATION.md)
- [MCP specification](MCP_TOOL_SPECIFICATION.md)
- [PAI integration](PAI.md)
- [Changelog](CHANGELOG.md)
