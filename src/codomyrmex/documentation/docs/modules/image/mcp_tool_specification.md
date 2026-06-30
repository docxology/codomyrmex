# image — MCP Tool Specification

## Overview

Lightweight image format introspection (local files). Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `image`.

## Tool: `image_detect_format`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `file_path` | string | Yes | Absolute path |

**Returns:** `status`, `format`, `file_path` (or `message` on error).

## Tool: `image_file_info`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `file_path` | string | Yes | Absolute path |

**Returns:** `status`, `file_path`, `exists`, `size_bytes`, `extension`.

## Tool: `image_list_formats`

No parameters. **Returns:** `status`, `formats` (sorted identifiers).

## Navigation

- **Parent**: [codomyrmex](../README.md)
- **Project root**: [README.md](../../../README.md)
