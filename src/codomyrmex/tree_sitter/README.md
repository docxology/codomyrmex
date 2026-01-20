# tree_sitter

Advanced code parsing and analysis module using Tree-sitter.

## Overview

This module provides a standardized interface for parsing source code into Abstract Syntax Trees (ASTs) using Tree-sitter. It supports multi-language parsing and provides utilities for tree traversal and querying.

## Key Features

- **Standardized Parser**: Unified interface for initializing and using Tree-sitter parsers.
- **Language Management**: Robust `LanguageManager` for discovering and loading grammars from shared libraries.
- **AST Traversal**: Helper methods for navigating and searching the syntax tree.
- **S-expression Export**: Support for exporting ASTs to S-expression format.

## Usage

```python
from codomyrmex.tree_sitter import TreeSitterParser

# Initialize parser for Python
parser = TreeSitterParser("python")

# Parse code
tree = parser.parse("def hello(): print('world')")

# Access nodes
root_node = tree.root_node
print(root_node.type)  # module
```

## Navigation Links

- [Functional Specification](SPEC.md)
- [Technical Documentation](AGENTS.md)
