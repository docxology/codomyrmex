# Tree-sitter Module — Agent Coordination

## Purpose

Tree-sitter parsing module for Codomyrmex.

## Key Capabilities

- Tree-sitter operations and management

## Agent Usage Patterns

```python
from codomyrmex.tree_sitter import *

# Agent uses tree-sitter capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/tree_sitter/](../../../src/codomyrmex/tree_sitter/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components


### Submodules

- `languages` — Languages
- `parsers` — Parsers
- `queries` — Queries
- `transformers` — Transformers

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k tree_sitter -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
