# PAI-Codomyrmex Workflows

**Version**: v1.0.3-dev | **Last Updated**: February 2026

## Overview

Codomyrmex provides two primary workflows for PAI integration, plus an Algorithm phase mapping that routes PAI's 7-phase protocol to specific Codomyrmex tools.

## `/codomyrmexVerify` — Capability Audit

**Trigger**: User says "verify codomyrmex", "audit tools", or invokes `/codomyrmexVerify`

**Purpose**: Full read-only audit of all Codomyrmex capabilities. Promotes safe tools from UNTRUSTED to VERIFIED.

**What it does:**

1. Enumerates all Codomyrmex modules
2. Builds the tool registry (static + dynamic)
3. Promotes safe tools to VERIFIED trust level
4. Checks MCP server health (tool/resource/prompt counts match)
5. Verifies PAI bridge status (installation, components)
6. Validates skill manifest integrity

**Backing function**: `verify_capabilities()` in `trust_gateway.py`

**Returns:**
```python
{
    "status": "verified",
    "modules": {"count": N, "names": [...]},
    "tools": {
        "count": N, "expected": M, "match": True/False,
        "safe_count": N, "destructive_count": M,
        "items": [{"name": ..., "trust_level": ..., "category": ...}]
    },
    "resources": {"count": 3, "items": [...]},
    "prompts": {"count": 10, "items": [...]},
    "mcp_server": {"healthy": True/False, "tools": N, "resources": M, "prompts": P},
    "pai_bridge": {"installed": True/False, "components": {...}},
    "skill_manifest": {"valid": True/False, "version": "..."},
    "trust": {"promoted_to_verified": [...], "current_state": {...}}
}
```

**When to use:**
- First interaction with a new Codomyrmex installation
- After updating Codomyrmex modules
- To check system health before executing tools
- Prerequisite for `/codomyrmexTrust`

## `/codomyrmexTrust` — Trust Promotion

**Trigger**: User says "trust codomyrmex", "trust tools", or invokes `/codomyrmexTrust`

**Purpose**: Promotes all tools (including destructive ones) to TRUSTED, enabling full execution.

**What it does:**

1. Calls `trust_all()` to promote every tool to TRUSTED
2. Persists trust state to `~/.codomyrmex/trust_ledger.json`
3. Returns promotion report

**Backing function**: `trust_all()` in `trust_gateway.py`

**Returns:**
```python
{
    "promoted": ["codomyrmex.write_file", "codomyrmex.run_command", ...],
    "count": N,
    "report": {"total_tools": N, "by_level": {...}, "counts": {...}}
}
```

**Security implications:**
- Enables `write_file` (file system writes)
- Enables `run_command` (shell execution)
- Enables `run_tests` (test execution with potential side effects)
- Enables `call_module_function` (arbitrary module function calls)

**When to use:**
- After `/codomyrmexVerify` has audited capabilities
- When you need the full power of Codomyrmex tools
- Trust persists across sessions via the ledger file

## Algorithm Phase → Codomyrmex Module Mapping

Each phase of PAI's 7-phase Algorithm maps to specific Codomyrmex tools:

| Phase | Tools | Purpose |
|-------|-------|---------|
| **OBSERVE** | `list_modules`, `module_info`, `list_directory` | Discover project structure and available modules |
| **THINK** | `analyze_python`, `search_codebase` | Analyze code structure, find patterns |
| **PLAN** | `read_file`, `json_query` | Read existing code and configuration |
| **BUILD** | `write_file` | Create and modify files |
| **EXECUTE** | `run_command`, `run_tests` | Run commands and tests |
| **VERIFY** | `git_status`, `git_diff`, `checksum_file` | Verify changes are correct |
| **LEARN** | `pai_awareness`, `pai_status` | Capture learning, check system state |

### Bidirectional Data Flow

**PAI → Codomyrmex** (during Algorithm execution):
```
OBSERVE: PAI calls list_modules to understand project
THINK:   PAI calls analyze_python to study code structure
PLAN:    PAI calls read_file to review existing implementation
BUILD:   PAI calls write_file to create/modify code
EXECUTE: PAI calls run_command / run_tests to execute
VERIFY:  PAI calls git_diff / checksum_file to verify changes
LEARN:   PAI calls pai_awareness to capture state
```

**Codomyrmex → PAI** (via PAIBridge):
```
bridge.is_installed()         → Is PAI available?
bridge.get_algorithm_version() → What Algorithm version?
bridge.list_skills()           → What skills are available?
bridge.list_hooks()            → What hooks are active?
bridge.has_codomyrmex_mcp()    → Is this bridge registered?
```

## Additional Workflow Prompts

The MCP bridge registers 7 additional workflow prompts (camelCase naming):

| Workflow | Description |
|----------|-------------|
| `codomyrmexAnalyze` | Deep project/file analysis |
| `codomyrmexMemory` | Add to agentic long-term memory |
| `codomyrmexSearch` | Codebase regex search |
| `codomyrmexDocs` | Retrieve module documentation |
| `codomyrmexStatus` | System health & PAI awareness report |
| `codomyrmexVerify` | Capability audit & trust promotion |
| `codomyrmexTrust` | Destructive tool trust granting |

Plus 3 dotted prompts for structured analysis:

| Prompt | Description |
|--------|-------------|
| `codomyrmex.analyze_module` | Analyze module structure → exports → tests → docs |
| `codomyrmex.debug_issue` | Debug using search → analysis → diff → tests |
| `codomyrmex.create_test` | Generate zero-mock tests for a module |

## Navigation

- **Index**: [README.md](README.md)
- **Architecture**: [architecture.md](architecture.md)
- **Tools**: [tools-reference.md](tools-reference.md)
- **API**: [api-reference.md](api-reference.md)
