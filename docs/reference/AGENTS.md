# Codomyrmex Agents — docs/reference

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Agent coordination for `docs/reference/`: API and CLI reference, performance and migration guides, and the authoritative [inventory.md](inventory.md) for repo metrics (top-level modules, `@mcp_tool` count, collected tests).

## Contents (by file)

| File | Role |
|:---|:---|
| [inventory.md](inventory.md) | Single source of truth for counts used across READMEs; refresh with `uv run python scripts/doc_inventory.py` |
| [mcp-tool-spec-coverage.md](mcp-tool-spec-coverage.md) | `MCP_TOOL_SPECIFICATION.md` sibling gaps; refresh list with `uv run python scripts/mcp_spec_gap.py` |
| [api.md](api.md), [api-complete.md](api-complete.md) | API reference |
| [cli.md](cli.md) | CLI surface |
| [changelog.md](changelog.md) | Version history |
| [glossary.md](glossary.md) | Terminology |
| [migration-guide.md](migration-guide.md) | Major-version migrations |
| [orchestrator.md](orchestrator.md) | Orchestrator reference |
| [performance.md](performance.md), [performance-benchmarks.md](performance-benchmarks.md), [performance-optimization.md](performance-optimization.md) | Performance |
| [security.md](security.md) | Security reference |
| [troubleshooting.md](troubleshooting.md) | Common failures |
| [README.md](README.md) | Section index |
| [SPEC.md](SPEC.md), [PAI.md](PAI.md) | Local specs / PAI notes for this tree |

## Operating contracts

- Volatile numbers belong in `inventory.md`, not duplicated in prose without a pointer to refresh steps.
- Cross-link to [docs/development/documentation.md](../development/documentation.md) when adding diagrams or bulk doc changes.

## Navigation

- **Parent**: [docs/AGENTS.md](../AGENTS.md), [docs/README.md](../README.md)
- **Project root**: [README.md](../../README.md), [AGENTS.md](../../AGENTS.md)
