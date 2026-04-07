<!-- agents: curated -->

# Codomyrmex Agents — docs/agents/infrastructure

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Path**: `docs/agents/infrastructure`
- **Human overview**: [README.md](README.md)
- **Agent coordination** (repo root): [../../../AGENTS.md](../../../AGENTS.md)

## Purpose

Documentation for **agent infrastructure** modules: shared services, deployment helpers, and cross-cutting utilities under `src/codomyrmex/agents/infrastructure/`. Distinct from `agents/core/` (primitives) and individual provider packages.

## Key Files

- [README.md](README.md)
- Code: [src/codomyrmex/agents/infrastructure/](../../../src/codomyrmex/agents/infrastructure/)
- Related: [docs/agents/core/AGENTS.md](../core/AGENTS.md), [docs/integration/](../../integration/)

## Operating Contracts

- Infra code often touches credentials and external services; document required env vars beside features and link [docs/security/](../../security/) for handling secrets.
- Prefer thin wrappers over duplicating orchestrator logic already in `src/codomyrmex/orchestrator/`.

## Dependencies

- Cloud and CI targets as each submodule requires; see individual Python modules for imports.

## Development Guidelines

- Follow the root [AGENTS.md](../../../AGENTS.md). Integration tests beat mocks for infra paths when feasible (project zero-mock policy).

## Navigation Links

- **Parent directory**: [agents](../README.md)
- **Project root**: ../../../README.md
