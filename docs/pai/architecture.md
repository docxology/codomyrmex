# PAI-Codomyrmex Architecture

**Version**: v0.4.0 | **Last Updated**: February 2026

## System Overview

PAI (Personal AI Infrastructure) is the orchestrator that runs The Algorithm on every Claude Code prompt. Codomyrmex is the toolbox that PAI agents consume via MCP (Model Context Protocol).

```
┌──────────────────────────────────────┐
│  PAI (TypeScript/Bun)                │
│  ~/.claude/skills/PAI/               │
│                                      │
│  ┌──────────┐  ┌──────────────────┐  │
│  │ Algorithm │  │ Skills/Hooks/    │  │
│  │ v1.5.0   │  │ Agents/Memory    │  │
│  └────┬─────┘  └────────┬─────────┘  │
│       │                 │            │
│       └────────┬────────┘            │
│                ▼                     │
│  ┌──────────────────────────────┐    │
│  │ Claude Code (MCP Client)     │    │
│  └──────────────┬───────────────┘    │
└─────────────────┼────────────────────┘
                  │ MCP Protocol / Direct Python
                  ▼
┌──────────────────────────────────────┐
│  Codomyrmex (Python/uv)             │
│  src/codomyrmex/agents/pai/         │
│                                      │
│  ┌───────────┐  ┌────────────────┐   │
│  │ PAIBridge  │  │ MCP Bridge     │   │
│  │ Discovery  │  │ 18 static +    │   │
│  │ Validation │  │ auto-discovered│   │
│  └───────────┘  └───────┬────────┘   │
│                         │            │
│  ┌──────────────────────┴─────────┐  │
│  │ Trust Gateway                   │  │
│  │ UNTRUSTED → VERIFIED → TRUSTED  │  │
│  └─────────────────────────────────┘  │
│                                      │
│  ┌─────────────────────────────────┐  │
│  │ 78 Codomyrmex Modules           │  │
│  │ (coding, llm, security, ...)    │  │
│  └─────────────────────────────────┘  │
└──────────────────────────────────────┘
```

## Component Architecture

### PAIBridge (`pai_bridge.py`, ~680 lines)

The discovery and validation layer. Reads PAI's filesystem to enumerate all subsystems.

**Responsibilities:**
- Installation detection (`is_installed()` — checks for SKILL.md)
- Component enumeration (skills, tools, hooks, agents, memory)
- Algorithm metadata (phases, version, principles)
- Settings and environment access
- MCP registration verification

**Key design decisions:**
- **Read-only**: Never modifies PAI files
- **Zero-mock**: Uses real `pathlib.Path` and `json` — no test doubles
- **Graceful fallback**: Returns `[]` or `{}` when PAI is absent

### MCP Bridge (`mcp_bridge.py`, ~1,020 lines)

Exposes all Codomyrmex capabilities as MCP tools for PAI consumption.

**Static Tools (18):**
- 15 core tools: file ops, code analysis, git, shell, data, discovery, PAI, testing
- 3 universal proxy tools: `list_module_functions`, `call_module_function`, `get_module_readme`

**Dynamic Discovery:**
The bridge auto-discovers additional tools from Codomyrmex modules:
1. **Phase 1**: Scans for `@mcp_tool` decorated functions in targeted modules
2. **Phase 2**: Auto-discovers all public functions from every module via `discover_all_public_tools()`

**Resources (2):** `codomyrmex://modules` (inventory), `codomyrmex://status` (health)

**Prompts (10):**
- 3 dotted prompts: `analyze_module`, `debug_issue`, `create_test`
- 7 camelCase workflow prompts: `codomyrmexAnalyze`, `codomyrmexMemory`, `codomyrmexSearch`, `codomyrmexDocs`, `codomyrmexStatus`, `codomyrmexVerify`, `codomyrmexTrust`

### Trust Gateway (`trust_gateway.py`, ~405 lines)

Gates destructive tools behind explicit approval using a three-tier model.

```
UNTRUSTED ──/codomyrmexVerify──→ VERIFIED ──/codomyrmexTrust──→ TRUSTED
   │                                │                              │
   │ All tools start here           │ Safe tools promoted          │ Destructive tools
   │ Cannot execute anything        │ Can execute read-only ops    │ Full execution
   └────────────────────────────────┴──────────────────────────────┘
```

**Safe tools (14 static):** Auto-promoted to VERIFIED by `/codomyrmexVerify`
- `read_file`, `list_directory`, `analyze_python`, `search_codebase`, `git_status`, `git_diff`, `json_query`, `checksum_file`, `list_modules`, `module_info`, `pai_status`, `pai_awareness`, `list_module_functions`, `get_module_readme`

**Destructive tools (4):** Require explicit `/codomyrmexTrust`
- `write_file`, `run_command`, `run_tests`, `call_module_function`

**Dynamic tool trust:** Auto-discovered tools are classified by pattern matching on function names (e.g., names containing "write", "delete", "execute" are flagged destructive).

**Persistence:** Trust state is persisted to `~/.codomyrmex/trust_ledger.json` and survives across sessions.

## Data Flow

### PAI → Codomyrmex (Tool Invocation)

```
PAI Agent (TypeScript)
  │
  ├─ MCP Protocol ──→ create_codomyrmex_mcp_server() ──→ MCPServer.run()
  │                                                         │
  │                                                    Tool Registry
  │                                                    (static + dynamic)
  │                                                         │
  └─ Direct Python ──→ call_tool("codomyrmex.X", **kw) ────┘
                              │
                         Trust Gateway
                         (enforces trust level)
                              │
                         Tool Handler
                         (actual implementation)
```

### Codomyrmex → PAI (Discovery)

```
PAIBridge
  │
  ├─ ~/.claude/skills/PAI/SKILL.md     → Algorithm version
  ├─ ~/.claude/skills/*/               → Skill enumeration
  ├─ ~/.claude/skills/PAI/Tools/*.ts   → Tool listing
  ├─ ~/.claude/hooks/                  → Hook discovery
  ├─ ~/.claude/agents/*.md             → Agent personalities
  ├─ ~/.claude/MEMORY/                 → Memory stores
  ├─ ~/.claude/skills/PAI/PAISECURITYSYSTEM/ → Security config
  ├─ ~/.claude/USER/                   → TELOS files
  └─ ~/.claude/settings.json           → Settings & env vars
```

## Cross-Language Communication

PAI runs in TypeScript/Bun. Codomyrmex runs in Python. Communication happens through:

1. **MCP Protocol** (primary): PAI's Claude Code integration consumes the Codomyrmex MCP server registered in `claude_desktop_config.json`
2. **Direct Python calls** (internal): Codomyrmex modules call each other directly — `call_tool()` bypasses MCP overhead
3. **Filesystem** (shared state): Both systems read shared config files (`settings.json`, trust ledger)

## Navigation

- **Index**: [README.md](README.md)
- **Tools**: [tools-reference.md](tools-reference.md)
- **API**: [api-reference.md](api-reference.md)
- **Workflows**: [workflows.md](workflows.md)
- **Root PAI Bridge**: [../../PAI.md](../../PAI.md)
