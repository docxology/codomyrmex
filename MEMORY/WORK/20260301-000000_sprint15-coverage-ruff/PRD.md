---
task: "Sprint 15 — coverage gate ratchet + ruff architectural violations"
slug: "20260301-000000_sprint15-coverage-ruff"
effort: Comprehensive
phase: observe
progress: 0/32
mode: ALGORITHM
started: "2026-03-01"
updated: "2026-03-01"
---

## Context

Continuation of the Codomyrmex comprehensive improvement project. Sprint 14 achieved:
- Ruff violations: 1,531 → 607 (-60.4%)
- server.py test coverage: 0% → 70%
- All 8 SPEC.md stubs expanded
- All 88 modules have complete RASP docs (AGENTS.md + README.md + PAI.md)

Sprint 15 targets from TODO.md:
1. **CRITICAL**: Ratchet coverage gate fail_under=68 → 70%
2. **HIGH**: Reduce TID252 (404 relative imports) and E402 (160 conditional imports)
3. **MEDIUM**: Add py.typed markers, MCP coverage for missing modules

### Risks
- Full test suite may reveal coverage below 70% — needs remediation before gate bump
- TID252/E402 fixes are architectural — risk of breaking import chains
- Some modules may have circular import issues when converting relative → absolute

## Criteria

- [ ] ISC-1: Full test suite runs without failures or regressions
- [ ] ISC-2: Overall test coverage ≥70% confirmed by pytest --cov
- [ ] ISC-3: pyproject.toml fail_under updated from 68 to 70
- [ ] ISC-4: Coverage gate passes (pytest --cov-fail-under=70 exits 0)
- [ ] ISC-5: server.py coverage remains ≥70% after gate bump
- [ ] ISC-6: At least 5 low-coverage modules identified for improvement
- [ ] ISC-7: At least one additional module coverage improved to ≥80%
- [ ] ISC-8: TID252 count reduced from 404 (convert ≥20 relative imports to absolute)
- [ ] ISC-9: E402 count reduced from 160 (fix ≥10 conditional import ordering issues)
- [ ] ISC-10: No new ruff violations introduced by import changes
- [ ] ISC-11: All import changes verified with pytest (no ImportError failures)
- [ ] ISC-12: py.typed marker added to at least 5 core modules (PEP 561)
- [ ] ISC-13: TODO.md updated with Sprint 15 progress
- [ ] ISC-14: Git committed with descriptive commit message
- [ ] ISC-15: Coverage report HTML generated for analysis
- [ ] ISC-16: At least 3 modules with 0% coverage identified
- [ ] ISC-17: email/provider.py coverage improved from 0% (was TODO item)
- [ ] ISC-18: agents/droid/run_todo_droid.py coverage improved from 0% (was TODO item)
- [ ] ISC-19: Ruff violations remain ≤607 (no regressions)
- [ ] ISC-20: ruff check src/ exits cleanly with final count logged
- [ ] ISC-21: At least 5 additional __init__.py exports fixed for completeness
- [ ] ISC-22: Any new F821 undefined names fixed immediately
- [ ] ISC-23: pyproject.toml syntax verified correct after edits
- [ ] ISC-24: All modified test files pass individually (uv run pytest <file>)
- [ ] ISC-25: Memory files updated with Sprint 15 results
- [ ] ISC-26: Rules submodule: at least 1 enhancement from TODO (rules_get_section or rules_search)
- [ ] ISC-27: MCP exposure: at least 1 new mcp_tools.py added to a missing module
- [ ] ISC-28: coverage.xml or .coverage file present for CI consumption
- [ ] ISC-29: No circular import warnings from test collection
- [ ] ISC-30: E741 ambiguous variable names: remaining count documented
- [ ] ISC-31: F401 unused imports: count confirmed ≤original (no new ones added)
- [ ] ISC-32: Final metrics snapshot written to TODO.md

## Decisions

## Verification
