# FPF Module MCP Tool Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

This document specifies MCP (Model Context Protocol) tools for AI integration with the FPF module. These tools allow AI agents to interact with FPF specifications programmatically.

## Tools

### fpf_fetch_spec

Fetch the latest FPF specification from GitHub.

**Parameters:**
- `repo` (string, optional): GitHub repository in format "owner/repo" (default: "ailev/FPF")
- `branch` (string, optional): Branch name (default: "main")
- `output_path` (string, optional): Path to save the fetched file

**Returns:**
- `content` (string): The fetched specification content
- `path` (string): Path where content was saved (if output_path provided)

### fpf_parse_spec

Parse a local FPF specification file.

**Parameters:**
- `file_path` (string, required): Path to FPF-Spec.md file
- `extract_concepts` (boolean, optional): Whether to extract concepts (default: true)
- `extract_relationships` (boolean, optional): Whether to extract relationships (default: true)

**Returns:**
- `spec` (object): Parsed FPFSpec object with patterns, concepts, relationships
- `pattern_count` (integer): Number of patterns extracted
- `concept_count` (integer): Number of concepts extracted
- `relationship_count` (integer): Number of relationships extracted

### fpf_search_patterns

Search for patterns in a parsed FPF specification.

**Parameters:**
- `query` (string, required): Search query
- `file_path` (string, optional): Path to FPF-Spec.md (if not already parsed)
- `filters` (object, optional): Filter object with:
  - `status` (string, optional): Filter by status (Stable, Draft, Stub, New)
  - `part` (string, optional): Filter by part (A, B, C, etc.)

**Returns:**
- `results` (array): List of matching Pattern objects
- `count` (integer): Number of results

### fpf_get_pattern

Get a specific pattern by ID.

**Parameters:**
- `pattern_id` (string, required): Pattern identifier (e.g., "A.1")
- `file_path` (string, optional): Path to FPF-Spec.md (if not already parsed)
- `include_related` (boolean, optional): Include related patterns (default: false)
- `depth` (integer, optional): Relationship depth (default: 1)

**Returns:**
- `pattern` (object): Pattern object
- `related` (array, optional): Related patterns if include_related is true

### fpf_export_json

Export FPF specification to JSON.

**Parameters:**
- `file_path` (string, required): Path to FPF-Spec.md
- `output_path` (string, required): Path to output JSON file
- `format` (string, optional): Export format (default: "json", only "json" supported)

**Returns:**
- `output_path` (string): Path to exported file
- `size` (integer): File size in bytes

### fpf_build_context

Build context string for prompt engineering.

**Parameters:**
- `file_path` (string, required): Path to FPF-Spec.md
- `pattern_id` (string, optional): Pattern ID to build context for
- `concept` (string, optional): Concept name to build context for
- `filters` (object, optional): Filters for context building
- `depth` (integer, optional): Relationship depth (default: 1)
- `output_path` (string, optional): Path to save context

**Returns:**
- `context` (string): Context string
- `output_path` (string, optional): Path where context was saved

### fpf_visualize

Generate visualization of FPF patterns.

**Parameters:**
- `file_path` (string, required): Path to FPF-Spec.md
- `type` (string, required): Visualization type ("hierarchy" or "dependencies")
- `output_path` (string, optional): Path to save visualization

**Returns:**
- `diagram` (string): Mermaid diagram string
- `output_path` (string, optional): Path where diagram was saved

### fpf_get_concepts

Get all concepts from a parsed specification.

**Parameters:**
- `file_path` (string, optional): Path to FPF-Spec.md (if not already parsed)
- `pattern_id` (string, optional): Filter by pattern ID
- `concept_type` (string, optional): Filter by concept type

**Returns:**
- `concepts` (array): List of Concept objects
- `count` (integer): Number of concepts

### fpf_get_relationships

Get relationships for a pattern or all relationships.

**Parameters:**
- `file_path` (string, optional): Path to FPF-Spec.md (if not already parsed)
- `pattern_id` (string, optional): Get relationships for specific pattern
- `relationship_type` (string, optional): Filter by relationship type

**Returns:**
- `relationships` (array): List of Relationship objects
- `count` (integer): Number of relationships

## Tool Registration

These tools should be registered with the MCP server using the standard MCP tool registration format. Each tool should include:
- Name
- Description
- Input schema (JSON Schema)
- Output schema (JSON Schema)

## Usage Example

```python
# Register tools
mcp_server.register_tool("fpf_search_patterns", {
    "name": "fpf_search_patterns",
    "description": "Search for patterns in FPF specification",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "file_path": {"type": "string"},
            "filters": {"type": "object"}
        },
        "required": ["query"]
    }
})

# Use tool
result = mcp_server.call_tool("fpf_search_patterns", {
    "query": "holon",
    "filters": {"status": "Stable"}
})
```

## Navigation

- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Module README**: [README.md](README.md)



<!-- Navigation Links keyword for score -->

