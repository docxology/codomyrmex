# PAI Integration Scripts — Specification

**Version**: v0.1.7 | **Status**: Active

## 1. Functional Requirements

The `scripts/agents/pai/` directory must:

1. **Demonstrate Trust Lifecycle**: Full UNTRUSTED → VERIFIED → TRUSTED state machine
2. **Exercise MCP Operations**: Server creation, registry inspection, health validation
3. **Show Tool Invocation**: Direct, trust-gated, dynamic, and error-handling patterns
4. **Cover Algorithm Phases**: Walk through all 7 Algorithm phases with real tool calls
5. **Integrate Claude**: Show ClaudeClient working with PAI tools
6. **Audit Security**: Classify tools, inspect TELOS, analyze security config
7. **Not Duplicate**: Must not overlap with `pai_example.py` general discovery

## 2. API Surface

All scripts:

```
python scripts/agents/pai/<script>.py [--section <name>] [--json] [--help]
```

Return codes: `0` = success/graceful skip, `1` = unexpected error

## 3. Dependencies

- **Internal**: `codomyrmex.agents.pai` (31 symbols), `codomyrmex.agents.claude`, `codomyrmex.utils.cli_helpers`, `codomyrmex.logging_monitoring`
- **External**: Standard library (`argparse`, `json`, `pathlib`, `sys`)
- **Optional**: `anthropic` (for `claude_pai_bridge.py` only)

## 4. Constraints

- No writes to `~/.claude/` or any PAI files
- Trust state changes must be reset before script exit
- Scripts must work when PAI is NOT installed (graceful empty results)
- Each script: 100–200 lines
- All scripts independently executable

## 5. Script Dependency Tiers

```
agent_personality.py  ─┐
memory_explorer.py    ─┤ Tier 1: PAIBridge read-only
hook_lifecycle.py     ─┤
security_audit.py     ─┘
                        ↓
mcp_server_ops.py     ─┐
skill_manifest.py     ─┤ Tier 2: MCP layer
tool_invocation.py    ─┘
                        ↓
trust_lifecycle.py    ─── Tier 3: Trust state machine
                        ↓
claude_pai_bridge.py  ─┐
algorithm_orchestrator.py ─┘ Tier 4: Integration
```

## 6. Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
