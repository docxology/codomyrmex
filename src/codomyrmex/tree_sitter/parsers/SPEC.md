# Code Parsers -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Wrapper around the tree-sitter `Parser` providing source code parsing into syntax trees and S-expression query execution against parsed ASTs. Handles UTF-8 encoding transparently.

## Architecture

Single class `TreeSitterParser` wrapping the external `tree_sitter.Parser`. Uses `importlib.import_module("tree_sitter")` to avoid namespace collision with the local `codomyrmex.tree_sitter` package.

## Key Classes

### `TreeSitterParser`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `language: Language` | `None` | Create a parser and set its language grammar |
| `parse` | `source_code: str` | `tree_sitter.Tree` | Parse source code into a concrete syntax tree; auto-encodes `str` to UTF-8 bytes |
| `query` | `tree: Tree, query_str: str` | `list` | Execute a tree-sitter S-expression query against the tree's root node; returns list of captured nodes |

### Internal State

| Attribute | Type | Description |
|-----------|------|-------------|
| `parser` | `tree_sitter.Parser` | Underlying tree-sitter parser instance |

## Usage Example

```python
from codomyrmex.tree_sitter.languages.languages import LanguageManager
from codomyrmex.tree_sitter.parsers.parser import TreeSitterParser

LanguageManager.load_language("/path/to/python.so", "python")
lang = LanguageManager.get_language("python")
parser = TreeSitterParser(lang)
tree = parser.parse("def hello(): pass")
captures = parser.query(tree, "(function_definition name: (identifier) @fn)")
```

## Dependencies

- **Internal**: `tree_sitter.languages` (provides `Language` instances for parser initialization)
- **External**: `tree_sitter` (pip package; imported via `importlib`)

## Constraints

- Requires a valid `Language` instance at construction; no lazy language loading.
- String input is auto-encoded to UTF-8; byte input is passed through directly.
- Query syntax follows tree-sitter S-expression format; invalid queries raise tree-sitter exceptions.
- Zero-mock: real parsing only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Parse and query errors propagate as tree-sitter library exceptions; no internal error wrapping.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md)
- Parent: [tree_sitter](../README.md)
