# container_optimization — MCP Tool Specification

## Overview

Docker image analysis and resource tuning. Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `container_optimization`. Requires Docker when exercising image/container paths.

## Tool: `container_optimization_analyze`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `image_name` | string | Yes | Image name or ID |

**Returns:** `status`, `image_name`, `size_mb`, `layers_count`, `optimization_score`, `user`, `suggestions`.

## Tool: `container_optimization_report`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `image_name` | string | Yes | Image name or ID |

**Returns:** `status`, `report`.

## Tool: `container_optimization_tune_resources`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `container_id` | string | Yes | Running container ID or name |

**Returns:** `status`, `usage`, `suggested_limits` (per implementation).

## Navigation

- **Parent**: [codomyrmex](../README.md)
- **Project root**: [README.md](../../../README.md)
