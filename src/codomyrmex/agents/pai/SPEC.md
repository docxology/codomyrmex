# pai — Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Upstream**: [danielmiessler/Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure)

## Purpose

Comprehensive bridge to the PAI (Personal AI Infrastructure) system. Provides programmatic access to all PAI subsystems at `~/.claude/skills/PAI/`.

## Core Capabilities

### System Discovery

- **Installation Check**: Verify PAI is installed by checking for `SKILL.md`
- **Component Enumeration**: Count skills, tools, hooks, agents, memory, security
- **Settings Access**: Parse `settings.json` for PAI environment variables

### Algorithm Operations

- **Phase Enumeration**: 7-phase protocol (OBSERVE → LEARN)
- **Version Detection**: Parse Algorithm version from SKILL.md
- **Principles**: 16 PAI Principles reference
- **Depth Levels**: FULL / ITERATION / MINIMAL response modes

### Subsystem Access

- **Skills**: List skill packs with SKILL.md/Tools/Workflows detection
- **Tools**: Enumerate TypeScript CLI tools (`.ts` files)
- **Hooks**: List lifecycle hooks with archived status detection
- **Agents**: List agent personality definitions (`.md` files)
- **Memory**: List memory stores with item counts
- **Security**: Read security system configuration
- **TELOS**: List identity/goals files from USER/ directory

### MCP Bridge Validation

- **Registration Check**: Verify codomyrmex in `claude_desktop_config.json`
- **Config Inspection**: Read full MCP server configuration

## Method Inventory

| Method | Returns | Description |
|--------|---------|-------------|
| `is_installed()` | `bool` | SKILL.md existence |
| `get_status()` | `dict` | Full status with all components |
| `get_components()` | `dict` | Component-by-component counts |
| `get_algorithm_phases()` | `list` | 7 Algorithm phases |
| `get_algorithm_version()` | `str` | Parsed version |
| `get_principles()` | `list` | 16 PAI Principles |
| `get_response_depth_levels()` | `list` | 3 depth levels |
| `list_skills()` | `list[PAISkillInfo]` | All skill packs |
| `list_tools()` | `list[PAIToolInfo]` | All TypeScript tools |
| `list_hooks()` | `list[PAIHookInfo]` | All hooks |
| `list_active_hooks()` | `list[PAIHookInfo]` | Active hooks only |
| `list_agents()` | `list[PAIAgentInfo]` | Agent personalities |
| `list_memory_stores()` | `list[PAIMemoryStore]` | Memory stores |
| `get_security_config()` | `dict` | Security system status |
| `get_telos_files()` | `list[str]` | TELOS identity files |
| `get_settings()` | `dict` | Parsed settings.json |
| `get_pai_env()` | `dict[str, str]` | PAI env variables |
| `get_mcp_registration()` | `dict` | MCP config |
| `has_codomyrmex_mcp()` | `bool` | Codomyrmex registered |

## MCP Bridge Operations (mcp_bridge.py)

Exposes all Codomyrmex modules to PAI via MCP protocol or direct Python calls.

| Function | Returns | Description |
|----------|---------|-------------|
| `create_codomyrmex_mcp_server()` | `MCPServer` | Fully-configured MCP server (20 static tools, 2 resources, 10 prompts) |
| `get_tool_registry()` | `MCPToolRegistry` | Pre-populated tool registry |
| `get_skill_manifest()` | `dict` | PAI-compatible skill manifest |
| `call_tool(name, **kwargs)` | `dict` | Direct Python call (no MCP overhead) |

## Design Principles

1. **Read-Only**: Never modifies PAI files or configuration
2. **Zero-Mock**: Uses real `pathlib.Path` and `json` — no test doubles in production
3. **Graceful Failure**: Returns structured empty results when PAI is absent
4. **Minimal Dependencies**: Only depends on `logging_monitoring` from codomyrmex

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Agent Documentation**: [AGENTS.md](AGENTS.md)
- **PAI Integration**: [PAI.md](PAI.md)
- **MCP Tool Spec**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **PAI SKILL**: [SKILL.md](SKILL.md)
- **Parent SPEC**: [../SPEC.md](../SPEC.md)
