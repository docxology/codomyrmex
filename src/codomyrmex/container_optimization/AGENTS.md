# Container Optimization -- Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The container_optimization module provides Docker image analysis and resource tuning capabilities for AI agents. It enables agents to inspect Docker image structure (layer count, size, base image, security posture), generate actionable optimization suggestions (multi-stage builds, layer consolidation, non-root users), and recommend resource limits (CPU, memory) based on live container usage metrics. Requires a running Docker daemon for all operations.

## Key Files

| File | Class/Function | Role |
|------|----------------|------|
| `__init__.py` | Exports `ContainerOptimizer`, `ResourceTuner` | Module entry point |
| `optimizer.py` | `ContainerOptimizer` | Analyzes Docker images for size, layers, security, and generates optimization reports |
| `optimizer.py` | `ImageAnalysis` (dataclass) | Holds analysis results: size, layers, base image, ports, volumes, env vars, optimization score |
| `optimizer.py` | `OptimizationSuggestion` (dataclass) | A single optimization suggestion with category, impact, effort, and suggested Dockerfile changes |
| `resource_tuner.py` | `ResourceTuner` | Analyzes live container resource usage (CPU, memory) and suggests optimal limits |
| `resource_tuner.py` | `ResourceUsage` (dataclass) | Snapshot of container resource metrics: cpu_percent, memory_usage/limit/percent |

## MCP Tools Available

This module exposes no MCP tools. Agents interact with it by importing `ContainerOptimizer` and `ResourceTuner` directly from `codomyrmex.container_optimization`.

## Agent Instructions

1. **Initialize with Docker client** -- Both `ContainerOptimizer()` and `ResourceTuner()` attempt `docker.from_env()` on construction. If Docker is unavailable, the client is set to `None` and all operations will raise `RuntimeError`. Guard initialization with a try/except or check `optimizer.client is not None` before calling methods.
2. **Analyze images before suggesting optimizations** -- Call `analyze_image(image_name)` to get an `ImageAnalysis` with size, layer count, base image, and an optimization score (0-100). Then call `suggest_optimizations(image_name)` for specific `OptimizationSuggestion` objects.
3. **Use `get_optimization_report()` for complete results** -- Returns a dict with `analysis`, `suggestions`, `score`, and `status` ("needs_improvement" if score < 80, "optimized" otherwise). Suitable for serializing to JSON.
4. **Tune resources from live containers** -- Call `ResourceTuner.analyze_usage(container_id)` to get a `ResourceUsage` snapshot, then `suggest_limits(usage)` for recommended CPU and memory limits with a 20% overhead margin.
5. **Handle `docker.errors.ImageNotFound`** -- `analyze_image()` raises `ValueError` for missing images. `analyze_usage()` raises `ValueError` for missing containers.
6. **Do not pass untrusted image names** -- Image names come from the Docker API; validate externally before passing.

## Operating Contracts

- Both classes require a live Docker daemon. All methods raise `RuntimeError` if the Docker client is `None`.
- `ContainerOptimizer.analyze_image()` raises `ValueError` when the image is not found locally (wraps `docker.errors.ImageNotFound`).
- `ResourceTuner.analyze_usage()` raises `ValueError` when the container ID is not found (wraps `docker.errors.NotFound`).
- Optimization score is calculated as 100 minus deductions: -30 for images > 1GB, -15 for > 500MB, -20 for > 30 layers, -10 for > 15 layers, -10 for root user. Score is clamped to [0, 100].
- `ResourceTuner.suggest_limits()` adds 20% memory overhead and enforces a 64MB minimum. CPU suggestion is 0.5 cores if usage < 10%, otherwise current usage + 0.5.
- All errors are logged via `loguru.logger` before being raised; exceptions are never silently swallowed.
- **Zero-Mock Policy**: Tests must use real Docker environments or `@pytest.mark.skipif` guards when Docker is unavailable. No `unittest.mock` for Docker client operations.
- **No silent fallbacks**: If Docker is unavailable, construction logs a warning but does not return fake data.

## Common Patterns

```python
from codomyrmex.container_optimization import ContainerOptimizer, ResourceTuner

# Analyze a Docker image
optimizer = ContainerOptimizer()
analysis = optimizer.analyze_image("python:3.12-slim")
print(f"Image size: {analysis.size_bytes / (1024*1024):.1f} MB")
print(f"Layers: {analysis.layers_count}")
print(f"Score: {analysis.optimization_score}/100")

# Get optimization suggestions
suggestions = optimizer.suggest_optimizations("python:3.12-slim")
for s in suggestions:
    print(f"[{s.impact}] {s.description}")

# Generate a full report
report = optimizer.get_optimization_report("myapp:latest")
print(report["status"])  # "needs_improvement" or "optimized"
```

```python
# Analyze live container resource usage
tuner = ResourceTuner()
usage = tuner.analyze_usage("container_abc123")
print(f"CPU: {usage.cpu_percent:.1f}%")
print(f"Memory: {usage.memory_usage_bytes / (1024*1024):.0f} MB")

limits = tuner.suggest_limits(usage)
print(f"Suggested CPU: {limits['cpu_limit']}")
print(f"Suggested Memory: {limits['memory_limit']}")
```

## Testing Patterns

```python
import pytest
import docker

DOCKER_AVAILABLE = False
try:
    docker.from_env().ping()
    DOCKER_AVAILABLE = True
except Exception:
    pass

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker daemon not available")
class TestContainerOptimizer:
    def test_analyze_known_image(self):
        from codomyrmex.container_optimization import ContainerOptimizer
        optimizer = ContainerOptimizer()
        analysis = optimizer.analyze_image("python:3.12-slim")
        assert analysis.size_bytes > 0
        assert analysis.layers_count > 0
        assert 0 <= analysis.optimization_score <= 100
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Use |
|-----------|-------------|-------------|
| **Engineer** | Full | Analyze images, tune resource limits, generate optimization reports during BUILD/EXECUTE |
| **Architect** | Design | Review optimization scores and layer architecture during PLAN |
| **QATester** | Validation | Verify image optimization scores meet thresholds during VERIFY |
| **Researcher** | Read-only | Inspect image metadata and resource usage patterns during OBSERVE |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
