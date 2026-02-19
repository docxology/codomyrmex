# static_analysis - Functional Specification

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

AST-based static analysis module for import dependency scanning, architectural layer classification, layer-boundary violation detection, and export auditing across the Codomyrmex package.

## Design Principles

- **AST-Only Analysis**: Parses Python source via `ast` module — never imports analyzed code
- **Zero External Dependencies**: Uses only Python stdlib (`ast`, `os`, `pathlib`)
- **Layer-Aware**: Classifies modules into architectural layers matching the package SPEC
- **Non-Destructive**: Read-only analysis; never modifies analyzed files

## Functional Requirements

### Import Scanning

- Walk all `.py` files recursively under a source directory
- Extract `codomyrmex.*` imports using AST (`ImportFrom` and `Import` nodes)
- Skip `__pycache__` directories
- Return structured edges with source module, destination module, file path, and layer info

### Layer Classification

- Map every module to one of four layers: Foundation, Core, Service, Specialized
- Layer sets must match the canonical definitions in `src/codomyrmex/SPEC.md`

### Violation Detection

- Foundation modules must not import Core or Specialized modules
- Core modules must not import Specialized modules
- Return violations with human-readable reason strings

### Export Auditing

- Discover all module directories with `__init__.py`
- Parse `__init__.py` for `__all__` definitions (standard assignment and annotated assignment)
- Report modules missing `__all__`

## Quality Requirements

- **Test Coverage**: ≥80% coverage
- **Type Hints**: All public functions have full type annotations
- **Documentation**: Complete docstrings on all public functions

## Navigation

- **Parent**: [../SPEC.md](../SPEC.md) — Package specification
- **README**: [README.md](README.md) — Module overview
- **AGENTS**: [AGENTS.md](AGENTS.md) — Agent coordination
