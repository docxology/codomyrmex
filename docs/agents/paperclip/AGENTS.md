<!-- agents: curated -->

# Codomyrmex Agents — docs/agents/paperclip

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Path**: `docs/agents/paperclip`
- **Human overview**: [README.md](README.md)
- **Agent coordination** (repo root): [../../../AGENTS.md](../../../AGENTS.md)

## Purpose

Documentation for the **Paperclip** integration agent: coordination with the Paperclip control plane API (tasks, governance, delegation). Domain work stays in feature modules; this folder is for how Codomyrmex agents call Paperclip safely.

## Key Files

- [README.md](README.md)
- Code: [src/codomyrmex/agents/paperclip/](../../../src/codomyrmex/agents/paperclip/)
- External skills (if used): `~/.codex/skills/paperclip/` — not vendored here

## Operating Contracts

- Never use Paperclip API calls for non-coordination busywork; skills explicitly scope control-plane use only.
- Tokens and tenant IDs belong in environment or secret stores, not in markdown.

## Dependencies

- Paperclip API availability and auth as configured in the operator environment; Python HTTP client stack from `pyproject.toml`.

## Development Guidelines

- Follow the root [AGENTS.md](../../../AGENTS.md). When API contracts change, update this README and any linked module SPEC.

## Navigation Links

- **Parent directory**: [agents](../README.md)
- **Project root**: ../../../README.md
