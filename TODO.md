<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.5.0 | **Date**: 2026-03-13 | **Modules**: 129 | **Sprint**: 33

> v1.5.0 "The Superorganism Horizon" delivered. All 33,000+ tests natively passing.

Authoritative project backlog. Upcoming work only; completed items removed.

---

## 🚀 v1.5.1 — Hermes Gateway Hardening

> **Theme**: Daemon robustness, PID lifecycle, and crash recovery.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Daemon Lifecycle & Auto-Replace** | `agents/hermes/` | Refine the startup sequence (`hermes gateway run --replace`) to safely kill stale PIDs and gracefully transfer socket bindings without dropping inflight messages. |
| D2 | **Multi-Instance Coordination** | `agents/hermes/` | Upgrade `state.db` concurrency controls to allow multiple gateway instances across different terminal multiplexers to share channel directories safely without SQLite WAL locks. |
| D3 | **Chron & Event Loop Opt** | `agents/hermes/` | Optimize the 60s cron ticker and main event loop to use native `asyncio` task groupings, preventing blocking during heavy platform adapter I/O. |

---

## 🚀 v1.5.2 — Platform Adapter Context & Compression

> **Theme**: Token efficiency and multi-channel scale.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Telegram/WhatsApp Latency** | `agents/hermes/` | Implement per-message latency metrics in platform adapters (`telegram.py`, `whatsapp.py`) to trace delay from raw receive to LLM inference via OpenRouter. |
| D2 | **Deep Context Compression** | `agents/hermes/` | Integrate the new `context_compressor.py` deeper into the gateway adapter loop to dynamically summarize session state if the token window per `session_id = f"{platform}_{user_id}"` exceeds thresholds. |
| D3 | **Channel Directory Sync** | `agents/hermes/` | Automate real-time `channel_directory.json` diffing so that dynamic group/DM arrivals are exposed to Codomyrmex analytics panels. |

---

## 🚀 v1.5.3 — Session Routing & Inference

> **Theme**: State persistence and seamless handoffs.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Cross-Platform Handoff** | `agents/hermes/` | Allow identity resolution matching Telegram `user_id` mapped identities to Discord/Slack handles, sharing session prompts seamlessly across platforms. |
| D2 | **Tool Execution Sandboxing** | `agents/hermes/` | Harden `prompt_builder.py` and tool-call returns inside the gateway so that malicious external messages cannot trigger destructive file system commands during inference. |

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
