# Codomyrmex Project Roadmap & To-Do

**Status**: Active | **Last Updated**: February 2026 | **Strategic Target**: v0.2.0+

This document outlines the phased roadmap for the Codomyrmex ecosystem.
Versions 0.1.5–0.1.7 harden foundations (modularity, testing, orchestration).
Versions 0.1.8–0.1.9 layer cognitive architecture on the hardened base.
Version 0.2.0 stabilizes a qualitatively bigger system: autonomous swarm orchestration.

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

## 🔧 Foundation Hardening (v0.1.5 – v0.1.7)

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

### v0.1.7 — MCP & Orchestration Hardening

**Theme**: "Plumbing That Works"

> Grounded in audit: `MCPServer` exists but no `MCPClient`. `git_operations` has 44 exports but 0 MCP registration.
> `containerization` has 5 exports but 0 MCP registration. `orchestrator.ParallelRunner` is sync-only.
> `logging_monitoring` has 1 test file and no WebSocket streaming.

- [ ] **MCP Tool Registration**
  - [ ] `git_operations/mcp_tools.py`: register `git_commit`, `git_branch`, `git_diff`, `git_log`, `git_status` as `@mcp_tool`.
  - [ ] `containerization/mcp_tools.py`: register `docker_logs`, `docker_compose_up`, `docker_ps` as `@mcp_tool`.
  - [ ] Auto-discover `mcp_tools.py` modules in `discovery.py` at server startup.
  - [ ] Ensure `_discover_dynamic_tools()` returns deterministic ordering (sort by name).
- [ ] **MCPClient** (`model_context_protocol/client.py`)
  - [ ] `MCPClient` for consuming external MCP servers (HTTP/SSE transport).
  - [ ] Methods: `connect()`, `list_tools()`, `call_tool()`.
  - [ ] Uses `networking.HTTPClient` internally.
- [ ] **MCP Smoke Tests & Trust Gateway**
  - [ ] `test_mcp_smoke.py`: iterate all registered tools, call each with minimal valid args, assert structured response.
  - [ ] `test_mcp_client.py`: `MCPClient` ↔ `MCPServer` local loopback round-trip.
  - [ ] `test_mcp_discovery.py`: deterministic tool ordering, auto-discovery from `mcp_tools.py` files.
  - [ ] Trust gateway round-trip: `verify_capabilities()` → `trust_all()` → `trusted_call_tool()`.
- [ ] **Orchestrator v2 (async-first)**
  - [ ] `orchestrator/async_runner.py`: `AsyncParallelRunner` using `asyncio.TaskGroup` (Python 3.11+).
  - [ ] `Workflow.run_async()`: async equivalent of `run()`.
  - [ ] Internal retry/backoff decorator (no new dependencies).
  - [ ] CLI startup time < 500ms: lazy-loading audit for heavy imports.
- [ ] **Observability**
  - [ ] `logging_monitoring`: `WebSocketLogHandler` for real-time log streaming.
  - [ ] `cli/doctor.py`: `codomyrmex doctor` diagnostic command (module imports, tool registry, MCP health).
  - [ ] `codomyrmex doctor --pai`: PAI skill status, tool count, trust state, version sync.
  - [ ] RASP completeness check: flag modules missing README/AGENTS/SPEC/PAI.
- [ ] **Test Coverage**
  - [ ] `test_logging_monitoring.py`: WebSocket handler with real EphemeralServer (Zero-Mock).
  - [ ] `test_orchestrator_async.py`: async workflow execution with real tasks.

---

## 🧠 Cognitive Layer (v0.1.8 – v0.1.9)

### v0.1.8 — Cognitive Architecture

**Theme**: "Active Inference"

- [ ] **Thinking Process**
  - [ ] Chain-of-Thought prompting wrapper in `codomyrmex.llm`.
  - [ ] `ThinkingAgent`: plan → reason → act loop.
  - [ ] Sliding window context management for unbounded conversations.
- [ ] **Cerebrum Integration**
  - [ ] Bayesian reasoning in `orchestrator` decision-making.
  - [ ] `CaseBase` retrieval for past successful code-generation patterns.
- [ ] **Memetic Analysis**
  - [ ] `meme` module detects repetitive anti-patterns in codebase.
  - [ ] Track "concept drift" between documentation and code.

---

### v0.1.9 — Security, Scale & Pre-Release Polish

**Theme**: "Fortress & Velocity"

- [ ] **Security Hardening**
  - [ ] Harden `wallet` module for secure key management.
  - [ ] Activate `defense` module patterns (honeytokens in test envs).
  - [ ] Rigorous dependency scanning in CI/CD.
- [ ] **Performance**
  - [ ] Benchmark every public API entry point.
  - [ ] Profile and optimize hot-path imports.
- [ ] **Release Candidate**
  - [ ] Full regression test suite (all modules, all markers).
  - [ ] Documentation freeze and CHANGELOG finalization.

---

## 🎯 v0.2.0 — The "Ant Colony" Release

**Theme**: "Swarm Orchestration"
*A qualitatively bigger system: autonomous multi-agent collaboration on hardened foundations.*

- [ ] **Swarm Protocol**: Typed multi-agent collaboration (Coder ↔ Reviewer ↔ DevOps).
- [ ] **Self-Healing Workflows**: Auto-diagnose build failures, fix config, and retry.
- [ ] **Project-Level Context**: Agents understand the full repository, not single files.
- [ ] **Meta-Agent**: Rewrites its own prompt strategies based on observed outcomes.

---

## 🔄 Ongoing Technical Debt

- [ ] Continuous removal of magic numbers and hardcoded paths.
- [ ] Keep `SPEC.md` / `AGENTS.md` synchronized with code changes.
- [ ] Enforce `mypy --strict` progressively across the codebase.
- [ ] Keep PAI bridge versions synchronized: `PAI.md` ↔ `SKILL.md` ↔ `agents/pai/__init__.py` ↔ `pyproject.toml`.
- [ ] Keep `skill-index.json` triggers/workflows consistent with actual skill files and workflow implementations.
- [ ] Maintain MCP tool count parity: SKILL.md tool table count must equal `get_total_tool_count()` at release time.
