<!-- agents: curated -->

# Agent guidance for repository scripts

## Purpose

Define execution and maintenance safety for repository automation.

## Development Guidelines

- Run from the repository root unless the script explicitly documents another
  working directory.
- Use `uv run --locked` and the appropriate dependency group.
- Read the nearest nested AGENTS file before editing or executing a script.
- Run GitNexus impact analysis before changing a function or class.
- Prefer explicit check, dry-run, output, and apply modes.
- Make `--help` and missing-mode invocations read-only for maintained mutators.
- Keep output deterministic, repository-relative, and credential-free.
- Preserve curated documentation, existing dirty changes, and submodule
  boundaries.
- Use real temporary repositories and subprocesses in tests.
- Update README, AGENTS, SPEC/PAI/security, Makefile/justfile, and changelog
  parity when a contributor-facing CLI changes.

## Key Files

- [README.md](README.md) — supported script categories and entry points
- [SPEC.md](SPEC.md) — script-surface specification
- `doc_inventory.py` — authoritative volatile metrics
- `src_structure_audit.py` — source/documentation parity
- `rasp_gap_report.py` — README/AGENTS pair audit
- `documentation/` — canonical documentation tooling

## High-risk categories

Treat generation, cleanup, dependency installation, publication, deployment,
Git operations, external messaging, and broad filesystem repair as mutating.
Resolve their exact targets before execution and request new authority when the
operation exceeds the user's stated scope.

## Validation

```bash
uv run --locked ruff check scripts tests
uv run --locked ruff format --check scripts tests
uv run --locked ty check --output-format concise scripts tests
uv run --locked pytest -q <relevant-test-path>
```

For documentation and manuscript scripts, also run `make docs-check` and
`make manuscript-check`.

## Navigation

- [Human overview](README.md)
- [Documentation scripts](documentation/AGENTS.md)
- [Repository agent contract](../AGENTS.md)
- [Repository root](../README.md)
