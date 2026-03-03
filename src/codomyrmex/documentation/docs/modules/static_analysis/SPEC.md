# static_analysis -- Technical Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Static analysis utilities for auditing Python module exports and imports. Provides `__all__` compliance checking, dead export detection, layer violation scanning, and unified audit reporting via 3 MCP tools.

## Design Principles

- **AST-based**: All analysis uses Python's `ast` module for reliable parsing.
- **Non-destructive**: All operations are read-only.
- **Composable audits**: Individual checks (`audit_exports`, `find_dead_exports`) combine into `full_audit`.

## Architecture

```
static_analysis/
  __init__.py      -- Package root (5 exports)
  exports.py       -- audit_exports, find_dead_exports, full_audit, check_all_defined
  imports.py       -- scan_imports, check_layer_violations, extract_imports_ast
  mcp_tools.py     -- 3 MCP tool definitions
```

## Functional Requirements

### exports.py
- `audit_exports(src_dir: Path) -> list[dict]` -- Find modules missing `__all__` definitions.
- `find_dead_exports(src_dir: Path) -> list[dict]` -- Find `__all__` entries never imported elsewhere.
- `full_audit(src_dir: Path) -> dict` -- Unified report combining all audit checks with `summary` counts.
- `check_all_defined(src_dir: Path) -> bool` -- Check whether `__all__` is properly defined.

### imports.py
- `scan_imports(path: Path) -> list` -- Scan a directory tree for all import statements.
- `check_layer_violations(path: Path) -> list` -- Detect imports that violate the project's layer hierarchy.
- `extract_imports_ast(path: Path) -> list` -- Extract imports from a single file using AST.

## Interface Contracts

MCP tool return formats:
- `static_analysis_audit_exports`: `list[dict]` with `module`, `issue`, `detail` keys
- `static_analysis_find_dead_exports`: `list[dict]` with `module`, `export_name`, `detail` keys
- `static_analysis_full_audit`: `dict` with `missing_all`, `dead_exports`, `unused_functions`, `summary`

## Dependencies

- **Internal**: `model_context_protocol.decorators` for `@mcp_tool`
- **Standard library**: `ast`, `pathlib` (no external dependencies)

## Constraints

- Relies on filesystem access to `src_dir`.
- Layer violation rules are defined within the codebase architecture (Foundation -> Core -> Service -> Application).

## Navigation

- [Root](../../../../../../README.md)
