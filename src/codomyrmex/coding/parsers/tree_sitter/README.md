# Tree-Sitter Module

**Version**: v0.1.0 | **Status**: Active

Code parsing with tree-sitter for syntax analysis and transformations.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Submodules

- **`languages/`** — Language support submodule.
- **`parsers/`** — Tree-sitter parser utilities.
- **`queries/`** — Query building submodule.
- **`transformers/`** — AST transformers submodule.

## Quick Start

```python
from codomyrmex.coding.parsers.tree_sitter import TreeSitterParser, LanguageManager

# Load language
manager = LanguageManager()
manager.load("python")
manager.load("javascript")

# Parse code
parser = TreeSitterParser(language="python")
tree = parser.parse('''
def hello(name):
    return f"Hello, {name}!"
''')

# Query syntax tree
functions = parser.query("(function_definition) @func")
for node in functions:
    print(f"Function: {node.text}")

# Extract structure
classes = parser.query("(class_definition name: (identifier) @name)")
```

## Submodules

| Module | Description |
|--------|-------------|
| `parsers` | Parser implementation |
| `languages` | Language loading and management |
| `queries` | Tree-sitter query patterns |
| `transformers` | AST transformations |

## Exports

| Class | Description |
|-------|-------------|
| `TreeSitterParser` | Parse code to syntax tree |
| `LanguageManager` | Load and manage languages |

## Supported Languages

Python, JavaScript, TypeScript, Go, Rust, C, C++, Java, and more via language packs.

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k tree_sitter -v
```

## Documentation

- [Module Documentation](../../../../../docs/modules/tree_sitter/README.md)
- [Agent Guide](../../../../../docs/modules/tree_sitter/AGENTS.md)
- [Specification](../../../../../docs/modules/tree_sitter/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
