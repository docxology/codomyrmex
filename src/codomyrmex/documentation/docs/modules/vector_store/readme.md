# Vector Store

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Vector Store module provides specialized capabilities for the codomyrmex platform.

## Architecture Overview

```
vector_store/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`SearchResult`**
- **`VectorEntry`**
- **`DistanceMetric`**
- **`normalize_embedding`**
- **`VectorStore`**
- **`InMemoryVectorStore`**
- **`NamespacedVectorStore`**
- **`create_vector_store`**
- **`cli_commands`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `vector_delete` | Safe |
| `vector_count` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/vector_store/](../../../../src/codomyrmex/vector_store/)
- **Parent**: [All Modules](../README.md)
