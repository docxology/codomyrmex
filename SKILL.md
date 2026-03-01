---
name: Codomyrmex
description: Full-spectrum coding workspace skill providing 171 MCP tools across 33 modules. USE WHEN user says 'verify codomyrmex', 'codomyrmexVerify', 'audit codomyrmex', 'trust codomyrmex', 'codomyrmexTrust', 'trust tools', 'enable destructive tools', 'check pai status', 'codomyrmex tools', 'codomyrmex analyze', 'codomyrmex search', 'codomyrmex memory', 'codomyrmex docs', 'codomyrmex status', 'codomyrmex git', 'codomyrmex security', 'codomyrmex ai', 'codomyrmex code', 'codomyrmex data', 'codomyrmex deploy', 'codomyrmex test', or uses any 'codomyrmex' automation tools.
---
# Codomyrmex Skill for PAI

**Version**: 1.0.4 | **Type**: Infrastructure Skill | **MCP**: `codomyrmex-mcp-server` | **Skills**: 15 | **Tools**: 171

## Description

Full-spectrum coding workspace skill providing 171 MCP tools across 33 auto-discovered modules for AI-assisted development, code analysis, testing, documentation generation, and workflow automation.

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

## Skill Domains (15)

| Skill | Domain | Key Triggers |
|-------|--------|-------------|
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

## Tools Summary (171)

167 safe tools + 4 destructive (require `/codomyrmexTrust`):

- **Destructive**: `write_file`, `run_command`, `run_tests`, `call_module_function`

Auto-discovered from 33 modules covering: agents, cerebrum, coding, containerization, crypto, data_visualization, documentation, events, formal_verification, git_analysis, git_operations, llm, logging_monitoring, maintenance, orchestrator, performance, plugin_system, relations, scrape, search, security, and more.

## Resources

- `codomyrmex://modules` — Full module inventory (JSON)
- `codomyrmex://status` — System + PAI status (JSON)

## Algorithm Phase Mapping

| Phase | Primary Tools |
|-------|-------------|
| OBSERVE | `list_modules`, `module_info`, `health_check`, `dependency_tree` |
| THINK | `analyze_python`, `search_codebase`, `think`, `query_knowledge_base` |
| PLAN | `read_file`, `json_query`, `analyze_workflow_dependencies` |
| BUILD | `write_file`, `generate_module_docs`, `code_execute` |
| EXECUTE | `run_command`, `run_tests`, `execute_agent`, `container_build` |
| VERIFY | `git_diff`, `checksum_file`, `solve_model`, `audit_code_security` |
| LEARN | `pai_awareness`, `memory_put`, `emit_event` |

## Trust Levels

| Level | Access | How |
|-------|--------|-----|
| `UNTRUSTED` | None | Default state |
| `VERIFIED` | Read-only tools | `/codomyrmexVerify` |
| `TRUSTED` | All 171 tools | `/codomyrmexTrust` |

## Repository

Source: `src/codomyrmex/agents/pai/` — MCP bridge, trust gateway, PAI bridge
