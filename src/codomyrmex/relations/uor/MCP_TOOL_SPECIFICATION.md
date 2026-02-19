# UOR Submodule — MCP Tool Specification

**Version**: v0.1.7 | **Last Updated**: February 2026

## Overview

MCP tool definitions for the UOR submodule. These tools enable LLM agents to perform PRISM coordinate computation, entity management, and graph traversal.

## Tools

### `uor_compute_triad`

Compute triadic coordinates for a digital value.

```json
{
  "name": "uor_compute_triad",
  "description": "Compute PRISM triadic coordinates (datum, stratum, spectrum) for a value",
  "inputSchema": {
    "type": "object",
    "properties": {
      "value": { "type": "integer", "description": "Integer value to compute coordinates for" },
      "quantum": { "type": "integer", "default": 0, "description": "Quantum level (0=8-bit)" }
    },
    "required": ["value"]
  }
}
```

### `uor_correlate`

Measure structural similarity between two values.

```json
{
  "name": "uor_correlate",
  "description": "Compute Hamming-distance fidelity between two values via PRISM",
  "inputSchema": {
    "type": "object",
    "properties": {
      "a": { "type": "integer", "description": "First value" },
      "b": { "type": "integer", "description": "Second value" },
      "quantum": { "type": "integer", "default": 0 }
    },
    "required": ["a", "b"]
  }
}
```

### `uor_manage_entity`

CRUD operations on UOR entities.

```json
{
  "name": "uor_manage_entity",
  "description": "Create, read, update, or delete a content-addressed UOR entity",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": { "type": "string", "enum": ["create", "get", "remove", "search"] },
      "name": { "type": "string" },
      "entity_type": { "type": "string", "default": "generic" },
      "attributes": { "type": "object" },
      "entity_id": { "type": "string" },
      "query": { "type": "string" }
    },
    "required": ["action"]
  }
}
```

### `uor_find_path`

Find the shortest path between two entities in the UOR graph.

```json
{
  "name": "uor_find_path",
  "description": "BFS shortest path between two entities in the UOR relationship graph",
  "inputSchema": {
    "type": "object",
    "properties": {
      "source_id": { "type": "string" },
      "target_id": { "type": "string" }
    },
    "required": ["source_id", "target_id"]
  }
}
```

## Navigation

- [README](README.md) | [API](API_SPECIFICATION.md) | [Parent](../MCP_TOOL_SPECIFICATION.md)
