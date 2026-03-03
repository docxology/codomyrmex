# Tree Sitter

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Tree-sitter parsing module for Codomyrmex.

## Architecture Overview

```
tree_sitter/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`TreeSitterParser`**
- **`LanguageManager`**
- **`parsers`**
- **`languages`**
- **`queries`**
- **`transformers`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `parse_code` | Safe |
| `list_languages` | Safe |
| `extract_symbols` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/tree_sitter/](../../../../src/codomyrmex/tree_sitter/)
- **Parent**: [All Modules](../README.md)
