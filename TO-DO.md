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

### v0.1.5 — Module Refactoring & Type Safety

**Theme**: "Clean Boundaries"

- [ ] **Module Boundary Hardening**
  - [ ] Enforce strict `__all__` exports in every `__init__.py`.
  - [ ] Eliminate cross-layer import leaks (Core ↔ Specialized).
  - [ ] `mypy --strict` on Core layer (`agents`, `coding`, `security`, `logging_monitoring`).
- [ ] **Dependency Graph Cleanup**
  - [ ] Generate and audit the real import graph.
  - [ ] Decouple `cerebrum` from `agents` via plugin interface.
  - [ ] Make `bio_simulation`, `finance`, `quantum` true optional extras (zero import-time cost).
- [ ] **Test Infrastructure**
  - [ ] Unify `conftest.py` fixtures across unit/integration/performance.
  - [ ] Target ≥80% coverage on Core modules.

---

### v0.1.6 — Agent & Memory Foundations

**Theme**: "Solid Agent Bones"

- [ ] **Agent Architecture Refactor**
  - [ ] `BaseAgent` protocol: `plan()`, `act()`, `observe()` contract.
  - [ ] Standardize inter-agent message format (typed dataclass, not dict).
  - [ ] `AgentRegistry` for dynamic agent discovery.
- [ ] **Memory System**
  - [ ] Wire `agentic_memory` → `vector_store` for persistent retrieval.
  - [ ] `ShortTermMemory` (session dict) + `LongTermMemory` (ChromaDB).
  - [ ] `user_profile.json` read/write for agent preferences.
- [ ] **Event Bus**
  - [ ] `events.EventBus` with typed publish/subscribe.
  - [ ] Integrate EventBus into `orchestrator` for decoupled task dispatch.

---

### v0.1.7 — MCP & Orchestration Hardening

**Theme**: "Plumbing That Works"

- [ ] **MCP Plumbing**
  - [ ] Register `git_operations` tools (`git_commit`, `git_branch`, `git_diff`).
  - [ ] Expose `containerization` tools (`docker_logs`, `docker_compose_up`).
  - [ ] Add `semantic_search` and `smart_grep` as MCP tools.
  - [ ] `MCPClient` to consume external MCP servers.
- [ ] **Orchestrator v2**
  - [ ] Async-first task parallelization (`asyncio.TaskGroup`).
  - [ ] Retry/backoff policies for flaky tool calls.
  - [ ] CLI startup time < 500ms (lazy loading audit).
- [ ] **Observability**
  - [ ] WebSocket real-time log streaming from `logging_monitoring`.
  - [ ] `codomyrmex doctor` diagnostic CLI command.

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
