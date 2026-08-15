# Container Optimization - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `container_optimization` module provides tools for analyzing and improving container images and resource usage. Includes image layer analysis, resource tuning, and optimization recommendations.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `ContainerOptimizer` | Analyzes container images and produces optimization recommendations |
| `ResourceTuner` | Tunes container resource limits (CPU, memory) based on usage patterns |

Both classes provide `close()` and can be used as context managers. They do not create a Docker SDK connection when the Docker CLI cannot reach a daemon; callers receive the existing unavailable-client errors for daemon-dependent operations.

## 3. Usage Example

```python
from codomyrmex.container_optimization import ContainerOptimizer, ResourceTuner

optimizer = ContainerOptimizer()
report = optimizer.get_optimization_report("myapp:latest")

tuner = ResourceTuner()
usage = tuner.analyze_usage("container-id")
limits = tuner.suggest_limits(usage)
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
