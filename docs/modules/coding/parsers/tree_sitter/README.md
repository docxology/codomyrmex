# Tree-Sitter Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Tree-sitter module provides high-fidelity source code parsing across multiple programming languages. It wraps the tree-sitter parsing library to enable advanced static analysis, code transformation, and intelligent auditing within the Codomyrmex ecosystem. The module is organized into four submodules covering parsing, language management, query building, and AST transformations.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **Multi-Language Parsing**: Parse source code from any language supported by tree-sitter into concrete syntax trees
- **Language Management**: Load, discover, and manage tree-sitter language grammars from shared libraries (.so, .dylib, .dll)
- **Syntax Tree Querying**: Execute tree-sitter query patterns against parsed syntax trees to capture specific nodes
- **AST Transformation**: Visitor and transformation patterns for modifying parsed syntax trees (early development)
- **Auto-Discovery**: Automatically discover and load language grammars from a directory of shared libraries


## Key Components

### Parsers (`parsers/`)

| Component | Description |
|-----------|-------------|
| `TreeSitterParser` | Core parser wrapper that takes a language instance and provides `parse()` for source code to syntax tree conversion and `query()` for executing tree-sitter query patterns against a tree |

### Languages (`languages/`)

| Component | Description |
|-----------|-------------|
| `LanguageManager` | Class-level manager for loading, storing, and discovering tree-sitter language grammars. Supports `load_language()`, `get_language()`, and `discover_languages()` for batch loading from a directory |

### Queries (`queries/`)

| Component | Description |
|-----------|-------------|
| `queries` | AST query pattern submodule (early development, exports pending) |

### Transformers (`transformers/`)

| Component | Description |
|-----------|-------------|
| `transformers` | AST transformation and visitor submodule (early development, exports pending) |

## Quick Start

```python
from codomyrmex.tree_sitter import TreeSitterParser, LanguageManager

# Load a language grammar from a shared library
LanguageManager.load_language("/path/to/tree-sitter-python.so", "python")

# Get the loaded language
python_lang = LanguageManager.get_language("python")

# Parse source code
parser = TreeSitterParser(python_lang)
tree = parser.parse("def hello(): pass")

# Query the syntax tree
captures = parser.query(tree, "(function_definition name: (identifier) @func_name)")

# Auto-discover all languages in a directory
LanguageManager.discover_languages("/path/to/grammars/")
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k tree_sitter -v
```

## Related Modules

- [static_analysis](../static_analysis/) - Code quality and security scanning that can leverage tree-sitter parsing
- [pattern_matching](../pattern_matching/) - Code pattern recognition built on syntax-aware parsing
- [coding](../coding/) - Code execution and review workflows

## Navigation

- **Source**: [src/codomyrmex/tree_sitter/](../../../src/codomyrmex/tree_sitter/)
- **Parent**: [docs/modules/](../README.md)
