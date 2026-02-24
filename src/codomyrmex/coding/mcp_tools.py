"""MCP tool definitions for the coding module.

Exposes code execution, review, and debugging capabilities as MCP
tools for agent consumption.
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


def _get_execute_code():
    """Lazy import to avoid circular import with coding.__init__."""
    from .execution import execute_code
    return execute_code


def _get_supported_languages():
    """Lazy import to avoid circular import with coding.__init__."""
    from .execution import SUPPORTED_LANGUAGES
    return SUPPORTED_LANGUAGES


@mcp_tool(
    category="coding",
    description="Execute code in a sandboxed environment. Supports Python, JavaScript, and more.",
)
def code_execute(
    language: str, code: str, timeout: int = 30
) -> dict[str, Any]:
    """Execute code and return output."""
    try:
        execute_code = _get_execute_code()
        result = execute_code(language, code, timeout=timeout)
        return {"status": "ok", "result": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="coding",
    description="List all supported programming languages for code execution.",
)
def code_list_languages() -> dict[str, Any]:
    """List supported languages."""
    SUPPORTED_LANGUAGES = _get_supported_languages()
    return {
        "status": "ok",
        "languages": sorted(SUPPORTED_LANGUAGES),
    }


@mcp_tool(
    category="coding",
    description="Analyze a Python file for quality metrics, complexity, and issues.",
)
def code_review_file(path: str) -> dict[str, Any]:
    """Review a file for code quality."""
    try:
        from . import analyze_file

        result = analyze_file(path)
        return {"status": "ok", "analysis": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="coding",
    description="Analyze a project directory for code quality metrics and architecture violations.",
)
def code_review_project(path: str) -> dict[str, Any]:
    """Review an entire project."""
    try:
        from . import analyze_project

        result = analyze_project(path)
        return {"status": "ok", "analysis": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="coding",
    description="Analyze an error and suggest fixes using the Debugger.",
)
def code_debug(
    code: str,
    stdout: str = "",
    stderr: str = "",
    exit_code: int = 1,
) -> dict[str, Any]:
    """Debug code given its output."""
    try:
        from . import Debugger

        debugger = Debugger()
        result = debugger.debug(code, stdout, stderr, exit_code)
        return {"status": "ok", "diagnosis": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
