# Codomyrmex — TODO

**Version**: v1.0.7 | **Date**: 2026-03-02 | **Modules**: 124 | **Active Sprint**: 19+

This is the authoritative project backlog. Updated after each sprint.

---

## Codebase Snapshot (Verified 2026-03-02)

| Metric | Value | Method |
| :--- | :--- | :--- |
| Top-level source modules | **124** | `ls -d src/codomyrmex/*/` |
| Source files (non-test) | 1,793 | `find -name "*.py" -not -path "*/tests/*"` |
| Source LOC (non-test) | 307,504 | `wc -l` across source files |
| Total LOC (incl. tests) | 557,855 | `wc -l` across all `.py` |
| Test files | 767 | `find -name "test_*.py"` |
| Test suite | **21,036** tests collected | `uv run pytest --collect-only` |
| Ruff violations | **1,226** | Sprint 16 zeroed; regressed via new modules & rules |
| `NotImplementedError` sites | 13 ABC-annotated (`# ABC: intentional`) | Architectural patterns verified |
| Pass-only function stubs | **2** (down from 227) | AST analysis |
| Missing `@abstractmethod` markers | **0** (was 26, all resolved v1.0.4) | AST analysis ✅ |
| Coverage gate | `fail_under=68` in pyproject; actual ~32% | Needs investigation |
| MCP Tools | **~250** `@mcp_tool` decorators; **299** registered at runtime | Auto-discovery + static |
| Auto-discovered MCP modules | **78** (74 at maxdepth 2) | MCP bridge |
| `mcp_tools.py` files | **78** | `find -name mcp_tools.py` |
| RASP documentation compliance | 124/124 | Automated audit |
| `py.typed` markers | **538** | PEP 561 ✅ |
| Zero-Mock policy | Enforced via `ruff.lint.flake8-tidy-imports.banned-api` | `pyproject.toml` |
| Python compatibility | 3.10 – 3.14 | `pyproject.toml classifiers` + `conftest.py` namespace guard |
| PAI Skills | **81** installed | Skill registry |

### Pass-Only Stub Status

> **Down from 227 → 2.** Nearly all pass-only stubs have been implemented or properly marked as ABCs. Only 2 remain across the entire codebase.

---

## 🔴 CRITICAL (blocking / must fix now)

- [ ] **Coverage investigation**: `fail_under=68` in pyproject.toml but actual coverage measures ~32%. Investigate cause (import errors? partial collection?) and either fix or recalibrate gate
- [ ] **Ruff regression**: Was zeroed in Sprint 16 but now at 1,226 violations from new modules/rules. Triage and fix.
- [x] **Circular import audit** *(Sprint 16)* — 1,646 modules imported cleanly; 0 circular imports; 2 `ImportError` bugs fixed (`ci_cd_automation/build/build_manager.py`, `model_ops/fine_tuning/fine_tuning.py`)

---

## 🟠 HIGH (next sprint targets)

### Stub Backfill (~107 concrete stubs → working implementations)

Prioritized by module criticality and user-facing impact. Excludes ~120 intentional ABC methods.

| Priority | Module | Stubs | Key Functions to Implement | Dependencies |
| :--- | :--- | :---: | :--- | :--- |
| **P0** | `ide` | 8 | `connect()`, `disconnect()`, `execute_command()`, `open_file()` | Cursor/Antigravity extension APIs |
| **P0** | `collaboration` | 12 | `CollaborationAgent.process_task()`, `Channel.send()/receive()`, `Protocol.execute()` | `events`, `agents` |
| **P1** | `coding` | 12 | `TreeSitterParser.parse()`, `RefactoringEngine.analyze()/execute()`, `StaticAnalyzer.__init__()` | `tree-sitter` optional dep |
| **P1** | `cloud` | 27 | `CloudProvider` CRUD, `StorageProvider` bucket/file ops, `ServerlessProvider` function mgmt | `boto3`, `google-cloud-storage`, `azure-*` optional deps |
| **P1** | `orchestrator` | 7 | `ExecutionEngine.execute()`, `PipelineStage.execute()`, `Trigger.get_next_run()` | `events`, `concurrency` |
| **P2** | `llm` | 25 | `BaseLLMProvider.complete()/complete_stream()`, `BaseEmbedding.embed()`, `BaseMemory.add_message()` | Mostly ABCs — add `@abstractmethod`; implement on concrete subclasses |
| **P2** | `telemetry` | 10 | `SpanExporter.export()/shutdown()`, `MetricReader.get_value()` | `opentelemetry-*` optional deps |
| **P2** | `security` | 7 | `AuditStore.store()/query()`, `ComplianceControl.check()`, `SecurityCheck.check()` | None |
| **P3** | `audio` | 14 | STT/TTS provider implementations | `faster-whisper`, `edge-tts` optional deps |
| **P3** | `cache` | 17 | `BaseCacheBackend` implementations | `redis` optional dep |
| **P3** | `containerization` | 6 | WASM runtime `load_module()/execute()` | `wasmtime` (new optional dep) |
| **P3** | `evolutionary_ai` | 3 | `mutate()`, `crossover()`, `select()` operators | `numpy` |
| **P3** | `feature_flags` | 3 | `Strategy.evaluate()`, serialization | None |

### MCP Coverage (78/124 modules have `mcp_tools.py`)

**78 modules** now have MCP exposure (up from 45 in Sprint 18). 46 modules remain without `mcp_tools.py`.
Sprint 16: `static_analysis` ✅, `vector_store` ✅, `feature_flags` ✅
Sprint 17: `serialization` ✅, `cache` ✅, `deployment` ✅, `model_ops` ✅, `testing` ✅, `templating` ✅
Sprint 18: `prompt_engineering` ✅, `database_management` ✅, `auth` ✅, `environment_setup` ✅, `utils` ✅, `tool_use` ✅
Sprint 19: 4 additional modules + documentation audit

| Module Group | Remaining Modules Without MCP |
|---|---|
| Infrastructure | `api`, `ci_cd_automation` |
| AI / ML | `evolutionary_ai` |
| Code Quality | `tree_sitter`, `pattern_matching` |
| Developer Tools | `cli`, `ide`, `terminal_interface` |
| Comms / Media | `audio`, `video`, `dark`, `documents`, `fpf` |
| Security | `encryption`, `defense`, `privacy` |
| Platform | `edge_computing`, `networking`, `physical_management`, `quantum` |
| Misc | `bio_simulation`, `finance`, `graph_rag`, `identity`, `logistics`, `market`, `meme`, `simulation`, `spatial`, `wallet` |

### Type Checking

- [x] Add `py.typed` markers across all modules with type hints (PEP 561) — **538 markers** across 124 modules *(Sprint 15+)*
- [ ] Check and complete type hint coverage: `cerebrum/`, `events/`, `search/`, `config_management/`, etc.

### Documentation — Completed ✅

<details>
<summary>Wave 2 + SPEC.md Expansion (March 2026) — all done</summary>

- [x] **PAI.md version headers** — all modules bumped to `v1.0.6 | March 2026`
- [x] **AGENTS.md Agent Role Access Matrix** — added to all modules
- [x] **README.md PAI Integration section** — added to all modules
- [x] **PAI.md MCP Tools table** — added to all modules
- [x] All 8 stub SPEC.md files expanded (agentic_memory, bio_simulation, ci_cd_automation, config_management, finance, model_context_protocol, physical_management, system_discovery) — 43-49 → 143-190 lines each

</details>

### Structural Quality

| Item | Current State | Target |
| :--- | :--- | :--- |
| **Oversized files** | `data_visualization/advanced_plotter.py` = 1,023 LOC | ≤500 LOC per file |
| `ide/antigravity/__init__.py` | ~~940 LOC~~ → **110 LOC** *(Sprint 16 ✅)* — reduced to re-export facade | Done |
| **Chronic coverage reopeners** | `ide/antigravity/agent_bridge.py` (324 LOC, flagged ×2) | ≥50% on each |
| **Circular imports** | **0 circular imports** detected (Sprint 16 audit: 1,646 modules clean) | ✅ Complete |

---

## 🟡 MEDIUM (notable enhancement, 2-4 sprint horizon)

### v1.1.0 — "Production Readiness"

First feature release targeting external consumption.

| Item | Scope | Detail |
| :--- | :--- | :--- |
| **PyPI publication** | `pyproject.toml`, `release/` | `hatch build` → `twine check` → TestPyPI dry-run → production publish |
| **MCP deprecation timeline UI** | `model_context_protocol/`, `website/` | Surface `deprecated_in` metadata from `@mcp_tool` in dashboard UI |
| **Bidirectional PAI ↔ Codomyrmex** | `agents/pai/` | HTTP webhook or Unix socket (currently: filesystem back-channel only) |
| **CLI doctor v2** | `cli/doctor.py` | `--fix` mode: auto-create `.env`, install optional deps, validate RASP docs |
| **API key rotation workflow** | `config_management/secrets/` | Automated key rotation with `pre-commit` secret scanner integration |
| **Mutation testing expansion** | `pyproject.toml [tool.mutmut]` | Extend beyond 3 files to cover `security/secrets/`, `orchestrator/core.py`, `events/core/event_bus.py` |
| **mypy strict ramp** | `pyproject.toml [[tool.mypy.overrides]]` | Promote `agents` to `disallow_untyped_defs = true`. Current: ~612 errors. Target: ≤300 |
| **Integration test formalization** | `tests/integration/` | Formalize 11 workflow files into CI pipeline with `pytest -m integration` marker |
| **Documentation site deployment** | `docs_gen/site_generator.py`, `mkdocs.yml` (new) | `mkdocs-material` site from 124 module RASP docs → GitHub Pages |

### Rules Submodule Enhancements (agentic_memory/rules/)

- [ ] Cache warm-up option: `RuleEngine.__init__(preload=True)` — loads all rules on startup
- [ ] Rule content validation script — verify all 75 `.cursorrules` files have sections 0-7
- [ ] Integrate `RuleEngine` into `MemoryConsolidator` — rule-aware importance thresholds
- [ ] Add optional `context_rules` param to `memory_search` MCP tool

### Test Coverage Gaps

- [ ] Cover `email/provider.py` (currently 0%)
- [ ] Cover `agents/droid/run_todo_droid.py` (currently 0%)
- [ ] Fix ~5 remaining `xfail` markers (verify if bugs are now fixed)

### Architecture Debt

- [ ] Fix oversized files — 8 files > 1K LOC
- [ ] `logistics/orchestration/project` class-based MCP pattern — add auto-discovery or document clearly

---

## 🟢 LOW (nice-to-have, backlog)

### GitHub Actions

- [ ] Add SBOM (Software Bill of Materials) generation workflow
- [ ] Add Lighthouse/performance budget enforcement for website
- [ ] Add automated changelog generation linked to `release.yml`
- [ ] Verify 5 Gemini workflows are functional (API key + integration health check)

### Documentation

- [x] Create `docs/ARCHITECTURE.md` — visual Mermaid layer diagram *(exists: 448-line dependency graph)*
- [ ] Expand `docs/getting-started/` with more tutorials (currently only `connecting-pai.md`)
- [ ] Auto-generate rule index table in `rules/README.md` from live filesystem scan
- [ ] Cross-reference rules to corresponding `AGENTS.md` files

### Developer Experience

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

## Medium-Term Development

Functional deepening and ecosystem maturation. No fixed release target; items ordered by estimated impact.

- **Collaboration module — Tier 2 promotion**: 12 pass-only stubs in `collaboration/agents/`, `communication/`, `coordination/`, `protocols/`. Implement `AgentRegistry` with in-memory store, `Channel.send()/receive()` over `EventBus`, and Bully leader election. Test with multi-agent task delegation scenario. *Depends on*: `events`, `agents`

- **Feature flags engine**: 3 stubs in `strategies/`. Implement `PercentageStrategy`, `UserListStrategy`, `TimeWindowStrategy`. Add JSON file persistence for flag state. Wire into `config_management` for runtime flag loading. *Depends on*: `serialization`, `config_management`

- **Infomaniak cloud provider**: 27 cloud stubs overall — Infomaniak is the concrete provider with the most gaps. Implement storage API (Swift-compatible), compute API (Nova-compatible), and DNS management against Infomaniak's public API. *Depends on*: `cloud/common/` ABC layer

- **Graph RAG pipeline**: Connect `graph_rag` knowledge graph to `llm/rag/` for retrieval-augmented generation with structured entity relationships. Implement: graph construction from Obsidian vaults, entity-aware retrieval, and context window assembly. *Depends on*: `agentic_memory/obsidian`, `llm/rag`, `llm/embeddings`

- **Agentic memory persistence**: Currently in-memory only beyond Obsidian. Add SQLite backend for `MemoryStore` with TTL-based expiry, tag indexing, and cross-session retrieval. Redis backend as optional high-performance alternative. *Depends on*: `database_management`, `serialization`

- **Dashboard v2**: Add WebSocket real-time streaming, test-run history timeline, module health heatmap, per-module stub/coverage sparklines. *Depends on*: `telemetry`, `performance`, `data_visualization`

- **Formal verification integration**: Wire `z3-solver` (already in optional deps) into `coding/` for automated invariant checking. *Depends on*: `coding/static_analysis`, `z3-solver`

- **Multimodal agent pipeline**: Connect `audio` extras (Whisper STT, Edge TTS) and `video` extras (MoviePy, OpenCV) to agent conversation loop. Target: voice-in/voice-out agent interaction. *Depends on*: `agents`, `llm`, `audio`, `video`

- **Cost management activation**: Implement real API spend tracking using provider usage APIs (OpenRouter, OpenAI, Anthropic). Add budget alerting with configurable thresholds and Slack/email notification. *Depends on*: `llm/providers`, `events/notification`, `networking`

---

## Longer-Term Vision

Architectural extensions and research directions. Aspirational and may require significant design work.

- **Spatial reasoning & Synergetics** — Deepen the `spatial` module: Fuller-inspired geodesic coordinate transforms, 4D rotation matrices (quaternion-based), icosahedral mesh generation. Integrate with `data_visualization` for 3D rendering via Matplotlib or ModernGL

- **Embodiment & ROS2 bridge** — The `embodiment` module is currently deprecated. Decide: archive/remove, or invest in full ROS2 bridge with `rclpy` bindings, sensor subscriptions, actuator commands, and safety interlock state machines

- **Evolutionary AI operators** — 3 stubs in `evolutionary_ai/operators/`. Implement tournament selection, single-point/uniform crossover, Gaussian mutation. Add `Population` class for generation management. Target: neural architecture search in `inference_optimization`

- **Cerebrum cognitive architecture** — Extend Bayesian reasoning with real probabilistic inference using `scipy.stats`. Belief revision (Jeffrey conditionalization), multi-hypothesis planning (particle filtering), uncertainty-aware goal decomposition

- **Inference optimization** — INT8/INT4 quantization wrappers, knowledge distillation, speculative decoding for local model acceleration. Wire into `llm/providers/` as transparent optimization layer

- **Plugin marketplace** — Plugin discovery (entry points + PyPI search), sandboxed installation, version management, compatibility checking. Surface via `plugin_system/discovery.py` and `skills/` registry

- **Multi-agent swarm protocols** — Fault-tolerant consensus (Raft in `coordination/`), hierarchical task decomposition, emergent behavior monitoring via `telemetry`, configurable communication topologies (mesh, star, ring)

- **Self-improving pipelines** — Connect `ImprovementPipeline` (detect → fix → test → review) to CI/CD via GitHub Actions trigger. Target: agent-driven code quality PRs with automated test generation and human-in-the-loop review gates

- **Secure cognitive agent hardening** — The 5 Secure Cognitive modules (`identity`, `wallet`, `defense`, `market`, `privacy`) need formal threat modeling (STRIDE), penetration testing, key management audit, and mixnet routing validation

- **Cross-platform distribution** — Homebrew formula (macOS), Nix flake (NixOS/cross-platform), multi-arch Docker image (amd64/arm64), `pipx` install pathway. Requires clean entry point, minimal core deps, optional feature detection

---

## ✅ COMPLETED — Sprint History

### Sprint 19 (March 2026) — Documentation Audit + MCP Expansion

- [x] **Repo-wide documentation audit**: 10 files corrected (README, SPEC, AGENTS, PAI, CLAUDE, INDEX, docs/README, docs/AGENTS, .github/README)
- [x] Version alignment: all docs updated v1.0.3/v1.0.5 → v1.0.6 → v1.0.7
- [x] Module count alignment: 88/95 → 124 across all documentation
- [x] MCP tool count alignment: various → ~250 decorators / 299 registered
- [x] Removed dead cross-references: `cursorrules/`, `resources.json`, `test.db`, `workflow.db`
- [x] Fixed module naming: `tools/` → `tool_use/`
- [x] Triple-checked PAI interface: 299 tools, 3 resources, 10 prompts, MCP Web UI verified via browser
- [x] TODO.md reconciliation: 15 stale metrics corrected to verified actuals
- [x] Pass-only stubs: 227 → 2 (massive improvement from prior sprints)

### Sprint 18 (March 2026) — MCP Coverage Expansion (6 Modules)

- [x] Created `mcp_tools.py` for `prompt_engineering` — 3 tools: `prompt_list_templates`, `prompt_list_strategies`, `prompt_evaluate`
- [x] Created `mcp_tools.py` for `database_management` — 3 tools: `db_list_adapters`, `db_monitor`, `db_generate_schema`
- [x] Created `mcp_tools.py` for `auth` — 3 tools: `auth_authenticate`, `auth_validate_token`, `auth_list_providers`
- [x] Created `mcp_tools.py` for `environment_setup` — 2 tools: `env_check`, `env_list_deps`
- [x] Created `mcp_tools.py` for `utils` — 3 tools: `utils_hash_content`, `utils_json_loads`, `utils_flatten_dict`
- [x] Created `mcp_tools.py` for `tool_use` — 2 tools: `tool_use_list_tools`, `tool_use_validate_input`
- [x] Created 37 new tests across 6 test files — all 37 pass
- [x] MCP tool count: ~198 → ~214 (+16)
- [x] Auto-discovered MCP modules: 39 → 45 (+6)

### Sprint 17 (March 2026) — MCP Coverage Expansion (6 Modules) + Templating Bug Fix

- [x] Created `mcp_tools.py` for `serialization` — 3 tools: `serialize_data`, `deserialize_data`, `serialization_list_formats`
- [x] Created `mcp_tools.py` for `cache` — 4 tools: `cache_get`, `cache_set`, `cache_delete`, `cache_stats` (singleton CacheManager pattern)
- [x] Created `mcp_tools.py` for `deployment` — 3 tools: `deployment_execute`, `deployment_list_strategies`, `deployment_get_history`
- [x] Created `mcp_tools.py` for `model_ops` — 3 tools: `model_ops_score_output`, `model_ops_sanitize_dataset`, `model_ops_list_scorers`
- [x] Created `mcp_tools.py` for `testing` — 2 tools: `testing_generate_data`, `testing_list_strategies`
- [x] Created `mcp_tools.py` for `templating` — 2 tools: `template_render`, `template_validate`
- [x] Fixed pre-existing bug in `templating/engines/template_engine.py:141` — `Jinja2Template(template, environment=env)` → `env.from_string(template)` (TypeError with modern Jinja2)
- [x] Created 44 new tests across 6 test files — all 44 pass
- [x] MCP tool count: 181 → ~198 (+17)

### Sprint 16 (March 2026) — Rules Enhancements & MCP Coverage Expansion

- [x] Extended `agentic_memory/rules/` with 5 new MCP tools: `rules_get_section`, `rules_search`, `rules_list_cross_module`, `rules_list_file_specific`, `rules_list_all`
- [x] Added `RuleRegistry.list_all_rules()` + `RuleEngine.list_all_rules()` — returns all 75 rules sorted by priority
- [x] Added 11 new tests for rules submodule (54 total, up from 43)
- [x] Created `mcp_tools.py` for `static_analysis` — 3 tools
- [x] Created `mcp_tools.py` for `vector_store` — 4 tools
- [x] Created `mcp_tools.py` for `feature_flags` — 3 tools
- [x] 27 new tests for the 3 new module MCP tools

### Sprint 15 (March 2026) — Ruff Cleanup, Bug Fixes & Coverage

- [x] **TID252 eliminated**: 241 relative parent imports converted to absolute across 107 source files
- [x] **E402 eliminated**: 160 "imports not at top" fixed across 120+ files
- [x] Ruff total: 607 → 43 violations (93% reduction; only F405 structural star imports remain)
- [x] Fixed circular import in `ide/__init__.py` — CursorClient deferred with `# noqa: E402`
- [x] Fixed seaborn `xticklabels=None` TypeError (→ `"auto"`) in `advanced_plotter.py`
- [x] Fixed `test_task_master.py` ANTHROPIC_API_KEY collection-time skip → execution-time `autouse` fixture
- [x] Fixed `orchestrator/execution/runner.py` `queue.empty()` race condition → `queue.get(timeout=5)`
- [x] Added 21 new health_handler tests: coverage 62% → 94%
- [x] Added missing `py.typed` markers for `docs_gen`, `git_analysis`, `release` (now 88/88)

### Sprint 14 (March 2026) — Test Suite Health & CI Hardening

- [x] GitHub Actions: remove silent `pylint`/`flake8` `|| true` from `ci.yml`
- [x] GitHub Actions: harden `uv pip check` (remove `|| true`)
- [x] GitHub Actions: fix `benchmarks.yml` double-write bug
- [x] GitHub Actions: add `code-health.yml` weekly dashboard
- [x] GitHub Actions: graceful Semgrep skip when `SEMGREP_APP_TOKEN` absent
- [x] New tests: `dependency_resolver` (22), `mcp_tools` (12), `git_operations/cli/metadata` (18), `docs_gen` (40+), `release` (40+)
- [x] Ruff Sprint 13: 1,878 → 1,531 violations (−18.4%)
- [x] Rules submodule: moved `cursorrules/` → `agentic_memory/rules/`, Python API, 3 MCP tools, 30 tests
- [x] 682 new tests across 5 thin modules (model_context_protocol, documentation, ide, prompt_engineering, audio)
- [x] Template `assert True` → `pytest.skip("placeholder")`
- [x] URL env-var standardization (`OLLAMA_BASE_URL`/`CONTAINER_REGISTRY_URL` fixtures)
- [x] `model_context_protocol/transport/server.py` — 0% → 60%+ test coverage
- [x] 10 stale worktrees + branches pruned

### v1.0.3 — "Obsidian Module v3.0" ✅ RELEASED (2026-02-27)

- [x] Obsidian CI stability (413/413 tests)
- [x] Coverage holds (`--cov-fail-under=68`)
- [x] CHANGELOG consolidation, SECURITY.md version table, root docs version sweep
- [x] Pre-commit pin refresh (Black 26.1.0, ruff v0.15.4, mypy v1.19.1)
- [x] `__init__.py` + `pyproject.toml` version bump → `1.0.3`

### Wave 2 (March 2026) — Documentation

- [x] Fix `__init__.py` version: `1.0.3.dev0` → `1.0.5`
- [x] Create `.github/CONTRIBUTING.md`
- [x] Fixed all `~/.claude/skills/PAI/` → `~/.claude/PAI/` refs (~30 docs/ files)
- [x] Added PAI Integration sections to 88 module READMEs
- [x] Added PAI Agent Role Access Matrix to 88 AGENTS.md files
- [x] Fixed Algorithm version `v1.5.0` → `v3.5.0` in all mermaid diagrams
- [x] Updated hub file versions → v1.0.5 / March 2026

### Sprint 13 (March 2026) — Code Quality

- [x] Ruff violations: 1,878 → 1,531 (−347, −18.4%), 478 auto-fixes
- [x] 6 F821 source bugs fixed
- [x] +44 new website tests (accessibility 14-33% → 75%+)
- [x] Coverage gate set to `pyproject.toml fail_under=68`

### Sprint 9–12 (Feb–Mar 2026)

- [x] Coverage gate ratcheted 65% → 67% → 68%
- [x] ~16,190+ tests collected total
- [x] 50 false-positive skip guards removed
- [x] Zero-Policy compliance: 38 violations fixed across 32 files
- [x] ~926 new tests; droid_manager 0% → 87%, cache_manager 0% → 91%

### Sprint 4–8 (Feb 2026)

- [x] 2,053 new tests in 34 new files (Sprint 4-5)
- [x] 1,414 new tests via 18 parallel agents (Sprint 6-7)
- [x] 12 missing `__init__.py` added; 9 stub RASP docs populated
- [x] 4 xfail markers removed; 113 weak assertions replaced

### Sprint 1–3 (Feb 2026)

- [x] Core agent framework: BaseAgent, AgentOrchestrator, SessionManager
- [x] MCP bridge: 171 tools (167 safe + 4 destructive), 33 auto-discovered modules
- [x] Trust gateway: UNTRUSTED → VERIFIED → TRUSTED state machine
- [x] PAI v4.0.1 integration: filesystem layout `~/.claude/PAI/` established
- [x] Website module: 27 REST endpoints, 14 interactive pages, dashboard

---

## Release Quality Gate Standard

> [!IMPORTANT]
> Every method implemented **must** satisfy all four criteria before the release tag:
>
> 1. **Real** — Functional implementation, no mocks, no placeholder logic
> 2. **Tested** — Zero-mock test(s) in `src/codomyrmex/tests/unit/` validating real behaviour
> 3. **Validated** — `pytest` green, `py_compile` clean, lint-free
> 4. **Documented** — Docstring with Args/Returns/Example sections; module README/SPEC updated if public API
>
> Additionally, each *module area* touched must have a **thin orchestration example** in `scripts/examples/` — a runnable ~50-80 line script demonstrating real cross-module integration (no mocks, no stubs, real I/O).

---

## Reference

- **Coverage gate**: `pyproject.toml [tool.pytest.ini_options] --cov-fail-under=68`
- **Test runner**: `uv run pytest`
- **Lint**: `uv run ruff check src/`
- **Type check**: `uv run mypy src/`
- **Architecture**: `CLAUDE.md` + `PAI.md` + `src/codomyrmex/PAI.md`
- **PAI Integration**: `docs/pai/README.md` + `docs/pai/architecture.md`

---

*Last updated: 2026-03-02 — Metrics reconciled to Sprint 19 verified actuals (v1.0.7).*
