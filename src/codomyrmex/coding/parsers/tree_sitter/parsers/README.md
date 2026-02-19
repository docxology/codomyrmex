# Parsers

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Tree-sitter inspired parser utilities for source code analysis. Provides regex-based parsers for Python and JavaScript that produce AST node trees with function, class, and import extraction, tree traversal, and source range tracking.

## Key Exports

### Enums

- **`NodeType`** -- Common AST node types: FUNCTION, CLASS, METHOD, VARIABLE, IMPORT, COMMENT, STRING, PARAMETER, RETURN, CALL, ASSIGNMENT, IF, FOR, WHILE, TRY

### Position and Range

- **`Position`** -- Source code position (line, column) with comparison support
- **`Range`** -- Source code range (start, end positions) with `line_count` and `contains()` methods

### AST Nodes

- **`ASTNode`** -- Tree node with type, text, range, children, parent, and metadata; supports:
  - `find_children(type)` -- Direct children of a specific type
  - `find_descendants(type)` -- Recursive descendant search
  - `walk()` -- Pre-order tree traversal iterator
  - `to_dict()` -- Serialization with text truncation

### Parser Base and Implementations

- **`Parser`** -- Abstract base class defining `parse()`, `get_functions()`, `get_classes()`, and `get_imports()` interface
- **`PythonParser`** -- Regex-based Python parser extracting function definitions (with parameters), class definitions (with base classes), and import statements; handles indentation-based block detection
- **`JavaScriptParser`** -- Regex-based JavaScript parser extracting function declarations, arrow functions, class declarations (with extends), and ES module imports

### Factory Functions

- **`get_parser()`** -- Get a parser by language name ("python", "py", "javascript", "js")
- **`parse_file()`** -- Parse a file by path, auto-detecting language from extension (.py, .js, .jsx, .ts, .tsx)

## Directory Contents

- `__init__.py` - All parser classes and factory functions (448 lines)
- `parser.py` - Additional parser utilities
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.coding.parsers.tree_sitter.parsers import PythonParser, parse_file

# Parse Python source
parser = PythonParser()
ast = parser.parse('''
def hello(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"

class Greeter:
    def greet(self):
        pass
''')

functions = parser.get_functions(ast)
print(functions[0].metadata["name"])  # "hello"

classes = parser.get_classes(ast)
print(classes[0].metadata["name"])  # "Greeter"

# Parse a file by path (auto-detects language)
ast = parse_file("/path/to/script.py")
```

## Navigation

- **Parent Module**: [tree_sitter](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
