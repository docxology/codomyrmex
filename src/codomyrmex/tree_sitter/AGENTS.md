# Agent Guidelines - Tree-sitter

## Module Overview

Code parsing with tree-sitter for syntax analysis and AST transformations.

## Key Classes

- **TreeSitterParser** — Parse code to syntax tree
- **LanguageManager** — Load and manage language grammars
- **QueryEngine** — Execute tree-sitter queries
- **ASTTransformer** — Transform parsed ASTs

## Agent Instructions

1. **Load languages first** — Call `LanguageManager.load(lang)` before parsing
2. **Use queries for search** — Tree-sitter queries are faster than tree traversal
3. **Cache parsers** — Reuse parser instances for same language
4. **Handle parse errors** — Trees may have ERROR nodes; check `tree.root_node.has_error`
5. **Use node types** — Query by node type (e.g., `function_definition`, `class_definition`)

## Common Queries

```python
# Find all functions
functions = parser.query("(function_definition name: (identifier) @name)")

# Find all classes
classes = parser.query("(class_definition name: (identifier) @name)")

# Find all imports
imports = parser.query("(import_statement) @import")

# Find function calls
calls = parser.query("(call expression: (identifier) @fn)")
```

## Testing Patterns

```python
# Verify parser loads language
manager = LanguageManager()
assert manager.load("python")

# Verify parsing works
parser = TreeSitterParser(language="python")
tree = parser.parse("def foo(): pass")
assert not tree.root_node.has_error

# Verify query results
results = parser.query("(function_definition) @fn")
assert len(results) == 1
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
