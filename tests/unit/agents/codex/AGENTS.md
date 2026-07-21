<!-- agents: curated -->

# Codomyrmex Agents — tests/unit/agents/codex

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: June 2026

## Purpose

Unit tests for the Codex agent module and its read-only Codomyrmex access
surfaces.

## Test Boundaries

This directory covers local status/catalog construction only. It must not call
remote Codex APIs, mutate trust state, sync skill repositories, or start
multiagent dispatch.

## Key Files

- `test_access.py` - Codex access status and dispatch catalog tests.

## Operating Contracts

- Keep tests read-only: do not call remote Codex APIs or launch agent dispatch.
- Prefer real Codomyrmex surfaces and bounded filesystem probes.

## Navigation Links

- **Parent directory**: [agents](../README.md)
- **Source module**: [../../../../agents/codex](../../../../agents/codex)

## Related Documents

- **Human overview**: [README.md](README.md)
- **Spec**: [SPEC.md](SPEC.md)
