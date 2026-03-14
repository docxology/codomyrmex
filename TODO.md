<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.5.0 | **Date**: 2026-03-13 | **Modules**: 129 | **Sprint**: 33

> v1.5.14 "Interactive Test Discovery & Scaffolding" delivered. `hermes_client` can autonomously discover missing test coverage, scaffold zero-mock tests, and iteratively repair code until green.

Authoritative project backlog. Upcoming work only; completed items removed.

---

## 🚀 v1.5.15 — Advanced Context Archival & Search

> **Theme**: Scaling Agentic Memory for Long-Running Swarms.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Cross-Session FTS5 Retrieval** | `agents/hermes/` | Enhance `SQLiteSessionStore` with SQLite FTS5 BM25 querying. Expose `hermes_recall_memory(query, limit)` MCP tool for semantic search over past conversations based on keyword relevance. |
| D2 | **Automated Graph Link Inference** | `agentic_memory/` | Expand Obsidian Vault integration to autonomously parse conversational context during `_summarize_context` and infer bi-directional `[[Concept Links]]` to build a dense knowledge graph, updating markdown files natively. |
| D3 | **Memory Garbage Collection (GC)** | `agents/hermes/` | Implement background lifecycle hooks in `SQLiteSessionStore.prune_old_sessions(max_size_mb=50)` to softly extract sessions older than 30 days into compressed `.json.gz` archival blobs, ensuring instantaneous SQLite query latency under heavy load. |

---

## 🚀 v1.5.16 — Autonomous Knowledge Codification

> **Theme**: Self-Tending & Self-Extracting Knowledge Base.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **High-Value Pattern Extraction** | `agents/hermes/` | Introduce an evaluation node on session conclusion. If a session successfully closes a high-complexity objective (e.g., green test generation), a background sub-agent extracts the successful architectural pattern into a standardized `Knowledge Item (KI)` markdown structure. |
| D2 | **Local MCP Native Indexing** | `search/` | Develop `hermes_search_knowledge_items(topic)` tool that uses TF-IDF or vector-based embeddings via local Ollama instances to cross-reference extracted KIs during the planning phase of new tasks to prevent duplicate failure paths. |
| D3 | **KI Deduplication & Merging** | `agentic_memory/` | Add logic to detect closely matching incoming Knowledge Items. Instead of creating new files, the memory agent should natively merge the new context into an existing KI, maintaining chronological evolution trails inside the document. |

---

## 🚀 v1.5.17 — Multi-Agent Swarm Orchestration Improvements

> **Theme**: Deep Swarm Observability & Load Balancing.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Dynamic Tool Routing** | `agents/hermes/` | Allow `AgentOrchestrator` to dynamically strip or supply MCP tools to child swarm agents based on the specific capability vectors required (e.g., Code Gen gets `write_file`, Reviewer gets `run_test`). Minimize context token payload per generation. |
| D2 | **Swarm Execution Topologies** | `orchestrator/` | Implement native DAG (Directed Acyclic Graph) orchestration. Sub-agents can be spawned in parallel (Fan-Out) to research independent files and synchronously collapse (Fan-In) before returning the combined payload to the user. |
| D3 | **Cross-Agent Message Bus** | `events/` | Extend the local event bus to allow peer-to-peer messaging between active agents (e.g., a documentation agent pinging a testing agent proactively to verify a docstring constraint natively). |

---

## 🔭 v1.6.0+ — Horizon & Integration

> **Theme**: Cryptographic persistence, spatial world modeling, and omnimodal processing.

| # | Direction | Builds On | Concrete Next Step |
| :--- | :--- | :--- | :--- |
| R1 | **Spatial World Models** | `spatial/` | Fully integrate 4D time-series scene generation to render persistent simulation environments natively for agent embodied trials. |
| R2 | **Self-Custody Wallet** | `wallet/` | Expose zero-knowledge decentralized self-custody frameworks to allow agents to control their operational resources and perform autonomous transactions securely. |
| R3 | **Identity & Persona** | `identity/` | Establish bio-verified and multi-persona cognitive masking for defensive agentic operations across public networks. |

---

## Release Criteria

> [!IMPORTANT]
> **Strict Delivery Requirements**:
>
> - **Zero-Mock Policy**: All tests must use 100% real dependencies and functional components. No mock methods, classes, or objects permitted. Test configurations must evaluate actual outputs natively.
> - **Full Test Pass**: All 21,000+ unit and integration tests must strictly pass natively (`uv run pytest`) with a 0 exit code before final branch integration.
> - **Code Health**: 0 backwards-compatible legacy APIs, absolute removal of dead or unreachable code, 0 technical debt items remaining on `desloppify` scanners, and 100% `ruff` lint compliance.
> - **Documentation Parity**: Complete API documentation and precise signposting (`AGENTS.md`) for all new modules/capabilities. Complete semantic synchronization between `README.md`, `SPEC.md`, and module-level structures.

---

## Reference

- **Coverage**: `pyproject.toml [tool.coverage.report] fail_under=75`
- **Test**: `uv run pytest` · **Lint**: `uv run ruff check .` · **Format**: `uv run ruff format .`
- **Type check**: `uv run ty check src/` · **Build**: `uv build`

---

*Last updated: 2026-03-13 — Sprint 33.*
