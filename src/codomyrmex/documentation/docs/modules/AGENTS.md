# Codomyrmex Modules -- Agent Integration Overview

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document is the top-level agent integration guide for all codomyrmex modules. Each module subdirectory contains its own `AGENTS.md` with detailed MCP tool tables, parameter schemas, and trust classifications.

## Agent Access Patterns

Agents interact with codomyrmex modules through three channels:

1. **MCP Tools** (primary) -- Auto-discovered via `@mcp_tool` decorators in each module's `mcp_tools.py`. Currently 118 modules expose ~303 tools.
2. **Direct Python Import** -- For modules without MCP tools, agents import classes directly (e.g., `from codomyrmex.compression import compress`).
3. **CLI** -- The `codomyrmex` CLI exposes module functionality as shell commands.

## Trust Gateway

All MCP tools pass through the Trust Gateway before execution.

| Trust Level | Description | Tools |
|-------------|-------------|-------|
| **Safe** | Read-only, no side effects | ~231 tools (majority) |
| **Destructive** | Writes, executes, or modifies state | 4 tools: `write_file`, `run_command`, `run_tests`, `call_module_function` |

Trust elevation: UNTRUSTED --> VERIFIED (`/codomyrmexVerify`) --> TRUSTED (`/codomyrmexTrust`)

## MCP Tool Summary by Module

### High-Tool-Count Modules (10+ tools)

| Module | Tool Count | Key Tools |
|--------|-----------|-----------|
| [git_operations](git_operations/AGENTS.md) | 35 | git_clone, git_commit, git_push, git_pull, git_branch, git_merge, git_diff, ... |
| [git_analysis](git_analysis/AGENTS.md) | 16 | git_analysis_commit_history, git_analysis_contributor_stats, git_analysis_file_changes, ... |
| [email](email/AGENTS.md) | 12 | agentmail_send_message, agentmail_list_messages, gmail_send_message, gmail_list_messages, ... |
| [formal_verification](formal_verification/AGENTS.md) | 8 | clear_model, add_item, delete_item, replace_item, get_model, solve_model, ... |

### Medium-Tool-Count Modules (3-9 tools)

| Module | Tool Count | Key Tools |
|--------|-----------|-----------|
| [skills](skills/AGENTS.md) | 7 | skills_list, skills_invoke, skills_search, ... |
| [calendar_integration](calendar_integration/AGENTS.md) | 5 | calendar_list_events, calendar_create_event, calendar_get_event, calendar_delete_event, calendar_update_event |
| [coding](coding/AGENTS.md) | 5 | code_execute, code_list_languages, code_review_file, code_review_project, code_debug |
| [operating_system](operating_system/AGENTS.md) | 6 | OS-level operations across Linux, Mac, and Windows |
| [cache](cache/AGENTS.md) | 4 | cache_get, cache_set, cache_delete, cache_stats |
| [containerization](containerization/AGENTS.md) | 4 | container_runtime_status, container_build, container_list, container_security_scan |
| [llm](llm/AGENTS.md) | 4 | generate_text, list_local_models, query_fabric_metadata, ... |
| [prompt_engineering](prompt_engineering/AGENTS.md) | 4 | Prompt template CRUD |
| [vector_store](vector_store/AGENTS.md) | 4 | Vector embedding operations |
| [agentic_memory](agentic_memory/AGENTS.md) | 3 | memory_put, memory_get, memory_search |
| [agents](agents/AGENTS.md) | 3 | execute_agent, list_agents, get_agent_memory |
| [api](api/AGENTS.md) | 3 | api_list_endpoints, api_get_spec, api_health_check |
| [auth](auth/AGENTS.md) | 3 | auth_validate_token, auth_list_permissions, auth_check_permission |
| [ci_cd_automation](ci_cd_automation/AGENTS.md) | 3 | ci_list_pipelines, ci_trigger_pipeline, ci_get_pipeline_status |
| [cloud](cloud/AGENTS.md) | 3 | list_cloud_instances, list_s3_buckets, upload_file_to_s3 |
| [collaboration](collaboration/AGENTS.md) | 3 | swarm_submit_task, pool_status, list_agents |
| [config_management](config_management/AGENTS.md) | 3 | get_config, set_config, validate_config |
| [crypto](crypto/AGENTS.md) | 3 | hash_data, verify_hash, generate_key |
| [database_management](database_management/AGENTS.md) | 3 | Database operations |
| [deployment](deployment/AGENTS.md) | 3 | Deployment orchestration |
| [documents](documents/AGENTS.md) | 3 | Document transformation |
| [events](events/AGENTS.md) | 3 | emit_event, list_event_types, get_event_history |
| [feature_flags](feature_flags/AGENTS.md) | 3 | Feature flag operations |
| [model_context_protocol](model_context_protocol/AGENTS.md) | 3 | inspect_server, list_registered_tools, get_tool_schema |
| [model_ops](model_ops/AGENTS.md) | 3 | ML model operations |
| [search](search/AGENTS.md) | 3 | search_documents, search_index_query, search_fuzzy |
| [security](security/AGENTS.md) | 3 | scan_vulnerabilities, scan_secrets, audit_code_security |
| [serialization](serialization/AGENTS.md) | 3 | Serialization operations |
| [static_analysis](static_analysis/AGENTS.md) | 3 | Static analysis tools |
| [system_discovery](system_discovery/AGENTS.md) | 3 | health_check, list_modules, dependency_tree |
| [terminal_interface](terminal_interface/AGENTS.md) | 3 | Terminal output operations |
| [tree_sitter](tree_sitter/AGENTS.md) | 3 | AST parsing tools |
| [utils](utils/AGENTS.md) | 3 | Utility operations |
| [validation](validation/AGENTS.md) | 3 | validate_schema, validate_config, validation_summary |

### Low-Tool-Count Modules (1-2 tools)

| Module | Tool Count | Key Tools |
|--------|-----------|-----------|
| [audio](audio/AGENTS.md) | 2 | audio_get_capabilities, audio_list_voices |
| [cerebrum](cerebrum/AGENTS.md) | 2 | query_knowledge_base, add_case_reference |
| [cli](cli/AGENTS.md) | 2 | CLI operations |
| [concurrency](concurrency/AGENTS.md) | 2 | Concurrency operations |
| [data_visualization](data_visualization/AGENTS.md) | 2 | generate_chart, export_dashboard |
| [docs_gen](docs_gen/AGENTS.md) | 2 | generate_module_docs, audit_rasp_compliance |
| [encryption](encryption/AGENTS.md) | 2 | Encryption operations |
| [environment_setup](environment_setup/AGENTS.md) | 2 | Environment validation |
| [ide](ide/AGENTS.md) | 2 | IDE integration |
| [maintenance](maintenance/AGENTS.md) | 2 | maintenance_health_check, maintenance_list_tasks |
| [orchestrator](orchestrator/AGENTS.md) | 2 | get_scheduler_metrics, analyze_workflow_dependencies |
| [performance](performance/AGENTS.md) | 2 | performance_check_regression, performance_compare_benchmarks |
| [plugin_system](plugin_system/AGENTS.md) | 2 | plugin_scan_entry_points, plugin_resolve_dependencies |
| [scrape](scrape/AGENTS.md) | 2 | scrape_extract_content, scrape_text_similarity |
| [templating](templating/AGENTS.md) | 2 | Templating operations |
| [testing](testing/AGENTS.md) | 2 | Test runner operations |
| [tool_use](tool_use/AGENTS.md) | 2 | Tool operations |
| [logging_monitoring](logging_monitoring/AGENTS.md) | 1 | logging_format_structured |
| [relations](relations/AGENTS.md) | 1 | relations_score_strength |

### No MCP Tools (direct Python import only)

bio_simulation, compression, dark, defense, dependency_injection, edge_computing, embodiment, evolutionary_ai, examples, exceptions, finance, fpf, graph_rag, identity, logistics, market, meme, module_template, networking, networks, physical_management, privacy, quantum, release, simulation, spatial, telemetry, tests, video, wallet, website

## PAI Phase Mapping

| PAI Phase | Primary Modules |
|-----------|----------------|
| OBSERVE | system_discovery, git_operations, search, git_analysis |
| THINK | cerebrum, agents (ThinkingAgent) |
| PLAN | orchestrator, logistics |
| BUILD | coding, agents (ai_code_editing) |
| EXECUTE | agents (all providers), git_operations |
| VERIFY | static_analysis, security, testing, validation |
| LEARN | agentic_memory, logging_monitoring |

## Navigation

- **Module index**: [README.md](README.md)
- **Technical specs**: [SPEC.md](SPEC.md)
- **Source modules**: [src/codomyrmex/](../../../src/codomyrmex/)
