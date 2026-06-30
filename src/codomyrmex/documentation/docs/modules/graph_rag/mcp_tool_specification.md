# MCP_TOOL_SPECIFICATION.md

**Version**: v1.1.9 | **Status**: Draft | **Last Updated**: February 2026

## Module: graph_rag

### Overview

Model Context Protocol tool specifications for the graph_rag module.

### Tools

The following MCP tools are available:

- `graph_rag_search_entities`: Search the knowledge graph for entities matching a query string.
- `graph_rag_get_neighbors`: Get neighboring entities for a given entity ID.
- `graph_rag_get_stats`: Get statistics about the current knowledge graph.

### Tool Schema

Tools follow the standard MCP tool specification format:

```json
{
  "name": "tool_name",
  "description": "Tool description",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```

### Integration

This module integrates with the Codomyrmex Model Context Protocol system defined in `src/codomyrmex/model_context_protocol/`.

## Navigation

- **Parent**: [README.md](README.md)
- **Project Root**: [../../README.md](../../README.md)
