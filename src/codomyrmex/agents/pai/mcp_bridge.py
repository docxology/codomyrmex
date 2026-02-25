"""PAI <-> Codomyrmex MCP Bridge.

Registers every Codomyrmex capability as MCP tools, resources, and prompts
so that PAI agents can access the full module ecosystem via MCP protocol
or direct Python calls.
"""

from .mcp.definitions import (
    _PROMPT_DEFINITIONS,
    _RESOURCE_DEFINITIONS,
    _TOOL_DEFINITIONS,
)
from .mcp.discovery import invalidate_tool_cache
from .mcp.server import (
    call_tool,
    create_codomyrmex_mcp_server,
    get_skill_manifest,
    get_tool_registry,
    get_total_tool_count,
)

__all__ = [
    "create_codomyrmex_mcp_server",
    "get_tool_registry",
    "get_skill_manifest",
    "call_tool",
    "get_total_tool_count",
    "invalidate_tool_cache",
    "TOOL_COUNT",
    "RESOURCE_COUNT",
    "PROMPT_COUNT",
]

TOOL_COUNT: int = len(_TOOL_DEFINITIONS)
RESOURCE_COUNT: int = len(_RESOURCE_DEFINITIONS)
PROMPT_COUNT: int = len(_PROMPT_DEFINITIONS)
