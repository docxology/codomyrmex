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
| Tests passing | 9,675 |
| Tests failing | 1 (flaky) |
| Warnings | 187 |
| Coverage | 31% |
| Python 3.14+ compat | ✅ |

> [!NOTE]
> Full release history (v0.1.3 → v1.0.0, Sprints 1–41) is archived in [CHANGELOG.md](CHANGELOG.md).

---

## 🔧 v1.0.1 — Next Actionable Steps

**Theme**: Depth, coverage, and hardening
**Effort**: 1–2 focused sessions

### 1. MCP Tool Coverage (P1)

31/93 modules have `mcp_tools.py`. Recent additions:

- [x] `agentic_memory/mcp_tools.py`: `memory_put`, `memory_get`, `memory_search`
- [x] `collaboration/mcp_tools.py`: `swarm_submit_task`, `pool_status`, `list_agents`
- [x] `validation/mcp_tools.py`: `validate_schema`, `validate_config`, `validation_summary`

### 2. Test Suite Health (P2)

- [ ] Investigate ~170 skipped tests — reduce env-specific skips where possible
- [ ] Re-audit coverage per Tier-1 module, set `fail_under` gates
- [ ] Clean up any remaining deprecation warnings from `filterwarnings`

---

## 🔄 Technical Debt (active items only)

| Pri | Item | Target | Status |
| :---: | :--- | :--- | :--- |
| **P1** | ~~MCP tool coverage 27→30+~~ | `mcp_tools.py` = 31 | ✅ Done |
| **P2** | `mypy --strict` progressive | 0 errors on backbone | Ongoing |
| **P2** | Coverage 31%→40%+ | measured, gates set | v1.0.1 |
| **P3** | Documentation site (MkDocs) | auto-deploy | Future |
| **P3** | Event store compaction | JSONL size | Future |
