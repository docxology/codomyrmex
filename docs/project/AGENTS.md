# Codomyrmex Agents — docs/project

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Agent coordination for project-level standards: architecture narratives, contributing workflow, and audit artifacts.

## Contents (by file)

| File | Role |
|:---|:---|
| [contributing.md](contributing.md) | PR process, deps policy, optional local review/SARIF pointers |
| [architecture.md](architecture.md), [architecture-overview.md](architecture-overview.md) | System design |
| [codebase_audit.md](codebase_audit.md), [docs_audit.md](docs_audit.md) | Audit logs |
| [README.md](README.md) | Section index |
| [SPEC.md](SPEC.md), [PAI.md](PAI.md) | Local specs / PAI notes |

## Navigation

- **Parent**: [docs/AGENTS.md](../AGENTS.md), [docs/README.md](../README.md)
- **Project root**: [README.md](../../README.md), [AGENTS.md](../../AGENTS.md)

## Dependencies

- [docs/AGENTS.md](../AGENTS.md) — parent doc hub.
- [src/codomyrmex/](../../src/codomyrmex/) — code referenced by architecture and audit notes.

## Development Guidelines

- Keep [contributing.md](contributing.md) aligned with root [CONTRIBUTING.md](../../CONTRIBUTING.md) when workflow changes.
- After substantive edits, run `uv run python scripts/documentation/validate_agents_structure.py --fail-on-invalid` from repo root.
