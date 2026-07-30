<!-- agents: curated -->

# Agent guidance for package-native documentation scripts

## Purpose

This directory contains a mixture of current validators and legacy mutators.
Do not infer safety from a script name or from the existence of `--help`.

## Development Guidelines

- Inspect the script and its tests before execution.
- Run GitNexus impact analysis before changing a function or class.
- Require read-only help and explicit dry-run/apply behavior for maintained
  mutators.
- Treat broad generation as prohibited during the active README/AGENTS
  hand-pass freeze.
- Preserve curated markers, dirty-worktree changes, and all submodule
  boundaries.
- Keep reports portable: relative paths, deterministic ordering, no credentials
  or absolute home paths.
- Return nonzero for processing failures and blocking validation findings.
- Test with real temporary repositories, byte-for-byte dry-run assertions, and
  subprocess exit codes.

## Key Files

- [README.md](README.md) — script classifications and safe commands
- [SPEC.md](SPEC.md) — maintained CLI contracts
- `triple_check.py` — read-only composed analysis
- `placeholder_check.py` — fail-closed placeholder repair
- `bootstrap_agents_readmes.py` — broad generation boundary

## Maintained commands

```bash
# Read-only validation
uv run --locked python \
  src/codomyrmex/documentation/scripts/triple_check.py \
  --repo-root . --fail-on-issues

# Read-only preview
uv run --locked python \
  -m codomyrmex.documentation.scripts.placeholder_check \
  --repo-root . --dry-run
```

Do not document an apply command as routine maintenance while the freeze is
active.

## Change parity

Changes to a package-native CLI require updates to its tests, this pair,
`docs/development/documentation.md`, the repository tooling guide when exposed
there, and the appropriate API/specification/changelog surfaces.

## Navigation

- [Human overview](README.md)
- [Documentation package](../AGENTS.md)
- [Repository tooling](../../../../scripts/documentation/AGENTS.md)
- [Maintenance guide](../../../../docs/development/documentation.md)
- [Repository agent contract](../../../../AGENTS.md)
