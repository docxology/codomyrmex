<!-- agents: curated -->

# Agent guidance for the documentation module mirror

## Purpose

This directory is a reader-facing mirror. Normative behavior and public
signatures live under
[`src/codomyrmex/documentation/`](../../../src/codomyrmex/documentation/).

## Development Guidelines

- Update this mirror when source API, MCP, PAI, security, or behavior changes.
- Do not run the module enricher over this directory during the hand-pass
  freeze; make reviewed targeted edits.
- Keep examples executable and use exact public signatures.
- Distinguish package-local Docusaurus helpers from the canonical MkDocs gate.
- Treat MCP generation as dry-run by default and disclose its PAI-only scope.
- Preserve limitations: heuristic scores and RASP presence do not prove
  correctness.
- Validate links and commands with `make docs-check`.

## Key Files

- [README.md](README.md) — reader entry point
- [API_SPECIFICATION.md](API_SPECIFICATION.md) — public export summary
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) — current MCP tools
- [SPEC.md](SPEC.md) — reader-facing contract
- [SECURITY.md](SECURITY.md) — source-linked threat boundary

## Navigation

- [Human overview](README.md)
- [Source agent guidance](../../../src/codomyrmex/documentation/AGENTS.md)
- [Module index](../AGENTS.md)
- [Repository agent contract](../../../AGENTS.md)
