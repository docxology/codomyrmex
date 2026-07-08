# Thermo-Nuclear Code Quality Review — Codomyrmex

**Date:** 2026-07-05  
**Scope:** Whole-repo health (`projects/ongoing/codomyrmex`, v1.3.0)  
**Rubric:** thermo-nuclear-code-quality-review (cursor-team-kit)

## Executive verdict

**Pre-P0:** BLOCK — four production files >1k LOC, script-layer figure logic, namespace leak for manuscript tokens, Hermes MCP god-module.

**Post-P0 (this pass):** PARTIAL UNBLOCK — Hermes MCP surface decomposed; figure logic moved to `src/`; manuscript variables namespaced. Remaining BLOCK modules: `hermes_client.py` (1764 LOC), `_provider_router.py` (1138), `falsification_worker.py` (1111), `manuscript/figures/generators.py` (1995 — moved from scripts, per-figure split deferred).

**Post-P1 (2026-07-05 continuation):** **UNBLOCK on production >1k LOC** — all four remaining blockers split into subpackages; max production module ~566 LOC (`mcp_tools_pkg/status.py`).

**Post-P2 (2026-07-05):** Tests relocated to top-level `tests/`; coverage gate raised 40%→60%; evolution external_importers tests rewritten without mocks (116 passed); explicit figure imports; RASP README/AGENTS added for split packages.

---

## P0 remediations implemented

| Target | Before | After |
| --- | --- | --- |
| Hermes MCP | `mcp_tools.py` 2327 LOC | Shim 7 LOC + `mcp_tools_pkg/` (max 566 LOC/file) |
| Figure script | `scripts/generate_manuscript_figures.py` 1995 LOC | Script 12 LOC; logic in `src/codomyrmex/manuscript/figures/generators.py` |
| Manuscript variables | `src/manuscript_variables.py` 690 LOC | `src/codomyrmex/manuscript/variables.py` + 9 LOC compat shim |
| Tests | Monkeypatch `mcp_tools._get_client` | `_client._factory_override` hook |

New packages:

- `src/codomyrmex/agents/hermes/mcp_tools_pkg/` — memory, skills, execution, sessions, tasks, status
- `src/codomyrmex/manuscript/` — variables + figures

---

## P1 remediations implemented (2026-07-05)

| Target | Before | After |
| --- | --- | --- |
| Falsification | `falsification_worker.py` 1111 LOC | Shim 9 LOC + `falsification/` (checks per attack vector, max ~111 LOC/check) |
| Figure generators | `generators.py` 1995 LOC | `_common.py` + 10 per-figure modules (max ~281 LOC) + `orchestrator.py` |
| Hermes client | `hermes_client.py` 1764 LOC | Shim 9 LOC + `client_pkg/` mixins (max 334 LOC) |
| Provider router | `_provider_router.py` 1138 LOC | Shim 18 LOC + `provider_router_pkg/` (max 445 LOC) |

Verification (targeted):

- `test_falsification_worker.py` — 94 passed
- `test_manuscript_consistency.py` + `test_figures.py` — 32 passed
- `test_hermes_provider_router.py` + `test_agents_hermes_client.py` — 65 passed, 1 skipped
- `test_hermes_mcp_tools_extended.py` + `test_gateway_mcp_new_tools.py` — 73 passed

---

## Findings (rubric priority)

### 1. Structural regressions (blockers)

- ~~**Hermes client monolith**~~ — split into `client_pkg/` mixins (P1 done).
- ~~**Provider router**~~ — split into `provider_router_pkg/` (P1 done).
- ~~**Falsification worker**~~ — split into `falsification/checks/` (P1 done).
- ~~**Figure generators monolith**~~ — split into per-figure modules under `manuscript/figures/` (P1 done).
- ~~**Tests inside `src/`**~~ — relocated to top-level `tests/` with `tests/support/repo_paths.py` (P2 done).

### 2. Code-judo opportunities

- Mirror `mcp_tools_pkg/` categories in `hermes/client/` subpackage; MCP tools become one-line delegates.
- Split `generators.py` into `palette.py`, `loaders.py`, one file per `fig_*()` (~200 LOC each).
- Split `falsification_worker.py` by `AttackVector` registry (pattern used successfully in `colony_kernel` elsewhere).
- **Positive control:** `colony_kernel` — 11 focused files, clear models contract, strong tests.

### 3. Spaghetti / branching

- SIZE_OK waivers on `variables.py`, former figure script — revoke after decomposition.
- Documented zero-mock policy vs 237 grep hits (mostly comments + legacy evolution tests).
- Repeated figure preamble (`_save`, `_pub_style`, provenance) — extract shared helpers (P1).

### 4. Boundary / type-contract

- Fixed: manuscript tokens outside package namespace.
- Fixed: matplotlib in `scripts/`.
- Remaining: optional `inject_via_infrastructure` infra hook should stay inside package (done).

### 5. File-size summary (production >1000 LOC)

| File | LOC | Status |
| --- | ---: | --- |
| `manuscript/figures/generators.py` | 1995 | Moved to src; split P1 |
| `agents/hermes/hermes_client.py` | 1764 | P1 |
| `agents/hermes/_provider_router.py` | 1138 | P1 |
| `colony_kernel/falsification_worker.py` | 1111 | P1 |
| ~~`agents/hermes/mcp_tools.py`~~ | ~~2327~~ | **Resolved** → `mcp_tools_pkg/` |

---

## P1 / P2 waves (deferred)

| Priority | Item |
| --- | --- |
| P1 | Split `hermes_client.py` + `_provider_router.py` |
| P1 | Split `falsification_worker.py` by attack vector |
| P1 | Split `generators.py` per figure + registry |
| P2 | Relocate `src/codomyrmex/tests/` → top-level `tests/` | **Done** |
| P2 | Raise coverage gate 40% → 60% | **Done** (`pyproject.toml`, `Makefile`) |
| P2 | RASP gap closure for split packages | **Done** (README/AGENTS on falsification, figures, hermes subpackages) |
| P1 | Purge `unittest.mock` in evolution external_importers tests | **Done** (116 tests, lazy DSPy import) |

---

## Verification (this pass)

```bash
uv run pytest tests/unit/hermes/ tests/unit/agents/ tests/unit/colony_kernel/ -q
uv run pytest tests/unit/manuscript/test_figures.py -q
uv run pytest src/codomyrmex/agents/hermes/evolution/tests/core/test_external_importers.py \
  --override-ini="addopts=" --rootdir=src/codomyrmex/agents/hermes/evolution -q
```

Hermes + colony_kernel: **1203+ passed** after P0 fixes.

---

## Appendix A — Metrics baseline

| Metric | Value |
| --- | --- |
| Top-level modules | 129 (+1 `manuscript` package) |
| Production `@mcp_tool` decorators | 610 |
| Pytest collected | 35,137 |
| Coverage gate | 40% |
| Hermes+kernel targeted coverage | 55.6% |
| Mock-policy grep hits | 237 across 216 files |
| RASP doc gaps | 257 dir-rows; 248 missing AGENTS.md under `src/codomyrmex/` |
| Production LOC (excl. tests) | ~375k |

Regenerate inventory: `uv run python scripts/doc_inventory.py --pytest`

---

## Appendix B — 129-module rollup

Full table: [thermo-nuclear-module-rollup-2026-07-05.md](thermo-nuclear-module-rollup-2026-07-05.md)

**Summary:** 130 modules | BLOCK=3 (`agents`, `colony_kernel`, `manuscript`) | under-covered=12 | OK=115

BLOCK modules after P0:

- `agents` — max file now `hermes_client.py` (1764), not MCP tools
- `colony_kernel` — `falsification_worker.py` (1111)
- `manuscript` — `figures/generators.py` (1995)

---

## Appendix C — Hermes MCP layout

```
src/codomyrmex/agents/hermes/
  mcp_tools.py              # 7-line shim
  mcp_tools_pkg/
    _client.py              # factory + _factory_override for tests
    memory.py               # 6 tools
    skills.py               # 8 tools
    execution.py            # 7 tools
    sessions.py             # 11 tools
    tasks.py                # 6 tools
    status.py               # 17 tools
```

Public imports unchanged: `from codomyrmex.agents.hermes import mcp_tools`.
