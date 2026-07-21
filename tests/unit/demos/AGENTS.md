# Codomyrmex — `tests/unit/demos`


**Version**: v0.1.0 | **Status**: Active | **Last Updated**: May 2026

**Status**: Active | **Last updated**: April 2026

## Purpose

Unit tests for `codomyrmex.demos` — registry and public surface checks (zero-mock per parent [SPEC.md](../SPEC.md)).

## Active components

| File | Role |
|------|------|
| `test_registry.py` | Demo registry and registration behavior |

Docs: `README.md`, `SPEC.md`.

## Dependencies

`uv run pytest`. Optional extras: root `pyproject.toml` (`demos` extra if present).

## Navigation

- [README.md](README.md) · [SPEC.md](SPEC.md) · [unit tests parent](../AGENTS.md) · [package source](../../../demos/)
## Maintenance Notes

- Keep this document synchronized with adjacent source files.
- Update sibling README, AGENTS, and SPEC documents together.
- Preserve working examples when changing public behavior.
- Prefer measured validation output over inferred status claims.
- Record any remaining gaps in TODO.md or the nearest planning document.
