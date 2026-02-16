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
    verify_capabilities()   # audit + promote safe tools
    trust_all()             # promote destructive tools
    trusted_call_tool("codomyrmex.write_file", path="x.py", content="...")
    ```

Version: v0.4.0
"""

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

from .mcp_bridge import (
    TOOL_COUNT,
    RESOURCE_COUNT,
    PROMPT_COUNT,
    call_tool,
    create_codomyrmex_mcp_server,
    get_skill_manifest,
    get_tool_registry,
)

from .trust_gateway import (
    DESTRUCTIVE_TOOL_COUNT,
    DESTRUCTIVE_TOOLS,
    SAFE_TOOL_COUNT,
    SAFE_TOOLS,
    TrustLevel,
    TrustRegistry,
    get_trust_report,
    is_trusted,
    reset_trust,
    trust_all,
    trust_tool,
    trusted_call_tool,
    verify_capabilities,
)

__all__ = [
    # Core
    "PAIBridge",
    "PAIConfig",
    # Data classes
    "PAISkillInfo",
    "PAIToolInfo",
    "PAIHookInfo",
    "PAIAgentInfo",
    "PAIMemoryStore",
    # Constants
    "ALGORITHM_PHASES",
    "RESPONSE_DEPTH_LEVELS",
    "PAI_PRINCIPLES",
    "PAI_UPSTREAM_URL",
    # MCP Bridge
    "create_codomyrmex_mcp_server",
    "get_tool_registry",
    "get_skill_manifest",
    "call_tool",
    "TOOL_COUNT",
    "RESOURCE_COUNT",
    "PROMPT_COUNT",
    # Trust Gateway
    "TrustLevel",
    "TrustRegistry",
    "verify_capabilities",
    "trust_tool",
    "trust_all",
    "trusted_call_tool",
    "get_trust_report",
    "is_trusted",
    "reset_trust",
    "SAFE_TOOLS",
    "DESTRUCTIVE_TOOLS",
    "SAFE_TOOL_COUNT",
    "DESTRUCTIVE_TOOL_COUNT",
]

__version__ = "0.4.0"

