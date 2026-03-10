"""MCP tools for the api module.

Exposes API documentation generation, specification extraction,
and health-check capabilities as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="api")
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


@mcp_tool(category="api")
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


@mcp_tool(category="api")
def api_health_check() -> dict[str, Any]:
    """Check the health and availability of the API module.

    Verifies that core API submodules (documentation, standardization,
    authentication, rate_limiting, circuit_breaker, webhooks, mocking,
    pagination) can be imported successfully.

    Returns:
        Dictionary with health status per submodule.
    """
    submodules = [
        "documentation",
        "standardization",
        "authentication",
        "rate_limiting",
        "circuit_breaker",
        "webhooks",
        "mocking",
        "pagination",
        "free_apis",
    ]
    results: dict[str, str] = {}
    all_ok = True

    for name in submodules:
        try:
            __import__(f"codomyrmex.api.{name}")
            results[name] = "ok"
        except Exception as exc:
            results[name] = f"error: {exc}"
            all_ok = False

    return {
        "status": "success" if all_ok else "degraded",
        "submodules": results,
        "healthy_count": sum(1 for v in results.values() if v == "ok"),
        "total_count": len(submodules),
    }
