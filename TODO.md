<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.2.8-draft | **Date**: 2026-03-19 | **Modules**: 128 | **Sprint**: 35

> **Current release**: v1.2.7 "Multi-Agent Swarm Orchestration" (2026-03-19).
> **Next release**: v1.2.8 (Sprint 35)
> **Archived**: v1.2.4–v1.2.7 → [CHANGELOG.md](CHANGELOG.md)

---

## 🚧 v1.2.8.0 — Sprint 35 Core

| # | Deliverable | Module | Status | Technical Detail |
| :--- | :--- | :--- | :--- | :--- |
| v1.2.8.1 | **Hermes v0.4.0 FastMCP scaffolding** | `agents/hermes/` | 🔄 In Progress | Integrate `optional-skills/mcp/fastmcp/scaffold_fastmcp.py` for Codomyrmex→Hermes MCP exposure |
| v1.2.8.2 | **Hermes Session Race Guards** | `agents/hermes/session.py` | ✅ Done | `SessionRaceGuard` with context manager, `SessionGuardContext`, granular threading.Lock per session_id. Tests: 10 passing (zero-mock) |
| v1.2.8.3 | **Webhook platform adapter** | `agents/hermes/gateway/platforms/webhook.py` | ✅ Done | `WebhookAdapter` with HMAC-SHA256 verification, GitHub PR/Commit/Issue payload parsing, prompt templates, implements `GatewayAdapter` protocol |
| v1.2.8.4 | **Webhook config schema** | `agents/hermes/gateway/platforms/webhook.py` | ✅ Done | `WebhookConfig(port: int, routes: dict, host: str)`, `WebhookRoute(secret, prompt_template, handler)` matching schema requirements |
| v1.2.8.5 | **Dynamic context window resolution** | `agents/hermes/_provider_router.py` | ✅ Done | `ModelContextRegistry` with OpenRouter API fallback, 11 known model defaults, thread-safe `get_context_length_safe()` |
| v1.2.8.6 | **ContextCompressor token eviction** | `agents/hermes/_provider_router.py` | ✅ Done | `CAPACITY_THRESHOLD=0.8` (80%), model_id property setter with error handling, integrates with registry for dynamic max_tokens |

---

## 🔭 v1.2.9+ — Horizon (Unscoped)

> **Theme**: Cryptographic persistence, spatial world modeling, omnimodal processing.

| # | Direction | Builds On | Concrete Next Step |
| :--- | :--- | :--- | :--- |
| R1 | **Spatial World Models** | `spatial/` | Integrate 4D time-series into `spatial/world_models/`, expose `spatial_render_agent_trial` |
| R2 | **Self-Custody Wallet** | `wallet/` | Expose `WalletManager` ZK-proof interfaces, integrate with `identity/` for signed capability proofs |
| R3 | **Identity & Persona** | `identity/` | Implement `BioCognitiveVerifier` real-bio hooks + `Persona` rotation |

---

## 📋 Backlog — Unscoped / Triaging

| # | Item | Module | Notes |
| :--- | :--- | :--- | :--- |
| B1 | **Tool versioning UI** | `model_context_protocol/` | `deprecated_in` metadata exists, not surfaced |
| B2 | **Oversized files audit** | `orchestrator/` | 16 files >800 LOC, largest: `orchestration.py` |
| B3 | **Video module full impl** | `video/` | Stub — exceptions only |
| B4 | **Meme module MCP exposure** | `meme/` | Experimental, needs RASP + `@mcp_tool` |
| B5 | **Secure Cognitive Layer MCP** | `identity/`, `wallet/`, `defense/`, `market/`, `privacy/` | Not MCP-exposed via PAI bridge |

---

## 🎯 Release Criteria

> **Strict Delivery Requirements** — All v1.2.8.x items must pass before tagging:

| Requirement | Command | Threshold |
| :--- | :--- | :--- |
| **Zero-Mock Policy** | `uv run pytest` | 0 `unittest.mock` / `mock` imports |
| **Full Test Pass** | `uv run pytest` | Exit code 0 |
| **Code Health** | `uv run ruff check .` | 0 errors |
| **Type Safety** | `uv run ty check src/` | <1,000 diagnostics |
| **Coverage Gate** | `uv run pytest --cov` | ≥40% |
| **Documentation Parity** | — | AGENTS.md, README.md, SPEC.md, CHANGELOG.md updated |

---

## 📖 Reference

### Navigation

| Context | Link |
| :--- | :--- |
| **Project Root** | [README.md](README.md) |
| **Agent Coordination** | [AGENTS.md](AGENTS.md) |
| **Functional Spec** | [SPEC.md](SPEC.md) |
| **Changelog** | [CHANGELOG.md](CHANGELOG.md) ← v1.2.4+ archived |
| **Module Docs** | [docs/modules/](docs/modules/README.md) |

### Commands

| Task | Command |
| :--- | :--- |
| **Test** | `uv run pytest` |
| **Lint** | `uv run ruff check .` |
| **Format** | `uv run ruff format .` |
| **Type Check** | `uv run ty check src/` |
| **Coverage** | `uv run pytest --cov=src/codomyrmex --cov-fail-under=40` |
| **Build** | `uv build` |

### Key Modules

| Module | Purpose | Documentation |
| :--- | :--- | :--- |
| **agents/hermes** | Dual-backend agent (CLI + Ollama) | [docs/agents/hermes/](docs/agents/hermes/README.md) · [AGENTS](src/codomyrmex/agents/hermes/AGENTS.md) |
| **orchestrator** | Workflow orchestration, swarm topologies | [AGENTS](src/codomyrmex/orchestrator/AGENTS.md) |
| **agentic_memory** | Persistent memory, knowledge indexing | [AGENTS](src/codomyrmex/agentic_memory/AGENTS.md) |
| **spatial** | 3D/4D world modeling | [AGENTS](src/codomyrmex/spatial/AGENTS.md) |
| **identity** | Multi-persona, bio-verification | [AGENTS](src/codomyrmex/identity/AGENTS.md) |
| **wallet** | Self-custody, recovery | [AGENTS](src/codomyrmex/wallet/AGENTS.md) |

---

## 🗂️ Document Hierarchy

```
codomyrmex/
├── TODO.md              ← This file (project backlog)
├── CHANGELOG.md         ← Historical releases (v1.2.4+)
├── AGENTS.md            ← Agent coordination
├── SPEC.md              ← Functional spec
├── README.md            ← Overview
├── SECURITY.md          ← Security policies
├── PAI.md               ← Personal AI Infrastructure
├── pyproject.toml       ← Package config (version: 1.2.7)
└── src/codomyrmex/      ← 128 modules
```

---

*Last updated: 2026-03-19 — Sprint 35 active.*
*Version: 1.2.8-draft*