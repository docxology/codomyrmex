# ml_pipeline

**Version**: v1.2.3 | **Status**: Stub | **Last Updated**: March 2026

## Overview

Lightweight interface for defining and executing machine learning pipelines. Currently implemented as a stub with two MCP tools. For production workflow orchestration, use the `orchestrator` module.

## Key Components

| Component | File | Description |
| :--- | :--- | :--- |
| `ml_pipeline_create` | `mcp_tools.py` | MCP tool: define a pipeline from name + steps |
| `ml_pipeline_execute` | `mcp_tools.py` | MCP tool: execute a pipeline with inputs |

## Quick Start

```python
from codomyrmex.ml_pipeline.mcp_tools import ml_pipeline_create, ml_pipeline_execute

result = ml_pipeline_create("my_pipeline", [{"name": "train", "epochs": 3}])
output = ml_pipeline_execute("my_pipeline", {"data": "/path/to/data"})
```

> [!NOTE]
> Both tools are currently stubs that return echo responses. No actual ML execution occurs.

## MCP Tools

| Tool | Description |
| :--- | :--- |
| `ml_pipeline_create` | Create a pipeline definition |
| `ml_pipeline_execute` | Execute a named pipeline |

## Directory Contents

| File | Purpose |
| :--- | :--- |
| `mcp_tools.py` | MCP tool definitions (2 tools, 34 lines) |
| `__init__.py` | Module marker (no public exports) |

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Documentation**: [SPEC.md](../../../../../../docs/modules/ml_pipeline/SPEC.md) | [API_SPECIFICATION.md](../../../../../../src/codomyrmex/ml_pipeline/API_SPECIFICATION.md) | [PAI.md](../../../../../../src/codomyrmex/ml_pipeline/PAI.md) | [AGENTS.md](../../../../../../docs/modules/ml_pipeline/AGENTS.md)
- **Related**: [orchestrator](../orchestrator/README.md) | [eval_harness](../eval_harness/README.md)
- **Project Root**: [../../../README.md](../../../README.md)
