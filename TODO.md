<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.2.8-draft | **Date**: 2026-03-24 | **Modules**: 128 | **Sprint**: 35

> **Current release**: v1.2.7 "Multi-Agent Swarm Orchestration" (2026-03-19).
> **Next release**: v1.2.8 (Sprint 35)
> **Archived**: v1.2.4–v1.2.7 → [CHANGELOG.md](CHANGELOG.md)

---

## 📊 Measured Metrics (2026-03-24)

> All values below are **measured**, not estimated. Command and timestamp documented.

| Metric | Value | Command |
| :--- | :--- | :--- |
| **Tests collected** | **35,916** (0 errors) | `uv run pytest --collect-only --no-cov -q` |
| **Ruff errors** | **0** | `uv run ruff check .` |
| **ty diagnostics** | **296** | `uv run ty check src/` |
| **Mock violations** | **0** | `grep -rc "from unittest.mock" src/ --include="*.py" \| grep -v ":0$"` |
| **MCP tool decorators** | **600** | `uv run python scripts/doc_inventory.py` (production tree; lines starting with `@mcp_tool`) |
| **Top-level modules** | **128** | `find src/codomyrmex -maxdepth 1 -type d` |
| **pyproject.toml version** | **1.2.7** | `grep version pyproject.toml \| head -1` |

---

## ✅ v1.2.8.0 — Sprint 35 Core (Complete)

| # | Deliverable | Module | Status | Technical Detail |
| :--- | :--- | :--- | :--- | :--- |
| v1.2.8.1 | **Hermes v0.4.0 FastMCP scaffolding** | `agents/hermes/` | ✅ Done | Integrated `optional-skills/mcp/fastmcp/scaffold_fastmcp.py` via `HermesClient.scaffold_fastmcp()` and MCP tool `hermes_fastmcp_scaffold` for Codomyrmex→Hermes MCP exposure |
| v1.2.8.2 | **Hermes Session Race Guards** | `agents/hermes/session.py` | ✅ Done | `SessionRaceGuard` with context manager, `SessionGuardContext`, granular threading.Lock per session_id. Tests: 10 passing (zero-mock) |
| v1.2.8.3 | **Webhook platform adapter** | `agents/hermes/gateway/platforms/webhook.py` | ✅ Done | `WebhookAdapter` with HMAC-SHA256 verification, GitHub PR/Commit/Issue payload parsing, prompt templates, implements `GatewayAdapter` protocol |
| v1.2.8.4 | **Webhook config schema** | `agents/hermes/gateway/platforms/webhook.py` | ✅ Done | `WebhookConfig(port: int, routes: dict, host: str)`, `WebhookRoute(secret, prompt_template, handler)` matching schema requirements |
| v1.2.8.5 | **Dynamic context window resolution** | `agents/hermes/_provider_router.py` | ✅ Done | `ModelContextRegistry` with OpenRouter API fallback, 11 known model defaults, thread-safe `get_context_length_safe()` |
| v1.2.8.6 | **ContextCompressor token eviction** | `agents/hermes/_provider_router.py` | ✅ Done | `CAPACITY_THRESHOLD=0.8` (80%), model_id property setter with error handling, integrates with registry for dynamic max_tokens |

---

## 🚀 v1.2.8 — Sprint 35 Unreleased

> Items from `[Unreleased]` in [CHANGELOG.md](CHANGELOG.md), pending tag.

| # | Deliverable | Module | Status | Technical Detail |
| :--- | :--- | :--- | :--- | :--- |
| v1.2.8.7 | **Hermes FastMCP scaffold lane** | `agents/hermes/` | ✅ Done | Bundled scaffold script at `optional-skills/mcp/fastmcp/scaffold_fastmcp.py` for Codomyrmex↔Hermes MCP exposure |
| v1.2.8.8 | **DAF Paperclip v0.4.1** | `projects/daf-consulting` | ✅ Done | Health-attempt telemetry, bootstrap audit CLI, end-to-end zero-mock CLI coverage |
| v1.2.8.9 | **Code Health sweep** | repo-wide | ✅ Done | 446 ruff diagnostics fixed, Zero-Mock enforcement (removed legacy `open_gauss` mock adapters) |
| v1.2.8.10 | **Zero-Mock hardening** | `tests/` | ✅ Done | Eliminated 4 remaining `unittest.mock` imports across `test_cognilayer_bridge.py`, `test_mission_control_client.py`, `test_gateway_coverage_loop.py`, `test_rotation.py` |
| v1.2.8.11 | **Ghost architecture bug fix** | `agents/ghost_architecture/model.py` | ✅ Done | Fixed `nn.ModuleDict.get()` → dict-style access pattern; PyTorch `ModuleDict` does not support `.get()` |
| v1.2.8.12 | **Hermes 0.4.0 Upstream Sync** | `agents/hermes/` | ✅ Done | Synchronized workspace with Hermes v0.4.0, upgraded dependencies via `uv lock --upgrade`, verified agent test stability. |

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
| B3 | **Video module depth** | `video/` | Partial impl (processor, extractor, analyzer, transcription paths); not a thin stub — see `video/README.md` / `SPEC.md` |
| B4 | **Meme module MCP exposure** | `meme/` | Experimental, needs RASP + `@mcp_tool` |
| B5 | **Secure Cognitive Layer MCP** | `identity/`, `wallet/`, `defense/`, `market/`, `privacy/` | Not MCP-exposed via PAI bridge |
| B6 | ~~Test collection errors~~ | `tests/` | ✅ Fixed — 64→0 errors via import guards in `crypto/currency/__init__.py` and `data_visualization/engines/__init__.py` |
| B7 | ~~README metric drift~~ | root | ✅ Fixed — aligned with [docs/reference/inventory.md](docs/reference/inventory.md) (35,916 tests, 600 MCP `@mcp_tool` lines) |
| B8 | **Coverage gate** | repo-wide | **40%** in `[tool.coverage.report] fail_under`; `meme/*` omitted from `[tool.coverage.run]`. Enforce with `make test` or `--cov-fail-under=40`. Re-verify after substantive changes. |

---

## 🎯 Release Criteria

> **Strict Delivery Requirements** — All items must pass before tagging v1.2.8:

| Requirement | Command | Threshold | Status |
| :--- | :--- | :--- | :--- |
| **Zero-Mock Policy** | `grep -rc "from unittest.mock" src/ --include="*.py" \| grep -v ":0$"` | 0 `unittest.mock` imports | ✅ PASSED (0 violations) |
| **Full Test Pass** | `uv run pytest` | Exit code 0 (default run has no `--cov`; does not check the 40% gate) | 🟡 PENDING (0 collection errors; needs full run) |
| **Code Health** | `uv run ruff check .` | 0 errors | ✅ PASSED (0 errors) |
| **Type Safety** | `uv run ty check src/` | <1,000 diagnostics | ✅ PASSED (296 diagnostics) |
| **Coverage Gate** | `make test` or `uv run pytest src/codomyrmex/tests/ ... --cov-fail-under=40` | ≥40% | 🟡 Confirm on CI / local green run — `meme/*` omitted from coverage (`pyproject.toml`); one dev unit+cov snapshot showed ~73% of ~135k statements (Mar 2026) |
| **Documentation Parity** | — | AGENTS.md, README.md, SPEC.md, CHANGELOG.md aligned with pytest/coverage source of truth | ✅ Updated (pytest → `pyproject.toml`; CI `coverage-gate`; `meme` omit) |

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
| **Test** | `uv run pytest` (no coverage) · `make test` (with `--cov` + 40% gate) |
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

*Last updated: 2026-03-23 — Sprint 35 active.*
*Version: 1.2.8-draft*
