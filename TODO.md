<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.2.4 | **Date**: 2026-03-18 | **Modules**: 129 | **Sprint**: 34

> v1.2.3 "Coherence Release" delivered. Repo-wide structural audit, 39 missing modules registered, version skew resolved across 7 files, coverage gate unified to 40%, spurious root files purged.

Authoritative project backlog. Upcoming work only; completed items removed.

---

## 🚀 v1.2.4 — Google Affordances & Auth Unification

> **Theme**: Unified OAuth2 pattern across all Google integrations. [Unreleased] → version this now.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Gmail MCP Tools** | `email/` | `GmailProvider.from_env()` OAuth2 env var constructor (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`) with ADC fallback. 4 MCP tools: `gmail_send_message`, `gmail_list_messages`, `gmail_get_message`, `gmail_create_draft`. PAI can now send Gmail directly via `FristonBlanket@gmail.com`. |
| D2 | **Calendar OAuth2** | `calendar_integration/` | `GoogleCalendar.from_env()` — same unified OAuth2 env var pattern as `GmailProvider`. `_get_provider()` now prefers `GOOGLE_REFRESH_TOKEN` env vars; token-file path is legacy fallback. |
| D3 | **Integration Tests** | `tests/integration/email/` | 11-test integration suite (9 skip without live creds). Covers send/list/get/retrieve and MCP tool layer end-to-end. |

---

## 🚀 v1.3.0 — Advanced Context Archival & Search

> **Theme**: Scaling Agentic Memory for Long-Running Swarms.

**Status — Implemented in Sprint 34**:

- D1 ✅ `hermes_recall_memory` already calls `SQLiteSessionStore.search_fts()` (FTS5 BM25 `ORDER BY rank`).
- D2 ✅ `hermes_build_memory_graph()` MCP tool: scans all sessions for `[[WikiLink]]` references, returns directed concept graph.
- D3 ✅ `prune_old_sessions()` already compresses to `.json.gz` via `gzip`; `hermes_prune_sessions` MCP tool exists.

**Remaining gaps** (depth-hardening for v1.3.0 final release):

- Integrate `search/hybrid.py:BM25Index` as fallback for out-of-SQLite use cases.
- `hermes_archive_sessions(max_size_mb)` MCP tool for size-based GC.
- 6 additional FTS5 BM25 ranking correctness tests.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **FTS5 BM25 Recall** | `agents/hermes/` | Upgrade `hermes_recall_memory` to route through `SQLiteSessionStore.search_sessions_fts()` using SQLite FTS5 BM25 rank scoring (`ORDER BY rank`). Expose optional `bm25=True` flag; default `True` in v1.3.0. Wire `search/hybrid.py:BM25Index` for out-of-SQLite use cases. Add 6 new tests covering BM25 ranking correctness. |
| D2 | **Graph Link Inference** | `agentic_memory/` | Extend `obsidian_bridge.py` to parse conversational context during `consolidation.py:_summarize_context()` and infer bi-directional `[[Concept Links]]` as `ObsidianNote` backlinks. Feed into `cognilayer_bridge.py` graph. Expose `hermes_build_memory_graph()` MCP tool in `hermes/mcp_tools.py`. Add 8 tests covering link inference and deduplication. |
| D3 | **Memory GC with Archival** | `agents/hermes/` | Extend `SQLiteSessionStore.prune_old_sessions()` to compress pruned sessions into `.json.gz` blobs via `compression/` module. Store archival path in `hermes_sessions` metadata column. Add `hermes_archive_sessions(max_size_mb: int = 50)` MCP tool. Add 4 tests covering GC thresholds and file output. |

---

## 🚀 v1.4.0 — Autonomous Knowledge Codification

> **Theme**: Self-Tending & Self-Extracting Knowledge Base.

**Status — Implemented in Sprint 34**:

- D1 ✅ `hermes_extract_ki(session_id)` MCP tool: loads a session, concatenates assistant turns, persists via `KnowledgeMemory.store()`.
- D2 ✅ `hermes_search_knowledge_items(topic, limit)` MCP tool: token-overlap ranked SEMANTIC recall via `KnowledgeMemory.recall()`.
- D3 ✅ `KnowledgeMemory.merge_duplicates(threshold=0.85)` and `hermes_deduplicate_ki()` MCP tool.

**Remaining gaps** (for v1.4.0 final release):

- `HermesSession.close()` automated KI extraction trigger (currently invocation-only).
- `KnowledgeItemIndex` wrapper in `agentic_memory/` for incremental embedding updates.
- Ollama embedding fallback path via `llm/ollama/`.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **High-Value Pattern Extraction** | `agents/hermes/` | Add a session-close evaluation node in `HermesSession.close()`. If a session resolves a high-complexity objective (≥ 3 tool cycles, success=True), trigger a sub-agent call to `hermes_client.py` with a KI extraction prompt. Output a standardised `KnowledgeItem` (title, tags, markdown body, source session ID) and persist via `KnowledgeMemory.store()`. Expose `hermes_extract_ki(session_id)` MCP tool. Add 6 tests. |
| D2 | **Local MCP Knowledge Search** | `search/` | Implement `hermes_search_knowledge_items(topic, limit=5)` MCP tool in `agents/hermes/mcp_tools.py`. Back it with `HybridSearchIndex` from `search/semantic.py`; optionally fall through to Ollama embeddings (`llm/ollama/`) if available. Build `KnowledgeItemIndex` wrapper in `agentic_memory/` that incrementally updates the index on each new `KnowledgeMemory.store()` call. Add 8 tests: keyword path + embedding path. |
| D3 | **KI Deduplication & Merging** | `agentic_memory/` | Add `KnowledgeMemory.merge_duplicates(threshold: float = 0.85)` using cosine similarity from `HybridSearchIndex`. When a new KI's embedding is within `threshold` of an existing item, append the new context as a `## Update` section with ISO timestamp rather than creating a new record. Expose `hermes_deduplicate_ki()` MCP tool. Add 6 tests covering merge correctness and collision edge cases. |

---

## 🚀 v1.5.0 — Multi-Agent Swarm Orchestration Improvements

> **Theme**: Deep Swarm Observability & Load Balancing.

**Status — Implemented in Sprint 34**:

- D1 ✅ `AgentOrchestrator(capability_profile)` + `filter_tools()` + `spawn_agent(role, task)`; `hermes_spawn_agent` MCP tool.
- D2 ✅ `SwarmTopology` (`orchestrator/swarm_topology.py`): Fan-Out/In/Pipeline/Broadcast; `orchestrator_run_dag` MCP tool.
- D3 ✅ `IntegrationBus.send_to_agent / receive / drain_inbox`; `events_send_to_agent` / `events_agent_inbox` MCP tools.

**Remaining gaps** (for v1.5.0 final release):

- `EventStore` append-only persistence backing for mailbox durability.
- Real `HermesClient` agent registration in `hermes_spawn_agent` (currently uses a stub).
- 8 remaining tests for dead-letter scenarios and `orchestrator_run_dag` MCP integration.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Dynamic Tool Routing** | `agents/hermes/` | Add `capability_profile: dict[str, list[str]]` to `AgentOrchestrator` in `orchestrator/integration.py`. On agent spawn, filter the active MCP registry to only supply tools matching the agent's `capability_profile` (e.g. `CodeGen` gets `write_file`, `run_command`; `Reviewer` gets `run_test`, `read_file`). Expose `hermes_spawn_agent(role, capability_profile)` MCP tool. Reduces context token payload per generation by >50% for specialist agents. Add 8 tests. |
| D2 | **Swarm DAG Topologies** | `orchestrator/` | Expose `WorkflowDAG.fan_out(tasks) -> list[AgentProcess]` and `WorkflowDAG.fan_in(processes) -> WorkflowResult` as first-class primitives in `orchestrator/engines/parallel.py`. Wire into a new `SwarmTopology` dataclass (`FAN_OUT`, `FAN_IN`, `PIPELINE`, `BROADCAST`). Extend `orchestrator/mcp_tools.py` with `orchestrator_run_dag(topology, tasks)`. Add 10 tests covering all 4 topology types. |
| D3 | **Cross-Agent Message Bus** | `events/` | Extend `IntegrationBus` in `events/integration_bus.py` with `send_to_agent(agent_id, message)` and `receive(agent_id, timeout)` methods for peer-to-peer direct messaging. Back the mailbox with `EventStore` append-only log for durability. Add `events_send_to_agent` and `events_agent_inbox` MCP tools. Add 8 tests covering delivery, timeout, and dead-letter scenarios. |

---

## 🔭 v2.0.0+ — Horizon & Integration

> **Theme**: Cryptographic persistence, spatial world modeling, and omnimodal processing.

| # | Direction | Builds On | Concrete Next Step |
| :--- | :--- | :--- | :--- |
| R1 | **Spatial World Models** | `spatial/` | Integrate 4D time-series scene generation (`spatial/four_d/`) into `spatial/world_models/`. Expose `spatial_render_agent_trial(scene_config)` MCP tool for embodied agent trials. |
| R2 | **Self-Custody Wallet** | `wallet/` | Expose `WalletManager` ZK-proof interfaces for agent-controlled operational resource management. Integrate with `identity/` for signed capability proofs. |
| R3 | **Identity & Persona** | `identity/` | Implement `BioCognitiveVerifier` real-bio hooks and multi-persona masking via `Persona` rotation on `IdentityManager`. Gate via `security/` trust model. |

---

## Release Criteria

> [!IMPORTANT]
> **Strict Delivery Requirements**:
>
> - **Zero-Mock Policy**: All tests must use 100% real dependencies and functional components. No mock methods, classes, or objects permitted. Test configurations must evaluate actual outputs.
> - **Full Test Pass**: All 21,000+ unit and integration tests must strictly pass (`uv run pytest`) with a 0 exit code before final branch integration.
> - **Code Health**: 0 backwards-compatible legacy APIs, absolute removal of dead or unreachable code, 0 technical debt items on `desloppify` scanners, and 100% `ruff` lint compliance.
> - **Type Safety**: `ty` diagnostics must be at **0** before any major release (≥ v1.3.0). Minor releases (v1.2.x) target < 500.
> - **Documentation Parity**: Complete API documentation and precise signposting (`AGENTS.md`) for all new modules. Complete semantic synchronisation between `README.md`, `SPEC.md`, and module-level structures.

---

## Reference

- **Coverage**: `pyproject.toml [tool.coverage.report] fail_under=40`
- **Test**: `uv run pytest` · **Lint**: `uv run ruff check .` · **Format**: `uv run ruff format .`
- **Type check**: `uv run ty check src/` · **Build**: `uv build`

---

*Last updated: 2026-03-18 — Sprint 34.*
