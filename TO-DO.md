# Codomyrmex — TO-DO

**Current**: v1.0.2-dev | **Next**: v1.0.2 | **Audited**: Feb 24, 2026

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
| Tests collected | 10,022 |
| Tests passing / failing / skipped | 10,022 / 0 / ~269 |
| Coverage | 31% |
| RASP coverage | 100% ✅ |
| MCP tool files | 32 / 87 |

---

## Sprint 1 — Critical Fixes (P0) ✅ COMPLETE

### 1.1 ~~Audit pass-only stub functions~~ — Reclassified, no action needed

Deep audit of 53 source "stubs": **49 are legitimate** (ABCs with `@abstractmethod`, context manager `__init__`/`__exit__` no-ops), **4 are intentional no-ops** (demo setup, exporter shutdown). Zero dead stubs remain. Original count of "88" was inflated by counting ABC interface methods.

60 test stubs remain (scaffolding for future tests) — not blocking.

### 1.2 Vendored Z3 solver (37 MB, 3,220 files) — deferred

Used by `formal_verification/backends/z3_backend.py` and `formal_verification/__init__.py` (conditional import). Replacing with `pip install z3-solver` is straightforward but is a large file operation (delete 3,220 files). Deferring to a dedicated cleanup PR.

- [ ] Replace vendored `z3/` with `z3-solver` pip dependency
- [ ] Remove `formal_verification/vendor/z3/` (37 MB)
- [ ] Update `z3_backend.py` imports to use installed package

### 1.3 ~~Fix pre-existing test failures~~ — DONE

- [x] Fixed `test_audit_documentation_help` — script moved to `scripts/documentation/` subdirectory
- [x] Rewrote `test_scripts_integration.py` — corrected all 10 script paths from `scripts/` root to actual subdirectory locations
- [x] Fixed `test_bare_except` — test input used `except Exception:` but detector checks for bare `except:`. Corrected test input.
- [x] Full suite: **9,683+ passed, 0 failed, 269 skipped**

---

## Sprint 2 — Code Quality (P1)

### 2.1 Broad exception handling (1,498 `except Exception` clauses)

- [ ] Audit top-20 files by broad exception count
- [ ] Replace with specific types in `agents/`, `orchestrator/`, `events/` backbone
- [ ] Add logging to remaining broad catches
- [ ] Target: <500 in backbone modules

### 2.2 Security patterns audit

| Pattern | Count | Action |
| :--- | ---: | :--- |
| `eval()`/`exec()` | 5 | Ensure sandboxed |
| `pickle.load/dump` | 6 | Replace with `json` where possible |
| `subprocess` `shell=True` | 7 | Replace with list form |
| `tempfile` without cleanup | 2 | Add cleanup |

- [x] Audit all 5 `eval`/`exec` — 3 false positives (regex, dict literal, redis.eval), 2 fixed: AST-based calculator + restricted namespace
- [x] Replace pickle with safer serialization in `cache/backends/` — file_based.py and redis_backend.py now use JSON; PickleSerializer kept as opt-in with security warning
- [x] Fix 7 `shell=True` usages — 1 hardened with `shlex.split` (`interactive_shell.py`), 6 documented as intentional shell executors with `# SECURITY` annotations
- [x] Add `finally` cleanup to 2 tempfile usages — `analyzer.py` and `deployment_orchestrator.py` now use try/finally

### 2.3 Fix SerializationManager bug

3 tests skip with reason "SerializationManager passes wrong kwarg 'format' to Serializer".

- [x] Fix the `format` kwarg bug in SerializationManager — convert string to `SerializationFormat` enum before passing to `Serializer`
- [x] Remove the 3 xfail decorators from `test_serialization.py`

### 2.4 Coverage 31% → 40%

- [ ] Audit 10 largest modules for untested code paths
- [ ] Add targeted tests for `orchestrator`, `agents`, `events`
- [ ] Set `--cov-fail-under=35`, ratchet to 40

---

## Sprint 3 — Architecture (P2)

### 3.1 Modularize 8 large source files (>1,000 LOC)

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

### 3.2 Refactor top-10 oversized `__init__.py` files

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

### 3.3 Break 35 circular import pairs

- [ ] Audit all 35 pairs — use interface modules or lazy imports
- [ ] Target: 0 cross-domain circular imports

### 3.4 Clean unused imports & micro-modules

- [ ] Fix 18 files with >3 unused imports
- [ ] Audit 8 micro-modules <500 LOC — merge or promote
- [ ] Audit `git_analysis/` (26 MB in source) — move generated data out

---

## Sprint 4 — Tooling & Type Safety (P2)

### 4.1 MCP tool expansion (32 → 38+)

- [ ] `events/mcp_tools.py` — `publish_event`, `subscribe`, `replay_events`
- [ ] `concurrency/mcp_tools.py` — `submit_task`, `pool_status`, `dead_letter_list`
- [ ] `system_discovery/mcp_tools.py` — `discover_modules`, `health_check`, `capability_scan`
- [ ] `networking/mcp_tools.py` — `http_get`, `http_post`, `dns_lookup`
- [ ] `containerization/mcp_tools.py` — `build_image`, `run_container`, `list_containers`
- [ ] `templating/mcp_tools.py` — `render_template`, `list_templates`, `validate_template`

### 4.2 Type safety (`mypy --strict` progressive)

- [ ] Run `mypy --strict` on backbone: `agents/`, `orchestrator/`, `events/`
- [ ] Fix highest-impact type errors
- [ ] Add `py.typed` marker to backbone modules

### 4.3 Skip reduction (269 -> ~241)

| Actionable Skips | Count | Fix |
| :--- | ---: | :--- |
| "Performance module not available" | 20 | Module exists — removed stale skips ✅ |
| "git not installed" | 8 | Always available — removed stale skips ✅ |
| "Required modules not available" | 9 | Audited — Not stale. Protects tests lacking Docker/ChromaDB ✅ |
| "Search indexer not available" | 7 | Audited — Not stale. Protects tests lacking backend indexers ✅ |

- [x] Fix the 20 stale "Performance module" skips
- [x] Remove 8 "git not installed" skips
- [x] Audit remaining 16 potentially stale skips (verified valid)

### 4.4 Docstring & type hint coverage

- [x] Add docstrings to backbone functions (target: <20% missing in `agents/`, `orchestrator/`, `events/`) — Achieved via 100% programmatic docstring remediation!
- [ ] Add type hints to backbone functions (target: <30% missing in `agents/`, `orchestrator/`, `events/`)

---

## Future (P3)

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

### Sprint 1 — Critical Fixes (P0)

- [x] Reclassified 53 source stubs: 49 legitimate ABCs/no-ops, 4 intentional no-ops, 0 dead
- [x] Fixed `test_scripts_integration.py` — corrected 10 script paths to subdirectories
- [x] Fixed `test_bare_except` — corrected test input to use actual bare except
- [x] Full suite: 9,683+ passed, 0 failed, 269 skipped

</details>
