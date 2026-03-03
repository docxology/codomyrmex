# Container Optimization Module

## Purpose
The `container_optimization` module provides tools and utilities to analyze, optimize, and tune container images and resource configurations for Codomyrmex.

## Features
- **ContainerOptimizer**: Analyzes Docker images for size, layer efficiency, and security best practices.
- **ResourceTuner**: Evaluates container resource usage and suggests optimal limits and requests.
- **Dockerfile Improvement**: Suggests automated improvements for Dockerfiles based on optimization best practices.
- **MCP Tools**: Exposes these capabilities as Model Context Protocol (MCP) tools via the `@mcp_tool` decorator.

## Usage
```python
from codomyrmex.container_optimization.optimizer import ContainerOptimizer

optimizer = ContainerOptimizer()
report = optimizer.get_optimization_report("my-image:latest")
print(report)
```

## Zero-Mock Policy
Following the Codomyrmex Zero-Mock Policy, all tests for this module must use real Docker interactions and authentic fixtures instead of mocks.
