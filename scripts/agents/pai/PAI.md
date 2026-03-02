# Personal AI Infrastructure — PAI Scripts Context

**Module**: scripts/agents/pai | **Version**: v1.0.0 | **Status**: Active

## Context

Example scripts demonstrating the full PAI agent integration API surface. These scripts serve as both documentation and validation of the 31-symbol public API exposed by `codomyrmex.agents.pai`.

## AI Strategy

### Core Patterns

1. **Always check installation**: Start with `bridge.is_installed()` before PAI ops
2. **Reset trust on exit**: Any script that calls `trust_all()` must call `reset_trust()`
3. **Graceful degradation**: Return 0 with informational message when PAI is absent
4. **Use cli_helpers**: `setup_logging()`, `print_info/success/warning/error` for output

### Import Pattern

```python
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))
```

### Algorithm Phase Mapping

| Script | Primary Algorithm Phase |
|--------|------------------------|
| `agent_personality.py` | OBSERVE (discover agents) |
| `memory_explorer.py` | LEARN (inspect memory) |
| `hook_lifecycle.py` | OBSERVE (discover hooks) |
| `security_audit.py` | VERIFY (audit security) |
| `mcp_server_ops.py` | BUILD (create server) |
| `skill_manifest.py` | THINK (assess capabilities) |
| `tool_invocation.py` | EXECUTE (call tools) |
| `trust_lifecycle.py` | VERIFY (trust management) |
| `claude_pai_bridge.py` | BUILD + EXECUTE (Claude integration) |
| `algorithm_orchestrator.py` | ALL 7 PHASES |

## Key Symbols (31 total from codomyrmex.agents.pai)

**Classes**: `PAIBridge`, `PAIConfig`, `PAISkillInfo`, `PAIToolInfo`, `PAIHookInfo`, `PAIAgentInfo`, `PAIMemoryStore`, `TrustLevel`, `TrustRegistry`

**Functions**: `verify_capabilities`, `trust_tool`, `trust_all`, `trusted_call_tool`, `get_trust_report`, `is_trusted`, `reset_trust`, `call_tool`, `create_codomyrmex_mcp_server`, `get_tool_registry`, `get_skill_manifest`

**Constants**: `ALGORITHM_PHASES`, `RESPONSE_DEPTH_LEVELS`, `PAI_PRINCIPLES`, `PAI_UPSTREAM_URL`, `SAFE_TOOLS`, `DESTRUCTIVE_TOOLS`, `SAFE_TOOL_COUNT`, `DESTRUCTIVE_TOOL_COUNT`, `TOOL_COUNT`, `RESOURCE_COUNT`, `PROMPT_COUNT`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
- **Parent**: [../README.md](../README.md)
