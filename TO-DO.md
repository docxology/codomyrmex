# Codomyrmex Project Roadmap & To-Do

**Status**: Active | **Last Updated**: February 18, 2026 | **Current**: v0.1.7 | **Target**: v0.4.0

v0.1.8–0.1.9 harden foundations (async orchestration, observability, PAI workflows, CLI diagnostics).
v0.2.0 certifies production-grade agent infrastructure.
v0.3.0 layers cognitive architecture. v0.4.0 delivers swarm orchestration.

---

## ✅ Completed Releases (v0.1.3 – v0.1.7)

| Version | Theme | Highlights |
|---------|-------|------------|
| **v0.1.3** | Foundation Hardening | RASP standardization, `uv` migration, 84 pass / 2 skip |
| **v0.1.4** | Zero-Mock Certification | `EphemeralServer` replaces httpbin, real LLM tests, `pytest-benchmark` |
| **v0.1.5** | Module Refactoring | 79/79 `__all__` exports, 0 cross-layer violations / 291 edges |
| **v0.1.6** | Agent & Memory Foundations | `AgentProtocol`, `AgentMessage`, `ToolRegistry.from_mcp()`, `VectorStoreMemory`, `EventBus.emit_typed()`, `OrchestratorEvents`, 71 new tests |
| **v0.1.7** | Documentation Audit & MCP Plumbing | Version sync to 0.1.7, module count →82, 62 dead scripts deleted, 6 `mcp_tools.py` registered, `MCPClient` (355 lines), 29 MCP tests, `ToolRegistry` thread-safe, 7 test failures→0, deprecated `get_event_loop` fixed |

<details>
<summary><strong>v0.1.7 — Detailed Record</strong></summary>

**Test Baseline**: 8205 passed, 245 skipped, 7 xfailed, 0 failures (497s).

**MCP Sprint**: 6 `mcp_tools.py` files (git_operations, containerization, coding, search, formal_verification, logistics). Auto-discovery in `discovery.py`. `MCPClient` with stdio + HTTP transports. 535 total tools. Full zero-mock test suite: `test_mcp_smoke.py` (13), `test_mcp_client.py` (9), `test_mcp_discovery.py` (7), `test_mcp_server.py`, `test_mcp_tools.py`, `test_mcp_bridge.py`, `test_mcp_http_and_errors.py` (15).

**Thread Safety**: `ToolRegistry._lock` added with proper usage in register/get/list/execute.

**Script Refactoring**: 7 audit/update scripts refactored to thin orchestrators → `maintenance` library. 62 dead documentation scripts deleted.

**Doc Sync**: Version 0.1.7 synchronized across 12 files. Module count corrected (78/80/82+/83 → 82) in 15+ files. 21 missing modules added to AGENTS.md.
</details>

---

## 🔧 v0.1.8 — Async-First Orchestration & Observability

**Theme**: "Concurrent Backbone" | **Scope**: 4 work streams, ~15 deliverables

> **Codebase Baseline (Feb 2026)**:
>
> - `ParallelRunner` (328 lines): thread-pool based (`ThreadPoolExecutor`), wraps via `asyncio.to_thread()` — no native async.
> - `Workflow.run()` (645 lines): async topological sort, `RetryPolicy`, semaphore concurrency, EventBus, conditional execution. Uses `asyncio.gather()` per level, not `TaskGroup`.
> - `orchestrator/scheduler/` (4 files): `Scheduler` with heapq priority, cron/interval/once triggers, thread-pool executor, `threading.Lock`.
> - `orchestrator/retry_policy.py` (163 lines): `RetryPolicy`, `PipelineRetryExecutor` (sync + async), exponential backoff, jitter, dead-letter routing.
> - `logging_monitoring/` (13 files): `json_formatter.py`, `logger_config.py`, `rotation.py`, `audit_logger.py`, `performance.py`. No WebSocket handler. No `enable_structured_json()` toggle.
> - `EventBus` has `emit_typed()`/`subscribe_typed()` + `threading.RLock`. No logging pipeline bridge.
> - `__getattr__` lazy loading in main `__init__.py:112`. Heavy imports: `matplotlib` (~200ms), `chromadb` (~300ms), `sentence_transformers` (~400ms).

### Stream 1: Orchestrator v2 (async-first)

| Deliverable | File | Description |
|-------------|------|-------------|
| `AsyncParallelRunner` | `orchestrator/async_runner.py` (NEW) | Native `asyncio.TaskGroup` (3.11+) parallel execution. Inputs: list of async callables + optional dependency DAG. `asyncio.Semaphore` for concurrency limiting. `fail_fast` via `TaskGroup` exception propagation. |
| `Workflow.run()` upgrade | `orchestrator/workflow.py:279–450` | Replace `asyncio.gather()` with `TaskGroup` for structured concurrency within topological levels. Preserve existing `RetryPolicy` integration and conditional task execution. |
| Unified retry | `orchestrator/retry_policy.py` | Wire `PipelineRetryExecutor` into `Workflow.run()` — currently `Workflow` has its own inline retry logic. Consolidate to single retry mechanism. Extract standalone `@with_retry` decorator from `PipelineRetryExecutor.execute_async()`. |
| `AsyncScheduler` | `orchestrator/scheduler/scheduler.py` | Add `priority: int` to `Job` model. New `AsyncScheduler` variant using `TaskGroup` instead of `ThreadPoolExecutor`. Wire scheduler lifecycle events into `EventBus`. |

### Stream 2: Observability Pipeline

| Deliverable | File | Description |
|-------------|------|-------------|
| WebSocket log handler | `logging_monitoring/ws_handler.py` (NEW) | `WebSocketLogHandler(logging.Handler)` for real-time structured log streaming. `asyncio.Queue` bridges sync `logging.emit()` → async WebSocket send via `aiohttp`. Filters: level, module, event type. |
| Structured JSON toggle | `logging_monitoring/logger_config.py` | `enable_structured_json(logger_name=None)` replaces default handler with `JsonFormatter`. `configure_all(level, json_mode, ws_endpoint)` convenience function. |
| Event→log bridge | `logging_monitoring/event_bridge.py` (NEW) | `EventLoggingBridge` subscribes to `EventBus.subscribe_typed()`, logs all agent/workflow/MCP events as structured JSON via `logging.getLogger('codomyrmex.events')`. Auto-enriches with correlation IDs from `OrchestratorEvents`. |
| Scheduler events | `orchestrator/orchestrator_events.py` | Add `scheduler_job_started()`, `scheduler_job_completed()`, `scheduler_job_failed()` factories (existing pattern: 8 workflow/task factories). |

### Stream 3: Performance Baselines

| Deliverable | File | Description |
|-------------|------|-------------|
| CLI startup benchmark | `scripts/benchmark_startup.py` (NEW) | Measure `codomyrmex --help` wall-clock. Target: <500ms. Identify heavy import chain: `matplotlib`, `chromadb`, `sentence_transformers`, `scipy`. |
| Module-level lazy loading | `data_visualization/__init__.py`, `agentic_memory/__init__.py`, `serialization/__init__.py`, `vector_store/__init__.py` | Add `__getattr__` lazy loading to defer `matplotlib`, `chromadb`, `pyarrow`, `sentence_transformers`. |
| API benchmarks | `performance/benchmark.py` | Time: `create_codomyrmex_mcp_server()`, `get_tool_registry()`, `_discover_dynamic_tools()`, `Workflow.run()` (10-task DAG), `Scheduler.schedule()` (100 jobs). |
| Import profiling | CI script | `python -X importtime -c "import codomyrmex"` → top-20 heaviest. Target: total <200ms. |

### Stream 4: Tests (Zero-Mock)

| Test | What it validates |
|------|-------------------|
| `test_async_runner.py` | 10 real async tasks, DAG dependency resolution, `TaskGroup` error propagation, semaphore concurrency (verify max 3) |
| `test_ws_handler.py` | WebSocket handler with real `EphemeralServer` — connect, send logs, verify receipt, filter by level |
| `test_event_bridge.py` | `EventLoggingBridge` captures `TASK_STARTED`/`COMPLETED`/`FAILED` events as structured JSON |
| `test_scheduler_async.py` | `AsyncScheduler` with 5 jobs, `TaskGroup` execution, priority ordering, trigger types |

**Gate criteria**: Full test suite 0 failures. CLI startup <500ms. Import time <200ms. Event bridge captures all lifecycle events.

---

## 🔧 v0.1.9 — PAI & Claude Code Workflow Hardening

**Theme**: "Bulletproof Workflows" | **Scope**: 5 work streams, ~25 deliverables

> **Codebase Baseline (Feb 2026)**:
>
> - 7 Claude Code workflows in `.agent/workflows/`: Analyze, Docs, Memory, Search, Status, Trust, Verify.
> - `verify_capabilities()` reports 535 tools (483 auto-discovered). MCP server healthy.
> - Trust gateway (585 lines): 3-tier model (UNTRUSTED→VERIFIED→TRUSTED), `_is_destructive()` pattern detection, `_FrozenSetProxy`. **No audit log. No input validation.**
> - `_discover_dynamic_tools()` (47 lines): **no caching** — re-imports all modules per call.
> - `concurrency/` (13 files): channels, distributed_lock, lock_manager, rate_limiter, semaphore, redis_lock. No managed async pool. No dead-letter queue.
> - `defense/` (3 files): `active.py`, `defense.py`, `rabbithole.py`. Honeytokens exist but not activated in tests.
> - CLI `core.py` (643 lines): auto-discovered module commands. **No `doctor` subcommand.**
> - `jsonschema>=4.23.0` in deps — input validation viable.

### Stream 1: PAI Bridge Hardening

| Deliverable | File | Description |
|-------------|------|-------------|
| Tool discovery cache | `agents/pai/mcp_bridge.py` | `_DYNAMIC_TOOLS_CACHE` with `threading.Lock` (v0.1.7 prereq). v0.1.9: expose `_tool_invalidate_cache()` as MCP tool + invalidation hook on module reload. Target: <100ms cached. |
| Capability response normalization | `agents/pai/mcp_bridge.py` | `verify_capabilities()` always returns `{ tools: { safe: [...], destructive: [...], total: int }, modules: { loaded: int, failed: [] }, trust: { level: str, audit_entries: int } }`. Wire to `_LazyToolSets`. |
| Error recovery envelope | `agents/pai/mcp_bridge.py` | Wrap every MCP tool handler with `try/except`. Return structured error: `{ "error": str, "error_type": str, "module": str, "suggestion": str }`. Log via `codomyrmex.mcp` logger. |
| Workflow listing tool | `agents/pai/mcp_bridge.py` | `_tool_list_workflows()`: read `.agent/workflows/*.md` YAML frontmatter → return `{ workflows: [{ name, description, filepath }] }`. |
| Cache invalidation tool | `agents/pai/mcp_bridge.py` | `_tool_invalidate_cache()`: clear `_TOOL_REGISTRY_CACHE`, force re-discovery for dev workflows. |

### Stream 2: Claude Code Workflow Integration Tests

All zero-mock, in `tests/integration/workflows/`:

| Test | Workflow | Assertion |
|------|----------|-----------|
| `test_workflow_analyze.py` | `/codomyrmexAnalyze` on `src/codomyrmex/utils/` | Valid JSON: file counts, line counts, function counts |
| `test_workflow_docs.py` | `/codomyrmexDocs` | Returns non-empty README for orchestrator, events, agents, model_context_protocol, logging_monitoring |
| `test_workflow_status.py` | `/codomyrmexStatus` | Dict with `system_status`, `pai_awareness`, `mcp_health`, `trust_level` |
| `test_workflow_trust.py` | Trust lifecycle | `verify_capabilities()` → `trust_all()` → `trusted_call_tool('list_modules')` → `reset_trust()` → verify UNTRUSTED |
| `test_workflow_verify.py` | `/codomyrmexVerify` | Dict with `modules` (≥82), `tools` (≥535), `resources`, `prompts`, `trust` |
| `test_workflow_search.py` | `/codomyrmexSearch` for `"def main"` | ≥3 matching files including `cli/core.py` |
| `test_workflow_memory.py` | `/codomyrmexMemory` | Add `"test_entry"` → recall → verify round-trip integrity |
| `test_workflow_error.py` | Invalid module name | Structured error response, no crash |

### Stream 3: CLI Doctor

New file `cli/doctor.py`, registered in `cli/core.py` via existing subparser pattern:

| Subcommand | What it checks |
|------------|----------------|
| `codomyrmex doctor` | Module imports (all 82), tool registry count, MCP server instantiation, test suite dry-run (`pytest --co -q` exit 0) |
| `--pai` | PAI skill status (`PAIBridge.get_status()`), tool count, trust state, version sync (`PAI.md` ↔ `SKILL.md` ↔ `pyproject.toml`) |
| `--workflows` | All 7 Claude Code workflows parse without error, YAML frontmatter valid, referenced tools exist in registry |
| `--rasp` | RASP completeness — leverage `scripts/audit_rasp.py` to flag modules missing README/AGENTS/SPEC/PAI |
| `--imports` | `python -X importtime` → top-10 heaviest imports, flag any >100ms |
| `--json` | Structured JSON output. Exit codes: 0=healthy, 1=warnings, 2=errors |

### Stream 4: Concurrency Hardening

| Deliverable | File | Description |
|-------------|------|-------------|
| Thread-safety audit | Multiple | `JSONFileStore.list_all()` doesn't hold lock during iteration → fix. Verify all shared-state classes. |
| `AsyncWorkerPool` | `concurrency/pool.py` (NEW) | `asyncio.TaskGroup` + `Semaphore`. Methods: `submit(coro) → Future`, `shutdown(wait=True)`, `map(func, items)`. Integrates with existing `concurrency/semaphore.py`. |
| `DeadLetterQueue` | `concurrency/dead_letter.py` (NEW) | Failed MCP tool invocations. Fields: `tool_name`, `args`, `error`, `timestamp`, `retry_count`. Persistence: `~/.codomyrmex/dead_letters.json`. Methods: `add()`, `replay()`, `purge(older_than)`. Wire into `PipelineRetryExecutor` on `DEAD_LETTER` outcome. |

### Stream 5: Security Pre-Audit

| Deliverable | File | Description |
|-------------|------|-------------|
| Trust audit log | `agents/pai/trust_gateway.py` | `_audit_log: list[dict]` on `TrustGateway`. Log: `{ timestamp, tool_name, args_hash, result_status, trust_level }`. Methods: `get_audit_log(since)`, `export_audit_log(path)`. |
| Input validation | `agents/pai/mcp_bridge.py` | MCP tool args validated against `input_schema` via `jsonschema.validate()` (dep confirmed). On failure: return `{ "error": "validation_error", "details": str }` without calling tool. |
| Honeytoken activation | `defense/active.py`, `conftest.py` | `CODOMYRMEX_TEST_MODE=1` → activate honeytoken patterns. `test_honeytoken_activation.py`: verify detection on simulated intrusion. |
| Dependency audit | CI | `uv pip audit` or equivalent in CI pipeline. Flag known CVEs in transitive deps. |

**Gate criteria**: All 7 workflows pass integration tests. `doctor` subcommand exit 0 on clean install. Trust audit log captures all tool invocations. Zero `jsonschema.ValidationError` passthrough.

---

## 🤖 v0.2.0 — "Agents Я Us"

**Theme**: "Everything Works, Everything Connects" | **Scope**: Certification release

> This release certifies that every Codomyrmex capability is accessible, tested, and production-grade
> through PAI, Claude Code, and MCP interfaces. No new cognitive features — just bulletproof plumbing.

### MCP Coverage Certification

- [ ] Every module with public functions has auto-discovered MCP tools (target: 600+ tools)
- [ ] `MCPClient` ↔ `MCPServer` full round-trip verified (both stdio and HTTP transports)
- [ ] Tool count parity: `get_total_tool_count()` matches SKILL.md tool table exactly
- [ ] MCP tool argument schemas fully typed — eliminate all `Any` in tool signatures
- [ ] `_discover_dynamic_tools()` cached and <100ms (v0.1.9 prerequisite)
- [ ] Tool category taxonomy: every tool tagged with one of {analysis, generation, execution, query, mutation}
- [ ] Rate limiting: `RateLimiter` from `concurrency/rate_limiter.py` wired into MCP server for external-facing tool invocations

### PAI Integration Certification

- [ ] All 7+ Claude Code workflows pass integration tests (from v0.1.9)
- [ ] `verify_capabilities()` returns accurate, normalized results with safe/destructive breakdown
- [ ] Full trust lifecycle tested end-to-end with audit log verification
- [ ] Skill manifest (`get_skill_manifest()`) matches actual capabilities — automated check in CI
- [ ] PAI version sync: `PAI.md` ↔ `SKILL.md` ↔ `agents/pai/__init__.py` ↔ `pyproject.toml` all `0.2.0`
- [ ] `PAIAGENTSYSTEM.md` agent type mapping: Engineer→`coding`+`git_operations`, Architect→`orchestrator`+`documentation`, QATester→`testing`+`static_analysis`. Automated mapping validation.
- [ ] PAI Algorithm phase coverage: all 8 phases have ≥2 mapped Codomyrmex modules with working MCP tools

### Logging & Observability

- [ ] Structured JSON logging toggleable across all modules via `enable_structured_json()`
- [ ] `WebSocketLogHandler` streaming verified with real WebSocket connections (from v0.1.8)
- [ ] `codomyrmex doctor` CLI fully operational with all subcommands (from v0.1.9)
- [ ] `EventBus` → logging pipeline: all agent/workflow/scheduler events observable as structured JSON
- [ ] Correlation ID propagation: every MCP tool invocation generates a trace ID visible in logs, events, and audit trail
- [ ] `logging_monitoring/dashboards/` (NEW): pre-built Grafana/JSON dashboard templates for MCP tool latency, error rates, agent activity

### Concurrency & Performance

- [ ] `AsyncParallelRunner` for truly async concurrent workflow execution (from v0.1.8)
- [ ] CLI startup <500ms, import time <200ms — enforced in CI
- [ ] All shared state thread-safe: `ToolRegistry`, `JSONFileStore`, `EventBus`, `AgentMemory`, `Scheduler`
- [ ] Performance benchmarks for all public API entry points — regression alerts in CI
- [ ] Dead-letter queue operational: failed MCP invocations captured, replayable
- [ ] Connection pooling: `HTTPClient` in `networking/` reuses sessions for repeated API calls
- [ ] Memory profiling: `tracemalloc` snapshots for long-running orchestrator workflows

### Test Suite Certification

- [ ] Full regression: **0 failures**, ≤100 skips, 0 xfails
- [ ] All async tests use `pytest-asyncio` with `asyncio_mode = auto`
- [ ] Optional-dependency tests gated behind `pytest.importorskip()`
- [ ] Coverage ≥80% on all actively maintained modules — enforced in CI
- [ ] Mutation testing: `mutmut` or `cosmic-ray` on critical paths (MCP bridge, trust gateway, retry policy)
- [ ] Load testing: MCP server handles 100 concurrent tool invocations without deadlock
- [ ] Test execution time budget: full suite <600s

### Documentation Freeze

- [ ] All 82 modules have current README.md, SPEC.md, AGENTS.md, PAI.md (RASP complete)
- [ ] CHANGELOG.md complete through v0.2.0 with proper Keep-a-Changelog format
- [ ] API reference auto-generated from docstrings (Sphinx or mkdocstrings)
- [ ] Claude Code workflow documentation in `.agent/workflows/` matches implementation
- [ ] `SKILL.md` tool table accurate and auto-validated against registry
- [ ] Architecture diagrams (Mermaid) in `SPEC.md` reflect actual module dependencies

**Gate criteria**: `codomyrmex doctor` exit 0. 0 test failures. Coverage ≥80%. MCP tool count ≥600. All workflows passing. PAI version sync validated.

---

## 🧠 v0.3.0 — "Active Inference"

**Theme**: "Thinking Agents" | **Scope**: Cognitive architecture on the hardened v0.2.0 base

> **Codebase Baseline**: `cerebrum/` has 25 .py files, `graph_rag/` has 4, `meme/` has 2, `prompt_engineering/` has 9,
> `llm/` has 29. All functional but largely unintegrated with agent core.

### Chain-of-Thought Reasoning

| Deliverable | File | Description |
|-------------|------|-------------|
| CoT prompting wrapper | `llm/chain_of_thought.py` (NEW) | Structured reasoning extraction: `think()` → `reason()` → `conclude()` pipeline. Supports step-by-step, tree-of-thought, and debate-style reasoning. Returns `ReasoningTrace` with confidence scores. |
| `ThinkingAgent` | `agents/core/thinking_agent.py` (NEW) | Extends `ReActAgent` with explicit reasoning traces. Overrides `plan()` to use CoT wrapper. Stores reasoning history in `AgentMemory`. Exposes `get_reasoning_trace()` for introspection. |
| Sliding context window | `llm/context_manager.py` (NEW) | Token-aware sliding window for unbounded conversations. Strategies: FIFO, importance-weighted, semantic similarity. Integrates with all LLM providers via `BaseLLMClient`. Configurable max tokens. |
| Reasoning MCP tools | `agents/core/mcp_tools.py` | Expose `think`, `reason`, `get_reasoning_trace` as MCP tools for PAI consumption. |

### Cerebrum + GraphRAG Integration

| Deliverable | File | Description |
|-------------|------|-------------|
| Case retrieval | `cerebrum/case_retrieval.py` (NEW) | `CaseBase` for past successful code patterns. Stores: problem→solution→outcome triples. Retrieval: similarity search via `VectorStoreMemory`. Integration: agents query case base during `plan()` phase. |
| Graph-agent bridge | `graph_rag/agent_bridge.py` (NEW) | Wires graph retrieval into agent context windows. `GraphContextProvider.get_relevant_context(query)` returns ranked subgraph snippets. Entity linking between code symbols and graph nodes. |
| Bayesian reasoning | `orchestrator/bayesian.py` (NEW) | Bayesian decision hooks for orchestrator task selection. Prior: historical task success rates. Likelihood: current context similarity. Posterior: weighted task prioritization. |
| Knowledge distillation | `cerebrum/distillation.py` (NEW) | Extract reusable patterns from agent execution traces. Store as `CaseBase` entries. Periodic distillation job via `Scheduler`. |

### Memetic Analysis

| Deliverable | File | Description |
|-------------|------|-------------|
| Anti-pattern detector | `meme/anti_pattern_detector.py` (NEW) | Detect repetitive code anti-patterns. Uses `static_analysis` + `coding/parsers` to identify: copy-paste drift, god objects, circular dependencies, dead code. Returns `AntiPatternReport` with severity and fix suggestions. |
| Concept drift tracker | `meme/drift_tracker.py` (NEW) | Track semantic drift between docs and code. Compares: docstring intent vs implementation behavior, README claims vs actual exports, SPEC requirements vs test coverage. Uses LLM for semantic comparison. |

### Prompt Engineering Integration

| Deliverable | File | Description |
|-------------|------|-------------|
| Template→agent wiring | `prompt_engineering/agent_prompts.py` (NEW) | Dynamic prompt selection based on task type (`code_review`, `bug_fix`, `feature_impl`, `refactor`). Template registry with version history. A/B testing support for prompt variants. |
| Context-aware prompts | `prompt_engineering/context.py` (NEW) | Enrich prompts with: file history (via `git_operations`), similar code (via `graph_rag`), past solutions (via `cerebrum`). Auto-truncation to fit provider token limits. |

### Security Hardening

- [ ] `wallet/key_rotation.py` (NEW): automated key rotation scheduler with configurable intervals
- [ ] `wallet/encrypted_storage.py` (NEW): AES-256-GCM encrypted credential storage with `cryptography` library
- [ ] Dependency scanning in CI/CD: `safety` or `pip-audit` in GitHub Actions workflow
- [ ] `defense/rabbithole.py` upgrade: canary token variants (DNS, HTTP, file-based)

### Tests (Zero-Mock)

| Test | Validates |
|------|-----------|
| `test_chain_of_thought.py` | CoT wrapper produces parseable `ReasoningTrace`, LLM integration via OpenRouter free tier |
| `test_thinking_agent.py` | `ThinkingAgent.plan()` includes reasoning trace, memory stores traces |
| `test_case_retrieval.py` | `CaseBase` store/retrieve round-trip, similarity ranking |
| `test_graph_agent_bridge.py` | Graph context enrichment in agent planning, entity linking |
| `test_anti_pattern_detector.py` | Detects known anti-patterns in test fixtures |
| `test_drift_tracker.py` | Identifies intentional doc-code drift in test fixtures |
| `test_prompt_selection.py` | Correct template selected for task type, context enrichment |

**Gate criteria**: ThinkingAgent produces valid reasoning traces. Case retrieval returns relevant results. Anti-pattern detector flags ≥3 known patterns in test fixtures. All new code ≥80% coverage.

---

## 🐜 v0.4.0 — "Ant Colony"

**Theme**: "Swarm Orchestration" | **Scope**: Autonomous multi-agent collaboration on thinking foundations

> **Codebase Baseline**: `collaboration/` has 18 .py files, `agents/` has 86 .py files with ReActAgent
> but no multi-agent protocol. `orchestrator/` has 26 files but no agent-to-agent coordination.
> `identity/` has 5 files. 359 test files total.

### Swarm Protocol

| Deliverable | File | Description |
|-------------|------|-------------|
| `SwarmProtocol` | `collaboration/swarm/protocol.py` (NEW) | Typed multi-agent collaboration. Roles: `Coder`, `Reviewer`, `DevOps`, `Architect`, `Tester`. Message passing via `EventBus`. Consensus mechanisms: majority vote, weighted expertise, veto. |
| `AgentPool` | `collaboration/swarm/pool.py` (NEW) | Managed agent pool with capability-based routing. Register agents with skill vectors. Route tasks to best-fit agent. Load balancing: round-robin, least-loaded, skill-match. Max pool size configurable. |
| `SwarmMessage` | `collaboration/swarm/message.py` (NEW) | Inter-agent message format extending `AgentMessage`. Fields: `sender_role`, `recipient_role`, `intent` (REQUEST/RESPONSE/BROADCAST), `thread_id` for conversation tracking. Serializable per `AgentMessage` pattern. |
| Agent identity | `identity/capability.py` (NEW) | Capability advertisement: agents declare skills, domains, and trust levels. Capability matching: task requirements → agent selection. Integrates with `identity` module's existing 5 files. |
| Swarm MCP tools | `collaboration/swarm/mcp_tools.py` (NEW) | Expose swarm operations: `create_swarm`, `assign_task`, `get_consensus`, `swarm_status` as MCP tools. |

### Self-Healing Workflows

| Deliverable | File | Description |
|-------------|------|-------------|
| Auto-diagnosis | `orchestrator/self_healing.py` (NEW) | On build/test failure: extract error, invoke `ThinkingAgent` to analyze root cause. Pattern library: missing import, type error, config mismatch, dependency conflict. Propose fix diff. |
| Config-aware retry | `orchestrator/self_healing.py` | Config fix + retry: detect config-related failures (env vars, paths, versions). Auto-adjust config and retry. Integrates with `config_management` module. |
| Diagnostics dead-letter | `orchestrator/self_healing.py` | Permanently failed tasks → structured diagnostic reports. Fields: `attempt_history`, `root_cause_analysis`, `suggested_fixes`, `related_cases` (from `CaseBase`). |

### Project-Level Context

| Deliverable | File | Description |
|-------------|------|-------------|
| `ProjectContext` | `agents/context/project.py` (NEW) | Full repo structure awareness. Auto-index: file types, module boundaries, dependency graph, git history. Methods: `get_context_for(file)`, `get_related_files(file)`, `get_module_for(file)`. |
| Repo indexer | `agents/context/indexer.py` (NEW) | `git_operations` + `coding.parsers` → automatic repo indexing. Supports: Python AST, TypeScript, Rust, Go. Incremental indexing on file change. Stored in `agentic_memory`. |
| Context-aware tool select | `agents/context/tool_selector.py` (NEW) | Given file type + task type, select optimal MCP tools. E.g., `.py` + `refactor` → `static_analysis.analyze_file` + `coding.execute_code` + `git_operations.create_branch`. |

### Meta-Agent

| Deliverable | File | Description |
|-------------|------|-------------|
| `MetaAgent` | `agents/meta/meta_agent.py` (NEW) | Self-improving agent: rewrites prompt strategies based on outcomes. Feedback loop: outcome scoring → strategy adjustment → A/B testing via `prompt_engineering`. |
| Strategy library | `agents/meta/strategies.py` (NEW) | Persistence via `agentic_memory`. Strategy: `{ name, prompt_template, success_rate, usage_count, domains }`. Methods: `select_strategy(task_type)`, `update_outcome(strategy, score)`, `retire_strategy(name)`. |
| Outcome scoring | `agents/meta/scoring.py` (NEW) | Multi-dimensional scoring: correctness (tests pass), efficiency (time taken), code quality (lint score), user satisfaction (explicit feedback). Weighted composite score. |

### Release Certification

- [ ] Full regression: 10,000+ tests, 0 failures, 0 xfails
- [ ] API stability contract: no breaking changes from v0.2.x/v0.3.x public APIs
- [ ] Performance: CLI startup <500ms, import <200ms, MCP tool registration <100ms
- [ ] MCP tool count >700 registered tools with trust gateway verified
- [ ] Swarm: 3-agent collaboration completes code review task end-to-end
- [ ] Self-healing: auto-diagnoses and fixes ≥3 common failure patterns
- [ ] Meta-agent: demonstrates measurable strategy improvement over 10 iterations
- [ ] Security: full trust audit log, input validation on all MCP tools, honeytoken coverage

**Gate criteria**: Swarm protocol completes multi-agent code review. Self-healing fixes common build failures autonomously. MetaAgent shows measurable improvement. All previous gate criteria still pass.

---

## 🔄 Ongoing Technical Debt

- [ ] Continuous removal of magic numbers and hardcoded paths
- [ ] Keep `SPEC.md` / `AGENTS.md` / `CHANGELOG.md` synchronized with code changes
- [ ] Enforce `mypy --strict` progressively across the codebase
- [ ] Keep PAI bridge versions synchronized: `PAI.md` ↔ `SKILL.md` ↔ `agents/pai/__init__.py` ↔ `pyproject.toml`
- [ ] Keep `skill-index.json` triggers/workflows consistent with actual skill files
- [ ] Maintain MCP tool count parity: SKILL.md ↔ `get_total_tool_count()` at release time
- [ ] Module RASP completeness: enforce via CI that all modules have README/AGENTS/SPEC/PAI
- [ ] Deprecation tracking: maintain list of deprecated APIs with removal target versions
