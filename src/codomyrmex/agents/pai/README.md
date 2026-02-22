# pai

**Version**: v0.4.0 | **Status**: Active | **Last Updated**: February 2026

**Upstream**: [danielmiessler/Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure)

## Overview

The `pai` module bridges Codomyrmex with the PAI (Personal AI Infrastructure) system at `~/.claude/skills/PAI/`. It provides programmatic access to **all PAI subsystems** — Algorithm, Skills, Tools, Hooks, Agents, Memory, Security, TELOS, and Settings.

PAI is the **orchestrator** that runs The Algorithm on every Claude Code prompt. Codomyrmex is the **toolbox** that PAI agents consume via MCP.

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `PAIBridge` | Class | Main bridge — discovery, validation, and all operations |
| `PAIConfig` | Dataclass | Filesystem path layout |
| `PAISkillInfo` | Dataclass | Skill pack metadata |
| `PAIToolInfo` | Dataclass | TypeScript tool metadata |
| `PAIHookInfo` | Dataclass | Lifecycle hook metadata |
| `PAIAgentInfo` | Dataclass | Agent personality metadata |
| `PAIMemoryStore` | Dataclass | Memory store metadata |
| `ALGORITHM_PHASES` | List | 7-phase Algorithm reference |
| `PAI_PRINCIPLES` | List | 16 PAI Principles |
| `RESPONSE_DEPTH_LEVELS` | List | FULL/ITERATION/MINIMAL levels |
| `create_codomyrmex_mcp_server` | Function | Create MCP server with all tools |
| `call_tool` | Function | Direct Python tool invocation |
| `get_tool_registry` | Function | Pre-populated tool registry |
| `get_skill_manifest` | Function | PAI skill manifest |
| `TrustLevel` | Enum | UNTRUSTED / VERIFIED / TRUSTED |
| `TrustRegistry` | Class | In-memory trust ledger |
| `verify_capabilities` | Function | Full capability audit (→ VERIFIED) |
| `trust_tool` | Function | Promote single tool to TRUSTED |
| `trust_all` | Function | Promote all tools to TRUSTED |
| `trusted_call_tool` | Function | Trust-gated tool execution |

## Quick Start

```python
from codomyrmex.agents.pai import PAIBridge

bridge = PAIBridge()

if bridge.is_installed():
    # Discovery
    print(bridge.get_algorithm_version())   # "v0.2.25"

    # Enumerate all subsystems
    for skill in bridge.list_skills():
        print(f"Skill: {skill.name} ({skill.file_count} files)")
    for tool in bridge.list_tools():
        print(f"Tool: {tool.name}")
    for hook in bridge.list_active_hooks():
        print(f"Hook: {hook.name}")
    for agent in bridge.list_agents():
        print(f"Agent: {agent.name}")
    for store in bridge.list_memory_stores():
        print(f"Memory: {store.name} ({store.item_count} items)")

    # Security & TELOS
    print(bridge.get_security_config())
    print(bridge.get_telos_files())
```

## MCP Bridge

The MCP bridge exposes all Codomyrmex capabilities to PAI agents via MCP protocol or direct Python calls.

```python
from codomyrmex.agents.pai import call_tool, create_codomyrmex_mcp_server

# Direct call (no MCP overhead)
modules = call_tool("codomyrmex.list_modules")
info = call_tool("codomyrmex.module_info", module_name="llm")

# Full MCP server
server = create_codomyrmex_mcp_server()
server.run()  # stdio or HTTP
```

**18 Static + Auto-Discovered Tools** | **2 Resources** | **10 Prompts**

The bridge now supports **Dynamic Discovery**, automatically exposing tools decorated with `@mcp_tool` from key modules (`visualization`, `llm`, `security`, `memory`).

## Trust Gateway

The trust gateway gates destructive tools behind explicit approval:

```python
from codomyrmex.agents.pai import verify_capabilities, trust_all, trusted_call_tool

# Step 1: Audit — promotes safe tools to VERIFIED
report = verify_capabilities()

# Step 2: Trust — promotes destructive tools to TRUSTED
trust_all()

# Step 3: Execute with enforcement
trusted_call_tool("codomyrmex.write_file", path="x.py", content="...")
```

**Trust Levels**: `UNTRUSTED → VERIFIED → TRUSTED`

- **Safe** (14 static tools): Auto-promoted to VERIFIED by `/codomyrmexVerify`
- **Destructive** (4 tools: `write_file`, `run_command`, `run_tests`, `call_module_function`): Require `/codomyrmexTrust`

## API Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `is_installed()` | `bool` | PAI SKILL.md exists |
| `get_status()` | `dict` | Full status with all components |
| `get_algorithm_phases()` | `list` | 7 Algorithm phases |
| `get_algorithm_version()` | `str` | Parsed version from SKILL.md |
| `get_principles()` | `list` | 16 PAI Principles |
| `list_skills()` | `list[PAISkillInfo]` | All skill packs |
| `list_tools()` | `list[PAIToolInfo]` | All TypeScript tools |
| `list_hooks()` | `list[PAIHookInfo]` | All hooks (active + archived) |
| `list_active_hooks()` | `list[PAIHookInfo]` | Active hooks only |
| `list_agents()` | `list[PAIAgentInfo]` | All agent personalities |
| `list_memory_stores()` | `list[PAIMemoryStore]` | All memory subdirectories |
| `get_security_config()` | `dict` | Security system status |
| `get_telos_files()` | `list[str]` | TELOS identity files |
| `get_settings()` | `dict` | Parsed settings.json |
| `get_pai_env()` | `dict[str, str]` | PAI environment variables |
| `get_mcp_registration()` | `dict` | MCP server config |
| `has_codomyrmex_mcp()` | `bool` | Codomyrmex MCP registered |

## Navigation

- **Specification**: [SPEC.md](SPEC.md)
- **Agent Docs**: [AGENTS.md](AGENTS.md)
- **PAI Integration**: [PAI.md](PAI.md)
- **MCP Tool Spec**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **PAI SKILL**: [SKILL.md](SKILL.md)
- **Parent**: [agents](../README.md)
- **Root PAI Bridge**: [../../../../PAI.md](../../../../PAI.md)

## Dashboard & Launch

Launch both PAI servers together using:

```bash
# Start PAI PM (port 8888) + Codomyrmex Admin (port 8787)
uv run python scripts/pai/dashboard.py

# Kill existing, regenerate, restart, open browser
uv run python scripts/pai/dashboard.py --restart
```

See `scripts/pai/README.md` for full usage and `scripts/pai/dashboard.py` for implementation.

- **PAI Project Manager** (primary): `http://localhost:8888` — 12 tabs, 45+ REST endpoints, AI dispatch
- **Codomyrmex Admin** (secondary): `http://localhost:8787` — module health, MCP tools, trust gateway
