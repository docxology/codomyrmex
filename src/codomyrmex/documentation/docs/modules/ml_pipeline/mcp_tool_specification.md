# ml_pipeline — MCP Tool Specification

## Overview

Named pipeline DAG create/execute. Auto-discovered from [`mcp_tools.py`](mcp_tools.py).

## Tool: `ml_pipeline_create`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `name` | string | Yes | Pipeline name |
| `steps` | array[object] | Yes | Step descriptors |

**Returns:** pipeline registration result dict.

## Tool: `ml_pipeline_execute`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `name` | string | Yes | Pipeline name |
| `inputs` | object | Yes | Input payload |

**Returns:** execution result dict.

## Navigation

- **Parent**: [codomyrmex](../README.md)
- **Project root**: [README.md](../../../README.md)
