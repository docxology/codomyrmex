# Codomyrmex — TO-DO

**Current**: v1.0.2-dev | **Next**: v1.0.2 | **Updated**: Feb 25, 2026

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
| Modules | 88 |
| Functions / Classes | 23,208 / 5,210 |
| Tests collected | 9,977 |
| Tests passing / failing / skipped | 9,724 / 0 / 253 |
| Coverage | 31% |
| RASP coverage | 100% ✅ |
| MCP tool files | 32 / 87 |

---

## Next Sprint — High-Impact Work (pick 3)

### NS-1  Coverage 31% → 40%

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

#### Modularize 8 large source files (>1,000 LOC)

| File | LOC | Split strategy |
| :--- | ---: | :--- |
| `coding/review/reviewer.py` | 2,284 | analysis/dashboard/report mixins |
| `agents/droid/generators/physical.py` | 1,776 | Split by concern |
| `git_operations/core/git.py` | 1,595 | remote/state/analysis/config |
| `agents/claude/claude_client.py` | 1,582 | auth/chat/streaming/tools |
| `cloud/coda_io/client.py` | 1,386 | docs/pages/tables/formulas |
| `agents/pai/mcp_bridge.py` | 1,264 | tools/resources/prompts |
| `git_operations/api/github.py` | 1,186 | repos/prs/issues/actions |
| `agents/ai_code_editing/ai_code_helpers.py` | 1,087 | further split |

#### Refactor top-10 oversized `__init__.py` files

119 files exceed 100 LOC. Top offenders:

| File | LOC |
| :--- | ---: |
| `ide/antigravity/__init__.py` | 709 |
| `skills/arscontexta/__init__.py` | 677 |
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

#### MCP tool expansion (32 → 38+)

- [ ] `events/mcp_tools.py` — `publish_event`, `subscribe`, `replay_events`
- [ ] `concurrency/mcp_tools.py` — `submit_task`, `pool_status`, `dead_letter_list`
- [ ] `system_discovery/mcp_tools.py` — `discover_modules`, `health_check`, `capability_scan`
- [ ] `networking/mcp_tools.py` — `http_get`, `http_post`, `dns_lookup`
- [ ] `containerization/mcp_tools.py` — `build_image`, `run_container`, `list_containers`
- [ ] `templating/mcp_tools.py` — `render_template`, `list_templates`, `validate_template`

#### Type safety (`mypy --strict` progressive)

- [ ] Run `mypy --strict` on backbone: `agents/`, `orchestrator/`, `events/`
- [ ] Fix highest-impact type errors
- [ ] Add `py.typed` marker to backbone modules

#### Type hint coverage

- [ ] Add type hints to backbone functions (target: <30% missing in `agents/`, `orchestrator/`, `events/`)

### Future (P3)

- [ ] Migrate 144+ files from `typing.Optional`/`List`/`Dict` to modern `X | Y` syntax
- [ ] Replace 40 wildcard `from X import *` with explicit imports
- [ ] Add docstrings to 534 classes missing them (10%)
- [ ] Remove 19 commented-out code blocks
- [ ] Documentation site (MkDocs) with auto-deploy
- [ ] Event store JSONL compaction
- [ ] `tests/visualization/test_dashboard.py` is empty — implement or remove

---

## Completed (archived)

<details>
<summary>Click to expand completed items</summary>

### v1.0.1

- [x] MCP tools: 27 → 31
- [x] Test failures: 44 → 0
- [x] 4 xfail → pass (secrets namespace)
- [x] Warning filters added

### v1.0.2-dev

- [x] Modularized 5 oversized files (tasks.py 3541→69, git.py 1747→1595, etc.)
- [x] Deleted 10 junk dirs from `src/codomyrmex/`
- [x] Cleaned ~209 MB root-level generated artifacts
- [x] Fixed 12 bare `except:` → specific types
- [x] Fixed 1 SyntaxWarning (escape sequence)
- [x] Replaced `os.system("clear")` → `subprocess.run`
- [x] Resolved 3 duplicate function defs (1 real + 2 false positives)
- [x] Updated 9 doc files to v1.0.2-dev
- [x] Added CHANGELOG v1.0.2-dev entry
- [x] Version bumped to 1.0.2.dev0
- [x] Renamed `calendar/` → `calendar_integration/` (namespace collision fix)
- [x] RASP coverage verified at 100%
- [x] Fixed 7 Python syntax errors (erroneous docstrings in mixins, handlers, etc.)
- [x] INDEX.md redesign with Quick Access + Module Layer Browser
- [x] Expanded 4 thin PAI.md files to full specs

### Sprint 1 — Critical Fixes (P0)

- [x] Reclassified 53 source stubs: 49 legitimate ABCs/no-ops, 4 intentional no-ops, 0 dead
- [x] Fixed `test_scripts_integration.py` — corrected 10 script paths to subdirectories
- [x] Fixed `test_bare_except` — corrected test input to use actual bare except
- [x] Full suite: 10,022 passed, 0 failed, ~269 skipped

### Sprint 2 — Code Quality (partial)

- [x] Security audit: 5 eval/exec (3 false positives, 2 fixed), 6 pickle→JSON, 7 shell=True hardened, 2 tempfile cleanup
- [x] SerializationManager `format` kwarg bug fixed + 3 xfail removed
- [x] Docstrings added to backbone functions (100% programmatic remediation)

### Sprint 4 — Tooling (partial)

- [x] Fixed 20 stale "Performance module" skips
- [x] Removed 8 "git not installed" skips
- [x] Audited remaining 16 potentially stale skips (verified valid)

</details>
