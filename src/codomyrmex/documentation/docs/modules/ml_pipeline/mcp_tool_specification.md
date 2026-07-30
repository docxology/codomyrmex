# ml_pipeline — MCP Tool Specification

## Overview

Two stateless, non-actuating receipt tools, auto-discovered from
[`mcp_tools.py`](mcp_tools.py). Neither tool validates, persists, looks up, or
executes a pipeline.

## Tool: `ml_pipeline_create`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `name` | string | Yes | Pipeline name |
| `steps` | array[object] | Yes | Step descriptors |

**Returns:**

```json
{"status": "success", "pipeline": {"name": "<name>", "steps": []}}
```

This is an echo receipt, not a registration record.

## Tool: `ml_pipeline_execute`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `name` | string | Yes | Pipeline name |
| `inputs` | object | Yes | Input payload |

**Returns:**

```json
{"status": "success", "result": {"pipeline": "<name>", "outputs": {}}}
```

`outputs` is the unchanged caller-supplied `inputs` mapping. The success label
describes receipt construction only; it is not evidence that a workload ran.

## Navigation

- **Parent**: [codomyrmex](../README.md)
- **Project root**: [README.md](../../../README.md)
