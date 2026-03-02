# Codomyrmex Agents -- src/codomyrmex/coding/parsers

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Top-level parsers package that aggregates code-parsing capabilities. Re-exports the tree-sitter sub-package (`TreeSitterParser`, `LanguageManager`) and exposes sub-modules for languages, queries, and AST transformers.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | _(re-exports)_ | Package initialiser; delegates to `tree_sitter` sub-package |
| `tree_sitter/` | sub-package | Tree-sitter parsing, language loading, query execution |

## Operating Contracts

- Agents must import parsers through this package rather than reaching into sub-modules directly.
- Adding a new parser backend requires a new sub-package under `parsers/` following the same layout as `tree_sitter/`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `tree_sitter` (external), `codomyrmex.logging_monitoring`
- **Used by**: `coding.pattern_matching`, `coding.review`, `coding.static_analysis`

## Navigation

- **Parent**: [coding](../README.md)
- **Root**: [Root](../../../../README.md)
