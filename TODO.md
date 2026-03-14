<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.5.0 | **Date**: 2026-03-13 | **Modules**: 129 | **Sprint**: 33

> v1.5.5 "Obsidian Vault Memory & Archival" delivered. Session context is natively dumped to local Obsidian Vaults; parsing and regex/history vault search RAG MCP capabilities added.

Authoritative project backlog. Upcoming work only; completed items removed.

---

## 🚀 v1.5.13 — Automated Dependency Healing

> **Theme**: Self-Maintaining Workspaces.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Lockfile Parser** | `environment_setup/` | Implement an MCP tool capable of reading and interpreting `uv.lock` output to safely determine if package collisions are blocking task executions. |
| D2 | **Resolution Agent** | `agents/hermes/` | When an `ImportError` or `ModuleNotFoundError` is caught during code execution, trigger an automated secondary loop (`_heal_environment`) attempting to map the missing local package to `pyproject.toml` and injecting it automatically via `uv add`. |
| D3 | **Healing Metrics** | `telemetry/` | Track `heal_attempts` and `heal_success_rate` in the Hermes session metadata, emitting structured logs for continuous monitoring. |

---

## 🚀 v1.5.14 — Interactive Test Discovery & Scaffolding

> **Theme**: Agent-Initiated Test Creation.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Missing Test Detection** | `agents/hermes/` | Integrate with `pytest --collect-only` or coverage readouts to actively scan a targeted directory and surface undocumented/untested functions immediately to the agent session as a structured JSON object. |
| D2 | **Zero-Mock Scaffolding Tool** | `agents/hermes/` | Add an MCP tool `hermes_scaffold_test` that generates the boilerplate pytest framework strictly mapping real execution dependencies so Hermes can seamlessly populate test coverage. |
| D3 | **Coverage Loop** | `agents/hermes/` | Introduce an autonomous loop that writes a test, runs `pytest`, captures failure traces, and iteratively fixes the test or the source code until the test passes. |

---

## 🚀 v1.5.15 — Advanced Context Archival & Search

> **Theme**: Scaling Agentic Memory.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Cross-Session Retrieval** | `agents/hermes/` | Enhance the `SQLiteSessionStore` with FTS5 BM25 querying, exposing a `hermes_recall` MCP tool that allows the agent to semantically search its own past sessions for relevant context. |
| D2 | **Graph Mapping** | `agentic_memory/` | Expand the Obsidian Vault integration to automatically infer links (`[[concept]]`) between entities extracted during `_summarize_context`, building a dense knowledge graph. |
| D3 | **Memory Garbage Collection** | `agents/hermes/` | Implement background routines to softly archive older SQLite sessions into compressed JSON blobs, maintaining strict maximum DB size limits for high-frequency deployment. |

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
> - **Zero-Mock Policy**: All tests must use 100% real dependencies and functional components. No mock methods.
> - **Full Test Pass**: All 33,000+ unit and integration tests passing natively (`uv run pytest`) before final branch integration.
> - **Code Health**: No backwards or legacy methods, no technical debt, and 100% lint compliance. Clean repository state.
> - **Documentation**: Complete API documentation and signposting (`AGENTS.md`) for all new capabilities. Consistency with README.md and SPEC.md.

---

## Reference

- **Coverage**: `pyproject.toml [tool.coverage.report] fail_under=75`
- **Test**: `uv run pytest` · **Lint**: `uv run ruff check .` · **Format**: `uv run ruff format .`
- **Type check**: `uv run ty check src/` · **Build**: `uv build`

---

*Last updated: 2026-03-13 — Sprint 33.*
