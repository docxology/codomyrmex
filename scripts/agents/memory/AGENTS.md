# Codomyrmex Agents — scripts/agents/memory

## Purpose

Maintain the local diagnostic entry point for the agents-memory package.

## Key Files

- [`run_memory.py`](run_memory.py) — bounded import and export probe.
- [`../../../src/codomyrmex/agents/memory/`](../../../src/codomyrmex/agents/memory/) — runtime package.
- [`README.md`](README.md) — usage and scope.

## Dependencies

The script uses the project Python package and its standard CLI logging helpers.
It should not require network credentials or a live service.

## Development Guidelines

- Keep the probe bounded, read-only, and safe to run from a clean checkout.
- Return a nonzero status when the target package cannot be imported.
- Use structured project logging helpers rather than ad hoc output for new work.
- Add a focused script test when behavior changes.

## Navigation

- [README](README.md)
- [Parent guidance](../AGENTS.md)
