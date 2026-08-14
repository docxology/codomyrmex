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
suggestions = optimizer.suggest_optimizations("myapp:latest")

tuner = ResourceTuner()
usage = tuner.analyze_usage("container-id")
resources = tuner.suggest_limits(usage)
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

- `mcp_tools.py` exposes image analysis, optimization reports, and resource tuning through MCP.
- Requires `docker` optional SDK (`uv sync --extra containerization`).
- A reachable Docker daemon is required for live image/container operations; constructors fail closed without opening a persistent SDK socket.
- Pairs with the `containerization` module, which handles build/run/scan operations.
- Call directly from Python for container optimization workflows.
