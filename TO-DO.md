# Codomyrmex Project Roadmap & To-Do

**Status**: Active | **Last Updated**: February 21, 2026 | **Current**: v1.0.0 (implemented) | **Next**: v1.0.1

---

## Release Policy

> [!CAUTION]
> **No versioned release ships with failing tests. No exceptions.**
>
> 1. **0 test failures** — `pytest` exits 0 across entire suite
> 2. **0 collection errors** — `pytest --co -q` discovers all tests without import/fixture errors
> 3. **All new code tested** — zero-mock policy
> 4. **Documentation current** — CHANGELOG, README, SPEC, AGENTS reflect accurate counts
> 5. **`codomyrmex doctor --all` exit 0**

---

## Codebase Reality (audited Feb 21, 2026)

| Metric | Value | Notes |
| :--- | ---: | :--- |
| Top-level modules | 93 | Excluding tests, examples, output, htmlcov |
| `mcp_tools.py` files | 27 | +1 `agentic_memory` |
| `@mcp_tool` decorators | 138 | Across 45 files |
| Tests collected | 9,860 | 0 collection errors ✅ |
| Tests passing | 9,860 | **100% Zero-Mock Pass** |
| Pre-existing failures | 0 | |
| Coverage | ~28% | (last measured; needs re-audit) |
| Python 3.14+ compat | ✅ | stdlib `compression` collision fixed |

---

## Completed Releases (v0.1.3 → v1.0.0)

All releases below have passed their gates. Sprint details archived in git history and CHANGELOG.md.

| Version | Theme | Sprints | Cumulative Tests |
|---------|-------|---------|---------------:|
| v0.1.3–v0.1.9 | Foundation → Workflows | — | 9,400+ |
| v0.2.0 | Zero Failures | 1–6 | 8,881+ |
| v0.2.1 | Quality Floor | 7–10 | +253 |
| v0.3.0 | Active Inference (CoT, knowledge, code analysis) | 11–14 | +140 |
| v0.4.0 | Ant Colony (swarm, self-healing, MetaAgent) | 15–18 | +102 |
| v0.5.0 | Embodied Intelligence (deploy, codegen, triage) | 19–22 | +67 |
| v0.6.0 | Cognitive Autonomy (workflows, memory, planning) | 23–26 | +45 |
| v0.7.0 | Advanced Agent Capabilities (feedback loops, knowledge sharing) | 27–30 | +55 |
| v0.8.0 | Distributed Intelligence (transport, queues, events) | 31–34 | +60 |
| v0.9.0 | Production Hardening (API versioning, observability, docs) | 35–38 | +58 |
| v1.0.0 | General Availability (API freeze, perf cert, release cert) | 39–41 | — |

> [!NOTE]
> Sprints 1–41 code is implemented and merged. The CHANGELOG.md has full details for each release.

---

## 🔧 v1.0.1 — Next Actionable Steps

**Theme**: Hygiene, accuracy, and incremental hardening  
**Effort**: 1–2 focused sessions

### 1. Metrics & Documentation Sync (P0)

The TO-DO and root docs have stale numbers. Fix them to match reality.

- [x] Re-audit coverage: `pytest --cov=codomyrmex --cov-report=term-missing -q` → record real %
- [x] Update `README.md` with accurate test count (9,860), module count (93), MCP tool count (138/26)
- [x] Update `SPEC.md` with matching numbers
- [x] Verify `CHANGELOG.md` has v1.0.0 entry with final metrics
- [x] `codomyrmex doctor --all` exit 0

### 2. Tier-3 Module Promotion (P1)

Six modules near the 2,000 LOC Tier-2 threshold (from previous audit). Each needs ~200–500 LOC of real functional code:

| Module | Approx LOC | Gap |
|--------|-----------|-----|
| `performance` | ~1,800 | ~200 |
| `scrape` | ~1,600 | ~400 |
| `plugin_system` | ~1,600 | ~400 |
| `maintenance` | ~1,500 | ~500 |
| `logging_monitoring` | ~1,500 | ~500 |
| `cache` | ~1,200 | ~800 |

- [ ] Pick 2–3 nearest-threshold modules and add real functional files
- [ ] 1–2 tests per new file (zero-mock)

### 3. MCP Tool Coverage (P2)

26/93 modules have `mcp_tools.py`. High-value gaps:

- [ ] `agentic_memory/mcp_tools.py`: `memory_put`, `memory_get`, `memory_search`
- [ ] `collaboration/mcp_tools.py`: `swarm_submit_task`, `pool_status`
- [ ] `validation/mcp_tools.py`: `validate_schema`, `validate_config`

### 4. Test Suite Health (P2)

- [ ] Investigate ~170 skipped tests — reduce env-specific skips where possible
- [ ] Re-audit coverage per Tier-1 module, set `fail_under` gates
- [ ] Clean up any remaining deprecation warnings from `filterwarnings`

---

## 🔄 Technical Debt (active items only)

| Pri | Item | Metric | Status |
| :---: | :--- | :--- | :--- |
| **P0** | ~~Fix 74 test failures~~ | 0 failures | ✅ Done |
| **P0** | ~~Fix 249→9 collection errors~~ | 0 errors | ✅ Done (agentic_memory created) |
| **P1** | Root doc sync (stale counts) | no stale numbers | ✅ Done |
| **P1** | Tier-3 → Tier-2 promotions | ≤37 Tier-3 | v1.0.1 |
| **P1** | MCP tool coverage 26→30+ | `mcp_tools.py` count | v1.0.1 |
| **P2** | `mypy --strict` progressive | 0 errors on backbone | Ongoing |
| **P2** | Coverage re-audit (real %) | measured, gates set | v1.0.1 |
| **P3** | Documentation site (MkDocs) | auto-deploy | Future |
| **P3** | Event store compaction | JSONL size | Future |
