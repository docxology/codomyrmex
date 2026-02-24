"""MCP tool definitions for the containerization module.

Exposes container management operations (Docker, Kubernetes, registry,
security scanning) as MCP tools for agent consumption.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        """Execute Mcp Tool operations natively."""
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func
        return decorator


@mcp_tool(
    category="containerization",
    description="Check availability of container runtimes (Docker, Kubernetes).",
)
def container_runtime_status() -> dict[str, Any]:
    """Report which container runtimes are available."""
    from . import HAS_DOCKER_MANAGER, HAS_K8S, HAS_REGISTRY, HAS_SCANNER, HAS_OPTIMIZER

    return {
        "status": "ok",
        "runtimes": {
            "docker": HAS_DOCKER_MANAGER,
            "kubernetes": HAS_K8S,
            "registry": HAS_REGISTRY,
            "security_scanner": HAS_SCANNER,
            "optimizer": HAS_OPTIMIZER,
        },
    }


@mcp_tool(
    category="containerization",
    description="Build container images using Docker.",
)
def container_build(
    image_name: str,
    dockerfile_path: str = ".",
    tag: str = "latest",
) -> dict[str, Any]:
    """Build a Docker image."""
    try:
        from . import DockerManager

        if DockerManager is None:
            return {"status": "error", "error": "Docker manager not available"}
        mgr = DockerManager()
        result = mgr.build_image(image_name, dockerfile_path, tag=tag)
        return {"status": "ok", "image": f"{image_name}:{tag}", "result": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="containerization",
    description="List running containers managed by Docker.",
)
def container_list() -> dict[str, Any]:
    """List running containers."""
    try:
        from . import DockerManager

        if DockerManager is None:
            return {"status": "error", "error": "Docker manager not available"}
        mgr = DockerManager()
        containers = mgr.list_containers()
        return {"status": "ok", "containers": containers}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="containerization",
    description="Scan a container image for security vulnerabilities.",
)
def container_security_scan(image: str) -> dict[str, Any]:
    """Run security scan on a container image."""
    try:
        from . import ContainerSecurityScanner, HAS_SCANNER

        if not HAS_SCANNER or ContainerSecurityScanner is None:
            return {"status": "error", "error": "Security scanner not available"}
        scanner = ContainerSecurityScanner()
        result = scanner.scan(image)
        return {"status": "ok", "image": image, "scan_result": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
