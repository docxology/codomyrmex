# Codomyrmex Agents — scripts/agents/pai

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Deep PAI integration example scripts exercising the full 31-symbol PAI agent API. Each script targets a distinct capability area with real tool invocations and orchestration patterns.

## Script Inventory

| File | ~Lines | Description |
|------|--------|-------------|
| `trust_lifecycle.py` | 180 | Complete trust state machine demo |
| `mcp_server_ops.py` | 170 | MCP server creation and health validation |
| `tool_invocation.py` | 160 | Direct, trusted, dynamic, and error tool patterns |
| `skill_manifest.py` | 150 | Manifest generation and algorithm mapping |
| `agent_personality.py` | 140 | Agent personality enumeration and cross-referencing |
| `memory_explorer.py` | 150 | Memory system three-tier analysis |
| `algorithm_orchestrator.py` | 200 | 7-phase Algorithm orchestration capstone |
| `claude_pai_bridge.py` | 180 | ClaudeClient + PAI combined workflow |
| `security_audit.py` | 150 | Security config, TELOS, tool classification |
| `hook_lifecycle.py` | 140 | Hook enumeration and lifecycle analysis |

## Method Coverage Matrix

| API Method | trust | mcp | tool | skill | agent | memory | algo | claude | sec | hook |
|------------|:-----:|:---:|:----:|:-----:|:-----:|:------:|:----:|:------:|:---:|:----:|
| `PAIBridge.is_installed()` | | | | | X | | X | X | | |
| `PAIBridge.get_status()` | | | | | | | X | | | |
| `PAIBridge.get_components()` | | | | | | | X | | | |
| `PAIBridge.list_skills()` | | | | X | X | | X | | | |
| `PAIBridge.list_tools()` | | | | | | | X | | | |
| `PAIBridge.list_hooks()` | | | | | | | | | | X |
| `PAIBridge.list_active_hooks()` | | | | | | | | | | X |
| `PAIBridge.list_agents()` | | | | | X | | | | | |
| `PAIBridge.list_memory_stores()` | | | | | | X | X | | | |
| `PAIBridge.get_security_config()` | | | | | | | | | X | |
| `PAIBridge.get_telos_files()` | | | | | | | | | X | |
| `PAIBridge.get_settings()` | | | | | | | | | X | |
| `PAIBridge.get_pai_env()` | | | | | | | | | X | |
| `verify_capabilities()` | X | | X | | | | X | | | |
| `trust_tool()` | X | | | | | | | | | |
| `trust_all()` | X | | X | | | | X | | | |
| `trusted_call_tool()` | X | | X | | | | X | | | |
| `get_trust_report()` | X | | | | | | X | | | |
| `reset_trust()` | X | | X | | | | X | | | |
| `call_tool()` | X | | X | | | | X | X | | |
| `create_mcp_server()` | | X | | | | | | | | |
| `get_tool_registry()` | | X | | X | | | | X | | |
| `get_skill_manifest()` | | | | X | | | X | X | | |

## Operating Contracts

1. **No Mutation of PAI**: Scripts never write to `~/.claude/` (except trust_ledger.json, which is reset)
2. **Trust Reset**: Scripts that modify trust state must reset on exit via `finally` block
3. **Graceful Degradation**: Return 0 when PAI is not installed
4. **CLI Helpers**: Use `codomyrmex.utils.cli_helpers` for formatted output
5. **argparse CLI**: All scripts accept `--help` and `--json` flags

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- **Parent**: [../README.md](../README.md)
