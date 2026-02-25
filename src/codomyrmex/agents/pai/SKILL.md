---
name: Codomyrmex
description: Full-spectrum coding workspace skill providing 167 MCP tools across 32 modules. USE WHEN user says 'verify codomyrmex', 'codomyrmexVerify', 'audit codomyrmex', 'trust codomyrmex', 'codomyrmexTrust', 'trust tools', 'enable destructive tools', 'check pai status', 'codomyrmex tools', 'codomyrmex analyze', 'codomyrmex search', 'codomyrmex memory', 'codomyrmex docs', 'codomyrmex status', 'codomyrmex git', 'codomyrmex security', 'codomyrmex ai', 'codomyrmex code', 'codomyrmex data', 'codomyrmex deploy', 'codomyrmex test', or uses any 'codomyrmex' automation tools.
---
# Codomyrmex Skill for PAI

**Version**: 1.0.3 | **Type**: Infrastructure Skill | **MCP**: `codomyrmex-mcp-server` | **Skills**: 15 | **Tools**: 167

## Description

Full-spectrum coding workspace skill providing 167 MCP tools across 32 auto-discovered modules for AI-assisted development, code analysis, testing, documentation generation, and workflow automation. Access via MCP protocol or direct Python calls.

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

## Tools (167)

Auto-discovered from 32 modules via `pkgutil` scan of all `mcp_tools` submodules. 163 safe + 4 destructive.

| Tool | Category | Description |
|------|----------|-------------|
| `codomyrmex.add_case_reference` | Cerebrum | Store intelligence context into the CaseBase |
| `codomyrmex.add_item` | Formal Verification | Add a Z3 expression to the constraint model |
| `codomyrmex.analyze_file` | Code Analysis | Analyze a single file |
| `codomyrmex.analyze_project` | Code Analysis | Analyze an entire project |
| `codomyrmex.analyze_python` | Code Analysis | Analyze a Python file for structure and metrics |
| `codomyrmex.analyze_workflow_dependencies` | Orchestrator | Analyze a workflow DAG for cyclic dependencies |
| `codomyrmex.apply_stash` | General | Apply stashed changes |
| `codomyrmex.ask` | LLM | Ask a question to an LLM provider |
| `codomyrmex.audit_code_security` | Security | Audit code quality and security for a file or directory |
| `codomyrmex.audit_rasp_compliance` | Documentation | Audit repository for RASP compliance |
| `codomyrmex.call_module_function` | General | Call any public function from any Codomyrmex module |
| `codomyrmex.checksum_file` | Data | Calculate file checksum (md5, sha1, sha256) |
| `codomyrmex.clear_model` | Formal Verification | Remove all items from the constraint model |
| `codomyrmex.clone_repository` | General | Clone a Git repository |
| `codomyrmex.code_debug` | Coding | Analyze an error and suggest fixes |
| `codomyrmex.code_execute` | Coding | Execute code in a sandboxed environment |
| `codomyrmex.code_list_languages` | Coding | List supported programming languages |
| `codomyrmex.code_review_file` | Coding | Analyze a Python file for quality and complexity |
| `codomyrmex.code_review_project` | Coding | Analyze a project for code quality metrics |
| `codomyrmex.commit_changes` | General | Commit staged changes |
| `codomyrmex.container_build` | Containerization | Build container images using Docker |
| `codomyrmex.container_list` | Containerization | List running containers |
| `codomyrmex.container_runtime_status` | Containerization | Check container runtime availability |
| `codomyrmex.container_security_scan` | Containerization | Scan a container image for vulnerabilities |
| `codomyrmex.create_ascii_art` | General | Create simple ASCII art for text |
| `codomyrmex.create_bar_chart` | Data Visualization | Generate a bar chart |
| `codomyrmex.create_branch` | General | Create and switch to a new Git branch |
| `codomyrmex.create_commit_timeline_diagram` | Git | Create a commit timeline diagram (Mermaid) |
| `codomyrmex.create_git_branch_diagram` | Git | Create a Git branch diagram (Mermaid) |
| `codomyrmex.create_git_workflow_diagram` | Git | Create a Git workflow diagram (Mermaid) |
| `codomyrmex.create_line_plot` | Data Visualization | Generate a line plot |
| `codomyrmex.create_pie_chart` | Data Visualization | Generate a pie chart |
| `codomyrmex.create_repository_structure_diagram` | Git | Create a repository structure diagram (Mermaid) |
| `codomyrmex.create_tag` | General | Create a Git tag |
| `codomyrmex.delete_item` | Formal Verification | Delete an item from the constraint model |
| `codomyrmex.dependency_tree` | System Discovery | Show module dependency tree |
| `codomyrmex.emit_event` | Events | Emit an event to the event bus |
| `codomyrmex.execute_agent` | Agents | Execute an agent conversation |
| `codomyrmex.execute_code` | General | Execute code in a sandboxed Docker environment |
| `codomyrmex.export_dashboard` | Data Visualization | Export a comprehensive HTML dashboard |
| `codomyrmex.generate_chart` | Data Visualization | Generate a visualization chart |
| `codomyrmex.generate_documentation` | General | Generate documentation for modules |
| `codomyrmex.generate_key` | Crypto | Generate a cryptographic key |
| `codomyrmex.generate_module_docs` | Documentation | Generate RASP docs for a module |
| `codomyrmex.generate_report` | Visualization | Generate a report |
| `codomyrmex.generate_text` | LLM | Generate text using an LLM provider |
| `codomyrmex.get_agent_memory` | Agents | Retrieve agent interaction logs |
| `codomyrmex.get_commit_history` | General | Get recent commit history |
| `codomyrmex.get_config` | Config Management | Retrieve a configuration value |
| `codomyrmex.get_current_branch` | General | Get the current Git branch name |
| `codomyrmex.get_event_history` | Events | Retrieve recent event history |
| `codomyrmex.get_last_trace` | Agents | Retrieve the most recent reasoning trace |
| `codomyrmex.get_model` | Formal Verification | Retrieve current constraint model |
| `codomyrmex.get_module_readme` | File Ops | Read README.md or SPEC.md for any module |
| `codomyrmex.get_scheduler_metrics` | Orchestrator | Get AsyncScheduler metrics |
| `codomyrmex.get_status` | General | Get Git repository status |
| `codomyrmex.get_thinking_depth` | Agents | Get ThinkingAgent reasoning depth |
| `codomyrmex.get_tool_schema` | MCP | Get JSON schema for an MCP tool |
| `codomyrmex.git_check_availability` | Git Operations | Check if git is available |
| `codomyrmex.git_clone` | Git Operations | Clone a git repository |
| `codomyrmex.git_commit` | Git Operations | Stage files and create a commit |
| `codomyrmex.git_create_branch` | Git Operations | Create a new branch |
| `codomyrmex.git_current_branch` | Git Operations | Get current branch name |
| `codomyrmex.git_diff` | Git | Get git diff for changes |
| `codomyrmex.git_init` | Git Operations | Initialize a new git repository |
| `codomyrmex.git_is_repo` | Git Operations | Check if directory is a git repo |
| `codomyrmex.git_log` | Git Operations | Get recent commit history |
| `codomyrmex.git_pull` | Git Operations | Pull latest changes from remote |
| `codomyrmex.git_push` | Git Operations | Push local commits to remote |
| `codomyrmex.git_repo_status` | Git Operations | Get repository status |
| `codomyrmex.git_status` | Git | Get git repository status |
| `codomyrmex.git_switch_branch` | Git Operations | Switch to a different branch |
| `codomyrmex.hash_data` | Crypto | Compute a cryptographic hash |
| `codomyrmex.health_check` | System Discovery | Run a health check |
| `codomyrmex.initialize_git_repository` | Git | Initialize a new Git repository |
| `codomyrmex.inspect_server` | MCP | Inspect MCP server state |
| `codomyrmex.invalidate_cache` | General | Invalidate dynamic tool discovery cache |
| `codomyrmex.json_query` | Data | Read and query a JSON file |
| `codomyrmex.list_agents` | Agents | List all available AI agents |
| `codomyrmex.list_cloud_instances` | Cloud | List cloud VM instances |
| `codomyrmex.list_directory` | File Ops | List directory contents |
| `codomyrmex.list_event_types` | Events | List registered event types |
| `codomyrmex.list_local_models` | LLM | List local Ollama models |
| `codomyrmex.list_module_functions` | File Ops | List public functions in a module |
| `codomyrmex.list_modules` | System Discovery | List all registered modules |
| `codomyrmex.list_registered_tools` | MCP | List all registered MCP tools |
| `codomyrmex.list_s3_buckets` | Cloud | List S3 storage buckets |
| `codomyrmex.list_stashes` | File Ops | List all stashes |
| `codomyrmex.list_tags` | File Ops | List all Git tags |
| `codomyrmex.list_workflows` | General | List available workflows |
| `codomyrmex.logging_format_structured` | Logging | Format log entry as structured JSON |
| `codomyrmex.maintenance_health_check` | Maintenance | Run maintenance health check |
| `codomyrmex.maintenance_list_tasks` | Maintenance | List maintenance tasks |
| `codomyrmex.memory_get` | Agentic Memory | Retrieve a memory by ID |
| `codomyrmex.memory_put` | Agentic Memory | Store a new memory entry |
| `codomyrmex.memory_search` | Agentic Memory | Search memories by query |
| `codomyrmex.merge_branch` | General | Merge a source branch |
| `codomyrmex.module_info` | General | Get module info (docstring, exports) |
| `codomyrmex.pai_awareness` | PAI | Get PAI awareness data |
| `codomyrmex.pai_status` | PAI | Get PAI status and inventory |
| `codomyrmex.performance_check_regression` | Performance | Check benchmark for regressions |
| `codomyrmex.performance_compare_benchmarks` | Performance | Compare two benchmark values |
| `codomyrmex.plugin_resolve_dependencies` | Plugins | Resolve plugin dependencies |
| `codomyrmex.plugin_scan_entry_points` | Plugins | Scan for installed plugins |
| `codomyrmex.pull_changes` | General | Pull from remote |
| `codomyrmex.push_changes` | General | Push to remote |
| `codomyrmex.query_fabric_metadata` | LLM | Query Fabric integration metadata |
| `codomyrmex.query_knowledge_base` | Cerebrum | Semantic retrieval from CaseBase |
| `codomyrmex.read_file` | File Ops | Read file contents with metadata |
| `codomyrmex.rebase_branch` | General | Rebase current branch |
| `codomyrmex.relations_score_strength` | Relations | Score relationship strength |
| `codomyrmex.replace_item` | Formal Verification | Replace an item in the constraint model |
| `codomyrmex.run_command` | Execution | Execute a shell command safely |
| `codomyrmex.run_tests` | Execution | Run pytest for a module or project |
| `codomyrmex.scan_secrets` | Security | Scan a file for leaked secrets |
| `codomyrmex.scan_vulnerabilities` | Security | Scan for security vulnerabilities |
| `codomyrmex.scrape_extract_content` | Scrape | Extract structured content from HTML |
| `codomyrmex.scrape_text_similarity` | Scrape | Compute text similarity |
| `codomyrmex.search_codebase` | Code Analysis | Search for patterns in code |
| `codomyrmex.search_documents` | Search | Full-text search across strings |
| `codomyrmex.search_fuzzy` | Search | Find best fuzzy match |
| `codomyrmex.search_index_query` | Search | Create search index and query |
| `codomyrmex.search_memory` | Code Analysis | Search agentic memory |
| `codomyrmex.set_config` | Config Management | Set a configuration value |
| `codomyrmex.set_thinking_depth` | Agents | Set reasoning depth |
| `codomyrmex.solve_model` | Formal Verification | Execute Z3 solver on model |
| `codomyrmex.stash_changes` | General | Stash current changes |
| `codomyrmex.switch_branch` | General | Switch to an existing branch |
| `codomyrmex.think` | Agents | Run Chain-of-Thought reasoning |
| `codomyrmex.upload_file_to_s3` | Cloud | Upload file to S3 storage |
| `codomyrmex.validate_config` | Config Management | Validate configuration |
| `codomyrmex.verify_hash` | Crypto | Verify data matches expected hash |
| `codomyrmex.write_file` | File Ops | Write content to a file |

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
| `codomyrmexVerify` | Verify all capabilities (runs /codomyrmexVerify workflow) |
| `codomyrmexTrust` | Trust all tools (runs /codomyrmexTrust workflow) |

## Algorithm Phase Mapping

| Phase | Tools |
|-------|-------|
| **OBSERVE** | `list_modules`, `module_info`, `list_directory`, `dependency_tree`, `health_check` |
| **THINK** | `analyze_python`, `search_codebase`, `think`, `search_documents`, `search_fuzzy` |
| **PLAN** | `read_file`, `json_query`, `get_config`, `analyze_workflow_dependencies` |
| **BUILD** | `write_file`, `generate_module_docs`, `code_execute`, `generate_text` |
| **EXECUTE** | `run_command`, `run_tests`, `execute_agent`, `container_build` |
| **VERIFY** | `git_status`, `git_diff`, `checksum_file`, `solve_model`, `audit_code_security` |
| **LEARN** | `pai_awareness`, `pai_status`, `memory_put`, `emit_event` |

## Skill Domains (15 Total)

| Skill | Domain | Key Triggers |
|-------|--------|-------------|
| `codomyrmexVerify` | Capability Audit | "verify codomyrmex", "audit tools" |
| `codomyrmexTrust` | Trust Management | "trust codomyrmex", "enable destructive" |
| `codomyrmexAnalyze` | Code Analysis | "analyze project", "code review" |
| `codomyrmexMemory` | Memory | "add to memory", "remember this" |
| `codomyrmexSearch` | Search | "search codebase", "grep pattern" |
| `codomyrmexDocs` | Documentation | "get module docs", "module readme" |
| `codomyrmexStatus` | Status | "system status", "health check" |
| `CodomyrmexGit` | Version Control | "git analysis", "commit timeline" |
| `CodomyrmexSecurity` | Security & Crypto | "security scan", "crypto key" |
| `CodomyrmexAI` | AI & Agents | "reasoning trace", "thinking agent" |
| `CodomyrmexCode` | Code Execution | "execute code", "sandbox code" |
| `CodomyrmexData` | Data & Visualization | "bar chart", "fuzzy search" |
| `CodomyrmexDeploy` | Infrastructure | "docker build", "list instances" |
| `CodomyrmexTest` | Testing | "run tests", "benchmark" |

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

## Knowledge Scope

| Domain | Modules |
|--------|---------|
| Core Infrastructure | `logging_monitoring`, `config_management`, `environment_setup`, `events`, `exceptions`, `utils`, `schemas`, `concurrency`, `compression`, `serialization`, `streaming` |
| AI & Agents | `agents`, `llm`, `model_context_protocol`, `orchestrator`, `prompt_engineering`, `cerebrum`, `agentic_memory`, `inference_optimization`, `model_ops`, `model_registry`, `model_evaluation`, `prompt_testing` |
| Code & Analysis | `coding`, `static_analysis`, `tree_sitter`, `documentation`, `git_operations`, `build_synthesis`, `testing`, `validation`, `pattern_matching`, `dependency_injection` |
| Data & Processing | `database_management`, `vector_store`, `cache`, `data_lineage`, `data_visualization`, `graph_rag`, `feature_store`, `feature_flags`, `search`, `documents`, `fpf`, `scrape` |
| Security & Identity | `security`, `auth`, `encryption`, `privacy`, `defense`, `identity`, `wallet`, `governance` |
| Infrastructure & Ops | `cloud`, `containerization`, `deployment`, `ci_cd_automation`, `networking`, `telemetry`, `performance`, `metrics`, `edge_computing`, `service_mesh`, `scheduler`, `rate_limiting`, `cost_management`, `chaos_engineering`, `migration`, `observability_dashboard` |
| UI & Interface | `cli`, `website`, `terminal_interface`, `ide`, `visualization`, `video`, `audio`, `multimodal`, `accessibility`, `i18n`, `templating`, `notification` |
| Domain & Simulation | `bio_simulation`, `finance`, `logistics`, `spatial`, `education`, `meme`, `embodiment`, `evolutionary_ai`, `quantum`, `smart_contracts`, `market`, `dark`, `physical_management`, `relations`, `collaboration` |
| System & Meta | `system_discovery`, `plugin_system`, `skills`, `tool_use`, `tools`, `module_template`, `examples`, `tests`, `workflow_testing`, `api` |
