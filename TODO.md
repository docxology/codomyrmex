# Codomyrmex — Master Project Backlog

**Version**: v1.0.5 | **Last Updated**: March 2026 | **Active Sprint**: 14+

This is the authoritative project backlog. Updated after each wave/sprint. Sprint history at bottom.

---

## 🔴 CRITICAL (blocking / must fix now)

- [x] Fix `__init__.py` version: `1.0.3.dev0` → `1.0.5` *(Wave 2 — done)*
- [x] Create `.github/CONTRIBUTING.md` *(Wave 2 — done)*
- [ ] **`model_context_protocol/transport/server.py`** — 654 LOC, 0% test coverage (chronic desloppify reopener — highest single-file gap)
- [ ] **Verify Gemini workflows** — 5 GitHub Actions workflows may have broken API keys: `gemini-review.yml`, `gemini-triage.yml`, `gemini-scheduled-triage.yml`, `gemini-dispatch.yml`, `gemini-invoke.yml`
- [ ] **Ratchet coverage gate** from `fail_under=68` → 70% (once transport/server.py tests added)
- [ ] **Resolve ~35 circular import pairs** (Sprint 4 target, still open)

---

## 🟠 HIGH (next sprint targets)

### Documentation — PAI.md Version Headers (75/88 modules outdated)

All need: `v1.0.0 | February 2026` → `v1.0.5 | March 2026`

**Group A (a-c):** `agentic_memory`, `api`, `audio`, `auth`, `bio_simulation`, `cache`, `calendar_integration`, `cerebrum`, `ci_cd_automation`
**Group B (cl-d):** `cloud`, `coding`, `compression`, `concurrency`, `config_management`, `containerization`, `crypto`, `dark`, `database_management`
**Group C (de-ev):** `defense`, `dependency_injection`, `deployment`, `documentation`, `documents`, `edge_computing`, `email`, `embodiment`, `encryption`, `environment_setup`
**Group D (ev-i):** `events`, `evolutionary_ai`, `examples`, `exceptions`, `feature_flags`, `finance`, `formal_verification`, `fpf`, `git_operations`
**Group E (gr-lo):** `graph_rag`, `ide`, `identity`, `llm`, `logging_monitoring`, `logistics`
**Group F (ma-ph):** `market`, `meme`, `model_ops`, `module_template`, `networking`, `networks`, `orchestrator`, `performance`, `physical_management`
**Group G (pl-sk):** `plugin_system`, `privacy`, `prompt_engineering`, `quantum`, `relations`, `scrape`, `security`, `simulation`, `skills`, `spatial`
**Group H (st-z):** `static_analysis`, `system_discovery`, `telemetry`, `templating`, `terminal_interface`, `testing`, `tests`, `tool_use`, `tree_sitter`, `utils`, `vector_store`, `video`, `wallet`

### Documentation — AGENTS.md Agent Role Access Matrix (79/88 missing)

Template: `src/codomyrmex/agentic_memory/AGENTS.md` (verified canonical). Already done: agents, agentic_memory, cerebrum, coding, git_operations, llm, model_context_protocol, orchestrator, security.

**Core Layer:**
- [ ] `static_analysis/AGENTS.md`
- [ ] `logging_monitoring/AGENTS.md`
- [ ] `environment_setup/AGENTS.md`
- [ ] `terminal_interface/AGENTS.md`

**Service Layer:**
- [ ] `ci_cd_automation/AGENTS.md`
- [ ] `formal_verification/AGENTS.md`
- [ ] `validation/AGENTS.md`
- [ ] `events/AGENTS.md`
- [ ] `config_management/AGENTS.md`
- [ ] `data_visualization/AGENTS.md`
- [ ] `maintenance/AGENTS.md`
- [ ] `plugin_system/AGENTS.md`
- [ ] `relations/AGENTS.md`
- [ ] `calendar_integration/AGENTS.md`
- [ ] `collaboration/AGENTS.md`
- [ ] `skills/AGENTS.md`
- [ ] `system_discovery/AGENTS.md`
- [ ] `performance/AGENTS.md`
- [ ] `scrape/AGENTS.md`
- [ ] `search/AGENTS.md`
- [ ] `cloud/AGENTS.md`
- [ ] `git_analysis/AGENTS.md`
- [ ] `containerization/AGENTS.md`

**Domain Modules:**
- [ ] `api/AGENTS.md`, `audio/AGENTS.md`, `auth/AGENTS.md`, `bio_simulation/AGENTS.md`
- [ ] `cache/AGENTS.md`, `compression/AGENTS.md`, `concurrency/AGENTS.md`, `dark/AGENTS.md`
- [ ] `database_management/AGENTS.md`, `defense/AGENTS.md`, `dependency_injection/AGENTS.md`
- [ ] `deployment/AGENTS.md`, `documents/AGENTS.md`, `edge_computing/AGENTS.md`
- [ ] `email/AGENTS.md`, `embodiment/AGENTS.md`, `encryption/AGENTS.md`
- [ ] `evolutionary_ai/AGENTS.md`, `examples/AGENTS.md`, `exceptions/AGENTS.md`
- [ ] `feature_flags/AGENTS.md`, `finance/AGENTS.md`, `fpf/AGENTS.md`
- [ ] `graph_rag/AGENTS.md`, `ide/AGENTS.md`, `identity/AGENTS.md`, `logistics/AGENTS.md`
- [ ] `market/AGENTS.md`, `meme/AGENTS.md`, `model_ops/AGENTS.md`, `module_template/AGENTS.md`
- [ ] `networking/AGENTS.md`, `networks/AGENTS.md`, `physical_management/AGENTS.md`
- [ ] `privacy/AGENTS.md`, `prompt_engineering/AGENTS.md`, `quantum/AGENTS.md`
- [ ] `simulation/AGENTS.md`, `spatial/AGENTS.md`, `telemetry/AGENTS.md`
- [ ] `templating/AGENTS.md`, `testing/AGENTS.md`, `tests/AGENTS.md`, `tool_use/AGENTS.md`
- [ ] `tree_sitter/AGENTS.md`, `utils/AGENTS.md`, `vector_store/AGENTS.md`
- [ ] `video/AGENTS.md`, `wallet/AGENTS.md`

### Documentation — README.md PAI Integration (82/88 missing)

Template: `src/codomyrmex/orchestrator/README.md` or `src/codomyrmex/security/README.md`. Already done: security, llm, orchestrator, git_operations, documentation, formal_verification.

**Priority 1 (largest modules by Python file count):**
- [ ] `agents/README.md` (168 Python files — top priority)
- [ ] `coding/README.md` (71 files)
- [ ] `data_visualization/README.md` (68 files)
- [ ] `cloud/README.md` (56 files)
- [ ] `meme/README.md` (57 files)
- [ ] `agentic_memory/README.md` (has matrix but missing PAI section)
- [ ] `cerebrum/README.md`
- [ ] `model_context_protocol/README.md`

**Priority 2 (service/foundation modules):**
- [ ] `api`, `auth`, `cache`, `cli`, `collaboration`, `config_management`
- [ ] `containerization`, `events`, `feature_flags`, `ide`, `logistics`
- [ ] `model_ops`, `plugin_system`, `prompt_engineering`, `relations`
- [ ] `scrape`, `search`, `skills`, `static_analysis`, `system_discovery`
- [ ] `telemetry`, `terminal_interface`, `utils`, `validation`

**Priority 3 (domain modules):**
- [ ] `audio`, `bio_simulation`, `compression`, `concurrency`, `crypto`
- [ ] `dark`, `database_management`, `defense`, `dependency_injection`
- [ ] `deployment`, `documents`, `edge_computing`, `embodiment`
- [ ] `encryption`, `environment_setup`, `examples`, `evolutionary_ai`
- [ ] `exceptions`, `finance`, `fpf`, `git_analysis`, `graph_rag`
- [ ] `identity`, `logging_monitoring`, `maintenance`, `market`
- [ ] `module_template`, `networking`, `networks`, `performance`
- [ ] `physical_management`, `privacy`, `quantum`, `simulation`
- [ ] `spatial`, `templating`, `testing`, `tests`, `tool_use`
- [ ] `tree_sitter`, `vector_store`, `video`, `wallet`

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

- [ ] Add `py.typed` markers across all modules with type hints (PEP 561)
- [ ] Check and complete: `cerebrum/`, `events/`, `search/`, `config_management/`, etc.

### Ruff Violations (1,531 remaining)

- [ ] Target: ≤1,000 violations in Sprint 15 (-35% from current)
- [ ] Fix remaining B904 exception chaining not yet addressed
- [ ] Address top TID violations (tidy-imports)
- [ ] Replace remaining star imports in non-`__init__.py` files

---

## 🟡 MEDIUM (notable enhancement, 2-4 sprint horizon)

### Documentation — PAI.md MCP Tools Tables (58/88 missing)

Add `## MCP Tools` section to 58 module PAI.md files:

**Has verified tools (add full table):** `events`, `config_management`, `cloud`, `cerebrum`, `performance`, `scrape`, `maintenance`, `plugin_system`, `relations`, `calendar_integration`, `data_visualization`, `collaboration`, `skills`, `git_analysis` and others (see MEMORY.md verified tool names)

**No MCP tools (add "not exposed" note):** All remaining modules without `@mcp_tool` decorators

### Documentation — SPEC.md Expansion (8 stub files < 50 lines)

- [ ] `agentic_memory/SPEC.md`
- [ ] `bio_simulation/SPEC.md`
- [ ] `ci_cd_automation/SPEC.md`
- [ ] `config_management/SPEC.md`
- [ ] `finance/SPEC.md`
- [ ] `model_context_protocol/SPEC.md`
- [ ] `physical_management/SPEC.md`
- [ ] `system_discovery/SPEC.md`

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
