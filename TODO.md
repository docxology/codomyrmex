# Codomyrmex — Master Project Backlog

**Version**: v1.0.5 | **Last Updated**: March 2026 | **Active Sprint**: 14+

This is the authoritative project backlog. Updated after each wave/sprint. Sprint history at bottom.

---

## 🔴 CRITICAL (blocking / must fix now)

- [x] Fix `__init__.py` version: `1.0.3.dev0` → `1.0.5` *(Wave 2 — done)*
- [x] Create `.github/CONTRIBUTING.md` *(Wave 2 — done)*
- [x] Create top-level `TODO.md` *(Wave 2 — done)*
- [x] Fix Gemini workflows — created `.gemini/` directory with 5 prompt files *(Wave 2 — done)*
- [x] **`model_context_protocol/transport/server.py`** — 0% → 60%+ test coverage, new `test_server_coverage.py` *(Sprint 14)*
- [ ] **Ratchet coverage gate** from `fail_under=68` → 70% (Sprint 15: +21 health_handler tests; need full-suite verification ≥70% before bumping gate)
- [ ] **Resolve ~35 circular import pairs** (Sprint 4 target, still open)

---

## 🟠 HIGH (next sprint targets)

### Documentation — Wave 2 COMPLETE ✅ *(March 2026)*

All RASP documentation enrichment complete across all 88 modules:

- [x] **PAI.md version headers** — all 88 bumped to `v1.0.5 | March 2026`
- [x] **AGENTS.md Agent Role Access Matrix** — added to all 88 modules (was 9/88)
- [x] **README.md PAI Integration section** — added to all 88 modules (was 6/88)
- [x] **PAI.md MCP Tools table** — added to all 88 modules (was 30/88)
- [x] **SPEC.md expansion** — 4 of 8 stub files expanded (agentic_memory, bio_simulation, ci_cd_automation, config_management); 4 pending (finance, model_context_protocol, physical_management, system_discovery)

### Documentation — SPEC.md Expansion COMPLETE ✅ *(March 2026)*

All 8 stub SPEC.md files expanded to 143-190 lines with Error Conditions, Data Contracts, Performance SLOs, Design Constraints, and PAI Algorithm Integration sections:

- [x] `agentic_memory/SPEC.md` — 49 → 143 lines
- [x] `bio_simulation/SPEC.md` — 43 → 162 lines
- [x] `ci_cd_automation/SPEC.md` — 49 → 159 lines
- [x] `config_management/SPEC.md` — 49 → 181 lines
- [x] `finance/SPEC.md` — 43 → 167 lines
- [x] `model_context_protocol/SPEC.md` — 49 → 172 lines
- [x] `physical_management/SPEC.md` — 49 → 190 lines
- [x] `system_discovery/SPEC.md` — 49 → 177 lines

### MCP Coverage (48+ modules missing `mcp_tools.py`)

Modules with no MCP exposure — invisible to the PAI bridge:

| Module Group | Modules |
|---|---|
| Infrastructure | `api`, `auth`, `cache`, `ci_cd_automation`, `deployment`, `environment_setup` |
| Data / Storage | `database_management`, `serialization`, `vector_store` |
| AI / ML | `feature_flags`, `model_ops`, `prompt_engineering`, `tool_use`, `evolutionary_ai` |
| Code Quality | `static_analysis`, `testing`, `tree_sitter`, `pattern_matching` |
| Developer Tools | `cli`, `ide`, `terminal_interface`, `templating`, `utils` |
| Comms / Media | `audio`, `video`, `dark`, `documents`, `fpf` |
| Security | `encryption`, `defense`, `privacy` |
| Platform | `edge_computing`, `networking`, `physical_management`, `quantum` |
| Misc | `bio_simulation`, `finance`, `graph_rag`, `identity`, `logistics`, `market`, `meme`, `simulation`, `spatial`, `wallet` |

### Type Checking

- [x] Add `py.typed` markers across all modules with type hints (PEP 561) — **88/88 modules complete** (Sprint 15)
- [ ] Check and complete type hint coverage: `cerebrum/`, `events/`, `search/`, `config_management/`, etc.

### Ruff Violations — Sprint 15 COMPLETE ✅ *(March 2026)*

- [x] Reduced 1,531 → 607 violations (-60.4%, Sprint 14)
- [x] Fixed all F821 source bugs, UP042 StrEnum, E721, B004, B005, B025, B006, B017, B023, B028, F811, F601, F402, B018, B027, UP022, UP036
- [x] **Sprint 15: 607 → 43 violations** (−93% from Sprint 14): all TID252 (241 relative imports → 0), all E402 (160 imports not at top → 0) eliminated across 107+ files
- [x] Remaining 43: F405 star-import usage in `physical_management/__init__.py` and `spatial/three_d/__init__.py` — structural, not fixable without major refactoring
- [x] Fixed circular import in `ide/__init__.py` (CursorClient deferred post class-defs with `# noqa: E402`)
- [x] Fixed seaborn heatmap `xticklabels=None` TypeError in `data_visualization/engines/advanced_plotter.py`
- [x] Fixed `test_task_master.py` ANTHROPIC_API_KEY isolation (collection-time `skipif` → execution-time `autouse` fixture)

---

## 🟡 MEDIUM (notable enhancement, 2-4 sprint horizon)

### Documentation — PAI.md MCP Tools Tables

- [x] All 88 modules have `## MCP Tools` section *(Wave 2 — done)*
- Modules with MCP tools have full tool tables (git_analysis 16 tools, email 12 tools, etc.)
- Modules without MCP tools have "not exposed" placeholder with import/CLI guidance

### Rules Submodule Enhancements (agentic_memory/rules/)

- [ ] Add `rules_get_section` MCP tool — retrieve specific section from a rule
- [ ] Add `rules_search` MCP tool — full-text search across all rule content
- [ ] Add `RuleRegistry.list_all_rules()` — return all 75 rules sorted by priority
- [ ] Cache warm-up option: `RuleEngine.__init__(preload=True)` — loads all rules on startup
- [ ] Rule content validation script — verify all 75 `.cursorrules` files have sections 0-7
- [ ] Add `py.typed` to `agentic_memory/rules/`

### Memory Integration

- [ ] Integrate `RuleEngine` into `MemoryConsolidator` — rule-aware importance thresholds
- [ ] Add optional `context_rules` param to `memory_search` MCP tool

### API Completeness

- [ ] Export `RuleLoader`, `RuleRegistry`, `RuleSection` from `agentic_memory/__init__.py`
- [ ] Add `rules_list_cross_module` MCP tool
- [ ] Add `rules_list_file_specific` MCP tool

### Test Coverage Gaps

- [ ] Cover `model_context_protocol/transport/server.py` (654 LOC, 0% — HIGHEST PRIORITY)
- [ ] Cover `email/provider.py` (currently 0%)
- [ ] Cover `agents/droid/run_todo_droid.py` (currently 0%)
- [ ] Add caching behavior tests in `test_rules.py` (registry `_cache` hit/miss)
- [ ] Add path normalization tests (relative/absolute/filename-only)
- [ ] Fix ~5 remaining `xfail` markers (verify if bugs are now fixed)

### Architecture Debt

- [ ] Fix oversized files — 8 files > 1K LOC (identify top after `mcp_bridge.py` refactor)
- [ ] Enable bidirectional comms: codomyrmex → PAI (currently filesystem only)
- [ ] Surface `deprecated_in` metadata from `@mcp_tool` in MCP tool list UI
- [ ] `logistics/orchestration/project` class-based MCP pattern — add auto-discovery or document clearly

---

## 🟢 LOW (nice-to-have, backlog)

### GitHub Actions

- [ ] Add SBOM (Software Bill of Materials) generation workflow
- [ ] Add Lighthouse/performance budget enforcement for website
- [ ] Add automated changelog generation linked to `release.yml`
- [ ] Verify 5 Gemini workflows are functional (API key + integration health check)

### Documentation

- [ ] Create `docs/ARCHITECTURE.md` — visual Mermaid layer diagram
- [ ] Expand `docs/getting-started/` with more tutorials (currently only `connecting-pai.md`)
- [ ] Auto-generate rule index table in `rules/README.md` from live filesystem scan
- [ ] Cross-reference rules to corresponding `AGENTS.md` files

### Developer Experience (Rules)

- [ ] `codomyrmex rules list` CLI command
- [ ] `codomyrmex rules check <file>` — print applicable rules for a given file path
- [ ] Graphical rule hierarchy viewer (mermaid): `RuleEngine.visualize()`

### Code Quality

- [ ] Desloppify score: 63.1 → 70+ overall (baseline March 2026)
- [ ] Reduce `# noqa` suppressions: 55,265 → < 50,000
- [ ] Address top "Smells" category (2,269 issues)
- [ ] Address top "Facade" category (1,993 issues)
- [ ] Property-based tests for `RuleLoader._parse_sections` using `hypothesis`

### Infrastructure

- [ ] Add WebSocket support to dashboard (currently 15s polling; replace with real-time push)
- [ ] Website telemetry: add alerting/notification when metrics drift from baseline

---

## ✅ COMPLETED — Sprint History

### Wave 2 (March 2026)
- [x] Fix `__init__.py` version: `1.0.3.dev0` → `1.0.5`
- [x] Create `.github/CONTRIBUTING.md`
- [x] Create this `TODO.md` as comprehensive master backlog
- [x] Fixed all `~/.claude/skills/PAI/` → `~/.claude/PAI/` refs (~30 docs/ files)
- [x] Added PAI Integration sections to 6 module READMEs (security, llm, orchestrator, git_operations, documentation, formal_verification)
- [x] Added PAI Agent Role Access Matrix to 9 AGENTS.md files
- [x] Fixed Algorithm version `v1.5.0` → `v3.5.0` in all mermaid diagrams
- [x] Updated docs/pai/api-reference.md PAIConfig table (v4/v3 legacy notation)
- [x] Fixed hub file versions: README.md, PAI.md, src/codomyrmex/PAI.md → v1.0.5 / March 2026
- [x] Added `## PAI Integration` table to root README.md (7-phase Algorithm table)
- [x] Updated root README.md test badge to 16,190, coverage gate reference to 68%

### Sprint 15 (March 2026) — Ruff Cleanup, Bug Fixes & Coverage
- [x] **TID252 eliminated**: 241 relative parent imports converted to absolute across 107 source files
- [x] **E402 eliminated**: 160 "imports not at top" fixed across 120+ files (logger placement, cli_commands, docstring order)
- [x] Ruff total: 607 → 43 violations (93% reduction; only F405 structural star imports remain)
- [x] Fixed circular import in `ide/__init__.py` — CursorClient deferred with `# noqa: E402`
- [x] Fixed seaborn `xticklabels=None` TypeError (→ `"auto"`) in `advanced_plotter.py`
- [x] Fixed `test_task_master.py` ANTHROPIC_API_KEY collection-time skip → execution-time `autouse` fixture
- [x] Fixed `orchestrator/execution/runner.py` `queue.empty()` race condition → `queue.get(timeout=5)` (fixes flaky multiprocessing tests)
- [x] Added 21 new health_handler tests (`test_health_handler.py`): coverage 62% → 94%
- [x] Added missing `py.typed` markers for `docs_gen`, `git_analysis`, `release` (now 88/88 modules have py.typed)

### Sprint 14 (March 2026) — Rules Submodule
- [x] Moved `cursorrules/` → `src/codomyrmex/agentic_memory/rules/` via `git mv`
- [x] Created Python API: `RuleEngine`, `RuleLoader`, `RuleRegistry`, `RulePriority`, `Rule`, `RuleSet`, `RuleSection`
- [x] Added 3 MCP tools: `rules_list_modules`, `rules_get_module_rule`, `rules_get_applicable`
- [x] 30 zero-mock tests passing for rules submodule
- [x] Updated `agentic_memory/PAI.md` and `README.md` with new rules tools
- [x] Updated parent `agentic_memory/__init__.py` with `Rule`, `RuleEngine`, `RulePriority`, `RuleSet` exports

### Sprint 13 (March 2026) — Code Quality
- [x] Ruff violations: 1,878 → 1,531 (−347, −18.4%), 478 auto-fixes
- [x] 80 B904 exception chaining violations fixed
- [x] 6 F821 source bugs fixed (dead code, wrong var names, missing imports)
- [x] +44 new website tests (accessibility 14-33% → 75%+, proxy handler 68% → 81%)
- [x] Coverage gate set to `pyproject.toml fail_under=68`
- [x] Fixed ruff-introduced concatenated import regression in `ide/__init__.py`

### Sprint 9–12 (Feb-Mar 2026)
- [x] Coverage gate ratcheted 65% → 67% → 68%
- [x] ~16,190+ tests collected total
- [x] 50 false-positive skip guards removed; scraper URL validation bug fixed
- [x] Zero-Policy compliance: 38 violations fixed across 32 files (Sprint 8)
- [x] ~926 new tests; droid_manager 0% → 87%, cache_manager 0% → 91%
- [x] 76 PAI skills installed (18 new Codomyrmex-specific skills)

### Sprint 6-7 (Feb 2026)
- [x] 1,414 new tests via 18 parallel agents; 2 source bugs fixed (futures.wait dict, max_workers=0)
- [x] 4 xfail markers removed; 113 weak assertions replaced
- [x] pipeline/manager.py concurrent.futures.wait(dict) bug fixed

### Sprint 4-5 (Feb 2026)
- [x] 2,053 new tests in 34 new files
- [x] 12 missing `__init__.py` added; 9 stub RASP docs populated
- [x] Fixed 8 AsyncProfiler failures (`@AsyncProfiler.profile` instance pattern)

### Sprint 1-3 (Feb 2026)
- [x] Core agent framework: BaseAgent, AgentOrchestrator, SessionManager
- [x] MCP bridge: 171 tools (167 safe + 4 destructive), 33 auto-discovered modules
- [x] Trust gateway: UNTRUSTED → VERIFIED → TRUSTED state machine
- [x] PAI v4.0.1 integration: filesystem layout `~/.claude/PAI/` established
- [x] Algorithm v3.5.0 integration via SKILL.md loading
- [x] Website module: 27 REST endpoints, 14 interactive pages, dashboard

---

## Metrics Snapshot (March 2026)

| Metric | Value |
|--------|-------|
| Version | v1.0.5 |
| Modules | 88 (89 load; 6 need optional SDKs) |
| Test suite | ~16,190+ tests collected |
| Coverage gate | 68% (`pyproject.toml fail_under=68`) |
| MCP Tools | 171 (167 safe + 4 destructive) |
| Auto-discovered modules | 33 |
| Ruff violations | 1,531 |
| Desloppify score | 63.1/100 (objective: 78.9) |
| PAI Skills | 76 installed |
| AGENTS.md with Access Matrix | 9/88 (10%) |
| README.md with PAI Integration | 6/88 (7%) |
| PAI.md with current version | ~13/88 (15%) |

---

## Reference

- **Coverage gate**: `pyproject.toml [tool.pytest.ini_options] --cov-fail-under=68`
- **Test runner**: `uv run pytest`
- **Lint**: `uv run ruff check src/`
- **Type check**: `uv run mypy src/`
- **Architecture**: `CLAUDE.md` + `PAI.md` + `src/codomyrmex/PAI.md`
- **PAI Integration**: `docs/pai/README.md` + `docs/pai/architecture.md`
- **Template AGENTS.md**: `src/codomyrmex/agentic_memory/AGENTS.md`
- **Template PAI Integration README**: `src/codomyrmex/orchestrator/README.md`
