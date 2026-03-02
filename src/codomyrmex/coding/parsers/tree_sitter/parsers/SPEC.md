# Tree-Sitter Parsers -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Dual-layer parser architecture: a thin wrapper around the C-based tree-sitter library for high-fidelity parsing, plus a regex/heuristic fallback for environments without compiled grammars.

## Architecture

Strategy pattern: `Parser` (ABC) defines the contract (`parse`, `get_functions`, `get_classes`, `get_imports`). Concrete strategies (`PythonParser`, `JavaScriptParser`) use regex for lightweight extraction. `TreeSitterParser` uses the native `tree_sitter.Parser` for full syntax trees.

## Key Classes

### `TreeSitterParser`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `parse` | `source_code: str` | `tree_sitter.Tree` | UTF-8 encode and parse via C API |
| `query` | `tree: Tree, query_str: str` | `list` | Run S-expression query, return captures |

### `PythonParser`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `parse` | `source: str` | `ASTNode` | Build ASTNode tree via regex extraction |
| `get_functions` | `root: ASTNode` | `list[ASTNode]` | Filter children by `function_definition` |
| `get_classes` | `root: ASTNode` | `list[ASTNode]` | Filter children by `class_definition` |
| `get_imports` | `root: ASTNode` | `list[ASTNode]` | Filter `import_statement` and `import_from_statement` |

### Data Types

| Type | Fields | Description |
|------|--------|-------------|
| `NodeType` | Enum (FUNCTION, CLASS, METHOD, ...) | Common AST node types |
| `Position` | `line: int, column: int` | Source location |
| `Range` | `start: Position, end: Position` | Source range with `contains()` and `line_count` |
| `ASTNode` | `type, text, range, children, parent, metadata` | Tree node with `find_children()`, `find_descendants()`, `walk()`, `to_dict()` |

## Dependencies

- **Internal**: none (self-contained data types)
- **External**: `tree_sitter` (optional), `re` (stdlib)

## Constraints

- `TreeSitterParser.parse()` encodes to UTF-8 before parsing.
- Regex parsers detect function/class boundaries by indentation; nested constructs may be approximate.
- Zero-mock: real parsing required; `ValueError` for unsupported languages.

## Error Handling

- `ValueError` raised by `get_parser()` for unknown language strings.
- Tree-sitter load failures logged at ERROR level.
