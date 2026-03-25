# multimodal — MCP Tool Specification

## Overview

Image generation via Google AI SDK. Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `multimodal`.

## Tool: `multimodal_generate_image`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `prompt` | string | — | Required non-empty text prompt |
| `model` | string | `imagen-4.0-generate-001` | Imagen model id |

Requires `GOOGLE_API_KEY` when calling live APIs.

**Returns:** `status`, `images`, `count`.

## Tool: `multimodal_check`

No parameters. Verifies backend import availability.

**Returns:** `status`, `available`, `backend`, optional `message`.

## Navigation

- **Parent**: [codomyrmex](../README.md)
- **Project root**: [README.md](../../../README.md)
