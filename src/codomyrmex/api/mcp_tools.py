"""MCP tools for the api module.

Exposes API documentation generation, specification extraction,
and health-check capabilities as MCP tools.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.tool_decorator import mcp_tool
except ImportError:

    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func

        return decorator


@mcp_tool(
    category="api",
    description="Check the API server status, aggregating health across components.",
)
def api_health_check() -> dict[str, Any]:
    """Check the health and availability of the API module.

    Verifies that core API submodules can be imported and aggregates
    their health via HealthChecker.

    Returns:
        Dictionary with overall health status and component details.
    """
    from codomyrmex.api.health import HealthChecker, ComponentHealth

    checker = HealthChecker()

    def check_submodules() -> ComponentHealth:
        submodules = [
            "documentation",
            "standardization",
            "authentication",
            "rate_limiting",
            "circuit_breaker",
            "webhooks",
            "mocking",
            "pagination",
        ]
        results = {}
        all_ok = True
        for name in submodules:
            try:
                __import__(f"codomyrmex.api.{name}")
                results[name] = "ok"
            except Exception as exc:
                results[name] = f"error: {exc}"
                all_ok = False
        if not all_ok:
            raise Exception(f"Failed to load submodules: {results}")
        return ComponentHealth(name="api_submodules", message="All submodules loaded")

    checker.register("submodules", check_submodules)
    report = checker.check()
    return report.to_dict()


@mcp_tool(
    category="api",
    description="List registered API endpoints discovered from source code.",
)
def api_list_endpoints(
    source_path: str = ".",
) -> dict[str, Any]:
    """List API endpoints discovered from source code.

    Scans the given source path for API endpoint definitions
    using the documentation generator's code analysis.

    Args:
        source_path: Directory or file path to scan for API endpoints.

    Returns:
        Dictionary with discovered endpoints or error information.
    """
    try:
        from codomyrmex.api.documentation.doc_generator import extract_api_specs

        endpoints = extract_api_specs(source_path)
        return {
            "status": "success",
            "endpoint_count": len(endpoints),
            "endpoints": [ep.to_dict() for ep in endpoints],
        }
    except NotImplementedError as exc:
        return {"status": "error", "message": f"not yet implemented: {exc}"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="api",
    description="Retrieve the OpenAPI specification generated from source code.",
)
def api_get_spec(
    title: str = "Codomyrmex API",
    version: str = "1.0.0",
    source_paths: str = "",
    base_url: str = "",
) -> dict[str, Any]:
    """Generate an API specification from source code.

    Produces an APIDocumentation structure by scanning source paths
    for endpoint definitions and assembling them into a specification.

    Args:
        title: Title for the generated API documentation.
        version: API version string.
        source_paths: Comma-separated list of source directories to scan.
        base_url: Base URL for the API.

    Returns:
        Dictionary with the generated API specification or error information.
    """
    try:
        from codomyrmex.api.documentation.doc_generator import generate_api_docs

        paths = [p.strip() for p in source_paths.split(",") if p.strip()] or None
        doc = generate_api_docs(
            title=title,
            version=version,
            source_paths=paths,
            base_url=base_url,
        )
        return {
            "status": "success",
            "spec": doc.to_dict(),
        }
    except NotImplementedError as exc:
        return {"status": "error", "message": f"not yet implemented: {exc}"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
