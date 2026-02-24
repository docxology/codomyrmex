# Personal AI Infrastructure — PAI Bridge Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: pai
**Status**: Active
**Upstream**: [danielmiessler/Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure)

## Context

This module **is** the PAI bridge within the Codomyrmex agent layer. It provides programmatic access from Codomyrmex *to* the full PAI system, covering all subsystems.

## PAI Subsystem Coverage

| PAI Subsystem | Bridge Method | Data Returned |
|---------------|---------------|---------------|
| Algorithm | `get_algorithm_phases()`, `get_algorithm_version()` | 7 phases, version string |
| Principles | `get_principles()` | 16 PAI Principles |
| Skills | `list_skills()`, `get_skill_info()` | Skill packs with SKILL.md/Tools/Workflows detection |
| Tools | `list_tools()`, `get_tool_info()` | TypeScript CLI tools with size |
| Hooks | `list_hooks()`, `list_active_hooks()` | Lifecycle hooks with archive status |
| Agents | `list_agents()`, `get_agent_info()` | Personality definitions |
| Memory | `list_memory_stores()`, `get_memory_info()` | Memory stores with item counts |
| Security | `get_security_config()` | Security system files and patterns |
| TELOS | `get_telos_files()` | Identity/mission/goals files |
| Settings | `get_settings()`, `get_pai_env()` | Configuration and env variables |
| MCP | `get_mcp_registration()`, `has_codomyrmex_mcp()` | Server registration status |

## Algorithm Phase Mapping

This module maps to The Algorithm phases:

| Phase | Role | Command |
|-------|------|---------|
| **OBSERVE** | `get_status()`, `get_components()` | `/codomyrmexVerify` |
| **THINK** | `get_algorithm_phases()`, `get_principles()` | |
| **VERIFY** | `has_codomyrmex_mcp()` | `/codomyrmexTrust` |
| **LEARN** | `list_memory_stores()` | |

## MCP Bridge — Codomyrmex → PAI

The `mcp_bridge.py` module exposes all Codomyrmex capabilities as MCP tools:

- **20 Static MCP Tools** (17 core + 3 universal proxy) + auto-discovered module tools
- **2 Resources**: module inventory, system status
- **10 Prompts** (3 dotted + 7 camelCase workflows)
- **Algorithm Mapping**: Each tool maps to an Algorithm phase (OBSERVE → LEARN)
- **Knowledge Scope**: 7 domains covering all 82 modules

```python
from codomyrmex.agents.pai import call_tool
modules = call_tool("codomyrmex.list_modules")
```

See [SKILL.md](SKILL.md) and [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md).

## AI Strategy

1. **Use `is_installed()` first**: Gate PAI-dependent logic on installation check
2. **Read-only**: This module never writes to `~/.claude/`
3. **Graceful fallback**: All list methods return `[]` when PAI is absent
4. **Upstream reference**: Use `PAI_UPSTREAM_URL` for attribution

## Signposting

### Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Agents PAI documentation
- **Root Bridge**: [../../../../PAI.md](../../../../PAI.md) — Authoritative PAI system bridge

### Related Documentation

- [README.md](README.md) — Module overview
- [AGENTS.md](AGENTS.md) — Agent coordination
- [SPEC.md](SPEC.md) — Technical specification
- [SKILL.md](SKILL.md) — PAI skill manifest
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) — MCP tool specs
- [MCP Bridge](../../model_context_protocol/PAI.md) — MCP integration with PAI
