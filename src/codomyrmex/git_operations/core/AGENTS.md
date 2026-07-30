<!-- agents: curated -->
# Codomyrmex Agents — `git_operations/core`

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Maintain the Git command facade, repository library, and repository-metadata
persistence without mutating package source or leaking checkout state into
distribution artifacts.

## Development Guidelines

- Keep command execution argument-based and preserve the reject-by-default
  safety behavior documented by the parent module.
- Treat repository metadata as user/runtime state. Honor an explicit
  `metadata_file`, then `CODOMYRMEX_REPOSITORY_METADATA_FILE`, then the XDG
  state path.
- Tests that save metadata must select a `tmp_path` file, directly or through
  the environment override. They must not rewrite files under `src/`.
- Do not enumerate timestamped backup files in README or AGENTS documentation.
- Keep runtime metadata and `*.backup.*` files out of wheel and sdist builds.
- Run GitNexus impact analysis before changing a function, class, or method.
- Keep README, SPEC, PAI, parent API/security documentation, tests, and
  changelog aligned when persistence behavior changes.

## Key Files

| Path | Contract |
|---|---|
| `git.py` | Public compatibility facade |
| `commands/` | Focused Git command implementations |
| `repository.py` | Repository library and bulk workflows |
| `metadata.py` | Metadata path selection, persistence, enrichment, reporting |
| `README.md` | Reader-facing state and validation boundary |
| `SPEC.md` | Functional contracts |
| `PAI.md` | Agent integration |

## Validation

```bash
uv run --locked pytest tests/unit/git_operations -q
uv run --locked ruff check src/codomyrmex/git_operations tests/unit/git_operations
uv run --locked ty check src/codomyrmex/git_operations
```

Before and after the test run, compare the digest of any pre-existing
checkout-local `repository_metadata.json`; the test suite must leave it
unchanged.

## Navigation

- [README](README.md)
- [Specification](SPEC.md)
- [PAI integration](PAI.md)
- [Parent module](../README.md)
- [Repository root](../../../../README.md)
