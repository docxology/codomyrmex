# Codomyrmex Project Roadmap & To-Do

**Status**: Active | **Last Updated**: February 2026 | **Strategic Target**: v0.4.0

This document outlines the phased roadmap for the Codomyrmex ecosystem.
Versions 0.1.7–0.1.9 harden foundations (testing, MCP plumbing, PAI workflows).
Version 0.2.0 certifies robust production-grade agent infrastructure.
Version 0.3.0 layers cognitive architecture on the hardened base.
Version 0.4.0 delivers autonomous swarm orchestration.

---

## ✅ Completed Releases

### v0.1.3 — Foundation Hardening

- [x] RASP standardization audit (`scripts/audit_rasp.py`).
- [x] Dependency pruning in `pyproject.toml` via `uv`.
- [x] Pre-release test verification (networking, logging — 84 pass, 2 skip).

### v0.1.4 — Descaffold & Zero-Mock Certification

- [x] `EphemeralServer` replaces external `httpbin.org` in networking tests.
- [x] LLM tests verified real API calls (OpenRouter/Ollama).
- [x] `pytest-benchmark` baselines (import time, AST parsing).
- [x] Coverage checks for Core and Specialized modules.

---

## 🔧 Foundation Hardening (v0.1.5 – v0.1.9)

### v0.1.5 — Module Refactoring & Type Safety ✅

**Theme**: "Clean Boundaries"

- [x] Export audit: 79/79 modules have `__all__` (`scripts/audit_exports.py`)
- [x] Import audit: 0 cross-layer violations / 291 edges (`scripts/audit_imports.py`, AST-based)
- [x] Added `__all__` to `module_template` and `tests`
- [x] Verified specialized modules (`cerebrum`, `bio_simulation`, `finance`, `quantum`) are already isolated

---

### v0.1.6 — Agent & Memory Foundations ✅

**Theme**: "Solid Agent Bones"

> Grounded in audit: `agents/core/base.py` has `execute()/stream()` but no `plan()/act()/observe()`.
> `agentic_memory` has `VectorStoreMemory` but it never actually wires to `vector_store`.
> `events.EventBus` exists but 0 integrations with `orchestrator`.

- [x] **Agent Protocol Extension** (`agents/core/`)
  - [x] Add `AgentProtocol` with `plan()`, `act()`, `observe()` methods to `base.py`.
  - [x] Add typed `AgentMessage` dataclass to new `messages.py` (replace `dict` messages in `ReActAgent`).
  - [x] Refactor `ReActAgent._execute_impl` into discrete `plan→act→observe` calls.
  - [x] Add `ToolRegistry.from_mcp(mcp_registry)` bridge to `registry.py`.
  - [x] Type-hint `ReActAgent.llm_client` as `codomyrmex.llm.BaseLLMClient | Any`.
- [x] **Memory → Vector Store Wiring** (`agentic_memory/`)
  - [x] `VectorStoreMemory.__init__`: auto-create `InMemoryVectorStore` when `vector_store=None`.
  - [x] Add `VectorStoreMemory.from_chromadb(path)` optional factory (try/except wrapped).
  - [x] Add `AgentMemory.add()` alias to `remember()` (MCP tool calls `.add()` which doesn't exist).
  - [x] `JSONFileStore.list_all()` method + thread-safe file writes.
  - [x] New `user_profile.py`: `UserProfile` dataclass with `~/.codomyrmex/user_profile.json` persistence.
- [x] **EventBus ↔ Orchestrator Integration** (`events/`, `orchestrator/`)
  - [x] `EventBus.emit_typed(event: Event)` convenience + `subscribe_typed(event_type, handler)`.
  - [x] `Workflow.run()` emits `TASK_STARTED`/`COMPLETED`/`FAILED` events via optional `event_bus` param.
  - [x] `OrchestratorEvents` enum in `orchestrator/events.py`.
- [x] **Test Coverage (≥80% on touched modules)**
  - [x] `test_agent_protocol.py`: `AgentMessage`, `BaseAgent.plan()/act()/observe()`, `ToolRegistry.from_mcp()`.
  - [x] `test_memory_integration.py`: `VectorStoreMemory` with real `InMemoryVectorStore`, `JSONFileStore` round-trip, `UserProfile`.
  - [x] `test_event_orchestrator.py`: events emitted during `Workflow.run()`.

---

### v0.1.7 — Test Integrity & MCP Plumbing

**Theme**: "Fix the Floor, Wire the Pipes"

> Grounded in audit: 72 pre-existing test failures (20 async event-loop, 8 schema import, 5 pyarrow, 5 skill_sync).
> Only 2 `mcp_tools.py` files exist (`formal_verification`, `logistics`). No `MCPClient`.
> `git_operations` has 44 exports but 0 MCP registration. `containerization` has 5 exports and 0 MCP registration.
> Auto-discovery finds 483 public tools from 76 modules. 535 total tools registered.

- [ ] **Fix Pre-Existing Test Failures (72 → 0)**
  - [ ] `streaming/test_streaming_async.py` (20 failures): add `pytest-asyncio` fixtures, replace deprecated `get_event_loop()` with `asyncio.Runner` / `@pytest.mark.asyncio`.
  - [ ] `utils/test_utils_integration.py` (5 failures): same async event loop fix — `make_async`, `gather_with_concurrency`, `async_timed_operation`.
  - [ ] `schemas/test_schemas.py` + `validation/schemas/test_schemas.py` (8 failures): add `database_management.schemas` re-export or fix import path.
  - [ ] `serialization/test_serialization*.py` (5 failures): gate parquet tests behind `pytest.importorskip("pyarrow")`.
  - [ ] `skills/test_skill_sync.py` (5 failures): gate git-dependent tests behind `@pytest.mark.skipif(not HAS_GIT_REMOTE)` or fix fixture expectations.
  - [ ] Verify: full suite achieves **0 failures, ≤240 skips**.
- [ ] **MCP Tool Registration Sprint**
  - [ ] `git_operations/mcp_tools.py`: register `git_commit`, `git_branch`, `git_diff`, `git_log`, `git_status` as `@mcp_tool`.
  - [ ] `containerization/mcp_tools.py`: register `docker_logs`, `docker_compose_up`, `docker_ps` as `@mcp_tool`.
  - [ ] `coding/mcp_tools.py`: register `parse_file`, `list_symbols`, `find_references` as `@mcp_tool`.
  - [ ] `search/mcp_tools.py`: register `search_codebase`, `search_files` as `@mcp_tool`.
  - [ ] Auto-discover all `mcp_tools.py` modules in `discovery.py` at server startup.
  - [ ] Ensure `_discover_dynamic_tools()` returns deterministic ordering (sort by name).
- [ ] **MCPClient** (`model_context_protocol/client.py`)
  - [ ] `MCPClient` for consuming external MCP servers (HTTP/SSE transport).
  - [ ] Methods: `connect()`, `list_tools()`, `call_tool()`.
  - [ ] Uses `networking.HTTPClient` internally.
- [ ] **MCP Tests (Zero-Mock)**
  - [ ] `test_mcp_smoke.py`: iterate all registered tools, call each with minimal valid args, assert structured response.
  - [ ] `test_mcp_client.py`: `MCPClient` ↔ `MCPServer` local loopback round-trip.
  - [ ] `test_mcp_discovery.py`: deterministic tool ordering, auto-discovery from `mcp_tools.py` files.

---

### v0.1.8 — Async-First Orchestration & Observability

**Theme**: "Concurrent Backbone"

> Grounded in audit: `Workflow.run()` is already async but `ParallelRunner` is sync-only.
> `logging_monitoring` has 1 test file and no WebSocket streaming.
> CLI startup time untested. 79 modules = heavy import tree.

- [ ] **Orchestrator v2 (async-first)**
  - [ ] `orchestrator/async_runner.py`: `AsyncParallelRunner` using `asyncio.TaskGroup` (Python 3.11+).
  - [ ] Unified `Workflow.run()` with concurrent task execution (topological sort + semaphore).
  - [ ] Internal retry/backoff decorator (no new dependencies).
  - [ ] `orchestrator/scheduler.py`: priority-based task scheduling with resource limits.
- [ ] **Observability**
  - [ ] `logging_monitoring/ws_handler.py`: `WebSocketLogHandler` for real-time log streaming.
  - [ ] Structured JSON log output mode for all modules.
  - [ ] Centralized log aggregation: `EventBus` → logging pipeline.
- [ ] **Performance Baselines**
  - [ ] CLI startup time target: `< 500ms`. Lazy-loading audit for heavy imports.
  - [ ] Benchmark public API entry points (`performance/benchmark.py`).
  - [ ] Profile and optimize hot-path imports (defer `matplotlib`, `chromadb`, `pyarrow`).
- [ ] **Test Coverage**
  - [ ] `test_async_runner.py`: async parallel execution with real tasks, dependency resolution, error propagation.
  - [ ] `test_ws_handler.py`: WebSocket handler with real `EphemeralServer` (Zero-Mock).

---

### v0.1.9 — PAI & Claude Code Workflow Hardening

**Theme**: "Bulletproof Workflows"

> Grounded in audit: 7 Claude Code workflows exist (`/codomyrmexAnalyze`, `/codomyrmexDocs`,
> `/codomyrmexMemory`, `/codomyrmexSearch`, `/codomyrmexStatus`, `/codomyrmexTrust`, `/codomyrmexVerify`).
> `verify_capabilities()` reports 535 tools (483 auto-discovered), MCP server healthy, PAI bridge installed.
> Trust gateway works but needs end-to-end integration tests and error recovery.
> `_discover_dynamic_tools()` is called ~12× during server creation (redundant).

- [ ] **PAI Bridge Hardening** (`agents/pai/`)
  - [ ] Deduplicate `_discover_dynamic_tools()` calls: cache registry at module level (currently called 12× per server create).
  - [ ] `verify_capabilities()` response structure: normalize `tools` key to always contain `safe`/`destructive` lists.
  - [ ] Error recovery: every workflow gracefully handles import failures, missing modules, timeouts.
  - [ ] `mcp_bridge.py`: add `list_workflows()` tool exposing the 7 Claude Code workflows via MCP.
- [ ] **Claude Code Workflow Integration Tests** (Zero-Mock)
  - [ ] `test_workflow_analyze.py`: `/codomyrmexAnalyze` on a sample directory → valid JSON with metrics.
  - [ ] `test_workflow_docs.py`: `/codomyrmexDocs` for 5+ core modules → README content returned.
  - [ ] `test_workflow_status.py`: `/codomyrmexStatus` → system_status + pai_awareness JSON.
  - [ ] `test_workflow_trust.py`: full trust lifecycle: `verify_capabilities()` → `trust_all()` → `trusted_call_tool()` → `reset_trust()`.
  - [ ] `test_workflow_verify.py`: `/codomyrmexVerify` → all sections populated (modules, tools, resources, prompts, trust).
  - [ ] `test_workflow_search.py`: `/codomyrmexSearch` for known patterns → matching results.
  - [ ] `test_workflow_memory.py`: `/codomyrmexMemory` add/recall round-trip.
- [ ] **CLI Doctor** (`cli/doctor.py`)
  - [ ] `codomyrmex doctor`: module imports, tool registry, MCP health, test suite summary.
  - [ ] `codomyrmex doctor --pai`: PAI skill status, tool count, trust state, version sync.
  - [ ] `codomyrmex doctor --workflows`: validate all 7 Claude Code workflows execute without error.
  - [ ] RASP completeness check: flag modules missing README/AGENTS/SPEC/PAI.
- [ ] **Concurrency Hardening**
  - [ ] Thread-safety audit: all shared state in `EventBus`, `ToolRegistry`, `AgentMemory` uses locks.
  - [ ] `concurrency/pool.py`: managed async worker pool for parallel tool calls.
  - [ ] Dead-letter handling for timed-out MCP tool invocations.
- [ ] **Security Pre-Audit**
  - [ ] Trust gateway: add audit log for all `trusted_call_tool()` invocations.
  - [ ] Input validation: MCP tool arguments validated against schemas before dispatch.
  - [ ] `defense` module: activate honeytoken patterns in test environments.

---

## 🤖 v0.2.0 — "Agents Я Us"

**Theme**: "Everything Works, Everything Connects"
*Robustly fully working PAI integration, Claude Code workflows, MCP, logging, concurrency.*

> This release certifies that every Codomyrmex capability is accessible, tested, and production-grade
> through PAI, Claude Code, and MCP interfaces. No new cognitive features — just bulletproof plumbing.

- [ ] **Complete MCP Coverage**
  - [ ] Every module with public functions has auto-discovered MCP tools (currently 483/535).
  - [ ] `MCPClient` ↔ `MCPServer` full round-trip verified.
  - [ ] Tool count parity: `get_total_tool_count()` matches SKILL.md tool table.
  - [ ] MCP tool argument schemas fully typed (no `Any` in tool signatures).
- [ ] **PAI Integration Certification**
  - [ ] All 7 Claude Code workflows (`/codomyrmex*`) pass integration tests.
  - [ ] `verify_capabilities()` returns accurate, normalized results.
  - [ ] `trust_all()` → `trusted_call_tool()` → `reset_trust()` lifecycle tested end-to-end.
  - [ ] Skill manifest (`get_skill_manifest()`) matches actual capabilities.
  - [ ] PAI version sync: `PAI.md` ↔ `SKILL.md` ↔ `agents/pai/__init__.py` ↔ `pyproject.toml` all `0.2.0`.
- [ ] **Logging & Observability**
  - [ ] Structured JSON logging available across all modules.
  - [ ] `WebSocketLogHandler` for real-time streaming.
  - [ ] `codomyrmex doctor` CLI fully operational with `--pai` and `--workflows` flags.
  - [ ] EventBus → logging pipeline: all agent/workflow events are observable.
- [ ] **Concurrency & Performance**
  - [ ] `AsyncParallelRunner` for concurrent workflow execution.
  - [ ] CLI startup `< 500ms`, import time `< 200ms`.
  - [ ] Thread-safe shared state: `EventBus`, `ToolRegistry`, `AgentMemory`, `JSONFileStore`.
  - [ ] Performance benchmarks for all public API entry points.
- [ ] **Test Suite Health**
  - [ ] Full regression: 8,000+ tests, **0 failures**, ≤100 skips.
  - [ ] All async tests use `pytest-asyncio` with proper event loop management.
  - [ ] Optional-dependency tests gated behind `pytest.importorskip()`.
  - [ ] Coverage ≥ 80% on all actively maintained modules.
- [ ] **Documentation Freeze**
  - [ ] All 79 modules have current README.md, SPEC.md, AGENTS.md.
  - [ ] CHANGELOG.md complete through v0.2.0.
  - [ ] API reference generated from docstrings.
  - [ ] Claude Code workflow documentation in `.agent/workflows/` matches implementation.

---

## 🧠 v0.3.0 — "Active Inference"

**Theme**: "Thinking Agents"
*Cognitive architecture layered on the hardened v0.2.0 base.*

> Grounded in audit: `cerebrum` has 3 files, `meme` has 2, `graph_rag` has 4 — all functional but unintegrated.
> No chain-of-thought wrapper exists in `llm`. `prompt_engineering` has 5 files but no agent integration.

- [ ] **Chain-of-Thought Reasoning**
  - [ ] `llm/chain_of_thought.py`: CoT prompting wrapper (structured reasoning extraction).
  - [ ] `agents/core/thinking_agent.py`: `ThinkingAgent` extending `ReActAgent` with reasoning traces.
  - [ ] Sliding window context management for unbounded conversations.
- [ ] **Cerebrum + GraphRAG Integration**
  - [ ] `cerebrum/case_retrieval.py`: `CaseBase` retrieval for past successful code-generation patterns.
  - [ ] `graph_rag/agent_bridge.py`: wires graph retrieval into agent context windows.
  - [ ] Bayesian reasoning hooks in `orchestrator` decision-making.
- [ ] **Memetic Analysis**
  - [ ] `meme/anti_pattern_detector.py`: detect repetitive anti-patterns in codebase.
  - [ ] `meme/drift_tracker.py`: track concept drift between documentation and code.
- [ ] **Prompt Engineering Integration**
  - [ ] Wire `prompt_engineering` templates into agent planning phase.
  - [ ] Dynamic prompt selection based on task type and context.
- [ ] **Security Hardening**
  - [ ] Harden `wallet` module for secure key management (key rotation, encrypted storage).
  - [ ] Dependency scanning in CI/CD (`uv audit` or equivalent).
- [ ] **Test Coverage**
  - [ ] `test_chain_of_thought.py`: CoT extraction with real LLM calls.
  - [ ] `test_case_retrieval.py`: case base storage and retrieval round-trip.
  - [ ] `test_anti_pattern_detector.py`: known anti-pattern detection on sample code.

---

## 🐜 v0.4.0 — "Ant Colony"

**Theme**: "Swarm Orchestration"
*Autonomous multi-agent collaboration on hardened, thinking foundations.*

> Grounded in audit: `collaboration` has 3 files. `agents` has ReActAgent but no multi-agent protocol.
> `orchestrator` has 13 files but no agent-to-agent coordination. `identity` has 5 files (agent identity management exists).

- [ ] **Swarm Protocol** (`collaboration/swarm/`)
  - [ ] `SwarmProtocol`: typed multi-agent collaboration (Coder ↔ Reviewer ↔ DevOps roles).
  - [ ] `AgentPool`: managed pool of agents with capability-based routing.
  - [ ] `SwarmMessage`: inter-agent message format extending `AgentMessage`.
  - [ ] Agent identity + capability advertisement via `identity` module.
- [ ] **Self-Healing Workflows** (`orchestrator/self_healing.py`)
  - [ ] Auto-diagnose build failures using `ThinkingAgent`.
  - [ ] Config-aware retry: fix configuration issues and retry failed tasks.
  - [ ] Dead-letter queue for permanently failed tasks with structured diagnostics.
- [ ] **Project-Level Context** (`agents/context/`)
  - [ ] `ProjectContext`: agents understand full repository structure, not single files.
  - [ ] `git_operations` + `coding.parsers` → automatic repo indexing.
  - [ ] Context-aware tool selection based on file types and project structure.
- [ ] **Meta-Agent** (`agents/meta/`)
  - [ ] `MetaAgent`: rewrites its own prompt strategies based on observed outcomes.
  - [ ] Feedback loop: outcome → scoring → prompt adjustment → next attempt.
  - [ ] Strategy library persistence via `agentic_memory`.
- [ ] **Release Certification**
  - [ ] Full regression: 10,000+ tests, 0 failures.
  - [ ] API stability contract: no breaking changes from v0.2.x/v0.3.x public APIs.
  - [ ] Performance: CLI startup < 500ms, import time < 200ms, MCP tool registration < 100ms.
  - [ ] Documentation: all modules have current SPEC.md, AGENTS.md, README.md.
  - [ ] MCP tool count > 600 registered tools with trust gateway verified.

---

## 🔄 Ongoing Technical Debt

- [ ] Continuous removal of magic numbers and hardcoded paths.
- [ ] Keep `SPEC.md` / `AGENTS.md` synchronized with code changes.
- [ ] Enforce `mypy --strict` progressively across the codebase.
- [ ] Keep PAI bridge versions synchronized: `PAI.md` ↔ `SKILL.md` ↔ `agents/pai/__init__.py` ↔ `pyproject.toml`.
- [ ] Keep `skill-index.json` triggers/workflows consistent with actual skill files and workflow implementations.
- [ ] Maintain MCP tool count parity: SKILL.md tool table count must equal `get_total_tool_count()` at release time.
