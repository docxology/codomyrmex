"""PAI (Personal AI Infrastructure) bridge for Codomyrmex agents.

Comprehensive integration between Codomyrmex and the PAI system.

**Upstream**: https://github.com/danielmiessler/Personal_AI_Infrastructure

Provides programmatic access to all PAI subsystems — Algorithm, Skills,
Tools, Hooks, Agents, Memory, Security, TELOS, and Settings.

MCP bridge exposes all Codomyrmex modules to PAI via MCP protocol
or direct Python calls.  Trust gateway gates destructive tools behind
explicit approval (``/codomyrmexVerify`` → ``/codomyrmexTrust``).

Example:
    ```python
    from codomyrmex.agents.pai import PAIBridge, PAIConfig

    bridge = PAIBridge()
    if bridge.is_installed():
        skills = bridge.list_skills()
        tools = bridge.list_tools()

    # MCP access to all Codomyrmex modules
    from codomyrmex.agents.pai import call_tool, create_codomyrmex_mcp_server

    modules = call_tool("codomyrmex.list_modules")
    server = create_codomyrmex_mcp_server()

    # Trust-gated access
    from codomyrmex.agents.pai import verify_capabilities, trust_all, trusted_call_tool

    verify_capabilities()  # audit + promote safe tools
    trust_all()  # promote destructive tools
    trusted_call_tool("codomyrmex.write_file", path="x.py", content="...")
    ```

Version: v0.4.0
"""

from importlib import import_module
from typing import Any

from .mcp_bridge import (
    PROMPT_COUNT,
    RESOURCE_COUNT,
    TOOL_COUNT,
    call_tool,
    create_codomyrmex_mcp_server,
    get_skill_manifest,
    get_tool_registry,
)
from .pai_bridge import (
    ALGORITHM_PHASES,
    PAI_PRINCIPLES,
    PAI_UPSTREAM_URL,
    RESPONSE_DEPTH_LEVELS,
    PAIAgentInfo,
    PAIBridge,
    PAIConfig,
    PAIHookInfo,
    PAIMemoryStore,
    PAISkillInfo,
    PAIToolInfo,
)

# Trust-gateway exports are resolved only when requested.  In particular, the
# dynamic count constants enumerate MCP tools, so importing them eagerly made a
# lightweight ``mcp_bridge`` import recursively import every tool package.
_TRUST_GATEWAY_EXPORTS = frozenset(
    {
        "DESTRUCTIVE_TOOL_COUNT",
        "DESTRUCTIVE_TOOLS",
        "SAFE_TOOL_COUNT",
        "SAFE_TOOLS",
        "TrustLevel",
        "TrustRegistry",
        "get_trust_report",
        "is_trusted",
        "reset_trust",
        "trust_all",
        "trust_tool",
        "trusted_call_tool",
        "verify_capabilities",
    }
)


def __getattr__(name: str) -> Any:
    """Resolve trust-gateway API members without eager tool discovery."""
    if name in _TRUST_GATEWAY_EXPORTS:
        trust_gateway = import_module(f"{__name__}.trust_gateway")
        value = getattr(trust_gateway, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Constants
    "ALGORITHM_PHASES",
    "DESTRUCTIVE_TOOLS",
    "DESTRUCTIVE_TOOL_COUNT",
    "PAI_PRINCIPLES",
    "PAI_UPSTREAM_URL",
    "PROMPT_COUNT",
    "RESOURCE_COUNT",
    "RESPONSE_DEPTH_LEVELS",
    "SAFE_TOOLS",
    "SAFE_TOOL_COUNT",
    "TOOL_COUNT",
    "PAIAgentInfo",
    # Core
    "PAIBridge",
    "PAIConfig",
    "PAIHookInfo",
    "PAIMemoryStore",
    # Data classes
    "PAISkillInfo",
    "PAIToolInfo",
    # Trust Gateway
    "TrustLevel",
    "TrustRegistry",
    "call_tool",
    # MCP Bridge
    "create_codomyrmex_mcp_server",
    "get_skill_manifest",
    "get_tool_registry",
    "get_trust_report",
    "is_trusted",
    "reset_trust",
    "trust_all",
    "trust_tool",
    "trusted_call_tool",
    "verify_capabilities",
]

__version__ = "0.4.0"
