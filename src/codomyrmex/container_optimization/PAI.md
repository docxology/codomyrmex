# Personal AI Infrastructure -- Container Optimization Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Analyzes Docker container images and suggests size/performance optimizations. Provides `ContainerOptimizer` for image analysis and `ResourceTuner` for CPU/memory resource right-sizing.

## PAI Capabilities

### Container Image Optimization

```python
from codomyrmex.container_optimization import ContainerOptimizer, ResourceTuner

optimizer = ContainerOptimizer()
analysis = optimizer.analyze_image("myapp:latest")
suggestions = optimizer.suggest_optimizations(analysis)

tuner = ResourceTuner()
resources = tuner.tune(cpu_usage_history, memory_usage_history)
```

## PAI Phase Mapping

| Phase   | Tool/Class         | Usage                                        |
|---------|--------------------|----------------------------------------------|
| OBSERVE | ContainerOptimizer | Analyze Docker image layers, size, and waste  |
| PLAN    | ContainerOptimizer | Generate optimization suggestions             |
| PLAN    | ResourceTuner      | Recommend CPU/memory resource allocations     |

## Key Exports

| Export             | Type  | Description                              |
|--------------------|-------|------------------------------------------|
| ContainerOptimizer | Class | Image analysis and optimization engine   |
| ResourceTuner      | Class | CPU/memory resource tuning               |

## Integration Notes

- No `mcp_tools.py` -- this module is not auto-discovered via MCP.
- Requires `docker` optional SDK (`uv sync --extra containerization`).
- Pairs with `containerization` module which handles build/run/scan operations.
- Call directly from Python for container optimization workflows.
