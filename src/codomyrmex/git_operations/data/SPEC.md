# Git Operations Data -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Static data directory for the git_operations module. Contains repository
metadata and library catalogs. This is NOT a Python module -- no executable
code is present.

## Contents

| File | Format | Description |
|------|--------|-------------|
| `repository_metadata.json` | JSON | Structured repository metadata (module inventory, version info) |
| `repository_library.txt` | Plain text | Curated repository reference catalog |
| `auto_generated_library.txt` | Plain text | Auto-generated library catalog |
| `docxology_repository_library.txt` | Plain text | Documentation-oriented repository library |

## Architecture

Flat directory of static data files. No Python code, no imports, no module
hierarchy. Files are read by sibling Python modules at runtime.

## Dependencies

- **Internal**: None (consumed by `git_operations.core.git`)
- **External**: None

## Constraints

- `repository_metadata.json` must be valid JSON.
- Text files are UTF-8 encoded.
- No executable code in this directory.
- Files should be kept in sync with actual repository structure.

## Error Handling

- Not applicable (static data files).
