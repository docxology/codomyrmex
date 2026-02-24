# Codomyrmex Agents — src/codomyrmex/agents/pai

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Upstream**: [danielmiessler/Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure)

## Purpose

Full-featured PAI bridge module. Discovers, validates, and provides programmatic access to all PAI subsystems at `~/.claude/skills/PAI/`.

## Active Components

| File | Lines | Description |
|------|-------|-------------|
| `__init__.py` | ~110 | Public API exports (31 symbols) |
| `pai_bridge.py` | ~680 | Bridge client with all subsystem operations |
| `mcp_bridge.py` | ~1,266 | MCP bridge — 20 static tools (17 core + 3 universal proxy) + auto-discovered module tools, 2 resources, 10 prompts |
| `trust_gateway.py` | ~405 | Trust gateway — UNTRUSTED/VERIFIED/TRUSTED tiers |

## Method Inventory

### PAIBridge (pai_bridge.py)

| Category | Method | Description |
|----------|--------|-------------|
| Discovery | `is_installed()` | SKILL.md existence check |
| Discovery | `get_status()` | Full installation status |
| Discovery | `get_components()` | Component enumeration |
| Algorithm | `get_algorithm_phases()` | 7 phases (static) |
| Algorithm | `get_algorithm_version()` | Parse version from SKILL.md |
| Algorithm | `get_principles()` | 16 PAI Principles (static) |
| Algorithm | `get_response_depth_levels()` | 3 depth levels (static) |
| Skills | `list_skills()` | All skill packs |
| Skills | `get_skill_info(name)` | Single skill details |
| Tools | `list_tools()` | All TypeScript tools |
| Tools | `get_tool_info(name)` | Single tool details |
| Hooks | `list_hooks()` | All hooks (active + archived) |
| Hooks | `list_active_hooks()` | Active hooks only |
| Hooks | `get_hook_info(name)` | Single hook details |
| Agents | `list_agents()` | Agent personalities |
| Agents | `get_agent_info(name)` | Single agent details |
| Memory | `list_memory_stores()` | Memory subdirectories |
| Memory | `get_memory_info(store)` | Single store details |
| Security | `get_security_config()` | Security system status |
| TELOS | `get_telos_files()` | Identity/goals files |
| Settings | `get_settings()` | Parsed settings.json |
| Settings | `get_pai_env()` | PAI env variables |
| MCP | `get_mcp_registration()` | MCP config |
| MCP | `has_codomyrmex_mcp()` | Registration check |

### PAIConfig (pai_bridge.py)

| Property | Path |
|----------|------|
| `pai_root` | `~/.claude/skills/PAI` |
| `skill_md` | Algorithm SKILL.md |
| `skills_dir` | `~/.claude/skills/` |
| `tools_dir` | `~/.claude/skills/PAI/Tools/` |
| `agents_dir` | `~/.claude/agents/` |
| `memory_dir` | `~/.claude/MEMORY/` |
| `hooks_dir` | `~/.claude/hooks/` |
| `security_dir` | `~/.claude/skills/PAI/PAISECURITYSYSTEM/` |
| `telos_dir` | `~/.claude/USER/` |
| `components_dir` | `~/.claude/skills/PAI/Components/` |

### MCP Bridge (mcp_bridge.py)

| Category | Function | Description |
|----------|----------|-------------|
| Server | `create_codomyrmex_mcp_server()` | Fully-configured MCP server |
| Registry | `get_tool_registry()` | Pre-populated tool registry |
| Direct | `call_tool(name, **kwargs)` | Direct Python invocation |
| Manifest | `get_skill_manifest()` | PAI-compatible skill manifest |

### Trust Gateway (trust_gateway.py)

| Category | Function | Description |
|----------|----------|-------------|
| Audit | `verify_capabilities()` | Full capability audit → VERIFIED |
| Trust | `trust_tool(name)` | Promote single tool to TRUSTED |
| Trust | `trust_all()` | Promote all tools to TRUSTED |
| Execute | `trusted_call_tool(name, **kw)` | Trust-gated tool invocation |
| Query | `get_trust_report()` | Current trust state |
| Query | `is_trusted(name)` | Bool trust check |
| Reset | `reset_trust()` | Reset all to UNTRUSTED |

## Operating Contracts

1. **Real Filesystem**: All discovery uses actual filesystem operations — zero mocks
2. **Graceful Degradation**: Returns structured results even when PAI is not installed
3. **Logging**: Uses `logging_monitoring.get_logger()` for warnings
4. **No Side Effects**: Read-only discovery; never modifies PAI files

## Navigation Links

- **README**: [README.md](README.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)
- **MCP Tool Spec**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **SKILL**: [SKILL.md](SKILL.md)
- **Parent**: [agents](../README.md)
