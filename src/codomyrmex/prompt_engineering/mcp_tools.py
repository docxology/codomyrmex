"""MCP tools for the prompt_engineering module.

Exposes template listing, strategy listing, and prompt evaluation
as auto-discovered MCP tools via the ``@mcp_tool`` decorator.
Zero external dependencies beyond the prompt_engineering module itself.
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
    category="prompt_engineering",
    description=(
        "List all prompt template names in the default registry. "
        "Returns a sorted list of template name strings."
    ),
)
def prompt_list_templates() -> list[str]:
    """Return all registered prompt template names."""
    from codomyrmex.prompt_engineering import list_templates

    return list_templates()


@mcp_tool(
    category="prompt_engineering",
    description=(
        "List available prompt optimization strategy names. "
        "Returns a sorted list of strategy identifier strings."
    ),
)
def prompt_list_strategies() -> list[str]:
    """Return all available optimization strategy identifiers."""
    from codomyrmex.prompt_engineering import list_strategies

    return list_strategies()


@mcp_tool(
    category="prompt_engineering",
    description=(
        "Evaluate a prompt-response pair using default scoring criteria. "
        "Returns a dictionary with per-criterion scores and a weighted total."
    ),
)
def prompt_evaluate(prompt: str, response: str) -> dict:
    """Evaluate a prompt-response pair and return scores.

    Args:
        prompt: The prompt text.
        response: The model response text.

    Returns:
        Dictionary with per-criterion scores and weighted total.
    """
    from codomyrmex.prompt_engineering import quick_evaluate

    return quick_evaluate(prompt, response)
