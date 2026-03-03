"""Meme module MCP tools.

As per MCP_TOOL_SPECIFICATION.md, the Meme module currently exposes no
MCP tools. This file provides the standard interface expected by the
application architecture while returning an empty list.
"""

from typing import Any


def register_tools() -> list[Any]:
    """Register MCP tools for the meme module.

    Returns:
        An empty list, as no tools are currently exposed.

    """
    return []
