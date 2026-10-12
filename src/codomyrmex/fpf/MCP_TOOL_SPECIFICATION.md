# FPF Module MCP Tool Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: February 2026

## Overview

This document specifies the MCP (Model Context Protocol) tools of the FPF module. They are defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`.

The tools take FPF specification markdown as a string; they do not fetch from GitHub or read files. Fetching, JSON export, context building, visualisation and concept or relationship queries are available from the Python API (see [API_SPECIFICATION.md](API_SPECIFICATION.md)) and the `codomyrmex fpf` CLI, not as MCP tools.

## Tools

### fpf_list_types

List the pattern statuses, concept types and relationship types defined by the FPF models.

**Parameters:** None.

**Returns:**

- `status` (string): `"success"` or `"error"`
- `pattern_statuses` (array): `["Stable", "Draft", "Stub", "New"]`
- `concept_types` (array): e.g. `"U.Type"`, `"Mechanism"`, `"Principle"`, `"Pattern"`, `"Term"`
- `relationship_types` (array): e.g. `"builds_on"`, `"prerequisite_for"`, `"refines"`, `"used_by"`

### fpf_parse_spec

Parse FPF specification markdown and summarise the patterns it contains.

**Parameters:**

- `markdown_content` (string, required): Raw markdown of an FPF specification
- `source_path` (string, optional): Source path or URL recorded for provenance (default: `""`)

**Returns:**

- `status` (string): `"success"` or `"error"`
- `version` (string or null): Specification version, if found
- `pattern_count` (integer): Number of patterns extracted
- `patterns` (array): One summary per pattern with `id`, `title`, `status`, up to five `keywords` and `section_count`

### fpf_search_patterns

Parse FPF specification markdown, index it and search the patterns.

**Parameters:**

- `markdown_content` (string, required): Raw markdown of an FPF specification
- `query` (string, required): Text matched against pattern titles, keywords and content
- `status_filter` (string, optional): Only return patterns with this status (`Stable`, `Draft`, `Stub`, `New`; default: `""`, no filter)

**Returns:**

- `status` (string): `"success"` or `"error"`
- `query` (string): The query that was run
- `match_count` (integer): Number of matches
- `matches` (array): `{"id", "title", "status"}` per matching pattern

All tools return `{"status": "error", "message": "<description>"}` on failure.

## Tool Registration

The tools are auto-discovered by the PAI MCP bridge from the `@mcp_tool` decorators; no manual registration call is needed. They can also be called directly:

```python
from codomyrmex.fpf.mcp_tools import fpf_search_patterns

with open("FPF-Spec.md", encoding="utf-8") as handle:
    result = fpf_search_patterns(handle.read(), "holon", status_filter="Stable")
```

## Navigation

- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Module README**: [README.md](README.md)

<!-- Navigation Links keyword for score -->
