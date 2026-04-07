<!-- agents: curated -->

# Codomyrmex Agents — docs/agents/mission_control

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Path**: `docs/agents/mission_control`
- **Human overview**: [README.md](README.md)
- **Agent coordination** (repo root): [../../../AGENTS.md](../../../AGENTS.md)

## Purpose

Documentation for the **Mission Control** agent surface: control-plane UI and API under `src/codomyrmex/agents/mission_control/app/` (Next.js-style app). This `docs/agents/mission_control/` tree holds human-facing notes; the embedded app has its own `AGENTS.md` files per directory.

## Key Files

- [README.md](README.md)
- Package root: [src/codomyrmex/agents/mission_control/](../../../src/codomyrmex/agents/mission_control/)
- Web app: [src/codomyrmex/agents/mission_control/app/](../../../src/codomyrmex/agents/mission_control/app/) (see app-level `AGENTS.md` for fractal docs)

## Operating Contracts

- API and UI behavior is defined in code under `app/`; update this folder when public operator workflows change, not for every component tweak.
- Keep secrets and tenant flows out of committed examples; follow security docs under [docs/security/](../../security/).

## Dependencies

- Node toolchain as required by the Mission Control app (see app `package.json`); Python side via `uv` for Codomyrmex integration.

## Development Guidelines

- Follow the root [AGENTS.md](../../../AGENTS.md). Prefer linking into `app/` AGENTS hubs rather than duplicating long file lists here.

## Navigation Links

- **Parent directory**: [agents](../README.md)
- **Project root**: ../../../README.md
