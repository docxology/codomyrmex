# Codomyrmex — TO-DO

**Current**: v1.0.3-dev | **Next**: v1.0.3 | **Updated**: Feb 25, 2026

---

## Release Gates

> [!CAUTION]
> No release ships unless **every** gate passes.

| Gate | Requirement |
| :--- | :--- |
| Tests | `pytest` exits 0; 0 collection errors |
| Mocks | Zero mocks/stubs/placeholders in non-vendored code |
| Warnings | No unresolved deprecation warnings |
| RASP | Every module has README.md, AGENTS.md, SPEC.md, PAI.md |
| Docs | Root docs synced (version, module count, test count) |
| API | All public methods have docstrings + type annotations |
| Scaffold | Every module has `__init__.py` + test file |
| Health | `codomyrmex doctor --all` exits 0 |

---

## Codebase Snapshot

| Metric | Value |
| :--- | ---: |
| Python files | 2,046 |
| Total LOC | 414,862 |
| Modules | 86 |
| Functions / Classes | 23,208 / 5,210 |
| Tests collected | 11,065 |
| Tests passing / failing / skipped | 9,724 / 0 / 253 |
| Coverage | 30% |
| RASP coverage | 100% ✅ |
| MCP tool files | 33 / 87 |

---

## v1.0.3-dev — Skills Release (in progress)

- [x] `skills/mcp_tools.py` — 7 MCP tools wrapping SkillsManager
- [x] `skills/skill_runner.py` — execution bridge (run_skill, run_skill_by_name)
- [x] `skills/skills/templates/` — 3 starter YAML templates (code_review, testing, documentation)
- [x] Modularize `arscontexta/__init__.py` (928 → 63 LOC)
- [x] Version bump to 1.0.3.dev0
- [x] CHANGELOG v1.0.3-dev entry
- [x] Clean TO-DO.md scope
- [ ] Update root docs version strings (README, SPEC, AGENTS, PAI, INDEX, CLAUDE)

---

## Next Sprint — High-Impact Work (pick 3)

### NS-1  Coverage 30% → 40%

Current coverage is the weakest release gate metric. Target backbone modules first.

- [ ] Audit 10 largest modules for untested code paths
- [ ] Add targeted tests for `orchestrator`, `agents`, `events`
- [ ] Set `--cov-fail-under=35`, ratchet to 40

### NS-2  Broad exception handling (1,498 `except Exception` clauses)

Production-quality error handling across the backbone.

- [ ] Audit top-20 files by broad exception count
- [ ] Replace with specific types in `agents/`, `orchestrator/`, `events/`
- [ ] Add logging to remaining broad catches
- [ ] Target: <500 in backbone modules

### NS-3  Vendored Z3 cleanup (37 MB, 3,220 files)

The single largest chunk of dead weight in the repo.

- [ ] Replace vendored `z3/` with `z3-solver` pip dependency
- [ ] Remove `formal_verification/vendor/z3/` (37 MB)
- [ ] Update `z3_backend.py` imports to use installed package

---

## Active Backlog

### Architecture (P2)

#### Modularize remaining large source files (>1,000 LOC)

| File | LOC | Split strategy | Status |
| :--- | ---: | :--- | :--- |
| `email/agentmail/provider.py` | 1,114 | Split by protocol | Open |
| `coding/static_analysis/static_analyzer.py` | 1,091 | Split by analysis type | Open |
| `utils/process/subprocess.py` | 1,035 | Split by concern | Open |
| `data_visualization/engines/advanced_plotter.py` | 1,024 | Split by chart type | Open |

#### Refactor top-10 oversized `__init__.py` files

119 files exceed 100 LOC. Top offenders:

| File | LOC |
| :--- | ---: |
| `ide/antigravity/__init__.py` | 709 |
| `llm/providers/__init__.py` | 558 |
| `api/webhooks/__init__.py` | 466 |
| `agents/history/__init__.py` | 459 |

- [ ] Extract implementation to named modules, keep `__init__.py` as thin re-exports
- [ ] Target: no `__init__.py` > 200 LOC

#### Break 35 circular import pairs

- [ ] Audit all 35 pairs — use interface modules or lazy imports
- [ ] Target: 0 cross-domain circular imports

#### Clean unused imports & micro-modules

- [ ] Fix 18 files with >3 unused imports
- [ ] Audit 8 micro-modules <500 LOC — merge or promote
- [ ] Audit `git_analysis/` (26 MB in source) — move generated data out

### Tooling & Type Safety (P2)

#### MCP tool expansion (33 → 38+)

- [ ] `events/mcp_tools.py` — `publish_event`, `subscribe`, `replay_events`
- [ ] `concurrency/mcp_tools.py` — `submit_task`, `pool_status`, `dead_letter_list`
- [ ] `system_discovery/mcp_tools.py` — `discover_modules`, `health_check`, `capability_scan`
- [ ] `networking/mcp_tools.py` — `http_get`, `http_post`, `dns_lookup`
- [ ] `containerization/mcp_tools.py` — `build_image`, `run_container`, `list_containers`

#### Type safety (`mypy --strict` progressive)

- [ ] Run `mypy --strict` on backbone: `agents/`, `orchestrator/`, `events/`
- [ ] Fix highest-impact type errors
- [ ] Add `py.typed` marker to backbone modules

### Future (P3)

- [ ] Migrate 144+ files from `typing.Optional`/`List`/`Dict` to modern `X | Y` syntax
- [ ] Replace 40 wildcard `from X import *` with explicit imports
- [ ] Add docstrings to 534 classes missing them (10%)
- [ ] Remove 19 commented-out code blocks
- [ ] Documentation site (MkDocs) with auto-deploy
- [ ] Event store JSONL compaction

---

## Completed (archived)

<details>
<summary>Click to expand completed items</summary>

### v1.0.2

- [x] Module count fixed: 89/88 → 86 (14 files)
- [x] Test count fixed: 9,977/10,022 → 11,065
- [x] SPEC.md architecture debt table updated
- [x] Ruff auto-fixed 3,639 lint issues
- [x] 3 orphan directories deleted
- [x] .gitignore updated for generated artifacts
- [x] TO-DO.md modularization table updated
- [x] Modularized `reviewer.py` (2,286→388 LOC) and `physical.py` (1,787→43 LOC)
- [x] Fixed circular import in `versioning/version_registry.py`
- [x] Fixed `callable | None` type error in `llm/memory/__init__.py`
- [x] Fixed `PerformanceLogger` import in `orchestrator/core.py`
- [x] Modularized 5 oversized files (tasks.py 3541→69, git.py 1747→1595, etc.)
- [x] Deleted 10 junk dirs from `src/codomyrmex/`
- [x] Cleaned ~209 MB root-level generated artifacts
- [x] Fixed 12 bare `except:` → specific types
- [x] Resolved 3 duplicate function defs
- [x] Updated 9 doc files to v1.0.2-dev
- [x] Renamed `calendar/` → `calendar_integration/` (namespace collision fix)
- [x] RASP coverage verified at 100%
- [x] Fixed 7 Python syntax errors
- [x] INDEX.md redesign with Quick Access + Module Layer Browser

### v1.0.1

- [x] MCP tools: 27 → 31
- [x] Test failures: 44 → 0
- [x] 4 xfail → pass (secrets namespace)

### Pre-v1.0

- [x] Reclassified 53 source stubs: 49 legitimate ABCs/no-ops
- [x] Security audit: 5 eval/exec, 6 pickle→JSON, 7 shell=True hardened
- [x] Docstrings added to backbone functions (100% programmatic remediation)
- [x] Fixed 20 stale "Performance module" skips
- [x] Removed 8 "git not installed" skips

</details>
