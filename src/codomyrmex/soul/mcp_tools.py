"""MCP tools for the soul module.

Exposes artificial consciousness, self-reflection, and personality management
as auto-discovered MCP tools. Zero external dependencies beyond the
soul module itself.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="soul",
    description=(
        "Reflect on a query using a specific personality configuration. "
        "Provide 'query' as a string and optionally 'personality' as a string."
    ),
)
def soul_reflect(query: str, personality: str | None = None) -> str:
    """Reflect on a query with a specific personality.

    Args:
        query: The query to reflect upon.
        personality: Optional personality string. Defaults to 'default'.

    Returns:
        The reflection output.
    """
    from codomyrmex.soul.soul import create_soul

    config: dict[str, Any] = {}
    if personality is not None:
        config["personality"] = personality

    soul = create_soul(config)
    try:
        return soul.reflect(query)
    except Exception as e:
        return f"Error: {e}"


@mcp_tool(
    category="soul",
    description=(
        "Get the current personality of a soul instance. "
        "Optionally provide 'personality' as a string to configure the soul."
    ),
)
def soul_get_personality(personality: str | None = None) -> str:
    """Get the personality of the soul.

    Args:
        personality: Optional personality string to configure the soul. Defaults to 'default'.

    Returns:
        The personality string.
    """
    from codomyrmex.soul.soul import create_soul

    config: dict[str, Any] = {}
    if personality is not None:
        config["personality"] = personality

    soul = create_soul(config)
    try:
        return soul.get_personality()
    except Exception as e:
        return f"Error: {e}"
