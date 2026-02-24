# Codomyrmex Project Roadmap & To-Do

**Status**: Active | **Last Updated**: February 24, 2026 | **Current**: v1.0.2-dev | **Next**: v1.0.2

---

## Release Policy

> [!CAUTION]
> **No versioned release — even patch releases — ships unless every gate below passes. No exceptions.**

### Testing Gates

1. **Zero test failures** — `pytest` exits 0 across the entire suite
2. **Zero collection errors** — `pytest --co -q` discovers all tests without import or fixture errors
3. **Zero mocks, stubs, or placeholders** — absolute zero-mock policy enforced across all non-vendored code
4. **No unresolved deprecation warnings** — `filterwarnings` clean in test output

### Documentation Gates

1. **RASP complete** — every module directory contains README.md, AGENTS.md, SPEC.md, PAI.md
2. **Root docs synced** — CHANGELOG, README, SPEC, TO-DO reflect accurate module counts, test counts, and version strings
3. **Public API documented** — all public methods have docstrings and type annotations

### Modularity Gates

1. **Module scaffold valid** — every module has `__init__.py` plus at least one test file
2. **Orchestration importable** — top-level entry points importable (`from codomyrmex import …`)
3. **`codomyrmex doctor --all` exit 0** — system-wide health check passes

---

## Codebase Snapshot (audited Feb 24, 2026)

| Metric | Value | Notes |
| :--- | ---: | :--- |
| Top-level module dirs | 98 | **~85 real** (see §Repo Hygiene below) |
| MCP tool files / decorators | 32 / 201 | |
| Tests collected (0 collection errors) | 10,010 | |
| Tests passing | 9,744 | |
| Tests failing (pre-existing) | **5** | see §Pre-existing Test Failures |
| Tests skipped | 280 | many likely stale |
| Warnings | 187 | |
| Coverage | **31%** | not moving; inflated LOC from junk dirs |
| Stub functions (`pass`-only bodies) | **292** across 101 files | see §Stub Functions |
| Python 3.14+ compat | ✅ | |

> [!WARNING]
> The "98 modules" metric is inflated by ~13 generated-artifact directories that should not exist inside `src/codomyrmex/`. Real module count is **~85**. See §Repo Hygiene.

> [!NOTE]
> Full release history (v0.1.3 → v1.0.1, Sprints 1–41) is archived in [CHANGELOG.md](CHANGELOG.md).

---

## ✅ v1.0.1 — Completed

**Theme**: Depth, coverage, and hardening

- [x] MCP tools: 27 → 31 (`agentic_memory`, `collaboration`, `validation`)
- [x] Test failures: 44 → 0 (trust_gateway, auth, stale paths, secrets namespace, deprecation warnings)
- [x] Flaky `test_save_plot_pdf_format` replaced with robust `test_save_plot_svg_format`
- [x] 4 xfail → pass (`generate_secret` stdlib namespace collision fixed)
- [x] Warning filters for `google.generativeai`, `PytestCollectionWarning`

---

## ✅ v1.0.2-dev — Modularization Sprint (completed)

**Theme**: Modularize oversized files, streamline imports, eliminate dead code

| File | Before | After | Technique |
| :--- | ---: | ---: | :--- |
| `droid/tasks.py` | 3,541 | **69** | Subpackage → `generators/{spatial,documentation,physical}.py` |
| `ai_code_helpers.py` | 1,188 | **1,087** | Dead code removal |
| `reviewer.py` | 2,320 | **2,284** | Convenience funcs → `coding/review/api.py` (47) |
| `git.py` | 1,747 | **1,595** | Dedup 7 duplicate functions |
| `data_provider.py` | 1,213 | **494** | Mixin → `health_mixin.py` (403) + `pai_mixin.py` (367) |

- [x] All legacy re-exports removed — imports point to actual locations
- [x] `generators/documentation.py` still has 1 duplicate function def (`generate_quality_tests` 2×) — needs fix

---

## 🚨 v1.0.2 — Critical: Repo Hygiene (P0)

> [!CAUTION]
> Generated artifact directories exist inside `src/codomyrmex/` and are committed to git. They inflate module counts, pollute imports, bloat the repo, and corrupt coverage metrics.

### Directories to delete and `.gitignore`

| Directory | Files | What it is |
| :--- | ---: | :--- |
| `src/codomyrmex/htmlcov/` | 1,358 | pytest coverage HTML output |
| `src/codomyrmex/src/` | 44 | nested duplicate of source tree |
| `src/codomyrmex/rollback_plans/` | 12 | generated rollback artifacts |
| `src/codomyrmex/config/` | 12 | generated config output |
| `src/codomyrmex/output/` | 8 | script output |
| `src/codomyrmex/pipeline_reports/` | 4 | generated reports |
| `src/codomyrmex/pipeline_metrics/` | 4 | generated metrics |
| `src/codomyrmex/rollback_history/` | 4 | generated artifacts |
| `src/codomyrmex/optimization_data/` | 4 | generated artifacts |
| `src/codomyrmex/plugins/` | 4 | generated plugins |

- [ ] Delete all 10 directories listed above
- [ ] Add entries to `.gitignore`: `src/codomyrmex/htmlcov/`, `src/codomyrmex/output/`, `src/codomyrmex/pipeline_*/`, `src/codomyrmex/rollback_*/`, `src/codomyrmex/optimization_data/`, `src/codomyrmex/plugins/`, `src/codomyrmex/config/`, `src/codomyrmex/src/`
- [ ] Re-audit module count after cleanup (expect ~85)

---

## 🚨 v1.0.2 — Critical: Stub Functions (P0)

> [!WARNING]
> **292 functions** across 101 files have `pass` as their only body. These violate the zero-mock/zero-placeholder policy and represent code that claims to exist but does nothing.

### Top offenders (implement or delete)

| File | Stubs | Action |
| :--- | ---: | :--- |
| `cloud/common/__init__.py` | 19 | Implement or remove cloud common interface |
| `agents/core/base.py` | 12 | Legitimate ABCs? Audit each method |
| `ide/__init__.py` | 8 | Implement or remove IDE stubs |
| `formal_verification/backends/base.py` | 7 | Likely legitimate ABCs — verify |
| `audio/text_to_speech/providers/base.py` | 7 | Likely legitimate ABCs — verify |
| `audio/speech_to_text/providers/base.py` | 7 | Likely legitimate ABCs — verify |
| `vector_store/store.py` | 6 | Implement or remove |
| `email/generics.py` | 6 | Implement or remove |
| `collaboration/agents/base.py` | 6 | Likely legitimate ABCs — verify |
| `cache/cache.py` | 6 | Implement or remove |

- [ ] Audit all 292 stubs: classify as legitimate ABCs vs dead placeholder code
- [ ] Delete all non-ABC stub functions
- [ ] For legitimate ABCs, add `@abstractmethod` decorator and `raise NotImplementedError`

---

## 🔧 v1.0.2 — Pre-existing Test Failures (P1)

5 tests that fail in full suite runs. Each has been present for multiple sessions.

- [ ] **`TestBuildPaiMermaidGraph::test_valid_syntax_with_data`** — stdlib `calendar` namespace collision
- [ ] **`TestBuildPaiMermaidGraph::test_orphan_projects_handled`** — same root cause as above
- [ ] **`test_call_tool_delegates_to_trust_gateway`** — MCP integration failure
- [ ] **`test_valid_127_origin`** — server test isolation (passes alone, fails in full suite)
- [ ] 1 intermittent failure — needs identification

Fix approach:

- [ ] Rename `src/codomyrmex/calendar/` to avoid stdlib namespace collision (root cause of mermaid failures)
- [ ] Debug MCP trust gateway delegation test
- [ ] Add test isolation fixtures for server tests

---

## 🔧 v1.0.2 — Remaining Duplicate Function Definitions (P1)

3 files still have duplicate `def` at module scope:

- [ ] `generators/documentation.py`: `generate_quality_tests` defined 2× (lines 104, 802) — remove first copy
- [ ] `tests/conftest.py`: `main` defined 2× (lines 172, 266) — merge or remove
- [ ] `tests/unit/agents/test_ollama_agents_integration.py`: `add` defined 2× (lines 128, 169) — merge or remove

---

## 🔧 v1.0.2 — Large Files Still Pending (P2)

Files >1,000 LOC that haven't been modularized (excluding vendor/ and test files):

| File | LOC | Suggests |
| :--- | ---: | :--- |
| `coding/review/reviewer.py` | 2,284 | Still a God class (89 methods). Split into analysis/dashboard/report mixins |
| `agents/droid/generators/physical.py` | 1,776 | Newly extracted but monolithic. Split by concern |
| `git_operations/core/git.py` | 1,595 | Split into remote/state/analysis/config submodules |
| `agents/claude/claude_client.py` | 1,582 | Split into auth/chat/streaming/tools |
| `cloud/coda_io/client.py` | 1,386 | Split into docs/pages/tables/formulas |
| `agents/pai/mcp_bridge.py` | 1,264 | Split into tools/resources/prompts |
| `git_operations/api/github.py` | 1,186 | Split into repos/prs/issues/actions |
| `agents/ai_code_editing/ai_code_helpers.py` | 1,087 | Was 1,188 — further split possible |

---

## 🔧 v1.0.2 — Coverage & Testing (P2)

### Coverage 31% → 40%+

- [ ] Audit the 10 largest modules by LOC and identify untested code paths
- [ ] Add targeted tests for un-covered branches in `orchestrator`, `agents`, `events`
- [ ] Set `--cov-fail-under=35` after first pass, ratchet to 40

### Skip Reduction (280 → <250)

- [ ] Review 9 "Required modules not available" skips — may be stale guards
- [ ] Check 8 "git not installed" skips — git is always available in CI
- [ ] Verify 7 "Search indexer not available" skips

---

## 🔧 v1.0.2 — MCP & Type Safety (P2)

### MCP Tool Expansion

32/~85 real modules have `mcp_tools.py`. Next 6 high-value additions:

- [ ] `events/mcp_tools.py`: `publish_event`, `subscribe`, `replay_events`
- [ ] `concurrency/mcp_tools.py`: `submit_task`, `pool_status`, `dead_letter_list`
- [ ] `system_discovery/mcp_tools.py`: `discover_modules`, `health_check`, `capability_scan`
- [ ] `networking/mcp_tools.py`: `http_get`, `http_post`, `dns_lookup`
- [ ] `containerization/mcp_tools.py`: `build_image`, `run_container`, `list_containers`
- [ ] `templating/mcp_tools.py`: `render_template`, `list_templates`, `validate_template`

### Type Safety

- [ ] Run `mypy --strict` on `agents/`, `orchestrator/`, `events/` backbone
- [ ] Fix highest-impact type errors (missing annotations, `Any` escape hatches)
- [ ] Add `py.typed` marker to backbone modules

---

## 🔄 Technical Debt Summary

| Pri | Item | Target | Status |
| :---: | :--- | :--- | :--- |
| **P0** | Delete 10 junk dirs from `src/` | ~85 real modules | **TODO** |
| **P0** | Audit 292 stub functions | 0 non-ABC stubs | **TODO** |
| **P1** | Fix 5 pre-existing test failures | 0 failures | **TODO** |
| **P1** | Fix 3 remaining duplicate function defs | 0 duplicates | **TODO** |
| **P1** | ~~Modularize 5 oversized files~~ | done | ✅ Done |
| **P1** | Coverage 31%→40%+ | measured, gates set | v1.0.2 |
| **P2** | 8 more files >1,000 LOC | no non-vendor file >1,500 | v1.0.2 |
| **P2** | MCP tool coverage 32→38+ | `mcp_tools.py` in high-value modules | v1.0.2 |
| **P2** | `mypy --strict` progressive | 0 errors on backbone | v1.0.2 |
| **P2** | Skip reduction | 280→<250 | v1.0.2 |
| **P3** | Documentation site (MkDocs) | auto-deploy | Future |
| **P3** | Event store compaction | JSONL size | Future |
