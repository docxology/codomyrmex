<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.2.7 | **Date**: 2026-03-19 | **Modules**: 129 | **Sprint**: 35

> **Current release**: v1.2.7 "Multi-Agent Swarm Orchestration" (2026-03-19). Sprint 35 work to be versioned as v1.2.8+ upon release.

Authoritative project backlog. Upcoming work only; completed items removed.

---

## ✅ v1.2.4 — Google Affordances & Auth Unification *(Released 2026-03-18)*

| # | Deliverable | Status |
| :--- | :--- | :--- |
| D1 | Gmail MCP Tools (`gmail_send_message`, `gmail_list_messages`, `gmail_get_message`, `gmail_create_draft`) | ✅ Done |
| D2 | `GoogleCalendar.from_env()` + `_get_provider()` env-var priority | ✅ Done |
| D3 | 11 Gmail integration tests (9 skip without live creds) | ✅ Done |

---

## ✅ v1.2.5 — Advanced Context Archival & Search *(Released 2026-03-19)*

| # | Deliverable | Status |
| :--- | :--- | :--- |
| D1 | `hermes_build_memory_graph` MCP tool (WikiLink → concept graph) | ✅ Done |
| D2 | `hermes_archive_sessions` MCP tool (size-based GC with dry_run) | ✅ Done |

---

## ✅ v1.2.6 — Autonomous Knowledge Codification *(Released 2026-03-19)*

| # | Deliverable | Status |
| :--- | :--- | :--- |
| D1 | `KnowledgeItemIndex` — TF-IDF index (`agentic_memory/ki_index.py`) | ✅ Done |
| D2 | `KnowledgeMemory.store / recall / merge_duplicates` + Ollama re-ranking | ✅ Done |
| D3 | `hermes_extract_ki`, `hermes_search_knowledge_items`, `hermes_deduplicate_ki` MCP tools | ✅ Done |
| D4 | `HermesSession.on_close` lifecycle hook + `HermesSession.close()` | ✅ Done |

---

## ✅ v1.2.7 — Multi-Agent Swarm Orchestration *(Released 2026-03-19)*

| # | Deliverable | Status |
| :--- | :--- | :--- |
| D1 | `SwarmTopology` (Fan-Out, Fan-In, Pipeline, Broadcast) | ✅ Done |
| D2 | `AgentOrchestrator.capability_profile` + `filter_tools` + `spawn_agent` | ✅ Done |
| D3 | `hermes_spawn_agent`, `orchestrator_run_dag` MCP tools | ✅ Done |
| D4 | `IntegrationBus` P2P mailbox + `EventStore` crash durability | ✅ Done |
| D5 | `events_send_to_agent`, `events_agent_inbox` MCP tools | ✅ Done |

---

## 🔭 v2.0.0+ — Horizon

> **Theme**: Cryptographic persistence, spatial world modeling, and omnimodal processing.

| # | Direction | Builds On | Concrete Next Step |
| :--- | :--- | :--- | :--- |
| R1 | **Spatial World Models** | `spatial/` | Integrate 4D time-series scene generation into `spatial/world_models/`. Expose `spatial_render_agent_trial(scene_config)` MCP tool. |
| R2 | **Self-Custody Wallet** | `wallet/` | Expose `WalletManager` ZK-proof interfaces. Integrate with `identity/` for signed capability proofs. |
| R3 | **Identity & Persona** | `identity/` | Implement `BioCognitiveVerifier` real-bio hooks and multi-persona masking via `Persona` rotation. |

---

## Release Criteria

> [!IMPORTANT]
> **Strict Delivery Requirements**:
>
> - **Zero-Mock Policy**: All tests must use 100% real dependencies. No mock methods permitted.
> - **Full Test Pass**: All tests must pass (`uv run pytest`) with exit code 0.
> - **Code Health**: 0 ruff errors (`uv run ruff check .`).
> - **Documentation Parity**: AGENTS.md, README.md, SPEC.md, CHANGELOG.md all updated before tagging.

---

## Reference

- **Coverage**: `pyproject.toml [tool.coverage.report] fail_under=40`
- **Test**: `uv run pytest` · **Lint**: `uv run ruff check .` · **Format**: `uv run ruff format .`
- **Type check**: `uv run ty check src/` · **Build**: `uv build`

---

*Last updated: 2026-03-19 — Sprint 35.*
