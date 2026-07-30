<!-- readme: curated -->
# Core Git Operations

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

This package contains the command facade, repository-library manager, and
repository-metadata persistence used by `codomyrmex.git_operations`.

Repository metadata is runtime state, not package data. Unless the caller
passes `metadata_file`, `RepositoryMetadataManager` uses:

1. `CODOMYRMEX_REPOSITORY_METADATA_FILE`, when set;
2. `$XDG_STATE_HOME/codomyrmex/git_operations/repository_metadata.json`; or
3. `~/.local/state/codomyrmex/git_operations/repository_metadata.json`.

The parent directory is created only when metadata is saved. Timestamped
backups may be written beside the selected state file. Neither live metadata
nor its backups belong in wheel or sdist artifacts.

## Key Files

| Path | Purpose |
|---|---|
| `git.py` | Compatibility facade for command modules |
| `commands/` | Branch, commit, config, history, merge, remote, repository, stash, status, sync, submodule, and tag operations |
| `repository.py` | Repository library and bulk-operation manager |
| `metadata.py` | Metadata models, persistence, GitHub enrichment, and reports |
| `__init__.py` | Public exports |
| `SPEC.md` | Functional and persistence contracts |
| `PAI.md` | Agent-facing usage boundary |

`repository_metadata.json` and `repository_metadata.json.backup.*` files found
in a checkout are mutable local state. Documentation intentionally does not
inventory individual backup filenames.

## Validation

```bash
uv run --locked pytest tests/unit/git_operations -q
uv run --locked ruff check src/codomyrmex/git_operations tests/unit/git_operations
uv run --locked ty check src/codomyrmex/git_operations
```

## Navigation

- [Parent module](../README.md)
- [Specification](SPEC.md)
- [Agent guide](AGENTS.md)
- [PAI integration](PAI.md)
- [Repository root](../../../../README.md)
