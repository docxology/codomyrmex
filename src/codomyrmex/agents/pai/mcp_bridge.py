"""PAI <-> Codomyrmex MCP Bridge.

Registers every Codomyrmex capability as MCP tools, resources, and prompts
so that PAI agents can access the full module ecosystem via MCP protocol
or direct Python calls.
"""

from .mcp.definitions import (
    PROMPT_DEFINITIONS,
    RESOURCE_DEFINITIONS,
    TOOL_DEFINITIONS,
)
from .mcp.discovery import get_discovery_metrics, invalidate_tool_cache
from .mcp.proxy_tools import (
    tool_call_module_function,
    tool_get_module_readme,
    tool_list_module_functions,
    tool_list_modules,
    tool_list_workflows,
    tool_module_info,
    tool_pai_awareness,
    tool_pai_status,
    tool_run_tests,
)
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
    "get_discovery_metrics",
    "invalidate_tool_cache",
    "TOOL_COUNT",
    "RESOURCE_COUNT",
    "PROMPT_COUNT",
    "tool_call_module_function",
    "tool_get_module_readme",
    "tool_list_module_functions",
    "tool_list_modules",
    "tool_list_workflows",
    "tool_module_info",
    "tool_pai_awareness",
    "tool_pai_status",
    "tool_run_tests",
]

TOOL_COUNT: int = len(TOOL_DEFINITIONS)
RESOURCE_COUNT: int = len(RESOURCE_DEFINITIONS)
PROMPT_COUNT: int = len(PROMPT_DEFINITIONS)
