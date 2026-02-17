---
name: Codomyrmex
description: Full-spectrum coding workspace skill providing 100+ modules for AI-assisted development. USE WHEN user says 'verify codomyrmex', 'codomyrmexVerify', 'audit codomyrmex', 'trust codomyrmex', 'codomyrmexTrust', 'trust tools', 'enable destructive tools', 'check pai status', or uses 'codomyrmex' automation tools.
---
# Codomyrmex Skill for PAI

**Version**: 0.4.0 | **Type**: Infrastructure Skill | **MCP**: `codomyrmex-mcp-server`

## Description

Full-spectrum coding workspace skill providing 100+ modules for AI-assisted development, code analysis, testing, documentation generation, and workflow automation. Access via MCP protocol or direct Python calls.

## Quick Start

```python
# MCP server (for PAI agent consumption)
from codomyrmex.agents.pai.mcp_bridge import create_codomyrmex_mcp_server
server = create_codomyrmex_mcp_server()
server.run()

# Direct Python calls (no MCP overhead)
from codomyrmex.agents.pai import call_tool, verify_capabilities, trust_all, trusted_call_tool

verify_capabilities()   # Step 1: Audit & Promote safe tools
trust_all()             # Step 2: Grant full execution trust
result = trusted_call_tool("codomyrmex.write_file", path="x.py", content="...")
```

## Tools (18)

| Tool | Category | Description |
|------|----------|-------------|
| `codomyrmex.read_file` | File Ops | Read file contents with metadata |
| `codomyrmex.write_file` | File Ops | Write content to a file |
| `codomyrmex.list_directory` | File Ops | List directory contents with filtering |
| `codomyrmex.analyze_python` | Code Analysis | Analyze Python file structure and metrics |
| `codomyrmex.search_codebase` | Code Analysis | Search for patterns (regex supported) |
| `codomyrmex.git_status` | Git | Repository status |
| `codomyrmex.git_diff` | Git | Diff for changes |
| `codomyrmex.run_command` | Shell | Execute shell commands safely |
| `codomyrmex.json_query` | Data | Read/query JSON files via dot-notation |
| `codomyrmex.checksum_file` | Data | Calculate file checksum |
| `codomyrmex.list_modules` | Discovery | List all Codomyrmex modules |
| `codomyrmex.module_info` | Discovery | Get module docstring, exports, path |
| `codomyrmex.pai_status` | PAI | Get PAI installation status and component inventory |
| `codomyrmex.pai_awareness` | PAI | Get full PAI awareness data (missions, projects, tasks) |
| `codomyrmex.run_tests`              | Testing   | Run pytest for any module            |
| `codomyrmex.list_module_functions` | Discovery | List functions/classes in any module |
| `codomyrmex.call_module_function`  | Discovery | Call any function in any module      |
| `codomyrmex.get_module_readme`     | Discovery | Read module README/SPEC docs         |

## Resources

| URI | Description |
|-----|-------------|
| `codomyrmex://modules` | Full module inventory (JSON) |
| `codomyrmex://status` | System + PAI status (JSON) |

## Prompts

| Name | Description |
|------|-------------|
| `codomyrmex.analyze_module` | Analyze a module (structure → tests → docs) |
| `codomyrmex.debug_issue` | Debug an issue using codomyrmex tools |
| `codomyrmex.create_test` | Generate zero-mock tests for a module |
| `codomyrmexAnalyze` | Deep project/file analysis workflow |
| `codomyrmexMemory`  | Add to agentic long-term memory     |
| `codomyrmexSearch`  | Codebase regex search workflow      |
| `codomyrmexDocs`    | Retrieve module documentation       |
| `codomyrmexStatus`  | System health & PAI awareness report|
| `codomyrmexVerify`  | Capability audit & trust promotion  |
| `codomyrmexTrust`   | Destructive tool trust granting     |

## Algorithm Phase Mapping

| Phase | Tools |
|-------|-------|
| **OBSERVE** | `list_modules`, `module_info`, `list_directory` |
| **THINK** | `analyze_python`, `search_codebase` |
| **PLAN** | `read_file`, `json_query` |
| **BUILD** | `write_file` |
| **EXECUTE** | `run_command`, `run_tests` |
| **VERIFY** | `git_status`, `git_diff`, `checksum_file` |
| **LEARN** | `pai_awareness`, `pai_status` |

## Workflow Routing

**When executing a workflow, output this notification directly:**

```bash
Running the **WorkflowName** workflow in the **Codomyrmex** skill to ACTION...
```

| Workflow | Trigger | File |
|----------|---------|------|
| **codomyrmexVerify** | "/codomyrmexVerify", "verify codomyrmex", "audit tools" | `Workflows/codomyrmexVerify.md` |
| **codomyrmexTrust** | "/codomyrmexTrust", "trust codomyrmex", "trust all" | `Workflows/codomyrmexTrust.md` |

## Workflows

### Analyze & Test

```bash
list_modules → module_info → analyze_python → run_tests
```

### Code Review

```bash
git_status → git_diff → search_codebase → analyze_python
```

### PAI Health Check

```bash
pai_status → pai_awareness → list_modules
```

## Knowledge Scope

| Domain | Modules |
|--------|---------|
| Core Infrastructure | `logging_monitoring`, `config_management`, `environment_setup`, `events`, `exceptions`, `utils`, `schemas` |
| AI & Agents | `agents`, `llm`, `model_context_protocol`, `orchestrator`, `prompt_engineering`, `cerebrum`, `agentic_memory` |
| Code & Analysis | `coding` (incl. `parsers.tree_sitter`), `static_analysis`, `documentation`, `git_operations`, `ci_cd_automation/build`, `testing`, `validation` |
| Data & Storage | `database_management`, `vector_store`, `cache`, `serialization`, `data_lineage`, `data_visualization`, `graph_rag` |
| Security | `security`, `auth`, `encryption`, `privacy`, `defense`, `identity`, `wallet` |
| Infrastructure | `cloud`, `containerization`, `deployment`, `ci_cd_automation`, `networking`, `telemetry`, `performance`, `metrics` |
| Domain-Specific | `bio_simulation`, `finance`, `logistics`, `spatial`, `education`, `meme`, `embodiment` |
