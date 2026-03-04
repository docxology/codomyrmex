"""MCP tool definitions for the container_optimization module.

Exposes Docker image analysis and optimization suggestions as MCP tools.
Requires Docker to be running for full functionality.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_optimizer():
    """Lazy import of ContainerOptimizer."""
    from codomyrmex.container_optimization.optimizer import ContainerOptimizer

    return ContainerOptimizer()


def _get_resource_tuner():
    """Lazy import of ResourceTuner."""
    from codomyrmex.container_optimization.resource_tuner import ResourceTuner

    return ResourceTuner()


@mcp_tool(
    category="container_optimization",
    description="Analyze a Docker image for optimization opportunities including size, layers, and security.",
)
def container_optimization_analyze(
    image_name: str,
) -> dict[str, Any]:
    """Analyze a Docker image and return optimization suggestions.

    Args:
        image_name: Docker image name or ID to analyze.

    Returns:
        dict with keys: status, image_name, size_mb, layers_count, optimization_score, suggestions
    """
    try:
        optimizer = _get_optimizer()
        analysis = optimizer.analyze_image(image_name)
        suggestions = optimizer.suggest_optimizations(image_name)
        return {
            "status": "success",
            "image_name": analysis.image_name,
            "size_mb": analysis.size_bytes / (1024 * 1024),
            "layers_count": analysis.layers_count,
            "optimization_score": analysis.optimization_score,
            "user": analysis.user,
            "suggestions": [s.to_dict() for s in suggestions],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="container_optimization",
    description="Get a complete optimization report for a Docker image with analysis and actionable suggestions.",
)
def container_optimization_report(
    image_name: str,
) -> dict[str, Any]:
    """Generate a complete optimization report for a Docker image.

    Args:
        image_name: Docker image name or ID.

    Returns:
        dict with keys: status, report (containing analysis, suggestions, score)
    """
    try:
        optimizer = _get_optimizer()
        report = optimizer.get_optimization_report(image_name)
        return {
            "status": "success",
            "report": report,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="container_optimization",
    description="Analyze resource usage of a running container and suggest optimal limits.",
)
def container_optimization_tune_resources(
    container_id: str,
) -> dict[str, Any]:
    """Analyze a running container's resource usage and suggest optimal limits.

    Args:
        container_id: Docker container ID or name.

    Returns:
        dict with keys: status, usage, suggested_limits
    """
    try:
        tuner = _get_resource_tuner()
        usage = tuner.analyze_usage(container_id)
        limits = tuner.suggest_limits(usage)
        return {
            "status": "success",
            "usage": usage.to_dict(),
            "suggested_limits": limits,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
