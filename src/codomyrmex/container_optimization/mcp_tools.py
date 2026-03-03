"""MCP tools for the Container Optimization module.

This module exposes core container optimization and resource tuning
capabilities as Model Context Protocol (MCP) tools.
"""

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.container_optimization.optimizer import ContainerOptimizer
from codomyrmex.container_optimization.resource_tuner import ResourceTuner, ResourceUsage


@mcp_tool(category="container_optimization")
def container_optimization_analyze_image(image_name: str) -> dict[str, Any]:
    """Analyze a Docker image for optimization opportunities.

    Args:
        image_name: The name or ID of the Docker image to analyze.

    Returns:
        dict: Analysis results including size, layers, and configuration.
    """
    optimizer = ContainerOptimizer()
    analysis = optimizer.analyze_image(image_name)
    return analysis.to_dict()


@mcp_tool(category="container_optimization")
def container_optimization_suggest_optimizations(image_name: str) -> list[dict[str, Any]]:
    """Generate specific optimization suggestions for a Docker image.

    Args:
        image_name: The name or ID of the Docker image.

    Returns:
        list[dict]: List of specific optimization suggestions.
    """
    optimizer = ContainerOptimizer()
    suggestions = optimizer.suggest_optimizations(image_name)
    return [s.to_dict() for s in suggestions]


@mcp_tool(category="container_optimization")
def container_optimization_get_optimization_report(image_name: str) -> dict[str, Any]:
    """Generate a complete optimization report for a Docker image.

    Args:
        image_name: The name or ID of the Docker image.

    Returns:
        dict: A comprehensive report including analysis, suggestions, and score.
    """
    optimizer = ContainerOptimizer()
    return optimizer.get_optimization_report(image_name)


@mcp_tool(category="container_optimization")
def container_optimization_analyze_usage(container_id: str) -> dict[str, Any]:
    """Analyze the current resource usage of a running container.

    Args:
        container_id: The ID or name of the running container.

    Returns:
        dict: Current resource usage metrics.
    """
    tuner = ResourceTuner()
    usage = tuner.analyze_usage(container_id)
    return usage.to_dict()


@mcp_tool(category="container_optimization")
def container_optimization_suggest_limits(
    container_id: str,
    cpu_percent: float,
    memory_usage_bytes: int,
    memory_limit_bytes: int,
    memory_percent: float
) -> dict[str, str]:
    """Suggest optimal resource limits based on provided usage data.

    Args:
        container_id: The ID or name of the container.
        cpu_percent: Current CPU usage percentage.
        memory_usage_bytes: Current memory usage in bytes.
        memory_limit_bytes: Current memory limit in bytes.
        memory_percent: Current memory usage percentage.

    Returns:
        dict: Suggested CPU and memory limits.
    """
    usage = ResourceUsage(
        container_id=container_id,
        cpu_percent=cpu_percent,
        memory_usage_bytes=memory_usage_bytes,
        memory_limit_bytes=memory_limit_bytes,
        memory_percent=memory_percent
    )
    tuner = ResourceTuner()
    return tuner.suggest_limits(usage)
