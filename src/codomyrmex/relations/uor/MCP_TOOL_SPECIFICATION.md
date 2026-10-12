# UOR Submodule — MCP Tool Specification

**Version**: v1.1.9 | **Last Updated**: February 2026

## Overview

MCP tool definitions for the UOR submodule, defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`. Both tools share one process-wide `UORGraph` (quantum level 0), so entities persist between calls.

PRISM coordinate computation, correlation, entity search or removal, and relationship creation are available from the Python API (`PrismEngine`, `EntityManager`, `UORGraph`) but are not MCP tools. Because no MCP tool adds relationships, `uor_find_path` only finds paths for relationships created from Python in the same process.

## Tools

### `uor_add_entity`

Create a content-addressed UOR entity in the shared graph.

```json
{
  "name": "uor_add_entity",
  "inputSchema": {
    "type": "object",
    "properties": {
      "name": { "type": "string", "description": "Human-readable entity name" },
      "entity_type": { "type": "string", "description": "Category, e.g. 'agent' or 'document'" },
      "attributes": { "type": "object", "description": "Entity properties (default {})" }
    },
    "required": ["name", "entity_type"]
  }
}
```

Returns `{"status": "success", "entity": {...}}`, where `entity` has `id`, `name`, `entity_type`, `attributes`, `content_hash`, `created_at` and `triadic_coordinates` (`datum`, `stratum`, `spectrum`, `total_stratum`).

### `uor_find_path`

Find the shortest (BFS) path between two entities in the shared graph.

```json
{
  "name": "uor_find_path",
  "inputSchema": {
    "type": "object",
    "properties": {
      "source_id": { "type": "string", "description": "Starting entity ID" },
      "target_id": { "type": "string", "description": "Destination entity ID" }
    },
    "required": ["source_id", "target_id"]
  }
}
```

Returns `{"status": "success", "path": ["<id>", ...]}`, or `{"status": "success", "message": "No path found."}` when the entities are not connected.

Both tools return `{"status": "error", "message": "<description>"}` on failure.

## Navigation

- [README](README.md) | [API](API_SPECIFICATION.md) | [Parent](../MCP_TOOL_SPECIFICATION.md)
