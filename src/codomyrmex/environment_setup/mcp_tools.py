"""MCP tools for the environment_setup module.

Exposes environment validation and dependency checking as
auto-discovered MCP tools. Zero external dependencies beyond the
environment_setup module itself.
"""

from __future__ import annotations

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:

    def mcp_tool(**kwargs):
        def decorator(fn):
            fn._mcp_tool_meta = kwargs
            return fn

        return decorator


@mcp_tool(
    category="environment_setup",
    description=(
        "Check the development environment: Python version validity, "
        "uv availability, and whether running inside a uv-managed "
        "environment. Returns a dict of boolean checks."
    ),
)
def env_check() -> dict:
    """Run environment validation checks.

    Returns:
        Dictionary with keys 'python_valid', 'uv_available',
        'uv_environment' — all booleans.
    """
    from codomyrmex.environment_setup import (
        is_uv_available,
        is_uv_environment,
        validate_python_version,
    )

    return {
        "python_valid": validate_python_version(),
        "uv_available": is_uv_available(),
        "uv_environment": is_uv_environment(),
    }


@mcp_tool(
    category="environment_setup",
    description=(
        "Verify that all required Python dependencies are installed. "
        "Returns the result of the dependency check."
    ),
)
def env_list_deps() -> bool | dict:
    """Check whether required dependencies are installed.

    Returns:
        True if all dependencies are satisfied, or a dict
        with detailed results.
    """
    from codomyrmex.environment_setup import ensure_dependencies_installed

    result = ensure_dependencies_installed()
    if isinstance(result, bool):
        return result
    return {"installed": bool(result), "details": str(result)}
