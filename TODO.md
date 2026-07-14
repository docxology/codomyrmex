<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.4.0-rc6 | **Date**: 2026-07-14 | **Modules**: 130 | **Sprint**: 41 publication and enforcement verification

> **Current release**: v1.4.0-rc6 "Colony Kernel enforcement" (candidate, 2026-07-14).
> **Next release**: v1.4.0 (held for provider evaluation and immutable release verification)
> **Archived**: v1.2.4–v1.2.8 → [CHANGELOG.md](CHANGELOG.md)

## 🔬 v1.4.0-rc6 — First-principles publication checkpoint

This candidate is an auditable release candidate, not a completed production-safety claim. The strict
profile governs only its explicit action-scope map; unregistered mutating paths remain bypasses. The
follow-up audit is recorded in
[`review_artifacts/Codomyrmex_RedTeam_FirstPrinciples_Science_Follow_Up_2026-07-14.md`](review_artifacts/Codomyrmex_RedTeam_FirstPrinciples_Science_Follow_Up_2026-07-14.md).

| Gate | Current evidence | Status |
| :--- | :--- | :--- |
| Scoped Colony Kernel suite | 826 selected and passed; 0 skipped, failed, or errored (827 collected, 1 deselected) | ✅ Measured |
| Branch coverage | 74.37185929648241% (592/796 branches; 82.59604190919674% line coverage) | ✅ Above 60% floor |
| Clean-clone PDF replay | `output/paper.pdf` hash `69fdbb018d81b7b5dd0ae170187842ef30647b8f6864af91f615fa23ea6ac706` at the tagged candidate | ✅ Byte-for-byte match |
| Clean-clone evidence replay | HTML, variables, coverage JSON, JUnit XML, and status JSON also match the candidate | ✅ Byte-for-byte match |
| Verifier integrity | Commit/tag, source/config, freshness, JUnit/status, and artifact hashes independently checked; clean clone has no status output | ✅ Measured |
| Provider benchmark | Concrete provider/model, raw receipts, and result artifact absent | ⛔ Open (R-20) |
| Immutable final publication | A-001 and A-016 remain open | ⛔ Open |

The benchmark gap is intentionally fail-closed. Fixture adapter output is contract evidence only and is
not a substitute for the predeclared controlled and SWE-bench Lite experiment.

---

## 📊 Measured Metrics (2026-07-02)

> All values below are **measured**, not estimated. Command and timestamp documented.

| Metric | Value | Command |
| :--- | :--- | :--- |
| **Tests collected** | **34,988** (0 errors) | `uv run python scripts/doc_inventory.py --pytest` |
| **Ruff errors** | **0** | `uv run ruff check .` |
| **ty diagnostics** | **0** | `uv run ty check --output-format concise src/` |
| **Mock violations** | **0** | `rg -n "from unittest\\.mock" src --glob '*.py'` |
| **MCP tool decorators** | **623** | `uv run python scripts/doc_inventory.py` (production tree; lines starting with `@mcp_tool`) |
| **Top-level modules** | **130** | `uv run python scripts/doc_inventory.py --pytest` |
| **pyproject.toml version** | **1.3.0** | `grep version pyproject.toml \| head -1` |
| **AGENTS validation** | **1,342 / 1,342 valid** | `make docs-check` |
| **Doc triple-check debt** | **0 files with issues; 0 broken links; 0 placeholders; 0 completeness issues** | `make docs-check` |
| **RASP doc gaps** | **10 dir-rows with gaps; 6 missing both README/AGENTS** | `uv run python scripts/rasp_gap_report.py` |

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
| v1.2.8.12 | **Hermes 0.4.0 Upstream Sync** | `agents/hermes/` | ✅ Done | Synchronized workspace with Hermes v0.4.0, upgraded dependencies via `uv lock --upgrade`, verified agent test stability. |
| v1.2.8.13 | **Repo health orchestration sweep** | repo-wide | ✅ Done | Repaired Make/just docs targets, made `triple_check.py` repo-root aware, added Docusaurus module-link fixer, restored ignored-but-required docs, guarded optional submodule tests, and tightened `agents/pooling/FallbackChain` type behavior. |
| v1.2.8.14 | **Type safety zero baseline** | repo-wide | ✅ Done | Burned down production and test `ty` diagnostics to 0 via typed dictionary shapes, optional SDK import guards, correct agent override signatures, safer monkeypatching, and explicit optional-result assertions. |
| v1.2.8.15 | **Documentation placeholder burn-down** | repo-wide docs | ✅ Done | Tightened triple-check marker detection, skipped `.gitmodules` vendor trees, repaired 2,296 generated README/AGENTS generic purpose lines, and verified `make docs-check`: 0 placeholders, 0 broken links, 1,342/1,342 AGENTS valid. |
| v1.2.8.16 | **Documentation completeness zero baseline** | repo-wide docs | ✅ Done | Added `repair_triple_check_completeness.py`, repaired 2,718 README/AGENTS/SPEC completeness gaps outside submodules, and verified `make docs-check`: 4,911 docs checked, 0 files with issues, 1,342/1,342 AGENTS valid. |

---

## 🌱 Colony Kernel — v1.3.0 Sprint 36

| # | Deliverable | Module | Status | Technical Detail |
| :--- | :--- | :--- | :--- | :--- |
| v1.3.0.1 | **Pheromone Store** | `colony_kernel/pheromone_store.py` | ✅ Done | Append-only pressure log: `emit(signal, intensity, source)` → eviction queue; `read_gradient(signal)` returns sorted `(timestamp, intensity, source)` tuples; SQLite-backed, thread-safe |
| v1.3.0.2 | **Resource Ledger** | `colony_kernel/resource_ledger.py` | ✅ Done | Double-entry resource accounting: `credit/debit(resource, amount, agent_id)` → `LedgerEntry`; `balance(resource)` enforces non-negative invariant; persisted via `SQLiteStore` |
| v1.3.0.3 | **Actuation Gate** | `colony_kernel/actuation_gate.py` | ✅ Done | Three-valued gate: `+1` (approve), `0` (defer), `-1` (veto); policy chain evaluates resource headroom + role clearance + consequence history; `ActuationDecision` dataclass with rationale |
| v1.3.0.4 | **Consequence Memory** | `colony_kernel/consequence_memory.py` | ✅ Done | Action→outcome record: `record(action_id, outcome, delta_resources, signal_changes)`; `recall(action_type, k)` returns ranked `ConsequenceRecord` list for gate policy |
| v1.3.0.5 | **Role Adapter** | `colony_kernel/role_adapter.py` | ✅ Done | Dynamic role assignment: `assign(agent_id, role, constraints)` with quorum check; `revoke`; `list_by_role`; roles carry clearance bitmask used by actuation gate |
| v1.3.0.6 | **Pruning Daemon** | `colony_kernel/pruning_daemon.py` | ✅ Done | Background eviction: configurable TTL per signal class; runs as `asyncio.Task`; emits `pruned` event on removal; `stop()` is graceful with drain timeout |
| v1.3.0.7 | **Falsification Worker** | `colony_kernel/falsification_worker.py` | ✅ Done | Conjecture stress-tester: pulls proposals from pheromone store, applies registered `Falsifier` callables, writes `FalsificationResult` to consequence memory; zero-mock (real callable chain) |
| v1.3.0.8 | **Kernel + MCP Tools** | `colony_kernel/__init__.py` + `colony_kernel/mcp_tools.py` | ✅ Done | `ColonyKernel` assembles all 8 subsystems; 8 `@mcp_tool` decorators: `colony_propose_action`, `colony_record_outcome`, `colony_agent_profile`, `colony_status`, `colony_pheromone_query`, `colony_falsify_plan`, `colony_pruning_report`, `colony_tick` |

---

## 🔭 v1.2.9+ — Horizon (Unscoped)

> **Theme**: Cryptographic persistence, spatial world modeling, omnimodal processing.

| # | Direction | Builds On | Concrete Next Step |
| :--- | :--- | :--- | :--- |
| R1 | **Spatial World Models** ✅ | `spatial/` | ✅ Done — `Trajectory4D`/`TrajectoryPoint4D` 4D time-series in `world_models/`, `render_agent_trial` + `summarize_trial` with quadray integration, `spatial_render_agent_trial` `@mcp_tool`; 41 new tests (zero-mock) |
| R2 | ~~Self-Custody Wallet~~ | `wallet/` | ✅ Fixed — `zk_proof.py` with `ZKProofVerifier`, `SignedCapabilityProofBuilder`; 2 new `@mcp_tool` decorators (`wallet_generate_zk_proof`, `wallet_verify_zk_proof`); 44 tests pass |
| R3 | ~~Identity & Persona~~ | `identity/` | ✅ Fixed — `HeartbeatValidator` with RMSSD/SDNN/mean_hr metrics + enrollment, `EEGFrequencyAnalyzer` with band power analysis, `PersonaRotation` system; 2 new `@mcp_tool` decorators; 22 tests pass |

---

## 📋 Backlog — Unscoped / Triaging

| # | Item | Module | Notes |
| :--- | :--- | :--- | :--- |
| B1 | ~~Tool versioning UI~~ | `model_context_protocol/` | ✅ Fixed — `deprecated_in` metadata now surfaced via `get_deprecated_tools()`, `get_deprecation_timeline()`, `get_deprecation_summary()` exported from `model_context_protocol.__init__` |
| B2 | ~~Oversized files audit~~ | `orchestrator/` | ✅ Fixed — refactored `thin.py` (549→focused submodules: `_decorators.py`, `_shell_exec.py`, `_batch_chain.py`); largest file now 514 LOC (`workflow.py`); no files >800 LOC |
| B3 | ~~Video module depth~~ | `video/` | ✅ Audited — video processor, extractor, analyzer, and transcription paths all implemented; 207 tests pass, 1 skip (optional dep) |
| B4 | ~~Meme module MCP exposure~~ | `meme/` | ✅ Fixed — 5 `@mcp_tool` decorators in `mcp_tools.py` (dissect, fitness, synthesize, propagate, narrative); RASP docs present |
| B5 | ~~Secure Cognitive Layer MCP~~ | `identity/`, `wallet/`, `defense/`, `market/`, `privacy/` | ✅ Fixed — PAI bridge module `pai_pm/secure_cognitive_bridge.py` registers all 15 MCP tools (3 per module × 5 modules); `register_secure_cognitive_tools()` + `get_secure_cognitive_tool_catalog()` |
| B6 | ~~Test collection errors~~ | `tests/` | ✅ Fixed — 35,119 tests collect with 0 errors via import guards and optional submodule skips |
| B7 | ~~README / inventory metric drift watch~~ | root | ✅ Fixed — updated all surfaces to 130 modules, 1,201 docs; manuscript consistency test updated |
| B8 | ~~Coverage gate~~ | repo-wide | ✅ Verified — **60%** in `[tool.coverage.report] fail_under` (raised from 40%); `meme/*` omitted from `[tool.coverage.run]`. Enforce with `make test` or `--cov-fail-under=60`. |
| B9 | ~~Type safety burn-down~~ | repo-wide | ✅ Fixed — `uv run ty check --output-format concise src/` now reports 0 diagnostics. Keep this zero baseline in CI/local gates. |
| B10 | ~~Documentation completeness burn-down~~ | `docs/`, `src/codomyrmex/**` | ✅ Fixed — `make docs-check` reports 4,911 docs checked, 0 placeholders, 0 broken links, 0 completeness issues, and 1,342/1,342 AGENTS valid. |

---

## 🎯 Release Criteria

> **Strict Delivery Requirements** — All items must pass before tagging v1.2.8:

| Requirement | Command | Threshold | Status |
| :--- | :--- | :--- | :--- |
| **Zero-Mock Policy** | `rg -n "from unittest\\.mock" src --glob '*.py'` | 0 `unittest.mock` imports | ✅ PASSED (0 violations) |
| **Full Test Pass** | `uv run pytest` | Exit code 0 (default run has no `--cov`; does not check the 60% gate) | 🟡 PENDING (35,119 tests collected with 0 errors; build_synthesis + colony_kernel + integration suites verified green) |
| **Code Health** | `uv run ruff check .` | 0 errors | ✅ PASSED (0 errors) |
| **Type Safety** | `uv run ty check --output-format concise src/` | 0 diagnostics | ✅ PASSED (0 diagnostics) |
| **Coverage Gate** | `make test` or the scoped release command with `--cov-fail-under=60` | ≥60% | ✅ PASSED — `fail_under = 60` in `pyproject.toml`; `meme/*` omitted from coverage; current Colony Kernel release coverage is 74.37185929648241% branch (592/796) |
| **Documentation Parity** | `make docs-check` | AGENTS.md, README.md, SPEC.md, CHANGELOG.md aligned with pytest/coverage source of truth | ✅ PASSED (0 placeholders, 0 broken links, 0 completeness issues, AGENTS validation passes) |

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
| **Test** | `uv run pytest` (no coverage) · `make test` (with `--cov` + 60% gate) |
| **Lint** | `uv run ruff check .` |
| **Format** | `uv run ruff format .` |
| **Type Check** | `uv run ty check --output-format concise src/` |
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
├── pyproject.toml       ← Package config (version: 1.3.0)
└── src/codomyrmex/      ← 130 modules
```

---

*Last updated: 2026-07-09 — Sprint 37 publication hardening active.*
*Version: 1.3.0-draft*
