---
task: "Ratchet coverage gate 68→70, add smoke markers to integration tests"
slug: "20260301-220000_coverage-gate-ratchet-smoke-markers"
effort: "Extended"
phase: "complete"
progress: "13/18"
mode: "algorithm"
started: "2026-03-01T22:00:00Z"
updated: "2026-03-01T22:00:00Z"
---

## Context

Continuing Sprint 14 work. Previous session added 169+ new tests (docs_gen: 84, release: 85) plus earlier 52 tests (dependency_resolver, mcp_tools, git_ops). Coverage gate currently at 68% in three places. Plan: run full test suite to confirm ≥70%, then ratchet all three config files. Also need to mark ~63 assertion-less integration tests with `@pytest.mark.smoke` (marker added to pytest.ini in previous session).

### Risks
- Coverage may still be below 70% (new tests added 169 new passing tests but coverage depends on LOC hit in new modules)
- Integration tests span large test files — wrong tests tagged as smoke could reduce meaningful assertion coverage
- Three config files must be updated atomically — partial update would leave system inconsistent

## Criteria

- [x] ISC-1: Full test suite runs (unit/ excl. agents): 66.26% coverage — confirmed running
- [ ] ISC-2: Coverage percentage reported by pytest is ≥70.0% — NOT YET (~68.3% with agents; needs ~2,290 more covered lines)
- [ ] ISC-3: `pyproject.toml` `fail_under` changed from 68 to 70 — DEFERRED (coverage not at 70%)
- [ ] ISC-4: `pytest.ini` `--cov-fail-under` changed from 68 to 70 — DEFERRED
- [ ] ISC-5: `.github/workflows/ci.yml` `--cov-fail-under=68` changed to 70 — DEFERRED
- [ ] ISC-6: All three coverage gate files updated consistently — DEFERRED
- [x] ISC-7: `test_cross_module_workflows.py` assertion-less tests identified: 4 tests
- [x] ISC-8: `test_cross_module_workflows.py` 4 smoke tests marked with `@pytest.mark.smoke`
- [x] ISC-9: `test_improvements.py` audit: all 7 tests have real assertions — none are smoke
- [x] ISC-10: `test_improvements.py` — no smoke marking needed (all have assertions)
- [x] ISC-11: `@pytest.mark.smoke` uses existing `pytest` import already in test file
- [x] ISC-12: Smoke tests collected: `pytest -m smoke` collects exactly 4 tests in that file
- [x] ISC-13: Non-smoke tests in same files still collected normally
- [ ] ISC-14: Full test suite passes at new 70% gate — DEFERRED (need more coverage first)
- [x] ISC-A1: Only assertion-conditional tests marked smoke; test_workflow_coordination has unconditional assertions → NOT marked
- [x] ISC-A2: Coverage gate stays at 68 (not lowered) in all three config files
- [x] ISC-A3: No test file imports broken — smoke decorator uses existing `pytest` import
- [x] ISC-18: TO-DO.md updated: Sprint 14 items 16-17 added, Sprint 15 item 1 expanded with specific targets

## Decisions

## Verification

- ISC-7,8,9,10,11,12,13: `pytest -m smoke` collects exactly 4 tests in test_cross_module_workflows.py: test_error_handling_across_workflows, test_workflow_performance_metrics, test_data_consistency_across_workflows, test_module_interoperability. 4/8 collected, 4 deselected.
- ISC-A1: test_workflow_coordination_and_reporting has unconditional `assert isinstance(report, dict)` etc. — correctly NOT marked smoke.
- ISC-A2: All three config files confirmed at 68%: pyproject.toml `fail_under=68`, pytest.ini `--cov-fail-under=68`, ci.yml `--cov-fail-under=68`.
- ISC-1: Unit test coverage run (excl. agents) completed: 66.26% (75,887/114,532 statements). With agents: ~68.3%.
- ISC-2 DEFERRED: 70% requires ~2,290 more covered lines. Top targets: git_operations/cli/repo.py (220 missing), email/agentmail/provider.py (220 missing), ide/antigravity/client.py (214 missing), cli/handlers/quick.py (198 missing).
- ISC-18: TO-DO.md Sprint 14 updated with items 16-17 (smoke markers, coverage confirmation). Sprint 15 item 1 expanded with specific coverage gap targets. Test files snapshot updated to 694.
