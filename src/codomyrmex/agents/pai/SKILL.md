---
name: Codomyrmex
description: Full-spectrum coding workspace skill providing ~600 production MCP `@mcp_tool` lines across 128 top-level modules. USE WHEN user says 'verify codomyrmex', 'codomyrmexVerify', 'audit codomyrmex', 'trust codomyrmex', 'codomyrmexTrust', 'trust tools', 'enable destructive tools', 'check pai status', 'codomyrmex tools', 'codomyrmex analyze', 'codomyrmex search', 'codomyrmex memory', 'codomyrmex docs', 'codomyrmex status', 'codomyrmex git', 'codomyrmex security', 'codomyrmex ai', 'codomyrmex code', 'codomyrmex data', 'codomyrmex deploy', 'codomyrmex test', or uses any 'codomyrmex' automation tools.
---
# Codomyrmex Skill for PAI

**Version**: v1.0.8 | **Type**: Infrastructure Skill | **MCP**: `codomyrmex-mcp-server` | **Skills**: 15 | **Tools**: ~600 (`@mcp_tool`; see `docs/reference/inventory.md`)

Canonical copy for install-from-repo: [SKILL.md](../../../../SKILL.md) at repository root. This file stays aligned with that manifest for PAI pack resolution.

## Description

Full-spectrum coding workspace skill providing ~600 production `@mcp_tool` lines across 128 top-level modules for AI-assisted development, code analysis, testing, documentation generation, and workflow automation.

## Installation

```bash
pip install codomyrmex
# or
uv add codomyrmex
```

## Quick Start

```python
# MCP server (for PAI agent consumption)
from codomyrmex.agents.pai.mcp_bridge import create_codomyrmex_mcp_server
server = create_codomyrmex_mcp_server()
server.run()

# Direct Python calls (no MCP overhead)
from codomyrmex.agents.pai import verify_capabilities, trust_all, trusted_call_tool

verify_capabilities()   # Step 1: Audit & promote safe tools
trust_all()             # Step 2: Grant full execution trust
result = trusted_call_tool("codomyrmex.write_file", path="x.py", content="...")
```

## Live tool and prompt inventory

Static documentation cannot list every MCP tool (the surface is large and changes with the tree). Use:

```python
from codomyrmex.agents.pai import get_skill_manifest

m = get_skill_manifest()
len(m["tools"])   # merged static + dynamic tool count
m["prompts"]      # prompt names and descriptions
m["workflows"]    # bundled workflow definitions
```

Refresh documented **decorator** and **file** counts after MCP changes: `uv run python scripts/doc_inventory.py` (optional: `--manifest` for runtime tool count).

## Skill Domains (15)

| Skill | Domain | Key Triggers |
| ------- | -------- | -------------- |
| `codomyrmexVerify` | Capability Audit | "verify codomyrmex", "audit tools" |
| `codomyrmexTrust` | Trust Management | "trust codomyrmex", "enable destructive" |
| `codomyrmexAnalyze` | Code Analysis | "analyze project", "code review" |
| `codomyrmexMemory` | Memory | "add to memory", "remember this" |
| `codomyrmexSearch` | Search | "search codebase", "grep pattern" |
| `codomyrmexDocs` | Documentation | "get module docs", "module readme" |
| `codomyrmexStatus` | Status Dashboard | "system status", "health check" |
| `CodomyrmexGit` | Version Control | "git analysis", "commit timeline" |
| `CodomyrmexSecurity` | Security & Crypto | "security scan", "crypto key" |
| `CodomyrmexAI` | AI & Agents | "reasoning trace", "thinking agent" |
| `CodomyrmexCode` | Code Execution | "execute code", "sandbox code" |
| `CodomyrmexData` | Data & Visualization | "bar chart", "fuzzy search" |
| `CodomyrmexDeploy` | Infrastructure | "docker build", "list instances" |
| `CodomyrmexTest` | Testing | "run tests", "benchmark" |

## Tools Summary (~600 decorators)

Most tools are read-only; a small set is destructive (require `/codomyrmexTrust`). Run `/codomyrmexVerify` for the live safe/destructive split.

- **Destructive**: `write_file`, `run_command`, `run_tests`, `call_module_function`

Auto-discovered from **149** `mcp_tools.py` files across the package tree (128 top-level modules). Volatile numbers: [docs/reference/inventory.md](../../../../docs/reference/inventory.md).

## Resources

- `codomyrmex://modules` — Full module inventory (JSON)
- `codomyrmex://status` — System + PAI status (JSON)

## Prompts

| Name | Description |
|------|-------------|
| `codomyrmex.analyze_module` | Analyze a module (structure → tests → docs) |
| `codomyrmex.debug_issue` | Debug an issue using codomyrmex tools |
| `codomyrmex.create_test` | Generate zero-mock tests for a module |
| `codomyrmexVerify` | Verify all capabilities (runs /codomyrmexVerify workflow) |
| `codomyrmexTrust` | Trust all tools (runs /codomyrmexTrust workflow) |

## Algorithm Phase Mapping

| Phase | Primary Tools |
| ------- | --------------- |
| OBSERVE | `list_modules`, `module_info`, `health_check`, `dependency_tree` |
| THINK | `analyze_python`, `search_codebase`, `think`, `query_knowledge_base` |
| PLAN | `read_file`, `json_query`, `analyze_workflow_dependencies` |
| BUILD | `write_file`, `generate_module_docs`, `code_execute` |
| EXECUTE | `run_command`, `run_tests`, `execute_agent`, `container_build` |
| VERIFY | `git_diff`, `checksum_file`, `solve_model`, `audit_code_security` |
| LEARN | `pai_awareness`, `memory_put`, `emit_event` |

## Trust Levels

| Level | Access | How |
| ------- | -------- | ------------ |
| `UNTRUSTED` | None | Default state |
| `VERIFIED` | Read-only tools | `/codomyrmexVerify` |
| `TRUSTED` | All dynamic tools (~600 production `@mcp_tool` lines in Python tree; see inventory) plus PAI static proxy tools | `/codomyrmexTrust` |

## Workflow Routing

**When executing a workflow, output this notification directly:**

```
Running the **WorkflowName** workflow in the **Codomyrmex** skill to ACTION...
```

| Workflow | Trigger | Skill |
|----------|---------|-------|
| **codomyrmexVerify** | "/codomyrmexVerify", "verify codomyrmex", "audit tools" | `codomyrmexVerify` |
| **codomyrmexTrust** | "/codomyrmexTrust", "trust codomyrmex", "trust all" | `codomyrmexTrust` |
| **codomyrmexAnalyze** | "/codomyrmexAnalyze", "analyze project", "code analysis" | `codomyrmexAnalyze` |
| **codomyrmexMemory** | "/codomyrmexMemory", "add to memory", "store memory" | `codomyrmexMemory` |
| **codomyrmexSearch** | "/codomyrmexSearch", "search codebase", "grep pattern" | `codomyrmexSearch` |
| **codomyrmexDocs** | "/codomyrmexDocs", "get module docs", "module documentation" | `codomyrmexDocs` |
| **codomyrmexStatus** | "/codomyrmexStatus", "system status", "health check" | `codomyrmexStatus` |

## Knowledge scope

Authoritative package list: `codomyrmex.list_modules`, resource `codomyrmex://modules`, and [docs/reference/inventory.md](../../../../docs/reference/inventory.md) (128 top-level modules as of last inventory refresh).

## Repository

Source: `src/codomyrmex/agents/pai/` — MCP bridge, trust gateway, PAI bridge
