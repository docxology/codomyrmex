# Specification: container_optimization

## Overview
The `container_optimization` module is designed to provide automated container optimization capabilities within the Codomyrmex ecosystem.

## Components

### `ContainerOptimizer`
- `analyze_image(image_name: str) -> ImageAnalysis`: Performs a deep analysis of a Docker image.
- `suggest_optimizations(image_name: str) -> list[OptimizationSuggestion]`: Generates specific suggestions for improving the image.
- `get_optimization_report(image_name: str) -> dict[str, Any]`: Combines analysis and suggestions into a comprehensive report.

### `ResourceTuner`
- `analyze_usage(container_id: str) -> ResourceUsage`: Monitors and analyzes the CPU and memory usage of a running container.
- `suggest_limits(usage: ResourceUsage) -> dict[str, str]`: Recommends resource limits based on historical usage.

### MCP Tools
The module exposes the following Model Context Protocol (MCP) tools via the `@mcp_tool(category="container_optimization")` decorator in `mcp_tools.py`:
- `container_optimization_analyze_image(image_name: str) -> dict[str, Any]`
- `container_optimization_suggest_optimizations(image_name: str) -> list[dict[str, Any]]`
- `container_optimization_get_optimization_report(image_name: str) -> dict[str, Any]`
- `container_optimization_analyze_usage(container_id: str) -> dict[str, Any]`
- `container_optimization_suggest_limits(container_id: str, cpu_percent: float, memory_usage_bytes: int, memory_limit_bytes: int, memory_percent: float) -> dict[str, str]`

## Data Models
- `ImageAnalysis`: Contains size, layer count, base image, and discovered optimizations.
- `OptimizationSuggestion`: Describes a specific improvement, its impact, and effort.
- `ResourceUsage`: Tracks peak and average resource consumption.

## Requirements
- `docker-py` for interacting with the Docker daemon.
- `loguru` for logging.
- `fire` for the CLI orchestrator.
