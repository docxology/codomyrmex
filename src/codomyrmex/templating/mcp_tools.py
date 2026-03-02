"""MCP tools for the templating module.

Exposes template rendering and syntax validation via Jinja2.
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
    category="templating",
    description=(
        "Render a Jinja2 template string with a context dict. "
        "Returns the rendered output string."
    ),
)
def template_render(template_string: str, context: dict | None = None) -> str:
    """Render a template with the given context."""
    from codomyrmex.templating import render

    return render(template_string, context or {})


@mcp_tool(
    category="templating",
    description=(
        "Validate that a Jinja2 template string is syntactically correct. "
        "Returns {valid: bool, error: str | null}."
    ),
)
def template_validate(template_string: str) -> dict:
    """Check template syntax without rendering."""
    try:
        try:
            from jinja2 import Environment

            Environment().parse(template_string)
        except ImportError:
            # Fallback: render with empty context to catch syntax errors
            from codomyrmex.templating import render

            render(template_string, {})
        return {"valid": True, "error": None}
    except Exception as exc:
        return {"valid": False, "error": str(exc)}
