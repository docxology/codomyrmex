<!-- agents: curated -->

# Codomyrmex Agents — docs/agents/core

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Path**: `docs/agents/core`
- **Human overview**: [README.md](README.md)
- **Agent coordination** (repo root): [../../../AGENTS.md](../../../AGENTS.md)

## Purpose

Documentation for **core agent infrastructure** shared across providers: transport, pooling, context, memory hooks, and related primitives under `src/codomyrmex/agents/core/`. Provider-specific docs live under sibling `docs/agents/<provider>/` folders.

## Key Files

- [README.md](README.md)
- Code: [src/codomyrmex/agents/core/](../../../src/codomyrmex/agents/core/)
- Agent index: [docs/agents/AGENTS.md](../AGENTS.md)

## Operating Contracts

- Changes here affect many providers; document breaking changes in [docs/plans/](../../plans/) or module README when behavior shifts.
- Keep MCP and HTTP boundaries explicit when describing shared clients.

## Dependencies

- Shared `codomyrmex` dependencies from `pyproject.toml`; optional provider SDKs consumed by higher layers, not necessarily by `core` alone.

## Development Guidelines

- Follow the root [AGENTS.md](../../../AGENTS.md). Add tests under `src/codomyrmex/tests/unit/agents/core/` (or current layout) for new shared behavior.

## Navigation Links

- **Parent directory**: [agents](../README.md)
- **Project root**: ../../../README.md
