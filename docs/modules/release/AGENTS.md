# Codomyrmex Agents — `docs/modules/release`

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Maintain the reader-facing release contract in parity with
`src/codomyrmex/release/`.

## Development Guidelines

- Describe only real behavior: strict evidence, real `uv build`, verified local
  copies, and dry-run remote plans.
- Keep archive-member safety explicit: traversal, absolute paths, SCM markers,
  private environment files, caches, and checkout-specific content fail the
  package build.
- Never call a dry-run receipt a publication.
- Keep manifest v1 fields, public immutable types, and CLI commands aligned
  with the source API specification.
- Represent an unassigned DOI as absent/`null`; do not promise a forthcoming
  identifier.
- Preserve the distinction between internal artifact verification and
  external archival acceptance.
- Update README, SPEC, PAI, source API/MCP documentation, and changelog together
  when public behavior changes.
- Use targeted edits during the active documentation hand-pass; do not run the
  broad bootstrap or enrichment generators.

## Key Files

| File | Contract |
|---|---|
| `README.md` | Reader-facing release and publication workflow |
| `SPEC.md` | Behavioral requirements and fail-closed invariants |
| `PAI.md` | Agent-facing release integration and safety boundary |
| `../../../src/codomyrmex/release/API_SPECIFICATION.md` | Canonical public Python and CLI API |
| `../../../src/codomyrmex/release/MCP_TOOL_SPECIFICATION.md` | Canonical MCP release-tool contract |
| `../../../src/codomyrmex/release/CHANGELOG.md` | Release-module compatibility history |

## Validation

```bash
uv run --locked pytest tests/unit/release -q
uv run --locked mkdocs build --strict
```

## Navigation

- [README](README.md)
- [Specification](SPEC.md)
- [PAI integration](PAI.md)
- [Source module](../../../src/codomyrmex/release/README.md)
