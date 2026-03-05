---
task: "Expand test_project to comprehensive codomyrmex exemplar covering 28 modules"
slug: "20260305-093700_test-project-module-expansion"
effort: "Advanced"
phase: "build"
progress: "0/28"
mode: "ALGORITHM"
started: "2026-03-05T09:37:00"
updated: "2026-03-05T09:40:00"
---

## Context

`projects/test_project/` is the authoritative reference implementation ("Mega-Seed") for codomyrmex integration patterns. Adding 6 new source modules + 6 test files + updating 5 existing files to expand coverage from ~12 to ~28 modules.

### Risks
- Crypto module uses `graphy.hashing` subpath not top-level `hash_data`
- Scrape module uses `Scraper` class not standalone functions
- git_analysis exports only `GitHistoryAnalyzer` (not 16 MCP tool names at top level)
- LLM module exports `OllamaManager` not `generate_text`/`list_local_models`
- formal_verification requires z3 — needs skipif guard
- Ollama must not be required for LLM tests to pass in CI

## Criteria

- [ ] ISC-1: `src/agent_brain.py` created with HAS_AGENT_MODULES = True
- [ ] ISC-2: AgentBrain class has list_available_agents(), remember(), recall(), score_relation()
- [ ] ISC-3: AgentBrain imports from codomyrmex.agents and codomyrmex.agentic_memory
- [ ] ISC-4: `src/git_workflow.py` created with HAS_GIT_MODULES = True
- [ ] ISC-5: GitWorkflow class has inspect_repo() and analyze_history()
- [ ] ISC-6: GitWorkflow imports from git_operations and git_analysis using real APIs
- [ ] ISC-7: `src/knowledge_search.py` created with HAS_SEARCH_MODULES = True
- [ ] ISC-8: KnowledgeSearch has build_index(), full_text_search(), fuzzy_match(), verify_constraints()
- [ ] ISC-9: KnowledgeSearch imports from codomyrmex.search, scrape, formal_verification
- [ ] ISC-10: `src/security_audit.py` created with HAS_SECURITY_MODULES = True
- [ ] ISC-11: SecurityAudit has audit_path(), hash_and_verify(), system_health(), project_deps()
- [ ] ISC-12: SecurityAudit imports security, crypto.graphy.hashing, maintenance, system_discovery
- [ ] ISC-13: `src/mcp_explorer.py` created with HAS_MCP_MODULES = True
- [ ] ISC-14: MCPExplorer has list_tools(), discover_skills(), scan_plugins()
- [ ] ISC-15: MCPExplorer imports model_context_protocol, skills, plugin_system
- [ ] ISC-16: `src/llm_inference.py` created with HAS_LLM_MODULES = True
- [ ] ISC-17: LLMInference has list_models(), swarm_task(), agent_pool_status()
- [ ] ISC-18: LLMInference imports codomyrmex.llm and codomyrmex.collaboration
- [ ] ISC-19: 6 test files created with proper zero-mock test classes
- [ ] ISC-20: External-service tests use @pytest.mark.skipif at class level
- [ ] ISC-21: All HAS_* flag tests assert flag is True
- [ ] ISC-22: run_demo.py extended with 6 new demo_*() functions
- [ ] ISC-23: src/__init__.py updated to export new modules
- [ ] ISC-24: README.md, SPEC.md, AGENTS.md updated with new module coverage
- [ ] ISC-25: No unittest.mock, MagicMock, monkeypatch in new test files
- [ ] ISC-26: All existing 13 test classes continue to pass (no regressions)
- [ ] ISC-27: New test files collectible without import errors
- [ ] ISC-28: Each source module has module-level docstring describing integration targets

## Decisions

- Used actual verified module APIs (GitHistoryAnalyzer, Scraper class, crypto.graphy.hashing)
- Skipped cerebrum/relations (not needed — agents module sufficient for agent_brain.py)
- LLM module: OllamaManager + LLMConfig as integration points (no Ollama required for imports)
- Formal verification: ConstraintSolver + SolverStatus (z3 optional via skipif)

## Verification
