<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.5.0 | **Date**: 2026-03-13 | **Modules**: 129 | **Sprint**: 33

> v1.5.5 "Obsidian Vault Memory & Archival" delivered. Session context is natively dumped to local Obsidian Vaults; parsing and regex/history vault search RAG MCP capabilities added.

Authoritative project backlog. Upcoming work only; completed items removed.

---

## 🚀 v1.5.10 — Semantic Deduplication

> **Theme**: Optimizing repetitive text streams.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Trace Compression Tool** | `agents/hermes/` | Implement `_compress_trace` pre-processor in `coding/execution/` or Hermes' tool handler that scans large incoming stack trace objects and uses string-distance grouping to strip repetitive loop errors (e.g., shrinking 500 identical warning lines to `[Warning repeated 500 times]`). |
| D2 | **Log Pagination Tool** | `agents/hermes/` | Enhance the file reading MCP tools (`read_file`, `grep_search`) to automatically redirect 10,000+ line read attempts into an ephemeral tmp file and expose a `read_log_chunk` interface forcing Hermes to explicitly paginate the text payload dynamically instead of blowing out the context window. |

---

## 🚀 v1.5.11 — Resource Monitoring Integration

> **Theme**: Hardware-aware local scaling.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Health-Aware Execution** | `agents/hermes/` | Tie active session loads into `system_discovery.HealthChecker`. Dynamically surface RAM/VRAM pressure via native `psutil` integration or macOS APIs. |
| D2 | **Dynamic Fallbacks** | `agents/hermes/` | Auto-failback to lighter Ollama models or reject heavy tasks with a clear out-of-memory warning if the system is thrashing heavily on swap memory natively. |

---

## 🚀 v1.5.12 — Unified Agent Traceability

> **Theme**: Deep Observability for Multi-Agent Dispatch.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Trace IDs** | `telemetry/` | Append unique X-Trace-ID tags across the sub-agent boundary, tying `hermes_delegate_task` executions directly to parent events in the unified log structure. |
| D2 | **Dispatch Metrics** | `dashboard/` | Expose active delegated tasks natively across the real-time websocket PAI dashboard to visualize swarm depth. |

---

## 🚀 v1.5.13 — Automated Dependency Healing

> **Theme**: Self-Maintaining Workspaces.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Lockfile Parser** | `environment_setup/` | Implement an MCP tool capable of reading and interpreting `uv.lock` output to safely determine if package collisions are blocking task executions. |
| D2 | **Resolution Agent** | `agents/hermes/` | When an `ImportError` or `ModuleNotFoundError` is caught during code execution, trigger an automated secondary loop (`_heal_environment`) attempting to map the missing local package to `pyproject.toml` and injecting it automatically via `uv add`. |

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
