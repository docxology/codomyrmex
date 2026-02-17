# Plan: Create PAI Agent Examples in scripts/agents/pai/

## Context

Daniel requested creating `scripts/agents/pai/` with many comprehensive examples demonstrating the full PAI (Personal AI Infrastructure) integration API. The existing flat scripts (`pai_example.py` — read-only discovery, `pai_dashboard.py` — web dashboard, `simulate_pai_chat.py` — slash command simulator) don't exercise the trust lifecycle, MCP server operations, tool invocation patterns, or Algorithm orchestration. The `pai/` subfolder fills this gap with 10 substantive Python scripts + 4 RASP docs, exercising all 31 public symbols from `src/codomyrmex/agents/pai/`.

## Files to Create (14 total)

### RASP Documentation (4 files)

| File | Purpose |
|------|---------|
| `scripts/agents/pai/README.md` | Index, quick start, learning path, script table |
| `scripts/agents/pai/AGENTS.md` | Method coverage matrix, operating contracts |
| `scripts/agents/pai/SPEC.md` | Functional requirements, API surface, constraints |
| `scripts/agents/pai/PAI.md` | AI strategy, Algorithm phase mapping, symbol index |

### Python Scripts (10 files)

| # | File | ~Lines | Description | Key API Exercised |
|---|------|--------|-------------|-------------------|
| 1 | `trust_lifecycle.py` | 180 | Full UNTRUSTED->VERIFIED->TRUSTED state machine with enforcement | `TrustRegistry`, `verify_capabilities`, `trust_tool`, `trust_all`, `trusted_call_tool`, `reset_trust`, `SAFE_TOOLS`, `DESTRUCTIVE_TOOLS` |
| 2 | `mcp_server_ops.py` | 170 | MCP server creation, registry inspection, health validation | `create_codomyrmex_mcp_server`, `get_tool_registry`, `get_total_tool_count`, `TOOL_COUNT`, `RESOURCE_COUNT`, `PROMPT_COUNT` |
| 3 | `tool_invocation.py` | 160 | Direct, trusted, dynamic, and error-handling tool call patterns | `call_tool`, `trusted_call_tool`, `verify_capabilities`, `trust_all` |
| 4 | `skill_manifest.py` | 150 | Manifest generation, algorithm-to-tool mapping, knowledge scope | `get_skill_manifest`, `get_tool_registry`, `ALGORITHM_PHASES` |
| 5 | `agent_personality.py` | 140 | Agent personality discovery and cross-referencing | `PAIBridge.list_agents`, `get_agent_info`, `list_skills` |
| 6 | `memory_explorer.py` | 150 | Memory system three-tier deep dive | `PAIBridge.list_memory_stores`, `get_memory_info`, `PAIConfig` |
| 7 | `algorithm_orchestrator.py` | 200 | **Capstone**: 7-phase Algorithm walkthrough using tools at each phase | Nearly all 31 symbols |
| 8 | `claude_pai_bridge.py` | 180 | Claude client + PAI bridge combined workflow | `ClaudeClient`, `ClaudeIntegrationAdapter`, `PAIBridge`, `call_tool`, `get_skill_manifest` |
| 9 | `security_audit.py` | 150 | Security config, TELOS, destructive tool classification | `get_security_config`, `get_telos_files`, `SAFE_TOOLS`, `DESTRUCTIVE_TOOLS`, `TrustLevel` |
| 10 | `hook_lifecycle.py` | 140 | Hook system enumeration, active/archived analysis | `list_hooks`, `list_active_hooks`, `get_hook_info` |

## Script Conventions (from existing scripts/agents/ patterns)

```python
#!/usr/bin/env python3
"""Docstring with Usage and Upstream link."""
import argparse, json, sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import (
    setup_logging, print_info, print_success, print_warning, print_error
)

def main() -> int:
    args = parse_args()
    setup_logging()
    # ... graceful degradation, sections, cleanup
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

Key conventions:
- `argparse` with `--section`/`--phase` selectors + `--json` + `--help`
- Graceful degradation: return 0 when PAI not installed
- Trust reset on exit for scripts that modify trust state
- `cli_helpers` for all formatted output

## Learning Path

```
Tier 1 — PAIBridge read-only:
  agent_personality.py → memory_explorer.py → hook_lifecycle.py → security_audit.py

Tier 2 — MCP layer:
  mcp_server_ops.py → skill_manifest.py → tool_invocation.py

Tier 3 — Trust state machine:
  trust_lifecycle.py

Tier 4 — Integration (capstone):
  claude_pai_bridge.py → algorithm_orchestrator.py
```

## Non-duplication with existing scripts

| Existing Script | What it covers | How new scripts go deeper |
|----------------|----------------|--------------------------|
| `pai_example.py` | Read-only PAIBridge discovery (11 subsystems) | New scripts exercise *mutable* trust state, *call* tools, *run* MCP servers |
| `pai_dashboard.py` | Web dashboard launcher | New scripts are CLI-first programmatic demonstrations |
| `simulate_pai_chat.py` | Slash command simulator | New scripts use the Python API directly, not slash commands |

## Critical Source Files (reuse, don't reimplement)

- `src/codomyrmex/agents/pai/__init__.py` — 31 public exports
- `src/codomyrmex/agents/pai/pai_bridge.py` — PAIBridge, PAIConfig, dataclasses
- `src/codomyrmex/agents/pai/mcp_bridge.py` — MCP server, tool registry, call_tool
- `src/codomyrmex/agents/pai/trust_gateway.py` — TrustLevel, TrustRegistry, trust functions
- `src/codomyrmex/agents/claude/claude_client.py` — ClaudeClient
- `src/codomyrmex/agents/claude/claude_integration.py` — ClaudeIntegrationAdapter

## Verification

1. All 14 files created and non-empty
2. Each Python script runs: `uv run python scripts/agents/pai/<script>.py --help` exits 0
3. No writes to `~/.claude/` (read-only against PAI filesystem)
4. Trust state reset verified (trust_lifecycle.py, tool_invocation.py, algorithm_orchestrator.py)
5. All 31 public symbols exercised across the suite (coverage matrix in AGENTS.md)
