# Search

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Search module provides specialized capabilities for the codomyrmex platform.

## Architecture Overview

```
search/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`cli_commands`**
- **`Document`**
- **`SearchResult`**
- **`Tokenizer`**
- **`SimpleTokenizer`**
- **`FuzzyMatcher`**
- **`QueryParser`**
- **`SearchIndex`**
- **`InMemoryIndex`**
- **`create_index`**
- **`quick_search`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `search_documents` | Safe |
| `search_index_query` | Safe |
| `search_fuzzy` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/search/](../../../../src/codomyrmex/search/)
- **Parent**: [All Modules](../README.md)
