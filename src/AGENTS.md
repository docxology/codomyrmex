<!-- agents: curated -->

# Agent guidance for the source tree

## Purpose

`src/codomyrmex/` is the installable package. Source changes must preserve
module boundaries, public exports, MCP discovery, typing, tests, and
source-adjacent documentation.

## Development Guidelines

- Read the nearest module `AGENTS.md` before editing.
- Run GitNexus impact analysis before changing any function, class, or method.
- Keep public API changes aligned with `__init__.py`, `API_SPECIFICATION.md`,
  `MCP_TOOL_SPECIFICATION.md`, PAI, security, tests, and changelog surfaces.
- Use centralized logging and typed exceptions for shared runtime behavior.
- Preserve MCP metadata and tool registration when refactoring handlers.
- Use real components and temporary resources in tests; follow the root
  zero-mock policy.
- Do not treat optional dependency discovery as permission to import expensive
  or conflicting native backends.
- Do not run broad source-documentation generators during the active hand-pass
  freeze.
- Keep submodule worktrees outside package-wide formatting or rewriting.

## Key Files

- [README.md](README.md) — source-tree overview
- [SPEC.md](SPEC.md) — source-surface specification
- `codomyrmex/__init__.py` — package exports and metadata
- `codomyrmex/AGENTS.md` — package-level agent guidance

## Validation

Select checks proportionate to the change, then run the package gate before
handoff:

```bash
uv run --locked ruff check src tests
uv run --locked ruff format --check src tests
uv run --locked ty check --output-format concise src tests
uv run --locked pytest -q <relevant-test-path>
make test
```

`make test` enforces the configured 60% coverage floor. Plain pytest is the
faster diagnostic path and does not prove coverage compliance.

## Navigation

- [Source overview](README.md)
- [Package overview](codomyrmex/README.md)
- [Package agent guidance](codomyrmex/AGENTS.md)
- [Repository architecture](../docs/project/architecture.md)
- [Repository agent contract](../AGENTS.md)
