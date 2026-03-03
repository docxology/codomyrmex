# PAI Integration Example Scripts

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive example scripts demonstrating the full PAI (Personal AI Infrastructure) agent integration API. These scripts go beyond basic discovery (covered by `pai_example.py`) into trust lifecycle management, MCP server operations, tool invocation patterns, Algorithm orchestration, and Claude integration.

**Upstream**: https://github.com/danielmiessler/Personal_AI_Infrastructure

## Prerequisites

- PAI installed at `~/.claude/skills/PAI/`
- Codomyrmex installed (`uv sync`)
- Optional: Anthropic API key for `claude_pai_bridge.py`

## Quick Start

```bash
# Explore PAI agent personalities
uv run python scripts/agents/pai/agent_personality.py

# Full trust lifecycle demo
uv run python scripts/agents/pai/trust_lifecycle.py

# 7-phase Algorithm orchestration
uv run python scripts/agents/pai/algorithm_orchestrator.py --phase all

# All scripts support --json and --help
uv run python scripts/agents/pai/tool_invocation.py --json
```

## Scripts

| Script | ~Lines | Description | API Coverage |
|--------|--------|-------------|--------------|
| `trust_lifecycle.py` | 180 | Trust state machine: UNTRUSTED→VERIFIED→TRUSTED | TrustRegistry, verify/trust/reset |
| `mcp_server_ops.py` | 170 | MCP server creation and validation | create_server, get_registry |
| `tool_invocation.py` | 160 | All tool calling patterns | call_tool, trusted_call_tool |
| `skill_manifest.py` | 150 | Manifest generation and inspection | get_skill_manifest |
| `agent_personality.py` | 140 | Agent personality enumeration | list_agents, get_agent_info |
| `memory_explorer.py` | 150 | Memory system deep dive | list_memory_stores |
| `algorithm_orchestrator.py` | 200 | 7-phase Algorithm walkthrough | Nearly all 31 symbols |
| `claude_pai_bridge.py` | 180 | Claude + PAI integration | ClaudeClient + PAIBridge |
| `security_audit.py` | 150 | Security and trust classification | SAFE/DESTRUCTIVE_TOOLS |
| `hook_lifecycle.py` | 140 | Hook system analysis | list_hooks, active hooks |

## Learning Path

1. **Discovery** (Tier 1): `agent_personality` → `memory_explorer` → `hook_lifecycle` → `security_audit`
2. **MCP Layer** (Tier 2): `mcp_server_ops` → `skill_manifest` → `tool_invocation`
3. **Trust** (Tier 3): `trust_lifecycle`
4. **Integration** (Tier 4): `claude_pai_bridge` → `algorithm_orchestrator`

## Relationship to Existing Scripts

These scripts complement (do not replace) the flat `scripts/agents/` PAI scripts:

- `pai_example.py` — General discovery across 11 subsystems (read-only)
- `pai_dashboard.py` — Web dashboard launcher
- `simulate_pai_chat.py` — Slash command simulator

## Navigation

- **Parent**: [../README.md](../README.md) — Agent scripts root
- **PAI Module**: [../../../src/codomyrmex/agents/pai/README.md](../../../src/codomyrmex/agents/pai/README.md)
- **PAI Bridge Doc**: [../../../PAI.md](../../../PAI.md)
