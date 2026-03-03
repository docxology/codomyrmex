"""MCP tools for the container_optimization module.

Exposes container image analysis, optimization suggestions, and resource tuning
capabilities as auto-discovered MCP tools.
"""

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="container_optimization",
    description="Analyze a Docker image for optimization opportunities.",
)
def container_optimization_analyze_image(image_name: str) -> dict[str, Any]:
    """Analyze a Docker image for optimization opportunities.

    Args:
        image_name: The name or ID of the Docker image to analyze.

    Returns:
        A dictionary containing the image analysis results.
    """
    from codomyrmex.container_optimization.optimizer import ContainerOptimizer

    optimizer = ContainerOptimizer()
    analysis = optimizer.analyze_image(image_name)
    return analysis.to_dict()


@mcp_tool(
    category="container_optimization",
    description="Generate specific optimization suggestions for a Docker image.",
)
def container_optimization_suggest_optimizations(
    image_name: str,
) -> list[dict[str, Any]]:
    """Generate specific optimization suggestions for a Docker image.

    Args:
        image_name: The name or ID of the Docker image.

    Returns:
        A list of dictionaries containing optimization suggestions.
    """
    from codomyrmex.container_optimization.optimizer import ContainerOptimizer

    optimizer = ContainerOptimizer()
    suggestions = optimizer.suggest_optimizations(image_name)
    return [s.to_dict() for s in suggestions]


@mcp_tool(
    category="container_optimization",
    description="Generate a complete optimization report for a Docker image.",
)
def container_optimization_get_optimization_report(image_name: str) -> dict[str, Any]:
    """Generate a complete optimization report for a Docker image.

    Args:
        image_name: The name or ID of the Docker image.

    Returns:
        A dictionary containing the full optimization report.
    """
    from codomyrmex.container_optimization.optimizer import ContainerOptimizer

    optimizer = ContainerOptimizer()
    return optimizer.get_optimization_report(image_name)


@mcp_tool(
    category="container_optimization",
    description="Analyze resource usage of a running container.",
)
def container_optimization_analyze_usage(container_id: str) -> dict[str, Any]:
    """Analyze resource usage of a running container.

    Args:
        container_id: The ID or name of the running container.

    Returns:
        A dictionary containing the resource usage data.
    """
    from codomyrmex.container_optimization.resource_tuner import ResourceTuner

    tuner = ResourceTuner()
    usage = tuner.analyze_usage(container_id)
    return usage.to_dict()


@mcp_tool(
    category="container_optimization",
    description="Suggest optimal resource limits based on a container's usage.",
)
def container_optimization_suggest_limits(container_id: str) -> dict[str, str]:
    """Suggest optimal resource limits based on a container's usage.

    Args:
        container_id: The ID or name of the running container.

    Returns:
        A dictionary containing the suggested limits (cpu_limit, memory_limit, etc.).
    """
    from codomyrmex.container_optimization.resource_tuner import ResourceTuner

    tuner = ResourceTuner()
    usage = tuner.analyze_usage(container_id)
    return tuner.suggest_limits(usage)
