# Personal AI Infrastructure — Tree Sitter Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Tree Sitter module provides PAI integration for AST parsing and code analysis.

## PAI Capabilities

### Code Parsing

Parse code into ASTs:

```python
from codomyrmex.tree_sitter import Parser

parser = Parser(language="python")
tree = parser.parse(source_code)

for node in tree.root_node.children:
    print(f"{node.type}: {node.text}")
```

### Query Support

Query code patterns:

```python
from codomyrmex.tree_sitter import Query

query = Query("(function_definition name: (identifier) @name)")
matches = query.execute(tree)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Parser` | Parse code |
| `Query` | Pattern matching |
| `Node` | AST navigation |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
