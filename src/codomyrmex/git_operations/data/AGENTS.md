# Codomyrmex Agents -- src/codomyrmex/git_operations/data

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Data subdirectory containing static data files used by the git_operations
module. This is NOT a Python module -- it contains no `.py` implementation
files. It holds repository metadata, library catalogs, and auto-generated
reference data.

## Contents

| File | Role |
|------|------|
| `repository_metadata.json` | Structured metadata about the repository (version, module inventory, etc.) |
| `repository_library.txt` | Curated library of repository references |
| `auto_generated_library.txt` | Auto-generated library catalog |
| `docxology_repository_library.txt` | Documentation-oriented repository library |

## Operating Contracts

- Files in this directory are data artifacts, not executable code.
- `repository_metadata.json` is consumed by `git_operations.core.git` and related tooling.
- Data files should be kept in sync with the actual repository structure.
- No Python imports originate from this directory.

## Integration Points

- **Depends on**: Nothing (static data)
- **Used by**: `git_operations` module for metadata lookups

## Navigation

- **Parent**: [git_operations](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
