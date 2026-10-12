# ml_pipeline

**Version**: v1.3.0 | **Status**: Experimental | **Last Updated**: July 2026

## Overview

Lightweight interface for producing pipeline-definition and execution-shaped
receipts. The two functions are Python exports and MCP tools. They are
stateless pass-through adapters—not an ML execution engine. For executable
workflow orchestration, use the `orchestrator` module.

## Key Components

| Component | File | Description |
| :--- | :--- | :--- |
| `ml_pipeline_create` | `mcp_tools.py` | MCP tool: define a pipeline from name + steps |
| `ml_pipeline_execute` | `mcp_tools.py` | MCP tool: execute a pipeline with inputs |

## Quick Start

```python
from codomyrmex.ml_pipeline import ml_pipeline_create, ml_pipeline_execute

result = ml_pipeline_create("my_pipeline", [{"name": "train", "epochs": 3}])
output = ml_pipeline_execute("my_pipeline", {"data": "/path/to/data"})
```

> [!NOTE]
> Both functions return echo responses. No validation, persistence, or ML
> execution occurs.

## MCP Tools

| Tool | Description |
| :--- | :--- |
| `ml_pipeline_create` | Create a pipeline definition |
| `ml_pipeline_execute` | Execute a named pipeline |

## Directory Contents

| File | Purpose |
| :--- | :--- |
| `mcp_tools.py` | MCP tool definitions (2 tools, 34 lines) |
| `__init__.py` | Explicit exports for both MCP-backed functions |

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Documentation**: [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md) | [PAI.md](PAI.md) | [AGENTS.md](AGENTS.md)
- **Related**: [orchestrator](../orchestrator/README.md) | [eval_harness](../eval_harness/README.md)
- **Project Root**: [../../../README.md](../../../README.md)
