# Codomyrmex Project Roadmap & To-Do

**Status**: Active | **Last Updated**: February 24, 2026 | **Current**: v1.0.1 | **Next**: v1.0.2

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

| Metric | Value |
| :--- | ---: |
| Top-level modules | 93 |
| MCP tool files / decorators | 31 / 138 |
| Tests collected (0 collection errors) | 9,955 |
| Tests passing | 9,676 |
| Tests failing | 0 |
| Warnings | 187 |
| Coverage | 31% |
| Python 3.14+ compat | ✅ |

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

## 🔧 v1.0.2 — Next Actionable Steps

**Theme**: Coverage depth, type safety, and MCP expansion
**Effort**: 2–3 focused sessions

### 1. Coverage 31% → 40%+ (P1)

- [ ] Audit the 10 largest modules by LOC and identify untested code paths
- [ ] Add targeted tests for un-covered branches in `orchestrator`, `agents`, `events`
- [ ] Set `--cov-fail-under=35` after first pass, ratchet to 40

### 2. MCP Tool Expansion (P1)

31/93 modules have `mcp_tools.py`. Next 6 high-value additions:

- [ ] `events/mcp_tools.py`: `publish_event`, `subscribe`, `replay_events`
- [ ] `concurrency/mcp_tools.py`: `submit_task`, `pool_status`, `dead_letter_list`
- [ ] `system_discovery/mcp_tools.py`: `discover_modules`, `health_check`, `capability_scan`
- [ ] `networking/mcp_tools.py`: `http_get`, `http_post`, `dns_lookup`
- [ ] `containerization/mcp_tools.py`: `build_image`, `run_container`, `list_containers`
- [ ] `templating/mcp_tools.py`: `render_template`, `list_templates`, `validate_template`

### 3. Type Safety (P2)

- [ ] Run `mypy --strict` on `agents/`, `orchestrator/`, `events/` backbone
- [ ] Fix highest-impact type errors (missing annotations, `Any` escape hatches)
- [ ] Add `py.typed` marker to backbone modules

### 4. Skip Reduction (P2)

280 skipped tests — most are genuine env-specific. Candidates for reduction:

- [ ] Review 9 "Required modules not available" skips — may be stale guards
- [ ] Check 8 "git not installed" skips — git is always available in CI
- [ ] Verify 7 "Search indexer not available" skips

---

## 🔄 Technical Debt (active items only)

| Pri | Item | Target | Status |
| :---: | :--- | :--- | :--- |
| **P1** | ~~MCP tool coverage 27→30+~~ | `mcp_tools.py` = 31 | ✅ Done |
| **P1** | ~~Test failures 44→0~~ | `pytest` exit 0 | ✅ Done |
| **P1** | Coverage 31%→40%+ | measured, gates set | v1.0.2 |
| **P2** | `mypy --strict` progressive | 0 errors on backbone | v1.0.2 |
| **P2** | Skip reduction | 280→<250 | v1.0.2 |
| **P3** | Documentation site (MkDocs) | auto-deploy | Future |
| **P3** | Event store compaction | JSONL size | Future |
