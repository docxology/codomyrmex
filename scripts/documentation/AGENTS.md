<!-- agents: curated -->

# Agent guidance for repository documentation tooling

## Purpose

This directory owns repository-level documentation validation and maintenance
entry points. Read [README.md](README.md) for the supported command surface.

## Development Guidelines

- Run commands from the repository root with `uv run --locked`.
- Treat `make docs-check` as the authoritative validation composition.
- Keep audits read-only apart from portable receipts and build output.
- Require explicit mutation modes for repair or generation commands.
- During the hand-pass freeze, never run broad bootstrap, enrichment,
  placeholder-repair, or missing-file generation in apply mode.
- Preserve curated markers and existing dirty-worktree changes.
- Keep submodules, vendor trees, caches, generated documentation, and build
  output outside first-party rewrite scope.
- Add zero-mock tests for parsing, path resolution, exit status, report
  portability, and fail-closed behavior.
- Update this README, the maintenance guide, Makefile/justfile parity, relevant
  specifications, and the changelog when a public CLI changes.

## Key Files

- [README.md](README.md) — supported tools and safe workflows
- [SPEC.md](SPEC.md) — repository tooling contracts
- `audit_readme_agents.py` — package-wide pair and path audit
- `enrich_module_docs.py` — fail-closed module mirror generation
- `mkdocs_hooks.py` — build-view link rewriting
- `validate_links_comprehensive.py` — repository link audit

## Required safety checks

Before editing a function or class, run GitNexus upstream impact analysis and
report the blast radius. Before handoff, run change detection against `main`.

For a new or changed mutating command, verify:

1. `--help` performs no repository writes;
2. no mode means no writes, preferably an argparse error;
3. dry-run bytes remain unchanged;
4. apply scope is explicit and bounded;
5. curated files and submodules remain protected;
6. failures return nonzero and identify affected paths.

## Validation

```bash
uv run --locked ruff check scripts/documentation tests/unit/documentation
uv run --locked pytest -q tests/unit/documentation
uv run --locked python scripts/documentation/audit_readme_agents.py \
  --repo-root . --strict
make docs-check
```

Use narrower tests during development, then the package gate before handoff.

## Navigation

- [Human overview](README.md)
- [Documentation maintenance guide](../../docs/development/documentation.md)
- [Hand-pass tracker](../../docs/plans/readme_agents_hand_pass.md)
- [Parent scripts](../README.md)
- [Repository agent contract](../../AGENTS.md)
